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

Apple "Bell" Subroutine: Inside your monitor ROM there is a subroutine at $FBE2 which uses the speaker to make a bell-like sound. Here is a copy of that code. Notice that the pulse width is controlled by calling another monitor subroutine, WAIT.

```bash
     1000  *---------------------------------
     1010  *      APPLE "BELL" ROUTINE
     1020  *---------------------------------
     1030         .OR $FBE2    IN MONITOR ROM
     1040         .TA $800
     1050  *---------------------------------
     1060  WAIT       .EQ $FCA8    MONITOR DELAY ROUTINE
     1070  SPEAKER    .EQ $C030
     1080  *---------------------------------
     1090  M.FBE2 LDY #192     # OF HALF-CYCLES
     1100  BELL2  LDA #12      SET UP DELAY OF 500 MICROSECONDS
     1110         JSR WAIT     FOR A HALF CYCLE OF 1000 HERTZ
     1120         LDA SPEAKER  TOGGLE SPEAKER
     1130         DEY          COUNT THE HALF CYCLE
     1140         BNE BELL2    NOT FINISHED
     1150         RTS
```

Another source of wisdom consulted concerning the speaker is https://ia600304.us.archive.org/9/items/AssemblyLinesCompleteWagner/AssemblyLinesCompleteWagner.pdf.
This PDF is s made available under a Creative Commons Attribution-NonCommercial-ShareAlike 2.0 license. You
are free to share and adapt the material in any medium or format under the following terms: (1) Attribution–You
must give appropriate credit, provide a link to the license, and indicate if changes were made; (2) NonCommercial
–You may not use the material for commercial purposes; (3) ShareAlike–If you remix, transform, or build upon
the material, you must distribute your contributions under the same license as the original. For the complete
license see http://creativecommons.org/licenses/by-nc-sa/2.0/. Interesting here is chapter 8 "sound generation":

"Sound generation in assembly language is such a large topic in itself that an entire book could be done on that subject alone. However, simple routines are so easy that they’re worth at least a brief examination here. These routines will not only allow you to put the commands you’ve learned to further use, but are also just plain fun.
The first element of a sound-generating routine is the speaker itself. Recall that the speaker is part of the memory range from $C000 to $C0FF that is devoted entirely to hardware items of the Apple II. In earlier programs, we looked at the keyboard by examining memory location $C000. The speaker can be similarly accessed by looking at location $C030. The exception here is that the value at $C000 (the keyboard) varied according to what key was pressed, whereas with $C030 (the speaker) there is no logical value returned.
Every time location $C030 is accessed, the speaker will click once. This is easy to demonstrate. Simply enter the Monitor with a 'CALL-151'. Enter 'C030' and
press <RETURN>. You’ll have to listen carefully, and you may have to try it several times. Each time, the speaker will click once. You can imagine that, if we could repeatedly access the speaker at a fast enough rate, the series of clicks would become a steady tone. In BASIC this can be done, although poorly, by a simple loop such as this:

```bash
     10 X = PEEK(-16336): GOTO 10
```
The pitch of the tone generated depends on the rate at which the speaker is accessed. Because Integer BASIC is faster in its execution than Applesoft, the
tone generated will be noticeably higher in pitch in the Integer version. In assembly language, the program would look like this:
     
```bash     
     0300- AD 30 C0 LDA $C030
     0303- 4C 00 03 JMP $0300
```

In this case I’m showing it as the Apple would directly disassemble it, as opposed to the usual assembly-language source listing. ⇢e program is so short
that the easiest way to enter it is by typing in the hex code directly. To do this, enter the Monitor (CALL-151) and type:

```bash
     300: AD 30 C0 4C 00 03
```

Then run the program by typing '300G'. Disappointed? Thee program is working. Thee problem is that the routine is actually too fast for the speaker to respond. What’s lacking here is some way of controlling the rate of execution of the loop. This is usually accomplished by putting a delay of some kind in the loop. We should also be able to specify the length of the delay, either before the program is run or, even better, during the execution of the program.
     
