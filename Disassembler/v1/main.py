
import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from disassemblerWindow import Ui_DisassemblerWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = QtWidgets.QMainWindow()
    disasm = Ui_DisassemblerWindow()
    disasm.setupUi(main)
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()