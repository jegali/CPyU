# The Speaker
The implementation of the speaker was a real challenge for me. How do you bind hardware to an emulator? How is this hardware to be described and modeled? These were all questions that go far beyond "I'll build a method that loads the accumulator".

## How the speaker works
First I tried Winston Gayler's book. Chapter 7 contained the following about the speaker:

"Tones are produced in the speaker of the Apple by toggling flip-flop J13-5 under program control. Transistor Q4 amplifies the output of J13-5 to drive the speaker [...] Decoder F13-12 goes low during phi whenever the range $C030-$C03F is addressed. On the rising edge of F13-12, J13-5 is clocked. This flip-flop will toggle since pin 6 is tied to pin 2. It takes two accesses to $C030 to generate one period of speaker oscillation. The square or rectangular wave at J13-5 is coupled through C1l and R24 to the base of Q4. Diode CRl provides a discharge path for C11. Thansistor Q4 is a Darlington pair that amplifies the signal to drive the speaker through R25. Capacitor C12 provides some integration and also absorbs some of the energy stored in the speaker winding when Q4 turns off.
Tb generate tones from the speaker, you must calculate the number of clock cycles needed between each toggle. The clock cycles are then obtained using a
software loop. Using this method, you can generate tones from below to above the audible range. If you want absolute pitch, remember that the average clock cycle is 980 nS long. Fig. 7-9 shows the voltage (to ground) measured at the internal speaker for I002-Hz and 10.4-kHz tones. Note the overshoot at each transition. You can get a much fuller sound by disconnecting the small internal speaker and connecting a larger external speaker. Be careful with the speaker leads; one side is connected directly to *5 volts."

This information confused me more than it helped me. Something with address $C030, I made a note of that. So I tried Jim Sather's book:

"Now there is no 'Control Address Bus' command in the 6502's repertoire. The 6502 reads from or writes to the data bus every cycle. So what does the programmer do when he wants to toggle the speaker? He does a 'LDA $C030' or a 'CPX $C030' or a 'WHO GIVES A DARN $C030' and ignores the meaningless data bus. This is why you can program the speaker with a statement like 'SOUND=PEEK(-16336)'. The object is not to 'PEEK' into memory. The object is to get $C030 on the address bus, commanding the speaker to toggle"
