#! /home/pi/.virtualenvs/MusicShare/bin/python

import threading
import os.path
import web
import json
import random
import time

import bcrypt
from web import form

from Playlist.m3uparser import m3uList
import MusicShare.utils as utils


USRDATABASE = '/home/pi/databases/USRDB4.db'
#MUSICDATABASE = '/Users/Antoine/Documents/Pn/projects/databases/MusicMac.db'
COOKIEDATABASE = '/home/pi/databases/cookieDB.db'
BASESALT = bcrypt.gensalt()
web.config.debug = False

render = web.template.render('/home/pi/projects/MusicShare/templates/')

db = utils.simple_db(COOKIEDATABASE)
#with open("/home/pi/projects/MusicShare/cookie.sql", 'r') as c:
#    db.sql_script(c.read())
#db.exit()


song_properties = ['Song', 'Album', 'Artist']

urls = (
        '/', 'index',
        '/playlist/','playlist',
        '/rplaylist/', 'rplaylist',
        '/login/','login',
        '/logout/','logout',
        '/signin/', 'signin',
        '/upload/', 'upload'
        )

app = web.application(urls, locals())

song_properties = ("id",
                   "title",
                   "album",
                   "artist",
                   "path")

def password_hash(password, salt):
    return bcrypt.hashpw(password, salt)

def cred_gen(password):
    salt = bcrypt.gensalt()
    comp_hash = password_hash(password, salt)
    return comp_hash, salt
    
def local_db():
    mydata = threading.local()
    if not hasattr(mydata, "database"):
        mydata.database = utils.simple_db(USRDATABASE)
    if not hasattr(mydata, "cookieDB"):
        mydata.cookieDB = utils.simple_db(COOKIEDATABASE)
    return mydata

def json_parser(web_data, attribute_list):
    if web_data:
        json_data = json.loads(web_data)
        for an_attr in attribute_list:
            if an_attr not in json_data:
                json_data[an_attr] = ""
    else:
        json_data = {}
        for an_attr in attribute_list:
            json_data[an_attr] = ""
    return json_data

def dictize_songs(result):
    return [dict(zip(song_properties, x)) for x in result]

def third_search_songs(song_data, database):
    sql_statement = ["SELECT Songs.id as id, Songs.song as title, albums.album as album, artists.name as artist, Songs.path as path FROM Songs, albums, artists WHERE Songs.album_id=albums.id AND albums.artist_id=artists.id"]
    values = []
    search_dict = {"Song": " AND Songs.song LIKE ?",
                    "Album": " AND albums.album LIKE ?",
                    "Artist": " AND artists.name LIKE ?"}
    for an_attr in song_data:
        sql_statement.append(search_dict[an_attr])
        values.append("%{0}%".format(song_data[an_attr]))
    result = database.sql_execute("".join(sql_statement), values)
    if result:
        transmit = dictize_songs(result)
        return transmit
    else:
        return False

class index:
    def GET(self):
        return render.index()

    def POST(self):
        #beg = time.time()
        mydata = local_db()
        #print "connection: ", time.time() - beg
        #json_data = json_parser(web.data(), song_properties)
        json_data = json.loads(web.data())
        #print json_data
        #print "parse: ", time.time() - beg
        transmit = third_search_songs(json_data,
                                mydata.database)
        web.header("Content-type", "application/json")
        #print "queried: ", time.time() - beg
        return json.dumps(transmit)

class rplaylist:
    def POST(self):
        mydata = local_db()

        json_data = json.loads(web.data())
        list_id = json_data
        statement = """
        SELECT Songs.id, Songs.Song, Songs.Album, Songs.Artist, Songs.path
        FROM belong, Songs
        WHERE belong.playlist = ? AND belong.song = Songs.id;
        """
        result = mydata.database.sql_execute(statement, [list_id])

        if result:
            transmit = dictize_songs(result)
            return json.dumps(transmit)

