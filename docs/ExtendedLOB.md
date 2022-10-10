# Extended LOB

To save more space for the new content, I added a new LOB compression method.

The LOB method in Ambermoon is type 06. The type is given in the highest byte of the 4 byte header which follows the magic string "1LOB".
This new LOB method uses byte FF (type 255). This way files can use any of the available LOB methods, so the original one is still available.
Moreover we can just use the existing container formats like AMNP without change and use any LOB method (old or new) for any sub-file.

For the original LOB, see here: https://github.com/Pyrdacor/Ambermoon/blob/master/Files/LOB.md.

This extended LOB should perform well on data like maps, characters, items, savegames and similar data. For text containers better use
the new [text LOB compression](TextLOB.md).


# Compression

The general approach is to find sequences of equal bytes and replace them with a run-length encoding (RLE) or find the current byte sequence somewhere else in the earlier data and replace the data by a back reference, also called a match (offset to the source data and length of the match). A run-length encoding just stores which byte to repeat and how often to repeat it. For example the sequence `00 00 00 00` can theoretically be expressed as `00 04`, where the first byte gives the byte to repeat and the second byte gives the amount. We will tweak this a little bit to encode a bit better but this is the general idea of RLE.

In constrast to the original LOB, instead of a header byte where each bit specifies if a literal or match follows, each header byte directly encodes some byte sequence.

As each header byte can have a value from 0 to 255, the following value ranges encode specific things.

So to process compressed data, read a byte from the encoded data stream, decode its meaning, read more bytes as needed and proceed with the next header byte. Keep going until the whole data is decompressed.


## 0: Encodes a run-length encoding (RLE) of zeros

### Compression

If a sequence of 3 or more zeros in a row is found, each chunk of 3 to 258 zeros is encoded as 2 bytes. The first byte is a zero, the second byte gives the amount minus 3.

- For example 10 zeros are encoded as those hex bytes: `00 07`.
- 3 zeros would be: `00 00`.
- And 300 zeros would be: `00 FF 00 27`.

The last case encodes 2 RLE sequences. The first two bytes encode 258 zeros. So 42 zeros remain. The second byte pair encodes those 42 zeros. Note the amount minus 3 is stored which is 39 (hex 27).

**Important**: There are cases where the last chunk has less than 3 zeros! For example you can't encode 260 bytes only with this RLE. The first 258 zeros are ok but then only 2 zeros remain. Those can't be encoded as an additional RLE! They have to be written as normal literals instead!

### Decompression

Whenever the header byte is zero, the next byte is read, increased by 3 and this amount of zeros is written to the output.


## 1 to 127: Encodes a sequence of literals

### Compression

If no compression is possible, the literals (byte values) have to be written to the output as they are. Of course the decompressor must know if a data chunk is uncompressed. This is done by this header.
You can just write the number of uncompressed bytes (up to 127) as a single byte to the output and then write the bytes. For sequences longer than 127 you have to use multiple of such sections.

The worst case for compression are single uncompressed bytes, as they need 2 bytes in the output. There is a special encoding for byte values less than 32 to avoid this a bit.
See 'Small byte literal' encoding at the end of this page for more details. For bytes equal or above 32, this is not possible unfortunately. They will cause the worst case.

The literal sequence encoding won't save space but will even add an additional byte to the output. These additional bytes should be compensated by other compression encodings. For large sections which can't be compressed,
this additional byte only becomes a small fraction of the section size. The smaller the size though, the more the byte matters. It is hard to determine how well the total compression will be as
it depends on the data. There might be cases where the extended LOB performs bad or even increases the size of the data. In that case use the raw data or another compression. In general it will
compress very well for its simplicity and will often out-perform the original LOB compression. Reading of encoded literal sequences should also be much faster as only 1 byte is decoded and then the
whole sequence can be read directly.

