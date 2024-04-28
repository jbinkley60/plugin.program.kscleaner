import xbmc
import xbmcgui
import xbmcplugin
import os, sys, linecache, json
import xbmcaddon
import xbmcvfs
import csv  
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception, translate
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature, openKodiTeDB, settings
from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'


def exportData(selectbl, dbtype = None, tablenm = None):         # CSV Output selected table

    dbextype = settings('dbtype')
    dbmuextype = settings('mudbtype')

    try:
        #xbmc.log("KS Cleaner selectable is: " +  str(selectbl), xbmc.LOGNINFO)

        folderpath = xbmcvfs.translatePath(os.path.join("special://home/", "output/"))
        if not xbmcvfs.exists(folderpath):
            xbmcvfs.mkdir(folderpath)
            xbmc.log("Kodi Export Output folder not found: " +  str(folderpath), xbmc.LOGINFO)
        selectindex = 100
        for a in range(len(selectbl)):
            fpart = datetime.now().strftime('%H%M%S')
            if dbtype == None :                                  # Logs CSV export
                selectindex = int(selectbl[a][:2])               # Get list index to determine DB
                selectname = selectbl[a][2:]                     # Parse table name in DB

                #xbmc.log("Mezzmo selectable is: " +  str(selectindex) + ' ' + selectname, xbmc.LOGINFO)
                if selectindex < 21:                             # Export Kodi video DB tables
                    dbexport = openKodiDB(dbextype)
                    dbase = 'videos_'
                elif selectindex < 41:                           # Export Kodi music DB tables
                    dbexport = openKodiMuDB(dbmuextype)
                    dbase = 'music_'
                else:
                    dbexport = openKodiTeDB()                    # Export Kodi video textures tables
                    dbase = 'textures_'                
            elif dbtype == 'analyzer':                           # Export video / music analyzer output
                selectname = selectbl[0]                
                dbexport = openKscleanDB()
            elif dbtype == 'logs':                               # Export KS Cleaner logs
                selectname = selectbl[0]
                dbexport = openKscleanDB()
                dbase = 'addon_'

            if dbtype == 'analyzer':
                outfile = folderpath + "kscleaner_video_analyzer_" + tablenm + "_" + fpart + ".csv"                
            else:
                outfile = folderpath + "kscleaner_" + dbase + selectname + "_" + fpart + ".csv"
            if dbextype == 'mysql' and dbtype != 'analyzer' and selectindex < 21:
                kcursor = dbexport.cursor()
                kcursor.execute("SELECT * FROM %s"% selectname)
                recs = kcursor.fetchall()
                kcursor.column_names
                headers = [i[0] for i in kcursor.description]
                kcursor.close()
            elif dbmuextype == 'mysql' and dbtype != 'analyzer' and selectindex < 41:
                kcursor = dbexport.cursor()
                kcursor.execute("SELECT * FROM %s"% selectname)
                recs = kcursor.fetchall()
                kcursor.column_names
                headers = [i[0] for i in kcursor.description]
                kcursor.close()
            else: 
                curm = dbexport.execute('SELECT * FROM '+selectname+'')
                recs = curm.fetchall()
                headers = [i[0] for i in curm.description]
            csvFile = csv.writer(open(outfile, 'w', encoding='utf-8'),
                             delimiter=',', lineterminator='\n',
                             quoting=csv.QUOTE_ALL, escapechar='\\')

            csvFile.writerow(headers)                       # Add the headers and data to the CSV file.
            for row in recs:
                recsencode = []
                for item in range(len(row)):
                    if isinstance(row[item], int) or isinstance(row[item], float):  # Convert to strings
                        rectemp = str(row[item])
                        try:
                            recitem = rectemp.decode('utf-8')
                        except:
                            recitem = rectemp
                    else:
                        rectemp = row[item]
                        try:
                            recitem = rectemp.decode('utf-8').replace('[COLOR blue]', '').replace('[/COLOR]', '')
                        except:
                            if rectemp != None:
                               recitem = str(rectemp).replace('[COLOR blue]', '').replace('[/COLOR]', '')
                            else:
                               recitem = rectemp
                    recsencode.append(recitem) 
                csvFile.writerow(recsencode)                
            dbexport.close()

        outmsg = folderpath
        dialog_text = translate(30318) + outmsg 
        xbmcgui.Dialog().ok(translate(30319), dialog_text)

    except Exception as e:
        printexception()
        dbexport.close()
        if 'videoversion' in selectname:
            mgenlog = translate(30320) + ': ' + selectname + ' ' + translate(30402)
        else:
            mgenlog = translate(30320) + ': ' + selectname
        xbmcgui.Dialog().notification(translate(30308), mgenlog, addon_icon, 5000)            
        xbmc.log(mgenlog, xbmc.LOGINFO)


