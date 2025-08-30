import paramiko


class Sftp:
    """A class that handles imports and exports of data from and to an SFTP server."""

    def __init__(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str = None,
        private_key_dir: str = None,
        authentication_type: str = "password",
        sftp_session: paramiko.SFTPClient = None,
        transport: paramiko.Transport = None,
    ):
        """
        Constructor method.

        Args:
            hostname: SFTP server hostname
            port: SFTP server port
            username: Username to connect to the SFTP server
            password: Password to connect to the SFTP server (only needed if
                authentication_type="password")
            private_key_dir: Directory of file containing the private key to connect to the SFTP
                server (only needed if authentication_type="private_key")
            authentication_type: Can take value "password" or "private_key"
            sftp_session: SFTP session object
            transport: Transport object

        Raises:
            ValueError: Raises an error in case of invalid authentication type
        """
        # Input validation
        valid_authentication_types = ["password", "private_key"]
        if authentication_type not in valid_authentication_types:
            raise ValueError(
                f"Invalid input 'authentication_type' value '{authentication_type}'. "
                f"Supported values: {valid_authentication_types}."
            )

        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.private_key_dir = private_key_dir
        self.authentication_type = authentication_type
        self.sftp_session = sftp_session
        self.transport = transport

    def open_session(self):
        """Opens an SFTP session."""
        # Establish an SSH client and connect to the server
        try:
            self.transport = paramiko.Transport((self.hostname, self.port))
            self.transport.connect(username=self.username, password=self.password)

            # Open an SFTP session
            self.sftp_session = paramiko.SFTPClient.from_transport(self.transport)

        except Exception as e:
            print(f"Error: {e}")

    def close_session(self):
        """Closes an SFTP session and transport."""
        self.sftp_session.close()
        self.transport.close()

    def get_file(self, remote_dir: str, local_dir: str):
        """
        Imports a file from an SFTP server to a local directory.

        Args:
            remote_dir: SFTP server file directory
            local_dir: Local file directory
        """
        self.sftp_session.get(remote_dir, local_dir)

    def put_file(self, local_dir: str, remote_dir: str):
        """
        Exports a file from a local directory to an SFTP server.

        Args:
            local_dir: Local file directory
            remote_dir: SFTP server file directory
        """
        self.sftp_session.put(local_dir, remote_dir)
