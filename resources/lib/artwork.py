import xbmc
import xbmcgui
import xbmcplugin
import os
import xbmcaddon
import xbmcvfs
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception, translate
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature, settings
from resources.lib.exports import exportData

from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'


def analyzeArtwork(dbtype):                                                  # Analyze artwork main menu

        detailedlog = settings('vavdetailed')                                # Detailed logging flag
        kvfile = openKodiDB(dbtype)                                          # Open Kodi video database
        if dbtype == "mysql":
            arcursor = kvfile.cursor()
            arcursor.execute("SELECT DISTINCT media_type from art order by media_type asc")
            media_types = arcursor.fetchall()
            arcursor.close()
        else:
            arupf = kvfile.execute("SELECT DISTINCT media_type from art order by media_type asc")
            media_types = arupf.fetchall()           
            del arupf

        xbmc.log('KS Cleaner video artwork media_types: ' + str(media_types), xbmc.LOGDEBUG)
        kvfile.close()

        xbmc.executebuiltin('Dialog.Close(all, true)')
        xbmc.sleep(200)

        if len(media_types) == 0:
            artdialog = xbmcgui.Dialog()
            kgenlog = 'No Video Artwork Validation Media Types found in art table'
            artdialog.ok('Video Artwork Validation - Media Selections', kgenllog)
            kgenlogUpdate(kgenlog, 'No')
            return

        mediaselect = ["All Video Artwork"]
        for media in media_types:
            mediaselect.append(media[0].capitalize())

        ddialog = xbmcgui.Dialog()
        vart =  ddialog.select(translate(30436) + ' - Select Media Type', mediaselect)

        if vart < 0:
            return
        else:
            kgenlog = 'KS Cleaner video artwork validation media type selection: ' + mediaselect[vart].lower()
            kgenlogUpdate(kgenlog, 'No')
            xbmc.log(kgenlog, xbmc.LOGDEBUG)

        media_selection = mediaselect[vart].lower()

        afunction = []
        menuitem1 = translate(30442)                       # Analyze artwork
        menuitem2 = translate(30354)                       # Analyze / CSV Export
        menuitem3 = translate(30443)                       # Analyze / Clean artwork

        selectfn = [menuitem1, menuitem2, menuitem3]
        ddialog = xbmcgui.Dialog()    
        #sfunction = ddialog.select(translate(30306) + ' - ' + translate(30356), selectfn)
        sfunction = ddialog.select(mediaselect[vart] + ' - ' + translate(30356), selectfn)
        if sfunction < 0:                                  # User cancel
            return
        elif menuitem1 in selectfn[sfunction]:
            arturls = getArtlist(dbtype, media_selection)
            checkArt(arturls, detailedlog)
        elif menuitem2 in selectfn[sfunction]:
            arturls = getArtlist(dbtype, media_selection)
            checkArt(arturls, detailedlog, 'yes')
            exportData(['art_temp'], 'artanalyzer', media_selection)
        elif menuitem3 in selectfn[sfunction]: 
            arturls = getArtlist(dbtype, media_selection)
            checkArt(arturls, detailedlog, 'yes')
            cleanArt(dbtype)      


def getArtlist(dbtype, mediaType, selections = 'none', browse = 'no'):       # Get list of artwork URLs / files for selections

        artlist = []
        kvfile = openKodiDB(dbtype)                                          # Open Kodi video database

        if selections != 'none':                                             # Request from video db browser  
            xbmc.log('KS Cleaner video artwork selection getArtlist list: ' + str(selections), xbmc.LOGDEBUG)
 
            aquery = "SELECT art_id, media_type, type, url FROM art WHERE media_id = ? and media_type = ?"
            aaquery = "SELECT art_id, media_type, type, url FROM art WHERE media_id = %s and media_type = %s"       

            for art in selections:
                if browse == 'no':
                    varquery = [art[3], mediaType]
                else:
                    varquery = [art[0], mediaType]
                xbmc.log('KS Cleaner video artwork getArtlist variables: ' + str(varquery) + ' ' + str(browse) + ' ' + str(art[0]), xbmc.LOGDEBUG)
                if dbtype == "mysql":
                    arcursor = kvfile.cursor()
                    arcursor.execute(aaquery, varquery)
                    arturls = arcursor.fetchall()                            # Get artwork files from video database
                    arcursor.close()
                else:
                    aurpf = kvfile.execute(aquery, varquery)
                    xbmc.log('KS Cleaner video artwork URL fetch: ' + str(art[0]), xbmc.LOGDEBUG) 
                    arturls = aurpf.fetchall()
                    del aurpf
                for a in arturls:
                    artlist.append(a)

        else:
            if 'all' in mediaType:                                           # Get all artwork
                if dbtype == "mysql":
                    arcursor = kvfile.cursor()
                    arcursor.execute("SELECT art_id, media_type, type, url from art")
                    arturls = arcursor.fetchall()
                    arcursor.close()
                else:
                    arupf = kvfile.execute("SELECT art_id, media_type, type, url from art")
                    arturls = arupf.fetchall()           
                    del arupf
            else:
                aquery = "SELECT art_id, media_type, type, url FROM art WHERE media_type = ?"
                aaquery = "SELECT art_id, media_type, type, url FROM art WHERE media_type = %s"  

                varquery = [mediaType]
                if dbtype == "mysql":
                    arcursor = kvfile.cursor()
                    arcursor.execute(aaquery, varquery)
                    arturls = arcursor.fetchall()                            # Get artwork files from video database
                    arcursor.close()
                else:
                    arupf = kvfile.execute(aquery, varquery)
                    arturls = arupf.fetchall()
                    del arupf
            for a in arturls:
                artlist.append(a)
        
        kvfile.close()
        xbmc.log('KS Cleaner video artwork number of art entries found: ' + str(len(artlist)), xbmc.LOGDEBUG)           
        xbmc.log('KS Cleaner video artwork Selections: ' + str(artlist), xbmc.LOGDEBUG) 

        return artlist


