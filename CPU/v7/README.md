# More Graphics enhancements
This version is all about some polishing and enhancements, mainly on the graphics / display module

## Flash
Ah-ah<br/>
He's a miracle<br/>
(Queen, Flash Gordon)<br/>

What is a display without a blinking cursor - or without a cursor at all? The user can't see "where he is" and it looks bad too. Therefore, in this section, we will take care of character blinking. [Wikipedia](https://en.wikipedia.org/wiki/Apple_II_character_set) is helpful here:

"The original Signetics 2513 character generator chip has 64 glyphs for upper case, numbers, symbols, and punctuation characters. Each 5x7 pixel bitmap matrix is displayed in a 7x8 character cell on the text screen. The 64 characters can be displayed in INVERSE in the range $00 to $3F, FLASHing in the range $40 to $7F, and NORMAL mode in the range $80 to $FF. Normal mode characters are repeated in the $80 to $FF range."

So we have an alphabet of 64 characters that is repeated four times in memory. Sounds like a bit manipulation task. We can use the divmod() function here - as well as when calculating the memory address on the display. Here is a small source code snippet:

```bash
value = 0x82
mode, ch = divmod(value, 0x40)
print ("mode", mode)
print ("ch", ch)
```

And some sample runs of the program:

```bash
value = 0x82
mode: 2
ch: 2

value = 0x42
mode: 1
ch: 2

value = 0x02
mode: 0
ch: 2
```
