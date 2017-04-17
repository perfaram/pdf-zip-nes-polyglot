#!/usr/bin/env python3

from __future__ import print_function
import argparse, sys, zipfile, ntpath
import os.path
from bitstring import ConstBitStream
import shutil

from io import BytesIO

def errprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def filelike_size(f):
	old_file_position = f.tell()
	f.seek(0, os.SEEK_END)
	size = f.tell()
	f.seek(old_file_position, os.SEEK_SET)
	return size

def path_leaf(path):
	head, tail = ntpath.split(path)
	return tail or ntpath.basename(head)

def find_offset(of, in_data):
	bitstream = ConstBitStream(in_data)
	offset = bitstream.find(of, bytealigned=False)
	return offset

def gen_message_append_command(start_offset, length, filename):
	return u"tail -c +" + str(start_offset) + u" " + filename + u" | head -c " + str(length) + u'\n'

class InMemoryZipFile(object):
	#mostly courtesy of Justin Ethier and @ruamel, stackoverflow.com/questions/2463770
	def __init__(self, file_name=None, compression=zipfile.ZIP_DEFLATED, debug=0):
		# Create the in-memory file-like object
		if hasattr(file_name, '_from_parts'):
			self._file_name = str(file_name)
		else:
			self._file_name = file_name

		self.in_memory_data = BytesIO()
		# Create the in-memory zipfile
		self.in_memory_zip = zipfile.ZipFile( self.in_memory_data, "w", compression, False )
		self.in_memory_zip.debug = debug
		self.compression_map = dict()
		self.compression = compression

	def append(self, filepath_to_zip, compress_type):
		'''Appends the file at path filepath_to_zip to the in-memory 
		zip, compressing according to the compress_type'''

		# Write the file to the in-memory zip
		self.in_memory_zip.write(filepath_to_zip, compress_type=compress_type)
		self.compression_map[filepath_to_zip] = compress_type

		return self #for daisy-chaining

	def appendStr(self, filename_in_zip, file_contents, compress_type):
		'''Appends a file with name filename_in_zip and contents of
		file_contents to the in-memory zip.'''
		self.in_memory_zip.writestr(filename_in_zip, file_contents, compress_type=compress_type)
		self.compression_map[filename_in_zip] = compress_type
		return self   # so you can daisy-chain

	def write_to_file(self, filename):
		'''Writes the in-memory zip to a file.'''
		# Mark the files as having been created on Windows so that
		# Unix permissions are not inferred as 0000
		for zfile in self.in_memory_zip.filelist:
			zfile.create_system = 0

		self.in_memory_zip.close()
		with open(filename, 'xb') as f:
			f.write(self.data)

	def close_and_return_data(self): #there's no coming back
		'''Closes the ZIP file, and make last required adjustments. 
		After calling this method, there's no coming back. The only
		thing you can do is writing the ZIP.'''
		# Mark the files as having been created on Windows so that
		# Unix permissions are not inferred as 0000
		for zfile in self.in_memory_zip.filelist:
			zfile.create_system = 0

		self.in_memory_zip.close()
		return self.data

	@property
	def data(self):
		return self.in_memory_data.getvalue()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if self._file_name is None:
			return
		self.write_to_file(self._file_name)

	def delete(self, file_name):
		"""
		zip_file can be a string or a zipfile.ZipFile object, the latter will be closed
		any name in file_names is deleted, all file_names provided have to be in the ZIP
		archive or else an IOError is raised
		"""
		new_in_memory_data = BytesIO()
		new_in_memory_zip = zipfile.ZipFile( new_in_memory_data, "w", self.compression, False )

		for l in self.in_memory_zip.infolist():
			if l.filename == file_name:
				continue
			new_in_memory_zip.writestr(l.filename, self.in_memory_zip.read(l.filename), compress_type=self.compression_map[l.filename])

		self.in_memory_zip = new_in_memory_zip
		self.in_memory_data = new_in_memory_data

	def delete_from_zip_file(self, pattern=None, file_names=None):
		"""
		zip_file can be a string or a zipfile.ZipFile object, the latter will be closed
		any name in file_names is deleted, all file_names provided have to be in the ZIP
		archive or else an IOError is raised
		"""
		if pattern and isinstance(pattern, string_type):
			import re
			pattern = re.compile(pattern)
		if file_names:
			if not isinstance(file_names, list):
				file_names = [str(file_names)]
			else:
				file_names = [str(f) for f in file_names]
		else:
			file_names = []
		with zipfile.ZipFile(self._file_name) as zf:
			for l in zf.infolist():
				if l.filename in file_names:
					file_names.remove(l.filename)
					continue
				if pattern and pattern.match(l.filename):
					continue
				self.append(l.filename, zf.read(l))
			if file_names:
				raise IOError('[Errno 2] No such file{}: {}'.format(
					'' if len(file_names) == 1 else 's',
					', '.join([repr(f) for f in file_names])))




