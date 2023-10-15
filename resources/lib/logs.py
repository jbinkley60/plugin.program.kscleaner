import xbmc
import xbmcgui
import xbmcplugin
import os
import xbmcaddon
import xbmcvfs
import csv 
from .common import openKodiDB, openKodiMuDB, openKscleanDB, printexception, translate
from .common import kgenlogUpdate, checkKscleanDB, nofeature
from .exports import exportData
from datetime import datetime

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo("path")
addon_icon = addon_path + '/resources/icon.png'

def displayGenLogs():

    dsfile = openKscleanDB()                                     # Open logs database

    menuitem1 = translate(30317)
    msdates = [menuitem1, "Most Recent"]
    msdialog = xbmcgui.Dialog()   

    cursync = dsfile.execute('SELECT DISTINCT kgDate FROM kscleanLog ORDER BY kgDate DESC LIMIT 30', )
    mstatdates = cursync.fetchall()                              # Get dates from database
    if mstatdates:        
        for a in range(len(mstatdates)):
            msdates.append(mstatdates[a][0])                     # Convert rows to list for dialog box
        mdate = msdialog.select(translate(30314), msdates)
        xbmc.log('Kodi selective cleaner selection is: ' + msdates[mdate], xbmc.LOGDEBUG)
        if mdate < 0:                                            # User cancel
            dsfile.close()
            return
        elif (msdates[mdate]) == "Most Recent":
            cursync = dsfile.execute('SELECT * FROM kscleanLog ORDER BY kgDate DESC, kgTime DESC LIMIT 2000',)
            headval = translate(30313)
        elif menuitem1 in msdates[mdate] :                       # CSV export of logs
            exportData(['kscleanLog'],'logs')
            return
        elif len(msdates[mdate]) > 2:                            # Get records for selected date
            cursync = dsfile.execute('SELECT * FROM kscleanLog WHERE kgDate=? ORDER BY kgTime DESC', \
            (msdates[mdate],))
            headval = translate(30315) + msdates[mdate][5:] + "-" + msdates[mdate][:4]
    else:                                                        # No gen logs found for date selected
        textval1 = translate(30311)                              # Should never happen. Safety check 
        msdialog.textviewer(translate(30308), textval1)            
        dsfile.close()
        return        

    mglogs = cursync.fetchall()                                   # Get logs from database
    textval1 = "{:^38}".format("Date") + "{:>32}".format(translate(30316))
    textval1 = textval1 + "\n" 

    if mglogs:
        for a in range(len(mglogs)):                              # Display logs if exist   
            msdate = mglogs[a][0]
            mstime = mglogs[a][1][:8]                             # Strip off milliseconds
            msynclog = mglogs[a][2]
            if msynclog[0:3] == '###':                            # Detect multiline logs
                msynclog = msynclog[3:]
                msdatetime = "{:>44}".format(" ")
            else:
                msdatetime = msdate + "   " + mstime + "      "
            textval1 = textval1 + "\n" + msdatetime + msynclog
        msdialog.textviewer(headval, textval1)                                     
    else:                                                         # No records found for date selected   
        perfdialog = xbmcgui.Dialog()
        dialog_text = translate(30312)        
        perfdialog.ok(translate(30308), dialog_text)     
    dsfile.close()
    return


