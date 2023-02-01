# The GUI version
Based on the experience with the disassembler module, I integrated the assembler function directly into the graphical user interface.

## The Interface
This user interface also has some quirks that I would like to discuss. The first thing to mention is that errors can occur during an assembly process, since a source code is translated into machine language. Unlike the disassembler, which translates executable code back, source code is usually created by a human and therefore there is always a certain probability that the code contains errors.

Thus, if errors occur during the assembly process, they will occur in a particular line of source code. Thus it is helpful if the corresponding erroneous line number is output - and the user is able to find the line again in the source code. For this reason I replaced the standard text component of Qt - with the Qscintilla editor component with integrated line numbering, syntax highlighting and other great features. To use the component, it must be installed via pip. At the console, enter this command:

```bash
pip install pyqt6-qscintilla
```

After that, the component must be imported in the source code. For this purpose these import statements in the source code are necessary:

```bash
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.Qsci import *
```

After that, only the TextEdit component of Qt has to be exchanged for the one of QScintilla.
Here is the source code of the Qt component:

```bash
self.txtEditSourceode = QtWidgets.QPlainTextEdit(self.centralwidget)
self.txtEditSourceode.setGeometry(QtCore.QRect(20, 40, 381, 281))
font = QtGui.QFont()
font.setFamily("Courier New")
font.setPointSize(11)
self.txtEditSourceode.setFont(font)
self.txtEditSourceode.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
self.txtEditSourceode.setReadOnly(False)
self.txtEditSourceode.setObjectName("txtEditSourceode")
```

And here is the source code for the integration of the QScintilla component:

```bash
self.sciEditSourcecode = QsciScintilla(self.centralwidget)
self.sciEditSourcecode.setGeometry(QtCore.QRect(20, 40, 581, 281))
self.sciEditSourcecode.setFont(font)
self.sciEditSourcecode.setUtf8(True)
self.sciEditSourcecode.setMarginWidth(0, "0000")
self.sciEditSourcecode.setCaretLineVisible(True)
self.sciEditSourcecode.setCaretLineBackgroundColor(QtGui.QColor('lightblue'))
self.sciEditSourcecode.setObjectName("sciEditSourcecode")
```

As you can clearly see, the QScintilla component (top left) looks different from the PlaintText component (top right)

![Assembler_GUI](/images/assembler-v1.png)

## How the assembler works
I have decided to implement a two-pass assembler. What is the difference between an assembler and a two-pass assembler? Let http://users.cis.fiu.edu/~downeyt/cop3402/two-pass.htm explain it:

"An assembler is a translator, that translates an assembler program into a conventional machine language program. Basically, the assembler goes through the program one line at a time, and generates machine code for that instruction. Then the assembler procedes to the next instruction. In this way, the entire machine code program is created. For most instructions this process works fine, for example for instructions that only reference registers, the assembler can compute the machine code easily, since the assembler knows where the registers are.

Consider an assembler instruction like the following

```bash 
          JMP  LATER
          ...
          ...
LATER:
```

This is known as a forward reference. If the assembler is processing the file one line at a time, then it doesn't know where LATER is when it first encounters the jump instruction. So, it doesn't know if the jump is a short jump, a near jump or a far jump. There is a large difference amongst these instructions. They are 2, 3, and 5 bytes long respectively. The assembler would have to guess how far away the instruction is in order to generate the correct instruction. If the assembler guesses wrong, then the addresses for all other labels later in the program woulds be wrong, and the code would have to be regenerated. Or, the assembler could alway choose the worst case. But this would mean generating inefficiency in the program, since all jumps would be considered far jumps and would be 5 bytes long, where actually most jumps are short jumps, which are only 2 bytes long.
Soooooooo, what is to be done to allow the assembler to generate the correct instruction? Answer: scan the code twice. The first time, just count how long the machine code instructions will be, just to find out the addresses of all the labels. Also, create a table that has a list of all the addresses and where they will be in the program. This table is known as the symbol table. On the second scan, generate the machine code, and use the symbol table to determine how far away jump labels are, and to generate the most efficient instruction.

This is known as a two-pass assembler. Each pass scans the program, the first pass generates the symbol table and the second pass generates the machine code."

