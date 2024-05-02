import xbmc
import xbmcgui
import xbmcplugin
import os
import xbmcaddon
import xbmcvfs
from resources.lib.common import openKodiDB, openKodiMuDB, openKscleanDB, printexception
from resources.lib.common import kgenlogUpdate, checkKscleanDB, nofeature, settings
from resources.lib.common import get_installedversion, getmuDatabaseName, translate

from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'

def checkMuTriggers():                                              # Check Music database Triggers 

    try:
        checktrig = settings('trgverify')                           # Check if trigger checking is enabled 
        dbtype = settings('mudbtype')                               # Check database type
        version = get_installedversion()                            # get Kodi version

        triggers = [('tgrDeleteAlbum',), ('tgrDeleteArtist',), ('tgrDeleteSong',), ('tgrDeleteSource',), \
        ('tgrInsertSong',), ('tgrUpdateSong',), ('tgrInsertAlbum',), ('tgrUpdateAlbum',),                \
        ('tgrInsertArtist',), ('tgrUpdateArtist',), ('tgrInsertGenre',), ('tgrInsertSongArtist',),       \
        ('tgrInsertAlbumArtist',), ('tgrDeleteSongArtist',), ('tgrDeleteAlbumArtist',), ]

        if checktrig != 'off':        
            xbmc.log('KS Cleaner music DB trigger checking enabled:' + ' ' + dbtype + ' ' + str(version), xbmc.LOGINFO)
            kmfile = openKodiMuDB(dbtype)                           # Open Kodi music database
            if kmfile == None:
                kgenlog = 'KS Cleaner Unable to open music database'
                kgenlogUpdate(kgenlog)
                return                
            if dbtype == 'local':
                mutrquery = "select name from sqlite_master where type = 'trigger'"
                curpf = kmfile.execute(mutrquery)
                trmusic = curpf.fetchall()                           # Get triggers from master database
                del curpf 
            else:
                dbname = getmuDatabaseName(dbtype)
                trmusic = []
                mucursor = kmfile.cursor()
                mutrquery = "show triggers from mymusic" + str(dbname)
                mucursor.execute(mutrquery)
                tempmusic = mucursor.fetchall()                     # Get triggers from master database
                if len(tempmusic) > 0:
                    for temp in tempmusic:
                        trmusic.append(temp[0])

            xbmc.log('KS Cleaner trmusic:' + str(trmusic), xbmc.LOGINFO)

            if len(trmusic) != len(triggers):                       # Check for all triggers
                for trigger in triggers:
                    xbmc.log('KS Cleaner trmusic:' + str(trigger), xbmc.LOGDEBUG)
                    if trigger not in trmusic and dbtype == 'local':    # Replace missing trigger
                        replaceTrigger(kmfile, trigger, version, checktrig)
                    elif trigger[0] not in trmusic and dbtype == 'mysql':
                        replacesqlTrigger(mucursor, trigger, version, checktrig)
                        #kgenlog = 'KS Cleaner missing music database trigger found: ' + trigger[0]
                        #kgenlogUpdate(kgenlog)
                        #xbmcgui.Dialog().ok(translate(30387) + ' - ' + trigger[0], translate(30388))
            else:
                kgenlog = 'KS Cleaner no missing music database triggers'
                kgenlogUpdate(kgenlog)
            kmfile.close()
        else:
            kgenlog = 'KS Cleaner music DB trigger checking is disabled'
            kgenlogUpdate(kgenlog)

    except Exception as e:
        printexception()
        kgenlog = 'KS Cleaner music DB missing trigger analysis failure'
        kgenlogUpdate(kgenlog)        
        

