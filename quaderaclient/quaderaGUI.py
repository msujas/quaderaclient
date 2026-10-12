from PyQt6 import QtCore, QtWidgets, QtGui
import sys
from .quadera_client import Quadera

PORT = 15000
class QuaderaGui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quadera client GUI")
        self.cw = QtWidgets.QWidget()
        self.gridlayout = QtWidgets.QGridLayout()

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

        rown+=1
        self.templatelabel = QtWidgets.QLabel()
        self.templatelabel.setText("template file")
        self.templatelabel.setObjectName("self.templatelabel")
        self.gridlayout.addWidget(self.templatelabel,rown,0)

        rown+=1
        self.templatebox = QtWidgets.QLineEdit()
        self.templatebox.setObjectName("self.templatebox")
        self.gridlayout.addWidget(self.templatebox, rown, 0)

        self.openbutton = QtWidgets.QPushButton()
        self.openbutton.setObjectName("self.openbutton")
        self.openbutton.setText("open template")
        self.openbutton.clicked.connect(self.opentemplate)
        self.gridlayout.addWidget(self.openbutton,rown,1)

        rown+=1
        self.startbutton = QtWidgets.QPushButton()
        self.startbutton.setObjectName('startbutton')
        self.startbutton.setText("start acquisition")
        self.startbutton.clicked.connect(self.startaq)
        self.gridlayout.addWidget(self.startbutton,rown,0)

        self.stopbutton = QtWidgets.QPushButton()
        self.stopbutton.setObjectName('stopbutton')
        self.stopbutton.setText('stop acquisition')
        self.stopbutton.clicked.connect(self.stopaq)
        self.gridlayout.addWidget(self.stopbutton, rown,1)

        rown+=1

        self.exportbutton = QtWidgets.QPushButton()
        self.exportbutton.setObjectName('exportbutton')
        self.exportbutton.setText('export data')
        self.exportbutton.clicked.connect(self.exportdata)
        self.gridlayout.addWidget(self.exportbutton,rown, 0)

        self.exportfname = QtWidgets.QLineEdit()
        self.exportfname.setObjectName('self.exportfname')
        self.gridlayout.addWidget(self.exportfname,rown,1)

        self.fnamelabel = QtWidgets.QLabel()
        self.fnamelabel.setObjectName('self.fnamelabel')
        self.fnamelabel.setText('export file name')
        self.gridlayout.addWidget(self.fnamelabel,rown, 2)

        rown+=1
        self.connectbutton = QtWidgets.QPushButton()
        self.connectbutton.setObjectName("self.connectbutton")
        self.connectbutton.setText("connect")
        self.gridlayout.addWidget(self.connectbutton,rown,0)

        self.cw.setLayout(self.gridlayout)
        self.setCentralWidget(self.cw)

    def gethostport(self):
        host = self.hostbox.text()
        port = self.portbox.value()
        return host,port

    def getquad(self):
        host,port = self.gethostport()
        return Quadera(host,port)

    def startaq(self):
        quad = self.getquad()
        print(quad.start())

    def stopaq(self):
        quad = self.getquad()
        print(quad.stop())

    def exportdata(self):
        quad = self.getquad()
        name = self.exportfname.text().strip()
        print(quad.exportData(name))
    def opentemplate(self):
        file = self.templatebox.text()
        quad = self.getquad()
        print(quad.openProjectFile(file))

    def connect(self):
        quad = self.getquad()
        print(quad.connect())
    


def run():
    app = QtWidgets.QApplication(sys.argv)
    ui = QuaderaGui()
    ui.show()
    sys.exit(app.exec())
