import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import os, sys, linecache, os.path
import json
from datetime import datetime
import mysql.connector
from mysql.connector import errorcode
import xml.etree.ElementTree as ET


def settings(setting, value = None):
    # Get or add addon setting
    if value:
        xbmcaddon.Addon().setSetting(setting, value)
    else:
        return xbmcaddon.Addon().getSetting(setting)  


def getPythonVersion():                 # get Python version

    pythinfo = sys.version_info
    pythver = str(pythinfo[0]) + '.' + str(pythinfo[1]) + '.' + str(pythinfo[2])
    kgenlog = 'Kodi Selective Cleaner Python vesion is: ' + pythver
    kgenlogUpdate(kgenlog)
    return pythver
 

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


def getDatabaseName(dbtype):
    installed_version = get_installedversion()
    if installed_version == '19' and dbtype == 'local':
        return "MyVideos119.db"
    elif installed_version == '19' and dbtype == 'mysql':
        return "119"
    elif installed_version == '20'  and dbtype == 'local':
        return "MyVideos121.db"
    elif installed_version == '20' and dbtype == 'mysql':
        return "121"
    elif installed_version == '21'  and dbtype == 'local':
        return "MyVideos131.db"
    elif installed_version == '21' and dbtype == 'mysql':
        return "131"
       
    return "" 


def getmuDatabaseName(dbtype):
    installed_version = get_installedversion()
    if installed_version == '19' and dbtype == 'local':
        return "MyMusic82.db"
    elif installed_version == '19' and dbtype == 'mysql':
        return "82"
    elif installed_version == '20'  and dbtype == 'local':
        return "MyMusic82.db"
    elif installed_version == '20' and dbtype == 'mysql':
        return "82"
    elif installed_version == '21'  and dbtype == 'local':
        return "MyMusic83.db"
    elif installed_version == '21' and dbtype == 'mysql':
        return "83"      
    return ""  


def getteDatabaseName():
    installed_version = get_installedversion()
    if installed_version == '19':
        return "Textures13.db"
    elif installed_version == '20':
        return "Textures13.db"
    elif installed_version == '21':
        return "Textures13.db"   
    
    return ""  


