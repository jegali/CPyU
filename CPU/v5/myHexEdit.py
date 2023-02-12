#
# Diese Klasse realisiert meinen Hex-Editor
#


from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QKeyEvent

#
# class myTextEdit(QtWidgets.QPlainTextEdit):
#
# Ich habe hier von der Klasse QPlainTextEdit
# eine Subklasse angelegt, um Tastendrücke abfangen zu können
# Editierbewegungen im hexeditor
# 

class myHexEdit(QtWidgets.QPlainTextEdit):  
    def __init__(self, parent=None):
        QtWidgets.QPlainTextEdit.__init__(self, parent)
        self.setOverwriteMode(True)


    # Der Benutzer nutzt innerhalb des Editierfeldes
    # die Tasten A-F, 0-9 oder die Pfeiltasten

    def keyPressEvent(self, event):
        myCursor = QtGui.QTextCursor(self.document())

        # Hier wird der editierbare Bereich eingegrenzt. Das sind die Spalten 7-55 und
        # die Anzahl der Zeilen in dem Textedit
        if self.textCursor().columnNumber() >= 7 and self.textCursor().columnNumber() <= 55 and \
            self.textCursor().blockNumber() < self.document().lineCount():

            # Das Ende der Zeile ist erreicht, wir benötigen einen Zeilenvorschub (falls möglich)
            if self.textCursor().columnNumber() == 55 and \
                self.textCursor().blockNumber() < self.document().lineCount()-1:
                myCursor.setPosition(7 + (self.textCursor().blockNumber()+1)*75)
                self.setTextCursor(myCursor)
            # falls wir bereits in der letzten Zeile sind, brich die Eingabebehandlung ab
            elif self.textCursor().columnNumber() == 55 and \
                self.textCursor().blockNumber() == self.document().lineCount()-1:
                return

            # Es sind als Eingabe nur die hexadezimalen Zeichen a-fA-F0.9 erlaubt
            # a-f werden durch die Behandlung auf uppercase gesetzt 
            if event.key() in (QtCore.Qt.Key.Key_A.value, QtCore.Qt.Key.Key_B.value,
                            QtCore.Qt.Key.Key_C.value, QtCore.Qt.Key.Key_D.value,
                            QtCore.Qt.Key.Key_E.value, QtCore.Qt.Key.Key_F.value) or \
                event.key() >= QtCore.Qt.Key.Key_0 and event.key() <= QtCore.Qt.Key.Key_9:
                text = event.text()
                text = text.upper()
                # Der Cursor muss um zwei Positionen versetzt werden, wenn er auf einem Leerzeichen zwischen den Bytes steht
                # (eine Position automatisch nach Texteingabe, eine weitere für das Leerzeichen)
                newEvent = QKeyEvent(event.type(), QtCore.Qt.Key.Key_unknown, event.modifiers(), text)
                if self.textCursor().columnNumber() in (9, 12, 15, 18, 21, 24, 27, 31, 34, 37, 40, 43, 46, 49, 52):
                    myCursor.setPosition(self.textCursor().position() + 1)
                    self.setTextCursor(myCursor)
                # steht der Cursor zwischen den beiden 8-Byte-Blöcken, muss er um drei Positionen versetzt werden
                # (eine Position automatisch nach Texteingabe, zwei weitere für die Leerzeichen)
                elif self.textCursor().columnNumber() == 30:
                    myCursor.setPosition(self.textCursor().position() + 2)
                    self.setTextCursor(myCursor)

                super().keyPressEvent(newEvent)

            # Der Benutzer scrollt nach links
            if event.key() == QtCore.Qt.Key.Key_Left.value:
                # solange der Benutzer noch nicht am linken Rand angekommen ist...
                if (self.textCursor().columnNumber() > 7):  
                    myCursor.setPosition(self.textCursor().position() - 1) 
                    self.setTextCursor(myCursor)
                # ... falls er am linken Rand angekommen ist, wird überprüft,
                # ob er in der obersten Zeile ist. Falls nein, den Cursor nach rechts setzen
                # und eine Zeile hoch gehen
                elif self.textCursor().columnNumber() == 7 and \
                self.textCursor().blockNumber() > 0 :
                    myCursor.setPosition(54 + (self.textCursor().blockNumber()-1)*75)
                    self.setTextCursor(myCursor)

            # Der Benutzer scrollt nach rechts
            if event.key() == QtCore.Qt.Key.Key_Right.value:
                # solange der Benutzer noch nicht am rechten Rand angekommen ist...
                if (self.textCursor().columnNumber() < 54):  
                    myCursor.setPosition(self.textCursor().position() + 1) 
                    self.setTextCursor(myCursor)
                # ... falls er am rechten Rand angekommen ist, wird überprüft,
                # ob er in der untersten Zeile ist. Falls nein, den Cursor nach rechts setzen
                # und eine Zeile runter gehen
                elif self.textCursor().columnNumber() == 54 and \
                self.textCursor().blockNumber() < self.document().lineCount()-1:
                    myCursor.setPosition(7 + (self.textCursor().blockNumber()+1)*75)
                    self.setTextCursor(myCursor)

            # Die PFeiltasten hoch und runter bleiben, wie sie sind
            if event.key() == QtCore.Qt.Key.Key_Up.value:
                super().keyPressEvent(event)
            if event.key() == QtCore.Qt.Key.Key_Down.value:
                super().keyPressEvent(event)
                


    #
    # def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
    #
    # Der Benutzer klickt mit der Maus in das Editierfeld
    #

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        cursor = self.cursorForPosition(event.pos())

        # Klickt der Benutzer in den Adressbereich oder den Ascii-Bereich, 
        # wird er auf die Editierfläche beschränkt
        columnNumber = cursor.positionInBlock()
        if columnNumber < 7:
            columnNumber = 7
        if columnNumber > 54:
            columnNumber = 54

        # Fall er auf die Leerstellen zwischen den Bytes klickt (linke Spalte)
        # wird der Cursor auf das nächstgelegene Byte gesetzt
        if columnNumber >= 7 and columnNumber <= 30:
            columnNumber -= 7
            columnNumber = (columnNumber // 3) * 3
            columnNumber += 7

        # Fall er auf die Leerstellen zwischen den Bytes klickt (rechte Spalte)
        # wird der Cursor auf das nächstgelegene Byte gesetzt
        if columnNumber >= 32 and columnNumber <= 54:
            columnNumber -= 32
            columnNumber = (columnNumber // 3) * 3
            columnNumber += 32

        # und nun den Cursor "wirklich setzen"
        block = cursor.block()

        cursor.setPosition(block.position() + columnNumber)
        self.setTextCursor(cursor)
