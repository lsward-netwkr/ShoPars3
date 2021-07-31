# ShoPars3
Shodan to MySQL parser. Python-based, it takes output from Shodan.io and places it in a MySQL database for processing. 

# Purpose
This was created in 2018, and was my second foray in to Python development to fulfil a need in my job. I am obviously by no means an expert, but this code will be slightly revamped in the coming weeks as free time comes up to ensure that future users can simply add their credentials for Shodan API and their MySQL server, and the script will handle everything else, checking the table exists (and if not, creating it), connecting to and downloading data from Shodan, and then begin inserting results in to MySQL. 

# Usage
It's designed to be run using cron, or the Windows Task Scheduler at a time frequency of your choosing. To ensure that you aren't eating through your API credits however, be sparing and maybe set it to run every 6 hours. 

On Windows, invoke the Shodan API using...
C:\Projects\shodan>shodan parse --fields ip_str,hostnames,transport,port,timestamp,data,title,ssl.cert,ssl.cipher,ssl.versions --separator ³ data.json.gz > data.csv

ShoPars3 can then be run, and will take data.csv as its input, and uses ³ as its delimiter as some Shodan output can include ',' which breaks things. It has no arguments.

# Dependencies
- Python 3.6 (tested on Windows and Ubuntu)
- Shodan connector for Python (install with: pip install shodan)
- MySQL connector for Python (install with: pip install mysql.connector)

MySQL Server notes: A MySQL server, either local or remote. I've tested this with a local MySQL 8.0 server, with the password stored as legacy/native mysql.

# Future
I would eventually like to create a web UI for this, and have a second table I can join the ShoPars3 output using with custom columns so internal notes can be added on who owns the server or service, or additional notes for provisioning, maintenance, and decommission for systems that are visible to the internet.

# Licence
This WAS the GNU GPL v3, however the licence was changed to the GNU Affero GPL v3.0. The reason is to ensure that changes to the code where it is to be used in a service-provision context is contributed back, so that every user of the code can benefit.
