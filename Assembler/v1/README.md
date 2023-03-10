# UI design with QT Designer
This version represents the basic framework of the application. Using QT Designer, the graphical user interface was created and converted into executable Python source code by pyuic6.<br/>

As already described, I have oriented myself to the assembler masswerk (https://www.masswerk.at/6502/assembler.html.) for the creation of the graphical user interface. 

I have already described the procedure for converting the surface file when creating the disassembler and therefore I would like to dispense with it here. Details can be found here: https://github.com/jegali/CPyU/tree/main/Disassembler/v1

I just want to give here the source code generated by pyuic, which we will build on in the next versions.

```bash
# Form implementation generated from reading ui file '.\assembler.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_AssemblerWindow(object):
    def setupUi(self, AssemblerWindow):
        AssemblerWindow.setObjectName("AssemblerWindow")
        AssemblerWindow.resize(800, 812)
        self.centralwidget = QtWidgets.QWidget(AssemblerWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.cmdSaveObjectcode = QtWidgets.QPushButton(self.centralwidget)
        self.cmdSaveObjectcode.setGeometry(QtCore.QRect(410, 330, 141, 24))
        self.cmdSaveObjectcode.setObjectName("cmdSaveObjectcode")
        self.cmdSaveAsmToFile = QtWidgets.QPushButton(self.centralwidget)
        self.cmdSaveAsmToFile.setGeometry(QtCore.QRect(220, 390, 75, 24))
        self.cmdSaveAsmToFile.setObjectName("cmdSaveAsmToFile")
        self.txtEditSourceode = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.txtEditSourceode.setGeometry(QtCore.QRect(20, 40, 381, 281))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(11)
        self.txtEditSourceode.setFont(font)
        self.txtEditSourceode.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.txtEditSourceode.setReadOnly(False)
        self.txtEditSourceode.setObjectName("txtEditSourceode")
        self.txtEditAssembler = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.txtEditAssembler.setGeometry(QtCore.QRect(20, 420, 381, 321))
        self.txtEditAssembler.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.txtEditAssembler.setReadOnly(False)
        self.txtEditAssembler.setObjectName("txtEditAssembler")
        self.lblObjectCode = QtWidgets.QLabel(self.centralwidget)
        self.lblObjectCode.setGeometry(QtCore.QRect(410, 10, 131, 16))
        self.lblObjectCode.setObjectName("lblObjectCode")
        self.txtEditObjectcode = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.txtEditObjectcode.setGeometry(QtCore.QRect(410, 40, 371, 281))
        self.txtEditObjectcode.setObjectName("txtEditObjectcode")
        self.cmdAssemble = QtWidgets.QPushButton(self.centralwidget)
        self.cmdAssemble.setGeometry(QtCore.QRect(310, 390, 75, 24))
        self.cmdAssemble.setObjectName("cmdAssemble")
        self.cmdLoadSourcecode = QtWidgets.QPushButton(self.centralwidget)
        self.cmdLoadSourcecode.setGeometry(QtCore.QRect(20, 330, 111, 24))
        self.cmdLoadSourcecode.setObjectName("cmdLoadSourcecode")
        self.lblSourcecodeView = QtWidgets.QLabel(self.centralwidget)
        self.lblSourcecodeView.setGeometry(QtCore.QRect(20, 10, 101, 16))
        self.lblSourcecodeView.setObjectName("lblSourcecodeView")
        self.txtEditDebug = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.txtEditDebug.setGeometry(QtCore.QRect(410, 420, 371, 321))
        self.txtEditDebug.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.txtEditDebug.setReadOnly(False)
        self.txtEditDebug.setObjectName("txtEditDebug")
        self.lblAssemblerView = QtWidgets.QLabel(self.centralwidget)
        self.lblAssemblerView.setGeometry(QtCore.QRect(20, 390, 101, 16))
        self.lblAssemblerView.setObjectName("lblAssemblerView")
        self.lblDebugView = QtWidgets.QLabel(self.centralwidget)
        self.lblDebugView.setGeometry(QtCore.QRect(410, 390, 101, 16))
        self.lblDebugView.setObjectName("lblDebugView")
        AssemblerWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(AssemblerWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        AssemblerWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(AssemblerWindow)
        self.statusbar.setObjectName("statusbar")
        AssemblerWindow.setStatusBar(self.statusbar)

        self.retranslateUi(AssemblerWindow)
        QtCore.QMetaObject.connectSlotsByName(AssemblerWindow)

    def retranslateUi(self, AssemblerWindow):
        _translate = QtCore.QCoreApplication.translate
        AssemblerWindow.setWindowTitle(_translate("AssemblerWindow", "6502 Assembler"))
        self.cmdSaveObjectcode.setText(_translate("AssemblerWindow", "Download object code"))
        self.cmdSaveAsmToFile.setText(_translate("AssemblerWindow", "Save to File"))
        self.txtEditSourceode.setPlainText(_translate("AssemblerWindow", ""))
        self.lblObjectCode.setText(_translate("AssemblerWindow", "Object Code:"))
        self.cmdAssemble.setText(_translate("AssemblerWindow", "Assemble"))
        self.cmdLoadSourcecode.setText(_translate("AssemblerWindow", "Load Sourcecode"))
        self.lblSourcecodeView.setText(_translate("AssemblerWindow", "Sourcecode View:"))
        self.lblAssemblerView.setText(_translate("AssemblerWindow", "Assembler Listing:"))
        self.lblDebugView.setText(_translate("AssemblerWindow", "Debug Window:"))
```

To start the program, a launcher app is needed. I put that code into a file called main.py:

```bash
import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from assemblerWindow import Ui_AssemblerWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    assem = Ui_AssemblerWindow()
    assem.setupUi(main)
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
```

After that, the app can be started by typing

```bash
python main.py
```

This should present you with the first app impression.

![Disassembler_UI](/images/assembler-v1.png)
