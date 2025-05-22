import os
import shutil
import glob
import csv
import threading
### Searches a directory and outputs the first file matching the pattern
def searchFiles(directory, pattern):
	for filename in glob.glob(os.path.join(directory,"**",pattern), recursive=True):
		return filename
	return None

def asyncCopy(file,dest):
	fileTransfer = threading.Thread(target=shutil.copy,args=(file,dest))
	fileTransfer.start()
	return fileTransfer
	#shutil.copy(file,dest)

def threadClean(threads):
	for thread in threads:
		thread.join();
### Checks if a directory exists, then makes it if not
def mkDir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

### Opens a CSV produced from the Production Control page of Tekla EPM
def openCSV(path):
	with open(path) as csvFile:
		reader = csv.DictReader(csvFile)
		return makeTable(reader)

### Makes a table out of an open CSV
def makeTable(table):
	final = []
	for row in table:
		final.append(row)

	return final