The original LOB also needs to store an additional header bit for each literal. For a sequence of 8 literals, it stores 8 additional bits or 1 additional byte. This means that literals sequences of length 1 to 7 are better encoded with original LOB, sequences of length 8 are equally well encoded and longer sequences are better encoded by the extended LOB. For the worse cases, often the small literal encoding might help.

### Decompression

If the header byte is 1 to 127. Just read this amount of bytes.


## 128 to 159: Encodes a small match

In hex the header is 80 to 9F. You can check if the header starts with the bit sequence 100.

Small matches encode a pair of offset and length. The offset is limited to the range 1 to 512, and the length to the range 3 to 18. The encoding needs 2 bytes. You will save 1 to 16 bytes.

### Compression

If the current byte sequence of length 3 to 18 exists in the previous data at a max distance of 512, you can encode this as a small match. Note that the offset can be smaller than 3 and even down to 1! This can theoretically be used to encode recurring patterns. Think of some data like 01 02 01 02 01 02. At the 3rd position you could encode a match with offset 2 and length 4. Matches are processed byte per byte.
See the decompression example below.

The next byte is also used to store information for the match. Basically header plus additional byte encode the match as follows (big endian format): `100LLLLO OOOOOOOO`

`LLLL` is a 4-bit value for the match length. Possible values are 0 to 15, but it encodes the length 3 to 18 (so subtract 3 from the match length for encoding).
`OOOOOOOOO` is a 9-bit value for the match offset. The highest bit is stored inside the header byte as bit 0! Possible values are 0 to 511, but it encodes offsets 1 to 512 (substract 1 for encoding).

### Decompression

If the header is of the bit form 100XXXXX, it is a small match. See the compression to know how offset and length are encoded. Don't forget to add 3 to the read match length as it is stored as 0 to 15 instead of 3 to 18. And add 1 to the read offset value.

If you decoded the match offset and length, you can process the match by reading from the current position minus the given offset.

Match processing:

Step | Data | Description
--- | --- | ---
Before | 01 02 | Data before match processing
1st | 01 02 01 | Copy from offset 2 (= current position minus 2)
2nd | 01 02 01 02 | Copy from current position minus 2
3rd | 01 02 01 02 01 | Copy again
4th | 01 02 01 02 01 02 | Copy again


## 160 to 191: Encodes a large match

In hex the header is A0 to BF. You can check if the header starts with the bit sequence 101.

Large matches are similar to small matches but with different value ranges for offset and length. Offsets can be 1 to 1024 and lengths 3 to 130. The encoding needs 2.5 bytes. You will save 0.5 to 127.5 bytes.
In worst case (last large match is a even one and length is 3), you don't save any space. But this happens at max once per data.

Note that you can express some matches as either small or large matches. Always prefer encoding them as small ones if possible.

The original LOB can handle greater offsets up to 4095 but is very limited when it comes to match lengths. Only lengths up to 18 are possible. I guess it was used as it performs good enough for data, images and texts. However for most non-text data, long matches and even long RLE sequences are quite common. Of course they perform very bad on text data. This is why I invented two different LOB methods for text and non-text data.

### Compression

For basic information see small matches. Here only the bit encoding is shown.

There are 2 possible encodings. If this is the first large match, the match is encoded as `101LLLLL LLOOOOOO OOOORRRR`. Here L and O represent bits for the match length and offset as for the small match.
Special are the R bits. As only 20 bits of the 24 bits are needed, we use the remaining 4 bits for the next large match. So when the second match is encoded it will be only `101LLLLL LLOOOOOO`.
Here the O bits only give the upper 6 bits of the 10 bit offset value. The other 4 bits must be stored in the reserve bits R of the previous match.

For compressors this means that parts of every second large match have to be added somewhere in the previous output stream.

Example:

Given the source data stream `01 02 .. 64 01 02 .. 64 01 02 .. 64` the output could be encoded with two large matches as : `01 02 .. 64 B8 46 33 B8 46`. Note that the source data consists of 3 sequences of
the hex values for 1 to 100!

