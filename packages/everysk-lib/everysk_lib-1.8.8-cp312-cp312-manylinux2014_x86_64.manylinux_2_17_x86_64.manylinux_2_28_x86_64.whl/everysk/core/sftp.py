###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
import os
from io import StringIO
from subprocess import DEVNULL, PIPE
from subprocess import run as command
from types import TracebackType

from paramiko import AutoAddPolicy, SFTPAttributes, SFTPClient, SSHClient, rsakey

from everysk.config import settings
from everysk.core.datetime import Date, DateTime
from everysk.core.object import BaseObject

###############################################################################
#   KnownHosts Class Implementation
###############################################################################
class KnownHosts(BaseObject):
    content: dict[str, str] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load()

    @property
    def filename(self) -> str:
        """
        Get the known_hosts file full path.
        """
        return os.path.join(settings.EVERYSK_SFTP_DIR, 'known_hosts')

    def _verify_file_exist(self) -> bool:
        # If the file already exists we stop here
        if os.path.exists(self.filename):
            return True

        # If the directory does not exist we need to create it
        dir = os.path.dirname(self.filename)  # pylint: disable=redefined-builtin
        if not os.path.exists(dir):
            os.makedirs(dir)

        # If the file does not exist, we create an empty one
        # https://stackoverflow.com/a/12654798
        open(self.filename, 'w', encoding='utf-8').close()  # pylint: disable=consider-using-with
        return True

    def add(self, hostname: str) -> None:
        """
        Add the hostname to the known_hosts in the cache and local file.

        Args:
            hostname (str): The hostname to add to the known_hosts. Example: 'files.example.com'
        """
        # Use the ssh-keyscan to get the key of the hostname
        result = command(['ssh-keyscan', hostname], stdout=PIPE, check=False, stderr=DEVNULL)
        # Add the key to the known_hosts locally
        self.content[hostname] = result.stdout.decode('utf-8')
        # Save the known_hosts to the local file
        self.write()

    def check(self, hostname: str) -> bool:
        """
        Check if the hostname is already in the known_hosts.

        Args:
            hostname (str): The hostname to check in the known_hosts. Example: 'files.example.com'
        """
        return hostname in self.content

    def delete(self, hostname: str) -> None:
        """
        Delete the hostname from the known_hosts in the cache and local file.

        Args:
            hostname (str): The hostname to delete from the known_hosts. Example: 'files.example.com'
        """
        if hostname in self.content:
            del self.content[hostname]
            self.write()

    def load(self) -> None:
        """
        Load the known_hosts from the local file $HOME/.ssh/known_hosts.
        """
        if self._verify_file_exist():
            with open(self.filename, 'r', encoding='utf-8') as fd:
                self.content = {line.split(' ')[0]: line for line in fd.readlines()}

    def write(self) -> None:
        """
        Write the known_hosts to the local file $HOME/.ssh/known_hosts for future use.
        """
        if self._verify_file_exist():
            with open(self.filename, 'w', encoding='utf-8') as fd:
                fd.writelines(self.content.values())
                # Ensure the file is written to disk
                fd.flush()
                os.fsync(fd.fileno())


