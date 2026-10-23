import socket
from .quadera_client import Quadera
import os, subprocess
import argparse
import logging
import time
import asyncio

PORT = 59682

def parseargs():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host',type=str, default='127.0.0.1', help = 'server host name (default localhost)')
    ap.add_argument('--port', type=int, help = 'server port value', default=PORT)
    ap.add_argument('--qhost', type=str, help='host name for Quadera server')
    ap.add_argument('--qport', type=int, default=15000, help='port value for Quadera server')
    args = ap.parse_args()
    return args.host, args.port, args.qhost, args.qport

class QuaderaHandler():
    def __init__(self):
        self.host,self.port, self.qhost, self.qport = parseargs()
        self.quad = Quadera(self.qhost, self.qport)
        self.running = False
        self.looptask: asyncio.Task | None = None
        self.shutdownevent = asyncio.Event()

    async def mainloop(self, exportname, localname):
        cmd = ['scp', f'{self.qhost}:{exportname}', localname]
        print(f'loop to export data as {exportname}, saving data as {localname}')
        self.running = True
        try:
            while self.running:
                qdata = self.quad.exportData(exportname)
                print(qdata)
                print(' '.join(cmd))
                subprocess.run(cmd)
                await asyncio.sleep(10)
        except asyncio.CancelledError as e:
            print("main loop stopped")
            raise e
        except RuntimeError as e:
            estring= str(e)
            if 'connection closed' in estring:
                print(e)
            raise asyncio.CancelledError


    def isrunning(self)->bool:
        return self.looptask is not None and not self.looptask.done()

    async def processCommand(self, line:str):
        cmd = line.split()[0]
        args = line.replace(cmd,'').strip()
        match cmd.lower():
            case 'run':
                try:
                    exportname, fname = args.split('|')
                    print(exportname, fname)
                except ValueError:
                    return 'run command not in correct format. Must be "run <export file name>|<local file name>"'
                if self.isrunning():
                    self.looptask.cancel()
                self.looptask = asyncio.create_task(self.mainloop(exportname, fname))
                return 'started'
            case 'stop':
                if not self.isrunning():
                    return 'not running'
                self.looptask.cancel()
                try:
                    await self.looptask
                except asyncio.CancelledError:
                    pass
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
