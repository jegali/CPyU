# Clipboard and copy/paste
Typing in the same program over and over again is quite exhausting. Especially if you do no have a possibility of saving your sources at hand - without cassette or Floppy Disk. So I decided to implement a copy/paste functionality to be able to copy source code from a Windows/Max/Linux editor to the Applesoft BASIC prompt.

## how does the Paste-function work
It is very convenient that the Apple polls the softswitch 0xC000 constantly. I found this out when I implemented an output in the method read_byte / read_bus when and how often the bus is polled. 0xC000 is actually constantly in operation. That was reason enough to think about using this polling actively by flooding the keyboard strobe with information. So I implemented a small routine that puts a letter on the line ten times in the main loop when CTRL is pressed. And, what can I say: this worked wonderfully.
