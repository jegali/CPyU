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