def replaceTrigger(kmfile, trigger, version, checktrig):         # replace missing music db trigger 

        xbmc.log('KS Cleaner music DB trigger checking is' + str(trigger[0]), xbmc.LOGDEBUG)
        mutrquery = None

        if checktrig == 'notify':                                # User requested notification
            dialog_text = translate(30389)
            dialog_head = translate(30387) + ' - ' + trigger[0]
            select = xbmcgui.Dialog().yesno(dialog_head, dialog_text)
            if select != 1:
                return

        if trigger[0] == 'tgrDeleteAlbum':
             mutrquery = "CREATE TRIGGER tgrDeleteAlbum AFTER delete ON album FOR EACH ROW BEGIN  \
             DELETE FROM song WHERE song.idAlbum = old.idAlbum;  DELETE FROM album_artist WHERE   \
             album_artist.idAlbum = old.idAlbum;  DELETE FROM album_source WHERE                  \
             album_source.idAlbum = old.idAlbum;  DELETE FROM art WHERE media_id=old.idAlbum AND  \
             media_type='album'; END"
        elif  trigger[0] == 'tgrDeleteAlbumArtist':
             mutrquery = "CREATE TRIGGER tgrDeleteAlbumArtist AFTER DELETE ON album_artist FOR    \
             EACH ROW BEGIN INSERT INTO removed_link (idArtist, idMedia, idRole)                  \
             VALUES(OLD.idArtist, OLD.idAlbum, -1); END"
        elif  trigger[0] == 'tgrDeleteArtist':
             mutrquery = "CREATE TRIGGER tgrDeleteArtist AFTER delete ON artist FOR EACH ROW      \
             BEGIN  DELETE FROM album_artist WHERE album_artist.idArtist = old.idArtist;  DELETE  \
             FROM song_artist WHERE song_artist.idArtist = old.idArtist;  DELETE FROM discography \
             WHERE discography.idArtist = old.idArtist;  DELETE FROM art WHERE                    \
             media_id=old.idArtist AND media_type='artist'; END"
        elif  trigger[0] == 'tgrDeleteSong':
             mutrquery = "CREATE TRIGGER tgrDeleteSong AFTER delete ON song FOR EACH ROW BEGIN    \
             DELETE FROM song_artist WHERE song_artist.idSong = old.idSong;  DELETE FROM          \
             song_genre WHERE song_genre.idSong = old.idSong;  DELETE FROM art WHERE              \
             media_id=old.idSong AND media_type='song'; END"
        elif  trigger[0] == 'tgrDeleteSongArtist':
             mutrquery = "CREATE TRIGGER tgrDeleteSongArtist AFTER DELETE ON song_artist FOR EACH \
             ROW BEGIN INSERT INTO removed_link (idArtist, idMedia, idRole) VALUES(OLD.idArtist,  \
             OLD.idSong, OLD.idRole); END"
        elif  trigger[0] == 'tgrDeleteSource':
             mutrquery = "CREATE TRIGGER tgrDeleteSource AFTER delete ON source FOR EACH ROW      \
             BEGIN  DELETE FROM source_path WHERE source_path.idSource = old.idSource;  DELETE    \
             FROM album_source WHERE album_source.idSource = old.idSource; END"
        elif  trigger[0] == 'tgrInsertAlbum':
             mutrquery = "CREATE TRIGGER tgrInsertAlbum AFTER INSERT ON album FOR EACH ROW BEGIN  \
             UPDATE album SET dateNew = DATETIME('now') WHERE idAlbum = NEW.idAlbum AND           \
             NEW.dateNew IS NULL; UPDATE album SET dateModified = DATETIME('now') WHERE idAlbum   \
             = NEW.idAlbum; END"
        elif  trigger[0] == 'tgrInsertAlbumArtist':
             mutrquery = "CREATE TRIGGER tgrInsertAlbumArtist AFTER INSERT ON album_artist FOR    \
             EACH ROW BEGIN DELETE FROM removed_link WHERE idArtist = NEW.idArtist AND idMedia    \
             = NEW.idAlbum AND idRole = -1; END"
        elif  trigger[0] == 'tgrInsertArtist':
             mutrquery = "CREATE TRIGGER tgrInsertArtist AFTER INSERT ON artist FOR EACH ROW      \
             BEGIN UPDATE artist SET dateNew = DATETIME('now') WHERE idArtist = NEW.idArtist AND  \
             NEW.dateNew IS NULL; UPDATE artist SET dateModified = DATETIME('now') WHERE idArtist \
             = NEW.idArtist; END"
        elif  trigger[0] == 'tgrInsertGenre':
             mutrquery = "CREATE TRIGGER tgrInsertGenre AFTER INSERT ON genre BEGIN UPDATE        \
             versiontagscan SET genresupdated = DATETIME('now'); END"
        elif  trigger[0] == 'tgrInsertSong':
             mutrquery = "CREATE TRIGGER tgrInsertSong AFTER INSERT ON song FOR EACH ROW BEGIN    \
             UPDATE song SET dateNew = DATETIME('now') WHERE idSong = NEW.idSong AND NEW.dateNew  \
             IS NULL; UPDATE song SET dateModified = DATETIME('now') WHERE idSong = NEW.idSong; END"
        elif  trigger[0] == 'tgrInsertSongArtist':
             mutrquery = "CREATE TRIGGER tgrInsertSongArtist AFTER INSERT ON song_artist FOR      \
             EACH ROW BEGIN DELETE FROM removed_link WHERE idArtist = NEW.idArtist AND idMedia    \
             = NEW.idSong AND idRole = NEW.idRole; END"
        elif  trigger[0] == 'tgrUpdateAlbum':
             mutrquery = "CREATE TRIGGER tgrUpdateAlbum AFTER UPDATE ON album FOR EACH ROW WHEN  \
             NEW.dateModified <= OLD.dateModified BEGIN UPDATE album SET dateModified =          \
             DATETIME('now') WHERE idAlbum = OLD.idAlbum; END"
        elif  trigger[0] == 'tgrUpdateArtist':
             mutrquery = "CREATE TRIGGER tgrUpdateArtist AFTER UPDATE ON artist FOR EACH ROW     \
             WHEN NEW.dateModified <= OLD.dateModified BEGIN UPDATE artist SET dateModified =    \
             DATETIME('now') WHERE idArtist = OLD.idArtist; END"
        elif  trigger[0] == 'tgrUpdateSong':
             mutrquery = "CREATE TRIGGER tgrUpdateSong AFTER UPDATE ON song FOR EACH ROW WHEN    \
             NEW.dateModified <= OLD.dateModified BEGIN UPDATE song SET dateModified =           \
             DATETIME('now') WHERE idSong = OLD.idSong; END"
        else:
             kgenlog = 'KS Cleaner the missing music database trigger ' + trigger[0] + ' was not '
             kgenlog = kgenlog + 'found in database. Please contact support.'
             kgenlogUpdate(kgenlog)

        if mutrquery != None:
            kmfile.execute(mutrquery)
            kmfile.commit() 
            kgenlog = 'KS Cleaner missing music database trigger replaced: ' + trigger[0]
            kgenlogUpdate(kgenlog)  