def parseConfig(config_file, database, dbtype):

    try:
        #tree = ET.parse(config_file)
        with open(file=config_file, mode='r', encoding='utf-8-sig') as xml_txt:                 
            tree = ET.fromstring((xml_txt.read().replace('&',' ').strip().encode('utf-8')), ET.XMLParser(encoding='utf-8'))

        if database == 'video':
            vconfig = tree.find('videodatabase')
            host = port = user = passw = type = ''
            if vconfig.find('type') != None:
                type = vconfig.find('type').text
            if type == None or type.lower() != 'mysql':
                kgenlog = translate(30395)
                kgenlogUpdate(kgenlog)
                xbmcgui.Dialog().ok(translate(30308), kgenlog)
                return None
            if vconfig.find('host') != None:
                host = vconfig.find('host').text
            if host == None or len(host) < 4:
                kgenlog = translate(30391)
                kgenlogUpdate(kgenlog)
                xbmcgui.Dialog().ok(translate(30308), kgenlog)
                return None
            if vconfig.find('port') != None:
                port = vconfig.find('port').text
            if port == None or len(port) < 3:
                kgenlog = translate(30392)
                kgenlogUpdate(kgenlog)
                xbmcgui.Dialog().ok(translate(30308), kgenlog)
                return None
            if vconfig.find('user') != None:
                user = vconfig.find('user').text
            if user == None or len(user) < 4:
                kgenlog = translate(30393)
                kgenlogUpdate(kgenlog)
                xbmcgui.Dialog().ok(translate(30308), kgenlog)
                return None                         
            if vconfig.find('pass') != None:
                passw = vconfig.find('pass').text
            if passw == None or len(passw) < 4:
                kgenlog = translate(30394)
                kgenlogUpdate(kgenlog)
                xbmcgui.Dialog().ok(translate(30308), kgenlog)
                return None
            dbname = None 
            if vconfig.find('name') != None:
                dbname = vconfig.find('name').text
            dbver = getDatabaseName(dbtype)
            if settings('dbvidname') != 'Default':
                dbname = settings('dbvidname') 
            elif dbname != None:
                dbname = dbname + dbver
            else:
                dbname = 'MyVideos' + dbver
            xbmc.log('KS Cleaner parse:' + ' ' + type + ' ' + host + ' ' + port + ' ' + user + ' ' \
            + passw + ' ' + dbname , xbmc.LOGDEBUG)
            config = {
                     'user': user,
                     'password': passw,
                     'host': host,
                     'port': port,
                     'database': dbname,
                     'raise_on_warnings': True
                     }
            return config

        elif database == 'music':
            mconfig = tree.find('musicdatabase')
            host = port = user = passw = type = ''
            if mconfig.find('type') != None:
                type = mconfig.find('type').text
            if type == None or type.lower() != 'mysql':
                kgenlog = translate(30400)
                kgenlogUpdate(kgenlog)
                xbmcgui.Dialog().ok(translate(30308), kgenlog)
                return None
            if mconfig.find('host') != None:
                host = mconfig.find('host').text
            if host == None or len(host) < 4:
                kgenlog = translate(30396)
                kgenlogUpdate(kgenlog)
                xbmcgui.Dialog().ok(translate(30308), kgenlog)
                return None
            if mconfig.find('port') != None:
                port = mconfig.find('port').text
            if port == None or len(port) < 3:
                kgenlog = translate(30397)
                kgenlogUpdate(kgenlog)
                xbmcgui.Dialog().ok(translate(30308), kgenlog)
                return None
            if mconfig.find('user') != None:
                user = mconfig.find('user').text
            if user == None or len(user) < 4:
                kgenlog = translate(30398)
                kgenlogUpdate(kgenlog)
                xbmcgui.Dialog().ok(translate(30308), kgenlog)
                return None                         
            if mconfig.find('pass') != None:
                passw = mconfig.find('pass').text
            if passw == None or len(passw) < 4:
                kgenlog = translate(30399)
                kgenlogUpdate(kgenlog)
                xbmcgui.Dialog().ok(translate(30308), kgenlog)
                return None
            dbname = None  
            if mconfig.find('name') != None:
                dbname = mconfig.find('name').text
            dbver = getmuDatabaseName(dbtype)
            if settings('dbmusname') != 'Default':
                dbname = settings('dbmusname') 
            elif dbname != None:
                dbname = dbname + dbver
            else:
                dbname = 'MyMusic' + dbver
            xbmc.log('KS Cleaner parse:' + ' ' + type + ' ' + host + ' ' + port + ' ' + user + ' ' \
            + passw + ' ' + dbname , xbmc.LOGDEBUG)
            config = {
                     'user': user,
                     'password': passw,
                     'host': host,
                     'port': port,
                     'database': dbname,
                     'raise_on_warnings': True
                     }
            return config

    except:
        printexception()
        kgenlog = "There is a problem with your MySQL configuration"
        kgenlogUpdate(kgenlog)
        xbmcgui.Dialog().ok(translate(30308), translate(30368))
        return None


def openKodiDB(dbtype):                               #  Open Kodi database

    if dbtype == 'local':
        try:
            from sqlite3 import dbapi2 as sqlite
        except:
            from pysqlite2 import dbapi2 as sqlite
                      
        DB = os.path.join(xbmcvfs.translatePath("special://database"), getDatabaseName(dbtype))
        db = sqlite.connect(DB)

        return(db)

    elif dbtype == 'mysql':
        try:
            config_file = os.path.join(xbmcvfs.translatePath("special://profile"), 'advancedsettings.xml')
            if not os.path.isfile(config_file):
                 kgenlog = "File not found: " + config_file
                 kgenlogUpdate(kgenlog)
                 xbmcgui.Dialog().ok(translate(30308), translate(30374))
            else:
                 #kgenlog = "MySQL format selected.  Settings file found for Video database"
                 #kgenlogUpdate(kgenlog)
                 config = parseConfig(config_file, 'video', dbtype)
                 if config == None:
                    kgenlog = "There is a problem opening your MySQL video database. "
                    kgenlogUpdate(kgenlog)
                    xbmcgui.Dialog().ok(translate(30303), translate(30372))
                    return                 
                 try:
                     db = mysql.connector.connect(**config)
                     return (db)
                 except mysql.connector.Error as err:
                     if err.errno == 1045:
                         kgenlog = "KS Cleaner MySQL server userid / password error: " + config['user']
                         xbmcgui.Dialog().ok(translate(30308), kgenlog)
                         kgenlogUpdate(kgenlog)
                     elif err.errno == 1049:
                         kgenlog = "KS Cleaner MySQL server database not found: " + config['database']
                         xbmcgui.Dialog().ok(translate(30308), kgenlog)
                         kgenlogUpdate(kgenlog)
                     elif err.errno == 2003:
                         kgenlog = "KS Cleaner could not connect to your MySQL server: " + config['host']
                         xbmcgui.Dialog().ok(translate(30308), kgenlog)
                         kgenlogUpdate(kgenlog)                   
                     else:
                         kgenlog = "KS Cleaner could not connect to your MySQL server " + config['host']
                         xbmcgui.Dialog().ok(translate(30308), kgenlog)
                         kgenlog = 'KS Cleaner MySQL error: ' + str(err)
                         kgenlogUpdate(kgenlog)
                 
        except:
            printexception()
            kgenlog = "There is a problem opening your MySQL video database. "
            kgenlogUpdate(kgenlog)
            xbmcgui.Dialog().ok(translate(30303), translate(30372))


