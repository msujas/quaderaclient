import socket
from .quadera_client import Quadera
import os, subprocess
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
import time

home = Path.home()
user = os.path.split(home)[-1]

PORT = 59682

def parseargs():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host',type=str, default='127.0.0.1', help = 'server host name (default localhost)')
    ap.add_argument('--port', type=int, help = f'server port value, default {PORT}', default=PORT)
    ap.add_argument('--qhost', type=str, help='host name for Quadera server', required=True)
    ap.add_argument('--qport', type=int, default=15000, help=f'port value for Quadera server. Default 15000')
    ap.add_argument('--username',type=str,default=user,help=f'user name on remote PC. Default: this user: {user}')
    args = ap.parse_args()
    return args.host, args.port, args.qhost, args.qport, args.username

def dtstring():
    dt = datetime.fromtimestamp(time.time())
    return f'{dt.year:04d}{dt.month:02d}{dt.day:02d}_{dt.hour:02d}{dt.minute:02d}{dt.second:02d}'

class QuaderaHandler():
    def __init__(self):
        self.host,self.port, self.qhost, self.qport, self.user = parseargs()
        print(f'using Quadera server at {self.qhost}:{self.qport}')
        self.running = False
        self.looptask: asyncio.Task | None = None
        self.shutdownevent = asyncio.Event()

    async def mainloop(self, exportname, localname, waittime = 60):
        cmd = ['scp', f'{self.user}@{self.qhost}:{exportname}', localname]
        print(f'loop to export data as {exportname}, saving data as {localname}')
        self.running = True
        self.quad = Quadera(self.qhost, self.qport)
        tries = 3
        try:
            while self.running:
                for n in range(tries):
                    qdata = self.quad.exportData(exportname)
                    if 'ERR' in qdata:
                        print(qdata)
                        if n >= tries-1:
                            raise asyncio.CancelledError(qdata)
                    else:
                        break    
                print(dtstring(),end=' ')
                print(qdata)
                print(' '.join(cmd))
                subprocess.run(cmd)
                await asyncio.sleep(waittime)
        except asyncio.CancelledError as e:
            print("main loop stopped")
            raise e
        except RuntimeError as e:
            estring= str(e)
            if 'connection closed' in estring:
                print('connection closed')
                print(e)
            raise asyncio.CancelledError


    def isrunning(self)->bool:
        return self.looptask is not None and not self.looptask.done()

    async def processCommand(self, line:str):
        cmd = line.split()[0]
        args = line.replace(cmd,'').strip()
        
        async def stoptask():
            self.looptask.cancel()
            try:
                await self.looptask
            except asyncio.CancelledError:
                pass

        match cmd.lower():
            case 'run':
                try:
                    argsplit = args.split('|')
                    exportname = argsplit[0]
                    fname = argsplit[1]
                    if len(args)>2:
                        waittime = float(argsplit[2])
                    else:
                        waittime = 60
                    print(exportname, fname,waittime)
                except ValueError:
                    return 'run command not in correct format. Must be "run <export file name>|<local file name>|<optional wait time>"'
                if self.isrunning():
                    await stoptask()
                    print('current task stopped')
                        
                self.looptask = asyncio.create_task(self.mainloop(exportname, fname))
                return 'started'
            case 'stop':
                if not self.isrunning():
                    return 'not running'
                await stoptask()
                return 'stopped'
            case 'status':
                return 'running' if self.isrunning() else 'not running'

    async def handleclient(self,reader:asyncio.StreamReader,writer:asyncio.StreamWriter):
        addr = writer.get_extra_info("peername")
        print(f'client connected: {addr}')

        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                line = data.decode().strip()
                if not line:
                    continue
                if line.lower() == 'quit':
                    writer.write(b'disconnecting client\n')
                    await writer.drain()
                    break
                reply = await self.processCommand(line)
                writer.write(f'{reply}\n'.encode())
                await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()
            print(f'client disconnected: {addr}')
    async def run(self):
        server = await asyncio.start_server(self.handleclient, self.host,self.port)
        print(f'listening on {self.host}:{self.port}')
        async with server:
            await self.shutdownevent.wait()
        if self.isrunning():
            self.looptask.cancel()
        print('server closed')

def main():
    try:
        asyncio.run(QuaderaHandler().run())
    except KeyboardInterrupt:
        print('caught keyboard interrupt. Exiting')
