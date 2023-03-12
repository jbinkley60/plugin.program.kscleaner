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

def displayMmusic(dbtype):                                          # Display menu 

    while True:
        try:
            kmfile = openKodiMuDB(dbtype)                           # Open Kodi music database
            pselect = []
            muquery = "SELECT upper(substr(strAlbum, 1, 1)) FROM album GROUP BY upper(substr(strAlbum, 1, 1))"
            if dbtype == 'mysql':
                kcursor = kmfile.cursor()
                kcursor.execute(muquery)
                kmmusic = kcursor.fetchall()                        # Get music videos from video database
                kcursor.close()
            else:
                curpf = kmfile.execute(muquery)
                kmmusic = curpf.fetchall()                          # Get music videos from video database
                del curpf 
            for mmusic in kmmusic:
                pselect.append(mmusic[0])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306) + ' - ' + translate(30325), pselect)
            xbmc.log('Kodi selective cleaner music menu selection is: ' + pselect[vdate], xbmc.LOGDEBUG)   
            kmfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Music menu error. ', xbmc.LOGERROR)
            if kmfile:            
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
            displayMusic(kmmusic[vdate][0], dbtype)


def displayMusic(smname, dbtype):                                  # Display menu 

    while True:
        try:
            kmfile = openKodiMuDB(dbtype)                          # Open Kodi music database
            pselect = []
            #curpf = kmfile.execute('SELECT idAlbum, strAlbum from album where strAlbum like ? ORDER BY     \
            #strAlbum ASC', (smname + '%',))
            mmuquery = "SELECT idAlbum, strAlbum from album where strAlbum like ? ORDER BY     \
            strAlbum ASC" 
            msuquery = "SELECT idAlbum, strAlbum from album where strAlbum like %s ORDER BY    \
            strAlbum ASC"
            varquery = list([smname + '%'])
            if dbtype == 'mysql':
                kcursor = kmfile.cursor()
                kcursor.execute(msuquery, varquery)
                kmusic = kcursor.fetchall()                        # Get music from music database
                kcursor.close()
            else:
                curpf = kmfile.execute(mmuquery, varquery)
                kmusic = curpf.fetchall()                          # Get music from music database
                del curpf 
            for music in kmusic:
                if len(music[1]) < 1:                              # Handle blank music names
                    pselect.append('Unknown')
                else:
                    pselect.append(music[1])                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.multiselect(translate(30306) + ' - ' + translate(30303), pselect)
            kmfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Music error. ', xbmc.LOGERROR)
            if kmfile:             
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



