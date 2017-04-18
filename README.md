# PDF-ZIP-NES polyglot file generator
Run with (using the included sample files) : 
```
./gen_poly.py --out magic.pdf --in "CAMUS, Albert - The Stranger.pdf" --message monalisa_joconde_ascii.txt --zip hyeronimus_bosch.jpg --header sample.nes
```

Let's break this up : 
* `--out` is the path/name of the resulting file – which will be a perfectly valid PDF file
* `--in` is your original PDF file
	* in my example : *The Stranger*, by Camus
* `--message` is the plaintext message that should appear when the resulting file will be opened in a hex editor, or directly `cat`-ed in a terminal
	* in my example : a splendid rendition of the Mona Lisa in ASCII
	* additional feature : a command to directly output this message (and **only** this message without any surrounding gibberish) will be added just before the message itself
		* this command looks like <code>tail -c +<strong>offset of message in file</strong> magic.pdf | head -c <strong>length of message</strong></code>
* `--zip` is the (list of) file(s) that are to be zipped and appended in the original PDF
	* in my example : a famous painting by Hyeronimus Bosch
	* additional feature : when unzipped, the original PDF will also appear, *although it is not duplicated in the resulting file* – ain't this magic :)
* `--header` is the file that is to be included at the beginning of the file, before the PDF itself
	* in my example : a NES game, for emulators. So that you can also the PDF in an emulator !

Still, with all this stuff appended to and included at the beginning of the PDF, it stays valid and viewable in any standard PDF viewer (such as Adobe Reader, Preview on macOS, etc...)
All of this is possible thanks to the fact that the PDF header does not have to be at the beginning of the file, for it to be a valid PDF.

**Inspired by PoC||GTFO-0x14**, though this would seem very basic to @angea
