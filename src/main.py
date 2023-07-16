#!/usr/bin/env python3

# records will be in a csv file
from os import listdir, path, system
import logging
from ftplib import *

# logging.basicConfig(filename='logs.txt', level=logging.INFO)

# phoneFTP = FTP()

# phoneFTP.connect(host='192.168.1.5', port=2121)
# logging.info('connected to mivaan')



class RemoteCon:
    
    def __init__(self, address, username, passwd):
        self.ftp_conn = FTP()
        self.host = address.split(':')[0]
        self.port = int(address.split(':')[1])
        self.username = username
        self.password = passwd
        self.dir = ''
        self.listDIR = None 
        self.connection = None

        try:
            self.ftp_conn.connect(host=self.host, port=self.port)
            self.ftp_conn.login(user=self.username, passwd=self.password)
            self.connection = True

        except Exception as e:
            self.connection = False
            print(f'FTP Exception: {e}')




    def set_dir(self, path):
        self.dir = path
        self.ftp_conn.cwd(self.dir)


    def send(self, file_binary, new_file_name=None):
        """
        sends a file to the remote folder
        :param file_binary: a file opened in binary mode
        :param new_file_name: file name, after sending file at the remote folder
        :return:
        """

        try:
            if new_file_name is None:
                new_file_name = file_binary.name.split(
                        '/' if '/' in file_binary.name else '\\'
                )[-1]
                
                self.ftp_conn.storbinary(
                    f'STOR {self.dir}/{new_file_name}',
                    file_binary
                )

            else:
                self.ftp_conn.storbinary(
                    f'STOR {self.dir}/{new_file_name}',
                    file_binary
                )

        except Exception as e:
            print(f'FTP Exception: {e}')

        file_binary.close()


    def send_folder(self, folder: dict):
        """
        Sends the folder to the connected server
        the folder dict should contain the files in binary mode
        :param folder: dict containing the files in binary mode
        """
        
        def send(folder: dict):
            name = tuple(folder.keys())[0]
            files = folder[name]
            self.create_directory(name)
            self.set_dir(name)


            for file in files:
                if type(file) is dict:
                    send(file)

                else:
                    self.send(file)

        send(folder)


    def create_directory(self, name):
        """
        creates a directory at the connected server
        :param name: name of the directory to be created
        """
        try:
            self.ftp_conn.mkd(name)        

        except all_errors as e:
            print('\
                <<<< FTP error starts >>>> \
                \n{e}\n \
            <<<< FTP error ends >>>>\
        ')



    def dir(self):
        return self.ftp_conn.dir(self.dir)


    def close(self):
        self.ftp_conn.close()



class LocalFolder:
    def __init__(self, name: str, folder: str):
        if folder is None:
            raise ValueError('PATH cannot be NULL')

        elif path.isdir(folder) is False:
            raise ValueError('PATH does not exist')

        elif path.isabs(folder) is False:
            raise ValueError('PATH should be absolute')

        else:
            self.path = folder

        if name is None:
            raise NameError('Name cannot be NULL')
        else:
            self.name = name

        self.contents = listdir(self.path)
        self.items = len(self.contents)
        self.folderName = path.dirname(self.path)

        print(f'"{self.name}" created')


    def update(self):
        """
        updates the instance variables
        about contents of the folder
        """

        self.contents = listdir(self.path)
        self.items = len(self.contents)


    def rename(self, new_name=None):
        """
        renames the current instance
        """

        if new_name is None:
            raise NameError('Name cannot be NULL')
        else:
            old_name = self.name
            self.name = new_name
            print(f'"{old_name}" renamed to "{self.name}"')


    def file_binary(self, local_file_name):
        """
        just returns teh given file in binary mode.
        :param local_file_name: name of the file to be converted
        :return: a file pointer, pointing to a binary file
        """

        return open(f'{self.path}/{local_file_name}', 'rb')


    def folder_binary(self, local_folder_name=None, recur=True):
        """
        creates a list of binary files of given folder.
        the first string in the list is the name of the folder.
        :param local_folder_name: name of the folder to be converted
        :return: a file pointer, pointing to a binary file
        """

        def binary(folder):
            from os import listdir, path 

            content = listdir(folder)
            basename = folder.split('\\')[-1] if '\\' in folder else folder.split('/')[-1]

            files = { basename: [], }

            for chld in content:
                if path.isdir(f'{folder}/{chld}'):
                    files[basename].append(binary(f'{folder}/{chld}'))

                elif path.isfile(f'{folder}/{chld}'):
                    files[basename].append(open(f'{folder}/{chld}', 'rb'))
                    # files[basename].append((f'{folder}/{chld}'))

            return files

        if local_folder_name is None:
            return binary(self.path)



if __name__ == '__main__':
    # college = LocalFolder(name='college', folder='/mnt/Softs_Study/College')
    # dt = (college.file_binary('DateSheet'))
    # print(dt.name)
    # SON = RemoteCon(address='192.168.1.5:2121', username='kabootar', passwd='&Dwcsaw6ti8')
    # SON.set_dir('Son/College')
    # SON.send(dt)
    # TODO check

    foldersToSync = {
        'college': ( 
            '/mnt/Softs_Study/College',
            'Son/'
        ),

        'computer science': (
            '/mnt/Softs_Study/Computer Science',
            'Son/'
        )
    }
                
    notifiy = lambda msg: system(f'notify-send -a python-FTP-sync {msg}')

    # first, we'll establish the connection
    # if the connection is established, log the successful message
    # else, notify the user of the connection failure

    addr = '192.168.1.5:2121'
    conn = RemoteCon(addr, 'kabootar', '&Dwcsaw6ti8')

    if conn.connection:
        print('Connection Successfully established')
    else:
        print('Unable to connect to {addr}')
        notifiy('Unable to connect to {addr}')
        conn.close()
        exit()

    for name, details in foldersToSync.items():
        Lfolder = LocalFolder(name, details[0])
        binaries = Lfolder.folder_binary()
        conn.set_dir(details[1])
        conn.send_folder(binaries)

        