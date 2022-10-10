import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import os, sys, linecache
import json
from datetime import datetime


def settings(setting, value = None):
    # Get or add addon setting
    if value:
        xbmcaddon.Addon().setSetting(setting, value)
    else:
        return xbmcaddon.Addon().getSetting(setting)   

def translate(text):
    return xbmcaddon.Addon().getLocalizedString(text)

def get_installedversion():
    # retrieve current installed version
    json_query = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
    json_query = json.loads(json_query)
    version_installed = []
    if 'result' in json_query and 'version' in json_query['result']:
        version_installed  = json_query['result']['version']['major']
    return str(version_installed)


def getDatabaseName():
    installed_version = get_installedversion()
    if installed_version == '18':
        return "MyVideos116.db"
    elif installed_version == '19':
        return "MyVideos119.db"
    elif installed_version == '20':
        return "MyVideos121.db"
       
    return "" 


def getmuDatabaseName():
    installed_version = get_installedversion()
    if installed_version == '18':
        return "MyMusic72.db"
    elif installed_version == '19':
        return "MyMusic82.db"
    elif installed_version == '20':
        return "MyMusic82.db"
       
    return ""  


def openKodiDB():                                   #  Open Kodi database
    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite
                      
    DB = os.path.join(xbmcvfs.translatePath("special://database"), getDatabaseName())
    db = sqlite.connect(DB)

    return(db)    


def openKodiMuDB():                                  #  Open Kodi music database
    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite
                      
    DB = os.path.join(xbmcvfs.translatePath("special://database"), getmuDatabaseName())
    db = sqlite.connect(DB)

    return(db)  


def openKscleanDB():                                 #  Open Kscleaner database
    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite
                      
    DBconn = os.path.join(xbmcvfs.translatePath("special://database"), "Ksclean10.db")  
    dbsync = sqlite.connect(DBconn)

    return(dbsync) 
 

def checkKscleanDB():                                   #  Verify Kscleaner database

    try:
        dbsync = openKscleanDB()

        dbsync.execute('CREATE table IF NOT EXISTS kscleanLog (kgDate TEXT, kgTime TEXT,   \
        kgGenDat TEXT, extVar1 TEXT, extVar2 TEXT )')
        dbsync.execute('CREATE INDEX IF NOT EXISTS kgen_1 ON kscleanLog (kgDate)')  

        dbsync.commit()
        dbsync.close()
        kgenlog ='KS Cleaner logging database check successful.  Addon started.'
        kgenlogUpdate(kgenlog)

    except Exception as e:
        xbmc.log('KS Cleaner logging database check error.', xbmc.LOGERROR)
        printexception()


def kgenlogUpdate(kgenlog):                              #  Add logs to DB

    try:

        xbmc.log(kgenlog, xbmc.LOGINFO)
        mgfile = openKscleanDB()                         #  Open Kscleaner log database

        currmsDate = datetime.now().strftime('%Y-%m-%d')
        currmsTime = datetime.now().strftime('%H:%M:%S:%f')
        mgfile.execute('INSERT into kscleanLog(kgDate, kgTime, kgGenDat) values (?, ?, ?)',                \
        (currmsDate, currmsTime, kgenlog))
     
        mgfile.commit()
        mgfile.close()
    except Exception as e:
        xbmc.log('KS cleaner problem writing to general log DB: ' + str(e), xbmc.LOGERROR)


def nofeature(note = ' '):

    dialog_text = translate(30307) + ' ' + str(note)
    xbmcgui.Dialog().ok(translate(30306), dialog_text)


def printexception():

    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    xbmc.log( 'EXCEPTION IN ({0}, LINE {1} "{2}"): {3}'.format(filename, lineno, line.strip(),     \
    exc_obj), xbmc.LOGERROR)