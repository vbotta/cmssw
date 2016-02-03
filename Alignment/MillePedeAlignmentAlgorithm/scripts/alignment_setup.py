#!/usr/bin/env python

#############################################################################
##  Builds the config-templates from the universal config-template for each
##  dataset specified in .ini-file that is passed to this script as argument.
##  Then calls mps_setup_v2.pl for all datasets.
##
##  Usage:
##     alignment_setup.py myconfig.ini
##

import argparse
import os
import re
import subprocess
import ConfigParser

# ------------------------------------------------------------------------------
# set up argument parser
helpEpilog =''' '''
parser = argparse.ArgumentParser(description='Setup the alignment as configured in the alignment_config file.', 
                                 epilog=helpEpilog, 
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
# positional argument: config file
parser.add_argument('alignmentConfig', 
                    action='store', 
                    help = 'Name of the .ini config file for alignment.')
# parse argument
args = parser.parse_args()
aligmentConfig = args.alignmentConfig

# ------------------------------------------------------------------------------

# set variables that are not too specific (millescript, pedescript, etc.)
mpsScriptsDir = os.environ['CMSSW_BASE'] + '/src/Alignment/MillePedeAlignmentAlgorithm/scripts/'
milleScript   = mpsScriptsDir + 'mps_runMille_template.sh'
pedeScript    = mpsScriptsDir + 'mps_runPede_rfcp_template.sh'

# get working directory name
currentDir = subprocess.check_output('pwd', stderr=subprocess.STDOUT, shell=True)
mpsdirname = ''
match = re.search(re.compile('mpproduction\/mp(.+?)$', re.M|re.I),currentDir)
if match:
	mpsdirname = 'mp'+match.group(1)
else:
	print 'there seems to be a problem to determine the current directory name:',currentDir
	exit()

# set directory on eos
mssDir = '/store/caf/user/'+os.environ['USER']+'/MPproduction/'+mpsdirname

# create directory on eos if it doesn't exist already
eos = '/afs/cern.ch/project/eos/installation/cms/bin/eos.select'
os.system(eos+' mkdir -p '+mssDir)

# parse config file
config = ConfigParser.ConfigParser()
config.read(aligmentConfig)

# read 'general' section from config file
classInf       = config.get('general','classInf')
pedeMem        = config.getint('general','pedeMem')
jobname        = config.get('general','jobname')
datasetdir     = config.get('general','datasetdir')


# loop over 'dataset' sections (with submit=True)
firstDataset = True
for section in config.sections():
	if 'dataset' in section:
		if config.getboolean(section,'submit'):
			
			# extract vars from config
			name           = config.get(section,'name')
			inputFileList  = config.get(section,'inputFileList')
			njobs          = config.getint(section,'njobs')
			globaltag      = config.get(section,'globaltag')
			collection     = config.get(section,'collection')
			configTemplate = config.get(section,'configTemplate')
			
			
			cosmicsZeroTesla = False
			if config.has_option(section,'cosmicsZeroTesla'):
				cosmicsZeroTesla = config.getboolean(section,'cosmicsZeroTesla')
			
			cosmicsDecoMode = False
			if config.has_option(section,'cosmicsDecoMode'):
				cosmicsDecoMode = config.getboolean(section,'cosmicsDecoMode')
			
			primaryWidth = -1.0
			if config.has_option(section,'primaryWidth'):
				primaryWidth = config.getfloat(section,'primaryWidth')
			
			weight = '1.0'
			if config.has_option(section,'weight'):
				weight = config.get(section,'weight')
			
			# replace '${datasetdir}' in inputFileList
			inputFileList = re.sub('\${datasetdir}', datasetdir, inputFileList)
			
			# replace $CMSSW_BASE in configTemplate
			configTemplate = re.sub('\$CMSSW_BASE', os.environ['CMSSW_BASE'], configTemplate)
			
			# BUILD THE CONFIG TEMPLATE FROM UNIVERSAL TEMPLATE
			with open(configTemplate,'r') as INFILE:
				tmpFile = INFILE.read()
			
			
			tmpFile = re.sub('setupGlobaltag\s*\=\s*[\"\'](.*?)[\"\']', 
			                 'setupGlobaltag = \"'+globaltag+'\"', 
			                 tmpFile)
			tmpFile = re.sub('setupCollection\s*\=\s*[\"\'](.*?)[\"\']', 
			                 'setupCollection = \"'+collection+'\"', 
			                 tmpFile)
			if cosmicsZeroTesla:
				tmpFile = re.sub(re.compile('setupCosmicsZeroTesla\s*\=\s*.*$', re.M),
				                 'setupCosmicsZeroTesla = True',
				                 tmpFile)
			if cosmicsDecoMode:
				tmpFile = re.sub(re.compile('setupCosmicsDecoMode\s*\=\s*.*$', re.M),
				                 'setupCosmicsDecoMode = True',
				                 tmpFile)
			if primaryWidth > 0.0:
				tmpFile = re.sub(re.compile('setupPrimaryWidth\s*\=\s*.*$', re.M),
				                 'setupPrimaryWidth = '+str(primaryWidth),
				                 tmpFile)
			
			
			with open('tmp.py', 'w') as OUTFILE:
				OUTFILE.write(tmpFile)
			thisCfgTemplate = 'tmp.py'
			
			
			# Set mps_setup append option for datasets following the first one
			append = ' -a'
			if firstDataset:
				append = ''
				firstDataset = False
			
			# call mps_setup
			command = 'mps_setup_v2.pl -m%s -M %d -N %s -w %s %s %s %s %d %s %s %s cmscafuser:%s' % (
			          append, 
			          pedeMem, 
			          name,
			          weight, 
			          milleScript,
			          thisCfgTemplate, 
			          inputFileList, 
			          njobs, 
			          classInf, 
			          jobname, 
			          pedeScript, 
			          mssDir)
			print '\n', command
			os.system(command)
			
			os.system('rm tmp.py')











