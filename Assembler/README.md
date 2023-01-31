# Assembler
The creation of the assembler was the logical consequence after the completion of the disassembler. In principle, an assembler does the exact opposite of a disassembler. It translates the mnemonics into the bytecode which can be processed by the processor.

The page https://www.dev-insider.de/was-ist-ein-assembler-a-756636/ knows about assemblers: 

"An assembler translates code written in assembly language directly into binary code, where the code may be manual or machine-generated. For example, some compilers first convert program code into assembly code and then call an assembler. This in turn acts as a compiler itself and creates the machine code as a final step.

Assembler programs can use the complete instruction set of a processor, because for each assembler instruction there is exactly one counterpart at machine level. Modern high-level languages, on the other hand, are limited to a selection from the instruction set. Therefore, some languages offer the possibility to integrate assembler code if required.

Each processor has its own architecture and its own instruction set with which it can be addressed. Therefore each processor needs its own assembler including its own assembly language.

Only code written in this language can be understood and translated by the corresponding assembler. A program for processor A can therefore not be used by processor B without modifications - assembler programs are strongly platform dependent. In some cases, individual assembly languages differ only minimally."