def openKodiMuDB(dbtype):                           #  Open Kodi music database

    if dbtype == 'local':
        try:
            from sqlite3 import dbapi2 as sqlite
        except:
            from pysqlite2 import dbapi2 as sqlite
                      
        DB = os.path.join(xbmcvfs.translatePath("special://database"), getmuDatabaseName(dbtype))
        db = sqlite.connect(DB)

        return(db)  

    elif dbtype == 'mysql':
        try:
            config_file = os.path.join(xbmcvfs.translatePath("special://profile"), 'advancedsettings.xml')
            if not os.path.isfile(config_file):
                 kgenlog = "File not found: " + config_file
                 kgenlogUpdate(kgenlog)
                 xbmcgui.Dialog().ok(translate(30308), translate(30374))
            else:
                 #kgenlog = "MySQL format selected.  Settings file found  for Music database"
                 #kgenlogUpdate(kgenlog)
                 config = parseConfig(config_file, 'music', dbtype)
                 if config == None:
                    kgenlog = "There is a problem opening your MySQL music database."
                    kgenlogUpdate(kgenlog)
                    xbmcgui.Dialog().ok(translate(30308), translate(30373))
                    return
                 try:
                     db = mysql.connector.connect(**config)
                     return (db)
                 except mysql.connector.Error as err:
                     if err.errno == 1045:
                         kgenlog = "KS Cleaner MySQL server userid / password error: " + config['user']
                         xbmcgui.Dialog().ok(translate(30308), kgenlog)
                         kgenlogUpdate(kgenlog)
                     elif err.errno == 1049:
                         kgenlog = "KS Cleaner MySQL server database not found: " + config['database']
                         xbmcgui.Dialog().ok(translate(30308), kgenlog)
                         kgenlogUpdate(kgenlog)
                     elif err.errno == 2003:
                         kgenlog = "KS Cleaner could not connect to your MySQL server: " + config['host']
                         xbmcgui.Dialog().ok(translate(30308), kgenlog)
                         kgenlogUpdate(kgenlog)                   
                     else:
                         kgenlog = "KS Cleaner could not connect to your MySQL server " + config['host']
                         xbmcgui.Dialog().ok(translate(30308), kgenlog)
                         kgenlog = 'KS Cleaner MySQL error: ' + str(err)
                         kgenlogUpdate(kgenlog)
                 
        except:
            printexception()
            kgenlog = "There is a problem opening your MySQL music database."
            kgenlogUpdate(kgenlog)
            xbmcgui.Dialog().ok(translate(30308), translate(30373))


def openKodiTeDB():                                  #  Open Kodi textures database
    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite
                      
    DB = os.path.join(xbmcvfs.translatePath("special://database"), getteDatabaseName())
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


