# Disassembler
The disassembler is the easiest piece of software to write. In principle a disassembler consists only of a table, which assigns an opcode to the individual bytecodes. Of course it must be noted which address mode the corresponding opcode is and how many bytes from memory the opcode needs. For a clean emulation later the table should also contain an overview of the required clock cycles. To be able to learn the processor specific assembly language better and faster, I also added a column with the description of the instruction in plain text to the table.<br/><br/>

As inspiration I used the disassembler/assembler/emulator from Masswerk, which is available on the internet and can be found at https://www.masswerk.at/6502/disassembler.html. 

![Masswerk_Disassembler](/images/masswerk-disassembler.png)

I rebuilt the interface in PyQT. For that, you have to install PyQT6 via the pip command in Powershell or terminal under MacOS / Linux. Interestingly enough, the PyQT-install also installs a tool called pyuic (pyuic6 for version 6) and a version of the qt-designer. The designer is used to build the GUI and pyuic is used to transform the GUI-Metadata to python code. Pyuic is not installed on the main path under Windows, but during the install you are informed where the file is stored.

```bash
pip install pyqt6
```

![PyQT_Install](/images/pyqt-install.png)

So add the path

```bash
C:\Users\jens\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts
```

to your system environment and path. Attention: this path may vary - depending on the installed version and the underlying operating system. If PyQT6 does not work with Python 3.10 or Python 3.11, do install a Python3.9 parallel. You can simply do that by downloading the installation packages from https://python.org
