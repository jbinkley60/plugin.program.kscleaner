import xbmc
import xbmcgui
import xbmcplugin
import os, sys, linecache
from pathlib import Path
import xbmcaddon
import xbmcvfs
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature, openKodiTeDB
from resources.lib.common import openKodiOutDB, translate, settings
from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'


def backupDB(selectdbs):                                          # Database backup menu

    try:

        #xbmc.log("KS Cleaner backup selectable is: " +  str(selectdbs), xbmc.LOGNINFO)
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
            dbout = openKodiOutDB('video')                       # open output
            dbin = openKodiDB()                                  # open input
            with dbout[0]:
                dbin.backup(dbout[0], pages=100)
            dbout[0].close()
            dbin.close()
            dbscompleted += 1
            checkBackups(dbout[2], 'MyVideos')                   # Limit number of backups
            kgenlog ='Kodi Video Database backup successful: ' + dbout[1].split('/')[1]
            kgenlogUpdate(kgenlog)
            kscprogress.update(int(float(dbscompleted / dbslength) * 100), translate(30328))
            xbmc.sleep(2000) 

        if 'music' in selectdbs:                                 # Music database backup
            dbout = openKodiOutDB('music')                       # open output
            dbin = openKodiMuDB()                                # open input
            with dbout[0]:
                dbin.backup(dbout[0], pages=100)
            dbout[0].close()
            dbin.close()
            dbscompleted += 1
            checkBackups(dbout[2], 'MyMusic')                    # Limit number of backups
            kgenlog ='Kodi Music Database backup successful: ' + dbout[1].split('/')[1]
            kgenlogUpdate(kgenlog)
            kscprogress.update(int(float(dbscompleted / dbslength) * 100), translate(30329))
            xbmc.sleep(2000) 

        if 'texture' in selectdbs:                               # Textures database backup
            dbout = openKodiOutDB('texture')                     # open output
            dbin = openKodiTeDB()                                # open input
            with dbout[0]:
                dbin.backup(dbout[0], pages=100)
            dbout[0].close()
            dbin.close()
            dbscompleted += 1
            checkBackups(dbout[2], 'Textures')                   # Limit number of backups
            kgenlog ='Kodi Textures Database backup successful: ' + dbout[1].split('/')[1] 
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


def selectBackups():                                            # Select databases to backup

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

