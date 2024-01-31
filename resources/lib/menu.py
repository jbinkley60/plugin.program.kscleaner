import xbmc
import xbmcgui
import xbmcplugin
import os
import xbmcaddon
import xbmcvfs
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception, translate
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature, settings
from resources.lib.logs import displayGenLogs
from resources.lib.tvshows import displayTvshows
from resources.lib.movies import displayMovieMenu
from resources.lib.mvideos import displayMvideos
from resources.lib.music import displayMmusic
from resources.lib.exports import selectExport
from resources.lib.backup import selectBackups
from resources.lib.vanalyze import vanalMenu
from resources.lib.mutriggers import checkMuTriggers
import mysql.connector

from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'

def displayMenu():                                              # Display menu 

    menuitem1 = translate(30300)
    menuitem2 = translate(30301)
    menuitem3 = translate(30302)
    menuitem4 = translate(30303) 
    menuitem5 = translate(30304)
    menuitem6 = translate(30317)
    menuitem7 = translate(30305)
    menuitem8 = translate(30338)
    menuitem9 = translate(30339)    

    while True:
        try:
            dbtype = settings('dbtype')
            mudbtype = settings('mudbtype')
            kvfile = openKodiDB(dbtype)                          # Open Kodi video database
            kmfile = openKodiMuDB(mudbtype)                      # Open Kodi music database
            kcursor = kmcursor = 0
            if not kvfile or not kmfile:
                break
            kcfile = openKscleanDB()                             # Open Kscleaner database
            pselect = []
            mvquery = "SELECT COUNT(c00) FROM movie"
            if dbtype == 'mysql':
                kcursor = kvfile.cursor()
                kcursor.execute(mvquery)
                kmovies = kcursor.fetchone()[0]                  # Get movies from video database
            else: 
                curpf = kvfile.execute(mvquery)
                kmovies = curpf.fetchone()[0]                    # Get movies from video database
            xbmc.log('Kodi selective cleaner movie count: ' + str(kmovies), xbmc.LOGDEBUG)
            if int(kmovies) > -1 :                               # If movies in video database
                pselect.append(str(menuitem1)  + '\t\t  -  ' + str(kmovies) + '  ' + translate(30327))

            mtquery = "SELECT count(c00) FROM tvshow"
            if dbtype == 'mysql':
                kcursor.execute(mtquery)
                ktvshows = kcursor.fetchone()[0]                 # Get tvshows from video database
            else:
                curpf = kvfile.execute(mtquery)
                ktvshows = curpf.fetchone()[0]                   # Get tvshows from video database
            xbmc.log('Kodi selective cleaner TV show count: ' + str(ktvshows), xbmc.LOGDEBUG)
            if int(ktvshows) > -1 :                              # If tvshows in video database
                pselect.append(str(menuitem2)  + '\t\t  -  ' + str(ktvshows) + '  ' + translate(30327))

            msquery = "SELECT count(c00) FROM musicvideo"
            if dbtype == 'mysql':
                kcursor.execute(msquery)
                kmvideos = kcursor.fetchone()[0]                 # Get tvshows from video database
            else:
                curpf = kvfile.execute(msquery)
                kmvideos = curpf.fetchone()[0]                   # Get musicvideos from video database 
            if int(kmvideos) > -1 :                              # If musicvideos in video database
                pselect.append(str(menuitem3)  + '\t  -  ' + str(kmvideos) + '  ' + translate(30327))

            mmquery = "SELECT count(strAlbum) FROM album"
            if mudbtype == 'mysql':
                kmcursor = kmfile.cursor()
                kmcursor.execute(mmquery)
                kmusic = kmcursor.fetchone()[0]                   # Get albums from music database
            else:
                curpf = kmfile.execute(mmquery)
                kmusic = curpf.fetchone()[0]                      # Get albums from music database
            if int(kmusic) > -1 :                                 # If albums in music database
                pselect.append(str(menuitem4)  + '\t\t  -  ' + str(kmusic) + '  ' + translate(30327))

            pselect.extend([menuitem8, menuitem9])               # Add analyzer menu options

            curpf = kcfile.execute('SELECT count (kgGenDat) FROM kscleanLog', )
            kslog = curpf.fetchone()[0]                          # Get logs from logging database
            if int(kslog) > -1:                                  # If logs in logging database
                pselect.append(menuitem5)     

            pselect.extend([menuitem6, menuitem7])

            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306), pselect)
            xbmc.log('Kodi selective cleaner selection is: ' + pselect[vdate], xbmc.LOGDEBUG)
            del curpf
            if kcursor:
                kcursor.close()
            if kmcursor:
                kmcursor.close()      
            kvfile.close()
            kcfile.close()
            kmfile.close()     
        except Exception as e:
            xbmc.log('KS Cleaner main menu error. ', xbmc.LOGERROR)
            del curpf             
            kvfile.close()
            kcfile.close()
            kmfile.close()
            printexception()
            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30309) + ' ' + translate(30310)
            perfdialog.ok(translate(30308), dialog_text)
            break            

        if vdate < 0:                                            # User cancel
            break      
        elif menuitem1 in (pselect[vdate]):                      # Movies selected
            if kmovies > 0:
                displayMovieMenu(dbtype)
        elif menuitem2 in (pselect[vdate]):                      # TV Shows selected
            if ktvshows > 0:
                displayTvshows(dbtype)
        elif menuitem3 in (pselect[vdate]):                      # Music video selected
            if kmvideos > 0:
                displayMvideos(dbtype)
        elif menuitem9 in (pselect[vdate]):                      # Music analyze
            nofeature() 
        elif menuitem4 in (pselect[vdate]):                      # Music selected
            if kmusic > 0:
                displayMmusic(mudbtype)
        elif menuitem5 in (pselect[vdate]):                      # Logging selected
            if kslog > 0: 
                displayGenLogs()        
        elif menuitem6 in (pselect[vdate]):                      # CSV Export selected 
            selectExport()
        elif menuitem7 in (pselect[vdate]):                      # Backup selected 
            selectBackups()
        elif menuitem8 in (pselect[vdate]):                      # Video analyze
            vanalMenu(dbtype)


def testdata():

    dbtype = settings('dbtype')
    outdb = openKodiDB(dbtype)

    x = 100000
    y = 200000

    if dbtype != 'mysql':
        for a in range(300000, 310000):
            outdb.execute('INSERT OR REPLACE into actor_link (actor_id, media_id, media_type,     \
            cast_order) values (?, ?, ?, ?)', (x, y, 'movie', 1,))
            x += 1
            y += 1
    else:
        kcursor = outdb.cursor()
        for a in range(300000, 310000):         
            kcursor.execute('INSERT into actor_link (actor_id, media_id, media_type,     \
            cast_order) values (%s, %s, %s, %s)', (x, y, 'movie', 1))
            x += 1
            y += 1
        kcursor.close()

    outdb.commit()         
    outdb.close()



checkKscleanDB()                                                #  Check Kscleaner logging database
checkMuTriggers()                                               #  Check music database triggers
displayMenu()                                                   #  Display main menu

