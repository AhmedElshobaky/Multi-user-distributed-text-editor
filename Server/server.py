from threading import Lock
import threading
import diff_match_patch as dmp_module
from config import SERVER, PORT, DOCUMENTS_PATH
import socket
import pickle
import time
import glob
import sys

dmp = dmp_module.diff_match_patch()


def to_bytes(msg):
    return pickle.dumps(msg)


def to_dict(msg):
    return pickle.loads(msg)


def get_files():
    files = []
    for file in glob.glob(DOCUMENTS_PATH + "*.html"):
        files.append(file.split('\\')[-1][:-5])
    return files


server_memory = {
    "available_files": get_files(),  # list of all available documents on server
    #     "test":{
    #                  #Content of the file is saved here and manipulated in the memory to prevent operations on disk
    #                 "content": "text",
    #                 "lock": Lock(),
    #                 "users": [],
    #                 "content_changed": False,
    #                 "buffer": open("test.txt", "r+")
    #                 }
}


def force_close():
    open_files = [elem for elem in server_memory.keys()]
    for file in open_files[1:]:
        server_memory[file]['buffer'].close()
        server_memory.pop(file)


memory_L = Lock()


class client_connection(threading.Thread):
    def __init__(self, conn, addr):
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
        with memory_L:
            if name in server_memory.keys():
                server_memory[name]['users'].append(self.addr)
                return server_memory[name]['content']

            if name not in server_memory["available_files"]:
                with open(DOCUMENTS_PATH + name + '.html', 'w') as f:
                    f.write('')
                server_memory["available_files"].append(name)

            if name in server_memory["available_files"]:
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

                f = server_memory[self.doc_name]['buffer']
                f.seek(0)
                f.write(server_memory[self.doc_name]['content'])
                f.truncate()

                server_memory[self.doc_name]['users'].remove(self.addr)
            if len(server_memory[self.doc_name]['users']) == 0:
                server_memory.pop(self.doc_name)
                f.close()

            self.conn.close()
            self.exit_code = 1

    def add_to_send_stack(self, delta, sv):
        self.send_stack[str(sv)] = delta

    def send_all_stack(self):
        msg = (self.send_stack, self.cv)
        out = self.conn.sendall(to_bytes(msg))

    def clear_stack(self):
        self.send_stack = {}

    def run(self):
        while self.exit_code == 0:

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
                #                 print("Enter",self.addr,self.sv,self.backup,self.shadow,server_memory[self.doc_name]['content'])
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

                # Remove recieved changes by the client from the send stack
                current_changes_in_stack = [elem for elem in self.send_stack.keys()]
                for v in current_changes_in_stack:
                    if int(v) <= int(rsv):
                        self.send_stack.pop(v)

                # Send updates found on the original to client
                with server_memory[self.doc_name]['lock']:
                    diff = dmp.diff_main(self.shadow, server_memory[self.doc_name]['content'])
                    delta = dmp.diff_toDelta(diff)
                    self.add_to_send_stack(delta, self.sv)
                    patches = dmp.patch_make(diff)
                    self.shadow = server_memory[self.doc_name]['content']
                    if len(patches) > 0:
                        self.sv += 1
                self.send_all_stack()


#                 print("End",self.addr,self.sv,self.backup,self.shadow,server_memory[self.doc_name]['content'])
#             print(server_memory['test']['content'])
class backup(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            time.sleep(30)
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