###############################################################################
#   SFTP Class Implementation
###############################################################################
class SFTP(BaseObject):
    """
    SFTP class to connect to the SFTP server.
    We could use the context manager to automatically close the connection when the object is deleted/destroyed.

    Args:
        compress (bool): If the connection will transfer compressed data. Defaults to True.
        date (Date, DateTime): The date/datetime used to parse the name. Defaults to today.
        hostname (str): The hostname of the SFTP server. Defaults to None.
        password (str): The password of the SFTP server. Defaults to None.
        private_key (str): The private key of the SFTP server. Defaults to None.
        passphrase (str): The passphrase of the private key. Defaults to None.
        port (int): The port of the SFTP server. Defaults to 22.
        timeout (int): The timeout of the SFTP connection. Defaults to 60.
        username (str): The username of the SFTP server. Defaults to None.

    Example:

        >>> from everysk.core.sftp import SFTP
        >>> with SFTP(username='', password='', hostname='') as sftp:
        ...     filename = sftp.search_by_last_modification_time(path='/dir', prefix='file_')
        >>> print(filename)
        /dir/2024/11/13/file_11.12.2024.csv
    """

    ## Private attributes
    _client: SFTPClient = None

    ## Public attributes
    compress: bool = True
    date: Date | DateTime = None
    hostname: str = None
    password: str = None
    private_key: str = None
    passphrase: str = None
    port: int = 22
    timeout: int = 60
    username: str = None

    @property
    def client(self) -> SFTPClient:
        """
        Get the SFTP client to connect to the SFTP server.
        """
        if self._client is None:
            self._client = self.get_sftp_client(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                private_key=self.private_key,
                passphrase=self.passphrase,
                compress=self.compress,
                timeout=self.timeout
            )

        return self._client

    ## Private methods
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str = None,
        port: int = 22,
        private_key: str = None,
        passphrase: str = None,
        date: Date | DateTime = None,
        compress: bool = True,
        timeout: int = 60,
        **kwargs
    ):
        """
        Constructor to initialize the SFTP connection.

        Args:
            hostname (str, optional): The hostname of the SFTP server. Defaults to None.
            username (str, optional): The username of the SFTP server. Defaults to None.
            password (str, optional): The password of the SFTP server. Defaults to None.
            port (int, optional): The port of the SFTP server. Defaults to 22.
            private_key (str, optional): The private key of the SFTP server. Defaults to None.
            passphrase (str, optional): The passphrase of the private key. Defaults to None.
            date (Date, DateTime, optional): The date/datetime used to parse the name. Defaults to today.
            compress (bool, optional): If the connection will transfer compressed data. Defaults to True.
            timeout (int, optional): The timeout of the SFTP connection. Defaults to 60.
        """
        if date is None:
            date = Date.today()

        super().__init__(
            compress=compress,
            date=date,
            hostname=hostname,
            password=password,
            port=port,
            private_key=private_key,
            passphrase=passphrase,
            timeout=timeout,
            username=username,
            **kwargs
        )

    def __del__(self):
        """
        Destructor to close the SFTP connection when the object is deleted/destroyed.
        """
        try:
            if self._client is not None:
                # Close the SFTP connection when the object is deleted/destroyed
                self._client.close()
        except Exception:  # pylint: disable=broad-except
            pass

    def __enter__(self):
        """
        Enter the context manager to return the object itself.
        """
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ):
        """
        https://docs.python.org/3/library/stdtypes.html#contextmanager.__exit__

        Returns:
            bool | None: If return is False any exception will be raised.
        """
        try:
            if self._client is not None:
                # Close the SFTP connection
                self._client.close()
                # Reset the SFTP client
                self._client = None
        except Exception:  # pylint: disable=broad-except
            pass

    def sort(self, lst: list, attr: str, reverse: bool = False) -> list:
        """
        Sort the list of objects by the attribute with order by asc or desc.
        If the attribute is not found, the list will be returned as is.
        If reverse is True, the list will be sorted in descending order.

        Args:
            lst (list): The list of objects to sort.
            attr (str): The name of the attribute to sort.
            reverse (bool, optional): The final order of the list. Defaults to False.
        """
        return sorted(lst, key=lambda obj: getattr(obj, attr), reverse=reverse)

    ## Public methods
    def get_sftp_client(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str = None,
        compress: bool = None,
        timeout: int = None,
        private_key: str = None,
        passphrase: str = None,
    ) -> SFTPClient:
        """
        Connect to the SFTP server and return the SFTP client.

        Args:
            hostname (str): The hostname of the SFTP server.
            port (int): The port of the SFTP server.
            username (str): The username of the SFTP server.
            password (str): The password of the SFTP server.
            compress (bool): If the connection will transfer compressed data.
            timeout (int): The timeout of the SFTP connection.
            private_key (str): The private key of the SFTP server.
            passphrase (str): The passphrase of the private key.
        """
        ssh = SSHClient()
        # On this point we create the file if it does not exists
        # known_hosts = KnownHosts()
        # Check if the hostname is already known
        # if not known_hosts.check(hostname):
        #     # Add the hostname to the known_hosts and write to the local file
        #     known_hosts.add(hostname)

        params = {
            'hostname': hostname,
            'port': port,
            'username': username,
            'compress': compress,
            'timeout': timeout,
        }

        # check if we have the password
        if password is not None:
            params['password'] = password
        elif private_key is not None:
            key_file = StringIO(private_key)
            params['pkey'] = rsakey.RSAKey.from_private_key(key_file)
            params['passphrase'] = passphrase

        # Load the known_hosts file
        # This was placed before the connection to have time for Google sync the file creation
        # https://everysk.atlassian.net/browse/COD-10872
        # ssh.load_system_host_keys(filename=known_hosts.filename)
        ssh.set_missing_host_key_policy(AutoAddPolicy)  # nosec B507

        ssh.connect(**params)
        return ssh.open_sftp()

    def get_file(self, filename: str) -> bytes | None:
        """
        Get the file content from the SFTP server.
        If the file is not found, return None.
        If the filename has a date format, it will be parsed with the date attribute.
        Example: '/dir/%Y/file_%Y.csv' -> '/dir/2024/file_2024.csv'

        Args:
            filename (str): The filename with the path to get the content. Example: '/dir/2024/file_2024.csv'
        """
        if '%' in filename:
            filename = self.parse_date(filename, self.date)

        try:
            with self.client.open(filename, 'rb') as fd:
                return fd.read()
        except IOError:
            # If the file is not found, return None
            pass

        return None

    def save_file(self, filename: str, content: bytes) -> None:
        """
        Save the file content to the SFTP server.
        If the filename has a date format, it will be parsed with the date attribute.
        Example: '/dir/%Y/file_%Y.csv' -> '/dir/2024/file_2024.csv'

        Args:
            filename (str): The filename with the path to save the content. Example: '/dir/2024/file_2024.csv'
            content (bytes): The content of the file to save.
        """
        if '%' in filename:
            filename = self.parse_date(filename, self.date)

        # Split the path to create the directories if not exists
        # the first element is empty, so we need to remove it
        dirs = os.path.dirname(filename).split('/')[1:]
        path = ''
        for dir in dirs:  # pylint: disable=redefined-builtin
            path = f'{path}/{dir}'
            try:
                self.client.mkdir(path)
            except IOError:
                pass

        with self.client.open(filename, 'wb') as fd:
            fd.write(content)

    def search_by_last_modification_time(self, path: str, prefix: str) -> str | None:
        """
        Search the file by the last modification time with the prefix in the path recursively.
        If the file is not found, return None.
        If the path or prefix has a date format, it will be parsed with the date attribute.
        Example: '/dir/%Y' -> '/dir/2024' or 'file_%m.%d.%Y' -> 'file_11.30.2024'

        Args:
            path (str): The path to start search the file.
            prefix (str): The prefix of the file to search. Example: 'file_' or 'file_%m.%d.%Y'
        """
        if '%' in prefix:
            prefix = self.parse_date(prefix, self.date)
        if '%' in path:
            path = self.parse_date(path, self.date)

        objs: list[SFTPAttributes] = self.client.listdir_attr(path)
        objs = self.sort(objs, 'st_mtime', reverse=True)
        for file in objs:
            if file.filename.startswith(prefix):
                return f'{path}/{file.filename}'

            if file.longname.startswith('d'):
                result = self.search_by_last_modification_time(f'{path}/{file.filename}', prefix)
                if result:
                    return result

        return None

    def parse_date(self, name: str, date: Date) -> str:
        """
        Parse the date format in the name with the date attribute.
        Example: '/dir/%Y/file_%Y.csv' -> '/dir/2024/file_2024.csv'

        Args:
            name (str): The name with the date format to parse.
            date (Date): The date to parse the date format.
        """
        if '%' in name:
            index = name.find('%')
            date_format = name[index : index + 2]
            result = date.strftime(date_format)
            name = name.replace(date_format, result)
            if '%' in name:
                return self.parse_date(name, date)

        return name
