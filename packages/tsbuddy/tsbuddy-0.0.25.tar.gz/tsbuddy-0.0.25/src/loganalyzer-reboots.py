import sqlite3, os
import pandas as pd

def CleanOutput(string):
#Remove unneeded characters
    string = string.replace("[", "")
    string = string.replace("]", "")
    string = string.replace(",", "")
    string = string.replace("(", "")
    string = string.replace(")", "")
    string = string.replace("'", "")
    return string

def main():
#Setup Pandas
    src_dir = os.path.dirname(os.path.abspath(__file__))
    console = pd.read_csv("ConsoleLogsParsed.csv",index_col=False)
    reboots = pd.read_csv(src_dir+'/loglist-reboots.csv',index_col=False)
    #replaces NaN with an empty string. Otherwise, we'll get "argument of type 'float' is not iterable"
    reboots = reboots.fillna('')
    console = console.fillna('')
#Initialize Database
    with sqlite3.connect(':memory:') as conn:
        console.to_sql("TempLogs", conn, if_exists='append', index=False)
        reboots.to_sql("Checks", conn, if_exists='append', index=False)
#Make new table with Primary Key
        cursor = conn.cursor()
        cursor.execute("create table Logs(id integer primary key autoincrement, Year integer, Month text, Day integer, Time integer, SwitchName Text, AppID Text, Subapp Text, Priority text, LogMessage text)")
        cursor.execute("insert into Logs (Year, Month, Day, Time, SwitchName, AppID, Subapp, Priority, LogMessage) select Year, Month, Day, Time, SwitchName, AppID, Subapp, Priority, LogMessage from TempLogs")
        cursor.execute("drop table TempLogs")
        conn.commit()
#Compare
    #Get Number of rows in Check
        cursor.execute("select count(*) from Checks")
        CheckCount = cursor.fetchall()
    #Remove extra characters
        CheckCount = str(CheckCount)
        CheckCount = CleanOutput(CheckCount)
        CheckCount = int(CheckCount)
        #print(CheckCount)
        cursor.execute("Select * from Checks")
        output = cursor.fetchall()
        
    #Clean and compare. Add LogMeaning to matched logs.
        cursor.execute("alter table Logs add column LogMeaning")
        cursor.execute("alter table Logs add column LogMatch")
        cursor.execute("update Logs set LogMatch = 'false'")
        cursor.execute("alter table Logs add column PreviousTime")
        cursor.execute("alter table Logs add column TimeDiff")
        for line in output:
            line = str(line)
            parts = line.split(', ')
            Message = parts[0]
            Meaning = parts[1]
            Message = CleanOutput(Message)
            Meaning = CleanOutput(Meaning)
            cursor.execute("update Logs set LogMeaning = '"+Meaning+"' where LogMessage like '%"+Message+"%'")
            cursor.execute("update Logs set LogMatch = 'true' where LogMessage like '%"+Message+"%'")
#Set PreviousTime
        cursor.execute("select id from Logs where LogMatch = 'true'")
        output = cursor.fetchall()
        #print(output)
        matchIDs = []
        RebootIDs = []
        FirstRebootTime = ""
        for line in output:
            line = str(line)
            matchIDs.append(CleanOutput(line))
        counter = 0
        #print(len(matchIDs))
        for id in matchIDs:
            if counter == 0:
                cursor.execute("select Year,Month,Day,Time from Logs where id = "+str(id))
                output = cursor.fetchall()
                output = str(output)
                FirstRebootTime = CleanOutput(output)
                cursor.execute("update Logs set PreviousTime = 'First Log' where id = "+matchIDs[counter-1])
                counter += 1
                continue
            cursor.execute("select time from Logs where ID = "+id)
            output = cursor.fetchall()
            output = str(output)
            Rowtime = CleanOutput(output)
            #print(Rowtime)
            cursor.execute("update Logs set PreviousTime = '"+Rowtime+"' where id = "+matchIDs[counter-1])
            #print(Rowid)
            #print(Rowtime)
#Set TimeDiff. Convert provided timestamp to seconds, compare, 
# mark any logs with a difference greater than 5 minutes and convert back to timestamp
            RowtimeParts = Rowtime.split('.')
            RowtimeParts = RowtimeParts[0].split(':')
            Rowtime_hr = int(RowtimeParts[0])
            Rowtime_mn = int(RowtimeParts[1])
            Rowtime_sc = int(RowtimeParts[2])
            Rowtime_totalseconds = ((Rowtime_hr*3600)+(Rowtime_mn*60)+(Rowtime_sc))
            #PreviousTime
            cursor.execute("select time from Logs where id = "+matchIDs[counter-1])
            PreviousTime = cursor.fetchall()
            PreviousTime = CleanOutput(str(PreviousTime))
            PreviousTime = PreviousTime.split('.')
            PreviousTime = PreviousTime[0].split(':')
            PreviousTime_hr = int(PreviousTime[0])
            PreviousTime_mn = int(PreviousTime[1])
            PreviousTime_sc = int(PreviousTime[2])
            PreviousTime_totalseconds = ((PreviousTime_hr*3600)+(PreviousTime_mn*60)+(PreviousTime_sc))
            #print("Rowtime: "+str(Rowtime_totalseconds))
            #print("PreviousTime: "+str(PreviousTime_totalseconds))
            Diff = abs(Rowtime_totalseconds-PreviousTime_totalseconds)
            if Diff >= 3600:
                RebootIDs.append(id)
            DiffTime_hr,Remainder = divmod(Diff, 3600)
            DiffTime_mn,DiffTime_sc = divmod(Remainder, 60)
            DiffTime_hr = str(DiffTime_hr)
            DiffTime_mn = str(DiffTime_mn)
            DiffTime_sc = str(DiffTime_sc)
            if len(DiffTime_hr) == 1:
                DiffTime_hr = "0"+DiffTime_hr
            if len(DiffTime_mn) == 1:
                DiffTime_mn = "0"+DiffTime_mn
            if len(DiffTime_sc) == 1:
                DiffTime_sc = "0"+DiffTime_sc
            DiffTime = (DiffTime_hr+":"+DiffTime_mn+":"+DiffTime_sc)
            #print(Diff)
            #print(DiffTime_hr)
            #print(DiffTime_mn)
            #print(DiffTime_sc)
            #print(DiffTime)
            cursor.execute("update Logs set TimeDiff = '"+str(DiffTime)+"' where id = "+matchIDs[counter-1])
            counter += 1

#Select columns and export        
        Output = pd.read_sql("SELECT Year,Month,Day,Time,TimeDiff,SwitchName,AppID,Subapp,Priority,LogMessage,LogMeaning from Logs order by LogMatch desc", conn)
        Output.to_excel("tsbuddy-ConsoleLogAnalysis-Reboots.xlsx")

#List reboot count and times
        RebootCount = len(RebootIDs)
        RebootTimes = []
        for id in RebootIDs:
            cursor.execute("select Year,Month,Day,Time from Logs where id = "+str(id))
            output = cursor.fetchall()
            output = str(output)
            RebootTime = CleanOutput(output)
            RebootTimes.append(RebootTime)
        if RebootCount == 0 and len(matchIDs) != 0:
            print("This switch rebooted once around: "+FirstRebootTime)
        if RebootCount == 0 and len(matchIDs) == 0:
            print("There are no reboots in these switch logs.")
        if RebootCount > 0:
            print("This switch rebooted "+str(RebootCount)+" times around the following timestamps:")
            for time in RebootTimes:
                print(time)

main()