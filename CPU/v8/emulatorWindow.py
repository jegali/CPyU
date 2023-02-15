# Form implementation generated from reading ui file '.\emulator.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.

# xxx RAM View
# xxx Zero page View
# xxx Stack View
# xxx ROM View


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QKeyEvent
from apple2 import Apple2
from disassemblerWindow import Ui_DisassemblerWindow
from assemblerWindow import Ui_AssemblerWindow
from myHexEdit import myHexEdit


import numpy
import pygame
import time

class Speaker:

    CPU_CYCLES_PER_SAMPLE = 60
    CHECK_INTERVAL = 1000

    def __init__(self):
        pygame.mixer.pre_init(11025, -16, 1)
        pygame.init()
        self.reset()

    def toggle(self, cycle):
        if self.last_toggle is not None:
            l = int((cycle - self.last_toggle) / Speaker.CPU_CYCLES_PER_SAMPLE)
            #print("L: ", l)
            self.buffer.extend([0, 26000] if self.polarity else [0, -2600])
            self.buffer.extend((l - 2) * [16384] if self.polarity else [-16384])
            self.polarity = not self.polarity
        self.last_toggle = cycle

    def reset(self):
        self.last_toggle = None
        self.buffer = []
        self.polarity = False

    def play(self):
        sample_array = numpy.int16(self.buffer)
        #sound = pygame.sndarray.make_sound(sample_array)
        sound = pygame.mixer.Sound(sample_array)
        sound.play()
        self.reset()

    def update(self, cycle):
        if self.buffer and (cycle - self.last_toggle) > self.CHECK_INTERVAL:
            self.play()


