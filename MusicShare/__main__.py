import DataBaseObject as DBO
import sqlite3
import os.path
import bin.WebInterface as WebInterface
from sys import argv

script, Path = argv
PathNameList = Path.split("\\")
PathNameList.insert(0,"DataBase")
PathName = "_".join(PathNameList)
DataPath = "/Users/Antoine/Documents/Pn/projects/databases/MusicMac.db".format(PathName)

Recalculate = True
usrdb_rewrite = False

print not(os.path.isfile(DataPath))

if Recalculate or not(os.path.isfile(DataPath)):
	print "Reindexing files and directories"
	Algorithm = DBO.DatabasePopulate(Path, DataPath)
	Algorithm.calculate_list_path()
	
if usrdb_rewrite or not(os.path.isfile(WebInterface.USRDATABASE)):
    print "Reinitiating user database"
    conn = sqlite3.connect(WebInterface.USRDATABASE)
    with open(WebInterface.USRDATABASE, mode='r') as f:
        conn.cursor().executescript(f.read())
    conn.commit()
