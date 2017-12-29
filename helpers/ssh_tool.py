import paramiko
import scp
import os
from logger.logger import Logger


class SSHTool(object):
    '''
    This class is used to work with Linux machines through SSH.
    '''

    def __init__(self, host, username, password, key='/root/.ssh/id_rsa'):
        '''
        :param host: the server to connect to through SSH
        :param username: the username to authenticate as
        :param password: password for the private key
        :param key: path to the private key for the authentication
        '''

        self.host = host
        self.username = username
        self.pkey = paramiko.RSAKey.from_private_key_file(key, password)
        self.password = password
        self.ssh = paramiko.SSHClient()
        self.scp_client = scp.SCPClient
        self.logger = Logger()
        self.module_path = os.path.abspath(__file__)

    def establish_connection(self):
        transport = self.ssh.get_transport()
        if transport is None or not transport.is_active():
            try:
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(self.host, pkey=self.pkey, username=self.username, password=self.password)
                self.logger.log(self.module_path,
                                "DEBUG",
                                "Connection to {0} has been successfully established".format(self.host))
            except Exception, exp:
                self.logger.log(self.module_path,
                                "ERROR",
                                "Connection has not been established to host. Please check: \
                                input parameters: host: {0}, pkey: {1}, username: {2}, password: {3}, \
                                exception: {4}".format(self.host, self.pkey, self.username, self.password, exp))
                return False
        return True

    def terminate_connection(self):
        self.logger.log(self.module_path, "DEBUG",
                        "Connection to {0} has been closed")
        self.ssh.close()

    def send_ssh_command(self, ssh_command):
        '''
        :param ssh_command: SSH command that should be executed
        :return:
            stdin, stdout, strerr messages
        '''
        self.establish_connection()
        stdin, stdout, stderr = self.ssh.exec_command(ssh_command)
        stdout = stdout.read()
        stderr = stderr.read()

        self.terminate_connection()

        if stderr:
            self.logger.log(self.module_path, "ERROR", stderr)

        self.logger.log(self.module_path, "DEBUG", stdout)
        return stdin, stdout, stderr

    def upload_files(self, local_path, remote_path, put_files=True):
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
            scp = self.scp_client(self.ssh.get_transport())

            if isinstance(local_path, str) and isinstance(remote_path, str):
                local_path = [local_path]
                remote_path = [remote_path]

            if isinstance(local_path, list) and isinstance(remote_path, list):
                for i, l_path in enumerate(local_path):
                    scp.put(l_path, remote_path[i], recursive=True)

                self.logger.log(self.module_path, "DEBUG",
                                "File {0} was successfully moved to host {1} in {2}".format(local_path, self.host,
                                                                                            remote_path))
        except Exception, e:
            self.logger.log(self.module_path, "DEBUG",
                            "File {0} wasn't moved to host {1} in {2}, due to exception: {3}".format(local_path,
                                                                                                     self.host,
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
            scp = self.scp_client(self.ssh.get_transport())

            if isinstance(local_path, str) and isinstance(remote_path, str):
                local_path = [local_path]
                remote_path = [remote_path]

            if isinstance(local_path, list) and isinstance(remote_path, list):
                for i, l_path in enumerate(local_path):
                    scp.get(remote_path[i], l_path, recursive=True)

                self.logger.log(self.module_path, "DEBUG",
                                "File {0} was successfully moved from host {1} to {2}".format(remote_path, self.host,
                                                                                              local_path))
        except Exception, e:
            self.logger.log(self.module_path, "DEBUG",
                            "File {0} wasn't moved to host {1} in {2}, due to exception: {3}".format(remote_path,
                                                                                                     self.host,
                                                                                                     local_path, e))
        finally:
            self.terminate_connection()


if __name__ == "__main__":
    sshtool = SSHTool(r'fedorapeople.org', r'esakaiev', r'zaq1@WSX#EDC(_', r'//home//esaka//.ssh//id_rsa')
    # sshtool.send_ssh_command('sudo ansible-playbook --tags=classic /home/fedora/upstream/iproute/tests.yml')
