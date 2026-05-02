import xbmc
import xbmcgui
import xbmcplugin
import os
import xbmcaddon
import xbmcvfs
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception, translate
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature, settings, vftUpdate, vbkUpdate
from resources.lib.artwork import getArtlist, checkArt, cleanArt
from resources.lib.exports import exportData


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

            xbmc.executebuiltin('Dialog.Close(all, true)')
            xbmc.sleep(200)                         
 
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
            vartworkv = settings('vartworkv')                       # Video artwork validation setting
            detailedlog = settings('vavdetailed')                   # Detailed logging flag
            kvfile = openKodiDB(dbtype)                             # Open Kodi video database
            selectall = translate(30430) + translate(30302)
            pselect = [selectall]
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

            xbmc.executebuiltin('Dialog.Close(all, true)')
            xbmc.sleep(200)                         
 
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

        selections = []
        if vdate == None:                                           # User cancel
            break
        elif 0 in vdate:
            for x in range(0, len(kmvideos)):
                #xbmc.log('KS Cleaner Music Video loop: ' + str(x), xbmc.LOGINFO)
                mvideo_info = kmvideos[x]
                selections.append(mvideo_info)
            xbmc.log('KS Cleaner Movie Selection: ' + str(selections), xbmc.LOGDEBUG)
        else:
            for x in vdate:
                mvideo_info = kmvideos[x-1]
                selections.append(mvideo_info)
            xbmc.log('KS Cleaner Movie Selections: ' + str(selections), xbmc.LOGDEBUG)          

        xbmc.executebuiltin('Dialog.Close(all, true)')
        xbmc.sleep(200)

        menuitem1 = translate(30432)                               # Clear Bookmark
        menuitem2 = translate(30433)                               # Set to Not Played
        menuitem3 = translate(30434)                               # Set to Played
        menuitem4 = translate(30435)                               # Remove from Kodi DB
        menuitem5 = translate(30436)                               # Video Artwork Validation

        moptions = [menuitem1, menuitem2, menuitem3, menuitem4]
        if vartworkv == 'true':                                    # Video artwork validation setting enabled
            moptions.append(menuitem5)
        ddialog = xbmcgui.Dialog()
        itemcount = len(selections)
        dialogheader = translate(30302).rstrip('s') + ' '  + translate(30431) + ' - ' + str(itemcount) + ' '   \
        + translate(30302) + translate(30452)
        mselect = ddialog.select(dialogheader, moptions)
        if mselect < 0:                                            # User cancel
            xbmc.executebuiltin('Dialog.Close(all, true)')
            xbmc.sleep(200)
            break
        elif  menuitem1 in moptions[mselect]:
            msg = translate(30437)				   # Bookmark cleared for
            for mvideo in selections:
                vbkUpdate('delete', mvideo[1], dbtype)
                kgenlogUpdate(msg +  'music video: ' + str(mvideo[2]), 'No') 
            mvideoSuccess(dialogheader, itemcount, msg)
        elif  menuitem2 in moptions[mselect]:
            msg = translate(30438)				   # Playcount set to 0 for 
            for mvideo in selections:
                vftUpdate('playcount', mvideo[1], dbtype, 0)
                kgenlogUpdate(msg +  'music video: ' + str(mvideo[2]), 'No')
            mvideoSuccess(dialogheader, itemcount, msg)
        elif  menuitem3 in moptions[mselect]:
            msg = translate(30439)				   # Playcount set to 1 for 
            for mvideo in selections:
                vftUpdate('playcount', mvideo[1], dbtype, 1)
                kgenlogUpdate(msg +  'music video: ' + str(mvideo[2]), 'No')
            mvideoSuccess(dialogheader, itemcount, msg)
        elif  menuitem5 in moptions[mselect]:
            #artList = getArtlist(dbtype, 'movie', selections)
            #if len(artList) > 0:
            #    checkArt(artList, detailedlog)

            xbmc.executebuiltin('Dialog.Close(all, true)')
            xbmc.sleep(200)

            afunction = []
            menuitem1 = translate(30442)                       # Analyze artwork
            menuitem2 = translate(30354)                       # Analyze / CSV Export
            menuitem3 = translate(30443)                       # Analyze / Clean artwork

            xbmc.executebuiltin('Dialog.Close(all, true)')
            xbmc.sleep(200)

            selectfn = [menuitem1, menuitem2, menuitem3]
            ddialog = xbmcgui.Dialog()    
            #sfunction = ddialog.select(translate(30306) + ' - ' + translate(30356), selectfn)
            sfunction = ddialog.select(translate(30436) + ' - ' + translate(30356), selectfn)
            xbmc.log('KS Cleaner Music Video Function selection: ' + selectfn[sfunction], xbmc.LOGDEBUG)     
            if sfunction < 0:                                  # User cancel
                return
            elif menuitem1 in selectfn[sfunction]:
                xbmc.log('KS Cleaner Music Video Artwork Validation: ' + str(selections), xbmc.LOGDEBUG)                   
                arturls = getArtlist(dbtype, 'musicvideo', selections, 'yes')
                #xbmc.log('KS Cleaner Music Video Artwork Validation URLs: ' + str(arturls), xbmc.LOGDEBUG)      
                checkArt(arturls, detailedlog)
            elif menuitem2 in selectfn[sfunction]:
                arturls = getArtlist(dbtype, 'musicvideo', selections, 'yes')
                checkArt(arturls, detailedlog, 'yes')
                exportData(['art_temp'], 'artanalyzer', 'musicvideo')
            elif menuitem3 in selectfn[sfunction]: 
                arturls = getArtlist(dbtype, 'musicvideo', selections, 'yes')
                checkArt(arturls, detailedlog, 'yes')
                cleanArt(dbtype)   
 
        else:
            nofeature()


def mvideoSuccess(dialogheader, itemcount, msg):                            # Display success dialog box

            xbmc.executebuiltin('Dialog.Close(all, true)')
            xbmc.sleep(200)

            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30302).rstrip('s') + ' '  + translate(30431) + msg + ' ' + str(itemcount) + \
            ' ' + translate(30302).lower()
            perfdialog.ok(dialogheader, dialog_text)

