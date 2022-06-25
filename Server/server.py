from threading import Lock
import threading
import diff_match_patch as dmp_module
from config import SERVER, PORT, DOCUMENTS_PATH,BACKUP_RATE
import socket
import pickle
import time
import glob
import sys

#Creating the diff_match_patch object, that allows us to preform the diff
# between strings, and patch changes to the current texr
dmp = dmp_module.diff_match_patch()

class backup(threading.Thread):
    '''
    This is the backup thread, the backup thread manages updating the documents
    on disk and saving some buckups, this is very important since all open files are
    loaded in the memory, so if the server was terminated for any reason, all progress
    of these documents will be lost, so this thread every BACKUP_RATE it loops over
    all open files and if it was changed it writes the chanes to the disk.
    '''
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            time.sleep(BACKUP_RATE)
            open_files =  [elem for elem in server_memory.keys()]
            for file in open_files[1:]:
                with server_memory[file]['lock']:
                    print(server_memory[file]['content_changed'])
                    if server_memory[file]['content_changed']:
                        print("backed up:", file)
                        f = server_memory[file]['buffer']
                        f.seek(0)
                        f.write(server_memory[file]['content'])
                        f.truncate()
                        server_memory[file]['content_changed'] = False


def to_bytes(msg):
    '''
    Utility function that serialize any python object, to be sent over the socket
    '''
    return pickle.dumps(msg)


def to_dict(msg):
    '''
        Utility function that digest the recieved bytes and transform it back to the correct representation
    '''
    return pickle.loads(msg)


def get_files():
    '''
        Utility function that get all the files available on the server
    '''
    files = []
    for file in glob.glob(DOCUMENTS_PATH + "*.html"):
        files.append(file.split('\\')[-1][:-5])
    return files


'''
This following represents the server memory, our server memory consist mainly of two things:
a) list of all available files on the server
b) open file data structure 

Open File Data structure:
File Name:{
    ->                 "content": "text",                        Conetnt of the actual file 
    ->                 "lock": Lock(),                           A mutex lock to prevent race conditions 
    ->                 "users": [],                              List of users connected to that document 
    ->                 "content_changed": False,                 Flag is set when content was manpipulated bu users
    ->                 "buffer": open("test.txt", "r+")          This is the buffer of the file on disk
     }

This structure allows multiple users manipulating the same document, also it limits the number 
of disk operations as most of the changes are done in the memory and periodically 
sycnhronized with the files on disk
'''
server_memory = {
    "available_files": get_files(),  # list of all available documents on server
    #     "test":{
    #                 "content": "text",                        Conetnt of the actual file
    #                 "lock": Lock(),                           A mutex lock to prevent race conditions
    #                 "users": [],                              List of users connected to that document
    #                 "content_changed": False,                 Flag is set when content was manpipulated bu users
    #                 "buffer": open("test.txt", "r+")          This is the buffer of the file on disk
    #                 }
}
"""
Memory Lock is a mutex lock that must be acquired when a thread opens new file or closes an open file
this is very important to prevent any race conditions and to maintain the integrity of the server memory.
"""
memory_L = Lock()

def force_close():
    """
    Function to force close all files open by the server to prevent
    leaving file buffers open and lose their pointers
    """
    open_files = [elem for elem in server_memory.keys()]
    for file in open_files[1:]:
        server_memory[file]['buffer'].close()
        server_memory.pop(file)





