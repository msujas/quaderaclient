import socket
from .quaderaexporter import PORT

class QuadExClient():
    def __init__(self, host='localhost', port=PORT):
        self.host = host
        self.port = port
    def sendmessage(self, message:str):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host,self.port))
        s.sendall(f'{message}\n'.encode())
        return s.recv(1024).decode()
    def runexporter(self, exportname, localname):
        data = self.sendmessage(f'run {exportname}|{localname}')
        return data
    def stopexporter(self):
        data = self.sendmessage('stop')
        return data
    def getstatus(self):
        return self.sendmessage('status')