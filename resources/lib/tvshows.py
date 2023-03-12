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

def displayTvshows(dbtype):                                         # Display menu 

    while True:
        try:
            kvfile = openKodiDB(dbtype)                             # Open Kodi video database
            pselect = []
            tquery = "SELECT idshow, c00 from tvshow ORDER BY c00 ASC"
            if dbtype == 'mysql':
                kcursor = kvfile.cursor()
                kcursor.execute(tquery)
                ktvshows = kcursor.fetchall()                       # Get TV Shows from video database
                kcursor.close()
            else:
                curpf = kvfile.execute(tquery)
                ktvshows = curpf.fetchall()                         # Get TV Shows from video database
                del curpf 
            for tvshow in ktvshows:
                if len(tvshow[1]) < 1:                              # Handle blank TV Show names
                    pselect.append('Unknown')
                else:
                    pselect.append(tvshow[1])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306) + ' - ' + translate(30301), pselect)
            xbmc.log('Kodi selective cleaner selection is: ' + pselect[vdate], xbmc.LOGDEBUG)  
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner TV Shows menu error. ', xbmc.LOGERROR)
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
            xbmc.log('KC Cleaner TV Show selection: ' + str(vdate) + ' ' + ktvshows[vdate][1], xbmc.LOGDEBUG )
            displaySeasons(ktvshows[vdate][0],ktvshows[vdate][1], dbtype)


def displaySeasons(sidshow, sname, dbtype):                         # Display menu 

    while True:
        try:
            kvfile = openKodiDB(dbtype)                             # Open Kodi video database
            pselect = []
            squery = "Select idShow, name, idSeason from seasons where idShow = ?   \
            ORDER BY season ASC"    
            ssquery = "Select idShow, name, idSeason from seasons where idShow = %s \
            ORDER BY season ASC"      
            varquery = list([sidshow])
            if dbtype == 'mysql':
                kcursor = kvfile.cursor()
                kcursor.execute(ssquery, varquery)
                ktvseason = kcursor.fetchall()                      # Get TV Seasons from video database
                kcursor.close()
            else:
                curpf = kvfile.execute(squery, varquery)
                ktvseason = curpf.fetchall()                        # Get TV Seasons from video database
                del curpf
            for season in ktvseason:
                if len(season[1]) < 1:                              # Handle blank TV Season names
                    pselect.append('Unknown')
                else:
                    pselect.append(season[1])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306) + ' - ' + translate(30321), pselect)
            xbmc.log('Kodi selective cleaner season selection is: ' + pselect[vdate], xbmc.LOGDEBUG)   
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner TV Seasons menu error. ', xbmc.LOGERROR)
            if kvfile:             
                kvfile.close()
            printexception()
            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30309) + ' ' + translate(30310)
            perfdialog.ok(translate(30308), dialog_text)
            break            

        if vdate < 0:                                               # User cancel
            break      
        else:                                                       # TV Season selected
            #nofeature()
            displayEpisodes(ktvseason[vdate][0],ktvseason[vdate][2], dbtype)


def displayEpisodes(sidshow, sseason, dbtype):                       # Display menu 

    while True:
        try:
            xbmc.log('KS Cleaner episode query: ' + str(sidshow) + ' ' + str(sseason), xbmc.LOGDEBUG)
            kvfile = openKodiDB(dbtype)                                   # Open Kodi video database
            pselect = ['Delete All Episodes']
            equery = "select idEpisode, idFile, c00, c13 from episode WHERE idShow = ?     \
            and idSeason = ? ORDER BY CAST(c13 AS INTEGER) ASC"
            esquery = "select idEpisode, idFile, c00, c13 from episode WHERE idShow = %s    \
            and idSeason = %s ORDER BY CAST(c13 AS UNSIGNED) ASC"
            #curpf = kvfile.execute('select idEpisode, idFile, c00, c13 from episode WHERE idShow = ?     \
            #and idSeason = ?  ORDER BY CAST(c13 AS INTEGER) ASC', (sidshow, sseason,))
            varquery = list([sidshow, sseason])
            if dbtype == 'mysql':
                kcursor = kvfile.cursor()
                kcursor.execute(esquery, varquery)
                kepisodes = kcursor.fetchall()                      # Get TV Episodes from video database
                kcursor.close()
            else:
                curpf = kvfile.execute(equery, varquery)
                kepisodes = curpf.fetchall()                        # Get TV Episodes from video database
                del curpf             
            for episode in kepisodes:
                if len(episode[2]) < 1:                              # Handle blank TV Episode names
                    pselect.append(episode[3] + ' - ' + 'Unknown')
                else:
                    pselect.append(episode[3] + ' - ' + episode[2])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.multiselect(translate(30306) + ' - ' + translate(30322), pselect)  
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner TV Episodes menu error. ', xbmc.LOGERROR)
            del curpf             
            kvfile.close()
            printexception()
            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30309) + ' ' + translate(30310)
            perfdialog.ok(translate(30308), dialog_text)
            break            

        if vdate == None:                                           # User cancel
            break      
        else:                                                       # Episodes selected
            xbmc.log('Kodi selective cleaner episode selection is: ' + str(vdate), xbmc.LOGDEBUG)
            nofeature()
