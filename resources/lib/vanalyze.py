import xbmc
import xbmcgui
import xbmcplugin
import os, sys, linecache, json
import xbmcaddon
import xbmcvfs
import csv  
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception, translate, nofeature
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature, openKodiTeDB, tempDisplay, settings
from resources.lib.exports import exportData
from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'

def vanalMenu(dbtype):                                     # Select table to exportanalyze
    try:
        while True:
            stable = []
            menuitem1 = translate(30341)
            menuitem2 = translate(30342)
            menuitem3 = translate(30343)
            menuitem4 = translate(30344)
            menuitem5 = translate(30345)		   # episode table
            if settings('strictfile') == 'false':
                menuitem6 = translate(30346)		   # file table
            else:
                menuitem6 = translate(30375)
            menuitem7 = translate(30347)		   # movie table
            menuitem8 = translate(30348)		   # musicvideo table
            menuitem9 = translate(30349)		   # sets table
            menuitem10 = translate(30350)		   # streamdetails table
            menuitem11 = translate(30351)		   # tvshow table
            menuitem12 = translate(30352)		   # writer_link table
            menuitem13 = translate(30359)		   # genre_link table
            menuitem14 = translate(30360)		   # seasons table
            menuitem15 = translate(30361)		   # tag_link table
            menuitem16 = translate(30379)		   # path table
            selectbl = [menuitem1, menuitem2, menuitem3, menuitem4, menuitem5, menuitem6,    \
            menuitem13, menuitem7, menuitem8, menuitem16, menuitem14, menuitem9, menuitem10, \
            menuitem15, menuitem11, menuitem12,]
            ddialog = xbmcgui.Dialog()    
            stable = ddialog.select(translate(30306) + ' - ' + translate(30340), selectbl)
            if stable < 0:                                 # User cancel
                break
            else:
                vanalfMenu(selectbl[stable], dbtype)

    except Exception as e:
        printexception()


def vanalfMenu(vtable, dbtype):                            # Select analyzer function 

    try:
        xbmc.log('Kodi selective cleaner analyzer selection is: ' + vtable, xbmc.LOGDEBUG)
        sfunction = []
        menuitem1 = translate(30353)
        menuitem2 = translate(30354)
        menuitem3 = translate(30355)

        selectfn = [menuitem1, menuitem2, menuitem3]
        ddialog = xbmcgui.Dialog()    
        sfunction = ddialog.select(translate(30306) + ' - ' + translate(30356), selectfn)
        if sfunction < 0:                                 # User cancel
            return
        if menuitem1 in selectfn[sfunction]:
            alrecs = vdbAnalysis(vtable, dbtype)
            kgenlog = ('Video DB Analysis - ' +  vtable + ' - ' + str(alrecs) + ' unmatched found')
            kgenlogUpdate(kgenlog, 'No')
            if alrecs != None and alrecs > 0:
                ccounts = getCounts()                      #  Gets counts for output table vheader
                vheader = getHeader(vtable)
                tempDisplay(vtable, vheader, ccounts)
            elif alrecs != None and alrecs == 0:
                displayClean(vtable)
            else:
                nofeature()
        elif menuitem2 in selectfn[sfunction]:
            alrecs = vdbAnalysis(vtable, dbtype)
            kgenlog = ('Video DB Analysis CSV - ' +  vtable + ' - ' + str(alrecs) + ' unmatched found')
            kgenlogUpdate(kgenlog, 'No')
            if alrecs != None and alrecs > 0:
                exportData(['vdb_temp'], 'analyzer', vtable)
            elif alrecs != None and alrecs == 0:
                displayClean(vtable)
            else:
                nofeature() 
        elif menuitem3 in selectfn[sfunction]:
            alrecs = vdbAnalysis(vtable, dbtype)
            kgenlog = ('Video DB Analysis Clean - ' +  vtable + ' - ' + str(alrecs) + ' unmatched found')
            kgenlogUpdate(kgenlog, 'No')
            if alrecs != None and alrecs > 0:
                if checkClean(vtable):
                    ccount = vdbClean(vtable, dbtype)
                    finishClean(vtable, ccount) 
                else:
                    kgenlog = ('Video DB Analysis Clean - ' +  vtable + ' - user cancelled')
                    kgenlogUpdate(kgenlog, 'No')
                    return 
            elif alrecs != None and alrecs == 0:
                displayClean(vtable)
            else:
                nofeature() 

    except Exception as e:
        printexception()    


def getCounts():                                        # Get clean and data error counts 

    try:
        countdb = openKscleanDB()

        curc = countdb.execute('SELECT count (*) FROM vdb_temp WHERE clean = "Yes" ')
        ccount = curc.fetchone()
        curb = countdb.execute('SELECT count (*) FROM vdb_temp WHERE clean = "No" ')
        bcount = curb.fetchone()        
        xbmc.log('KS Cleaner counts: ' + str(bcount[0]) + '  ' + str(ccount[0]), xbmc.LOGDEBUG)        
        countdb.close()

        return (str(bcount[0]), str(ccount[0]))

    except Exception as e:
        printexception()  


