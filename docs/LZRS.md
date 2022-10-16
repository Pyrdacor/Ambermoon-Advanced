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

If there are more than 3 bytes following a match/RLE, first the amount of literals given in the match header are read (in general the value should be 3). Only then the next literal header follows and then the other literals.

Example:

`E0 00 0C 00 01 02 03 E0 04`

The first by is a literal header with amount 1.
Then the literal `00` follows.
The 3rd byte starts a match header.
The match has length 3 and offset 1, so the output is `00 00 00 00` afterwards.
The match header states that 3 literals follow, which are then `01 02 03`.
And then another literal header with amount 1 follows.
The last byte is then this literal.

The total output is `00 00 00 00 01 02 03 04`


## Data start

Compressed data can never start with a match as there are no literals to provide a back reference.

As the data always starts with literals, the first header is a special one. It is just a single byte giving the amount of literals directly.
The value range is 0..255. As 0 literals doesn't make sense, a value of 0 means 256 and another byte is read and added to that value.
You can add more bytes if the value is at the maximum (255). This can be repeated unlimited.

This saves a byte if the sequence starts with more literals than the normal literal header could express 