def checkArt(artList, detailedlog, csv = 'no'):

        artcount = len(artList)

        logdb = openKscleanDB()

        if csv != 'no':
            logdb.execute('CREATE TABLE IF NOT EXISTS art_temp (art_id INTEGER, media_type TEXT, type TEXT,  \
            status TEXT, url TEXT)')
            logdb.execute('DELETE FROM art_temp')
            logdb.commit()

        xbmc.executebuiltin('Dialog.Close(all, true)')
        xbmc.sleep(200)

        if artcount > 500:
            msgdialogprogress = xbmcgui.DialogProgress()
            dialogmsg = translate(30444)				# Artwork URLs processed
            dialoghead = translate(30445)				# Video Artwork Validation Progress
            dialogmsgs = translate(30446)				# Artwork validation beginning
            msgdialogprogress.create(dialoghead, dialogmsgs)
            msgdialogprogress.update(0, translate(30446))  

        found = notfound = skipped = pcount = 0
        for art in artList:
            if art[3][:4].lower() == 'http':
                if detailedlog == 'true':
                    kgenlogUpdate('Artwork check skipped for URL: ' + art[3], 'No', logdb)
                skipped += 1
                art_status = 'Skipped HTTP'
            else:
                if os.path.isfile(art[3]):
                    if detailedlog == 'true':
                        kgenlogUpdate('Artwork file found: ' + art[3], 'No', logdb)
                    found += 1
                    art_status = 'Artwork file found'
                else:
                    kgenlogUpdate('Artwork file not found: ' + art[3], 'No', logdb)
                    notfound += 1
                    art_status = 'Artwork file not found'
            if csv != 'no':
                logdb.execute('INSERT into art_temp (art_id, media_type, type, status, url) values (?, ?, ?, ?, ?)',  \
                (art[0], art[1], art[2], art_status, art[3],))
            pcount += 1

            if pcount % 500 == 0:
                percent = int(float(pcount/artcount) * 100)
                msgdialogprogress.update(percent, dialogmsg + str(pcount) + " of " + str(artcount))
                xbmc.sleep(50) 

        if artcount > 500:
            msgdialogprogress.close()

        logdb.commit()
        logdb.close()

        xbmc.executebuiltin('Dialog.Close(all, true)')
        xbmc.sleep(200)
                
        artdialog = xbmcgui.Dialog()
        dialog_text = translate(30447) + str(skipped) + '\n' + translate(30448)  + str(found) + \
        '\n' + translate(30449)  + str(notfound)
        artdialog.ok(translate(30450) + str(artcount) + translate(30451), dialog_text)

        kgenlogUpdate('Video Artwork Validation Results: ' + dialog_text.replace('\n', ' '), 'No')


def cleanArt(dbtype):                                                    # Remoe missing artwork file entries in art table

        logdb = openKscleanDB()

        aurpf = logdb.execute('SELECT * FROM art_temp WHERE status like ?', ('%not found%',))
        artuples = aurpf.fetchall()
        artlen = len(artuples)
        logdb.close()

        xbmc.log('KS Cleaner video artwork clean count: ' + str(artlen), xbmc.LOGDEBUG) 

        if artlen == 0:
            kgenlogUpdate('KS Cleaner Video Artwork Validation Results - No artwork to clean', 'No')
            return

        xbmc.executebuiltin('Dialog.Close(all, true)')
        xbmc.sleep(200)
        
        dialoghead = translate(30436) + " - " + str(artlen) + " " + translate(30327)
        dialogmsg = translate(30621)
        select = xbmcgui.Dialog().yesno(dialoghead, dialogmsg)
        if not select:
            kgenlogUpdate('KS Cleaner Video Artwork Validation Cleaning cancelled. ', 'No')
            return

        kvfile = openKodiDB(dbtype)                                        # Open Kodi video database
        if dbtype == "mysql":
            arcursor = kvfile.cursor()

        for art in artuples:
            if dbtype == 'mysql':
                dquery = "DELETE FROM art WHERE art_id = %d" 
                varquery = list(art[0])   
                arcursor.execute(dquery, varquery)
            else:   
                kvfile.execute('DELETE FROM art WHERE art_id = ?', (art[0],))

            kgenlog = 'KS Cleaner cleaned art table entry: ' +  str(art[0])  + ' - ' + art[4]
            kgenlogUpdate(kgenlog, 'No')                

        kvfile.commit()
        if dbtype == 'mysql':
            arcursor.close() 
        kvfile.close()

 
       