class Ui_EmulatorWindow(object):

    program_counter = 0
    code = "A9 03"
    running = False
    Emulator = None
    window_asm = None
    window_dis = None

    def __init__(self) -> None:
        self.myApple = None
        self.speaker = Speaker()
        self.disasm_preview = Ui_DisassemblerWindow()

    def setupUi(self, Emulator):
        Emulator.setObjectName("Emulator")
        Emulator.resize(1440, 900)
        self.Emulator = Emulator
        # this sets the close event, if user clicks "X"
        self.Emulator.closeEvent = self.closeEvent
        self.centralwidget = QtWidgets.QWidget(Emulator)
        self.centralwidget.setObjectName("centralwidget")

        # Groupbox für den aktuellen Befehl
        self.grpCmd = QtWidgets.QGroupBox(self.centralwidget)
        self.grpCmd.setGeometry(QtCore.QRect(760, 20, 310, 71))
        self.grpCmd.setObjectName("grpCmd")
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        self.grpCmd.setFont(font)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.lblCmd = QtWidgets.QLabel(self.grpCmd)
        self.lblCmd.setGeometry(QtCore.QRect(10, 30, 290, 20))
        self.lblCmd.setFont(font)
        self.lblCmd.setObjectName("lblCmd")

        # Groupbox for Registers / Flags
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(1080, 20, 341, 71))
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.lblFlags = QtWidgets.QLabel(self.groupBox)
        self.lblFlags.setGeometry(QtCore.QRect(254, 20, 71, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblFlags.setFont(font)
        self.lblFlags.setObjectName("lblFlags")
        self.lblSP = QtWidgets.QLabel(self.groupBox)
        self.lblSP.setGeometry(QtCore.QRect(204, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblSP.setFont(font)
        self.lblSP.setObjectName("lblSP")
        self.lblSR = QtWidgets.QLabel(self.groupBox)
        self.lblSR.setGeometry(QtCore.QRect(174, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblSR.setFont(font)
        self.lblSR.setObjectName("lblSR")
        self.lblYR = QtWidgets.QLabel(self.groupBox)
        self.lblYR.setGeometry(QtCore.QRect(143, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblYR.setFont(font)
        self.lblYR.setObjectName("lblYR")
        self.lblXR = QtWidgets.QLabel(self.groupBox)
        self.lblXR.setGeometry(QtCore.QRect(113, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblXR.setFont(font)
        self.lblXR.setObjectName("lblXR")
        self.lblAc = QtWidgets.QLabel(self.groupBox)
        self.lblAc.setGeometry(QtCore.QRect(80, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblAc.setFont(font)
        self.lblAc.setObjectName("lblAc")
        self.lblPC = QtWidgets.QLabel(self.groupBox)
        self.lblPC.setGeometry(QtCore.QRect(30, 20, 20, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblPC.setFont(font)
        self.lblPC.setObjectName("lblPC")
        self.txtPC = QtWidgets.QLineEdit(self.groupBox)
        self.txtPC.setGeometry(QtCore.QRect(20, 40, 41, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtPC.setFont(font)
        self.txtPC.setObjectName("txtPC")
        self.txtAC = QtWidgets.QLineEdit(self.groupBox)
        self.txtAC.setGeometry(QtCore.QRect(76, 40, 24, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtAC.setFont(font)
        self.txtAC.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtAC.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtAC.setObjectName("txtAC")
        self.txtXR = QtWidgets.QLineEdit(self.groupBox)
        self.txtXR.setGeometry(QtCore.QRect(110, 40, 24, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtXR.setFont(font)
        self.txtXR.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtXR.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtXR.setObjectName("txtXR")
        self.txtYR = QtWidgets.QLineEdit(self.groupBox)
        self.txtYR.setGeometry(QtCore.QRect(140, 40, 24, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtYR.setFont(font)
        self.txtYR.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtYR.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtYR.setObjectName("txtYR")
        self.txtSR = QtWidgets.QLineEdit(self.groupBox)
        self.txtSR.setGeometry(QtCore.QRect(170, 40, 24, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtSR.setFont(font)
        self.txtSR.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtSR.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtSR.setObjectName("txtSR")
        self.txtSP = QtWidgets.QLineEdit(self.groupBox)
        self.txtSP.setGeometry(QtCore.QRect(200, 40, 24, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtSP.setFont(font)
        self.txtSP.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtSP.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtSP.setObjectName("txtSP")
        self.txtFlags = QtWidgets.QLineEdit(self.groupBox)
        self.txtFlags.setGeometry(QtCore.QRect(245, 40, 81, 20))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtFlags.setFont(font)
        self.txtFlags.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.txtFlags.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.txtFlags.setObjectName("txtFlags")

        # Die Gruppe für die Zeropage
        self.grpZP = QtWidgets.QGroupBox(self.centralwidget)
        self.grpZP.setGeometry(QtCore.QRect(760, 110, 661, 200))
        self.grpZP.setObjectName("grpZP")
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtFlags.setFont(font)
        #self.txtZP = QtWidgets.QPlainTextEdit(self.grpZP)
        self.txtZP = myHexEdit(self.grpZP)
        self.txtZP.setGeometry(QtCore.QRect(10, 30, 641, 150))
        self.txtZP.setObjectName("txtZP")
        self.txtZP.setFont(font)

        # Die Gruppe für den Stack
        self.grpStack = QtWidgets.QGroupBox(self.centralwidget)
        self.grpStack.setGeometry(QtCore.QRect(760, 320, 661, 200))
        self.grpStack.setObjectName("grpStack")
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtFlags.setFont(font)
        self.txtStack = QtWidgets.QPlainTextEdit(self.grpStack)
        self.txtStack.setGeometry(QtCore.QRect(10, 30, 641, 150))
        self.txtStack.setObjectName("txtStack")
        self.txtStack.setFont(font)


        # Die Gruppe für das RAM
        self.grpRAM = QtWidgets.QGroupBox(self.centralwidget)
        self.grpRAM.setGeometry(QtCore.QRect(760, 530, 661, 320))
        self.grpRAM.setObjectName("grpRAM")
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.txtFlags.setFont(font)
        self.txtRAM = QtWidgets.QPlainTextEdit(self.grpRAM)
        self.txtRAM.setGeometry(QtCore.QRect(10, 30, 641, 266))
        self.txtRAM.setObjectName("txtRAM")
        self.txtRAM.setFont(font)

        self.cmdStep = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.startApple2())
        self.cmdStep.setGeometry(QtCore.QRect(110, 30, 75, 23))
        self.cmdStep.setObjectName("cmdStep")

        self.cmdStep1 = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.stopApple2())
        self.cmdStep1.setGeometry(QtCore.QRect(110, 60, 75, 23))
        self.cmdStep1.setObjectName("cmdStep1")

        self.cmdStep2 = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.stepApple2())
        self.cmdStep2.setGeometry(QtCore.QRect(110, 90, 75, 23))
        self.cmdStep2.setObjectName("cmdStep2")

        Emulator.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Emulator)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuWindow = QtWidgets.QMenu(self.menubar)
        self.menuWindow.setObjectName("menuWindow")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        Emulator.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Emulator)
        self.statusbar.setObjectName("statusbar")
        Emulator.setStatusBar(self.statusbar)
        
        self.actionDisassembler = QtGui.QAction(Emulator)
        self.actionDisassembler.setObjectName("actionDisassembler")
        self.actionDisassembler.triggered.connect(self.showDisassembler)
        
        self.actionAssembler = QtGui.QAction(Emulator)
        self.actionAssembler.setObjectName("actionAssembler")
        self.actionAssembler.triggered.connect(self.showAssembler)
        
        self.actionExit = QtGui.QAction(Emulator)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.triggered.connect(self.exitProgram)

        self.menuWindow.addAction(self.actionDisassembler)
        self.menuWindow.addAction(self.actionAssembler)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuWindow.menuAction())

        self.retranslateUi(Emulator)
        QtCore.QMetaObject.connectSlotsByName(Emulator)

        # Die Referenz auf den Apple2 Emulator setzen
        self.myApple = Apple2(self)



    def retranslateUi(self, Emulator):
        _translate = QtCore.QCoreApplication.translate
        Emulator.setWindowTitle(_translate("Emulator", "Emulator"))
        self.groupBox.setTitle(_translate("Emulator", "Registers / Flags"))
        self.lblFlags.setText(_translate("Emulator", "NV-BDIZC"))
        self.lblCmd.setText(_translate("Emulator", "0000-   00 00 00   ???"))
        self.lblSP.setText(_translate("Emulator", "SP"))
        self.lblSR.setText(_translate("Emulator", "SR"))
        self.lblYR.setText(_translate("Emulator", "YR"))
        self.lblXR.setText(_translate("Emulator", "XR"))
        self.lblAc.setText(_translate("Emulator", "AC"))
        self.lblPC.setText(_translate("Emulator", "PC"))
        self.txtPC.setText(_translate("Emulator", "0000"))
        self.txtAC.setText(_translate("Emulator", "00"))
        self.txtXR.setText(_translate("Emulator", "00"))
        self.txtYR.setText(_translate("Emulator", "00"))
        self.txtSR.setText(_translate("Emulator", "00"))
        self.txtSP.setText(_translate("Emulator", "00"))
        self.txtFlags.setText(_translate("Emulator", "00-00000"))
        self.grpCmd.setTitle(_translate("Emulator", "Current Command"))
        self.grpRAM.setTitle(_translate("Emulator", "RAM"))
        self.grpZP.setTitle(_translate("Emulator", "Zero Page"))
        self.grpStack.setTitle(_translate("Emulator", "Stack"))
        self.cmdStep.setText(_translate("Emulator", "Reset"))
        self.cmdStep1.setText(_translate("Emulator", "Stop"))
        self.cmdStep2.setText(_translate("Emulator", "Step"))
        self.menuWindow.setTitle(_translate("Emulator", "Window"))
        self.menuFile.setTitle(_translate("Emulator", "File"))
        self.actionDisassembler.setText(_translate("Emulator", "Disassembler"))
        self.actionAssembler.setText(_translate("Emulator", "Assembler"))
        self.actionExit.setText(_translate("Emulator", "Exit"))

    # def eventFilter(self, obj, event):
    #     if obj is self.plainTextEdit and event.type() == QtCore.QEvent.KeyPress:
    #         if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
    #             print("Enter pressed")
    #             return True
    #     return super(MainWindow, self).eventFilter(obj, event)



    #####
    
    #  Menu Functions

    #
    # def exitProgram(self): 
    #
    # User clicked File | Exit
    # Program will be closed
    #

    def exitProgram(self):
        exit(0)

    #
    # def closeEvent(self, event): 
    #
    # User clicked "X" button
    # Program will be closed
    #

    def closeEvent(self, event):
        exit(0)

    #
    # def showDisassembler(self):
    #
    # User clicked Windows | Disassembler
    # Program will open a disassembler view
    # help from: https://www.youtube.com/watch?v=R5N8TA0KFxc
    #

    def showDisassembler(self):
        self.window_dis = QtWidgets.QMainWindow()
        self.disasm = Ui_DisassemblerWindow()
        self.disasm.setupParent(self)
        self.disasm.setupUi(self.window_dis)
        if self.myApple:
            self.disasm.transfer_memory(self.myApple.dump_mem())
            self.disasm.fill_code_view(bytearray(self.myApple.dump_mem()))
            self.disasm.disassemble()
        self.window_dis.show()

    #
    # def showAssembler(self):
    #
    # User clicked Windows | Assembler
    # Program will open a assembler view
    # help from: https://www.youtube.com/watch?v=R5N8TA0KFxc
    #

    def showAssembler(self):
        self.window_asm = QtWidgets.QMainWindow()
        self.asm = Ui_AssemblerWindow()
        self.asm.setupUi(self.window_asm)
        self.window_asm.show()



    ##### BASIC EMULATION COMMANDS

    def startApple2(self):
        self.running = True
        #self.myApple = Apple2(self)
        self.updateRegisterFlags(self.myApple.cpu)
        self.disasm_preview.transfer_memory(self.myApple.dump_mem())
        self.lblCmd.setText(self.disasm_preview.disassemble_command(self.myApple.read_PC(),self.myApple.dump_mem()))
        #self.myApple.run()
        update_cycle = 0
        t = time.time()
        cycles = self.myApple.cpu.cycles
        while self.running:
            # Die While-Schleife muss für Eventbehandlung unterbrochen werden, 
            # sonst haben wir hier eine Endlosschleife
            # Über ProcessEvents kann auch das Event auf den Stop-Button abgefragt werden,
            # das die Variable running auf False setzt und damit die Schleife beendet
            self.stepApple2()
            # if self.myApple.memory.is_bus_read == 1:
            #     self.handle_read_io()
            # if self.myApple.memory.is_bus_write == 1:
            #     self.handle_write_io()
                    
            # update_cycle += 1
            # if update_cycle >= 1024:
            #     #self.display.flash()
            #     #pygame.display.flip()
            #     if self.speaker:
            #         self.speaker.update(self.myApple.memory.is_bus_cycle)
            #     update_cycle = 0
            elapsed_time = time.time() - t
            if elapsed_time > 1:
                print("Cycles: " + str(self.myApple.cpu.cycles-cycles) + " " + str(elapsed_time))
                t = time.time()
                cycles = self.myApple.cpu.cycles
            QtWidgets.QApplication.processEvents()
        print("Done")

    def stepApple2(self):
        self.myApple.cpu.exec_command()

    def stepApple2_debug(self):
        self.myApple.cpu.exec_command()
        self.updateRegisterFlags(self.myApple.cpu)
        self.lblCmd.setText(self.disasm_preview.disassemble_command(self.myApple.read_PC(),self.myApple.dump_mem()))

    def stopApple2(self):
        self.running = False


    def handle_read_io(self):
        address = self.myApple.memory.is_bus_address
        cycle = self.myApple.memory.is_bus_cycle
        if address == 0xC030:
            if self.speaker:
                self.speaker.toggle(cycle)
        #print("Beep")
        #print("Bus read: ", hex(self.myApple.memory.is_bus_address))

    def handle_write_io(self):
        #print("Bus write: ", hex(self.myApple.memory.is_bus_address))
        pass

    def updateRegisterFlags(self, myCPU):
        self.txtPC.setText(self.int2hex(myCPU.read_PC(),4))
        self.txtAC.setText(self.int2hex(myCPU.read_AC(),2))
        self.txtXR.setText(self.int2hex(myCPU.read_XR(),2))
        self.txtYR.setText(self.int2hex(myCPU.read_YR(),2))
        self.txtSP.setText(self.int2hex(myCPU.read_SP(),2))
        self.txtFlags.setText(myCPU.read_Flags())


    def updateMemoryView(self, myMemory):
        # Zeropage
        self.updateRAMView(myMemory, 0)
        # Stackpage
        self.updateRAMView(myMemory, 1)
        # RAM
        self.updateRAMView(myMemory, 2)


    def updateRAMView(self, myMemory, myRAM):
        if myRAM == 0:
            control = self.txtZP
            code_array = myMemory.dump_zeropage()
            address = 0x0000
        if myRAM == 1:
            control = self.txtStack
            code_array = myMemory.dump_stack()
            address = 0x0100
        if myRAM == 2:
            control = self.txtRAM
            #code_array = myMemory.dump_ram() + myMemory.dump_rom()
            code_array = myMemory.dump_mem()
            address = 0x0000

        control.clear()
        
        blocksize = 16
        for chunk in range(0,len(code_array), blocksize):
            if address < 65536:
                address_str = hex(address)[2:].upper().zfill(4) + ": "
                first_8 =  '{}'.format(' '.join(self.int2hex(x,2) for x in code_array[chunk:chunk+blocksize//2]))
                second_8 =  '{}'.format(' '.join(self.int2hex(x,2) for x in code_array[chunk+blocksize//2:chunk+blocksize]))
                first_asc = self.convert2ascii(code_array[chunk:chunk+blocksize//2])
                second_asc = self.convert2ascii(code_array[chunk+blocksize//2:chunk+blocksize])
                control.appendPlainText(address_str + " " + first_8 + "  " + second_8 + "  " + first_asc + " " + second_asc)
            address += blocksize
        txtCursor = control.textCursor()
        txtCursor.setPosition(0)
        control.setTextCursor(txtCursor)



    #
    # def convert2ascii(self, memblock):
    #
    # This method converts a hex byte to ascii char
    # for display in the memory editor
    #

    def convert2ascii(self, memblock):
        ascii_str = ''
        for i in memblock:
            if 0x20 < ord(chr(i)) < 0x7F:
                ascii_str += chr(i)
            else:
                ascii_str += "."
        return ascii_str
 
 
 
    #
    # def int2hex(x,y):
    #
    # Diese Methode wandelt einen int-Wert (x)
    # in einen hex-Wert der Länge (y) um
    #

    def int2hex(self,x,y):
        return hex(x)[2:].zfill(y).upper() 
