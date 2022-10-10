# Text LOB

To save more space for the new text content, I added a new LOB compression method.

The LOB method in Ambermoon is type 06. The type is given in the highest byte of the 4 byte header which follows the magic string "1LOB".
This new LOB method uses byte FE (type 254). This way files can use any of the available LOB methods, so the original one is still available.

For the original LOB, see here: https://github.com/Pyrdacor/Ambermoon/blob/master/Files/LOB.md.

The text LOB, as the name implies, was designed to compress text data well. For other data use the original LOB or the new [extended LOB](ExtendedLOB.md).

Texts tend to contain no sequences of equal bytes, so RLE makes no sense here. Moreover the texts in Ambermoon will never use non-printable characters
of the range 0 to 31. An exception is the terminating zero (code 0), which is used to separate texts. As we want to keep the possibility open to add
more languages later, we won't use character codes which are not used in english or german but might be used by other languages.

It would be best to pack all texts together and compress them, as this increases the chance of finding matches in other parts. But unfortunatly the
original only reads sub-files and decode them so we have no access to other text files or even text containers. But sub-files are mostly associated
to maps, characters and so on. Therefore at least some texts are packed together in a single sub-file. Still those sub-files only have a size of just
a few kilobytes. The largest sub-file is around 7KB, most are in the range 1 to 3 KB.

From those observations the focus lies on matches which allow reasonable offsets. Text matches are more likely to be short. Think of words like "AND"
or "THE" which are very common. Long matches like full sentences are very unlikely so match lengths can be short. Another factor is to encode the
matches with very few bits. It might be even benefical to encode matches of length 2, but then the match encoding must be lower than 2 bytes of course.

The basic idea is to use the invalid character codes 1 to 31 to express encodings. This way we need no additional header bytes and can output normal
characters without additional cost. So in a worst case scenario the compression will not exceed the original size! This is likely for very few short
texts!

As it makes encoding and decoding a bit easier, not the values 1 to 31 are used for the encoding but instead the values 0 to 30. The termination 0
(byte 0) is special encoded as 31 (hex 1F) instead.

So the basic encoding is:
- 0 to 30: Match
- 31: Zero byte (00)
- 32 and above: Byte as it is

In the following sections we will only look at the matches as the rest is obvious.


## Matches

As mentioned, match lengths can be rather short. In fact we use match lengths of 2 to 10 here only. To be able to save space for 2-byte matches
we encode this special match with only 1.5 bytes. 2-byte matches are use frequently but might use large offsets. Therefore it won't be useful
to encode 2-byte matches in a single byte as offsets would be very limited and therefore quite useless.


### 2-byte matches

You might think of texts "TO BE OR NOT TO BE" where you can encode the "TO" and the "BE" as a back reference. But for those cases often a 3-byte match is better which includes
the space as well (if possible). For example the second "TO " (with space) can be encoded. 2-byte matches are much more common: "THE FIRE BURNS QUITE HOT OVER THERE".
You won't expect much matches here but if you include the space you can see that the sequence "E " (with space) is used 3 times here. This is also true for parts of words. You can match "HO", "TH" or "ER" as well.

So in total we have a bunch of 2-byte matches here. Encoded as 1.5 bytes each, we can at least save some bytes, which is ok for a random short text. Consider many maps and characters with all their texts and we will
already save some kilobytes just with those 2-byte matches.

Of course with entropy encoding like Huffman we could compress this much better. But we want to use it on the Amiga with simple code and good performance!
There is always a tradeoff and I came up with this compression to allow a fast decompression which is good enough to save a few KBs in total.

#### Encoding

As mentioned we only consider values 0 to 30 for matches. In binary this is 00000000 to 00011110. So if any of the upper 3 bits is set, it is no match!

To state that it is a 2-byte match, the 4th bit (from left) is also 0. So for 2-byte matches the first byte is of the form 0000XXXX. In contrast 0001XXXX would start
a match of higher length.

