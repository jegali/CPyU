# CPU
In contrast to the Disassember and Assembler modules, I paid more attention to modularization and object orientation when creating the CPU and its components.
So the CPU is not a monolith, but I have sorted the CPU into the context in which it should work later. So there is a class Apple, which will realize the surrounding computer. Parts of the class Apple are the CPU, the RAM and the ROM. RAM and ROM as memory components inherit again from the class Memory.
