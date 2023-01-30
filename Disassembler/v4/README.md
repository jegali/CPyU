# The GUI version
The next step in the creation of the disassembler module was the integration of the command line version into a contemporary graphical user interface. For this the already presented user interface created in QT Designer was used. I made some changes to the source code of the disassembler, which will be discussed in the next sections.

## The Interface
The interface has all the features that I consider useful at the moment. There is a minimal hex-viewer at the top left, the possibility to load object or assembler files and - very important - the disassemble button. Depending on the selected function the output takes place with clock cycles, occupation and/or address mode.

![Disassembler_CMD](/images/disassembler.png)

So, pretty much of the functionality already shown on the command line can be found here.

##
