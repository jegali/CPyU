# Disassembler
The disassembler is the easiest piece of software to write. In principle a disassembler consists only of a table, which assigns an opcode to the individual bytecodes. Of course it must be noted which address mode the corresponding opcode is and how many bytes from memory the opcode needs. For a clean emulation later the table should also contain an overview of the required clock cycles. To be able to learn the processor specific assembly language better and faster, I also added a column with the description of the instruction in plain text to the table.<br/><br/>

As inspiration I used the disassembler/assembler/emulator from Masswerk, which is available on the internet and can be found at https://www.masswerk.at/6502/disassembler.html. 

![Masswerk_Disassembler](/images/masswerk-disassembler.png)

I rebuilt the interface in PyQT.
