## ShoPars3 - Load and commit Shodan downloaded data to database.
## a Lee Ward (l.ward@netwkr.net) tool, developed September 2018.
## Started development 08/09/2018 at v0.5
## v0.6 ready 09/09/2018

## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## Note: I'm not a developer, I'm an IT Security Officer in my day job and an IT engineer at all other times.
## Code quality wasn't what I was going for when I made this, I just needed a quick solution so I could
## quickly browse Shodan data for changes to networks I was interested in learning about the infrastructure in use.
## I'm inexperienced in Python, so please forgive the mess!

## commandline used to acquire data in a compatible format, using the Shodan Python CLI:
## C:\Projects\shodan>shodan parse --fields ip_str,hostnames,transport,port,timestamp,data,title,ssl.cert,ssl.cipher,ssl.versions --separator ³ data.json.gz > data.csv

## Requires:
## Python 3.6 (tested on Windows)
## MySQL connector for Python (install with: pip install mysql.connector)
## A MySQL server, either local or remote. I've tested this with a local MySQL 8.0 server, with the password stored as legacy/native mysql.

## import dependencies. ensure that you've pip installed mysql.connector. 
import os
import time
import mysql.connector
from mysql.connector import errorcode
import csv

## this script assumes we've already got the download from Shodan.
## would like to achieve:
## - open the file [DONE 08/09/2018]
## - on a line by line basis query mysql to see if the record already exists [DONE 09/09/2018]
## - if yes, update timestamp and server banner. [DONE 09/09/2018]
## - if no, add record [DONE 08/09/2018]
## ... in v0.6 [NOW 0.6 09/09/2018]

## - error handling when database couldn't be found
## - regex to search for and split out the Server, X-Powered-By headers from HTTP response headers.
## - discover any web technologies in use using the header information
## - pull down and store HTML output and discover any web technologies in use from this information
## ... in v0.7

print("ShoPars3 v0.6 (09/09/2018) licenced under GPLv3")
print("=============------")
print("A quickly hacked-together at-home tool by Lee Ward (l.ward@netwkr.net)")
print("\n")
print("ShoPars3 Copyright (c)2018 Lee Ward")
print("This program comes with ABSOLUTELY NO WARRANTY.")
print("For information, please visit gnu.org/licenses/gpl-3.0.en.html")
print("This is free software, and you are welcome to redistribute it")
print("under certain conditions under the GPL v3.")
print("\n")
print("------======= TASK BEGIN =======------")
print("\n")

## Connect to MySQL/MariaDB...
## IMPORTANT: Edit DB credentials as required.
## ALSO IMPORTANT: The table this works with has the following CREATE statement:
''' BEGIN...
CREATE TABLE `data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_seen` int(11) NOT NULL,
  `ip_str` varchar(15) NOT NULL,
  `hostnames` varchar(100) DEFAULT NULL,
  `transport` varchar(5) NOT NULL,
  `port` int(11) NOT NULL,
  `timestamp` int(11) NOT NULL,
  `data` longtext,
  `html_title` varchar(120) DEFAULT NULL,
  `ssl_cert` longtext,
  `ssl_cipher` longtext,
  `ssl_versions` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1379 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
...END '''

try:
    dbc = mysql.connector.connect(user='EnterYourDBUserHere', password='EnterYourDBPasswordHere', host='EnterYourDBHostHere', database='EnterYourDBNameHere')

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("!! Credential Error - Database connection fail. Errors may persist...")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("!! Database Error - Database doesn't exist? Errors may persist...")
    else:
        print(err)
else:
    print(">> DB connection good.")

cursor = dbc.cursor(buffered=True)
## Hack so I can see how many new items got added (if any). Should implement this with a bit more finesse when more experienced.
num = 1

## open csv data file
with open('data.csv') as csvfile:
    data = csv.reader(csvfile, delimiter='³')
    for row in data:
        ## print(row[0],".",row[1])
        ## Check if record exists
        query = "SELECT * FROM data WHERE ip_str = %s AND transport = %s AND port = %s"
        qdata = (row[0],row[2],row[3])
        cursor.execute(query, qdata)
        if cursor.rowcount > 0:
            ## Row already exists with same IP, transport and port.
            ## Convert CSV timestamp to epoch, and compare that with what the DB is storing.
            pattern = '%Y-%m-%dT%H:%M:%S.%f'
            epoch = int(time.mktime(time.strptime(row[4], pattern)))
                        
            for data in cursor.fetchall():
                if data[6] == epoch:
                    ## do nothing, skip
                    print(">> Record for",row[0],row[2],"port",row[3],"is up to date, skipping...")
                else:
                    ##  print(data[6],epoch)
                    ## 09/09/2018 dirty fix to fix my already imported data as didn't update timestamp at the same time as the server banner data and ssl cert info.
                    ##  query = "UPDATE data SET timestamp = %s WHERE id = %s"
                    ##  qdata = (epoch, data[0])
                    ##  cursor.execute(query, qdata)
                    ## check if banner needs to be updated?
                    if row[5] != data[7]:
                        ## Different, update it.
                        query = "UPDATE data SET data = %s, timestamp = %s WHERE id = %s"
                        qdata = (row[5], epoch, data[0])
                        cursor.execute(query, qdata)
                        print(">> Server banner data updated. Record ID:",data[0])
                    if row[7] != data[9]:
                        ## Different, update it.
                        query = "UPDATE data SET ssl_cert = %s, timestamp = %s WHERE id = %s"
                        qdata = (row[7], epoch, data[0])
                        cursor.execute(query, qdata)
                        print(">> SSL cert data updated. Record ID:",data[0])

                        
        else:
            ## Add new record.
            ## Shodan time/date pattern example: '2018-08-11T12:42:31.001557'
            ## convert and store timestamp in epoch because it's easier to work with in PHP.   
            pattern = '%Y-%m-%dT%H:%M:%S.%f'
            epoch = int(time.mktime(time.strptime(row[4], pattern)))
            outdate = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(epoch))
            ##print (row[4]," = ",epoch," = ", outdate)
            current_time = int(time.time())
            query = "INSERT INTO data (first_seen,ip_str,hostnames,transport,port,timestamp,data,html_title,ssl_cert,ssl_cipher,ssl_versions) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            qdata = (current_time,row[0],row[1],row[2],row[3],epoch,row[5],row[6],row[7],row[8],row[9])
            cursor.execute(query, qdata)
            print(">> New record",num,"for IP",row[0], row[2],"port",row[3],"ready for commit...")
            num = num+1

## DB commits aren't automatically performed, until we...
dbc.commit()
print(">> Data committed successfully!")

## Close MySQL/MariaDB connection
print(">> Closing DB connection...")
dbc.close()

print(">> Complete. Data is ready for use (hopefully).")
print("------======= TASK END =======------")


