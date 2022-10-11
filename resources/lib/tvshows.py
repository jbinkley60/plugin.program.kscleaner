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

def displayTvshows():                                              # Display menu 

    while True:
        try:
            kvfile = openKodiDB()                                   # Open Kodi video database
            pselect = []
            curpf = kvfile.execute('SELECT idshow, c00 from tvshow ORDER BY c00 ASC',)
            ktvshows = curpf.fetchall()                             # Get TV Shows from video database
            for tvshow in ktvshows:
                if len(tvshow[1]) < 1:                              # Handle blank TV Show names
                    pselect.append('Unknown')
                else:
                    pselect.append(tvshow[1])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306) + ' - ' + translate(30301), pselect)
            xbmc.log('Kodi selective cleaner selection is: ' + pselect[vdate], xbmc.LOGDEBUG)
            del curpf    
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner TV Shows menu error. ', xbmc.LOGERROR)
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
            xbmc.log('KC Cleaner TV Show selection: ' + str(vdate) + ' ' + ktvshows[vdate][1], xbmc.LOGDEBUG )
            displaySeasons(ktvshows[vdate][0],ktvshows[vdate][1])


def displaySeasons(sidshow, sname):                                 # Display menu 

    while True:
        try:
            kvfile = openKodiDB()                                   # Open Kodi video database
            pselect = []
            curpf = kvfile.execute('Select idShow, name, idSeason from seasons where idShow = ? ORDER BY     \
            season ASC', (sidshow,))
            ktvseason = curpf.fetchall()                            # Get TV Seasons from video database
            for season in ktvseason:
                if len(season[1]) < 1:                              # Handle blank TV Season names
                    pselect.append('Unknown')
                else:
                    pselect.append(season[1])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306) + ' - ' + translate(30321), pselect)
            xbmc.log('Kodi selective cleaner season selection is: ' + pselect[vdate], xbmc.LOGDEBUG)
            del curpf    
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner TV Seasons menu error. ', xbmc.LOGERROR)
            del curpf             
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
            displayEpisodes(ktvseason[vdate][0],ktvseason[vdate][2])


def displayEpisodes(sidshow, sseason):                              # Display menu 

    while True:
        try:
            xbmc.log('KS Cleaner episode query: ' + str(sidshow) + ' ' + str(sseason), xbmc.LOGDEBUG)
            kvfile = openKodiDB()                                   # Open Kodi video database
            pselect = ['Delete All Episodes']
            curpf = kvfile.execute('select idEpisode, idFile, c00, c13 from episode WHERE idShow = ?     \
            and idSeason = ?  ORDER BY c13 ASC', (sidshow, sseason,))
            kepisodes = curpf.fetchall()                            # Get TV Episodes from video database
            for episode in kepisodes:
                if len(episode[2]) < 1:                              # Handle blank TV Episode names
                    pselect.append(episode[3] + ' - ' + 'Unknown')
                else:
                    pselect.append(episode[3] + ' - ' + episode[2])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.multiselect(translate(30306) + ' - ' + translate(30322), pselect)
            del curpf    
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
