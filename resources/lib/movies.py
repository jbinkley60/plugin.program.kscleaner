import xbmc
import xbmcgui
import xbmcplugin
import os
import xbmcaddon
import xbmcvfs
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception, translate
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature

from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'

def displayMovieMenu():                                             # Display menu 

    while True:
        try:
            kvfile = openKodiDB()                                   # Open Kodi video database
            pselect = []
            curpf = kvfile.execute('SELECT upper(substr(c00, 1, 1)) FROM movie GROUP BY upper(substr(c00, 1, 1))')
            kmmovies = curpf.fetchall()                             # Get movies from video database
            for mmovie in kmmovies:
                pselect.append(mmovie[0])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306) + ' - ' + translate(30323), pselect)
            xbmc.log('Kodi selective cleaner movie menu selection is: ' + pselect[vdate], xbmc.LOGDEBUG)
            del curpf    
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Movies menu error. ', xbmc.LOGERROR)
            del curpf             
            kvfile.close()
            printexception()
            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30309) + ' ' + translate(30310)
            perfdialog.ok(translate(30308), dialog_text)
            break            

        if vdate < 0:                                              # User cancel
            break      
        else:                                                      # TV Show selected
            xbmc.log('KC Cleaner Movies Menu selection: ' + str(kmmovies[vdate][0]), xbmc.LOGDEBUG )
            #nofeature()
            displayMovies(kmmovies[vdate][0])


def displayMovies(ssname):                                          # Display menu 

    while True:
        try:
            kvfile = openKodiDB()                                   # Open Kodi video database
            pselect = []
            curpf = kvfile.execute('SELECT idMovie, idFile, c00 from movie where c00 like ? ORDER BY     \
            c00 ASC', (ssname + '%',))
            kmovies = curpf.fetchall()                              # Get movies from video database
            for movie in kmovies:
                if len(movie[2]) < 1:                               # Handle blank movie names
                    pselect.append('Unknown')
                else:
                    pselect.append(movie[2])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.multiselect(translate(30306) + ' - ' + translate(30300), pselect)
            del curpf    
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Movies error. ', xbmc.LOGERROR)
            del curpf             
            kvfile.close()
            printexception()
            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30309) + ' ' + translate(30310)
            perfdialog.ok(translate(30308), dialog_text)
            break            

        if vdate == None:                                           # User cancel
            break      
        else:                                                       # Movie(s) selected
            xbmc.log('Kodi selective cleaner movies selection is: ' + str(vdate), xbmc.LOGDEBUG)
            nofeature()



