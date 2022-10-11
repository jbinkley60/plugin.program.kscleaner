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

def displayMmusic():                                                # Display menu 

    while True:
        try:
            kmfile = openKodiMuDB()                                 # Open Kodi music database
            pselect = []
            curpf = kmfile.execute('SELECT upper(substr(strAlbum, 1, 1)) FROM album GROUP BY upper(substr(strAlbum, 1, 1))')
            kmmusic = curpf.fetchall()                             # Get music videos from video database
            for mmusic in kmmusic:
                pselect.append(mmusic[0])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306) + ' - ' + translate(30325), pselect)
            xbmc.log('Kodi selective cleaner music menu selection is: ' + pselect[vdate], xbmc.LOGDEBUG)
            del curpf    
            kmfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Music menu error. ', xbmc.LOGERROR)
            del curpf             
            kmfile.close()
            printexception()
            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30309) + ' ' + translate(30310)
            perfdialog.ok(translate(30308), dialog_text)
            break            

        if vdate < 0:                                              # User cancel
            break      
        else:                                                      # Music album selected
            xbmc.log('KC Cleaner Music Menu selection: ' + str(kmmusic[vdate][0]), xbmc.LOGDEBUG )
            displayMusic(kmmusic[vdate][0])


def displayMusic(smname):                                          # Display menu 

    while True:
        try:
            kmfile = openKodiMuDB()                                # Open Kodi music database
            pselect = []
            curpf = kmfile.execute('SELECT idAlbum, strAlbum from album where strAlbum like ? ORDER BY     \
            strAlbum ASC', (smname + '%',))
            kmusic = curpf.fetchall()                              # Get music from music database
            for music in kmusic:
                if len(music[1]) < 1:                              # Handle blank music names
                    pselect.append('Unknown')
                else:
                    pselect.append(music[1])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.multiselect(translate(30306) + ' - ' + translate(30303), pselect)
            del curpf    
            kmfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Music error. ', xbmc.LOGERROR)
            del curpf             
            kmfile.close()
            printexception()
            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30309) + ' ' + translate(30310)
            perfdialog.ok(translate(30308), dialog_text)
            break            

        if vdate == None:                                          # User cancel
            break      
        else:                                                      # Album selected
            xbmc.log('Kodi selective cleaner music selection is: ' + str(vdate), xbmc.LOGDEBUG)
            nofeature()



