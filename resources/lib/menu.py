import xbmc
import xbmcgui
import xbmcplugin
import os
import xbmcaddon
import xbmcvfs
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception, translate
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature
from resources.lib.logs import displayGenLogs
from resources.lib.tvshows import displayTvshows
from resources.lib.movies import displayMovieMenu
from resources.lib.mvideos import displayMvideos
from resources.lib.music import displayMmusic
from resources.lib.exports import selectExport

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

    while True:
        try:
            kvfile = openKodiDB()                                # Open Kodi video database
            kmfile = openKodiMuDB()                              # Open Kodi music database
            kcfile = openKscleanDB()                             # Open Kscleaner database
            pselect = []
            #curpf = kvfile.execute('SELECT c00 FROM movie LIMIT 1', )
            curpf = kvfile.execute('SELECT count (c00) FROM movie',)
            kmovies = curpf.fetchone()[0]                        # Get movies from video database
            if int(kmovies) > -1 :                               # If movies in video database
                pselect.append(str(menuitem1)  + '\t\t  -  ' + str(kmovies) + '  ' + translate(30327))

            #curpf = kvfile.execute('SELECT c00 FROM tvshow LIMIT 1', )
            curpf = kvfile.execute('SELECT count (c00) FROM tvshow',)
            ktvshows = curpf.fetchone()[0]                       # Get tvshows from video database
            if int(ktvshows) > -1 :                              # If tvshows in video database
                pselect.append(str(menuitem2)  + '\t\t  -  ' + str(ktvshows) + '  ' + translate(30327))

            curpf = kvfile.execute('SELECT count (c00) FROM musicvideo', )
            kmvideos = curpf.fetchone()[0]                       # Get musicvideos from video database 
            if int(kmvideos) > -1 :                              # If musicvideos in video database
                pselect.append(str(menuitem3)  + '\t  -  ' + str(kmvideos) + '  ' + translate(30327))

            curpf = kmfile.execute('SELECT count (strAlbum) FROM album', )
            kmusic = curpf.fetchone()[0]                         # Get albums from music database
            if int(kmusic) > -1 :                                # If albums in music database
                pselect.append(str(menuitem4)  + '\t\t  -  ' + str(kmusic) + '  ' + translate(30327))

            curpf = kcfile.execute('SELECT count (kgGenDat) FROM kscleanLog', )
            kslog = curpf.fetchone()[0]                          # Get logs from logging database
            if int(kslog) > -1:                                  # If logs in logging database
                pselect.append(menuitem5)     

            pselect.append(menuitem6)
            pselect.append(menuitem7)

            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306), pselect)
            xbmc.log('Kodi selective cleaner selection is: ' + pselect[vdate], xbmc.LOGDEBUG)
            del curpf    
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
                displayMovieMenu()
        elif menuitem2 in (pselect[vdate]):                      # TV Shows selected
            if ktvshows > 0:
                displayTvshows()
        elif menuitem3 in (pselect[vdate]):                      # Music video selected
            if kmvideos > 0:
                displayMvideos()
        elif menuitem4 in (pselect[vdate]):                      # Music selected
            if kmusic > 0:
                displayMmusic()
        elif menuitem5 in (pselect[vdate]):                      # Logging selected
            if kslog > 0: 
                displayGenLogs()        
        elif menuitem6 in (pselect[vdate]):                      # CSV Export selected 
            selectExport()
        elif menuitem7 in (pselect[vdate]):                      # Backup selected
            nofeature() 
            #perfStats()

checkKscleanDB()                                                #  Check Kscleaner logging database
displayMenu()                                                   #  Display main menu

