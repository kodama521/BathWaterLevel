# -*- coding: utf-8 -*-
import paramiko
import scp

class MySsh(object):
    def __init__(self, hostname, port, username, password):
        self.__hostname = hostname
        self.__port = port
        self.__username = username
        self.__password = password

    def scp(self, local_fname, remote_path):
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.__hostname,
                        port=self.__port,
                        username=self.__username,
                        password=self.__password)

            with scp.SCPClient(ssh.get_transport()) as scp_client:
                scp_client.put(local_fname, remote_path)
                print('scp success!!')

    def exec_command(self, command):
        _, stdout, stderr = ssh.exec_command(command)
        print('-----stdout-------')
        for out in stdout:
            print(out.strip())

        print('-----stderr-------')
        for err in stderr:
            print(err.strip())


if __name__ == '__main__':
    HOSTNAME='192.168.1.100'
    PORT=22
    USERNAME='pi'
    PASSWORD='ks6056kk'

    my_ssh = MySsh(HOSTNAME, PORT, USERNAME, PASSWORD)

    my_ssh.scp('../config.csv', 'Hobby/BathWaterLevel')

#    my_ssh.exec_command('ls')  need ssh install
