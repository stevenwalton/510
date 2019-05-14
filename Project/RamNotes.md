000E00: Coins (Hex Val 1-byte)
000104: Time - Minute 
000102: Time - Second
000101: Time - Milisecond

0010C1: Lap (133=lap 5/finish) (subtract 128 from this number to determine lap)
001040: Rank (divide by 2 and add 1 to determine rank)
000148: Lap size (length of track)
0010DC: Checkpoint. Shows distance from start of track (increments up to Lap size - 1. Eg if Lap Size = 36, Checkpoint = N%37)

Seems like place doesn't show when it is updated on the screen. Frame of update is different than frame of screen update.
- First place does not equal 1. 8th place doesn't equal 8
