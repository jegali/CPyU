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

## Implementation details
We will now go through the main components of the code and explain how the assembler works.

First of all, for the lexical analysis of the source code to be assembled, the regular expression evaluation module is included. With the help of the regular expressions it can then be easily checked whether, on the one hand, valid code words have been used and, on the other hand, whether they have been used syntactically correctly.

```bash
# Form implementation generated from reading ui file '.\assembler.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.Qsci import *

from collections import OrderedDict
import re
import os
```

Besides the regular expressions, the orderedDict is also used. This dictionary is used to create the symbol table in which, for example, the labels just described are also stored and assigned. The next lines of code initialize global variables used by the assembler.

```bash
class Ui_AssemblerWindow(object):

    # Die Meldungen im Debug-Fenster werden zunächst in eine Liste geschrieben
    # Die Liste wird gefiltert und die gefilterten Meldungen angezeigt
    status_txt = list()

    # Der Quelltext aus dem Editor-Fenster wird vor Assemblierung in diese
    # Liste geladen und die Liste Liste dann zeilenweise abgearbeitet
    sourcecode = list()

    # Im ersten Pass werden Label gesammelt und ihnen 
    # eine Adresse zugewiesen. Das wird in diesem Dict gespeichert 
    label_dict = dict()

    # Jedes Quellprogramm wird ab $0 assembliert
    # Es sei denn, es gibt eine .ORG-Direktive
    program_counter = 0

    # Traten während der Assemblierläufe Fehler auf?
    pass1_error_count = 0
    pass2_error_count = 0

    # Der erzeugte Code während Pass 2 wird hier gespeichert
    code_dict = OrderedDict()
    
    # Diese Variable speichert die den Namen der geladenen Datei,
    # dieser wird in allen Dateivorgängen als Vorwauswahl angezeigt
    used_filename = None
```

Now the tables with the valid lexical terms follow - thus the individual commands and the structure of a code line of the assembler source text. Via the regular expressions the assignment of the commands in the source code to the corresponding byte code of the machine language is done.
 
```bash
    validdirectives = {'.DB', '.DW', '.DDW', '.DQW', '.STR', 
                       '.ORG', '.LE', '.BE', '.EQU', '.END'}

    validopcodes = {'ADC', 'AND', 'ASL', 'BCC', 'BCS', 'BEQ', 'BIT', 'BMI',
                    'BNE', 'BPL', 'BRK', 'BVC', 'BVS', 'CLC', 'CLD', 'CLI',
                    'CLV', 'CMP', 'CPX', 'CPY', 'DEC', 'DEX', 'DEY', 'EOR',
                    'INC', 'INX', 'INY', 'JMP', 'JSR', 'LDA', 'LDX', 'LDY',
                    'LSR', 'NOP', 'ORA', 'PHA', 'PHP', 'PLA', 'PLP', 'ROL',
                    'ROR', 'RTI', 'RTS', 'SBC', 'SEC', 'SED', 'SEI', 'STA', 
                    'STX', 'STY', 'TAX', 'TAY', 'TSX', 'TXA', 'TXS', 'TYA'}

    relative_address_mode_instructions = {
                    'BPL': '10', 'BMI': '30', 'BVC': '50', 'BVS':'70', 
                    'BCC': '90', 'BCS': 'B0', 'BNE': 'D0', 'BEQ': 'F0'
                    }

    address_mode_patterns_sym = {
                    '\#[0-9A-Z]{1,8}': 'Immediate', '[0-9A-Z+-]{1,8}': ('Zero Page', 'Absolute'), 
                    '[0-9A-Z]{1,8},X': ('Zero Page,X', 'Absolute,X'), '[0-9A-Z]{1,8},Y': ('Zero Page,Y', 'Absolute,Y'),  
                    '\([0-9A-Z]{1,8}\)': 'Indirect', '\([0-9A-Z]{1,8},X\)': 'Indirect,X', '\([0-9A-Z]{1,8}\),Y': 'Indirect,Y'
                    }

    address_mode_patterns = {
                    '\#\$[0-9A-F]{2}': 'Immediate', '\$[0-9A-F]{2}': 'Zero Page', '\$[0-9A-F]{2},X': 'Zero Page,X', 
                    '\$[0-9A-F]{2},Y': 'Zero Page,Y', '\$[0-9A-F]{4}': 'Absolute', '\$[0-9A-F]{4},X': 'Absolute,X',
                    '\$[0-9A-F]{4},Y': 'Absolute,Y', '\(\$[0-9A-F]{4}\)': 'Indirect', '\(\$[0-9A-F]{2},X\)': 'Indirect,X',
                    '\(\$[0-9A-F]{2}\),Y': 'Indirect,Y'
                    }
```

