LZRS is a LZ77 variant designed mainly for the Ambermoon Advanced project to achieve better compression and therefore save some KB in contrast to the used LOB compression.

As usual it encodes matches as offset/length pairs or just stores literals.

The focus lies on very compact encodings. Therefore short matches up to a length of 15, will be encoded as 2 bytes only.

To differentiate between literals and matches, a header byte is used. For literals it stores the amount of literals to follow. For matches it contains part of the length and offset.


## Literals

**Header** (binary): `111NNNNN`

The lower 5 bits give the number of literals that follow. The value range is 0..31. This is mapped to 1..32 by adding 1.
If the amount is 32, another byte is read after those 32 literals and this amount of literals also follow. A byte has a value range of 0..255. If this byte has also the max value of 255, another byte is read and added after the literals, and so on.
There is no limit in theory. If all the data is not compressible, it will increase by at max 0.4% due to this design.

Note that the next byte must be always read if the previous byte was at maximum, even if its value is 0.

Example:

`1F 00 .. 1F FF 00 .. FF 01 20`

The first byte is 31, so 32 literals follow: `00` to `1F`. And then another byte is read as the value was 31. This byte has value 255, so this amount of literals follow: `00` to `FF`. And another byte is read as the value was 255. Now the byte has a value of 1. So only a single byte follows: `20`. And no more literals follow.


## Matches

**Header** (binary): `LLLLNNOO OOOOOOOO`

The first (upper) 4 bits `LLLL` give the match length. Note that the header for the literals occupies all values starting with three 1-bits,
so the length value here can only be in the binary range 0000 to 1101, which is 0 to 13.
The length is mapped to the real lengths 3 to 16 by adding 3.

Like for literals the amount (here length) can be extended by adding bytes if the value is at maximum. So if the mapped length value is 16, another byte is read and added and so on.
Note that the additional length bytes all directly follow the second header byte. Match lengths can be unlimited in theory as well.

For example a match of length 300 would be expressed as `Fx xx FF 1D` where xxx depends on the offset and following literal count.
The first nibble `F` stands for the amount of 16. As it is at max, the third byte `FF` is another length byte. It adds 255. As it is also at max, another byte is used. This time `1D` which is 29. 16 + 255 + 29 = 300.

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

As the data always starts with literals, the first header is a special one. It is just a single byte giving the amount of literals directly. The value range is 0..255. As 0 literals doesn't make sense, a value of 0 means 256 and another byte is read and processed after those 256 literals. Similar to other literal encodings, this can be continued with bytes of value 255.

This saves a byte if the sequence starts with more literals than the normal literal header could express, which is 32. But even 32 would require an additional length byte so a byte is saved if the initial length of uncompressable literals is 32 or greater.

If the first 500 bytes are uncompressable literals the data would start with `00 literals F4 more literals`. The zero byte stands for 256 and more bytes. After 256 literal bytes, the byte `F4` stands for 244 additional literals. Then they follow.


### Additional length encoding

One might ask why the bytes for additional lengths are not right after each other. It would be better readable this way. A program could just read all length bytes and then copy all literals at once.

The reason is, that the decompressor can process chunks of literals easier and with lower resources. It just needs to memorize if another chunk follows, read the amount of one chunk of literals and copy them.

This will also work when the total amount of literals exceed large values like 65535 (max word value). For example a decompressor can always use a byte or word to store the amount per chunk. This is useful for the Amiga and similar systems. You don't need to worry about integer range exceeding even if the total amount is very large.

In theory the same is true for matches, but as there no literals are needed, the length bytes follow each other directly. You may still want to use code which writes chunks of the match with a max length of 255 and repeat the process until all chunks are processed.
