import diff_match_patch as dmp_module
from config import SERVER, PORT, RECV_TIMEOUT
import socket
import pickle


def to_bytes(msg):
    return pickle.dumps(msg)


def to_dict(msg):
    return pickle.loads(msg)


class client():
    def __init__(self, name):
        self.name = name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dmp = dmp_module.diff_match_patch()
        self.send_stack = {}
        self.shadow = ""
        self.cv = 0
        self.sv = 0

    def start(self):
        self.socket.connect((SERVER, PORT))
        try:
            msg = "Get:documents"
            self.socket.sendall(to_bytes(msg))
            reply = to_dict(self.socket.recv(4096))
            return reply
        except:
            self.socket.close()
            return []

    def connect(self, document_name, new=False):
        if new:
            msg = "Create:" + document_name
        else:
            msg = "Open:" + document_name
        self.socket.sendall(to_bytes(msg))
        reply = to_dict(self.socket.recv(4096))
        if (reply.startswith("Error")):
            self.socket.close()
            return False, reply
        else:
            self.shadow = reply
            return True, self.shadow

    def add_to_send_stack(self, delta, cv):
        self.send_stack[str(cv)] = delta

    def send_all_stack(self):
        msg = (self.send_stack, self.sv)
        self.socket.sendall(to_bytes(msg))
        print(msg)

    def clear_recieve_buffer(self):
        self.socket.setblocking(False)
        try:
            while self.socket.recv(4096): pass
        except:
            pass
        self.socket.setblocking(True)

    def try_to_recieve(self):
        self.socket.settimeout(RECV_TIMEOUT)
        print("Trying to recieve")
        try:
            return to_dict(self.socket.recv(4096))
        except socket.timeout as e:
            return None

    def send(self, new_text):
        diff = self.dmp.diff_main(self.shadow, new_text)
        delta = self.dmp.diff_toDelta(diff)
        self.add_to_send_stack(delta, self.cv)
        if len(self.dmp.patch_make(diff)) > 0:
            self.cv += 1
        self.shadow = new_text
        self.clear_recieve_buffer()
        self.send_all_stack()
        reply = self.try_to_recieve()
        if reply != None:
            content, rcv = reply
            # Remove recieved changes by the server from the send stack
            current_changes_in_stack = [elem for elem in self.send_stack.keys()]
            for v in current_changes_in_stack:
                if int(v) <= int(rcv):
                    self.send_stack.pop(v)
            # Apply changes recieved from the server to the shadow and original
            for rsv in content.keys():
                diff = self.dmp.diff_fromDelta(delta=content[rsv], text1=self.shadow)
                patches = self.dmp.patch_make(diff)
                updated_text, result = self.dmp.patch_apply(patches, self.shadow)
                self.shadow = updated_text
                if len(patches) > 0:
                    self.sv = int(rsv) + 1
            return self.shadow

    def close(self):
            msg = "Close:" + self.name
            self.socket.sendall(to_bytes(msg))
            self.socket.close()
            return True