Next, we need a mapping table of the individual valid commands to the respective address mode:

```bash
   address_mode = {
    #   ROR A
        'Accumulator': (1, [ ('ASL', '0A'), ('LSR', '4A'), ('ROL', '2A'), ('ROR', '6A') ] ),

    #   SBC #$44
        'Immediate':   (2, [ ('ADC', '69'), ('AND', '29'), ('LDY', 'A0'), ('LDX', 'A2'), 
                            ('LDA', 'A9'), ('EOR', '49'), ('CPY', 'C0'), ('CPX', 'E0'), 
                            ('CMP', 'C9'), ('ORA', '09'), ('SBC', 'E9') ] ),

    #   SBC $44
        'Zero Page':   (2, [ ('ADC', '65'), ('AND', '25'), ('ASL', '06'), ('BIT', '24'), 
                            ('LSR', '46'), ('LDY', 'A4'), ('LDX', 'A6'), ('LDA', 'A5'), 
                            ('INC', 'E6'), ('EOR', '45'), ('DEC', 'C6'), ('CPY', 'C4'), 
                            ('CPX', 'E4'), ('CMP', 'C5'), ('ORA', '05'), ('ROL', '26'),
                            ('ROR', '66'), ('SBC', 'E5'), ('STA', '85'), ('STX', '86'),
                            ('STY', '84') ] ),

    #   SBC $44,X
        'Zero Page,X': (2, [ ('ADC', '75'), ('AND', '35'), ('ASL', '16'), ('CMP', 'D5'),
                            ('DEC', 'D6'), ('EOR', '55'), ('INC', 'F6'), ('LDA', 'B5'),
                            ('LDY', 'B4'), ('LSR', '56'), ('ORA', '15'), ('ROL', '36'),
                            ('ROR', '76'), ('SBC', 'F5'), ('STA', '95'), ('STY', '94') ] ),

    #   STX $44,Y
        'Zero Page,Y': (2, [ ('LDX', 'B6'), ('STX', '96') ] ),

    #   STX $4400
        'Absolute':    (3, [ ('ADC', '6D'), ('AND', '2D'), ('ASL', '0E'), ('BIT', '2C'), 
                            ('CMP', 'CD'), ('CPX', 'EC'), ('CPY', 'CC'), ('DEC', 'CE'),
                            ('EOR', '4D'), ('INC', 'EE'), ('JMP', '4C'), ('JSR', '20'),
                            ('LDA', 'AD'), ('LDX', 'AE'), ('LDY', 'AC'), ('LSR', '4E'),
                            ('ORA', '0D'), ('ROL', '2E'), ('ROR', '6E'), ('SBC', 'ED'),
                            ('STA', '8D'), ('STX', '8E'), ('STY', '8C') ] ),

    #   STA $4400,X
        'Absolute,X':  (3, [ ('ADC', '7D'), ('AND', '3D'), ('ASL', '1E'), ('CMP', 'DD'),
                            ('DEC', 'DE'), ('EOR', '5D'), ('INC', 'FE'), ('LDA', 'BD'),
                            ('LDY', 'BC'), ('LSR', '5E'), ('ORA', '1D'), ('ROL', '3E'),
                            ('SBC', 'FD'), ('STA', '9D') ] ),

    #   STA $4400,Y
        'Absolute,Y':  (3, [ ('ADC', '79'), ('AND', '39'), ('CMP', 'D9'), ('EOR', '59'),
                            ('LDA', 'B9'), ('LDX', 'BE'), ('ORA', '19'), ('SBC', 'F9'),
                            ('STA', '99') ] ),

    #   JMP ($5597)
        'Indirect':    (3, [ ('JMP', '6C') ] ),

    #   LDA ($44,X)
        'Indirect,X':  (2, [ ('ADC', '61'), ('AND', '21'), ('CMP', 'C1'), ('EOR', '41'),
                            ('LDA', 'A1'), ('ORA', '01'), ('SBC', 'E1'), ('STA', '81') ] ),

    #   LDA ($44),Y
        'Indirect,Y':  (2, [ ('ADC', '71'), ('AND', '31'), ('CMP', 'D1'), ('EOR', '51'),
                            ('LDA', 'B1'), ('ORA', '11'), ('SBC', 'F1'), ('STA', '91') ] ),

    #   BRK
        'Implied':     (1, [ ('BRK', '00'), ('CLC', '18'), ('SEC', '38'), ('CLI', '58'),
                            ('SEI', '78'), ('CLV', 'B8'), ('CLD', 'D8'), ('SED', 'F8'),
                            ('TAX', 'AA'), ('TXA', '8A'), ('DEX', 'CA'), ('INX', 'E8'),
                            ('TAY', 'A8'), ('TYA', '98'), ('DEY', '88'), ('INY', 'C8'),
                            ('TXS', '9A'), ('TSX', 'BA'), ('PHA', '48'), ('PLA', '68'),
                            ('PHP', '08'), ('PLP', '28'), ('NOP', 'EA'), ('RTI', '40'),
                            ('RTS', '60') ] )
    }
```

