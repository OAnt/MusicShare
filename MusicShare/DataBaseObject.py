import os
import os.path
import sqlite3
import time
import stat

from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
#import kaa.metadata
#import eyed3

from utils import simple_db, parser, make_eq_dict

class Algo(object):
    pass

class database(simple_db):
    def __init__(self, data_path):
        self.database = sqlite3.connect(data_path)
        self.db_cursor = self.database.cursor()

    def update_song(self, data_list):
        sql = """UPDATE Songs SET path = ?
            WHERE Song = ? AND Album = ? AND Artist = ?;
            """
        self.insertion(SQL, data_list)

    def insert_song(self, data_list):
        SQL = """INSERT INTO Songs
            (Song, Album, Artist, path) VALUES (?,?,?,?);
            """
        self.insertion(SQL,data_list)

    def creation_database(self):
        with open('music.sql', mode='r') as f:
            self.sql_script(f.read())

class DatabasePopulate(Algo):
    """ This class takes the initial path to give associated
    directories
    
    This object contains methods used in the Algorithm
    """
    def __init__(self, init_path, database_path):
        self.list_path = [init_path]
        self.Data = database(database_path) #Uses the class
        self.Data.creation_database()
        #constants
        self.FileInsert = []
        self.DirInsert = []
        mp4_song_properties = ["\xa9nam", "\xa9alb", "\xa9ART"]
        id3_song_properties = ["title", "album", "artist"] #tags must follow this order title, album, artist
        self.equivalencies = make_eq_dict(mp4_song_properties, id3_song_properties)
        self.prop = {".mp3": (EasyID3, id3_song_properties),
                    ".m4a": (MP4, mp4_song_properties)}

    
    def mparser(self, song_path, extensions = [".mp3",".m4a"]):
        ext = os.path.splitext(song_path)[1]
        if ext in extensions:
            #print song_path
            file = parser(song_path, ext, self.equivalencies, self.prop)
            #print file
            if file:
                if file["title"]:
                    song_title = file["title"]
                else:
                    a_path, song_title = os.path.split(song_path)
                    
                if file["album"]:
                    song_album = file["album"]
                else:
                    song_album = "unknown"
                    
                if file["artist"]:
                    song_artist = file["artist"]
                else:
                    song_artist = "unknown"
            else:
                path, song_title = os.path.split(song_path)
                path, song_album = os.path.split(path)
                path, song_artist = os.path.split(path)
                
            self.FileInsert.append([song_title.lower(),
            song_album.lower(),
            song_artist.lower(),
            song_path.decode('UTF-8')
            ])#on must decode using system default encoding
        
    
    def childrens(self, Path):
        """ returns same same outputs as os.listdir skipping
        windows error 5 for NTFS junction
        
        Moreover if a folder accessed is denied you'll never be able to
        clean it which is the ultimate goal of using DiskMonitor, so I
        skip windows error 5 access denied (BTW its number is 13 in
        python)
        """
        DirList = []
        FileList = []
        ErrorMsg = "Skipt because this program is not able to handle NTFS junction or accessed denied"
        try:
            Elements = os.listdir(Path)
            for Item in Elements:
                item_path = os.path.join(Path,Item)
                mode = os.stat(item_path).st_mode
                if stat.S_ISDIR(mode):
                    DirList.append(item_path)
                else:
                    self.mparser(item_path)
        except OSError, E:
            if E.errno == 13:
                print Path, ErrorMsg
            else:
                raise E
        return DirList, FileList
    
    def calculate_list_path(self, update):
        """ This method unfold the original path to return a list
        containing all sub directories woth their sizes
        """
        for FatherPath in self.list_path:
            DirList, FileList = self.childrens(FatherPath)
            for Item in DirList:
                self.list_path.append(Item)
        if not(update):
            self.Data.insert_song(self.FileInsert)
        else:
            for song in self.FileInsert:
                temp = song.pop()
                song.insert(temp, 0)
            self.Data.update_song(self.FileInsert)