The first large match begins with `B8`. The 5 bytes `B8 46 33 B8 46` represented in bits are:

`10111000 01000110 00110011 10111000 01000110`

The first 20 bits encode the first large match: `10111000 01000110 0011`. This is the header for large matches `101`, followed by the encoded match length `1100001` which is 97 (add 3 for 100). Then the
match offset follows as `0001100011` which is 99. Add 1 to get 100. So the match has offset 100 and length 100.

The next 4 bits are the reserve for the next large match. For encoding you could add it as the lower 4 bits of the encoded data stream. When decompressing you would normally store those 4 bits somewhere
for later use. Here the reserve is `0011`.

Then the second large match encoding follows with `10111000 01000110`. Note that there might be other bytes or encodings in-between in other cases.

When decompressing you would basically concat the reserve bits to those 16 bits to have the full 20 bits: `10111000 01000110 0011`. This again encodes a match with offset 100 and length 100.

Use a toggle variable to determine if it's time to write a new additional byte or add the last 4 bits to an already written byte.

With the reserve bits feature, it is possible to encode large matches effectively with 2.5 bytes instead of 3 bytes.

### Decompression

Most of it is covered in the decompression section for small matches and in the compression section for large matches. The only tricky thing is to determine where the last 4 bits for the match offset
come from. In general it's good to use a toggle variable to determine if you have to read an additional byte and take those bits from there or use the bits from a previously read reserve.

In general when processing the nth large match, if n is even (0, 2, 4, etc), read an additional byte, take the upper 4 bits for the offset and store the lower 4 bits as reserve.
If n is odd (1, 3, 5, etc), just take the 4 bits from the reserve.


## 192 to 223: Encodes a non-zero RLE

In hex the header is C0 to DF. You can check if the header starts with the bit sequence 110. You can save 1 to 32 bytes with this.

### Compression

If there is a sequence of equal bytes which has a length greater or equal 3, you can use this encoding. Basically it works like the zero RLE but with other byte values.

The amount here is limited to 34 though where the zero RLE allows up to 258. In theory you could also encode zero RLEs with this but it's not recommended.

The bit encoding of the header is: `110LLLLL`. Here the L bits give a length value of 0 to 31, which represents a length of 3 to 34 (so subtract 3 for encoding or add 3 for decoding).

The following byte gives the byte to repeat.

### Decompression

If the header starts with the bits `110`, read the next 5 bits as a length, increase it by 3 and write the following byte to the output n times, where n is the given length.


## 224 to 255: Small byte literal

In hex the header is E0 to FF. You can check if the header starts with the bit sequence 111. You won't save space directly but avoid a worst case scenario or adding an additional byte for sequences.

As mentioned above, the worst case scenario for compression is a single uncompressed byte. To reduce the cost of this a bit, single bytes with values below 32 can be encoded
with just a single byte. The encoding is `111XXXXX` where the X bits directly specify the byte value.

For example consider the following source data `00 00 00 05 00 00 00 06` which is very common. The sequences of zero can be run-length-encoded but then you have the single
byte `05` in-between. Normally you would have to encode this byte as the two-byte encoding `01 05`. But with this special encoding you can just encoded it as `E5`.

Another benefit is that you save a byte for sequences of small bytes. Consider the source data `01 02 03 04 05`. Normally you would encode a sequence of uncompressed
bytes as `05 01 02 03 04 05`. The first byte is the header byte which gives the amount of uncompressed literals. Instead you can also just use `E1 E2 E3 E4 E5` here.

This saves a byte as every single byte is basically a header byte with some encoding. But note that this approach might be slower as you have to decode every byte instead
of just copy the sequence after decoding one header. This is especially true if the sequence is very long. In that case the single saved byte isn't that important anymore
so it's preferred to use the normal literal sequence with the 1-byte header instead. For short sequences, the 1 additional byte matters and should be avoided.
