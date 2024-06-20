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

def displayMvideos(dbtype):                                         # Display menu 

    while True:
        try:
            kvfile = openKodiDB(dbtype)                             # Open Kodi video database
            pselect = []
            mvquery = "SELECT upper(substr(c00, 1, 1)) FROM musicvideo GROUP BY upper(substr(c00, 1, 1))"
            #curpf = kvfile.execute('SELECT upper(substr(c00, 1, 1)) FROM musicvideo GROUP BY upper(substr(c00, 1, 1))')
            #kmvideos = curpf.fetchall()                             # Get music videos from video database
            if dbtype == 'mysql':
                kcursor = kvfile.cursor()
                kcursor.execute(mvquery)
                kmvideos = kcursor.fetchall()                       # Get music videos from video database
                kcursor.close()
            else:
                curpf = kvfile.execute(mvquery)
                kmvideos = curpf.fetchall()                         # Get music videos from video database
                del curpf 
            for mmvideo in kmvideos:
                pselect.append(str(mmvideo[0]))                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.select(translate(30306) + ' - ' + translate(30324), pselect)
            xbmc.log('Kodi selective cleaner music video menu selection is: ' + pselect[vdate], xbmc.LOGDEBUG)  
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Music Videos menu error. ', xbmc.LOGERROR)
            if kvfile:             
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
            displayVideos(kmvideos[vdate][0], dbtype)


def displayVideos(smname, dbtype):                                  # Display menu 

    while True:
        try:
            kvfile = openKodiDB(dbtype)                             # Open Kodi video database
            pselect = []
            mmvquery = "SELECT idMVideo, idFile, c00 from musicvideo where c00 like ? ORDER BY     \
            c00 ASC" 
            mvsquery = "SELECT idMVideo, idFile, c00 from musicvideo where c00 like %s ORDER BY     \
            c00 ASC"
            varquery = list([smname + '%'])
            if dbtype == 'mysql':
                kcursor = kvfile.cursor()
                kcursor.execute(mvsquery, varquery)
                kmvideos = kcursor.fetchall()                        # Get music videos from video database
                kcursor.close()
            else: 
                curpf = kvfile.execute(mmvquery, varquery)
                kmvideos = curpf.fetchall()                          # Get music videos from video database
                del curpf  
            for video in kmvideos:
                if video[2] == None:                                 # Handle blank music video names
                    kgenlog = "Musicvideo with idMVideo: " + str(video[0]) + " has an invalid title."
                    kgenlogUpdate(kgenlog)
                    pselect.append('Unknown musicvideo title for idMVideo:' + str(video[0]))
                else:
                    pselect.append(str(video[2]))                          
 
            ddialog = xbmcgui.Dialog()    
            vdate = ddialog.multiselect(translate(30306) + ' - ' + translate(30302), pselect) 
            kvfile.close()
        except Exception as e:
            xbmc.log('KS Cleaner Music Videos error. ', xbmc.LOGERROR)
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
            xbmc.log('Kodi selective cleaner music videos selection is: ' + str(vdate), xbmc.LOGDEBUG)
            nofeature()



