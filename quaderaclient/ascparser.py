from datetime import datetime

def _parsetimeline(line:str):
    linesplit = line.split()
    datestr = linesplit[2]
    timestr = linesplit[3]
    ampm = linesplit[4]
    mo,d,y = datestr.split('/')
    mo = int(mo)
    d = int(d)
    y = int(y)
    h,m,s = timestr.split(':')
    sint, sfrac = s.split('.')
    h = int(h)
    m = int(m)
    s = float(s)
    sint = int(sint)
    sfrac = float(f'0.{sfrac}')
    micros = int(sfrac*1e6)
    if ampm == 'pm':
        h += 12
    dt = datetime(y,mo,d,h,m,second=sint,microsecond=micros)
    return dt

class AscInfo():
    def __init__(self,startline:str, endline:str):
        self.startline = startline
        self.endline = endline
        self.parseTimes()
    def parseTimes(self):
        self.startdt = _parsetimeline(self.startline)
        self.enddt = _parsetimeline(self.endline)

def getfiletimes(ascfile):
    f = open(ascfile)
    startline = ''
    endline = ''
    for line in f:
        if 'Start Time' in line:
            startline = line
        if 'End Time' in line:
            endline = line
            break
    f.close()
    return AscInfo(startline, endline)