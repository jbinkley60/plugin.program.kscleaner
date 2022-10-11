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

def displayMvideos():                                               # Display menu 

    while True:
        try:
            kvfile = openKodiDB()                                   # Open Kodi video database
            pselect = []
            curpf = kvfile.execute('SELECT upper(substr(c00, 1, 1)) FROM musicvideo GROUP BY upper(substr(c00, 1, 1))')
            kmvideos = curpf.fetchall()                             # Get music videos from video database
            for mmvideo in kmvideos:
                pselect.append(mmvideo[0])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306) + ' - ' + translate(30324), pselect)
            xbmc.log('Kodi selective cleaner music video menu selection is: ' + pselect[vdate], xbmc.LOGDEBUG)
            del curpf    
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Music Videos menu error. ', xbmc.LOGERROR)
            del curpf             
            kvfile.close()
            printexception()
            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30309) + ' ' + translate(30310)
            perfdialog.ok(translate(30308), dialog_text)
            break            

        if vdate < 0:                                              # User cancel
            break      
        else:                                                      # Music video selected
            xbmc.log('KC Cleaner Music Videos Menu selection: ' + str(kmvideos[vdate][0]), xbmc.LOGDEBUG )
            #nofeature()
            displayVideos(kmvideos[vdate][0])


def displayVideos(smname):                                          # Display menu 

    while True:
        try:
            kvfile = openKodiDB()                                   # Open Kodi video database
            pselect = []
            curpf = kvfile.execute('SELECT idMVideo, idFile, c00 from musicvideo where c00 like ? ORDER BY     \
            c00 ASC', (smname + '%',))
            kmvideos = curpf.fetchall()                             # Get music videos from video database
            for video in kmvideos:
                if len(video[2]) < 1:                               # Handle blank music video names
                    pselect.append('Unknown')
                else:
                    pselect.append(video[2])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.multiselect(translate(30306) + ' - ' + translate(30302), pselect)
            del curpf    
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Music Videos error. ', xbmc.LOGERROR)
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
            xbmc.log('Kodi selective cleaner music videos selection is: ' + str(vdate), xbmc.LOGDEBUG)
            nofeature()



