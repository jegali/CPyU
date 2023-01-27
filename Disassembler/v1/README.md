# UI design with QT Designer
This version represents the basic framework of the application. Using QT Designer, the graphical user interface was created and converted into executable Python source code by pyuic6.<br/><br/>

As already described, I have oriented myself to the disassembler masswerk (https://www.masswerk.at/6502/disassembler.html.) for the creation of the graphical user interface. 

![Disassembler_UI](/images/disassembler-ui.png)

The designer software saves the design as a file of type ui. This is a file in XML format that describes the interface elements. With the help of the pyuic program, this file can be translated into Python source code. I saved the UI design as "disassembler.ui". You will find this file in this directory. here is some of its content:

```bash
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>DisassemblerWindow</class>
 <widget class="QMainWindow" name="DisassemblerWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>810</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>6502 Disassembler</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QPlainTextEdit" name="txtEditCode">
    <property name="geometry">
     <rect>
      <x>20</x>
      <y>40</y>
      <width>361</width>
      <height>181</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <family>Courier New</family>
      <pointsize>11</pointsize>
     </font>
    </property>
    <property name="readOnly">
     <bool>true</bool>
    </property>
   </widget>
   <widget class="QPlainTextEdit" name="txtEditSymbol">
    <property name="geometry">
     <rect>
      <x>410</x>
      <y>40</y>
      <width>361</width>
      <height>181</height>
     </rect>
    </property>
   </widget>
   ...
```
