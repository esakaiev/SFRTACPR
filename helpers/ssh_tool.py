import paramiko
import scp
import os
import pyping
from logger.logger import Logger


class SSHTool(object):
    '''
    This class is used to work with Linux machines through SSH.
    '''
    _module_path = os.path.abspath(__file__)

    def __init__(self, host, username, password, key=r'/root/.ssh/id_rsa'):
        '''
        :param host: the server to connect to through SSH
        :param username: the username to authenticate as
        :param password: password for the private key
        :param key: path to the private key for the authentication
        '''

        self._host = host
        self._username = username
        self._pkey = paramiko.RSAKey.from_private_key_file(key, password)
        self._password = password
        self._ssh = paramiko.SSHClient()
        self._scp_client = scp.SCPClient
        self._logger = Logger()

    def establish_connection(self):
        result = True

        transport = self._ssh.get_transport()
        if transport is None or not transport.is_active():
            try:
                self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self._ssh.connect(self._host, pkey=self._pkey, username=self._username, password=self._password)
                self._logger.log(self.module_path,
                                 "DEBUG",
                                 "Connection to {0} has been successfully established".format(self._host))
            except Exception, exp:
                self._logger.log(self.module_path,
                                 "ERROR",
                                 "Connection has not been established to host. Please check: \
                                 input parameters: host: {0}, pkey: {1}, username: {2}, password: {3}, \
                                 exception: {4}".format(self._host, self._pkey, self._username, self._password,
                                                        exp))
                result = False
        return result

    def terminate_connection(self):
        self._logger.log(self.module_path, "DEBUG",
                         "Connection to {0} has been closed")
        self._ssh.close()

    def send_ssh_command(self, ssh_command):
        '''
        :param ssh_command: SSH command that should be executed
        :return:
            stdin, stdout, strerr messages
        '''
        self.establish_connection()
        stdin, stdout, stderr = self._ssh.exec_command(ssh_command)
        stdout = stdout.read()
        stderr = stderr.read()

        self.terminate_connection()

        self._logger.log(self.module_path, "DEBUG", stderr)
        self._logger.log(self.module_path, "DEBUG", stdout)
        return stdin, stdout, stderr

    def upload_files(self, local_path, remote_path):
        '''
            This method is used to copy files on remote
            :param local_path: Path to file on localhost
            :param remote_path: Path to file on remote machine

            :Example:
            >> upload_files('/tmp/test.log', '/tmp/test.log') # moving files to Linux machine
            >> upload_files('/tmp/test/', '/tmp/test/') # moving files to Linux machine
            >> upload_files(['/tmp/test.log', '/tmp/test1.log'] , ['/tmp/test.log', '/tmp/test1.log'])
        '''
        self.establish_connection()
        try:
            scp = self._scp_client(self._ssh.get_transport())

            if isinstance(local_path, str) and isinstance(remote_path, str):
                local_path = [local_path]
                remote_path = [remote_path]

            if isinstance(local_path, list) and isinstance(remote_path, list):
                for i, l_path in enumerate(local_path):
                    scp.put(l_path, remote_path[i], recursive=True)

                self._logger.log(self.module_path, "DEBUG",
                                 "File {0} was successfully moved to host {1} in {2}".format(local_path, self._host,
                                                                                             remote_path))
        except Exception, e:
            self._logger.log(self.module_path, "DEBUG",
                             "File {0} wasn't moved to host {1} in {2}, due to exception: {3}".format(local_path,
                                                                                                      self._host,
                                                                                                      remote_path, e))
        finally:
            self.terminate_connection()

    def download_files(self, remote_path, local_path):
        '''
            This method is used to copy files on remote
            :param local_path: Path to file on localhost
            :param remote_path: Path to file on remote machine

            :Example:
            >> download_files('/tmp/test.log', '/tmp/test.log') # moving files to Linux machine
            download_files('/tmp/test/', '/tmp/test/') # moving files to Linux machine
            >> download_files(['/tmp/test.log', '/tmp/test1.log'] , ['/tmp/test.log', '/tmp/test1.log'])
        '''
        self.establish_connection()
        try:
            scp = self._scp_client(self._ssh.get_transport())

            if isinstance(local_path, str) and isinstance(remote_path, str):
                local_path = [local_path]
                remote_path = [remote_path]

            if isinstance(local_path, list) and isinstance(remote_path, list):
                for i, l_path in enumerate(local_path):
                    scp.get(remote_path[i], l_path, recursive=True)

                self._logger.log(self.module_path, "DEBUG",
                                 "File {0} was successfully moved from host {1} to {2}".format(remote_path, self._host,
                                                                                               local_path))
        except Exception, e:
            self._logger.log(self.module_path, "DEBUG",
                             "File {0} wasn't moved to host {1} in {2}, due to exception: {3}".format(remote_path,
                                                                                                      self._host,
                                                                                                      local_path, e))
        finally:
            self.terminate_connection()

    @property
    def module_path(self):
        return SSHTool._module_path


if __name__ == "__main__":
    sshtool = SSHTool(r'fedorapeople.org', r'esakaiev', r'zaq1@WSX#EDC(_', r'//home//esaka//.ssh//id_rsa')
    # sshtool.send_ssh_command('sudo ansible-playbook --tags=classic /home/fedora/upstream/iproute/tests.yml')
