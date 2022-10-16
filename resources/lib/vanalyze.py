import xbmc
import xbmcgui
import xbmcplugin
import os, sys, linecache, json
import xbmcaddon
import xbmcvfs
import csv  
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception, translate
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature, openKodiTeDB, tempDisplay
from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'


def vanalMenu():                                            # Select table to export

    try:
        while True:
            stable = []
            menuitem1 = translate(30341)
            menuitem2 = translate(30342)
            menuitem3 = translate(30343)
            menuitem4 = translate(30344)
            menuitem5 = translate(30345)
            menuitem6 = translate(30346)
            menuitem7 = translate(30347)
            menuitem8 = translate(30348)
            menuitem9 = translate(30349)
            menuitem10 = translate(30350)
            menuitem11 = translate(30351)
            menuitem12 = translate(30352)
            selectbl = [menuitem1, menuitem2, menuitem3, menuitem4, menuitem5, menuitem6,  \
            menuitem7, menuitem8, menuitem9, menuitem10, menuitem11, menuitem12,]
            ddialog = xbmcgui.Dialog()    
            stable = ddialog.select(translate(30306) + ' - ' + translate(30340), selectbl)
            if stable < 0:                                 # User cancel
                break
            else:
                vanalfMenu(selectbl[stable])

    except Exception as e:
        printexception()


def vanalfMenu(vtable):                                   # Select analyzer function 

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
            alrecs = vdbAnalysis(vtable)
            kgenlog = ('Video DB Analysis - ' +  vtable + ' - ' + str(alrecs) + ' unmatched found')
            kgenlogUpdate(kgenlog)
            if alrecs != None and alrecs > 0:
                tempDisplay(vtable)
            elif alrecs != None and alrecs == 0:
                displayClean(vtable)
            else:
                nofeature()
        elif menuitem2 in selectfn[sfunction]:
            nofeature()      
        elif menuitem3 in selectfn[sfunction]:
            nofeature() 

    except Exception as e:
        printexception()    