class client_connection(threading.Thread):
    def __init__(self, conn, addr):
        '''
        Intialise a worker thread that handles all communications with users
        :param conn: Connection object
        :param addr: Address of the connected user
        '''
        threading.Thread.__init__(self)
        self.exit_code = 0
        print ("New connection added: ", addr)
        self.conn = conn
        self.addr = addr
        self.send_stack = {}
        self.doc_name = ""
        self.shadow = ""
        self.backup = ""
        self.cv = 0
        self.sv = 0

    def open_file(self, name):
        """
        Opens a specfic file and open its content to the server memory
        String :param name: filename
        String :return : content of the opened file, if no file was found it creates a new one and return an empty string
        """
        with memory_L: #Acquire memory lock
            if name in server_memory.keys(): #Name already opened in memory
                server_memory[name]['users'].append(self.addr)
                return server_memory[name]['content']

            if name not in server_memory["available_files"]: #File is not available in the server,so create it
                with open(DOCUMENTS_PATH + name + '.html', 'w') as f:
                    f.write('')
                server_memory["available_files"].append(name)

            if name in server_memory["available_files"]:  # File was found and opened in memory
                doc = open(DOCUMENTS_PATH + name + '.html', 'r+')
                server_memory[name] = {
                    "content": doc.read(),
                    "lock": Lock(),
                    "users": [self.addr],
                    "content_changed": False,
                    "buffer": doc
                }
            return server_memory[name]['content']

    def config(self, data):
        '''
        This handles all configuration requests at the start of the connection with the user, Config messages includes:
         -> get operation to get all available files on the server
         -> Open to open a specfic file
         -> Close close server connection with the user
        String :param data: msg recieved
        Bytes :return: appropiate response
        '''
        req = data.split(":")
        if (req[0] == "Get"):
            return to_bytes(server_memory["available_files"])
        elif (req[0] == "Open"):
            content = self.open_file(req[1])
            self.doc_name = req[1]
            self.shadow = content
            self.backup = content
            return to_bytes(content)
        elif (req[0] == "Close" and len(self.doc_name) > 0):
            with server_memory[self.doc_name]['lock']:
                #Sync file content with disk
                f = server_memory[self.doc_name]['buffer']
                f.seek(0)
                f.write(server_memory[self.doc_name]['content'])
                f.truncate()

                #Remove user from document
                server_memory[self.doc_name]['users'].remove(self.addr)

            if len(server_memory[self.doc_name]['users']) == 0: # if no users have the document opened, remove it from memory
                server_memory.pop(self.doc_name)
                f.close()

            #Close connection
            self.conn.close()
            #Terminate this thread
            self.exit_code = 1

    def add_to_send_stack(self, delta, sv):
        '''
        Add changes to the send stack
        :param delta: changes
        :param sv: server version
        '''
        self.send_stack[str(sv)] = delta

    def send_all_stack(self):
        '''
        Send the stack to user
        '''
        msg = (self.send_stack, self.cv)
        out = self.conn.sendall(to_bytes(msg))

    def clear_stack(self):
        '''
        Clear all content of the stack
        '''
        self.send_stack = {}

    def run(self):
        while self.exit_code == 0: #Check if the thread should be terminated

            data = self.conn.recv(4096)

            if not data:
                continue
            print(self.addr, self.cv, self.sv)
            # Connection just started and the folllowing handles configuration requests
            if isinstance(to_dict(data), str):
                response = self.config(to_dict(data))
                if response != None:
                    self.conn.sendall(response)
            else:  # Handle data messages
                changes, rsv = to_dict(data)
                if int(rsv) < self.sv:  # Rollback to backup
                    print("Rolling back")
                    self.shadow = self.backup
                    self.sv -= 1
                    self.clear_stack()

                for rcv in changes.keys():
                    if int(rcv) < self.cv:
                        continue
                    diff = dmp.diff_fromDelta(delta=changes[rcv], text1=self.shadow)
                    patches = dmp.patch_make(diff)
                    updated_text, result = dmp.patch_apply(patches, self.shadow)
                    self.shadow = updated_text
                    if len(patches) > 0:
                        self.cv = int(rcv) + 1

                    with server_memory[self.doc_name]['lock']:
                        updated_text, result = dmp.patch_apply(patches, server_memory[self.doc_name]['content'])
                        server_memory[self.doc_name]['content'] = updated_text
                        server_memory[self.doc_name]['content_changed'] = True

                    self.backup = updated_text

                # Remove already recieved changes by the client from the send stack
                current_changes_in_stack = [elem for elem in self.send_stack.keys()]
                for v in current_changes_in_stack:
                    if int(v) <= int(rsv):
                        self.send_stack.pop(v)

                # Send updates found by other clients to the connected user
                with server_memory[self.doc_name]['lock']:
                    diff = dmp.diff_main(self.shadow, server_memory[self.doc_name]['content'])
                    delta = dmp.diff_toDelta(diff)
                    self.add_to_send_stack(delta, self.sv)
                    patches = dmp.patch_make(diff)
                    self.shadow = server_memory[self.doc_name]['content']
                    if len(patches) > 0:
                        self.sv += 1
                self.send_all_stack()



class server ():
    def __init__(self):
        pass
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((SERVER, PORT))
            backup_thread = backup()
            backup_thread.start()
            while True:

                server.listen(1)
                clientsock, clientAddress = server.accept()
                newthread = client_connection( clientsock,clientAddress)
                newthread.start()


if __name__ == "__main__":
    s = server()
    s.start()
