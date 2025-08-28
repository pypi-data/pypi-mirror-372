###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.api import utils
from everysk.core.string import pluralize, snake_case

###############################################################################
#   APIResource Implementation
###############################################################################
class APIResource(utils.EveryskObject):
    """
    Represents a resource accessible via an API

    This class serves as a base class for API resources and provides method for refreshing resource data and obtaining class names and URLs.
    """
    def __init__(self, retrieve_params, params) -> None:
        super().__init__(retrieve_params, params)
        self.__retrieve_params = retrieve_params

    def refresh(self, **kwargs):
        """
        Refreshes the resource data from the API.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            APIResource: The refreshed APIResource object.
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f"{self.class_url()}/{self.get('id')}"
        response = api_req.get(url, self.__retrieve_params)
        data = response[self.class_name()]
        self.update(data)
        self.clear_unsaved_values()
        return self

    @classmethod
    def class_name(cls):
        """
        convert the class name to the snake case format
        """
        return snake_case(cls.__name__)

    @classmethod
    def class_name_list(cls):
        """
        Returns the pluralized class name.

        Returns:
            str: The pluralized class name.
        """
        return pluralize(cls.class_name())

    @classmethod
    def class_url(cls):
        """
        Returns the URL path for the class.
        Utilizing the class name list and ensuring consistency across different parts of the code.

        Returns:
            str: The URL path for the class.
        """
        return f'/{cls.class_name_list()}'

###############################################################################
#   Retrievable APIResource Implementation
###############################################################################
class RetrievableAPIResource(APIResource):

    @classmethod
    def retrieve(cls, id, **kwargs):
        """
        Retrieves a single resource from the API by its ID.
        Sends a GET request to the API to retrieve a single resource of the specified class type
        identified by the provided ID.

        Args:
            id (str):
                The unique identifier of the resource.

            workspace (str):
                Determines on which workspace the request will be made

            **kwargs (dict):
                Any additional keyword arguments to customize the request

        Returns:
            object: A single resource of the class type.
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f'{cls.class_url()}/{id}'
        response = api_req.get(url, kwargs)
        return utils.to_object(cls, kwargs, response)

###############################################################################
#   Listable APIResource Implementation
###############################################################################
class ListableAPIResource(APIResource):

    @classmethod
    def list(cls, **kwargs):
        """
        Retrieves a list of resources from the API.
        This class method sends a GET request to the API to retrieve a list of resources of the specified class type.
        Check https://everysk.com/api/docs/#list-all-portfolios for additional information

        Args:
            query (str, optional):
                Request a list of portfolios fileting it by `name` or `tag`

            workspace (str, optional):
                Determines on which workspace the request will be made

            page_size (int, optional):
                Set the number of object that will be listed per page

            page_token (int, optional):
                This token defines which page will be returned to the user

            **kwargs (dict):
                Additional keyword arguments to customize the request

        Returns:
            list: A list of resource of the class type.
        """
        api_req = utils.create_api_requestor(kwargs)
        url = cls.class_url()
        response = api_req.get(url, kwargs)
        return utils.to_list(cls, kwargs, response)

    @classmethod
    def auto_paging_iter(cls, **kwargs):
        """
        Provides an iterator over all resources, handling pagination automatically.
        This class method iterates over all resources of the specified class type, handling pagination automatically
        to retrieve the complete list of resources. Check https://everysk.com/api/docs/#pagination for more information

        Args:
            page_size (int):
                A limit on the number of objects to be returned, between 1 and 100

            page_token (str):
                Returns the previous page token

            **kwargs (dict):
                Additional keyword arguments to customize the request, such as filters or pagination parameters.

        Returns:
            object: A resource of the class type.
        """
        params = dict(kwargs)
        page = cls.list(**params)
        while True:
            for item in page:
                yield item
            if page.next_page_token() is None:
                return
            params['page_token'] = page.next_page_token()
            page = cls.list(**params)

###############################################################################
#   Deletable APIResource Implementation
###############################################################################
class DeletableAPIResource(APIResource):

    def delete(self):
        """
        Deletes the current instance of the resource from the API
        This class method sends a DELETE request to the API to delete the current instance.

        Example:
            >>> from everysk.api.api_resources.api_resource import DeletableAPIResource
            >>> resource = DeletableAPIResource.retrieve("resource_id")
            >>> resource.delete()
        """
        api_req = utils.create_api_requestor()
        url = f"{self.class_url()}/{self.get('id')}"
        workspace = self.get('workspace', None)
        if workspace:
            url = f'{url}?workspace={workspace}'
        response = api_req.delete(url)
        data = response[self.class_name()]
        self.clear()
        self.update(data)
        self.clear_unsaved_values()
        return self

    @classmethod
    def remove(cls, id, **kwargs):
        """
        Deletes a resource from the API by its ID.
        Sends a DELETE request to the API to delete a resource of the specified class type
        identified by the provided ID.

        Args:
            id: The unique identifier of the resource to be deleted.

            workspace (str, optional):
                Determines on which workspace the request will be made.

            **kwargs (dict): Additional keyword arguments to customize the request.

        Example:
            >>> DeletableAPIResource.remove('resource_id')
            Deleted resource_object
        """
        api_req = utils.create_api_requestor()
        url = f'{cls.class_url()}/{id}'
        workspace = kwargs.get('workspace', None)
        if workspace:
            url = f'{url}?workspace={workspace}'
        response = api_req.delete(url)
        data = response[cls.class_name()]
        return utils.to_object(cls, {}, response)

