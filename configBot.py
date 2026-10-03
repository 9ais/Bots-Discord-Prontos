#Configurações do SEU Bot.
tokenBot = 'SeuToken'
prefixBot = '!'

from discord import Color
defaultColor = Color.from_rgb(0, 102, 255)
import sqlite3
def checkPunish(idServer):
    with sqlite3.connect("data.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT ban, kick, warn FROM configs WHERE serverId = ?", (idServer,))
        ban, kick, warn = map(bool, cursor.fetchone())
        if ban:
            return 0
        elif kick:
            return 1
        elif warn: 
            return 2
        
    
def updatePunish(serveId, idPunish):
     with sqlite3.connect("data.db") as db:
            cursor = db.cursor()
            if idPunish == 0:
                cursor.execute("UPDATE configs SET ban = ?, kick = ?, warn = ? WHERE serverId = ?", (True, False, False, serveId))
            elif idPunish == 1:
                cursor.execute("UPDATE configs SET ban = ?, kick = ?, warn = ? WHERE serverId = ?", (False, True, False, serveId))
            elif idPunish == 2:
                cursor.execute("UPDATE configs SET ban = ?, kick = ?, warn = ? WHERE serverId = ?", (False, False, True, serveId))
                
            db.commit()
        
    
def checkServer(idServer):
    with sqlite3.connect("data.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT serverId FROM configs WHERE serverId = ?", (idServer,))
        if cursor.fetchone() != None:
            return True
        else:
            try:
                with sqlite3.connect("data.db") as db:
                    cursor = db.cursor()
                    cursor.execute("INSERT INTO configs (serverId) VALUES (?)", (idServer,))
                    db.commit()
            except:
                return False
            
            return True
        
def checkActive(idServer):
    with sqlite3.connect("data.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT active FROM configs WHERE serverId = ?", (idServer,))
        active = bool(cursor.fetchone()[0])
        return active
    
#UpdateActive
def updateActive(idServer):
    active = checkActive(idServer)
    with sqlite3.connect("data.db") as db:
        cursor = db.cursor()
        cursor.execute("UPDATE configs SET active = ? WHERE serverId = ?", (not active, idServer))
        db.commit()
    
def checkChannel(idServer):
    with sqlite3.connect("data.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT channelId FROM configs WHERE serverId = ?", (idServer,))
        channel = cursor.fetchone()
        return channel[0]
        
def updateChannel(idServer, channelId):
    with sqlite3.connect("data.db") as db:
        cursor = db.cursor()
        cursor.execute("UPDATE configs SET channelId = ? WHERE serverId = ?", (channelId, idServer))
        db.commit()
                
async def connectData():
    with sqlite3.connect("data.db") as db:
        cursor = db.cursor()
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS configs (
                        serverId INTEGER PRIMARY KEY,
                        active BOOLEAN DEFAULT FALSE,
                        ban BOOLEAN DEFAULT FALSE,
                        kick BOOLEAN DEFAULT TRUE,
                        warn BOOLEAN DEFAULT FALSE,
                        channelId INTEGER DEFAULT NULL
                        )
    """)
        db.commit()
        
