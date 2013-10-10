import DataBaseObject as DBO
import sqlite3
from sys import argv

import bin.WebInterface as WebInterface

script, Path = argv

Recalculate = True
usrdb_rewrite = True

if Recalculate or not(os.path.isfile(WebInterface.USRDATABASE)):
	print "Reindexing files and directories"
	Algorithm = DBO.DatabasePopulate(Path, WebInterface.USRDATABASE)
	Algorithm.calculate_list_path(True)
        
	
if usrdb_rewrite or not(os.path.isfile(WebInterface.USRDATABASE)):
    print "Reinitiating user database"
    conn = sqlite3.connect(WebInterface.USRDATABASE)
    with open('schema.sql', mode='r') as f:
        conn.cursor().executescript(f.read())
    conn.commit()
