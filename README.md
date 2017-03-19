Coracle 2.0
==============
[Coracle](https://en.wikipedia.org/wiki/Coracle) is a lightweight modified PhantomJS/Outlook365 client designed to listen and monitor and automate the UAlbany ITS shift manager and all the events that take place.

-By Alexander Comerford

## About

Grabbing and dropping shifts can be very annoying because the ITS website is an old system and all the other employees are much more adamant and motivated to check the site constantly to get shifts.

Coracle works by having an Outlook365 client listening for emails from the UAlbany server specifically being sent from ITS about shifts. If a new email is recieved, coracle will check its settings set by the user to see if it should temp take/temp drop the shift. If it wants to take the shift, coracle will go to the ITS website and take action and temp/perm take the shift. 

### Prerequisites

This program is based in python so make sure you have python 2.7 installed

The 2 dependencies for this script are [PhantomJS](http://phantomjs.org/download.html), and [Selenium](http://selenium-python.readthedocs.io/installation.html). If you don't know how to computer, contact Alex from ITS and he'll give you advice.

Instructions
------------

### 1. Input your credentials

Go to ```creds.json``` and under ```ITS``` and ```Outlook``` input your associated credentials. Since python is interpreted you can see the source code to make sure nothing malicious is being done with your information.

### 2. Configure the settings

Go to ```settings.json``` and modify the settings accordingly

* *active* is the number of seconds the program will stay active and listen for dropped and taken shifts
* *logging* is a boolean value that will log via the terminal all of what coracle is thinking and doing
* *email* is the email coracle will notify when a shift was been taken/dropped successfully. If you don't want it to notify you, you can take the parameter out of leave the email as ""
* *refresh* is the time coracle will wait before it checks your email again for any new emails. WARNING if you make this time very small it may slow down your computer.   
* *dates* is a subsetting where you will input your personal preferences on what times you want coracle to focus on

### Configuring dates

*dates* may look complicated in ```settings.json``` but once you get the hang of the syntax, you'll set it up once and forget about it until you get lazy and want to change it back.

The general syntax for a *date-range* setting looks as follows

```json
<date-range ex. 9/30/16-10/31/16>:{
    <day ex. "Monday">:{
	    "locations":[<location1 ex. SciLib>, <location2>, ...]
	    "hours":{
		<time-range ex."4PM-5PM">:[<preffered-action ex. "TempTake">],
		...
	    }
    },
    ...
}
```

**Explanation:**

*dates* is split into something called *date-range*(s). This enables users to have multiple different actions seperated by a ranges of time. A *date* is read as "mm/dd/yyyy". There is only ~one~ exception to that format and that is if you put "all" as the *date-range* which, no matter what a new email says, will check against the rest of the setting to see if it should take the shift.

Inside of each *date-range* you include *days* (Monday, Tuesday, etc.) as the keys. Again, just like *dates*, you can include the *all* key instead of (Monday, Tuesday, etc.) and coracle will proceed without discretion for the day of the week.  
Inside of each day you have the option of including a *locations* parameter which will only take the shift if the listed location is the one that is free. If you do not include this option, coracle will continue to try to grab shifts, agnostic of location. 

In addition, you must include *hours* which consists of a *time-range* key such as "10-11AM" and a value in a list format with the preferred list of actions.

### 3. Run

With the proper settings in place made by the user you can run

```bash
python coracle.py
``` 

To run and initialize coracle to start listening for events and reacting. If you have your own settings/credentials you want to use, you can use ```-s <settings-file>``` to use your own settings file, and ```-c <credentials-file>``` to use your own credentials file



IMPORTANT FOR DEVELOPMENT

make sure you cache a history
get the users current schedule
make sure settings times don't conflict with users schedule
emails don't provide a location, make sure you check with ITS client if location is available