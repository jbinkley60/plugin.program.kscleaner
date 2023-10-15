import xbmc
import xbmcgui
import xbmcplugin
import os
import xbmcaddon
import xbmcvfs
from .common import openKodiDB, openKodiMuDB, openKscleanDB, printexception, translate
from .common import kgenlogUpdate, checkKscleanDB, nofeature

from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'

def displayMovieMenu(dbtype):                                       # Display menu 

    while True:
        try:
            kvfile = openKodiDB(dbtype)                             # Open Kodi video database
            pselect = []
            mquery = "SELECT upper(substr(c00, 1, 1)), idMovie FROM movie GROUP BY upper(substr(c00, 1, 1))"
            if dbtype == 'mysql':
                kcursor = kvfile.cursor()
                kcursor.execute(mquery)
                kmmovies = kcursor.fetchall()                       # Get movies from video database
                kcursor.close()
            else:
                curpf = kvfile.execute(mquery)
                kmmovies = curpf.fetchall()                         # Get movies from video database
                del curpf

            for mmovie in kmmovies:
                if mmovie[0] == None:
                    pselect.append('Invalid Titles')
                else:
                    pselect.append(str(mmovie[0]))                         
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306) + ' - ' + translate(30317), pselect)
            #xbmc.log('Kodi selective cleaner movie menu selection is: ' + pselect[vdate], xbmc.LOGDEBUG)  
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Movies menu error. ', xbmc.LOGERROR)
            if kvfile:            
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
            displayMovies(kmmovies[vdate][0], dbtype)


def displayMovies(ssname, dbtype):                                  # Display menu 

    while True:
        try:
            kvfile = openKodiDB(dbtype)                             # Open Kodi video database
            pselect = []
            mmquery = "SELECT idMovie, idFile, c00 from movie where c00 like ? ORDER BY     \
            c00 ASC" 
            msquery = "SELECT idMovie, idFile, c00 from movie where c00 like %s ORDER BY     \
            c00 ASC"
            varquery = list([ssname + '%'])
            vars = ssname + "%"
            if dbtype == 'mysql':
                kcursor = kvfile.cursor()
                kcursor.execute(msquery, varquery) 
                kmovies = kcursor.fetchall()                       # Get movies from video database
                kcursor.close()
            else:
                curpf = kvfile.execute(mmquery, varquery)
                kmovies = curpf.fetchall()                         # Get movies from video database
                del curpf 
            for movie in kmovies:
                if movie[2] == None:                               # Handle blank movie names
                    kgenlog = "Movie with idMovie: " + str(movie[0]) + " has an invalid movie title."
                    kgenlogUpdate(kgenlog)
                    pselect.append('Unknown movie title for idMovie:' + str(movie[0]))
                else:
                    pselect.append(str(movie[2]))                           
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.multiselect(translate(30306) + ' - ' + translate(30300), pselect)
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Movies error. ', xbmc.LOGERROR)
            if kvfile:            
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



