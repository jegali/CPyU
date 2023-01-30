# CPyU - an emulation project for the 6502 CPU

by Jens Gaulke, 2022-2023 <br/><br/>
This is an emulation project for the 6502 CPU, hopefully expanding to the emulation of a complete Apple ][ computer. Started 2022, updated continously
The project is completely written in python.

## Credits

## Why Python
I decided to go with python because I wanted a platform independent language for this project. Execution speed of the interpreter should be fast enough to emulate the CPU step by step, and hopefully it is fast enough to emulate a complete computer like the Apple ][.

## Needed libraries
The project makes use of Qt, so PyQt has to be installed. I also used the pyqt-tools and the QT-Designer

```bash
pip install pyqt6
pip install pyqt6-tools
pip install PyQt5Designer
```

## Approach
The project is divided in several subparts I wanted to development independently from another.
Of course I thought about the structure of the project and the functions to be implemented, but the focus here is clearly on the learning factor and not on commercial software development. Therefore, I have deliberately avoided principles like Scrum or iterative models like the waterfall model. It is clear to me that this approach potentially leads to the need to restructure or even redevelop parts of the code. In order to be able to trace the development steps and perhaps even derive a pedagogical concept for an online course from them, I have stored the individual evolutionary stages in subdirectories.

## Status
2022-12-08: I started developing the disassemble unit<br/>
2022-12-09: [Disassembler V1](https://github.com/jegali/CPyU/tree/main/Disassembler/v1) - Designed the UI for the disassemble unit with QT Designer<br/>
2022-12-10: [Disassembler V2](https://github.com/jegali/CPyU/tree/main/Disassembler/v2) - Implemented a command line parser module for disassembling<br/>
2022-12-11: [Disassembler V3](https://github.com/jegali/CPyU/tree/main/Disassembler/v3) - Optimizied the command line parser module for disassembling<br/>
2022-12-12: [Disassembler V4](https://github.com/jegali/CPyU/tree/main/Disassembler/v4) - Integrated the cmd version with a GUI<br/>
