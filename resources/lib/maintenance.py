import xbmc
import xbmcgui
import xbmcplugin
import os, sys, linecache, shutil
from pathlib import Path
import xbmcaddon
import xbmcvfs
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature, openKodiTeDB
from resources.lib.common import openKodiOutDB, translate, settings, getPythonVersion
from resources.lib.common import getDatabaseName, getmuDatabaseName, getteDatabaseName
from resources.lib.backup import backupDB
from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'


def selectMaintenance():                                           # Select database maintenance activities

    dbtype = settings('dbtype')
    mudbtype = settings('mudbtype')
    dbbkreminder = settings('dbbkreminder')
    if dbtype == 'mysql':
        kgenlog = translate(30422)
        kgenlogUpdate(kgenlog)
        xbmcgui.Dialog().ok(translate(30307), translate(30422))
        return
    try:
        while True:

            folderpath = xbmcvfs.translatePath(os.path.join("special://database/", "kscleaner/"))
            if not xbmcvfs.exists(folderpath):
                xbmcvfs.mkdir(folderpath)
                xbmc.log("KS Cleaner Backup folder not found: " +  str(folderpath), xbmc.LOGINFO)

            moptions = [translate(30417),translate(30418),translate(30419),translate(30423),translate(30424),translate(30425)]              
            ddialog = xbmcgui.Dialog()    
            mselect = ddialog.select(translate(30306) + ' - ' + translate(30613), moptions)
            if mselect < 0:                                        # User cancel
                xbmc.executebuiltin('Dialog.Close(all, true)')
                xbmc.sleep(200)
                break

            elif moptions[mselect] == translate(30417):		# Get video database statistics
                physical_size = getDBsize('video')
                xbmcgui.Dialog().ok(translate(30306) + ' - ' + translate(30417), physical_size)
                kgenlog = translate(30417) + ' - ' + physical_size.replace('\n', ' ')
                kgenlogUpdate(kgenlog)

            elif moptions[mselect] == translate(30418):		# Reindex video database
                dbMaintenance('video', 'reindex')
                if dbbkreminder == 'true':                      # Backup reminder check
                    select = xbmcgui.Dialog().yesno(translate(30418), translate(30429))
                    if select:
                        backupDB(['video']) 
                xbmcgui.Dialog().ok(translate(30306) + ' - ' + translate(30418), translate(30420))
                kgenlog = translate(30420) + ": " + getDatabaseName('local')
                kgenlogUpdate(kgenlog)                

            elif moptions[mselect] == translate(30419):		# Vacuum video database
                dbMaintenance('video', 'vacuum')
                if dbbkreminder == 'true':                      # Backup reminder check
                    select = xbmcgui.Dialog().yesno(translate(30419), translate(30429))
                    if select:
                        backupDB(['video']) 
                xbmcgui.Dialog().ok(translate(30306) + ' - ' + translate(30419), translate(30421))
                kgenlog = translate(30421) + ": " + getDatabaseName('local')
                kgenlogUpdate(kgenlog)       

            elif moptions[mselect] == translate(30423):		# Get music database statistics
                physical_size = getDBsize('music')
                xbmcgui.Dialog().ok(translate(30306) + ' - ' + translate(30423), physical_size)
                kgenlog = translate(30423) + ' - ' + physical_size.replace('\n', ' ')
                kgenlogUpdate(kgenlog)

            elif moptions[mselect] == translate(30424):		# Reindex music database
                dbMaintenance('music', 'reindex')
                if dbbkreminder == 'true':                      # Backup reminder check
                    select = xbmcgui.Dialog().yesno(translate(30424), translate(30429))
                    if select:
                        backupDB(['music']) 
                xbmcgui.Dialog().ok(translate(30306) + ' - ' + translate(30424), translate(30426))
                kgenlog = translate(30426) + ": " + getDatabaseName('local')
                kgenlogUpdate(kgenlog)       

            elif moptions[mselect] == translate(30425):		# Vacuum music database
                dbMaintenance('music', 'vacuum')
                if dbbkreminder == 'true':                      # Backup reminder check
                    select = xbmcgui.Dialog().yesno(translate(30425), translate(30429))
                    if select:
                        backupDB(['music']) 
                xbmcgui.Dialog().ok(translate(30306) + ' - ' + translate(30425), translate(30427))
                kgenlog = translate(30427) + ": " + getDatabaseName('local')
                kgenlogUpdate(kgenlog)       

            else:
                kgenlog = 'User selected maintenance activity: ' + moptions[mselect]
                kgenlogUpdate(kgenlog)
                xbmc.executebuiltin('Dialog.Close(all, true)')
                xbmc.sleep(200)                

     

    except Exception as e:
        printexception()


def getDBsize(database):					#  Get database physical and logical sizes

        if database == 'video':
            dbfile = os.path.join(xbmcvfs.translatePath("special://database"), getDatabaseName('local'))
            db = openKodiDB('local')
        elif database == 'music':
            dbfile = os.path.join(xbmcvfs.translatePath("special://database"), getmuDatabaseName('local'))
            db = openKodiMuDB('local')

        xbmc.log("KS Cleaner dbfile name: " +  str(dbfile), xbmc.LOGDEBUG)        
        database_bytes = os.path.getsize(dbfile)
        database_mb = database_bytes / (1024 * 1024)
        database_mb_text = f"Physical file size: {database_mb:.2f} MB"
        xbmc.log("KS Cleaner dbfile size: " +  database_mb_text, xbmc.LOGDEBUG)   

        dbstuple = db.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();")
        dbftuple = db.execute("SELECT (page_count - freelist_count) * page_size FROM pragma_page_count(),       \
        pragma_freelist_count(), pragma_page_size();")
        logical_bytes = dbstuple.fetchone()[0]
        logical_used_bytes = dbftuple.fetchone()[0]
        db.close()

        logical_mb = logical_bytes / (1024 * 1024)
        logical_mb_text = f"Logical DB size: {logical_mb:.2f} MB"   

        logical_used_mb = logical_used_bytes / (1024 * 1024)
        logical_used_mb_text = f"Logical DB used: {logical_used_mb:.2f} MB"  

        db_usage = (logical_mb / logical_used_mb) * 100
        db_usage_text = f"Database usage: {db_usage:.2f} %"      

        return database_mb_text + '\n' + logical_mb_text + '\n' + logical_used_mb_text + '\n' + db_usage_text


def dbMaintenance(database, action):					#  Kodi database maintenance

        if database == 'video':
            db = openKodiDB('local')
        elif database == 'music':
            db = openKodiMuDB('local')
        
        if action == 'reindex':
            db.execute('REINDEX',)
        elif action == 'vacuum':
            db.execute('VACUUM',)
        db.commit()    
        db.close()  