###############################################################################
#   Creatable APIResource Implementation
###############################################################################
class CreateableAPIResource(APIResource):

    @classmethod
    def create(cls, **kwargs):
        """
        Creates a new instance of the resource and saves it to the API.
        This class method sends a POST request to the API to create a new instance of the resource with the provided data.

        Args:
            description (str, optional):
                Provides detailed information about the resource

            tags (list, optional):
                Sequence of hashtags used to label the related resources. Any sequence of lowercase character, numbers, and underscore might be used.

            date (str, optional):
                Resource date in the following format: `YYYYMMDD`

            workspace (str, optional):
                Determines on which workspace the request will be made

            **kwargs (dict):
                Keyword arguments representing the data for creating the resource. Depending on the resource, each entity will have different kwargs.

        Example:
            >>> new_resource_data = {'name': 'New Resource'}
            >>> new_resource = CreatableAPIResource.create(**new_resource_data)
            >>> print(new_resource)
            New resource_object
        """
        api_req = utils.create_api_requestor(kwargs)
        url = cls.class_url()
        response = api_req.post(url, kwargs)
        return utils.to_object(cls, kwargs, response)

###############################################################################
#   Updatable APIResource Implementation
###############################################################################
class UpdateableAPIResource(APIResource):

    @classmethod
    def modify(cls, id, **kwargs):
        """
        Modifies a resource by its ID with the provided data.

        This class method sends a PUT request to the API to modify a resource of the specified class type
        identified by the provided ID with the provided data.

        Args:
            id (str):
                The unique identifier of the resource to be modified.

            **kwargs (dict):
                Keyword arguments representing the data to be updated. The kwargs will differ for each entity.

        Example:
            >>> updated_data = {'name': 'Updated Resource'}
            >>> updated_resource = UpdateableAPIResource.modify('resource_id', **updated_data)
            >>> print(updated_resource)
            Updated resource_object
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f'{cls.class_url()}/{id}'
        response = api_req.put(url, kwargs)
        data = response[cls.class_name()]
        return utils.to_object(cls, kwargs, response)

    def save(self, **kwargs):
        """
        Saves the changes made to the current instance of the resource to the API.
        This method sends a PUT request to the API to save the changes made to the current instance of the resource.

        Args:
            **kwargs (dict):
                each entity will have different arguments for saving

        Example:
            >>> resource = UpdateableAPIResource.retrieve('resource_id')
            >>> resource['name'] = 'Updated Name'
            >>> resource.save()
            Updated resource_object
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f"{self.class_url()}/{self.get('id')}"
        #response = api_req.put(url, self)
        unsaved_values = self.get_unsaved_values()
        response = api_req.put(url, unsaved_values)
        data = response[self.class_name()]
        self.update(data)
        self.clear_unsaved_values()
        return self

###############################################################################
#   Filterable APIResource Implementation
###############################################################################
class FilterableAPIResource(APIResource):

    @classmethod
    def filter(cls,**kwargs):
        """
        Filters resources based on the provided criteria.

        This class method sends a POST request to the API to filter resources of the specified class type
        based on the provided criteria.

        Args:
            limit (int, optional): The maximum number of resources to retrieve. Defaults to a predetermined limit if not specified.

            tags (list[str], optional):
                A list of strings representing tags used to filter resources. Tags should be a sequence
                of lowercase characters, numbers, and underscores.

            start (str, optional):
                A start value used for filtering. The format and usage of this parameter can vary
                depending on the resource type and should be a string or null.

            end (str, optional):
                An end value for filtering, similar in format and function to `start`. It should be a string or null.

            date_time (str, optional):
                A datetime string used for filtering resources. The expected format should be compliant
                with the API's datetime format requirements.

            link_uid (str, optional):
                A unique identifier used to filter resources by their association to another entity.

            **kwargs (dict):
                Additional keyword arguments that represent other filtering criteria not explicitly listed. These should
                align with the filterable fields of the resources.

        Returns:
            list: A list of filtered resources.

        Example:
            >>> filtered_resources = FilterableAPIResource.filter(param1=value1, param2=value2)
            >>> print(filtered_resources)
            [filtered_resource1, filtered_resource2, ...]
        """
        api_req = utils.create_api_requestor(kwargs)
        url = f'/{cls.class_name_list()}/filter'
        response = api_req.post(url, kwargs)
        return utils.to_list(cls, kwargs, response)
