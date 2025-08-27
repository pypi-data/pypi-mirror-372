import paramiko
from scp import SCPClient


class Transport:

    def __init__(self, server, port, user, password):
        self.ssh = self._createSSHClient(server=server, port=port, user=user, password=password)
        self.scp = SCPClient(self.ssh.get_transport())

    @staticmethod
    def _createSSHClient(server, port, user, password):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        return client


