
import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from assemblerWindow import Ui_AssemblerWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    disasm = Ui_AssemblerWindow()
    disasm.setupUi(main)
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()