# PDF-ZIP polyglot file generator
Run with (using the included sample files) : 
```
./gen_poly.py --out magic.pdf --in "CAMUS, Albert - The Stranger.pdf" --message monalisa_joconde_ascii.txt --zip hyeronimus_bosch.jpg
```

This will output a file that : 
1. Is a valid PDF file (will display *The Stranger*, by Camus, when you open it)
2. Is a valid ZIP file (will unzip to a famous painting by Hyeronimus Bosch, and a splendid rendition of the Mona Lisa in ASCII)
3. Will actually display this rendition when run thru `cat`
4. Also includes, just before this, the command which is to be run to directly output this painting (without the surrounding gibberish)

However, the added command in point 4. will also appear when decompressing the archive. I’m working on a workaround (by hiding it in the PDF itself).

**Inspired by PoC||GTFO-0x14**, though this would seem very basic to them.