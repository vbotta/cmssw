#!/usr/bin/env python
import re
import argparse


# Set up argrument parser
helpEpilog = ''''''

parser = argparse.ArgumentParser(description='Take card file, blank all INFI directives and insert the INFI directives from the modifier file instead.', 
                                 epilog=helpEpilog, 
                                 formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument('inCfg', action='store',
                    help='name of the config-template')
parser.add_argument('modCfg', action='store',
                    help='name of the modifier file from mps_split')
parser.add_argument('outCfg', action='store',
                    help='name of modified output file')
parser.add_argument('isn', action='store',
                    help='number of the job')

# Parse arguments
args = parser.parse_args()
inCfg  = args.inCfg
modCfg = args.modCfg
outCfg = args.outCfg
isn    = args.isn


# open input file
with open(inCfg, 'r') as INFILE:
	body = INFILE.read()

# read modifier file
with open(modCfg, 'r') as MODFILE:
	mods = MODFILE.read()
mods = mods.strip()

# prepare the new fileNames directive
fileNames = mods.split('\n')
if 'CastorPool=' in fileNames[0]:
	del fileNames[0]

# prepare list of fileNames as string
replaceBlock = "\n                "
numberOfFiles = len(fileNames)
for i in range(numberOfFiles):
	entry = fileNames[i].strip()
	
	if (i+1) < (numberOfFiles):
	    replaceBlock += "\'"+entry+"\',\n                "
	else:
		replaceBlock += "\'"+entry+"\'"

# replace the placeholder
body = re.sub('[\"\']placeholder_readFiles[\"\']', replaceBlock, body)

# replace ISN number (input is a string of three digit number with leading zeros though)
body = re.sub(re.compile('ISN',re.M), isn, body)

# print to outCfg
with open(outCfg, 'w') as OUTFILE:
	OUTFILE.write(body)







