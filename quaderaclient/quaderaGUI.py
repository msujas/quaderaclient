from PyQt6 import QtCore, QtWidgets, QtGui
import sys, os
from .quadera_client import Quadera
from pathlib import Path

home = Path.home()

# TODO - set up config saving
class GuiValues():
    def __init__(self,widget:QtWidgets.QLineEdit|QtWidgets.QSpinBox):
        self.widget = widget
        self.name = widget.objectName()
        match type(widget):
            case QtWidgets.QLineEdit:
                self.value = widget.text()
            case QtWidgets.QSpinBox:
                self.value = widget.value()
    def setvalue(self,value):
        match type(self.widget):
            case QtWidgets.QLineEdit:
                self.widget.setText(str(value))
            case QtWidgets.QSpinBox:
                self.widget.setValue(int(value))

class WidgetList():
    def __init__(self, alist: list[GuiValues]):
        self.list = alist
    def getwidget(self,name):
        for item in self.list:
            if item.name == name:
                return item
    def additem(self,item):
        self.list.append(item)
    def __getitem__(self, key:int):
        return self.list[key]
        

    
PORT = 15000
class QuaderaGui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QtCore.QSettings()
        self.configfile = f'{home}/.log/quaderagui/quaderagui.log'
        os.makedirs(os.path.dirname(self.configfile),exist_ok=True)
        self.setWindowTitle("Quadera client GUI")
        self.cw = QtWidgets.QWidget()
        self.gridlayout = QtWidgets.QGridLayout()
        self.connected:bool = False
        rown = 0
        self.hostbox = QtWidgets.QLineEdit()
        self.hostbox.setObjectName('hostbox')
        self.gridlayout.addWidget(self.hostbox,rown,0)

        self.hostlabel = QtWidgets.QLabel()
        self.hostlabel.setObjectName('hostlabel')
        self.hostlabel.setText('host address')
        self.gridlayout.addWidget(self.hostlabel,rown,1)

        rown+=1
        self.portbox = QtWidgets.QSpinBox()
        self.portbox.setObjectName('portbox')
        self.portbox.setMinimum(0)
        self.portbox.setMaximum(65535)
        self.portbox.setValue(PORT)
        self.gridlayout.addWidget(self.portbox, rown, 0)

        self.portlabel = QtWidgets.QLabel()
        self.portlabel.setObjectName('portlabel')
        self.portlabel.setText('port number')
        self.gridlayout.addWidget(self.portlabel, rown, 1)

        self.connectserverbutton = QtWidgets.QPushButton()
        self.connectserverbutton.setObjectName("self.connectserverbutton")
        self.connectserverbutton.setText("connect server")
        self.connectserverbutton.clicked.connect(self.connecttoserver)
        self.gridlayout.addWidget(self.connectserverbutton, rown, 2)

        rown+=1
        self.setdevicebutton = QtWidgets.QPushButton()
        self.setdevicebutton.setObjectName("self.setdevicebutton")
        self.setdevicebutton.setText("set device 1")
        self.setdevicebutton.clicked.connect(self.setdevice1)
        self.gridlayout.addWidget(self.setdevicebutton, rown, 0)

        rown+=1
        self.templatelabel = QtWidgets.QLabel()
        self.templatelabel.setText("template file")
        self.templatelabel.setObjectName("self.templatelabel")
        self.gridlayout.addWidget(self.templatelabel,rown,0)

        rown+=1
        self.templatebox = QtWidgets.QLineEdit()
        self.templatebox.setObjectName("self.templatebox")
        self.gridlayout.addWidget(self.templatebox, rown, 0,1,2)

        self.openbutton = QtWidgets.QPushButton()
        self.openbutton.setObjectName("self.openbutton")
        self.openbutton.setText("open template")
        self.openbutton.clicked.connect(self.opentemplate)
        self.openbutton.setEnabled(False)
        self.gridlayout.addWidget(self.openbutton,rown,2)

        rown+=1
        self.startbutton = QtWidgets.QPushButton()
        self.startbutton.setObjectName('startbutton')
        self.startbutton.setText("start acquisition")
        self.startbutton.clicked.connect(self.startaq)
        self.startbutton.setEnabled(False)
        self.gridlayout.addWidget(self.startbutton,rown,0)

        self.stopbutton = QtWidgets.QPushButton()
        self.stopbutton.setObjectName('stopbutton')
        self.stopbutton.setText('stop acquisition')
        self.stopbutton.clicked.connect(self.stopaq)
        self.stopbutton.setEnabled(False)
        self.gridlayout.addWidget(self.stopbutton, rown,1)

        rown+=1
        self.fnamelabel = QtWidgets.QLabel()
        self.fnamelabel.setObjectName('self.fnamelabel')
        self.fnamelabel.setText('export file name')
        self.gridlayout.addWidget(self.fnamelabel,rown, 0)

        rown+=1

        self.exportbutton = QtWidgets.QPushButton()
        self.exportbutton.setObjectName('exportbutton')
        self.exportbutton.setText('export data')
        self.exportbutton.clicked.connect(self.exportdata)
        self.exportbutton.setEnabled(False)
        self.gridlayout.addWidget(self.exportbutton,rown, 2)

        self.exportfname = QtWidgets.QLineEdit()
        self.exportfname.setObjectName('self.exportfname')
        self.gridlayout.addWidget(self.exportfname,rown,0,1,2)



        rown+=1
        self.connectbutton = QtWidgets.QPushButton()
        self.connectbutton.setObjectName("self.connectbutton")
        self.connectbutton.setText("connect")
        self.gridlayout.addWidget(self.connectbutton,rown,0)
        self.switchwidgets(False)

        self.readconfig()

        self.cw.setLayout(self.gridlayout)
        self.setCentralWidget(self.cw)

    def gethostport(self):
        host = self.hostbox.text()
        port = self.portbox.value()
        return host,port

    def getquad(self):
        host,port = self.gethostport()
        return Quadera(host,port, timeout=10)

    def startaq(self):
        print(self.quad.start())
        self.setstartstop()

    def stopaq(self):
        print(self.quad.stop())
        self.setstartstop()

    def exportdata(self):
        name = self.exportfname.text().strip()
        print(self.quad.exportData(name))
    def opentemplate(self):
        file = self.templatebox.text()
        print(self.quad.openProjectFile(file))

    def connect(self):
        self.saveconfig()
        try:
            print(self.quad.connect())
        except TimeoutError:
            print('connection couldn\'t be established')

    def switchwidgets(self, state:bool):
        #self.connectserverbutton.setEnabled(not state)
        self.setdevicebutton.setEnabled(state)
        self.openbutton.setEnabled(state)
        self.connectbutton.setEnabled(state)
        self.startbutton.setEnabled(state)
        self.stopbutton.setEnabled(state)
        self.exportbutton.setEnabled(state)
        self.connectbutton.setEnabled(state)

    def connecttoserver(self):
        match self.connected:
            case False:
                try:
                    self.quad = self.getquad()
                except TimeoutError:
                    print("couldn't establish connection")
                    return
                self.connectserverbutton.setText('disconnect server')
                self.hostbox.setEnabled(False)
                self.portbox.setEnabled(False)
                self.switchwidgets(True)
                self.connected = True
                self.setstartstop()

            case True:
                self.connectserverbutton.setText('connect server')
                self.hostbox.setEnabled(True)
                self.portbox.setEnabled(False)
                self.switchwidgets(False)
                self.connected = False
    def setstartstop(self):
        status = self.quad.getstatus()
        if status['running'] == 'Running':
            self.startbutton.setEnabled(False)
            self.stopbutton.setEnabled(True)
        else:
            self.startbutton.setEnabled(True)
            self.stopbutton.setEnabled(False)
    
    def updatewidgets(self):
        widgets = [self.hostbox, self.portbox, self.templatebox, self.exportfname]
        self.widgets = WidgetList([GuiValues(w) for w in widgets])
        
    def saveconfig(self):
        self.updatewidgets()
        s = ''
        for w in self.widgets:
            s += f'{w.name};{w.value}\n'
        f = open(self.configfile,'w')
        f.write(s)
        f.close()
    def readconfig(self):
        self.updatewidgets()
        if not os.path.exists(self.configfile):
            return
        f = open(self.configfile,'r')
        for line in f:
            if not line:
                continue
            linesplit = line.strip().split(';')
            name = linesplit[0]
            value = linesplit[1]
            w = self.widgets.getwidget(name)
            if w:
                w.setvalue(value)
        f.close()

    def closeEvent(self, a0):
        self.saveconfig()
        return super().closeEvent(a0)

    def setdevice1(self):
        return self.quad.choosedevice(1)


def run():
    app = QtWidgets.QApplication(sys.argv)
    ui = QuaderaGui()
    ui.show()
    sys.exit(app.exec())
