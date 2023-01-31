# The GUI version
Based on the experience with the disassembler module, I integrated the assembler function directly into the graphical user interface.

## The Interface
This user interface also has some quirks that I would like to discuss. The first thing to mention is that errors can occur during an assembly process, since a source code is translated into machine language. Unlike the disassembler, which translates executable code back, source code is usually created by a human and therefore there is always a certain probability that the code contains errors.

Thus, if errors occur during the assembly process, they will occur in a particular line of source code. Thus it is helpful if the corresponding erroneous line number is output - and the user is able to find the line again in the source code. For this reason I replaced the standard text component of Qt - with the Qscintilla editor component with integrated line numbering, syntax highlighting and other great features. To use the component, it must be installed via pip. At the console, enter this command:

```bash
pip install pyqt6-qscintilla
```