## File operations
As already described in the disassembler, the graphical variant of the assembler also uses file operation to load and save files using Qt's built-in file dialogs:

```bash
   #
    # def saveObjFile(self):
    #
    # Diese Methode speichert das generierte Object-Listing
    # als .obj Datei
    #
    
    def saveObjFile(self):
        fileName, _ = QFileDialog.getSaveFileName(None, 
            "Save File", self.used_filename, "All Files(*);;Object Code Files (*.obj)")

        if fileName:
            with open(fileName, 'w') as f:
                f.write(self.txtEditObjectcode.toPlainText())



    #
    # def saveLstFile(self):
    #
    # Diese Methode speichert das generierte Assembler-Listing
    # als .lst Datei
    #
    
    def saveLstFile(self):
        fileName, _ = QFileDialog.getSaveFileName(None, 
            "Save File", self.used_filename, "All Files(*);;Assembler List Files (*.lst)")

        if fileName:
            with open(fileName, 'w') as f:
                f.write(self.txtEditAssembler.toPlainText())



    #
    # def saveSourcecode(self):
    #
    # Diese Methode speichert den Inhalt des QScintilla-Editorfensters ab
    # Das ist der (Assemblerquelltext)
    #

    def saveSourcecode(self):
        fileName, _ = QFileDialog.getSaveFileName(None, 
            "Save File", self.used_filename, "All Files(*);;Assembler Source Files (*.asm)")

        if fileName:
            with open(fileName, 'w') as f:
                f.write(self.sciEditSourcecode.text())
    

    #
    # def loadSourcecode(self):
    # 
    # Dies ist die Behandlungsroutine für den Click auf den Button "Load Sourcecode"
    # 
     
    def loadSourcecode(self):
        # File Dialog liefert die angeklickte Datei zurück
        self.sourcecode.clear()
        fname = QFileDialog.getOpenFileName(None, "Open File", ".\\", "Assembler Source Files (*.asm)")
        if fname[0]:
            used_path, used_filename = os.path.split(fname[0])
            self.used_filename = used_filename.split('.')[0]
            self.sciEditSourcecode.clear()
            with open(fname[0], "r") as input_file:
                for line in input_file:
                    self.sourcecode.append(line.strip("\r").strip("\n"))
                    self.sciEditSourcecode.append(line)
            # Die Breite der Spalte für die Zeilennummerierung festlegen (plus eine Extrastelle) 
            self.sciEditSourcecode.setMarginWidth(0, str(self.sciEditSourcecode.lines())+"0")

```

## Avengers... assemble!
No copyright infringement intended. Avengers and Avengers assemble is a trademark of Marvel, the creators of the finest comic books in the universe. This two words just fit for an assembler... and now to work, Avengers. Time to see the assemble code. The code is split up in some methods. First we have the assemble method. It clears all textfields and does some error checking for the loaded file before the assembly process starts.

As stated above, I decided to go with a two pass assembler. Basically, the program is run twice. Im the first pass, the file is analyzed and the symbol table is build. In the second pass, every symbol is replaced and the file is analyzed again and then finally translated. The third pass is just here to make it more beautiful.

