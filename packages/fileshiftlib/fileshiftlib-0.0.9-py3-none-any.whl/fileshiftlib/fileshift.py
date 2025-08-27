from dataclasses import dataclass
import logging
import paramiko

# Creates a logger for this module
logger = logging.getLogger(__name__)


class SFTP(object):
    @dataclass
    class Configuration:
        host: str = "10.0.0.1"
        port: int = 22
        username: str = "admin"
        password: str | None = None

    def __init__(self, host: str, username: str, password: str, port: int = 22, logger: logging.Logger | None = None) -> None:
        """
        Initializes the SFTP client with the given configuration and authenticates.

        Args:
            host (str): The hostname of the SFTP server.
            username (str): The username for authentication.
            password (str): The password for authentication.
            port (int, optional): The port number of the SFTP server. Defaults to 22.
            logger (logging.Logger, optional): Logger instance to use. If None, a default logger is created.
        """
        # Init logging
        # Use provided logger or create a default one
        self._logger = logger or logging.getLogger(name=__name__)

        # Credentials/configuration
        self._configuration = self.Configuration(host=host,
                                                 port=port,
                                                 username=username,
                                                 password=password)

        # Authenticate
        self._transport, self.sftp_client = self.auth()

    def __del__(self) -> None:
        """
        Destructor to clean up the SFTP client and close the transport session.
        """
        self._logger.info(msg="Closes session")

        self._transport.close()
        self.sftp_client.close()

    def auth(self) -> tuple:
        """
        Authenticates with the SFTP server and initializes the SFTP client.

        Returns:
            tuple: A tuple containing the transport and SFTP client objects.
        """
        self._logger.info(msg="Opens session")

        # Connect       
        transport = paramiko.Transport((self._configuration.host, self._configuration.port))
        transport.connect(username=self._configuration.username, password=self._configuration.password)
        sftp_client = paramiko.SFTPClient.from_transport(transport)
        
        return transport, sftp_client
    
    def reconnect(self) -> None:
        """
        Reconnects to the SFTP server by closing the current session and re-authenticating.
        """
        self._logger.info(msg="Reconnects to the SFTP server")
        try:
            self._transport.close()
            self.sftp_client.close()
        except Exception as e:
            self._logger.warning(msg=f"Error closing existing connection: {e}")

        self._transport, self.sftp_client = self.auth()

    def is_connected(self) -> bool:
        """
        Checks if the SFTP connection is currently active.

        Returns:
            bool: True if the connection is active, False otherwise.
        """
        self._logger.info(msg="Checks if the connection is active")

        return self._transport.is_active()

    def list_dir(self, path: str = ".") -> list:
        """
        Lists the names of the contents in the specified folder on the SFTP server.

        Args:
            path (str, optional): The path to the folder on the SFTP server. Defaults to the current directory.

        Returns:
            list: A list of names of the contents in the specified folder.
        """
        self._logger.info(msg="Lists the names of the contents in the specified folder")
        self._logger.info(msg=path)

        return self.sftp_client.listdir(path)

    def change_dir(self, path: str = ".") -> None:
        """
        Changes the current working directory on the SFTP server.

        Args:
            path (str, optional): The path to the folder to change to on the SFTP server. Defaults to the current directory.
        """
        self._logger.info(msg="Changes the current working directory")
        self._logger.info(msg=path)

        self.sftp_client.chdir(path)

    def delete_file(self, filename: str) -> None:
        """
        Deletes a file on the SFTP server.

        Args:
            filename (str): The name of the file to delete on the SFTP server.
        """
        self._logger.info(msg="Deletes a file")
        self._logger.info(msg=filename)

        self.sftp_client.remove(filename)

    def download_file(self, remote_path: str, local_path: str) -> None:
        """
        Downloads a file from the SFTP server to the local machine.

        Args:
            remote_path (str): The path to the file on the SFTP server.
            local_path (str): The path on the local machine where the file will be saved.
        """
        self._logger.info(msg="Downloads a file from the SFTP server to the local machine")
        self._logger.info(msg=remote_path)
        self._logger.info(msg=local_path)

        self.sftp_client.get(remote_path, local_path)

    def upload_file(self, local_path: str, remote_path: str) -> None:
        """
        Uploads a file from the local machine to the SFTP server.

        Args:
            local_path (str): The path to the file on the local machine.
            remote_path (str): The path on the SFTP server where the file will be saved.
        """
        self._logger.info(msg="Uploads a file from the local machine to the SFTP")
        self._logger.info(msg=local_path)
        self._logger.info(msg=remote_path)

        self.sftp_client.put(local_path, remote_path)

# eom
