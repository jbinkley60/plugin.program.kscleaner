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

            xbmc.executebuiltin('Dialog.Close(all, true)')
            xbmc.sleep(200)
 
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
            vartworkv = settings('vartworkv')                       # Video artwork validation setting
            detailedlog = settings('vavdetailed')                   # Detailed logging flag
            kvfile = openKodiDB(dbtype)                             # Open Kodi video database
            selectall = translate(30430) + translate(30300)
            pselect = [selectall]
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

            xbmc.executebuiltin('Dialog.Close(all, true)')
            xbmc.sleep(200) 

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

        selections = []
        if vdate == None:                                           # User cancel
            break
        elif 0 in vdate:
            for x in range(0, len(kmovies)):
                #xbmc.log('KS Cleaner Movie loop: ' + str(x), xbmc.LOGINFO)
                movie_info = kmovies[x]
                selections.append(movie_info)
            xbmc.log('KS Cleaner Movie Selection: ' + str(selections), xbmc.LOGDEBUG)
        else:
            for x in vdate:
                movie_info = kmovies[x-1]
                selections.append(movie_info)
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

        xbmc.executebuiltin('Dialog.Close(all, true)')
        xbmc.sleep(200)

        ddialog = xbmcgui.Dialog()
        itemcount = len(selections)
        dialogheader = translate(30300).rstrip('s') + ' '  + translate(30431) + ' - ' + str(itemcount) + ' '   \
        + translate(30300) + translate(30452)
        mselect = ddialog.select(dialogheader, moptions)
        if mselect < 0:                                            # User cancel
            xbmc.executebuiltin('Dialog.Close(all, true)')
            xbmc.sleep(200)
            break
        elif  menuitem1 in moptions[mselect]:
            msg = translate(30437)				   # Bookmark cleared for
            for movie in selections:
                vbkUpdate('delete', movie[1], dbtype)
                kgenlogUpdate(msg +  'movie: ' + str(movie[2]), 'No') 
            movieSuccess(dialogheader, itemcount, msg)
        elif  menuitem2 in moptions[mselect]:
            msg = translate(30438)				   # Playcount set to 0 for 
            for movie in selections:
                vftUpdate('playcount', movie[1], dbtype, 0)
                kgenlogUpdate(msg +  'movie: ' + str(movie[2]), 'No')
            movieSuccess(dialogheader, itemcount, msg)
        elif  menuitem3 in moptions[mselect]:
            msg = translate(30439)				   # Playcount set to 1 for 
            for movie in selections:
                vftUpdate('playcount', movie[1], dbtype, 1)
                kgenlogUpdate(msg +  'movie: ' + str(movie[2]), 'No')
            movieSuccess(dialogheader, itemcount, msg)
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

            selectfn = [menuitem1, menuitem2, menuitem3]
            ddialog = xbmcgui.Dialog()    
            #sfunction = ddialog.select(translate(30306) + ' - ' + translate(30356), selectfn)
            sfunction = ddialog.select(translate(30436) + ' - ' + translate(30356), selectfn)
            xbmc.log('KS Cleaner Movie Function selection: ' + selectfn[sfunction], xbmc.LOGDEBUG)     
            if sfunction < 0:                                  # User cancel
                return
            elif menuitem1 in selectfn[sfunction]:
                xbmc.log('KS Cleaner Movie Artwork Validation: ' + str(selections), xbmc.LOGDEBUG)                   
                arturls = getArtlist(dbtype, 'movie', selections, 'yes')
                #xbmc.log('KS Cleaner Movie Artwork Validation URLs: ' + str(arturls), xbmc.LOGDEBUG)      
                checkArt(arturls, detailedlog)
            elif menuitem2 in selectfn[sfunction]:
                arturls = getArtlist(dbtype, 'movie', selections, 'yes')
                checkArt(arturls, detailedlog, 'yes')
                exportData(['art_temp'], 'artanalyzer', 'movie')
            elif menuitem3 in selectfn[sfunction]: 
                arturls = getArtlist(dbtype, 'movie', selections, 'yes')
                checkArt(arturls, detailedlog, 'yes')
                cleanArt(dbtype)   
 
        else:
            nofeature()


def movieSuccess(dialogheader, itemcount, msg):                            # Display success dialog box

            xbmc.executebuiltin('Dialog.Close(all, true)')
            xbmc.sleep(200)

            perfdialog = xbmcgui.Dialog()
            dialog_text = translate(30300).rstrip('s') + ' '  + translate(30431) + msg + ' ' + str(itemcount) + \
            ' ' + translate(30300).lower()
            perfdialog.ok(dialogheader, dialog_text)

