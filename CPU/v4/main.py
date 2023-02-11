
import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from emulatorWindow import Ui_EmulatorWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    emulator = Ui_EmulatorWindow()
    emulator.setupUi(main)
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()