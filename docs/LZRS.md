LZRS is a LZ77 variant designed mainly for the Ambermoon Advanced project to achieve better compression and therefore save some KB in contrast to the used LOB compression.

As usual it encodes matches as offset/length pairs or just stores literals.

The focus lies on very compact encodings. Therefore short matches up to a length of 15, will be encoded as 2 bytes only.

To differentiate between literals and matches, a header byte is used. For literals it stores the amount of literals to follow. For matches it contains part of the length and offset.


## Literals

**Header** (binary): `111NNNNN`

The lower 5 bits give the number of literals that follow. The value range is 0..31. This is mapped to 1..32 by adding 1.
If the amount is 32, another byte is read and its value is added. A byte has a value range of 0..255. If this byte has also the max value of 255, another byte is read and added, and so on.
There is no limit in theory. If all the data is not compressible, it will increase by at max 0.4% due to this design.

Note that the next byte must be always read if the previous byte was at maximum, even if its value is 0.


## Matches

**Header** (binary): `LLLLNNOO OOOOOOOO`

The first (upper) 4 bits `LLLL` give the match length. Note that the header for the literals occupies all values starting with three 1-bits,
so the length value here can only be in the binary range 0000 to 1101, which is 0 to 13.
The length is mapped to the real lengths 3 to 16 by adding 3.

Like for literals the amount (here length) can be extended by adding bytes if the value is at maximum. So if the mapped length value is 16, another byte is read and added and so on.
Match lengths can be unlimited in theory as well.
For real matches this should be limited so that the compression process won't take too long.
But matches can also be used to express RLE, where long match lengths are desired and should not be limited 

The offset is given by the lower 10 bits `OOOOOOOOOO`. The value range 0 to 1023 is increased by 1 to the range 1 to 1024.
So the max match offset is limited to 1024, which is ok for data of only some KB.

The two `NN` bits give an optional number of following literals (0 to 3).
This is helpful when there are only a few bytes between matches or RLE sequences. You won't need another literal encoding which would add another additional byte to the data.
