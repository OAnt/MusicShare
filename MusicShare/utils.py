import sqlite3
import string
import random
import base64
import StringIO
#import csv
#import chardet

import mutagen

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class simple_db(object):

    def __init__(self, database):
        self.database = sqlite3.connect(database)
        #self.database.row_factory = dict_factory
        self.db_cursor = self.database.cursor()
        self.sql_execute("PRAGMA foreign_keys = ON", [])
    
    def exit(self):
        self.database.close()
    
    def sql_script(self,statement):
        try:
            Result = self.db_cursor.executescript(statement)
            self.database.commit()
            return Result.fetchall()
        except sqlite3.Error as e:
            print e
            return False

    def insertion(self,SQL,data_list):
        self.db_cursor.executemany(SQL, data_list)
        self.database.commit()

    def sql_execute(self,statement, List):
        #print "Is SQL", sqlite3.complete_statement(statement), statement
        #DO NOT USE FOR INSERT OR UPDATE ONLY FOR READING
        try:
            Result = self.db_cursor.execute(statement, List)
            self.database.commit()
            return Result.fetchall()
        except sqlite3.Error as e:
            print e
            return False

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
	ConvSize[0] = str(float(Size))
	String = " ".join(ConvSize)
	return String
    
def id_generator(size=20):
    with open("/dev/urandom", 'r') as zzz:
        aaa = zzz.read(size)
    return base64.b64encode(aaa)
    
def id_generator_old(size=20, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))
    
def itune_list_parser(playlist):
    #playlist_io = StringIO.StringIO(playlist)
    enc_playlist = playlist.decode('utf-16').encode('utf-8')
    print enc_playlist
    parsed_songs = []
    for line in enc_playlist.split("\n"):
        new_line = line
        song_array = line.split("\t")
        #print len(song_array)
        if len(song_array) > 4:
            parsed_songs.append((song_array[0], song_array[3], song_array[1]))
    parsed_songs.pop(0)
    return parsed_songs


def make_eq_dict(*args):
    song_properties = ["title", "album", "artist"]
    eq_dict = {}
    std_len = len(song_properties)
    for tag_list in args:
        if len(tag_list) >= std_len:
            for i in xrange(0, std_len):
                eq_dict[tag_list[i]] = song_properties[i]
                #print song_properties[i]
    #print eq_dict
    return eq_dict


def parser (a_file, extension, equivalencies, prop):
    audio = {}
    try:
        file_tags = prop[extension][0](a_file)
        #if extension == ".m4a":
        #    print file_tags.keys()[2]
        #print file_tags
        for tag in prop[extension][1]:
            #if extension == ".m4a":
            #    print tag
            if tag in file_tags.keys():
                audio[equivalencies[tag]] = file_tags[tag][0]
            else:
                audio[equivalencies[tag]] = "unknown"
        return audio
    except mutagen._id3util.ID3NoHeaderError:
        return audio

