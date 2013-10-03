from nose.tools import*
import MusicShare.utils as utils
import math

def setup():
    print "SETUP!"
    
def teardown():
    print "TEAR DOWN!"
    
def test_basic():
    print "I RAN!"

def itune_test():
    zzz = open("Punk _ Rock.txt", "r")
    songs = utils.itune_list_parser(zzz.read())
    print songs[0]
    assert_true(songs[0] == ("I'm Picky", "The Geeks and the Jerkin' Socks", "Shaka Ponk"))
    zzz.close()
    
def id_generator_test():
    count = 100
    zzz = utils.id_generator(size=count)
    #zzz = 150*"a"
    #raise Exception(zzz)
    assert_true(len(zzz) > count)
    total = len(zzz)
    byte_counts = {}
    for byte in zzz:
        if hasattr(byte_counts, byte):
            byte_counts[byte] += 1
        else:
            byte_counts[byte] = 1
    entropy = 0
    for count in byte_counts.values():
        p = 1.0 * count / total
        entropy -= p*math.log(p, 256)
    assert_true(entropy > 0)

def conversion_test():
    size_list = []
    for i in xrange(0, 5):
        size_list.append(utils.conversion_soft(10**(i*3)))
    unit_comp_list = []
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    for unit in units:
        unit_comp_list.append("1.0 "+unit)
    #raise Exception(unit_comp_list, size_list)
    for i in xrange(0, 5):
        assert_true(unit_comp_list[0] == size_list[0])
        
def db_test():
    test_db = "/Users/Antoine/Documents/Pn/projects/databases/testing.db"
    db = utils.simple_db(test_db)
    with open("schema.sql", 'r') as c:
        res = db.sql_script(c.read())
    to_insert = [u"un tel", u"an hash", u"zzz"]
    db.sql_execute("insert into users (name, hash, salt) values (?, ?, ?)", to_insert)
    res = db.sql_execute("select * from users", [])[0]
    res = list(res)
    res.pop(0)
    for i in xrange(0, 2):
        assert_true(res[i] == to_insert[i])
    db.exit()