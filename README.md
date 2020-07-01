Created for Unify OpenScape business PBX systems.

Tested on versions up to R7. 

## IMPORTANT:
"db_template.db" is provided for the correct columns. You will need to enter the:
Company name, IP address (https://1.2.3.4:443), username (name@system), and password for each customer.

You will need to edit the config file (project/src/{version}/config.ini.template). Rename to "config.ini" and edit as needed.

1 = YES, 0 = NO

[options]

backup_location = This is where the backups will be stored once done, in individual customer folder names (dependant on the company name provided).

database_loc = Please enter where the database is stored

multicore_on = This is to choose whether or not you would like to use multicore processing. A task will be run on each core; 4 cores = 4 backups at once

cores = Set the number of cores you would like (dependandt on multicore_on)

nas = Whether you are using a network file share (this checks whether the drive is connected, and waits until is)

nas_location = Address to the NAS

onedrive = If you are using onedrive desktop app, you can use this to alert you if the onedrive app is *not* running

&nbsp;

[selenium]

headless = This should always be 1 except for debugging

&nbsp;

[email]

email_on = Whether to email on completion or not

from = The email to be sent from

to = Where the email should be sent

&nbsp;

[email_server]

All options here are dependant on you and your SMTP server

