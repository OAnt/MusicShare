import threading
import os.path
import web
import json
import random
import time

import bcrypt
from web import form

import MusicShare.utils as utils


USRDATABASE = '/Users/Antoine/Documents/Pn/projects/databases/usrDB2.db'
#MUSICDATABASE = '/Users/Antoine/Documents/Pn/projects/databases/MusicMac.db'
COOKIEDATABASE = '/Users/Antoine/Documents/Pn/projects/databases/cookieDB.db'
BASESALT = bcrypt.gensalt()
web.config.debug = False

render = web.template.render('templates/')

db = utils.simple_db(COOKIEDATABASE)
with open("cookie.sql", 'r') as c:
    db.sql_script(c.read())
db.exit()


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

def dictize_songs(db_res):
    transmit = []
    for element in db_res:
        temp_dict = {}
        temp_str = " in ".join([element[1].title(),
                            element[2].title()])
        temp_str = " by ".join([temp_str,
                            element[3].title()])
        temp_dict["key"] = temp_str
        temp_dict["value"] = element[4]
        temp_dict["id"] = element[0]
        transmit.append(temp_dict)
    return transmit

def search_songs(song_title, song_album, song_artist, database):
    sql_statement = ["SELECT * FROM Songs"]
    values = []
    multiple = False
    if song_title:
        sql_statement.append(" WHERE Song LIKE ?")
        values.append("%{0}%".format(song_title))
        multiple = True
        
    if song_album and multiple:
        sql_statement.append(" AND Album LIKE ?")
        values.append("%{0}%".format(song_album))
    elif song_album and not multiple:
        sql_statement.append(" WHERE Album LIKE ?")
        values.append("%{0}%".format(song_album))
        multiple = True
        
    if song_artist and multiple:
        sql_statement.append(" AND Artist LIKE ?")
        values.append("%{0}%".format(song_artist))
    elif song_artist and not multiple:
        sql_statement.append(" WHERE Artist LIKE ?")
        values.append("%{0}%".format(song_artist))
    
    result = database.sql_execute("".join(sql_statement), values)
    if result:
        transmit = dictize_songs(result)
        return transmit
    else:
        return False

class index:
    def GET(self):
        web.setcookie("session_cookie", "", expires=-1)
        return render.index()

    def POST(self):
        mydata = local_db()
        json_data = json_parser(web.data(), song_properties)
        #print json_data
        transmit = search_songs(json_data["Song"],
                                json_data["Album"],
                                json_data["Artist"],
                                mydata.database)
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
        if session_id:
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
        if session_id:
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
    def POST(self):
        mydata = local_db()
        #beg = time.time()
        json_data = json_parser(web.data(), ["name", "password"])
        username = json_data["name"]
        password = json_data["password"]
        #print type(password)
        statement = """

        SELECT hash, salt FROM users WHERE name = ?;
        """
        
        
        result = mydata.database.sql_execute(statement, 
                                            [username])
        #print "hash access", time.time() - beg
        #beg = time.time()
        if result:

            comp_hash, salt = result[0]
            #print type(password)
        else:
            comp_hash = False
            salt = False
        
        if comp_hash and salt:
            hash = password_hash(password.encode('utf-8'),
                                 salt.encode('utf-8'))
        else:
            hash = password_hash(password.encode('utf-8'),
                                 BASESALT.encode('utf-8'))
        #print "hashing", time.time() - beg
        if hash == comp_hash:
            #beg = time.time()
            session_id = utils.id_generator()
            #print "random", time.time() - beg
            #beg = time.time()
            statement = """
            INSERT INTO cookies (username, session_id) VALUES (?, ?)
            """
            mydata.cookieDB.sql_execute(statement, [username, session_id])
            #print "cookie db", time.time() - beg
            web.setcookie("session_cookie", session_id, expires="3600")
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
        
        statement = """
        SELECT * FROM users WHERE name = ?;
        """
        
        result = mydata.database.sql_execute(statement, [json_data["name"]])
        
        if not result:
            comp_hash, salt = cred_gen(json_data["password"].encode("UTF-8"))
            statement = """
            INSERT INTO users (name, hash, salt) VALUES (?, ?, ?);
            """
            mydata.database.sql_execute(statement, [json_data["name"],
                                                    comp_hash,
                                                    salt])
            return "true"
        else:
            return "false"

class upload:
    def POST(self):
        mydata = local_db()
        session_id = web.cookies().get("session_cookie")
        #print session_id
        if session_id:
            statement = """
            SELECT username FROM cookies WHERE session_id = ?
            """
            user = mydata.cookieDB.sql_execute(statement, [session_id])[0][0]
            #print user

            playlist = web.data()
            parsed_list = utils.itune_list_parser(playlist)
            
            song_list=[]
            
            for song in parsed_list:
                name, album, artist = song
                matching = search_songs(name, album, artist, mydata.database)
                for item in matching:
                    song_list.append(item)
            #print song_list
            statement = """
            INSERT INTO playlist (name, list, owner) VALUES (?,?,?);
            """
            result = mydata.database.sql_execute(statement, 
                                                    ["list"+str(time.time()),
                                                    json.dumps(song_list),
                                                    user])

                
            
            
def header_processor(handle):
    web.header("Access-Control-Allow-Credentials", "true")
    web.header("Cache-Control", "No-Cache")
    return handle()
    
app.add_processor(header_processor)

if __name__ == "__main__":
    app.run()            