```bash
    #
    # def assemble(self):
    #
    # xxx mal drüber nachdenken:
    # xxx brauchen wir die Liste tatsächlich, oder kann
    # xxx der Assembler aus dem Editor gefüttert werden ?


    def assemble(self):
        # Wenn kein Quelltext geladen oder eingegeben wurde,
        # eine Warnmeldung ausgeben
        if self.sciEditSourcecode.length() == 0:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Warning")
            msgBox.setText("No sourcecode to assemble.\nPlease load or enter Code.")
            msgBox.exec()
        else:
            # Die Liste mit dem zu untersuchenden Quelltext löschen
            self.sourcecode.clear()
            # Den Quelltext aus dem Editor in die Liste laden
            for line in range(self.sciEditSourcecode.lines()):
                self.sourcecode.append(self.sciEditSourcecode.text(line).strip("\r").strip("\n"))

            self.reset_vars()

            self.log_status("Avengers... assemble", "always")
            self.log_status(" ", "always")
            self.log_status("Starting Pass 1", "always")

            # der Quelltext wird zweimal durchlaufen
            # Pass 1: Finde alle Label, deren Adressen,
            #         und baue die Symboltabelle auf
            # Pass 2: Ersetze alle Label durch Adressen und
            #         reloziere Jumps 
            # Pass 3: schreibe die Objektdatei

            self.pass_1()

            if self.pass1_error_count > 0:
                self.log_status(" ", "always")
                self.log_status("Error(s) encountered", "always")
                self.log_status("Unable to continue", "always")
                self.log_status(" ", "always")
            else:
                self.log_status("Pass 1 completed successfully", "always")
                self.log_status(" ", "always")
                self.log_status("Starting Pass 2", "always")
                self.log_status(" ", "always")
                self.pass_2()

            if self.pass2_error_count > 0:
                self.log_status(" ", "always")
                self.log_status("Error(s) encountered", "always")
                self.log_status("Unable to continue", "always")
                self.log_status(" ", "always")
            else:
                self.log_status("Pass 2 completed successfully", "always")
                self.log_status(" ", "always")
                self.log_status("Creating Object File", "always")
                self.log_status(" ", "always")
                self.pass_3()

            self.show_status()
```

The methods pass_1(), pass_2() and pass_3() then do the actual work. Pass_2() is almost 80% a copy of pass_1(). Still, I took a quick and dirty approach and just wrote the method twice.

