# PGP File System

PGP File System (pgpfs) is a tool to turn your friendly pgp keyserver into a
redundant persistant filesystem.

## Installation

From a base Ubuntu 14.04.5 installation, please install the following packages:

```
apt-get install git python-pip python-virtualenv rng-tools
```

Check out the repository onto your local machine:
```
git clone git@gitlab.com:aestetix/pgpfs.git
```
This creates a directory called "pgpfs." Go into the directory and  run
```
virtualenv .
source bin/activate
pip install -r requirements.txt
```
# Fork()

Patched pgpfs code from https://github.com/aestetix/pgpfs. 
Has now:

- argparse
- compression / decompression

# TODO

- add threading
- add encryption

# TODO for someone with time and skills

- Building an vfs based on pgpfs, implementation ideas welcome :)

# USAGE

./pgpfs.py -h
usage: pgpfs.py [-h] -a ACTION [-k KAT] [-s STORE] [--keyserver KEYSERVER]
                [--pgpfspath PGPFSPATH] [--gpgbinary PGPFSBIN]

https://github.com/aestetix/pgpfs

optional arguments:
  -h, --help            show this help message and exit
  -a ACTION, --action ACTION
                        action to do: store or fetch
  -k KAT, --katfile KAT
                        if fetch specify KAT file
  -s STORE, --storefile STORE
                        if store specify file for upload
  --keyserver KEYSERVER
                        specify keyserver
  --pgpfspath PGPFSPATH
                        specify path for pgpfs
  --gpgbinary PGPFSBIN  specify path for pgpfs binary(patched gpg bin)

# Upload
./pgpfs.py -a store -s somefile.ext -k somefile.kat

# Download
./pgpfs.py -a store -s example.gif -k sample.kat

# NOTE
Please note that you need the gpg patched code from here:
https://github.com/aestetix/gpg
Compile and place somewhere. Adjust --gpgbinary accoringly.

Also you need to run an entropy source:
rndg -r /dev/urandom
