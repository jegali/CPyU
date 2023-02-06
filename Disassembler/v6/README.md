# Changes
This version of the disassembler has some small innovations and improvements . As always, we will go through and discuss these changes one by one.

# Mouse Cursor during diassembly
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


- einen bestimmten befehl decodieren
- wie viele Bytes maximal kann ein befeh haben -> 3 
- also drei bytes und due adresse übergeben

- speicherbereich an die unit übergeben
- einzelne befehle aus dem speicher disassemblieren

- wie speicherbereich updaten, falls ein programm den speicher verändert?
- jedes mal 64KB daten übergeben?

- wie wäre es mit einem zusätzlichen Button "get apple memory" anstelle von "load code"
- wie? die Datenübergabe herstellen?
- Emulator kennt disassembler
- woher kennt disassembler emulator

- befehle für disassemble von/bis noch implementieren
 
