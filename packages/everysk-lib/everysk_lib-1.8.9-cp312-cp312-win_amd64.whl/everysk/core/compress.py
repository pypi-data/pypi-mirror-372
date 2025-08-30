###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

__all__ = ['compress', 'decompress']

import gzip
import zlib
import io
import os
import zipfile
import base64
import fnmatch
from typing import Any

from everysk.core.log import Logger
from everysk.core.serialize import dumps, loads


log = Logger('everysk-lib-compress')


###############################################################################
#   Private Functions Implementation
###############################################################################
def compress_json(obj: Any) -> str:
    """
    This function first serializes the input object into a JSON string using the dumps function.
    Then it compresses the JSON string using zlib compression.
    The output is a bytes object which may contain non-printable characters due to compression

    Args:
        obj (Any): The JSON-serializable object to compress.

    Returns:
        str: The compressed string representation of the JSON-serialized object.

    Example:
        >>> data = {'key': 'value'}
        >>> compressed_data = compress_json(data)
        >>> print(compressed_data)
        >>> b'x\x9c\xcbH\xcd\xc9\xc9W(....)' # Example of the compressed data
    """
    log.deprecated("compress_json is deprecated. Use compress(obj, serialize='json') instead.")
    return compress(obj, serialize='json')

def decompress_json(data: str, convert_str_to_date: bool = False) -> Any: # pylint: disable=unused-argument
    """
    Decompress data with zlib and transform to an obj with loads function.
    The input data should be a zlib-compressed string.
    The returned object may be any valid JSON-serializable Python object

    Args:
        data (str): the zlib-compressed string to decompress and deserialized data.
        convert_str_to_date (bool, optional): Enable conversion of str to Date and Datetime. Default is True.

    Returns:
        Any: The Python object reconstructed from the decompressed and deserialized.

    Example:
        >>> from everysk.core.compress import decompress_json
        >>> compressed_data = b'x\x9c\xabV\xcaN\xadT\xb2RP*K\xcc)MU\xaa\x05\x00+\xaf\x05A'
        >>> decompressed_data = decompress_json(compressed_data)
        >>> print(decompressed_data)
        >>> {'key': 'value'} # Example of the decompressed data'
    """
    log.deprecated("decompress_json is deprecated. Use decompress(obj, serialize='json') instead.")
    return decompress(data, serialize='json')

def compress_pickle(obj: Any) -> str:
    """
    Convert obj to string with pickle dumps then uses zlib to compress it.
    The output is a bytes object which may contain non-printable characters due to compression.

    Args:
        obj (Any): The Python object to compress.

    Returns:
        str: The compressed string representation of the serialized object.

    Example:
        >>> data = {'key': 'value'}
        >>> compressed_data = compress_pickle(data)
        >>> print(compressed_data)
        >>> b'x\x9c\xabV*I,.Q(...)'  # Example compressed string output
    """
    log.deprecated("compress_pickle is deprecated. Use compress(obj, serialize='pickle') instead.")
    return compress(obj, serialize='pickle')

def decompress_pickle(data: str) -> Any:
    """
    Decompress data with zlib and transform to a obj with pickle loads.
    The input data should be a zlib-compressed string generated from a pickled Python object.

    Args:
        data (str): The zlib-compressed string to decompress and deserialize.

    Returns:
        Any: The Python object reconstructed from the decompressed and deserialized data.

    Example:
        >>> compressed_data = b'x\x9c\xabV\xcaN\xadT\xb2RP*K\xcc)MU\xaa\x05\x00+\xaf\x05A' # Example compressed data
        >>> decompressed_data = decompress_pickle(compressed_data)
        >>> print(decompressed_data)
        >>> {'key': 'value'}  # Example decompressed object output
    """
    log.deprecated("decompress_pickle is deprecated. Use decompress(obj, serialize='pickle') instead.")
    return decompress(data, serialize='pickle')

