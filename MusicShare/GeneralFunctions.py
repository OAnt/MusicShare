""" This module contains general function used in various algrithm
"""

import os
import sqlite3

def convert_tuple(ATuple):
	AList = []
	for Item in ATuple:
		AList.append(Item)
	return AList

def sql_execute(Cursor, Statement, List):
	print "Is SQL", sqlite3.complete_statement(Statement), Statement
	try:
		Result = Cursor.execute(Statement, List)
		return [Result]
	except sqlite3.Error as e :
		return [False, e]

def childrens(Path):
	""" returns same same outputs as os.listdir skipping
	windows error 5 for NTFS junction
	
	Moreover if a folder accessed is denied you'll never be able to
	clean it which is the ultimate goal of using DiskMonitor, so I
	skip windows error 5 access denied (BTW its number is 13 in
	python)
	"""
	DirList = []
	FileList = []
	
	try:
	
		Elements = os.listdir(Path)			
		for Item in Elements:
			ItemPath = "\\".join([Path,Item])
			if os.path.isdir(ItemPath):
				DirList.append(ItemPath)
			elif os.path.isfile(ItemPath):
				FileList.append(ItemPath)
				
	except OSError, E:
		if E.errno == 13:
			print Path, "Skipt because this program is not able to handle NTFS junction or accessed denied"
		else:
			raise E

	return DirList, FileList

def calculate_local_size(FileList):
	#print "Path!", Path
	TempSize = 0
	for Item in FileList:
		TempSize = TempSize + os.stat(Item).st_size
	return TempSize

def conversion_brutal(Size):
	""" Aim at converting a size measured in bytes in a more
	convenient value
	"""
	String = str(Size)
	Exponent = len(String)
	if 7>Exponent>3:
		String = " ".join([str(Size/1000), "KB"])
	elif Exponent>6:
		String = " ".join([str(Size/1000), "MB"])
	else:
		String = " ".join([String, "B"])
	return String
		
def conversion_soft(ASize):
	Size = ASize
	Units = ["B", "KB", "MB", "GB", "TB", "PB"]
	LU = len(Units)
	String = str(Size)
	Exponent = len(String)
	ConvSize = [String, "B"]
	i = 0
	while Exponent > 3 or i >= len(Units):
		i = i + 1
		Size = round(Size / 1000,1)
		Exponent = Exponent - 3
		ConvSize[1] = Units[i]
	ConvSize[0] = str(Size)
	String = " ".join(ConvSize)
	return String
	
#disrcimination function

def pareto_discrimination(Size, Factor):
	TempSize = Factor - Size
	if Factor >= 0:
		return True, TempSize
	else:
		return False, TempSize
			
def size_discrimination(Size, Factor):
	if Size >= Factor:
		return True, Factor
	else:
		return False, Factor