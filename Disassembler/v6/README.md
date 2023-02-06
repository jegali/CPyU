# Changes
This version of the disassembler has some small innovations and improvements . As always, we will go through and discuss these changes one by one.

## Mouse Cursor during diassembly
It is now possible to start the slide assembler from the emulator window and to pass it the complete memory area of the Apple ][ on this occasion. Disassembling an entire 64KB block can take quite some time, so I decided to set the mouse cursor to Waiting at the beginning of the disassemble() method and to reset it when the method is finished. To achieve this, I made these changes:

```bash
   def disassemble(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        
        # Do the heavy task
        
        txtCursor = self.plainTextEdit_3.textCursor()
        txtCursor.setPosition(0)
        self.plainTextEdit_3.setTextCursor(txtCursor)
        QtWidgets.QApplication.restoreOverrideCursor()
```

## Decode only one command
In the emulator window I would like to see a disassembly of a single command - as a preview, so to speak, of what is being processed. Think of it as the equivalent of playing Tetris. Here, too, you get a preview of the next piece of the puzzle. For this purpose I created a method called disassemble_command(), which in principle does exactly what is done in the loop of the disasssmble() method. Maybe the two methods can still be integrated so that there is no duplicate code. For now, though, it stays exactly as it is right now.

```bash
    def disassemble_command(self, pc, memory):
        self.code_array = memory
        line_to_write = hex(pc)[2:].upper().zfill(4) + "- \t"
        opcode = int(self.code_array[pc])
        operation = self.operations[opcode]
        info = operation[5](pc)
        bytecount = operation[6]
        hexcode = ' '.join([hex(i)[2:].upper().zfill(2) for i in self.code_array[pc:pc+bytecount]]) 
        line_to_write = line_to_write + "{:<11}".format(hexcode)
        command = operation[1]
        line_to_write = line_to_write + command                
        line_to_write = line_to_write + " " + "{:<15}".format(info["operand"])                
        return line_to_write
```

## Who is your daddy ?
The disassembler can be called standalone - or via the menu in the emulator window. To be able to distinguish between these two modes of operation, I have implmented a status variable that can be used to query the status:

```bash
    def __init__(self) -> None:
        self.emulatorWindow = None
        self.init_operations()
   
   ...
   
    #
    # who is your daddy ? 
    #
    # We need this information for determining:
    # - is this the standalone disassembler
    # - is this the disassembler called from the emulator
    # 
     
    def setupParent(self, object):
        self.emulatorWindow = object


    def setupUi(self, DisassemblerWindow):

        self.init_operations()

        if self.emulatorWindow:
            print("Emulator ist Hauptfenster")
        else:
            print("Disassembler läuft standalone")

        ...
```

When the disassembler is called via the emulator, the status variables just discussed must of course be set. This is done within the emulator class in the method showDisassembler()

```bash
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
```

- befehle für disassemble von/bis noch implementieren
 