def zip_directory_to_str(path_list: str | list, path_name_list: str | list, ignore_files: list = None, ignore_roots: list = None) -> str:
    """
    This function takes a directory path as input and creates a zip file in memory.

    Args:
        path_list (str | list): The path to the directory to zip, it can be a list of paths.
        path_name_list (str | list): The name of the root folder inside the zip file, it can be a list of path names.
        ignore_files (list, optional): A list of file names to ignore when zipping the directory.
        ignore_roots (list, optional): A list of patterns to ignore when zipping the directory.

    Returns:
        str: The base64 encoded string representation of the zip file.

    Raises:
        ValueError: If the length of path_list and path_name_list is not the same.

    Example:
        >>> zip_directory_to_str('path/to/directory', 'root_folder_name')
        >>> zip_directory_to_str('path/to/directory', 'root_folder_name', ['config.json'], ['**/log', '**/temp/**'])

        Below is an example of using a list of paths and path names:
        >>> zip_directory_to_str(['path/to/directory1', 'path/to/directory2'], ['root_folder_name1', 'root_folder_name2'], ['config.json'], ['**/log', '**/temp/**'])
    """
    # Create a BytesIO object to store the zip file
    memory_zip = io.BytesIO()

    if isinstance(path_list, str):
        path_list = [path_list]

    if isinstance(path_name_list, str):
        path_name_list = [path_name_list]

    if len(path_list) != len(path_name_list):
        raise ValueError("The length of path_list and path_name_list should be the same.")

    # Create a ZipFile object with the memory buffer as its destination
    with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for path, path_name in zip(path_list, path_name_list):
            for root, _, files in os.walk(path):
                # Check if the current root matches any of the ignore_roots patterns
                if ignore_roots and any(fnmatch.fnmatch(root, pattern) for pattern in ignore_roots):
                    continue
                for file in files:
                    # Ignore files if specified
                    if ignore_files and file in ignore_files:
                        continue
                    file_path = os.path.join(root, file)
                    # Compute the relative path and add the path_name as the root folder
                    relative_path = os.path.relpath(file_path, path)
                    zip_file.write(file_path, os.path.join(path_name, relative_path))

    # We need to adjust the cursor of the BytesIO object to the start after writing
    memory_zip.seek(0)

    # Return the base64 encoded string representation of the zip file
    return base64.b64encode(memory_zip.getvalue()).decode('utf-8')

###############################################################################
#   Public Functions Implementation
###############################################################################
def compress(obj: Any, protocol: str = 'zlib', serialize: str | None = 'pickle', use_undefined: bool | None = True, add_class_path: bool | None = None) -> bytes:
    """
    Compress an object using either zlib or gzip compression.
    If serialize is set, the object is serialized using the specified serialization format before compression.
    Supported options for serialization are JSON or Pickle.

    Args:
        obj (Any): The Python object to compress
        protocol (str, optional): The serialization protocol to use. Default is 'zlib'. Options are 'zlib' and 'gzip'.
        serialize (str, optional): The serialization format to use. Default is 'pickle'. Options are 'json', 'pickle' and None.
        use_undefined (bool, optional): If True, undefined values are included in the serialization. Default is True.
        add_class_path (bool, optional): If True, the class path is included in the serialization. Default is None.

    Returns:
        bytes: The compressed string representation of the serialized object.

    Example:
        >>> data = {'key': 'value'}
        >>> compress(data)
        >>> b'x\x9c\xabV*I,.Q(...)'  # Example compressed string output
    """
    if protocol == 'zlib':
        compress_fn = zlib.compress
    elif protocol == 'gzip':
        compress_fn = gzip.compress
    else:
        raise ValueError(f"Unsupported compression protocol '{protocol}'. Use 'zlib' or 'gzip'.")

    result = obj
    if serialize:
        result = dumps(obj, protocol=serialize, use_undefined=use_undefined, add_class_path=add_class_path)

    if isinstance(result, str):
        result = result.encode('utf-8')

    return compress_fn(result)

def decompress(data: bytes, protocol: str = 'zlib', serialize: str | None = 'pickle', use_undefined: bool | None = True, instantiate_object: bool | None = True) -> Any:
    """
    Decompress data using either zlib or gzip compression.
    If serialize is set, the result from decompress is serialized using the specified serialization converting it to a python object.
    Supported options for serialization are JSON or Pickle.

    Args:
        data (bytes): The compressed data to decompress.
        protocol (str, optional): The serialization protocol to use. Default is 'zlib'. Options are 'zlib' and 'gzip'.
        serialize (str, optional): The serialization format to use. Default is 'pickle'. Options are 'json', 'pickle' and None.
        use_undefined (bool, optional): If True, undefined values are included in the serialization. Default is True.
        instantiate_object (bool, optional): If True, the object is instantiated. Default is True.

    Returns:
        Any: If serialize is set returns a Python object otherwise a bytes object.

    Example:
        >>> compressed_data = b'x\x9c\xabV\xcaN\xadT\xb2RP*K\xcc)MU\xaa\x05\x00+\xaf\x05A' # Example of compressed data
        >>> decompress(compressed_data)
        >>> {'key': 'value'}
    """
    if protocol == 'zlib':
        decompress_fn = zlib.decompress
    elif protocol == 'gzip':
        decompress_fn = gzip.decompress
    else:
        raise ValueError(f"Unsupported decompression protocol '{protocol}'. Use 'zlib' or 'gzip'.")

    result = decompress_fn(data)
    if serialize:
        result = loads(result, protocol=serialize, use_undefined=use_undefined, instantiate_object=instantiate_object)

    return result
