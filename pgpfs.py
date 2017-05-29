#!/usr/bin/env python2
# 
# watch out, this is only possible with modified gpg version
# download this version as well from aestetix repo 

""" pgpfs is a tool to turn your friendly pgp keyserver into a redundant
persistant filesystem."""

import re
import os
import sys
import gnupg
import base64
import pylzma
import argparse
import threading

from hashlib import sha256

# TODO adjust with pgpfspath
os.system('rm -fr .pgpfs')

# trial and error lead to this number
SPLIT_LENGTH = 986

# pack file
def pack_file_to_disk(source_file):
	''' takes the file and packs it '''
	print 'Compressing file'
	# TODO gen random temp here
	target_file='tempfile.tmp'
	with open(source_file, 'r') as source, open(target_file,'wb') as target:
		lz = pylzma.compressfile(source, eos=1)
		while True: 
			b =lz.read(1)
			if not b:
				break
			target.write(b)
		target.close()
	return target_file

def unpack_file_from_disk(packed_file, out_file):
	''' unpack file '''
	print 'Uncompressing file'
	with open(packed_file, 'rb') as packed, open(out_file,'wb') as out:
		obj = pylzma.decompressobj()
		decompress = ''
		while True:
			b = packed.read(1)
			if not b:
				break 
			dec = obj.decompress(b)
			out.write(dec)
	return True

# store file
def read_file_into_list(source_file):
	""" reads file into list"""
	with open(source_file, 'r') as source:
		data = base64.b64encode(source.read())
		return [data[i:i+SPLIT_LENGTH] for i in range(0, len(data), SPLIT_LENGTH)]

def create_comment(data):
	""" takes data bit and turns it into a key comment"""
	checksum = sha256(data).hexdigest()
	comment = checksum + ' ' + data
	return comment

def create_key(name):
	""" creates gpg key out of given data"""
	input_data = GPG.gen_key_input(
		key_type='RSA',
		key_length='1024',
		name_real='PGP File System',
		name_comment=create_comment(name),
		name_email='placeholder@email.address'
	)
	return GPG.gen_key(input_data)

def send_key(key_id):
	""" uploads given key to keyserver"""
	key_id = str(key_id)
	GPG.send_keys(KEYSERVER, key_id)
	if key_id == GPG.search_keys(key_id, KEYSERVER)[0]['keyid']:
		return key_id
	else:
		error = 'Error uploading key ', key_id
		return error

def store_file(filename1, filename2):
	""" overall function to upload file to keyserver"""
	print 'Splitting ', filename1, ' into encoded comments for keys'

	# watch out return value is the name of the newly packed file now
	filename1 = pack_file_to_disk(filename1)

	file_list = read_file_into_list(filename1)
	output_file = open(filename2, 'w')
	counter_length = len(file_list)
	counter = 0
	for chunk in file_list:
		print 'Creating key ', counter, ' of ', counter_length
		counter = counter + 1
		key_id = create_key(chunk)
		output_file.write(send_key(key_id)+'\n')
		output_file.flush()
		print '--> key has been created and uploaded'
	print 'File has been successfully uploaded to ', KEYSERVER

	# TODO adjust with args
	# tempfile is created at packing stage
	os.system('tempfile.tmp')

# fetch file

def get_key_comment(key_id):
	""" returns comment section of a given key"""
	return GPG.search_keys(key_id, KEYSERVER)[0]['uids']

def parse_key(key_id):
	"""" parses file bit out of key comment"""
	comment = get_key_comment(key_id)[0]
	regex = re.compile(".*?\\((.*?)\\)")
	comment_bits = re.findall(regex, comment)[0].split(' ')
	if comment_bits[0] == sha256(comment_bits[1]).hexdigest():
		return comment_bits[1]

def fetch_file(index_file, filename):
	""" overall function to fetch component file parts from keyserver"""
	filelzma='%s.lzma' % filename
	with open(index_file, 'r') as index, open(filelzma, 'w+') as download:
		print 'Fetching keys from ', KEYSERVER, ' to create ', filelzma
		fetched_file = ''
		index_length = len(index.readlines())
		index.seek(0) # because python is stupid
		counter = 0
		for key in index.readlines():
			print 'Fetching key ', counter, ' of ', index_length
			counter = counter + 1
			fetched_file = fetched_file + parse_key(key.rstrip('\n'))
		print 'All keys have been downloaded'
		download.write(base64.b64decode(fetched_file))
	# hook in here and unpack the data
	# filename == original outname
	# filelzma == packed file here as download
	unpack_file_from_disk(filelzma,filename)
	print 'File has been decoded and saved as ', filename

	# remove lzma 
	os.unlink(filelzma)

def usage():
	print """Usage: ./pgpfs.py [action] filename1 filename2'
		   action can be either ''store'' or ''fetch'''

	   When action is 'store':
		   filename1 is the file to upload, filename2 is the name of the key allocation table
	   When action is 'fetch':
		   filename1 is the key allocation table, filename2 is the output file

	   Example uses:
		 - To store 'sample.mp3' on the keyserver
		   ./pgpfs.py store sample.mp3 sample.kat
		 - To fetch the file contained in 'sample.kat' and store it as 'sample.mp3'
		   ./pgpfs.py fetch sample.kat sample.mp3
	"""
	sys.exit(0)

def run(args):
	''' run function, do all the magic '''

	global KEYSERVER
	global GPG 


	pgpfspath = args.pgpfspath
	pgpfsbin = args.pgpfsbin
	KEYSERVER = args.keyserver
	ACTION = args.action
	kat = args.kat
	store = args.store
		
	GPG = gnupg.GPG(gnupghome=pgpfspath,gpgbinary=pgpfsbin)

	if ACTION not in ['store', 'fetch']:
		print 'Please specific either ''store'' or ''fetch'''
		sys.exit(0)

	if ACTION == 'store':
		store_file(store, kat)
	elif ACTION == 'fetch':
		fetch_file(kat, store)
	pass

def main():
	prog_name='pgpfs.py'
	prog_desc='https://github.com/aestetix/pgpfs'

	parser = argparse.ArgumentParser(prog=prog_name, description=prog_desc)
	parser.add_argument('-a','--action',help='action to do: store or fetch',dest='action',required=True)
	parser.add_argument('-k','--katfile',help='if fetch specify KAT file',dest='kat',required=False)
	parser.add_argument('-s','--storefile',help='if store specify file for upload',dest='store',required=False)
	parser.add_argument('--keyserver',help='specify keyserver',dest='keyserver',required=False, default='pgp.mit.edu')
	parser.add_argument('--pgpfspath',help='specify path for pgpfs',dest='pgpfspath',required=False, default='.pgpfs')
	parser.add_argument('--gpgbinary',help='specify path for pgpfs binary(patched gpg bin)',dest='pgpfsbin',required=False, default='/root/fuzzygpg/bin/gpg2')
	args = parser.parse_args()
	run(args)

if __name__ == '__main__':
	main()
