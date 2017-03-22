Coracle 2.0
==============
[Coracle](https://en.wikipedia.org/wiki/Coracle) is a lightweight modified PhantomJS/Outlook365 client designed to listen monitor and automate the UAlbany Information Technology Services (ITS) shift manager based on user configuration.

-By Alexander Comerford

## About

Instead of visiting the ITS website only to find an unavailable shift or an inconvenient one, Coracle constantly monitors for dropped shifts and grabs the most desirable for the user.

Coracle works with 2 main components. 

1. Leveraging the IMAP python client, and listening for emails from the UAlbany mail server.
2. PhantomJS headless webkit to interact with the ITS shift management website

### Prerequisites

This program is based in python so make sure you have python 2.7 installed

The 2 dependencies for this script are [PhantomJS](http://phantomjs.org/download.html), and [Selenium](http://selenium-python.readthedocs.io/installation.html). There are multiple youtube videos on how to install them

Instructions
------------

### 1. Input your credentials

Edit ```creds.json``` and input your associated credentials. 

### 2. Configure the settings

Edit ```settings.json``` and modify the settings accordingly

* ***active*** is the number of seconds the program will stay active and listen for dropped and taken shifts
* ***logging*** is a boolean value that will log via the terminal all of what coracle is thinking and doing
* <del><b>*email*</b></del> (work in progress) <del>is the email coracle will notify when a shift was been taken/dropped successfully. If you don't want it to notify you, you can take the parameter out of leave the email as ""</del>
* ***refresh*** is the time coracle will wait before it checks your email again for any new emails. WARNING if you make this time very small it may slow down your computer.   
* ***dates*** is a subsetting where you will input your personal preferences on what times you want coracle to focus on

### Configuring dates

***dates*** may look complicated in ```settings.json``` but once you get the hang of the syntax it is easy to maintain and change.

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

If you have your own settings/credentials you want to use, you can use ```-s <settings-file>``` to use your own settings file, and ```-c <credentials-file>``` to use your own credentials file

IMPORTANT FOR DEVELOPMENT

* make sure you cache a history
* get the users current schedule
* make sure settings times don't conflict with users schedule
* emails don't provide a location, make sure you check with ITS client if * location is available