```bash
   #
    # def pass_3(self):
    #
    # Diese Methode nimmt den generierten Quellcode
    # trennt die Bytes mit einem ' ' und schreibt das
    # Ergebnis in das Onject-Textfeld
    #

    def pass_3(self):
        total_code = ''
        for address in self.code_dict:
            code = self.code_dict[address]
            total_code = total_code + code
        
        blanked = ' '.join(total_code[i:i+2] for i in range(0,len(total_code),2))    
        self.txtEditObjectcode.appendPlainText(blanked)



    def pass_1(self):
        # So lange wir keine .ORG Direktive finden, ist davon auszugehen, 
        # dass das Programm bei $0000 beginnt
        self.program_counter = 0
        # Jede Zeile durchgehen
        for line in self.sourcecode:
            # besteht die Zeile aus Leerzeichen oder nur einem Return?
            # dann weiter mit der nächsten Zeile
            if len(line) == 0 or line.isspace():
                continue
            else:
                # die Token kommen als Liste zurück
                # label: lda #3   ; comment
                # liefert [0]: label, [1] lda, [2] #3
                token = self.tokenize(line)
                # Wenn eine Zeile aus einem Kommentar besteht, 
                # hat sie keine Token. Dann weiter mit der nächsten Zeile
                if len(token) == 0:
                    continue 

            # Wir haben Token. Nun überprüfen, ob es sich um gültige
            # Opcodes (LDA, STX, RTS, ...) oder Direktiven (.EQU, .END, .DB, ...) handelt 
            if (token[0] not in self.validopcodes) and (token[0] not in self.validdirectives):
                # Wenn es kein Opcode und keine Direktive ist, ist es ein Label. Punkt.
                # Über pop(0) wird das Element aus der Liste entfernt
                label = token.pop(0)
                # Den Label in das Dictionary eintragen und die aktuelle
                # Programmadresse (in hex umgewandelt) als Wert eintragen
                # Der program_counter muss nicht hochgezählt werden, 
                # ein Label verändert die aktuelle Adresse nicht.
                self.label_dict[label] = self.int2hex(self.program_counter, 4)

            # Wenn wir immer noch 2 Token übrig haben, überprüfen wir auf 
            # Immediate Operanden (also alles, was mit "#" beginnt) 
            if (len(token) == 2) and (token[1].startswith('#')):
                # Es gibt unterschiedliche immediate operands: 
                # #$0A, #128, #'C', #%00001111
                # und wir brauchen alle im hex-Format
                if token[1][1].isdigit():
                    token[1] = '#' + '$' + self.int2hex(int(token[1][1:]), 2)
                elif token[1][1] == "'":
                    token[1] = '#' + '$' + self.int2hex(ord(token[1][2:3]), 2)
                elif token[1][1] == "%":
                    token[1] = '#' + '$' + self.int2hex(int(token[1][2:],2), 2) 
        
            # Das noch vorhandene Token an der ersten Stelle könnte eine Direktive sein.
            # Das untersuchen wir als erstes
            if token[0] == '.ORG':
                self.program_counter = int(token[1][1:],16)
            elif token[0] == '.DB':
                num_data_bytes, data_bytes = self.build_data_bytes(token[1])
                self.program_counter = self.program_counter + num_data_bytes
            elif token[0] == '.DS':
                self.program_counter = self.program_counter + int(token[1])
            elif token[0] == '.EQU':
                num_data_bytes, data_bytes = self.build_data_bytes(token[1])
                self.label_dict[label] = data_bytes
            elif token[0] == '.END':
                if self.pass1_error_count == 0:
                    print('Pass 1 Complete - No Errors Encountered')
                else:
                    print('Pass 1 Complete - ', self.pass1_error_count, 'Error(s) Encountered')
                print(' ')
                break             

            # Dann gibt es noch die relativen Adressmodi...
            elif token[0] in self.relative_address_mode_instructions and re.fullmatch('[0-9A-Z]{1,8}', token[1]) != None:
                self.program_counter = self.program_counter + 2

            # Und den ganzen Rest
            else:
                # Bei zwei Token haben wir einen Opcode und einen Operanden
                if len(token) == 2:
                    operand = token[1]
                    if not '$' in operand:
                        for adrmode in self.address_mode_patterns_sym.keys():
                            z = re.fullmatch(adrmode, operand)
                            if z != None:
                                mode = self.address_mode_patterns_sym[adrmode]
                            if isinstance(mode, tuple):
                                if 'Zero Page' in mode:
                                    label = operand
                                elif 'Zero Page,X' in mode:
                                    label = operand.rstrip(',X')
                                elif 'Zero Page,Y' in mode:
                                    label = operand.rstrip(',Y')
                            else:
                                if mode == 'Indirect':
                                    label = operand.lstrip('(').rstrip(')')
                                elif mode == 'Indirect,X':
                                    label = operand.lstrip('(').rstrip(',X)')
                                elif mode == 'Indirect,Y':
                                    label = operand.lstrip('(').rstrip('),Y')
                                elif mode == 'Immediate':   
                                    label = operand.lstrip('#')
                            # handle arithmetic in symbolic label
                            z = re.search('[0-9+-]{2,4}', label)
                            if z != None:
                                f, t = z.span()
                                label = label[0:f]
                            if label in self.label_dict:
                                operand = '$' + self.label_dict[label]
                            else:
                                operand = '$FFFF'
                                self.label_dict[label] = operand
                            if isinstance(mode, tuple):
                                if 'Zero Page,X' in mode:
                                    operand = operand + ',X'
                                elif 'Zero Page,Y' in mode:
                                    operand = operand + ',Y'
                            else:
                                if mode == 'Indirect':
                                    operand = '(' + operand + ')'
                                elif mode == 'Indirect,X':
                                    operand = '(' + operand + ',X)'
                                elif mode == 'Indirect,Y':
                                    operand = '(' + operand + '),Y'
                                elif mode == 'Immediate':   
                                    operand = '#' + operand                            
                            break
                        
                    am, nb, oc = self.determine_mode(token[0], operand)
                    self.pass1_error_check(token, am, oc)

                # Bei einem Token haben wir nur einen Opcode
                elif len(token) == 1:
                    am, nb, oc = self.determine_mode(token[0], '')
                    self.pass1_error_check(token, am, oc)
                
                # Bei gar keinem Token haben wir ein Problem
                # bei mehr als zwei Token auch... solche Befehle gibt es nicht
                else:
                    self.pass1_error_count += 1
                    print('Error on:', token, ' - Too Many Tokens')
                    
                self.program_counter = self.program_counter + nb    



    def pass_2(self):
        # So lange wir keine .ORG Direktive finden, ist davon auszugehen, 
        # dass das Programm bei $0000 beginnt
        self.program_counter = 0
        # Jede Zeile durchgehen
        for line in self.sourcecode:
            # besteht die Zeile aus Leerzeichen oder nur einem Return?
            # dann weiter mit der nächsten Zeile
            if len(line) == 0 or line.isspace():
                #print(line)
                self.txtEditAssembler.appendPlainText(line) 
                continue
            else:
                # die Token kommen als Liste zurück
                # label: lda #3   ; comment
                # liefert [0]: label, [1] lda, [2] #3
                token = self.tokenize(line)
                # Wenn eine Zeile aus einem Kommentar besteht, 
                # hat sie keine Token. Dann weiter mit der nächsten Zeile
                if len(token) == 0:
                    #print(line)
                    self.txtEditAssembler.appendPlainText(line) 
                    continue        
            
            # Wir haben Token. Nun überprüfen, ob es sich um gültige
            # Opcodes (LDA, STX, RTS, ...) oder Direktiven (.EQU, .END, .DB, ...) handelt 
            if (token[0] not in self.validopcodes) and (token[0] not in self.validdirectives):
                # Wenn es kein Opcode und keine Direktive ist, ist es ein Label. Punkt.
                # Über pop(0) wird das Element aus der Liste entfernt
                label = token.pop(0)

            # Wenn wir immer noch 2 Token übrig haben, überprüfen wir auf 
            # Immediate Operanden (also alles, was mit "#" beginnt) 
            if (len(token) == 2) and (token[1].startswith('#')):
                # Es gibt unterschiedliche immediate operands: 
                # #$0A, #128, #'C', #%00001111
                # und wir brauchen alle im hex-Format
                if token[1][1].isdigit():
                    token[1] = '#' + '$' + self.int2hex(int(token[1][1:]), 2)
                elif token[1][1] == "'":
                    token[1] = '#' + '$' + self.int2hex(ord(token[1][2:3]), 2)
                elif token[1][1] == "%":
                    token[1] = '#' + '$' + self.int2hex(int(token[1][2:],2), 2)

            # Das noch vorhandene Token an der ersten Stelle könnte eine Direktive sein.
            # Das untersuchen wir als erstes

            if token[0] == '.ORG':
                self.program_counter = int(token[1][1:],16)
                lineout = self.myprint(line, 'pc =', self.program_counter)
                self.txtEditAssembler.appendPlainText(lineout)   
            elif token[0] == '.DB':
                num_data_bytes, data_bytes = self.build_data_bytes(token[1])
                lineout = self.myprint(line, self.int2hex(self.program_counter, 4), ':', data_bytes)
                self.txtEditAssembler.appendPlainText(lineout)   
                self.code_dict[self.int2hex(self.program_counter, 4)] = data_bytes
                self.program_counter = self.program_counter + num_data_bytes
            elif token[0] == '.DS':
                lineout = self.myprint(line, self.int2hex(self.program_counter, 4), ':', 'Reserved', token[1], 'Bytes')
                self.txtEditAssembler.appendPlainText(lineout)   
                self.program_counter = self.program_counter + int(token[1])
            elif token[0] == '.EQU':
                num_data_bytes, data_bytes = self.build_data_bytes(token[1])
                lineout = self.myprint(line, label, '=', data_bytes)
                self.txtEditAssembler.appendPlainText(lineout)   
            elif token[0] == '.END':
                lineout = self.myprint(line, self.int2hex(self.program_counter, 4))
                self.txtEditAssembler.appendPlainText(lineout)   
                print(' ')
                if self.pass2_error_count == 0:
                    print('Pass 2 Complete - No Errors Encountered')
                else:
                    print('Pass 2 Complete - ', self.pass2_error_count, 'Error(s) Encountered')
                print(' ')
                print('Assembly Complete')
                break

            # Dann gibt es noch die relativen Adressmodi...
            elif token[0] in self.relative_address_mode_instructions and re.fullmatch('[0-9A-Z]{1,8}', token[1]) != None:
                oc = self.relative_address_mode_instructions[token[0]]
                x = int(self.label_dict[token[1]], 16) - self.program_counter
                if x > 127 or x < -128:
                    self.pass2_error_count += 1
                    print('Error on:', token, ' - Relative Displacment Out of Range')
                else:
                    if x < 0:
                        disp = self.cvtint2scomp(x-2)
                    else:    
                        disp = hex(x-2)[2:].zfill(2).upper()
                    lineout = self.myprint(line, self.int2hex(self.program_counter, 4), ':', oc, disp)
                    self.txtEditAssembler.appendPlainText(lineout)   
                    self.code_dict[self.int2hex(self.program_counter, 4)] = oc + disp             
                    self.program_counter = self.program_counter + 2
            
            else:
                if len(token) == 2:
                    oper = token[1]
                    if not '$' in oper:
                        for p in self.address_mode_patterns_sym.keys():
                            z = re.fullmatch(p, oper)
                            if z != None:
                                mode = self.address_mode_patterns_sym[p]
                                if isinstance(mode, tuple):
                                    if 'Zero Page' in mode:
                                        label = oper
                                    elif 'Zero Page,X' in mode:
                                        label = oper.rstrip(',X')
                                    elif 'Zero Page,Y' in mode:
                                        label = oper.rstrip(',Y')
                                else:
                                    if mode == 'Indirect':
                                        label = oper.lstrip('(').rstrip(')')
                                    elif mode == 'Indirect,X':
                                        label = oper.lstrip('(').rstrip(',X)')
                                    elif mode == 'Indirect,Y':
                                        label = oper.lstrip('(').rstrip('),Y')
                                    elif mode == 'Immediate':   
                                        label = oper.lstrip('#')
                                # handle arithmetic in symbolic label
                                z = re.search('[0-9+-]{2,4}', label)
                                if z != None:
                                    f, t = z.span()
                                    exp = label[f:t]
                                    label = label[0:f]
                                    lab_len = len(self.label_dict[label])
                                    x = eval(str(int(self.label_dict[label], 16)) + exp)
                                    if lab_len == 2 and x < 256:
                                        oper = '$' + self.int2hex(x, 2)
                                    elif lab_len == 4 and x < 65536:
                                        oper = '$' + self.int2hex(x, 4)
                                    else:
                                        self.pass2_error_count += 1
                                        print('Error on:', token, ' - Symbol Arithmetic Overflow')
                                        oper = '$FF'
                                        if lab_len == 4:
                                            oper += 'FF'
                                else:
                                    oper = '$' + self.label_dict[label]

                                if isinstance(mode, tuple):
                                    if 'Zero Page,X' in mode:
                                        oper = oper + ',X'
                                    elif 'Zero Page,Y' in mode:
                                        oper = oper + ',Y'
                                else:
                                    if mode == 'Indirect':
                                        oper = '(' + oper + ')'
                                    elif mode == 'Indirect,X':
                                        oper = '(' + oper + ',X)'
                                    elif mode == 'Indirect,Y':
                                        oper = '(' + oper + '),Y'
                                    elif mode == 'Immediate':   
                                        oper = '#' + oper                            
                                break
                        
                    am, nb, oc = self.determine_mode(token[0], oper)
                elif len(token) == 1:
                    am, nb, oc = self.determine_mode(token[0], '')
                        
                if am == 'Implied' or am == 'Accumulator':
                    lineout = self.myprint(line, self.int2hex(self.program_counter, 4), ':', oc)
                    self.txtEditAssembler.appendPlainText(lineout)   
                    self.code_dict[self.int2hex(self.program_counter, 4)] = oc
                elif am == 'Immediate' or am == 'Indirect,X' or am == 'Indirect,Y':
                    lineout = self.myprint(line, self.int2hex(self.program_counter, 4), ':', oc, oper[2:4])
                    self.txtEditAssembler.appendPlainText(lineout)   
                    self.code_dict[self.int2hex(self.program_counter, 4)] = oc + oper[2:4]
                elif am == 'Zero Page' or am == 'Zero Page,X' or am == 'Zero Page,Y': 
                    lineout = self.myprint(line, self.int2hex(self.program_counter, 4), ':', oc, oper[1:3])
                    self.txtEditAssembler.appendPlainText(lineout)   
                    self.code_dict[self.int2hex(self.program_counter, 4)] = oc + oper[1:3]
                elif am == 'Absolute' or am == 'Absolute,X' or am == 'Absolute,Y':
                    lineout = self.myprint(line, self.int2hex(self.program_counter, 4), ':', oc, oper[3:5], oper[1:3])
                    self.txtEditAssembler.appendPlainText(lineout)   
                    self.code_dict[self.int2hex(self.program_counter, 4)] = oc + oper[3:5] + oper[1:3]
                elif am == 'Indirect':
                    lineout = self.myprint(line, self.int2hex(self.program_counter, 4), ':', oc, oper[4:6], oper[2:4])    
                    self.txtEditAssembler.appendPlainText(lineout)   
                    self.code_dict[self.int2hex(self.program_counter, 4)] = oc + oper[4:6] + oper[2:4]
                
                self.program_counter = self.program_counter + nb
```