def vdbAnalysis(vtable):                                 # Analyze table

    try:
        kodidb = openKodiDB()
        outdb = openKscleanDB()

        outdb.execute('DROP table IF EXISTS vdb_temp')   # Drop temporary output table
        outdb.commit()

        if vtable == 'actor_link':                       # Check tables for unmatched data  
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
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)) + ' ' +  str(len(mlist)) \
            + ' ' + str(len(elist)) + ' ' + str(len(tlist)) + ' ' + str(len(vlist)) + ' ' +         \
            str(len(slist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No Orphan records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(actor_id INTEGER, media_id INTEGER, media_type TEXT, \
            role TEXT, cast_order INTEGER, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add actor unmatcheds
                for a in range(len(alist)):
                    acomment = "{:<47}".format('actor_link table actor unmatched') +           \
                    "{:10d}".format(int(alist[a][0])) + "{:10d}".format(int(alist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(alist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (alist[a][0], alist[a][1], alist[a][2], acomment))
                outdb.commit()
                      
            if len(mlist) > 0:                            # Add movie unmatcheds
                for a in range(len(mlist)):
                    acomment = "{:<45}".format('actor_link table movie unmatched') +           \
                    "{:10d}".format(int(mlist[a][0])) + "{:10d}".format(int(mlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(mlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (mlist[a][0], mlist[a][1], mlist[a][2], acomment))
                outdb.commit()

            if len(elist) > 0:                            # Add episode unmatcheds
                for a in range(len(elist)):
                    acomment = "{:<44}".format('actor_link table episode unmatched') +         \
                    "{:10d}".format(int(elist[a][0])) + "{:10d}".format(int(elist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(elist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (elist[a][0], elist[a][1], elist[a][2], acomment))
                outdb.commit()

            if len(tlist) > 0:                            # Add tvshow unmatcheds
                for a in range(len(tlist)):
                    acomment = "{:<44}".format('actor_link table tvshow unmatched') +           \
                    "{:10d}".format(int(tlist[a][0])) + "{:10d}".format(int(tlist[a][1])) +     \
                    "{:<8}".format(' ') + "{:>16}".format(str(tlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (tlist[a][0], tlist[a][1], tlist[a][2], acomment))
                outdb.commit()  

            if len(vlist) > 0:                            # Add musicvideo unmatcheds
                for a in range(len(vlist)):
                    acomment = "{:<40}".format('actor_link table musicvideo unmatched') +      \
                    "{:10d}".format(int(vlist[a][0])) + "{:10d}".format(int(vlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<14}".format(str(vlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (vlist[a][0], vlist[a][1], vlist[a][2], acomment))
                outdb.commit() 

            if len(slist) > 0:                            # Add season unmatcheds
                for a in range(len(slist)):
                    acomment = "{:<44}".format('actor_link table season unmatched') +          \
                    "{:10d}".format(int(slist[a][0])) + "{:10d}".format(int(slist[a][1])) +    \
                    "{:<10}".format(' ') + "{:>16}".format(str(slist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (slist[a][0], slist[a][1], slist[a][2], acomment))
                outdb.commit()                            
            outdb.close()
            return orprecs

        #==========================  Actor Table analysis ===============================

        if vtable == 'actor':                            # Check tables for unmatched data  
            cura = kodidb.execute('SELECT * FROM actor WHERE actor_id not in (SELECT actor_id         \
            FROM actor_link)')
            alist = cura.fetchall()
            del cura
            kodidb.close()
            orprecs = len(alist)
            xbmc.log('Kodi selective cleaner analyzer: ' + str(len(alist)), xbmc.LOGDEBUG)
            if orprecs == 0:                              # No Orphan records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(actor_id INTEGER, name TEXT, art_urls TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add actor_link unmatcheds
                for a in range(len(alist)):
                    acomment = "{:<32}".format('actor table actor_link missing') +                \
                    "{:12d}".format(int(str(alist[a][0]))) + "{:<12}".format(' ') + str(alist[a][1])
                    outdb.execute('INSERT OR REPLACE into vdb_temp(actor_id, name, comments) values    \
                    (?, ?, ?)', (alist[a][0], alist[a][1], acomment))
                outdb.commit()
            outdb.close()
            return orprecs

        #==========================  Art Table analysis ===============================

        if vtable == 'art':                       # Check tables for unmatched data 
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
            if orprecs == 0:                              # No Orphan records found
                outdb.close()
                return 0
            outdb.execute('CREATE TABLE vdb_temp(art_id INTEGER, media_id INTEGER, media_type TEXT, \
            type TEXT, url TEXT, comments TEXT)')
            outdb.commit()

            if len(alist) > 0:                            # Add actor unmatcheds
                for a in range(len(alist)):
                    acomment = "{:<47}".format('art table sets unmatched') +           \
                    "{:10d}".format(int(alist[a][0])) + "{:10d}".format(int(alist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(alist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (alist[a][0], alist[a][1], alist[a][2], acomment))
                outdb.commit()
                      
            if len(mlist) > 0:                            # Add movie unmatcheds
                for a in range(len(mlist)):
                    acomment = "{:<45}".format('art table movie unmatched') +           \
                    "{:10d}".format(int(mlist[a][0])) + "{:10d}".format(int(mlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(mlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (mlist[a][0], mlist[a][1], mlist[a][2], acomment))
                outdb.commit()

            if len(elist) > 0:                            # Add episode unmatcheds
                for a in range(len(elist)):
                    acomment = "{:<44}".format('art table episode unmatched') +         \
                    "{:10d}".format(int(elist[a][0])) + "{:10d}".format(int(elist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<16}".format(str(elist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (elist[a][0], elist[a][1], elist[a][2], acomment))
                outdb.commit()

            if len(tlist) > 0:                            # Add tvshow unmatcheds
                for a in range(len(tlist)):
                    acomment = "{:<44}".format('art table tvshow unmatched') +           \
                    "{:10d}".format(int(tlist[a][0])) + "{:10d}".format(int(tlist[a][1])) +     \
                    "{:<8}".format(' ') + "{:>16}".format(str(tlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (tlist[a][0], tlist[a][1], tlist[a][2], acomment))
                outdb.commit()  

            if len(vlist) > 0:                            # Add musicvideo unmatcheds
                for a in range(len(vlist)):
                    acomment = "{:<40}".format('art table musicvideo unmatched') +      \
                    "{:10d}".format(int(vlist[a][0])) + "{:10d}".format(int(vlist[a][1])) +    \
                    "{:<8}".format(' ') + "{:<14}".format(str(vlist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (vlist[a][0], vlist[a][1], vlist[a][2], acomment))
                outdb.commit() 

            if len(slist) > 0:                            # Add season unmatcheds
                for a in range(len(slist)):
                    acomment = "{:<44}".format('art table season unmatched') +          \
                    "{:10d}".format(int(slist[a][0])) + "{:10d}".format(int(slist[a][1])) +    \
                    "{:<10}".format(' ') + "{:>16}".format(str(slist[a][2]))
                    outdb.execute('INSERT OR REPLACE into vdb_temp(art_id, media_id, media_type,    \
                    comments) values (?, ?, ?, ?)', (slist[a][0], slist[a][1], slist[a][2], acomment))
                outdb.commit()                            
            outdb.close()
            return orprecs

     
    except Exception as e:
        printexception()    

def displayClean(vtable):                                 # Clean unmatched analysis

    dialog_text = translate(30358) + vtable
    xbmcgui.Dialog().ok(translate(30306), dialog_text)



