# PDF-ZIP polyglot file generator
Run with (using the included sample files) : 
```
./gen_poly.py --out magic.pdf --in "CAMUS, Albert - The Stranger.pdf" --message monalisa_joconde_ascii.txt --zip hyeronimus_bosch.jpg
```

This will output a file that : 
1. Is a valid PDF file (will display *The Stranger*, by Camus, when you open it)
2. Is a valid ZIP file (will unzip to a famous painting by Hyeronimus Bosch)
3. Will display a splendid rendition of the Mona Lisa in ASCII, when run thru `cat`
4. Also includes, just before the ASCII art, the command which is to be run to directly output this painting (without the surrounding gibberish)

However, the ASCII art being in the middle of the file, it is unlikely you'll see it. I’m working on a workaround (by hiding it in the beginning of the PDF itself).

**Inspired by PoC||GTFO-0x14**, though this would seem very basic to them.