We can do this in any of three ways: (1) physically alter the length of the program to increase the execution time of each pass through the loop; (2) store a
value somewhere in memory before running the program and then use that value in a delay loop; or (3) get the delay value on a continual basis from the outside world, such as from the keyboard or paddles. For the first method, you can use a new and admittedly complex command. The mnemonic for this instruction is NOP and stands for No OPeration. Whenever the 6502 microprocessor encounters this, it just continues to the next instruction without doing anything. ⇢is code is used for just what we need here – a time delay.
It is more often used, though, as either a temporary filler when assembling a block of code (such as for later data tables) or to cancel out existing operations in a previously written section of code. Quite often, this command ($EA, or 234 in decimal) is used in this manner to patch parts of the Apple DOS to cancel out various features that you no longer want to have active (such as the NOTDIRECT command error that prevents you from doing aGOTO directly to a line that has a DOS command on it).
In our sound routine, a NOP will take a certain amount of time even to pass over and will thus reduce the number of cycles per second of the tone frequency.
The main problem in writing the new version will be determining the number of NOPs that will have to be inserted. The easiest way to get a large block of memory cleared to a speciFc value is to use the move routine already present in the Monitor. To clear the block, load the first memory location in the range to be cleared with the desired value. Then type in themove command, moving everything from the beginning of the range to the end up one byte. For instance, to clear the range from $300 to $3A0 and fill it with $EAs, you would, from the Monitor of course, type in:

```bash     
     300: EA
     301<300.3A0M
```

Note that we are clearing everything from $300 to$3A0 to contain the value $EA. Now type in:

```bash
     300: AD 30 C0
     3A0: 4C 00 03
```
      
Then type in 300L, followed with L for each additional list section, to view your new program.
                  
```bash                  
     *300L
     0300- AD 30 C0 LDA $C030
     0303- EA NOP
     0304- EA NOP
     0305- EA NOP
     0306- EA NOP
     0307- EA NOP
     0308- EA NOP
     0309- EA NOP
     * * *
     * * *
     * * *
     0395- EA NOP
     0396- EA NOP
     0397- EA NOP
     0398- EA NOP
     0399- EA NOP
     039A- EA NOP
     039B- EA NOP
     039C- EA NOP
     039D- EA NOP
     039E- EA NOP
     039F- EA NOP
     03A0- 4C 00 03 JMP $0300
```
                  
Now run this with the usual 300G. The tone produced should be a very nice, pure tone. The pitch of the tone can be controlled by moving theJMP$300 to points of varying distance from the LDA $C030. Granted, this is a very clumsy way of controlling the pitch and is rather permanent once created, but it does illustrate the basic principle.
For a different tone, hit RESET to stop the program, then type in:

```bash                  
     350: 4C 00 03
```
        
When this is run (300G), the tone will be noticeably higher. The delay time is about half of what it was, and thus the frequency is twice the original value. Try typing in the three bytes in separate runs at $320 and $310. At $310 you may not be able to hear the tone, because the pitch is now essentially in the ultrasonic range.

## Sound generation in python
As we have already learned, the basic idea of speaker toggling is based on a square wave form. So, let's learn how to create a square wave in python and what it actually looks like. 

### Square Wave
Let's see what [Wikipedia](https://en.wikipedia.org/wiki/Square_wave) knows about a square wave:
"A square wave is a non-sinusoidal periodic waveform in which the amplitude alternates at a steady frequency between fixed minimum and maximum values, with the same duration at minimum and maximum. In an ideal square wave, the transitions between minimum and maximum are instantaneous.

The square wave is a special case of a pulse wave which allows arbitrary durations at minimum and maximum amplitudes. The ratio of the high period to the total period of a pulse wave is called the duty cycle. A true square wave has a 50% duty cycle (equal high and low periods).

Square waves are often encountered in electronics and signal processing, particularly digital electronics and digital signal processing. Its stochastic counterpart is a two-state trajectory.

Square waves are universally encountered in digital switching circuits and are naturally generated by binary (two-level) logic devices. Square waves are typically generated by metal–oxide–semiconductor field-effect transistor (MOSFET) devices due to their rapid on–off electronic switching behavior, in contrast to bipolar junction transistors (BJTs) which slowly generate signals more closely resembling sine waves rather than square waves.[1]

Square waves are used as timing references or "clock signals", because their fast transitions are suitable for triggering synchronous logic circuits at precisely determined intervals. However, as the frequency-domain graph shows, square waves contain a wide range of harmonics; these can generate electromagnetic radiation or pulses of current that interfere with other nearby circuits, causing noise or errors. To avoid this problem in very sensitive circuits such as precision analog-to-digital converters, sine waves are used instead of square waves as timing references.

In musical terms, they are often described as sounding hollow, and are therefore used as the basis for wind instrument sounds created using subtractive synthesis. Additionally, the distortion effect used on electric guitars clips the outermost regions of the waveform, causing it to increasingly resemble a square wave as more distortion is applied."