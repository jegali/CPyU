# The Speaker
The implementation of the speaker was a real challenge for me. How do you bind hardware to an emulator? How is this hardware to be described and modeled? These were all questions that go far beyond "I'll build a method that loads the accumulator".

## How the speaker works
First I tried Winston Gayler's book. Chapter 7 contained the following about the speaker:

"Tones are produced in the speaker of the Apple by toggling flip-flop J13-5 under program control. Transistor Q4 amplifies the output of J13-5 to drive the speaker [...] Decoder F13-12 goes low during phi whenever the range $C030-$C03F is addressed. On the rising edge of F13-12, J13-5 is clocked. This flip-flop will toggle since pin 6 is tied to pin 2. It takes two accesses to $C030 to generate one period of speaker oscillation. The square or rectangular wave at J13-5 is coupled through C1l and R24 to the base of Q4. Diode CRl provides a discharge path for C11. Thansistor Q4 is a Darlington pair that amplifies the signal to drive the speaker through R25. Capacitor C12 provides some integration and also absorbs some of the energy stored in the speaker winding when Q4 turns off.
Tb generate tones from the speaker, you must calculate the number of clock cycles needed between each toggle. The clock cycles are then obtained using a
software loop. Using this method, you can generate tones from below to above the audible range. If you want absolute pitch, remember that the average clock cycle is 980 nS long. Fig. 7-9 shows the voltage (to ground) measured at the internal speaker for I002-Hz and 10.4-kHz tones. Note the overshoot at each transition. You can get a much fuller sound by disconnecting the small internal speaker and connecting a larger external speaker. Be careful with the speaker leads; one side is connected directly to *5 volts."

This information confused me more than it helped me. Something with address $C030, I made a note of that. So I tried Jim Sather's book and read chapter 7:

"Now there is no 'Control Address Bus' command in the 6502's repertoire. The 6502 reads from or writes to the data bus every cycle. So what does the programmer do when he wants to toggle the speaker? He does a 'LDA $C030' or a 'CPX $C030' or a 'WHO GIVES A DARN $C030' and ignores the meaningless data bus. This is why you can program the speaker with a statement like 'SOUND=PEEK(-16336)'. The object is not to 'PEEK' into memory. The object is to get $C030 on the address bus, commanding the speaker to toggle"

## Making noise and other sounds
Ok, so now we know how the speaker is addressed. Now let's take care of generating tones or understanding the tone generation at all. Fortunately I found an article by Bob Sander-Cederlof in the Apple Assembly Line (https://textfiles.meulie.net/aal/1981/aal8102.html), which I would like to reproduce here in parts: 

"The Apple's built-in speaker is one of its most delightful features. To be sure, it is very limited; but I have used it for everything from sound effects in games to music in six parts (weird-sounding guitar chords) and even speech. Too many ways to put all in one AAL article! I will describe some of the sound effects I have used, and maybe you can go on from there.

The speaker hardware is very simple. A flip-flop controls the current through the speaker coil. Everytime you address $C030, the flip-flop changes state. This in turn reverses the current through the speaker coil. If the speaker cone was pulled in, it pops out; if it was out, it pulls in. If we "toggle" the state at just the right rate, we can make a square-wave sound. By changing the time between reversals dynamically, we can make very complex sounds. We have no control over the amplitude of the speaker motions, only the frequency.

Simple Tone: This program generates a tone burst of 128 cycles (or 256 half-cycles, or 256 pulses), with each half-cycle being 1288 Apple clocks. Just to make it easy, let's call Apple's clock 1MHz. It is really a little faster, but that will be close enough. So the tone will be about 388 Hertz (cycles per second, if you are as old as me!).

How did I figure out those numbers? To get the time for a half-cycle (which I am going to start calling a pulse), I added up the Apple 6502 cycles for each instruction in the loop. LDA SPEAKER takes 4 cycles. DEX is 2 cycles, and BNE is 3 cycles when it branches. The DEX-BNE pair will be executed 256 times for each pulse, but the last time BNE does not branch; BNE only takes 2 cycles when it does not branch. The DEY-BNE pair will branch during each pulse, so we use 5 cycles there. So the total is 4+256*5-1+5=1288 cycles. I got the frequency by the formula f=1/T; T is the time for a whole cycle, or 2576 microseconds."

```bash
     1000  *---------------------------------
     1010  *      SIMPLE TONE
     1020  *---------------------------------
     1030  SPEAKER    .EQ $C030
     1040  *---------------------------------
     1050  TONE   LDY #0       START CYCLE COUNTER
     1060         LDX #0       START DELAY COUNTER
     1070  .1     LDA SPEAKER  TOGGLE SPEAKER
     1080  .2     DEX          DELAY LOOP
     1090         BNE .2
     1100         DEY          QUIT AFTER 128 CYCLES
     1110         BNE .1
     1120         RTS
```
