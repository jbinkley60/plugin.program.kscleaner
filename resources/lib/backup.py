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
from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'


def backupDB(selectdbs):                                         # Database backup menu

    dbtype = settings('dbtype')
    mudbtype = settings('mudbtype')
    backtype = 'normal'
    if dbtype == 'mysql' or mudbtype == 'mysql':
        nofeature()
        return

    pyver = getPythonVersion()                                   # Determine backup type by Python version
    pyversion = pyver.split('.')
    if int(pyversion[0]) < 3:                                    # Python 2 not supported
        nofeature() 
        return
    elif int(pyversion[0]) == 3 and int(pyversion[1]) <= 6:      # File backups for Python 3.6 and below
        backtype = 'file'

    kgenlog = 'Kodi Selective Cleaner backup type is: ' + backtype
    kgenlogUpdate(kgenlog)             

    try:
        dbpath = os.path.join(xbmcvfs.translatePath("special://database"), 'kscleaner')
        xbmc.log("KS Cleaner backup selectable is: " +  str(selectdbs), xbmc.LOGINFO)
        dbslength = len(selectdbs)
        dbscompleted = 0
        if dbslength > 0:
            kscprogress = xbmcgui.DialogProgress()
            dialoghead = translate(30306) + ' - ' + translate(30332)
            dialogmsgs = translate(30333) 
            kscprogress.create(dialoghead, dialogmsgs)
            xbmc.sleep(2000) 
        else:
            return

        folderpath = 'kodi/userdata/Database/kscleaner/'

        if 'video' in selectdbs:                                 # Video database backup
            if backtype == 'file':
                dbout = openKodiOutDB('video', 'yes')            # open output file copy mode
                infile = os.path.join(xbmcvfs.translatePath("special://database"), getDatabaseName('local'))
                shutil.copyfile(infile, dbout[3])
                #xbmc.log("KS Cleaner fileinfo is: " +  infile + ' ' + str(dbout[3]), xbmc.LOGINFO)
            else:
                dbout = openKodiOutDB('video')                   # open output
                dbin = openKodiDB(dbtype)                        # open input
                with dbout[0]:
                    dbin.backup(dbout[0], pages=100)
                dbout[0].close()
                dbin.close()
            dbscompleted += 1
            checkBackups(dbout[2], 'MyVideos')                   # Limit number of backups
            kgenlog ='Kodi Video DB backup successful: ' + dbout[1].split('/')[1]
            kgenlogUpdate(kgenlog)
            kscprogress.update(int(float(dbscompleted / dbslength) * 100), translate(30328))
            xbmc.sleep(2000) 

        if 'music' in selectdbs:                                 # Music database backup
            if backtype == 'file':
                dbout = openKodiOutDB('music', 'yes')            # open output file copy mode
                infile = os.path.join(xbmcvfs.translatePath("special://database"), getmuDatabaseName('local'))
                shutil.copyfile(infile, dbout[3])
                #xbmc.log("KS Cleaner fileinfo is: " +  infile + ' ' + str(dbout[3]), xbmc.LOGINFO)
            else:
                dbout = openKodiOutDB('music')                   # open output
                dbin = openKodiMuDB(mudbtype)                    # open input
                with dbout[0]:
                    dbin.backup(dbout[0], pages=100)
                dbout[0].close()
                dbin.close()
            dbscompleted += 1
            checkBackups(dbout[2], 'MyMusic')                    # Limit number of backups
            kgenlog ='Kodi Music DB backup successful: ' + dbout[1].split('/')[1]
            kgenlogUpdate(kgenlog)
            kscprogress.update(int(float(dbscompleted / dbslength) * 100), translate(30329))
            xbmc.sleep(2000) 

        if 'texture' in selectdbs:                               # Textures database backup
            if backtype == 'file':
                dbout = openKodiOutDB('texture', 'yes')          # open output file copy mode
                infile = os.path.join(xbmcvfs.translatePath("special://database"), getteDatabaseName())
                shutil.copyfile(infile, dbout[3])
                #xbmc.log("KS Cleaner fileinfo is: " +  infile + ' ' + str(dbout[3]), xbmc.LOGINFO)
            else:
                dbout = openKodiOutDB('texture')                 # open output 
                dbin = openKodiTeDB()                            # open input
                with dbout[0]:
                    dbin.backup(dbout[0], pages=100)
                dbout[0].close()
                dbin.close()
            dbscompleted += 1
            checkBackups(dbout[2], 'Textures')                   # Limit number of backups
            kgenlog ='Kodi Textures DB backup successful: ' + dbout[1].split('/')[1] 
            kgenlogUpdate(kgenlog)
            kscprogress.update(int(float(dbscompleted / dbslength) * 100), translate(30330))
            xbmc.sleep(2000) 

        if dbslength > 0:
            kscprogress.close()

        outmsg = folderpath
        dialog_text = translate(30335) + outmsg 
        xbmcgui.Dialog().ok(translate(30306), dialog_text)


    except Exception as e:
        printexception()
        kgenlog = translate(30334)
        xbmcgui.Dialog().notification(translate(30308), kgenlog, addon_icon, 5000)            
        kgenlogUpdate(kgenlog)


def selectBackups():                                           # Select databases to backup

    dbtype = settings('dbtype')
    mudbtype = settings('mudbtype')
    if dbtype == 'mysql' or mudbtype == 'mysql':
        nofeature()
        return
    try:
        while True:

            folderpath = xbmcvfs.translatePath(os.path.join("special://database/", "kscleaner/"))
            if not xbmcvfs.exists(folderpath):
                xbmcvfs.mkdir(folderpath)
                xbmc.log("KS Cleaner Backup folder not found: " +  str(folderpath), xbmc.LOGINFO)

            stable = []
            selectbl = []
            tables = [translate(30328),translate(30329),translate(30330)]              
            ddialog = xbmcgui.Dialog()    
            stable = ddialog.multiselect(translate(30306) + ' - ' + translate(30331), tables)
            if stable == None:                                 # User cancel
                break
            if 0 in stable:
                selectbl.append('video')
            if 1 in stable:
               selectbl.append('music')   
            if 2 in stable:
                selectbl.append('texture')
            backupDB(selectbl)         

    except Exception as e:
        printexception()


def checkBackups(fpath, fname):                              #  Check for proper number of backups

    try:
        backcount = settings('backcount')
        if int(backcount) == 0:                              #  Keep infinite copies
            return
        paths = sorted(Path(fpath).iterdir(), key=os.path.getmtime, reverse=True)
        count = 0
        for p in range(0, len(paths)):
            if fname in str(paths[p]):
                count += 1
                if count > int(backcount):
                    try:
                        fremove = str(paths[p]).lstrip(fpath)
                        os.remove(str(paths[p]))
                        kgenlog = 'Old backup file successfully deleted: ' + fremove
                        kgenlogUpdate(kgenlog) 
                    except Exception as e:
                        kgenlog = 'There was a problem deleting an old backup.' + fremove           
                        kgenlogUpdate(kgenlog)
                        printexception()                        

    except Exception as e:
        kgenlog = 'There was a problem with the Backup Checker.  See kodi.log file.'           
        kgenlogUpdate(kgenlog)
        printexception()           