def replacesqlTrigger(kmfile, trigger, version, checktrig):      # replace missing music db trigger 

        xbmc.log('KS Cleaner music DB trigger checking is' + str(trigger[0]), xbmc.LOGDEBUG)
        mutrquery = None

        if checktrig == 'notify':                                # User requested notification
            dialog_text = translate(30389)
            dialog_head = translate(30387) + ' - ' + trigger[0]
            select = xbmcgui.Dialog().yesno(dialog_head, dialog_text)
            if select != 1:
                return

        if trigger[0] == 'tgrDeleteAlbum':
             mutrquery = "CREATE TRIGGER tgrDeleteAlbum AFTER delete ON album FOR EACH ROW BEGIN DELETE FROM song WHERE song.idAlbum = old.idAlbum;  DELETE FROM album_artist WHERE album_artist.idAlbum = old.idAlbum;  DELETE FROM album_source WHERE album_source.idAlbum = old.idAlbum;  DELETE FROM art WHERE media_id=old.idAlbum AND media_type='album'; END"
        elif  trigger[0] == 'tgrDeleteAlbumArtist':
             mutrquery = "CREATE TRIGGER tgrDeleteAlbumArtist AFTER DELETE ON album_artist FOR EACH ROW BEGIN INSERT INTO removed_link (idArtist, idMedia, idRole) VALUES(OLD.idArtist, OLD.idAlbum, -1); END"
        elif  trigger[0] == 'tgrDeleteArtist':
             mutrquery = "CREATE TRIGGER tgrDeleteArtist AFTER delete ON artist FOR EACH ROW BEGIN  DELETE FROM album_artist WHERE album_artist.idArtist = old.idArtist;  DELETE FROM song_artist WHERE song_artist.idArtist = old.idArtist;  DELETE FROM discography WHERE discography.idArtist = old.idArtist;  DELETE FROM art WHERE media_id=old.idArtist AND media_type='artist'; END"
        elif  trigger[0] == 'tgrDeleteSong':
             mutrquery = "CREATE TRIGGER tgrDeleteSong AFTER delete ON song FOR EACH ROW BEGIN  DELETE FROM song_artist WHERE song_artist.idSong = old.idSong;  DELETE FROM song_genre WHERE song_genre.idSong = old.idSong;  DELETE FROM art WHERE media_id=old.idSong AND media_type='song'; END"
        elif  trigger[0] == 'tgrDeleteSongArtist':
             mutrquery = "CREATE TRIGGER tgrDeleteSongArtist AFTER DELETE ON song_artist FOR EACH ROW BEGIN INSERT INTO removed_link (idArtist, idMedia, idRole) VALUES(OLD.idArtist, OLD.idSong, OLD.idRole); END"
        elif  trigger[0] == 'tgrDeleteSource':
             mutrquery = "CREATE TRIGGER tgrDeleteSource AFTER delete ON source FOR EACH ROW BEGIN  DELETE FROM source_path WHERE source_path.idSource = old.idSource;  DELETE FROM album_source WHERE album_source.idSource = old.idSource; END"
        elif  trigger[0] == 'tgrInsertAlbum':
             mutrquery = "CREATE TRIGGER tgrInsertAlbum BEFORE INSERT ON album FOR EACH ROW BEGIN  IF NEW.dateNew IS NULL THEN SET NEW.dateNew = now();  END IF;  SET NEW.dateModified = now(); END"
        elif  trigger[0] == 'tgrInsertAlbumArtist':
             mutrquery = "CREATE TRIGGER tgrInsertAlbumArtist AFTER INSERT ON album_artist FOR EACH ROW BEGIN DELETE FROM removed_link WHERE idArtist = NEW.idArtist AND idMedia = NEW.idAlbum AND idRole = -1; END"
        elif  trigger[0] == 'tgrInsertArtist':
             mutrquery = "CREATE TRIGGER tgrInsertArtist BEFORE INSERT ON artist FOR EACH ROW BEGIN  IF NEW.dateNew IS NULL THEN SET NEW.dateNew = now();  END IF;  SET NEW.dateModified = now(); END"
        elif  trigger[0] == 'tgrInsertGenre':
             mutrquery = "CREATE TRIGGER tgrInsertGenre AFTER INSERT ON genre FOR EACH ROW UPDATE versiontagscan SET genresupdated = now()"
        elif  trigger[0] == 'tgrInsertSong':
             mutrquery = "CREATE TRIGGER tgrInsertSong BEFORE INSERT ON song FOR EACH ROW BEGIN  IF NEW.dateNew IS NULL THEN SET NEW.dateNew = now();  END IF;  SET NEW.dateModified = now(); END"
        elif  trigger[0] == 'tgrInsertSongArtist':
             mutrquery = "CREATE TRIGGER tgrInsertSongArtist AFTER INSERT ON song_artist FOR EACH ROW BEGIN DELETE FROM removed_link WHERE idArtist = NEW.idArtist AND idMedia = NEW.idSong AND idRole = NEW.idRole; END"
        elif  trigger[0] == 'tgrUpdateAlbum':
             mutrquery = "CREATE TRIGGER tgrUpdateAlbum BEFORE UPDATE ON album FOR EACH ROW SET NEW.dateModified = now()"
        elif  trigger[0] == 'tgrUpdateArtist':
             mutrquery = "CREATE TRIGGER tgrUpdateArtist BEFORE UPDATE ON artist FOR EACH ROW SET NEW.dateModified = now()"
        elif  trigger[0] == 'tgrUpdateSong':
             mutrquery = "CREATE TRIGGER tgrUpdateSong BEFORE UPDATE ON song FOR EACH ROW SET NEW.dateModified = now()"
        else:
             kgenlog = 'KS Cleaner the missing music database trigger ' + trigger[0] + ' was not '
             kgenlog = kgenlog + 'found in database. Please contact support.'
             kgenlogUpdate(kgenlog)

        if mutrquery != None:
            kmfile.execute(mutrquery)
            #kmfile.commit() 
            kgenlog = 'KS Cleaner missing music SQL database trigger replaced: ' + trigger[0]
            kgenlogUpdate(kgenlog)  