parser = argparse.ArgumentParser(description='Generate a ZIP/PDF/Whatever polyglot file, with a cleartext message embedded (and instructions to output this message included). The `whatever` may be, for instance, a NES game file - it is added before the PDF.')
parser.add_argument('--out', dest='out_path', action='store', help='set the path of the resulting file', required=True)
parser.add_argument('--in', dest='in_path', action='store', help='path of the PDF to which to append', required=True)
parser.add_argument('--zip', dest='zip_array', action='store', nargs='+', help='path(s) to the file(s) going to be zipped and included in the PDF', required=True)
parser.add_argument('--message', dest='message_path', action='store', help='path to the plaintext file', required=True)
parser.add_argument('--header', dest='header_path', action='store', help='path to the header file, that will be added before the PDF', required=True)

def main():
	args = parser.parse_args()

	out_path = args.out_path
	tempout_path = out_path + ".temp"
	in_path = args.in_path
	zip_array = args.zip_array
	message_path = args.message_path
	header_path = args.header_path

	if os.path.exists(out_path):
		errprint("File " + out_path + " ALREADY EXISTS, gonna overwrite !!!!!!!")
		#exit(1)

	offset = 0

	with open(tempout_path, 'xb') as outfile:
		with open(header_path, 'rb') as headerfile:
			offset += filelike_size(headerfile)
			shutil.copyfileobj(headerfile, outfile)

		#with open(in_path, 'rb') as infile:
		#	offset += filelike_size(infile)
		#	shutil.copyfileobj(infile, outfile)

		with open(message_path, 'rb') as message_file:
			message_bytes = message_file.read()

			#WARNING
			#this is notoriously suboptimal, as we may very well have an issue when adding a number (eg 9 to 10, 99 to 100)
			#therefore, we add a useless linebreak at the end of the message (so that if the last char gets cut, it didn't matter anyway)
			len_msg_comm = len(gen_message_append_command(start_offset = offset, length = len(message_bytes) + 24, filename = path_leaf(out_path)))
			#minimum overhead of the command string ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
			message_command = gen_message_append_command(start_offset = offset, length = len(message_bytes) + 1 + len_msg_comm, filename = path_leaf(out_path)) 
			#notice the "+1" there ? This is to account for the additional linebreak     ->~~~~~~~~~~~~~~~~~~>^
			
			new_message = message_command.encode('utf-8') + message_bytes + "\n".encode('utf-8')
			outfile.write(new_message)
			message_len = len(new_message)
			print("The ASCII art begins @" + str(offset) + " and lasts " + str(message_len) + " bytes")
			offset += message_len
			print("ZIP file will have its offsets off by " + str(offset) + " bytes")

		with InMemoryZipFile() as memzip:
			memzip.append(in_path, compress_type=zipfile.ZIP_STORED)
			for file_to_zip in zip_array:
				memzip.append(file_to_zip, compress_type=zipfile.ZIP_DEFLATED) #deflated
			size_of_zipped = filelike_size(memzip.in_memory_data)
			offset += size_of_zipped

			outfile.write(memzip.close_and_return_data())

	print("Now fixing ZIP file : ")
	fix_command = "zip -Fv " + tempout_path + " --out " + out_path #this fixes the offsets in the pdf/zip polyglot file, otherwise zip will complain (albeit correctly performing its work) when unzipping
	os.system(fix_command)
	os.remove(out_path + ".temp")

if __name__ == '__main__':
	main()