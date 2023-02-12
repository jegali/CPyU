# Keyboard
The keyboard was the easiest I/O component to implement. Unfortunately, it didn't make sense without a screen output - 
that's why I'm only going into the keyboard now.

## how does the keyboard work
Oh, actually quite simple. When the user presses a key, the byte value of that key is put on the address bus - 
at address 0xC000. There the value stays until it is deleted again. Usually this happens when you write something to 0xC001.