def openKodiOutDB(dbtype, fcopy='no'):                    #  Open Kodi output database
    try:
        from sqlite3 import dbapi2 as sqlite
    except:
        from pysqlite2 import dbapi2 as sqlite

    fpart = 'kscleaner/' + datetime.now().strftime('%m%d%Y-%H%M%S') + '_'  

    if dbtype == 'video':                  
        ppart = fpart + getDatabaseName('local')
    elif dbtype == 'music':
        ppart = fpart + getmuDatabaseName('local')
    elif dbtype == 'texture':
        ppart = fpart + getteDatabaseName()

    DB = os.path.join(xbmcvfs.translatePath("special://database"), ppart)
    dbpath = os.path.join(xbmcvfs.translatePath("special://database"), 'kscleaner')
    if fcopy == 'no':
        db = sqlite.connect(DB)
    else:
        db = ''
    return[db, ppart, dbpath, DB]   
 

def checkKscleanDB():                                   #  Verify Kscleaner database

    try:
        dbsync = openKscleanDB()

        dbsync.execute('CREATE table IF NOT EXISTS kscleanLog (kgDate TEXT, kgTime TEXT,   \
        kgGenDat TEXT, extVar1 TEXT, extVar2 TEXT )')
        dbsync.execute('CREATE INDEX IF NOT EXISTS kgen_1 ON kscleanLog (kgDate)') 

        dblimit1 = 10000
        dbsync.execute('delete from kscleanLog where kgDate not in (select kgDate from  \
        kscleanLog order by kgDate desc limit ?)', (dblimit1,))

        dbsync.commit()
        dbsync.execute('REINDEX',)
        dbsync.execute('VACUUM',)
        dbsync.commit()
        dbsync.close()

        kgenlog ='KS Cleaner logging database check successful.  Addon started.'
        kgenlogUpdate(kgenlog)
        getPythonVersion()
        installver = get_installedversion()
        kgenlog ='KS Cleaner Kodi version detected: ' + installver
        kgenlogUpdate(kgenlog)

    except Exception as e:
        xbmc.log('KS Cleaner logging database check error.', xbmc.LOGERROR)
        printexception()


def kgenlogUpdate(kgenlog, kdlog = 'Yes', dbfile = None):  #  Add logs to DB

    try:
        if kdlog == 'Yes':                               #  Write to Kodi logfile
            xbmc.log(kgenlog, xbmc.LOGINFO)
        if dbfile != None:                               #  DB handle passed for faster cleaning
            mgfile = dbfile
        else:
            mgfile = openKscleanDB()                     #  Open Kscleaner log database

        currmsDate = datetime.now().strftime('%Y-%m-%d')
        currmsTime = datetime.now().strftime('%H:%M:%S:%f')
        mgfile.execute('INSERT into kscleanLog(kgDate, kgTime, kgGenDat) values (?, ?, ?)',                \
        (currmsDate, currmsTime, kgenlog))

        if dbfile == None:                              # Commit and close if not cleaning   
            mgfile.commit()
            mgfile.close()
    except Exception as e:
        xbmc.log('KS cleaner problem writing to general log DB: ' + str(e), xbmc.LOGERROR)


def tempDisplay(vtable, vheader = '', counts = ''):

    try:        
        tempdb = openKscleanDB()
        curr = tempdb.execute('SELECT comments FROM vdb_temp')
        mglogs = curr.fetchall()                                     # Get logs from database
        msdialog = xbmcgui.Dialog()
        headval = "{:^128}".format(translate(30306))
        if len(vheader) == 0:        
            textval1 = "{:^128}".format(translate(30357) + ' - ' + vtable )
        else:
            #textval1 = "{:^128}".format(translate(30357) + ' - ' + vtable )  + '\n\n' + vheader
            textval1 = "{:>72}".format(translate(30357) + ' - ' + vtable ) + '\n'  
            textval1 = textval1 + '[COLOR blue]' + "{:>48}".format('Clean Count: ' + counts[1]) + '[/COLOR]'
            textval1 = textval1 + "{:>32}".format('Data Integrity Count: ' + counts[0]) + '\n\n' + vheader
        textval1 = textval1 + '\n' 

        if mglogs:
            for a in range(len(mglogs)):                              # Display logs if exist   
                mcomment = mglogs[a][0]
                textval1 = textval1 + "\n" + mcomment
            msdialog.textviewer(headval, textval1)                                     
        else:                                                         # No records found for date selected   
            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30312)        
            perfdialog.ok(translate(30308), dialog_text)     
        tempdb.close()
        return

    except Exception as e:
        xbmc.log('KS Cleaner logging database check error.', xbmc.LOGERROR)
        printexception()




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