## Helper functions
Last but not least, the clss containes some helper functions. I will show them here but not explain them further:

```bash
    #
    # def tokenize(self, line):
    #
    # Diese Methode zerstückelt die Codezeile in einzelne Token
    #

    def tokenize(self, line):
        # Gibt es einen Kommentar ?
        comment_position = line.find(';')
        # -1 bedeutet, dass kein ";" gefunden wurde
        if comment_position == -1:
            # dann benötigen wir die ganze Zeile
            comment_position = len(line)
    
        # die Zeile entlang der Blanks aufspalten. Da bei Mehrfachblanks '' entstehen können,
        # werden diese durch die integrierte if-Abfrage entfernt
        return [token for token in line[0:comment_position].upper().split(' ') if token != '']


 
    #
    # def show_status(self):
    #
    # This method filters the log messages according to the 
    # set checkbox info | warn | error | all
    #

    def show_status(self):
        self.txtEditDebug.clear()
        search_for = "(^always:)"
        if self.chkAll.isChecked():
            search_for += "|(.*)"
        else:
            if self.chkInfo.isChecked():
                search_for += "|(^info:)"
            if self.chkWarning.isChecked():
                search_for += "|(^warning:)"
            if self.chkError.isChecked():
                search_for += "|(^error:)"

        reg = re.compile(search_for)
        filtered_text = list(filter(reg.search, self.status_txt))
        for line in filtered_text:
            line = re.sub('always:', '', line)
            self.txtEditDebug.appendPlainText(line)



    #
    # def log_status(self, line, level):
    #
    # This method logs the different outputs in different levels
    #

    def log_status(self, line, level):
        self.status_txt.append(level+": " + line)


    #
    # def int2hex(x,y):
    #
    # Diese Methode wandelt einen int-Wert (x)
    # in einen hex-Wert der Länge (y) um
    #

    def int2hex(self,x,y):
        return hex(x)[2:].zfill(y).upper() 



    def determine_mode(self, mnemonic, operand):
        mode = 'Invalid'
        if operand == '':
            mode = 'Implied'
        elif operand == 'A':
            mode = 'Accumulator'
        else:
            for p in self.address_mode_patterns.keys():
                z = re.fullmatch(p, operand)
                if z != None:
                    mode = self.address_mode_patterns[p]        
                    break

        if mode == 'Invalid':
            return (mode, 9, 'XX')
        
        numbytes = self.address_mode[mode][0]
        good_mnemonic = False
        for m, opc in self.address_mode[mode][1]:
            if m == mnemonic:
                good_mnemonic = True
                break
        if good_mnemonic:
            return (mode, numbytes, opc)
        else:
            return (mode, numbytes, 'XX')



    def cvtint2scomp(self, x):
        t = bin(x)[3:]
        b = '0'*(8-len(t)) + t   #expand by propagating a '0' out to 8 bits
        #flip the bits in b creating num1 
        num1 = ''
        for bit in b:
            if bit == '0':
                num1 = num1 + '1'
            else:
                num1 = num1 + '0'
        return hex(int(num1,2) + int('0001',2))[2:].upper()



    def build_data_bytes(self, operand):
        db_str = ''
        for db in operand.split(','):
            if db.startswith('$'):
                db_str = db_str + db[1:]
            elif db[0].isdigit():
                h = hex(int(db))[2:].upper()
                if (len(h) % 2) != 0:
                    db_str = db_str + '0' + h
                else:
                    db_str = db_str + h
            elif db[0] == "'":
                for c in db:
                    if c == "'":
                        continue
                    else:
                        db_str = db_str + hex(ord(c))[2:].zfill(2).upper()
            elif db[0] == '%':                   
                db_str = db_str + hex(int(db[1:],2))[2:].zfill(2).upper()
        nb = len(db_str) // 2        
        return (nb, db_str)



    def myprint(self, sline, *arguments):
        z = ''
        for arg in arguments:
            if isinstance(arg, str):
                z = z + arg + ' '
            else:
                z = z + str(arg) + ' '
        l = len(z)
        if l > 25:
            z = z[0:26]
        else:
            z = z + (25-l)*' '
        print(z, sline)
        return z + ' ' + sline



    def pass1_error_check(self, t, a, o):
        if o == 'XX':
            self.pass1_error_count += 1
            if a == 'Invalid':
                print('Error:', t[1], ' - Invalid Operand')
            else:
                print('Error:', t[0], ' - Invalid Mnemonic for the specified Addressing Mode')
        return


    def reset_vars(self):
        self.program_counter = 0
        self.pass1_error_count = 0
        self.pass2_error_count =0
        self.label_dict = dict()
        self.code_dict = OrderedDict()
        self.txtEditDebug.clear()
        self.txtEditAssembler.clear()
        self.status_txt.clear()
```