def vdbAnalysis(vtable, dbtype):                        # Analyze table

    try:
        kodidb = openKodiDB(dbtype)
        outdb = openKscleanDB()

        outdb.execute('DROP table IF EXISTS vdb_temp')  # Drop temporary output table
        outdb.commit()

        dquery = "DROP table IF EXISTS files_temp"
        try:
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute(dquery)
                kcursor.commit()
                kcursor.close()
            else:
                kodidb.execute('DROP table IF EXISTS files_temp')   # Drop temporary Kodi table
                kodidb.commit()
        except:
            pass

        if vtable == 'actor_link':                      # Check tables for unmatched data
            if dbtype == 'mysql':
                aquery = "SELECT * FROM actor_link WHERE actor_id not in      \
                (SELECT actor_id FROM actor)"
                kcursor = kodidb.cursor()
                kcursor.execute(aquery)
                alist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM actor_link WHERE media_id not in      \
                (SELECT idMovie FROM movie) and media_type = 'movie'")
                mlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM actor_link WHERE media_id not in      \
                (SELECT idEpisode FROM episode) and media_type = 'espisode'")
                elist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM actor_link WHERE media_id not in      \
                (SELECT idShow FROM tvshow) and media_type = 'tvshow'")
                tlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM actor_link WHERE media_id not in      \
                (SELECT idMVideo FROM musicvideo) and media_type = 'musicvideo'")
                vlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM actor_link WHERE media_id not in      \
                (SELECT idSeason FROM seasons) and media_type = 'season'")
                slist = kcursor.fetchall()
                kcursor.close()
            else:  
                cura = kodidb.execute('SELECT * FROM actor_link WHERE actor_id not in      \
                (SELECT actor_id FROM actor)')
                curm = kodidb.execute('SELECT * FROM actor_link WHERE media_id not in      \
                (SELECT idMovie FROM movie) and media_type = "movie" ')
                cure = kodidb.execute('SELECT * FROM actor_link WHERE media_id not in      \
                (SELECT idEpisode FROM episode) and media_type = "episode" ')
                curt = kodidb.execute('SELECT * FROM actor_link WHERE media_id not in      \
                (SELECT idShow FROM tvshow) and media_type = "tvshow" ') 
                curv = kodidb.execute('SELECT * FROM actor_link WHERE media_id not in      \
                (SELECT idMVideo FROM musicvideo) and media_type = "musicvideo" ') 
                curs = kodidb.execute('SELECT * FROM actor_link WHERE media_id not in      \
                (SELECT idSeason FROM seasons) and media_type = "season" ')    
                alist = cura.fetchall()
                mlist = curm.fetchall()
                elist = cure.fetchall()
                tlist = curt.fetchall()
                vlist = curv.fetchall()
                slist = curs.fetchall()
                del cura, curm, cure, curt, curv, curs
            kodidb.close()
            orprecs = len(alist) + len(mlist) + len(elist) + len(tlist) + len(vlist) + len(slist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)) + ' ' +  str(len(mlist))  \
            + ' ' + str(len(elist)) + ' ' + str(len(tlist)) + ' ' + str(len(vlist)) + ' ' +          \
            str(len(slist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(actor_id INTEGER, media_id INTEGER, media_type TEXT, \
            role TEXT, cast_order INTEGER, clean TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add actor unmatcheds
                for a in range(len(alist)):
                    acomment = '[COLOR blue]' + "{:<47}".format('actor_link table actor unmatched')       \
                    +  '[/COLOR]' + "{:10d}".format(int(alist[a][0])) + "{:10d}".format(int(alist[a][1])) \
                    +   "{:<8}".format(' ') + "{:<16}".format(str(alist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,        \
                    clean, comments) values (?, ?, ?, ?, ?)', (alist[a][0], alist[a][1], alist[a][2],     \
                    'Yes', acomment))
                outdb.commit()
                      
            if len(mlist) > 0:                            # Add movie unmatcheds
                for a in range(len(mlist)):
                    acomment = '[COLOR blue]' + "{:<46}".format('actor_link table movie unmatched')       \
                    +  '[/COLOR]' + "{:10d}".format(int(mlist[a][0])) + "{:10d}".format(int(mlist[a][1])) \
                    +   "{:<8}".format(' ') + "{:<16}".format(str(mlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,        \
                    clean, comments) values (?, ?, ?, ?, ?)', (mlist[a][0], mlist[a][1], mlist[a][2],     \
                    'Yes', acomment))
                outdb.commit()

            if len(elist) > 0:                            # Add episode unmatcheds
                for a in range(len(elist)):
                    acomment = '[COLOR blue]' + "{:<47}".format('actor_link table episode unmatched')     \
                    +  '[/COLOR]' + "{:10d}".format(int(elist[a][0])) + "{:10d}".format(int(elist[a][1])) \
                    +   "{:<8}".format(' ') + "{:<16}".format(str(elist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,        \
                    clean, comments) values (?, ?, ?, ?, ?)', (elist[a][0], elist[a][1], elist[a][2],     \
                    'Yes', acomment))
                outdb.commit()

            if len(tlist) > 0:                            # Add tvshow unmatcheds
                for a in range(len(tlist)):
                    acomment = '[COLOR blue]' + "{:<46}".format('actor_link table tvshow unmatched')      \
                    +  '[/COLOR]' + "{:10d}".format(int(tlist[a][0])) + "{:10d}".format(int(tlist[a][1])) \
                    +   "{:<8}".format(' ') + "{:<16}".format(str(tlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,        \
                    clean, comments) values (?, ?, ?, ?, ?)', (tlist[a][0], tlist[a][1], tlist[a][2],     \
                    'Yes', acomment))
                outdb.commit()

            if len(vlist) > 0:                            # Add musicvideo unmatcheds
                for a in range(len(vlist)):
                    acomment = '[COLOR blue]' + "{:<42}".format('actor_link table musicvideo unmatched')  \
                    +  '[/COLOR]' + "{:10d}".format(int(vlist[a][0])) + "{:10d}".format(int(vlist[a][1])) \
                    +   "{:<8}".format(' ') + "{:<16}".format(str(vlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,        \
                    clean, comments) values (?, ?, ?, ?, ?)', (vlist[a][0], vlist[a][1], vlist[a][2],     \
                    'Yes', acomment))
                outdb.commit()

            if len(alist) > 0:                            # Add seasons unmatcheds
                for a in range(len(alist)):
                    acomment = '[COLOR blue]' + "{:<45}".format('actor_link table seasons unmatched')     \
                    +  '[/COLOR]' + "{:10d}".format(int(alist[a][0])) + "{:10d}".format(int(alist[a][1])) \
                    +   "{:<8}".format(' ') + "{:<16}".format(str(alist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,        \
                    clean, comments) values (?, ?, ?, ?, ?)', (alist[a][0], alist[a][1], alist[a][2],     \
                    'Yes', acomment))
                outdb.commit()                         
            outdb.close()
            return orprecs

        #==========================  Actor Table analysis ================================

        if vtable == 'actor':                            # Check tables for unmatched data
            #aquery = "SELECT * FROM actor WHERE actor_id not in (SELECT actor_id FROM actor_link       \
            #where actor_id is not NULL) or (SELECT actor_id FROM director_link where actor_id is       \
            #not NULL) "
            #aquery = "SELECT * FROM actor WHERE actor_id not in (SELECT actor_id FROM actor_link       \
            #where actor_id is not NULL) or (SELECT actor_id FROM director_link where actor_id is       \
            #not NULL) " 
            if dbtype == 'mysql':
                dquery = "CREATE TABLE files_temp(actor_id INTEGER)"
                kcursor = kodidb.cursor()
                kcursor.execute("CREATE TABLE IF NOT EXISTS files_temp(actor_id INT)")
                kcursor.execute("CREATE INDEX file_1 ON files_temp (actor_id)")
                kodidb.commit()
                kcursor.execute("INSERT INTO files_temp (actor_id) select distinct actor_id from actor_link")
                kcursor.execute("INSERT INTO files_temp (actor_id) select distinct actor_id from director_link")
                kcursor.execute("INSERT INTO files_temp (actor_id) select distinct actor_id from writer_link")
                kodidb.commit()

                kcursor.execute("SELECT * FROM actor WHERE actor_id not in          \
                (SELECT actor_id FROM files_temp)")
                alist = kcursor.fetchall()
                kcursor.close()
            else:
                kodidb.execute('CREATE TABLE files_temp(actor_id INTEGER)')
                kodidb.execute('CREATE INDEX IF NOT EXISTS file_1 ON files_temp (actor_id)')
                kodidb.commit()
                kodidb.execute('INSERT INTO files_temp (actor_id) select distinct actor_id from actor_link')
                kodidb.execute('INSERT INTO files_temp (actor_id) select distinct actor_id from director_link')
                kodidb.execute('INSERT INTO files_temp (actor_id) select distinct actor_id from writer_link')
                kodidb.commit()
             
                cura = kodidb.execute('SELECT * FROM actor WHERE actor_id not in          \
                (SELECT actor_id FROM files_temp)')
                alist = cura.fetchall()
                del cura
            kodidb.close()
            orprecs = len(alist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(actor_id INTEGER, name TEXT, art_urls TEXT,        \
            clean TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add actor_link unmatcheds
                for a in range(len(alist)):
                    acomment = '[COLOR blue]' + "{:<32}".format('actor table actor_link missing') + \
                    '[/COLOR]' + "{:12d}".format(int(str(alist[a][0]))) + "{:<12}".format(' ') +    \
                     str(alist[a][1])
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, name, clean, comments)  \
                    values (?, ?, ?, ?)', (alist[a][0], alist[a][1], 'Yes', acomment))
                outdb.commit()
            outdb.close()
            return orprecs

        #=========================  Art Table analysis ============================

        if vtable == 'art':                       # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM art WHERE media_id not in      \
                (SELECT idSet FROM sets) and media_type = 'sets' ")
                alist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM art WHERE media_id not in      \
                (SELECT idMovie FROM movie) and media_type = 'movie' ")
                mlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM art WHERE media_id not in      \
                (SELECT idEpisode FROM episode) and media_type = 'episode' ")
                elist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM art WHERE media_id not in      \
                (SELECT idShow FROM tvshow) and media_type = 'tvshow' ")
                tlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM art WHERE media_id not in      \
                (SELECT idMVideo FROM musicvideo) and media_type = 'musicvideo' ")
                vlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM art WHERE media_id not in      \
                (SELECT idSeason FROM seasons) and media_type = 'season' ")
                slist = kcursor.fetchall()
                kcursor.close()
            else: 
                cura = kodidb.execute('SELECT * FROM art WHERE media_id not in      \
                (SELECT idSet FROM sets) and media_type = "sets" ')
                curm = kodidb.execute('SELECT * FROM art WHERE media_id not in      \
                (SELECT idMovie FROM movie) and media_type = "movie" ')
                cure = kodidb.execute('SELECT * FROM art WHERE media_id not in      \
                (SELECT idEpisode FROM episode) and media_type = "episode" ')
                curt = kodidb.execute('SELECT * FROM art WHERE media_id not in      \
                (SELECT idShow FROM tvshow) and media_type = "tvshow" ') 
                curv = kodidb.execute('SELECT * FROM art WHERE media_id not in      \
                (SELECT idMVideo FROM musicvideo) and media_type = "musicvideo" ') 
                curs = kodidb.execute('SELECT * FROM art WHERE media_id not in      \
                (SELECT idSeason FROM seasons) and media_type = "season" ')    
                alist = cura.fetchall()
                mlist = curm.fetchall()
                elist = cure.fetchall()
                tlist = curt.fetchall()
                vlist = curv.fetchall()
                slist = curs.fetchall()
                del cura, curm, cure, curt, curv, curs
            kodidb.close()
            orprecs = len(alist) + len(mlist) + len(elist) + len(tlist) + len(vlist) + len(slist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)) + ' ' +  str(len(mlist)) \
            + ' ' + str(len(elist)) + ' ' + str(len(tlist)) + ' ' + str(len(vlist)) + ' ' +         \
            str(len(slist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(art_id INTEGER, media_id INTEGER, media_type TEXT, \
            type TEXT, url TEXT, clean TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add sets unmatcheds
                for a in range(len(alist)):
                    acomment = '[COLOR blue]' +  "{:<47}".format('art table sets unmatched') +              \
                    '[/COLOR]' + "{:10d}".format(int(alist[a][0])) + "{:10d}".format(int(alist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(alist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type, type,      \
                     clean, comments) values (?, ?, ?, ?, ?, ?)', (alist[a][0], alist[a][1], alist[a][2],   \
                     alist[a][3],'Yes', acomment))
                outdb.commit()
                      
            if len(mlist) > 0:                            # Add movie unmatcheds
                for a in range(len(mlist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('art table movie unmatched') +             \
                    '[/COLOR]' + "{:10d}".format(int(mlist[a][0])) + "{:10d}".format(int(mlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(mlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type, type,      \
                    clean, comments) values (?, ?, ?, ?, ?, ?)', (mlist[a][0], mlist[a][1], mlist[a][2],    \
                    mlist[a][3],'Yes', acomment))
                outdb.commit()

            if len(elist) > 0:                            # Add episode unmatcheds
                for a in range(len(elist)):
                    acomment = '[COLOR blue]' +  "{:<44}".format('art table episode unmatched') +           \
                    '[/COLOR]' + "{:10d}".format(int(elist[a][0])) + "{:10d}".format(int(elist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(elist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type, type,      \
                    clean, comments) values (?, ?, ?, ?, ?, ?)', (elist[a][0], elist[a][1], elist[a][2],    \
                    elist[a][3], 'Yes', acomment))
                outdb.commit()

            if len(tlist) > 0:                            # Add tvshow unmatcheds
                for a in range(len(tlist)):
                    acomment = '[COLOR blue]' +  "{:<44}".format('art table tvshow unmatched') +            \
                    '[/COLOR]' + "{:10d}".format(int(tlist[a][0])) + "{:10d}".format(int(tlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(tlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type, type,      \
                    clean, comments) values (?, ?, ?, ?, ?, ?)', (tlist[a][0], tlist[a][1], tlist[a][2],    \
                    tlist[a][3], 'Yes', acomment))
                outdb.commit()  

            if len(vlist) > 0:                            # Add musicvideo unmatcheds
                for a in range(len(vlist)):
                    acomment = '[COLOR blue]' +  "{:<41}".format('art table musicvideo unmatched') +        \
                    '[/COLOR]' + "{:10d}".format(int(vlist[a][0])) + "{:10d}".format(int(vlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(vlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type, type,      \
                    clean, comments) values (?, ?, ?, ?, ?, ?)', (vlist[a][0], vlist[a][1], vlist[a][2],    \
                    vlist[a][3], 'Yes', acomment))
                outdb.commit() 

            if len(slist) > 0:                            # Add season unmatcheds
                for a in range(len(slist)):
                    acomment = '[COLOR blue]' +  "{:<44}".format('art table season unmatched') +            \
                    '[/COLOR]' + "{:10d}".format(int(slist[a][0])) + "{:10d}".format(int(slist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(slist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type, type,      \
                    clean, comments) values (?, ?, ?, ?, ?, ?)', (slist[a][0], slist[a][1], slist[a][2],    \
                    slist[a][3], 'Yes', acomment))
                outdb.commit()                            
            outdb.close()
            return orprecs

        #==========================  Director_link Table analysis ===========================

        if vtable == 'director_link':                       # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM director_link WHERE actor_id not in      \
                (SELECT actor_id FROM actor where actor_id is not NULL)")
                alist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM director_link WHERE media_id not in      \
                (SELECT idMovie FROM movie) and media_type = 'movie' ")
                mlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM director_link WHERE media_id not in      \
                (SELECT idEpisode FROM episode) and media_type = 'episode' ")
                elist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM director_link WHERE media_id not in      \
                (SELECT idMVideo FROM musicvideo) and media_type = 'musicvideo' ")
                vlist = kcursor.fetchall()
                kcursor.close()
            else: 
                cura = kodidb.execute('SELECT * FROM director_link WHERE actor_id not in      \
                (SELECT actor_id FROM actor where actor_id is not NULL)')
                curm = kodidb.execute('SELECT * FROM director_link WHERE media_id not in      \
                (SELECT idMovie FROM movie) and media_type = "movie" ')
                cure = kodidb.execute('SELECT * FROM director_link WHERE media_id not in      \
                (SELECT idEpisode FROM episode) and media_type = "episode" ')
                curv = kodidb.execute('SELECT * FROM director_link WHERE media_id not in      \
                (SELECT idMVideo FROM musicvideo) and media_type = "musicvideo" ')  
                alist = cura.fetchall()
                mlist = curm.fetchall()
                elist = cure.fetchall()
                vlist = curv.fetchall()
                del cura, curm, cure, curv
            kodidb.close()
            orprecs = len(alist) + len(mlist) + len(elist) + len(vlist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)) + ' ' +        \
            str(len(mlist)) + ' ' + str(len(elist)) + ' ' + str(len(vlist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(actor_id INTEGER, media_id INTEGER,      \
            media_type TEXT, clean TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add actor unmatcheds
                for a in range(len(alist)):
                    acomment = '[COLOR blue]' +  "{:<47}".format('director_link table actor unmatched') +   \
                    '[/COLOR]' + "{:10d}".format(int(alist[a][0])) + "{:10d}".format(int(alist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(alist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,  clean,  \
                    comments) values (?, ?, ?, ?, ?)', (alist[a][0], alist[a][1], alist[a][2], 'Yes', acomment))
                outdb.commit()
                      
            if len(mlist) > 0:                            # Add movie unmatcheds
                for a in range(len(mlist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('director_link table movie unmatched') +   \
                    '[/COLOR]' + "{:10d}".format(int(mlist[a][0])) + "{:10d}".format(int(mlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(mlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,  clean,  \
                    comments) values (?, ?, ?, ?, ?)', (mlist[a][0], mlist[a][1], mlist[a][2], 'Yes', acomment))
                outdb.commit()

            if len(elist) > 0:                            # Add episode unmatcheds
                for a in range(len(elist)):
                    acomment = '[COLOR blue]' +  "{:<44}".format('director_link table episode unmatched') +  \
                    '[/COLOR]' + "{:10d}".format(int(elist[a][0])) + "{:10d}".format(int(elist[a][1])) +     \
                    "{:<8}".format(' ') + "{:<16}".format(str(elist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,  clean,   \
                    comments) values (?, ?, ?, ?, ?)', (elist[a][0], elist[a][1], elist[a][2], 'Yes', acomment))
                outdb.commit()

            if len(vlist) > 0:                            # Add musicvideo unmatcheds
                for a in range(len(vlist)):
                    acomment = '[COLOR blue]' +  "{:<40}".format('director_link table musicvideo unmatched') + \
                    '[/COLOR]' + "{:10d}".format(int(vlist[a][0])) + "{:10d}".format(int(vlist[a][1])) +       \
                    "{:<8}".format(' ') + "{:<16}".format(str(vlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,  clean,     \
                    comments) values (?, ?, ?, ?, ?)', (vlist[a][0], vlist[a][1], vlist[a][2], 'Yes', acomment))
                outdb.commit() 
                          
            outdb.close()
            return orprecs

        #========================  Episode Table analysis =========================

        if vtable == 'episode':                       # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM episode WHERE idFile not in        \
                (SELECT idFile FROM files where idFile is not NULL)")
                flist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM episode WHERE c03 not in           \
                (SELECT rating_id FROM rating where media_type = 'episode') ")
                rlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM episode WHERE c19 not in           \
                (SELECT idPath FROM path where idPath is not NULL) ")
                plist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM episode WHERE c20 not in           \
                (SELECT uniqueid_id FROM uniqueid where media_type = 'episode') ")
                ulist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM episode WHERE idShow not in        \
                (SELECT idShow FROM tvshow where idShow is not NULL) ")
                tlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM episode WHERE idSeason not in      \
                (SELECT idSeason FROM seasons where idSeason is not NULL) ")
                slist = kcursor.fetchall()
                kcursor.close()
            else:  
                curf = kodidb.execute('SELECT * FROM episode WHERE idFile not in        \
                (SELECT idFile FROM files where idFile is not NULL)')
                curr = kodidb.execute('SELECT * FROM episode WHERE c03 not in           \
                (SELECT rating_id FROM rating where media_type = "episode") ')
                curp = kodidb.execute('SELECT * FROM episode WHERE c19 not in           \
                (SELECT idPath FROM path where idPath is not NULL)')
                curu = kodidb.execute('SELECT * FROM episode WHERE c20 not in           \
                (SELECT uniqueid_id FROM uniqueid where media_type = "episode") ') 
                curt = kodidb.execute('SELECT * FROM episode WHERE idShow not in        \
                (SELECT idShow FROM tvshow where idShow is not NULL)') 
                curs = kodidb.execute('SELECT * FROM episode WHERE idSeason not in      \
                (SELECT idSeason FROM seasons where idSeason is not NULL)')       
                flist = curf.fetchall()
                rlist = curr.fetchall()
                plist = curp.fetchall()
                ulist = curu.fetchall()
                tlist = curt.fetchall()
                slist = curs.fetchall()
                del curf, curr, curp, curu, curt, curs
            kodidb.close()
            orprecs = len(flist) + len(rlist) + len(plist) + len(ulist) + len(tlist) + len(slist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(flist)) + ' ' +  str(len(rlist)) \
            + ' ' + str(len(plist)) + ' ' + str(len(ulist)) + ' ' + str(len(tlist)) + ' ' +         \
            str(len(slist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(idEpisode INTEGER, idFile INTEGER, c00 TEXT,       \
            clean TEXT, comments TEXT)')
            outdb.commit()

            if len(flist) > 0:                            # Add files unmatcheds
                for a in range(len(flist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('episode table files unmatched') +         \
                    '[/COLOR]' + "{:10d}".format(int(flist[a][0])) + "{:10d}".format(int(flist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(flist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idEpisode, idFile, c00, clean,         \
                    comments) values (?, ?, ?, ?, ?)', (flist[a][0], flist[a][1], flist[a][2], 'Yes', acomment))
                outdb.commit()
                      
            if len(rlist) > 0:                            # Add ratings unmatcheds
                for a in range(len(rlist)):
                    acomment = "{:<42}".format('episode table ratings unmatched') +                 \
                    "{:10d}".format(int(rlist[a][0])) + "{:10d}".format(int(rlist[a][1])) +         \
                    "{:<8}".format(' ') + "{:<16}".format(str(rlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idEpisode, idFile, c00, clean,   \
                    comments) values (?, ?, ?, ?, ?)', (rlist[a][0], rlist[a][1], rlist[a][2], 'No', acomment))
                outdb.commit()

            if len(plist) > 0:                            # Add path unmatcheds
                for a in range(len(plist)):
                    acomment = "{:<44}".format('episode table path unmatched') +                    \
                    "{:10d}".format(int(plist[a][0])) + "{:10d}".format(int(plist[a][1])) +         \
                    "{:<8}".format(' ') + "{:<16}".format(str(plist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idEpisode, idFile, c00, clean,   \
                    comments) values (?, ?, ?, ?, ?)', (plist[a][0], plist[a][1], plist[a][2], 'No', acomment))
                outdb.commit()

            if len(ulist) > 0:                            # Add uniqueid unmatcheds
                for a in range(len(ulist)):
                    acomment = "{:<41}".format('episode table uniqueid unmatched') +                \
                    "{:10d}".format(int(ulist[a][0])) + "{:10d}".format(int(ulist[a][1])) +         \
                    "{:<8}".format(' ') + "{:<16}".format(str(ulist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idEpisode, idFile, c00, clean,   \
                    comments) values (?, ?, ?, ?, ?)', (ulist[a][0], ulist[a][1], ulist[a][2], 'No', acomment))
                outdb.commit()  

            if len(tlist) > 0:                            # Add tvshows unmatcheds
                for a in range(len(tlist)):
                    acomment = "{:<40}".format('episode table tvshow unmatched') +                  \
                    "{:10d}".format(int(tlist[a][0])) + "{:10d}".format(int(tlist[a][1])) +         \
                    "{:<8}".format(' ') + "{:<16}".format(str(tlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idEpisode, idFile, c00, clean,   \
                    comments) values (?, ?, ?, ?, ?)', (tlist[a][0], tlist[a][1], tlist[a][2], 'No', acomment))
                outdb.commit() 

            if len(slist) > 0:                            # Add season unmatcheds
                for a in range(len(slist)):
                    acomment = "{:<42}".format('episode table season unmatched') +                  \
                    "{:10d}".format(int(slist[a][0])) + "{:10d}".format(int(slist[a][1])) +         \
                    "{:<8}".format(' ') + "{:<16}".format(str(slist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idEpisode, idFile, c00, clean,   \
                    comments) values (?, ?, ?, ?, ?)', (slist[a][0], slist[a][1], slist[a][2], 'No', acomment))
                outdb.commit()                            
            outdb.close()
            return orprecs

        #======================  Files Table Strict analysis =========================

        if 'strict' in vtable:                       # Check tables for unmatched data
            if dbtype == 'mysql':
                dquery = "CREATE TABLE files_temp(idFile INTEGER)"
                kcursor = kodidb.cursor()
                kcursor.execute("CREATE TABLE IF NOT EXISTS files_temp(idFile INT)")
                kcursor.execute("CREATE INDEX file_1 ON files_temp (idFile)")
                kodidb.commit()
                kcursor.execute("INSERT INTO files_temp (idFile) select distinct idFile from movie")
                kcursor.execute("INSERT INTO files_temp (idFile) select distinct idFile from episode")
                kcursor.execute("INSERT INTO files_temp (idFile) select distinct idFile from musicvideo")
                kodidb.commit()

                kcursor.execute("SELECT * FROM files WHERE idFile not in          \
                (SELECT idFile FROM files_temp)")
                flist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM files WHERE idFile not in (SELECT  \
                idFile FROM streamdetails WHERE iStreamType = '0') ")
                alist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM files WHERE idFile not in (SELECT  \
                idFile FROM streamdetails WHERE iStreamType = '1')  ")
                mlist = kcursor.fetchall()
                kcursor.close()

            else:            
                kodidb.execute('CREATE TABLE files_temp(idFile INTEGER)')
                kodidb.execute('CREATE INDEX IF NOT EXISTS file_1 ON files_temp (idFile)')
                kodidb.commit()
                kodidb.execute('INSERT INTO files_temp (idFile) select distinct idFile from movie')
                kodidb.execute('INSERT INTO files_temp (idFile) select distinct idFile from episode')
                kodidb.execute('INSERT INTO files_temp (idFile) select distinct idFile from musicvideo')
                kodidb.commit()
             
                curf = kodidb.execute('SELECT * FROM files WHERE idFile not in          \
                (SELECT idFile FROM files_temp)')
                cura = kodidb.execute('SELECT * FROM files WHERE idFile not in (SELECT  \
                idFile FROM streamdetails WHERE iStreamType = 0) ')
                curm = kodidb.execute('SELECT * FROM files WHERE idFile not in (SELECT  \
                idFile FROM streamdetails WHERE iStreamType = 1) ')
                alist = cura.fetchall()
                mlist = curm.fetchall()
                flist = curf.fetchall()
                del cura, curm, curf
            kodidb.close()
            orprecs = len(alist) + len(mlist) + len(flist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)) + ' ' +  str(len(mlist)) \
            + ' ' + str(len(flist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(idFile integer, idPath integer, strFilename text,  \
            playCount integer, lastPlayed text, dateAdded text, clean TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add audio codes unmatcheds
                for a in range(len(alist)):
                    acomment = "{:<55}".format('files table streamdetails audio unmatched') +                   \
                    "{:10d}".format(int(alist[a][0])) + "{:10d}".format(int(alist[a][1])) + "{:<8}".format(' ') \
                    + "{:<16}".format(str(alist[a][5]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idFile, idPath, dateAdded, clean, comments)   \
                    values (?, ?, ?, ?, ?)', (alist[a][0], alist[a][1], alist[a][5], 'No', acomment))
                outdb.commit()
                      
            if len(mlist) > 0:                            # Add video codecs unmatcheds
                for a in range(len(mlist)):
                    acomment = "{:<55}".format('files table streamdetails video unmatched') +                    \
                    "{:10d}".format(int(mlist[a][0])) + "{:10d}".format(int(mlist[a][1])) + "{:<8}".format(' ')  \
                    + "{:<16}".format(str(mlist[a][5]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idFile, idPath, dateAdded, clean, comments)   \
                    values (?, ?, ?, ?, ?)', (mlist[a][0], mlist[a][1], mlist[a][5], 'No', acomment))
                outdb.commit()

            if len(flist) > 0:                            # Add movie, episode, musicvideos unmatcheds
                for a in range(len(flist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('files table movie, episode, musicvideo unmatched') \
                    + '[/COLOR]' + "{:10d}".format(int(flist[a][0])) + "{:10d}".format(int(flist[a][1])) +           \
                    "{:<8}".format(' ') + "{:<16}".format(str(flist[a][5]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idFile, idPath, dateAdded, clean, comments)  \
                    values (?, ?, ?, ?, ?)', (flist[a][0], flist[a][1], flist[a][5], 'Yes', acomment))
                outdb.commit()                          
            outdb.close()
            kodidb.close()
            return orprecs

        #=======================  Files Normal Table analysis =============================

        if vtable == 'files':                            # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM files WHERE idPath not in (SELECT idPath FROM       \
                path  where idPath is not NULL) ")
                alist = kcursor.fetchall()
                kcursor.close()
            else:  
                cura = kodidb.execute('SELECT * FROM files WHERE idPath not in (SELECT idPath FROM   \
                path  where idPath is not NULL)')
                alist = cura.fetchall()
                del cura
            kodidb.close()
            orprecs = len(alist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(idFile integer, idPath integer, strFilename text,    \
            playCount integer, lastPlayed text, dateAdded text, clean TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add path unmatcheds
                for a in range(len(alist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('files table path unmatched')                  \
                    + '[/COLOR]' + "{:10d}".format(int(alist[a][0])) + "{:10d}".format(int(alist[a][1])) +      \
                    "{:<8}".format(' ') + "{:<16}".format(str(alist[a][5]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idFile, idPath, dateAdded, clean, comments)  \
                    values (?, ?, ?, ?, ?)', (alist[a][0], alist[a][1], alist[a][5], 'Yes', acomment))
                outdb.commit()
            outdb.close()
            return orprecs


        #============================  Path Table analysis ==============================

        if vtable == 'path':                            # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("select * from path where idPath not in(select idPath from files) and \
                idPath not in (select idParentPath from path where idParentPath is not NULL) ")
                alist = kcursor.fetchall()
                kcursor.close()
            else:  
                cura = kodidb.execute('select * from path where idPath not in(select idPath from   \
                files) and idPath not in (select idParentPath from path where idParentPath is not NULL)')
                alist = cura.fetchall()
                del cura
            kodidb.close()
            orprecs = len(alist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(idPath integer, strPath text, strContent text,    \
            dateAdded text, clean TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add files unmatcheds
                for a in range(len(alist)):
                    acomment = '[COLOR blue]' +  "{:<32}".format('path table files unmatched') + '[/COLOR]'       \
                    + "{:10d}".format(int(alist[a][0])) + "{:<8}".format(' ') + "{:<36}".format(alist[a][1][:36]) \
                    + "{:<8}".format(' ') + "{:<16}".format(str(alist[a][11]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idPath, strPath, strContent, dateAdded,      \
                    clean, comments) values (?, ?, ?, ?, ?, ?)', (alist[a][0], alist[a][1], alist[a][2],        \
                    alist[a][11], 'Yes', acomment))
                outdb.commit()
            outdb.close()
            return orprecs


        #==========================  Genre_link Table analysis ===========================

        if vtable == 'genre_link':                       # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM genre_link WHERE media_id not in      \
                (SELECT idMovie FROM movie) and media_type = 'movie' ")
                mlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM genre_link WHERE media_id not in      \
                (SELECT idEpisode FROM episode) and media_type = 'episode' ")
                elist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM genre_link WHERE media_id not in      \
                (SELECT idShow FROM tvshow) and media_type = 'tvshow' ")
                slist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM genre_link WHERE media_id not in      \
                (SELECT idMVideo FROM musicvideo) and media_type = 'musicvideo' ")
                vlist = kcursor.fetchall()
                kcursor.close()
            else: 
                curm = kodidb.execute('SELECT * FROM genre_link WHERE media_id not in      \
                (SELECT idMovie FROM movie) and media_type = "movie" ')
                cure = kodidb.execute('SELECT * FROM genre_link WHERE media_id not in      \
                (SELECT idEpisode FROM episode) and media_type = "episode" ')
                curs = kodidb.execute('SELECT * FROM genre_link WHERE media_id not in      \
                (SELECT idShow FROM tvshow) and media_type = "tvshow" ')
                curv = kodidb.execute('SELECT * FROM genre_link WHERE media_id not in      \
                (SELECT idMVideo FROM musicvideo) and media_type = "musicvideo" ')  
                mlist = curm.fetchall()
                elist = cure.fetchall()
                slist = curs.fetchall()
                vlist = curv.fetchall()
                del curm, cure, curs, curv
            kodidb.close()
            orprecs = len(mlist) + len(elist) + len(slist) + len(vlist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(mlist)) + ' '     \
            + str(len(elist)) + ' ' + str(len(slist)) + ' ' +       \
            str(len(vlist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(genre_id INTEGER, media_id INTEGER,      \
            media_type TEXT, clean TEXT, comments TEXT)')
            outdb.commit()
                      
            if len(mlist) > 0:                            # Add movie unmatcheds
                for a in range(len(mlist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('genre_link table movie unmatched') +      \
                    '[/COLOR]' + "{:10d}".format(int(mlist[a][0])) + "{:10d}".format(int(mlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(mlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(genre_id, media_id, media_type, clean,   \
                    comments) values (?, ?, ?, ?, ?)', (mlist[a][0], mlist[a][1], mlist[a][2], 'Yes', acomment))
                outdb.commit()

            if len(elist) > 0:                            # Add episode unmatcheds
                for a in range(len(elist)):
                    acomment = '[COLOR blue]' +  "{:<44}".format('genre_link table episode unmatched') +    \
                    '[/COLOR]' + "{:10d}".format(int(elist[a][0])) + "{:10d}".format(int(elist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(elist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(genre_id, media_id, media_type, clean,   \
                    comments) values (?, ?, ?, ?, ?)', (elist[a][0], elist[a][1], elist[a][2], 'Yes', acomment))
                outdb.commit()

            if len(slist) > 0:                            # Add tvswhow unmatcheds
                for a in range(len(slist)):
                    acomment = '[COLOR blue]' +  "{:<44}".format('genre_link table tvshow unmatched') +     \
                    '[/COLOR]' + "{:10d}".format(int(slist[a][0])) + "{:10d}".format(int(slist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(slist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(genre_id, media_id, media_type, clean,   \
                    comments) values (?, ?, ?, ?, ?)', (slist[a][0], slist[a][1], slist[a][2], 'Yes', acomment))
                outdb.commit()

            if len(vlist) > 0:                            # Add musicvideo unmatcheds
                for a in range(len(vlist)):
                    acomment = '[COLOR blue]' +  "{:<40}".format('genre_link table musicvideo unmatched') +  \
                    '[/COLOR]' + "{:10d}".format(int(vlist[a][0])) + "{:10d}".format(int(vlist[a][1])) +     \
                    "{:<8}".format(' ') + "{:<16}".format(str(vlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(genre_id, media_id, media_type, clean,    \
                    comments) values (?, ?, ?, ?, ?)', (vlist[a][0], vlist[a][1], vlist[a][2], 'Yes', acomment))
                outdb.commit() 
                          
            outdb.close()
            return orprecs


        #==========================  Movie Table analysis ============================

        if vtable == 'movie':                       # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM movie WHERE idFile not in        \
                (SELECT idFile FROM files where idFile is not NULL)")
                flist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM movie WHERE c05 not in           \
                (SELECT rating_id FROM rating where media_type = 'movie') ")
                rlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM movie WHERE c23 not in           \
                (SELECT idPath FROM path where idPath is not NULL) ")
                plist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM movie WHERE c09 not in           \
                (SELECT uniqueid_id FROM uniqueid where media_type = 'movie') ")
                ulist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM movie WHERE idSet not in         \
                (SELECT idSet FROM sets) ")
                slist = kcursor.fetchall()
                kcursor.close()
            else:  
                curf = kodidb.execute('SELECT * FROM movie WHERE idFile not in   \
                (SELECT idFile FROM files where idFile is not NULL)')
                curr = kodidb.execute('SELECT * FROM movie WHERE c05 not in      \
                (SELECT rating_id FROM rating where media_type = "movie") ')
                curp = kodidb.execute('SELECT * FROM movie WHERE c23 not in      \
                (SELECT idPath FROM path where idPath is not NULL)')
                curu = kodidb.execute('SELECT * FROM movie WHERE c09 not in      \
                (SELECT uniqueid_id FROM uniqueid where media_type = "movie") ') 
                curs = kodidb.execute('SELECT * FROM movie WHERE idSet not in    \
                (SELECT idSet FROM sets)')       
                flist = curf.fetchall()
                rlist = curr.fetchall()
                plist = curp.fetchall()
                ulist = curu.fetchall()
                slist = curs.fetchall()
                del curf, curr, curp, curu, curs
            kodidb.close()
            orprecs = len(flist) + len(rlist) + len(plist) + len(ulist) + len(slist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(flist)) + ' ' +  str(len(rlist)) \
            + ' ' + str(len(plist)) + ' ' + str(len(ulist)) + ' ' + str(len(slist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(idMovie INTEGER, idFile INTEGER, c00 TEXT,         \
            clean TEXT, comments TEXT)')
            outdb.commit()

            if len(flist) > 0:                            # Add files unmatcheds
                for a in range(len(flist)):
                    acomment = '[COLOR blue]' +  "{:<47}".format('movie table files unmatched') +        \
                    '[/COLOR]' + "{:10d}".format(int(flist[a][0])) + "{:10d}".format(int(flist[a][1])) + \
                    "{:<8}".format(' ') + "{:<16}".format(str(flist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idMovie, idFile, c00, clean, comments) \
                    values (?, ?, ?, ?, ?)', (flist[a][0], flist[a][1], flist[a][2], 'Yes', acomment))
                outdb.commit()
                      
            if len(rlist) > 0:                            # Add ratings unmatcheds
                for a in range(len(rlist)):
                    acomment = "{:<43}".format('movie table ratings unmatched') +              \
                    "{:10d}".format(int(rlist[a][0])) + "{:10d}".format(int(rlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(rlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idMovie, idFile, c00, clean, comments) \
                    values (?, ?, ?, ?, ?)', (rlist[a][0], rlist[a][1], rlist[a][2], 'No', acomment))
                outdb.commit()

            if len(plist) > 0:                            # Add path unmatcheds
                for a in range(len(plist)):
                    acomment = "{:<45}".format('movie table path unmatched') +                 \
                    "{:10d}".format(int(plist[a][0])) + "{:10d}".format(int(plist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(plist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idMovie, idFile, c00, clean, comments) \
                    values (?, ?, ?, ?, ?)', (plist[a][0], plist[a][1], plist[a][2], 'No', acomment))
                outdb.commit()

            if len(ulist) > 0:                            # Add uniqueid unmatcheds
                for a in range(len(ulist)):
                    acomment = "{:<41}".format('movie table uniqueid unmatched') +             \
                    "{:10d}".format(int(ulist[a][0])) + "{:10d}".format(int(ulist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(ulist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idMovie, idFile, c00, clean, comments) \
                    values (?, ?, ?, ?, ?)', (ulist[a][0], ulist[a][1], ulist[a][2], 'No', acomment))
                outdb.commit()  

            if len(slist) > 0:                            # Add sets unmatcheds
                for a in range(len(slist)):
                    acomment = "{:<46}".format('movie table sets unmatched') +                 \
                    "{:10d}".format(int(slist[a][0])) + "{:10d}".format(int(slist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(slist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idMovie, idFile, c00, clean, comments) \
                    values (?, ?, ?, ?, ?)', (slist[a][0], slist[a][1], slist[a][2], 'No', acomment))
                outdb.commit()                            
            outdb.close()
            return orprecs

        #=======================  Musicvideo Table analysis ==========================

        if vtable == 'musicvideo':                     # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM musicvideo WHERE idFile not in        \
                (SELECT idFile FROM files where idFile is not NULL)")
                flist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM musicvideo WHERE c14 not in           \
                (SELECT idPath FROM path where idPath is not NULL)")
                plist = kcursor.fetchall()
                kcursor.close()
            else:   
                curf = kodidb.execute('SELECT * FROM musicvideo WHERE idFile not in        \
                (SELECT idFile FROM files where idFile is not NULL)')
                curp = kodidb.execute('SELECT * FROM musicvideo WHERE c14 not in           \
                (SELECT idPath FROM path where idPath is not NULL)') 
                flist = curf.fetchall()
                plist = curp.fetchall()
                del curf, curp
            kodidb.close()
            orprecs = len(flist) + len(plist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(flist)) + ' ' +     \
            str(len(plist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(idMVideo INTEGER, idFile INTEGER, c00 TEXT, \
            clean TEXT, comments TEXT)')
            outdb.commit()

            if len(flist) > 0:                            # Add files unmatcheds
                for a in range(len(flist)):
                    acomment = '[COLOR blue]' +  "{:<47}".format('musicvideo table files unmatched') +     \
                    '[/COLOR]' +  "{:10d}".format(int(flist[a][0])) + "{:10d}".format(int(flist[a][1])) +  \
                    "{:<8}".format(' ') + "{:<16}".format(str(flist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idMVideo, idFile, c00, clean, comments) \
                    values (?, ?, ?, ?, ?)', (flist[a][0], flist[a][1], flist[a][2], 'Yes', acomment))
                outdb.commit()

            if len(plist) > 0:                            # Add path unmatcheds
                for a in range(len(plist)):
                    acomment = "{:<45}".format('musicvideo table path unmatched') +          \
                    "{:10d}".format(int(plist[a][0])) + "{:10d}".format(int(plist[a][1])) +  \
                    "{:<8}".format(' ') + "{:<16}".format(str(plist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idMVideo, idFile, c00, clean, comments) \
                    values (?, ?, ?, ?, ?)', (plist[a][0], plist[a][1], plist[a][2], 'No', acomment))
                outdb.commit()                           
            outdb.close()
            return orprecs


        #=======================  Seasons Table analysis ==========================

        if vtable == 'seasons':                     # Check tables for unmatched data 
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM seasons WHERE idShow not in        \
                (SELECT idShow FROM tvshow where idShow is not NULL) ")
                tlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM seasons WHERE idSeason not in      \
                (SELECT idSeason FROM episode where idSeason is not NULL) ")
                elist = kcursor.fetchall()
                kcursor.close()
            else:   
                curt = kodidb.execute('SELECT * FROM seasons WHERE idShow not in        \
                (SELECT idShow FROM tvshow where idShow is not NULL)')
                cure = kodidb.execute('SELECT * FROM seasons WHERE idSeason not in      \
                (SELECT idSeason FROM episode where idSeason is not NULL)') 
                tlist = curt.fetchall()
                elist = cure.fetchall()
                del curt, cure
            kodidb.close()
            orprecs = len(tlist) + len(elist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(tlist)) + ' ' +     \
            str(len(elist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(idSeason INTEGER, idShow INTEGER,      \
            name TEXT, clean TEXT, comments TEXT)')
            outdb.commit()

            if len(tlist) > 0:                            # Add tvshow unmatcheds
                for a in range(len(tlist)):
                    acomment = '[COLOR blue]' +  "{:<47}".format('seasons table tvshow unmatched') +        \
                    '[/COLOR]' + "{:10d}".format(int(tlist[a][0])) + "{:10d}".format(int(tlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(tlist[a][3]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idSeason, idShow, name, clean, comments) \
                    values (?, ?, ?, ?, ?)', (tlist[a][0], tlist[a][1], tlist[a][3], 'Yes', acomment))
                outdb.commit()

            if len(elist) > 0:                            # Add episode unmatcheds
                for a in range(len(elist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('seasons table episode unmatched') +        \
                    '[/COLOR]' + "{:10d}".format(int(elist[a][0])) + "{:10d}".format(int(elist[a][1])) +     \
                    "{:<8}".format(' ') + "{:<16}".format(str(elist[a][3]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idSeason, idShow, name, clean, comments)  \
                    values (?, ?, ?, ?, ?)', (elist[a][0], elist[a][1], elist[a][3], 'Yes', acomment))
                outdb.commit()                           
            outdb.close()
            return orprecs


        #==========================  Sets Table analysis ================================

        if vtable == 'sets':                            # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM sets WHERE idSet not in (SELECT idSet FROM movie      \
                where idSet is not NULL) ")
                alist = kcursor.fetchall()
                kcursor.close()
            else:  
                cura = kodidb.execute('SELECT * FROM sets WHERE idSet not in (SELECT idSet FROM movie \
                where idSet is not NULL)')
                alist = cura.fetchall()
                del cura
            kodidb.close()
            orprecs = len(alist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(idSet integer, strSet text, strOverview text,    \
            clean TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add actor_link unmatcheds
                for a in range(len(alist)):
                    acomment = '[COLOR blue]' +  "{:<32}".format('sets table movie missing') + '[/COLOR]'  \
                    + "{:12d}".format(int(str(alist[a][0]))) + "{:<12}".format(' ') + str(alist[a][1])
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idSet, strSet, clean, comments) values  \
                    (?, ?, ?, ?)', (alist[a][0], alist[a][1], 'Yes', acomment))
                outdb.commit()
            outdb.close()
            return orprecs


        #=======================  Streamdetails Table analysis ==========================

        if vtable == 'streamdetails':                   # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM streamdetails WHERE idFile not in             \
                (SELECT idFile FROM files where idFile is not NULL) and iStreamType = '0' ")
                vlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM streamdetails WHERE idFile not in             \
                (SELECT idFile FROM files where idFile is not NULL)  and iStreamType = '1'  ")
                alist = kcursor.fetchall()
                kcursor.close()
            else:    
                curv = kodidb.execute('SELECT * FROM streamdetails WHERE idFile not in        \
                (SELECT idFile FROM files where idFile is not NULL) and iStreamType = 0 ')
                cura = kodidb.execute('SELECT * FROM streamdetails WHERE idFile not in        \
                (SELECT idFile FROM files where idFile is not NULL)  and iStreamType = 1 ') 
                vlist = curv.fetchall()
                alist = cura.fetchall()
                del curv, cura
            kodidb.close()
            orprecs = len(vlist) + len(alist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(vlist)) + ' ' +     \
            str(len(alist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(idFile INTEGER, iStreamType INTEGER,  \
            clean TEXT, comments TEXT)')
            outdb.commit()

            if len(vlist) > 0:                            # Add files unmatcheds
                for a in range(len(vlist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('streamdetails table files unmatched') +  \
                    '[/COLOR]' + "{:10d}".format(int(vlist[a][0])) + "{:10d}".format(int(vlist[a][1])) +   \
                    "{:<8}".format(' ') + "{:<16}".format(str('video codec'))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idFile, iStreamType, clean, comments)   \
                    values (?, ?, ?, ?)', (vlist[a][0], vlist[a][1], 'Yes', acomment))
                outdb.commit()

            if len(alist) > 0:                            # Add streamdetails unmatcheds
                for a in range(len(alist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('streamdetails table files unmatched') +  \
                    '[/COLOR]' + "{:10d}".format(int(alist[a][0])) + "{:10d}".format(int(alist[a][1])) +   \
                    "{:<8}".format(' ') + "{:<16}".format(str('audio codec'))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idFile, iStreamType, clean, comments)   \
                    values (?, ?, ?, ?)', (alist[a][0], alist[a][1], 'Yes', acomment))
                outdb.commit()                           
            outdb.close()
            return orprecs


        #=======================  Tag_link Table analysis ==========================

        if vtable == 'tag_link':                     # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM tag_link WHERE tag_id not in                \
                (SELECT tag_id FROM tag where tag_id is not NULL) ")
                tlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM tag_link WHERE media_id not in (SELECT      \
                idEpisode FROM episode where idEpisode is not NULL) and media_type = 'episode' ")
                elist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM tag_link WHERE media_id not in (SELECT      \
                idMovie FROM movie where idMovie is not NULL) and media_type = 'movie' ")
                mlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM tag_link WHERE media_id not in (SELECT      \
                idMVideo FROM musicvideo where idMVideo is not NULL) and media_type = 'musicvideo' ")
                vlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM tag_link WHERE media_id not in (SELECT      \
                idShow FROM tvshow where idShow is not NULL) and media_type = 'tvshow' ")
                slist = kcursor.fetchall()
                kcursor.close()
            else:  
                curt = kodidb.execute('SELECT * FROM tag_link WHERE tag_id not in                \
                (SELECT tag_id FROM tag where tag_id is not NULL) ')
                cure = kodidb.execute('SELECT * FROM tag_link WHERE media_id not in (SELECT      \
                idEpisode FROM episode where idEpisode is not NULL) and media_type = "episode"')
                curm = kodidb.execute('SELECT * FROM tag_link WHERE media_id not in (SELECT      \
                idMovie FROM movie where idMovie is not NULL) and media_type = "movie"') 
                curv = kodidb.execute('SELECT * FROM tag_link WHERE media_id not in (SELECT      \
                idMVideo FROM musicvideo where idMVideo is not NULL) and media_type = "musicvideo"') 
                curs = kodidb.execute('SELECT * FROM tag_link WHERE media_id not in (SELECT      \
                idShow FROM tvshow where idShow is not NULL) and media_type = "tvshow"') 
                tlist = curt.fetchall()
                elist = cure.fetchall()
                mlist = curm.fetchall()
                vlist = curv.fetchall()
                slist = curs.fetchall()
                del curt, cure, curm, curv, curs
            kodidb.close()
            orprecs = len(tlist) + len(elist) + len(mlist) + len(vlist) + len(slist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(tlist)) + ' ' +     \
            str(len(elist)) + ' ' + str(len(mlist)) + ' ' + str(len(vlist)) + ' ' +    \
            str(len(slist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(tag_id INTEGER, media_id INTEGER,      \
            media_type TEXT, clean TEXT, comments TEXT)')
            outdb.commit()

            if len(tlist) > 0:                            # Add tag unmatcheds
                for a in range(len(tlist)):
                    acomment = '[COLOR blue]' +  "{:<47}".format('tag_link table tag unmatched') +                \
                    '[/COLOR]' + "{:10d}".format(int(tlist[a][0])) + "{:14d}".format(int(tlist[a][1])) +          \
                    "{:<12}".format(' ') + "{:<16}".format(str(tlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(tag_id, media_id, media_type, clean, comments) \
                    values (?, ?, ?, ?, ?)', (tlist[a][0], tlist[a][1], tlist[a][2], 'Yes', acomment))
                outdb.commit()

            if len(elist) > 0:                            # Add episode unmatcheds
                for a in range(len(elist)):
                    acomment = '[COLOR blue]' +  "{:<44}".format('tag_link table episode unmatched') +            \
                    '[/COLOR]' + "{:10d}".format(int(elist[a][0])) + "{:14d}".format(int(elist[a][1])) +          \
                    "{:<12}".format(' ') + "{:<16}".format(str(elist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(tag_id, media_id, media_type, clean, comments) \
                    values (?, ?, ?, ?, ?)', (elist[a][0], elist[a][1], elist[a][2], 'Yes', acomment))
                outdb.commit()

            if len(mlist) > 0:                            # Add movie unmatcheds
                for a in range(len(mlist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('tag_link table movie unmatched') +              \
                    '[/COLOR]' + "{:10d}".format(int(mlist[a][0])) + "{:14d}".format(int(mlist[a][1])) +          \
                    "{:<12}".format(' ') + "{:<16}".format(str(mlist[a][2])) 
                    outdb.execute('INSERT OR REPLACE into vdb_temp(tag_id, media_id, media_type, clean, comments) \
                    values (?, ?, ?, ?, ?)', (mlist[a][0], mlist[a][1], mlist[a][2], 'Yes', acomment))
                outdb.commit()  

            if len(vlist) > 0:                            # Add musicvideo unmatcheds
                for a in range(len(vlist)):
                    acomment = '[COLOR blue]' +  "{:<40}".format('tag_link table musicvideo unmatched') +         \
                    '[/COLOR]' + "{:10d}".format(int(vlist[a][0])) + "{:14d}".format(int(vlist[a][1])) +          \
                    "{:<12}".format(' ') + "{:<16}".format(str(vlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(tag_id, media_id, media_type, clean, comments) \
                    values (?, ?, ?, ?, ?)', (vlist[a][0], vlist[a][1], vlist[a][2], 'Yes', acomment))
                outdb.commit()  

            if len(slist) > 0:                            # Add tvshow unmatcheds
                for a in range(len(slist)):
                    acomment = '[COLOR blue]' +  "{:<44}".format('tag_link table tvshow unmatched') +             \
                    '[/COLOR]' + "{:10d}".format(int(slist[a][0])) + "{:14d}".format(int(slist[a][1])) +          \
                    "{:<12}".format(' ') + "{:<16}".format(str(slist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(tag_id, media_id, media_type, clean, comments) \
                    values (?, ?, ?, ?, ?)', (slist[a][0], slist[a][1], slist[a][2], 'Yes', acomment))
                outdb.commit()                             
            outdb.close()
            return orprecs


        #==========================  TV Show Table analysis ===========================

        if vtable == 'tvshow':                        # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM tvshow WHERE idShow not in        \
                (SELECT idShow FROM episode where idShow is not NULL) ")
                slist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM tvshow WHERE idShow not in        \
                (SELECT idShow FROM seasons where idShow is not NULL) ")
                elist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM tvshow WHERE c04 not in           \
                (SELECT rating_id FROM rating where media_type = 'tvshow') and c04 is not NULL ")
                rlist = kcursor.fetchall()
                kcursor.close()
            else: 
                cure = kodidb.execute('SELECT * FROM tvshow WHERE idShow not in   \
                (SELECT idShow FROM episode where idShow is not NULL)')
                curs = kodidb.execute('SELECT * FROM tvshow WHERE idShow not in   \
                (SELECT idShow FROM seasons where idShow is not NULL) ')
                curr = kodidb.execute('SELECT * FROM tvshow WHERE c04 not in      \
                (SELECT rating_id FROM rating where media_type = "tvshow") and c04 is not NULL')  
                slist = curs.fetchall()
                elist = cure.fetchall()
                rlist = curr.fetchall()
                del curs, cure, curr
            kodidb.close()
            orprecs = len(slist) + len(elist) + len(rlist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(slist)) + ' '  \
            + str(len(elist)) + ' ' + str(len(rlist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(idShow INTEGER, c00 TEXT,  clean TEXT, \
            comments TEXT)')
            outdb.commit()
                      
            if len(slist) > 0:                            # Add seasons unmatcheds
                for a in range(len(slist)):
                    acomment = '[COLOR blue]' +  "{:<37}".format('tvshow table seasons unmatched')   \
                    +  '[/COLOR]' + "{:10d}".format(int(slist[a][0])) + "{:<8}".format(' ') +        \
                    "{:<16}".format(slist[a][1])
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idShow, c00, clean, comments)     \
                    values (?, ?, ?, ?)', (slist[a][0], slist[a][1], 'Yes', acomment))
                outdb.commit()

            if len(elist) > 0:                            # Add episode unmatcheds
                for a in range(len(elist)):
                    acomment = "{:<40}".format('tvshow table episode unmatched') +               \
                    "{:10d}".format(int(elist[a][0])) + "{:<8}".format(' ') +                    \
                    "{:<16}".format(elist[a][1])
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idShow, c00, clean, comments) \
                    values (?, ?, ?, ?)', (elist[a][0], elist[a][1], 'No', acomment))
                outdb.commit()

            if len(rlist) > 0:                            # Add rating unmatcheds
                for a in range(len(rlist)):
                    acomment = "{:<43}".format('tvshow table rating unmatched') +                \
                    "{:10d}".format(int(rlist[a][0])) + "{:<8}".format(' ') +                    \
                    "{:<16}".format(rlist[a][1])
                    outdb.execute('INSERT OR REPLACE into vdb_temp(idShow, c00, clean, comments) \
                    values (?, ?, ?, ?)', (rlist[a][0], rlist[a][1], 'No', acomment))
                outdb.commit() 
                          
            outdb.close()
            return orprecs

        #==========================  Writer_link Table analysis ===========================

        if vtable == 'writer_link':                       # Check tables for unmatched data
            if dbtype == 'mysql':
                kcursor = kodidb.cursor()
                kcursor.execute("SELECT * FROM writer_link WHERE actor_id not in      \
                (SELECT actor_id FROM actor where actor_id is not NULL) ")
                alist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM writer_link WHERE media_id not in      \
                (SELECT idMovie FROM movie) and media_type = 'movie' ")
                mlist = kcursor.fetchall()
                kcursor.execute("SELECT * FROM writer_link WHERE media_id not in      \
                (SELECT idEpisode FROM episode) and media_type = 'episode' ")
                elist = kcursor.fetchall()
                kcursor.close()
            else: 
                cura = kodidb.execute('SELECT * FROM writer_link WHERE actor_id not in      \
                (SELECT actor_id FROM actor where actor_id is not NULL)')
                curm = kodidb.execute('SELECT * FROM writer_link WHERE media_id not in      \
                (SELECT idMovie FROM movie) and media_type = "movie" ')
                cure = kodidb.execute('SELECT * FROM writer_link WHERE media_id not in      \
                (SELECT idEpisode FROM episode) and media_type = "episode" ') 
                alist = cura.fetchall()
                mlist = curm.fetchall()
                elist = cure.fetchall()
                del cura, curm, cure
            kodidb.close()
            orprecs = len(alist) + len(mlist) + len(elist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)) + ' ' +        \
            str(len(mlist)) + ' ' + str(len(elist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No unmatched records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(actor_id INTEGER, media_id INTEGER, media_type TEXT, \
            clean TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add actor unmatcheds
                for a in range(len(alist)):
                    acomment = '[COLOR blue]' +  "{:<47}".format('writer_link table actor unmatched') +    \
                    '[/COLOR]' + "{:10d}".format(int(alist[a][0])) + "{:10d}".format(int(alist[a][1])) +   \
                    "{:<8}".format(' ') + "{:<16}".format(str(alist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type, clean,  \
                    comments) values (?, ?, ?, ?, ?)', (alist[a][0], alist[a][1], alist[a][2], 'Yes', acomment))
                outdb.commit()
                      
            if len(mlist) > 0:                            # Add movie unmatcheds
                for a in range(len(mlist)):
                    acomment = '[COLOR blue]' +  "{:<45}".format('writer_link table movie unmatched') +    \
                    '[/COLOR]' + "{:10d}".format(int(mlist[a][0])) + "{:10d}".format(int(mlist[a][1])) +   \
                    "{:<8}".format(' ') + "{:<16}".format(str(mlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type, clean,  \
                    comments) values (?, ?, ?, ?, ?)', (mlist[a][0], mlist[a][1], mlist[a][2], 'Yes', acomment))
                outdb.commit()

            if len(elist) > 0:                            # Add episode unmatcheds
                for a in range(len(elist)):
                    acomment = '[COLOR blue]' +  "{:<44}".format('writer_link table episode unmatched') +  \
                    '[/COLOR]' + "{:10d}".format(int(elist[a][0])) + "{:10d}".format(int(elist[a][1])) +   \
                    "{:<8}".format(' ') + "{:<16}".format(str(elist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type, clean,  \
                    comments) values (?, ?, ?, ?, ?)', (elist[a][0], elist[a][1], elist[a][2], 'Yes', acomment))
                outdb.commit()
                      
            outdb.close()
            return orprecs

     
    except Exception as e:
        kodidb.close()
        printexception()
            

def displayClean(vtable):                                 # Clean unmatched analysis

    dialog_text = translate(30358) + vtable
    xbmcgui.Dialog().ok(translate(30306), dialog_text)


def checkClean(vtable):                                   # Check to ensure cleaning

    dialog_text = translate(30362)
    dialog_head = translate(30306) + ' - ' + vtable
    select = xbmcgui.Dialog().yesno(dialog_head, dialog_text)
    return select


def finishClean(vtable, recs):                            # Clean unmatched results

    kgenlog = translate(30363) + vtable + ' - ' + str(recs) + translate(30364)
    kgenlogUpdate(kgenlog)
    dialog_text = translate(30363) + '\n' + vtable + ' - ' + str(recs) + translate(30364)
    xbmcgui.Dialog().ok(translate(30306), dialog_text)


def getHeader(vtable):

    try:
        if vtable == 'actor_link':
             vheader = "{:^48}".format('Table Comparison') +  "{:^15}".format('actor_id')         \
             + "{:^20}".format('media_id') + "{:<4}".format(' ') + "{:<16}".format('media_type')
        elif vtable == 'actor':
             vheader = "{:^42}".format('Table Comparison') +  "{:^15}".format('actor_id')         \
             + "{:^32}".format('Name')
        elif vtable == 'art':
             vheader = "{:^48}".format('Table Comparison') +  "{:^15}".format('art_id')           \
             + "{:^20}".format('media_id') + "{:<4}".format(' ') + "{:<16}".format('media_type')
        elif vtable == 'director_link':
             vheader = "{:^48}".format('Table Comparison') +  "{:^15}".format('actor_id')         \
             + "{:^20}".format('media_id') + "{:<4}".format(' ') + "{:<16}".format('media_type')
        elif vtable == 'episode':
             vheader = "{:^48}".format('Table Comparison') +  "{:^15}".format('idEpisode')        \
             + "{:^20}".format('idFile') + "{:<4}".format(' ') + "{:<16}".format('title / c00')
        elif 'files' in vtable:
             vheader = "{:^48}".format('Table Comparison') +  "{:^15}".format('idFile')           \
             + "{:^20}".format('idPath') + "{:<4}".format(' ') + "{:<16}".format('dateAdded')
        elif 'path' in vtable:
             vheader = "{:^40}".format('Table Comparison') +  "{:^15}".format('idPath')           \
             + "{:^64}".format('strPath') + "{:<4}".format(' ') + "{:<16}".format('dateAdded')
        elif vtable == 'genre_link':
             vheader = "{:^48}".format('Table Comparison') +  "{:^15}".format('genre_id')         \
             + "{:^20}".format('media_id') + "{:<4}".format(' ') + "{:<16}".format('media_type')
        elif vtable == 'movie':
             vheader = "{:^48}".format('Table Comparison') +  "{:^15}".format('idMovie')          \
             + "{:^20}".format('idFile') + "{:<4}".format(' ') + "{:<16}".format('title / c00')
        elif vtable == 'musicvideo':
             vheader = "{:^48}".format('Table Comparison') +  "{:^15}".format('idMVideo')         \
             + "{:^20}".format('idFile') + "{:<4}".format(' ') + "{:<16}".format('title / c00')
        elif vtable == 'seasons':
             vheader = "{:^48}".format('Table Comparison') +  "{:^15}".format('idSeason')         \
             + "{:^20}".format('idShow') + "{:<4}".format(' ') + "{:<16}".format('name')
        elif vtable == 'sets':
             vheader = "{:^42}".format('Table Comparison') +  "{:^15}".format('idSet')            \
             + "{:^32}".format('strSet')
        elif vtable == 'streamdetails':
             vheader = "{:^60}".format('Table Comparison') +  "{:^15}".format('idFile')           \
             + "{:^32}".format('iStreamType')
        elif vtable == 'tag_link':
             vheader = "{:^48}".format('Table Comparison') +  "{:^18}".format('tag_id')           \
             + "{:^20}".format('media_id') + "{:<4}".format(' ') + "{:<16}".format('media_type')
        elif vtable == 'tvshow':
             vheader = "{:^54}".format('Table Comparison') +  "{:^15}".format('idShow')           \
             + "{:^32}".format('title / c00')
        elif vtable == 'writer_link':
             vheader = "{:^48}".format('Table Comparison') +  "{:^15}".format('actor_id')         \
             + "{:^20}".format('media_id') + "{:<4}".format(' ') + "{:<16}".format('media_type')
        else:
            return ''
        return vheader

    except Exception as e:
        printexception()   


def vdbClean(vtable, dbtype):                                  # Clean video database

    try:
        kodidb = openKodiDB(dbtype)
        cleandb = openKscleanDB()
        recscount = 0

        curt = cleandb.execute('SELECT count (*) FROM vdb_temp WHERE clean = "Yes" ')
        curc = cleandb.execute('SELECT * FROM vdb_temp WHERE clean = "Yes" ')
        recscount = curt.fetchone()[0]
        cleanrecs = curc.fetchall()
        #cleandb.close()

        if dbtype == 'mysql':
            kcursor = kodidb.cursor()
    
        xbmc.log('KS Cleaner records to clean: ' + str(recscount), xbmc.LOGDEBUG)

        if vtable == 'actor':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql':
                    kcursor.execute("DELETE from actor WHERE actor_id = %s"% var1)
                else:
                    kodidb.execute('DELETE from actor WHERE actor_id = ? ', (var1,))   
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'actor_id ' + str(var1) + \
                ' name ' + str(var2))
                kgenlogUpdate(kgenlog, 'No', cleandb)  
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()                
            kodidb.close()
            cleandb.commit()
            cleandb.close() 
            return recscount    

        elif vtable == 'actor_link':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql':
                    dquery = "DELETE from actor_link WHERE actor_id = %s and media_id = %s and      \
                    media_type = %s"
                    varquery = list([var1, var2, var3])   
                    kcursor.execute(dquery, varquery)
                else:   
                    kodidb.execute('DELETE from actor_link WHERE actor_id = ? and media_id = ? and   \
                    media_type = ? ', (var1, var2, var3,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'actor_id ' + str(var1) +       \
                ' media_id ' + str(var2) + ' media_type ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)                
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close() 
            kodidb.close()
            cleandb.commit()
            cleandb.close()
            return recscount        

        elif vtable == 'art':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                var4 =  cleanrecs[clean][3] 
                if dbtype == 'mysql':
                    dquery = "DELETE from art WHERE art_id = %s and media_id = %s and   \
                    media_type = %s and type = %s"
                    varquery = list([var1, var2, var3, var4])   
                    kcursor.execute(dquery, varquery)
                else:    
                    kodidb.execute('DELETE from art WHERE art_id = ? and media_id = ? and   \
                    media_type = ? and type = ?', (var1, var2, var3, var4,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'art_id ' + str(var1) + \
                ' media_id ' + str(var2) + ' media_type ' + str(var3) + ' type ' + str(var4))
                kgenlogUpdate(kgenlog, 'No', cleandb)                
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()   
            kodidb.close()
            cleandb.commit()
            cleandb.close() 
            return recscount        

        elif vtable == 'director_link':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql':
                    dquery = "DELETE from director_link WHERE actor_id = %s and media_id = %s and   \
                    media_type = %s "
                    varquery = list([var1, var2, var3])   
                    kcursor.execute(dquery, varquery)
                else:      
                    kodidb.execute('DELETE from director_link WHERE actor_id = ? and media_id = ? and   \
                    media_type = ? ', (var1, var2, var3,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'actor_id ' + str(var1) + \
                ' media_id ' + str(var2) + ' media_type ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)                
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()  
            kodidb.close()
            cleandb.commit()
            cleandb.close() 
            return recscount

        elif vtable == 'episode':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql': 
                    kcursor.execute("DELETE from episode WHERE idEpisode = %s"% var1)
                else:    
                    kodidb.execute('DELETE from episode WHERE idEpisode = ? ', (var1,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'idEpisode ' + str(var1) + \
                ' idFile ' + str(var2) + ' name ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)              
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close() 
            kodidb.close()
            cleandb.commit()
            cleandb.close() 
            return recscount    

        elif 'files' in vtable:
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql': 
                    kcursor.execute("DELETE from files WHERE idFile = %s"% var1)
                else:    
                    kodidb.execute('DELETE from files WHERE idFile = ? ', (var1,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'idFile ' + str(var1) + \
                ' idPath ' + str(var2) + ' dateadded ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)               
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()  
            kodidb.close()
            cleandb.commit()
            cleandb.close()
            return recscount   

        elif 'path' in vtable:
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][3]
                if dbtype == 'mysql': 
                    kcursor.execute("DELETE from path WHERE idPath = %s"% var1)
                else:    
                    kodidb.execute('DELETE from path WHERE idPath = ? ', (var1,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'idPath ' + str(var1) + \
                ' idPath ' + str(var2) + ' dateadded ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)               
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()  
            kodidb.close()
            cleandb.commit()
            cleandb.close()
            return recscount   

        elif vtable == 'genre_link':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql': 
                    dquery = "DELETE from genre_link WHERE genre_id = %s and media_id = %s and   \
                    media_type = %s "
                    varquery = list([var1, var2, var3])   
                    kcursor.execute(dquery, varquery)
                else: 
                    kodidb.execute('DELETE from genre_link WHERE genre_id = ? and media_id = ? and   \
                    media_type = ? ', (var1, var2, var3,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'genre_id ' + str(var1) + \
                ' media_id ' + str(var2) + ' media_type ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)                
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()  
            kodidb.close()
            cleandb.commit()
            cleandb.close()
            return recscount

        elif vtable == 'movie':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql': 
                    kcursor.execute("DELETE from movie WHERE idMovie = %s"% var1)
                else:       
                    kodidb.execute('DELETE from movie WHERE idMovie = ? ', (var1,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'idMovie ' + str(var1) + \
                ' idFile ' + str(var2) + ' name ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)                
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()  
            kodidb.close()
            cleandb.commit()
            cleandb.close() 
            return recscount    

        elif vtable == 'musicvideo':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql': 
                    kcursor.execute("DELETE from musicvideo WHERE idMVideo = %s"% var1)
                else:          
                    kodidb.execute('DELETE from musicvideo WHERE idMVideo = ? ', (var1,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'idMVideo ' + str(var1) + \
                ' idFile ' + str(var2) + ' name ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)               
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close() 
            kodidb.close()
            cleandb.commit()
            cleandb.close() 
            return recscount    

        elif vtable == 'seasons':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql': 
                    dquery = "DELETE from seasons WHERE idSeason = %s and idShow = %s "
                    varquery = list([var1, var2])   
                    kcursor.execute(dquery, varquery)
                else:    
                    kodidb.execute('DELETE from seasons WHERE idSeason = ? and idShow = ? ',       \
                    (var1, var2,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'idSeason ' + str(var1) + \
                ' idShow ' + str(var2) + ' name ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)              
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()  
            kodidb.close()
            cleandb.commit()
            cleandb.close() 
            return recscount

        elif vtable == 'sets':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                if dbtype == 'mysql': 
                    kcursor.execute("DELETE from sets WHERE idSet = %s"% var1)
                else:    
                    kodidb.execute('DELETE from sets WHERE idSet = ? ', (var1,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'idSet ' + str(var1) + \
                ' strSet ' + str(var2))
                kgenlogUpdate(kgenlog, 'No', cleandb)                 
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close() 
            kodidb.close()
            cleandb.commit()
            cleandb.close() 
            return recscount

        elif vtable == 'streamdetails':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                if dbtype == 'mysql': 
                    dquery = "DELETE from streamdetails WHERE idFile = %s and iStreamType = %s "
                    varquery = list([var1, var2])   
                    kcursor.execute(dquery, varquery)
                else:   
                    kodidb.execute('DELETE from streamdetails WHERE idFile = ? and iStreamType = ? ', \
                    (var1, var2,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'idFile ' + str(var1) + \
                ' iStreamType ' + str(var2))
                kgenlogUpdate(kgenlog, 'No', cleandb)                
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()  
            kodidb.close()
            cleandb.commit()
            cleandb.close()
            return recscount

        elif vtable == 'tag_link':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql': 
                    dquery = "DELETE from tag_link WHERE tag_id = %s and media_id = %s and   \
                    media_type = %s "
                    varquery = list([var1, var2, var3])   
                    kcursor.execute(dquery, varquery)
                else:      
                    kodidb.execute('DELETE from tag_link WHERE tag_id = ? and media_id = ? and   \
                    media_type = ? ', (var1, var2, var3,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'tag_id ' + str(var1) + \
                ' media_id ' + str(var2) + ' media_type ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)                
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()  
            kodidb.close()
            cleandb.commit()
            cleandb.close()
            return recscount        

        elif vtable == 'tvshow':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                if dbtype == 'mysql': 
                    kcursor.execute("DELETE from tvshow WHERE idShow = %s"% var1)
                else:     
                    kodidb.execute('DELETE from tvshow WHERE idShow = ? ', (var1,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'idShow ' + str(var1) + \
                ' name ' + str(var2))
                kgenlogUpdate(kgenlog, 'No', cleandb)                
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close()  
            kodidb.close()
            cleandb.commit()
            cleandb.close()
            return recscount

        elif vtable == 'writer_link':
            for clean in range(len(cleanrecs)):
                var1 =  cleanrecs[clean][0]
                var2 =  cleanrecs[clean][1]
                var3 =  cleanrecs[clean][2]
                if dbtype == 'mysql': 
                    dquery = "DELETE from writer_link WHERE actor_id = %s and media_id = %s and   \
                    media_type = %s "
                    varquery = list([var1, var2, var3])   
                    kcursor.execute(dquery, varquery)
                else:   
                   kodidb.execute('DELETE from writer_link WHERE actor_id = ? and media_id = ? and   \
                   media_type = ? ', (var1, var2, var3,))
                kgenlog = ('KS Cleaner cleaned ' +  vtable + ' - ' + 'actor_id ' + str(var1) + \
                ' media_id ' + str(var2) + ' media_type ' + str(var3))
                kgenlogUpdate(kgenlog, 'No', cleandb)               
            kodidb.commit()
            if dbtype == 'mysql':
                kcursor.close() 
            kodidb.close()
            cleandb.commit()
            cleandb.close()
            return recscount

    except Exception as e:
        printexception() 
        kodidb.close()





