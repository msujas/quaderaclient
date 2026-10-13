import socket

class Quadera:
    def __init__(self, host, port=15000, timeout=120):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.file = self.sock.makefile("rw", encoding="utf-8", newline="\n")

    def cmd(self, line):
        """Send one command; return the text after 'OK', raise on 'ERR'."""
        self.file.write(line + "\n")
        self.file.flush()
        reply = self.file.readline().rstrip("\r\n")
        if not reply.startswith("OK"):
            raise RuntimeError(f"{line!r} -> {reply or 'connection closed'}")
        return reply[2:].strip()
    def openProjectFile(self, template, outputfile):
        '''
        template -  .qmt file
        outputfile - .qmp file
        '''
        return self.cmd(f"OPEN {template}|{outputfile}")
    def start(self):
        return self.cmd(f"START")
    def stop(self):
        return self.cmd(f"STOP")
    def exportData(self, fname:str):
        if not fname:
            return self.cmd(f"EXPORT")
        if not fname.endswith('.asc'):
            fname += '.asc'
        return self.cmd(f"EXPORT {fname}")
    def closeProject(self):
        return self.cmd("CLOSE")
    def getstatus(self):
        status = self.cmd("STATUS")
        ssplit = status.split(';')
        statusdct = {}
        for s in ssplit:
            ssplit2 = s.split('=')
            statusdct[ssplit2]=ssplit2[1]
        return statusdct
    def connect(self):
        return self.cmd("CONNECT")
    def choosedevice(self,devname):
        return self.cmd(f"DEVICE {devname}")
    def getdevices(self):
        return self.cmd("DEVICES")
    def close(self):
        try:
            self.cmd("QUIT")
        finally:
            self.sock.close()


if __name__ == "__main__":
    import time

    q = Quadera("127.0.0.1")          # address of the QUADERA PC
    print(q.cmd("STATUS"))
    q.cmd(r"OPEN C:\Path\To\MyTemplate.qmt|test_run.qmp")
    q.cmd("FILAMENT ON")
    q.cmd("START")
    time.sleep(60)
    q.cmd("STOP")
    print("exported:", q.cmd("EXPORT"))
    q.cmd("CLOSE")
    q.close()
