
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