As mentioned we use 1.5 bytes to encode such a match. To do so we either use 2 bytes or 1 byte. We alternate between reading 2 or 1 bytes, and every second 2-byte match will use a half
byte (4 bits) of the last 2-byte match. A similar thing is done in the [Extended LOB algorithm](ExtendedLOB.md). There for the large matches which use 2.5 bytes.
So have a look there to understand the process better.

For the nth 2-byte-match the following is done:
- If n is even (0, 2, 4, etc): Read 2 bytes, use the first byte and the upper 4 bits of the second. Store the lower 4 bits of byte 2 as a reserve.
- If n is odd (1, 3, 5, etc): Read 1 byte and append the previously read reserve bits.

So for each of those matches, 1.5 bytes (12 bits) are used in total.

For even matches it is `0000OOOO OOOORRRR`. The O bits give the offset value, the R bits are the reserve for the next 2-byte match.
For odd matches it is `0000OOOO`. Then `RRRR` from last match is append to form again `OOOORRRR` which gives the offset value.

As offset values consist of 8 bits, they can theoretically represent the values 0 to 255. But we interpret it as 3 to 258.
Offsets below 3 don't make much sense for text.

- An offset of 1 would represent a sequence of 3 additional bytes like "AAA" which is not common in text.
- An offset of 2 would represent a sequence of 2 equal bytes like "ABAB" which is also not very common in text.

It is more valuable to allow the offset to be as large as possible.

#### Decoding

When reading and a byte has a value between 0 and 15, it is a 2-byte match. Based on the reserve toggle state, read an additional byte or use the reserve bits.

Then extract the offset (don't forget to increase it by 3) and copy the match from the already decoded data to the end of it. The length is implicit here and is always 2 of course.


### Longer matches

If the 4th bit (from left) is set, it is a match of length 3 to 10. This is always encoded as 2 full bytes. So this will never influence the reserve bits or
toggle for the 2-byte matches! The encoding for longer matches is `0001OOOO OOOOOLLL`. So here we have 9 bits in total for the offset and 3 bits for the length.
As matches of length 2 are already handled, we interpret the length value (0 to 7) as 3 to 10.

The offset consists of 9 bits, therefore it can theoretically express the values 0 to 511. But as byte 31 is a special encoding for a zero byte, the first byte
can't be 31 (binary `00011111`). At max the first byte can be `00011110` in binary. Therefore our 9 bit offset value is limited to `111011111` which is 479.
Again offsets below 3 make not much sense, so we interpret the offset range as 3 to 482. The max offset for longer matches is therefore 482.

The process of encoding and decoding is the same. Only the match offset and length are stored differently. For 2-byte matches the length is implicit. Don't forget to adjust the offset and length values (add or remove 3).


### Initial bytes

Text sub-files start with some header bytes in general. For example bytes which specify the amount of texts or the text lengths. As they are part of the data,
they have to be encoded as well. But those values can be anything, including the values 1 to 31 which are forbidden otherwise. To enable the above encodings,
the header bytes can be skipped for compression. To accomplish this, the whole compressed data starts with a byte which gives the size of bytes which should
not be compressed. The amount is then just copied over and then decompression starts.

If you compress data with this, find the last byte which has a value between 1 and 31. Then store the amount (including this last byte) as the first byte of
the encoded data. A value of 0 is also valid. In that case decompression would directly start after reading this initial byte. Note that it is not possible
to compress data which has an invalid byte after the first 255 bytes. So the whole text LOB algorithm is not usable for most binary files or any file which
stores some non-text characters after a small header. However it should work well for the Ambermoon text container sub-files. It was designed for those files.


### Summary

The compressed data stream must start with a byte which gives the amount of bytes to copy directly to the output. This can't exceed 255. Then all bytes are
either output as they are or encoded. A zero byte in the uncompressed data becomes 0x1f in the compressed data. Every value between 0x00 and 0x1e in the compressed data is an encoded match which might use an additional byte. All other bytes are copied as they are.