def selectExport():                                            # Select table to export

    try:
        while True:
            stable = []
            selectbl = []
            tables = ["Kodi Video DB - Actors","Kodi Video DB - Episodes","Kodi Video DB - Movies",              \
            "Kodi Video DB - TV Shows","Kodi Video DB - Artwork","Kodi Video DB - Path","Kodi Video DB - Files", \
            "Kodi Video DB - Streamdetails", "Kodi Video DB - Seasons", "Kodi Video DB - Episode View",          \
            "Kodi Video DB - Movie View",  "Kodi Video DB - actor_link", "Kodi Video DB - director_link",        \
            "Kodi Video DB - writer_link", "Kodi Video DB - uniqueid",  "Kodi Video DB - Music Video View",      \
            "Kodi Video DB - Video Version", "Kodi Video DB - Video Version Type",                               \
            "Kodi Music DB - Artist","Kodi Music DB - Album Artist View",                                        \
            "Kodi Music DB - Album View ","Kodi Music DB - Artist View", "Kodi Music DB - Song",                 \
            "Kodi Music DB - Song Artist View","Kodi Music DB - Song View","Kodi Music DB - Path",               \
            "Textures DB - Path","Textures DB - Sizes","Textures DB - Texture"]
            ddialog = xbmcgui.Dialog()    
            stable = ddialog.multiselect(translate(30306) + ' - ' + translate(30317), tables)
            if stable == None:                                 # User cancel
                break
            if 0 in stable:
                selectbl.append('00actor')
            if 1 in stable:
               selectbl.append('01episode')   
            if 2 in stable:
                selectbl.append('02movie')
            if 3 in stable:
                selectbl.append('03tvshow')
            if 4 in stable:
                selectbl.append('04art')    
            if 5 in stable:
                selectbl.append('05path')  
            if 6 in stable:
                selectbl.append('06files')  
            if 7 in stable:
                selectbl.append('07streamdetails')
            if 8 in stable:
                selectbl.append('08seasons')
            if 9 in stable:
                selectbl.append('09episode_view')
            if 10 in stable:
                selectbl.append('10movie_view')
            if 11 in stable:
                selectbl.append('11actor_link')
            if 12 in stable:
                selectbl.append('12director_link')
            if 13 in stable:
                selectbl.append('13writer_link')
            if 14 in stable:
                selectbl.append('14uniqueid')
            if 15 in stable:
                selectbl.append('15musicvideo_view')
            if 16 in stable:
                selectbl.append('16videoversion')
            if 17 in stable:
                selectbl.append('17videoversiontype')
            if 18 in stable:
                selectbl.append('21artist')
            if 19 in stable:
                selectbl.append('22albumartistview')
            if 20 in stable:
                selectbl.append('23albumview')
            if 21 in stable:
                selectbl.append('24artistview')
            if 22 in stable:
                selectbl.append('25song')
            if 23 in stable:
                selectbl.append('26songartistview')
            if 24 in stable:
                selectbl.append('27songview')
            if 25 in stable:
                selectbl.append('28path')
            if 26 in stable:
                selectbl.append('41path')
            if 27 in stable:
                selectbl.append('42sizes')
            if 28 in stable:
                selectbl.append('43texture')

            exportData(selectbl)         

    except Exception as e:
        printexception()