class playlist:
    def GET(self):
        mydata = local_db()
        session_id = web.cookies().get("session_cookie")
        if session_id is not None:
            statement = """
            SELECT username FROM cookies WHERE session_id = ?
            """
            user = mydata.cookieDB.sql_execute(statement, [session_id])[0][0]

            statement = """
            SELECT id, name FROM playlist WHERE owner = ?;
            """
            result = mydata.database.sql_execute(statement, [user])
            return json.dumps(result)



    def POST(self):
        mydata = local_db()

        json_data = json.loads(web.data())
        list_name = json_data[0]
        playlist = json_data[1]
        session_id = web.cookies().get("session_cookie")
        if session_id is not None:
            statement = """
            SELECT username FROM cookies WHERE session_id = ?
            """
            user = mydata.cookieDB.sql_execute(statement, [session_id])[0][0]
            #print list_name, playlist
            statement = """
            INSERT INTO playlist (name, owner) VALUES (?,?);
            """
            result = mydata.database.sql_execute(statement, 
                    [list_name,
                    user])
            statement = """
            SELECT id FROM playlist where name = ? and owner = ?;
            """

            result = mydata.database.sql_execute(statement, 
                    [list_name,
                    user])
            an_id = result[0]

            for song in playlist:

                #print type(an_id), type(song["id"])
                statement = """
                INSERT INTO belong (playlist, song) Values (?, ?);
                """
                
                result = mydata.database.sql_execute(statement, 
                                                        [an_id[0],
                                                        song["id"]])
            return "true"
        else:
            return "false"

    def DELETE(self):
        mydata = local_db()
        i = web.input(id=None)
        statement = """
        DELETE FROM playlist WHERE id = ?;
        """
        mydata.database.sql_execute(statement, 
                                    [i.id])
        statement = """
        DELETE FROM belong where playlist = ?;
        """
        mydata.database.sql_execute(statement, 
                                    [i.id])
            
class login:
    def GET(self):
        mydata = local_db()
        session_id = web.cookies().get("session_cookie")
        if session_id is not None:
            statement = """
            SELECT username FROM cookies WHERE session_id = ?
            """
            user = mydata.cookieDB.sql_execute(statement, [session_id])[0][0]
            return json.dumps(user)
        else:
            return "" 

    def POST(self):
        mydata = local_db()
        json_data = json_parser(web.data(), ["name", "password"])
        username = json_data["name"]
        password = json_data["password"]
        statement = """
        SELECT hash, salt FROM users WHERE name = ?;
        """
        result = mydata.database.sql_execute(statement, 
                                            [username])
        if result:
            comp_hash, salt = result[0]
        else:
            comp_hash = False
            salt = False
        if comp_hash and salt:
            hash = password_hash(password.encode('utf-8'),
                                 salt.encode('utf-8'))
        else:
            hash = password_hash(password.encode('utf-8'),
                                 BASESALT.encode('utf-8'))
        if hash == comp_hash:
            session_id = utils.id_generator()
            statement = """
            INSERT INTO cookies (username, session_id) VALUES (?, ?)
            """
            mydata.cookieDB.sql_execute(statement, [username, session_id])
            #print "cookie db", time.time() - beg
            web.setcookie("session_cookie", session_id, expires="3600", secure=True)
            return "True"
        else:
            return "False"

class logout:
    def GET(self):
        mydata = local_db()
        session_id = web.cookies().get("session_cookie")
        statement = "DELETE FROM cookies WHERE session_id = ?"
        mydata.cookieDB.sql_execute(statement, [session_id])
        web.setcookie("session_cookie", "", expires=-1)
            
class signin:
    def POST(self):
        mydata = local_db()
        json_data = json_parser(web.data(), ["name", "password"])
        statement = "INSERT INTO users (name, hash, salt) VALUES (?, ?, ?);"
        comp_hash, salt = cred_gen(json_data["password"].encode("UTF-8"))
        try:
            mydata.database.sql_execute(statement, [json_data["name"],
                                                    comp_hash,
                                                    salt])
            return "True"
        except sqlite3.IntegrityError as e:
            print e
            return "False"

class upload:
    def POST(self):
        mydata = local_db()
        session_id = web.cookies().get("session_cookie")
        #print session_id
        if session_id is not None:
            statement = "SELECT username FROM cookies WHERE session_id = ?"
            user = mydata.cookieDB.sql_execute(statement, [session_id])[0][0]
            #print user

            playlist = web.data()
            parser = m3uList()
            parser.parse(playlist)
            song_list=[]
            for song in parser:
                name = song["Title"]
                artist = song["Artist"]
                matching = search_songs(name, False, artist, mydata.database)
                for item in matching:
                    song_list.append(item)
            #print song_list
            list_name = "list"+str(time.time())
            statement = "INSERT INTO playlist (name,  owner) VALUES (?,?);"
            result = mydata.database.sql_execute(statement, 
                                                    [list_name,
                                                    user])
            statement = "SELECT id FROM playlist where name = ? and owner = ?;"
            result = mydata.database.sql_execute(statement, 
                    [list_name,
                    user])
            #print result
            an_id = result[0]

            for song in song_list:

                #print type(an_id), type(song["id"])
                statement = """
                INSERT INTO belong (playlist, song) Values (?, ?);
                """
                
                result = mydata.database.sql_execute(statement, 
                                                        [an_id[0],
                                                        song["id"]])

                
            
            
def header_processor(handle):
    web.header("Access-Control-Allow-Credentials", "true")
    #web.header("Cache-Control", "No-Cache")
    return handle()
    
app.add_processor(header_processor)

if __name__ == "__main__":
    func = app.wsgifunc()
    web.httpserver.runsimple(func, ('localhost', 8000))
    #app.run()            
