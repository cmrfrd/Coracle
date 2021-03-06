from os.path import abspath, dirname, realpath, join
import json
import datetime
import logging
import logging.config
from copy import deepcopy

from ..constants import *
from ..coracle_exceptions import ParseException

current_filepath = dirname(realpath(__file__))

logging.config.fileConfig(join(current_filepath, "..", PATH_TO_DEFAULT_LOGGING_FILE))

class File_Parser(object):
    '''
    Parse contains the methods needed for
    loading a json,
    json to dict,
    checking loading.

    You must override validate() when validating a loaded dict
    '''
    def __init__(self, filepath=None, advanced_logging=False):
        self.filepath = None
        self.input_dict = None

        self.parser_logger = logging.getLogger("parser")
        self.simple_logger = logging.getLogger("simple_log")

        if advanced_logging:
            self.simple_logger.handlers = [h for h in self.simple_logger.handlers if type(h) != logging.StreamHandler]
        else:
            self.parser_logger.handlers = [h for h in self.parser_logger.handlers if type(h) != logging.StreamHandler]
        if filepath != None:self.load(filepath) 

    @staticmethod
    def json_to_dict(filepath):
        '''
        Provided a string filepath, return a dictionary object from a json
        file in ../settings/
        '''
        with open(join(current_filepath, filepath)) as json_file:
            return json.load(json_file)
        
    def get_dict(self):
        '''check if the dict has been loaded, if it has, then return the dict
        '''
        self.check_loaded()
        return self.input_dict

    def is_loaded(self):
        '''return boolean if dict is initialized
        '''
        return self.input_dict != None

    def check_loaded(self):
        '''check if "input_dict" is loaded, if not, throw ParseException
        '''
        if not self.is_loaded():
            self.parser_logger.error("No settings json has been loaded into %s" % (self.__class__))
            self.simple_logger.error("FAILURE TO LOAD SETTINGS")
            raise ParseException("No settings have been loaded")

    def load(self, filepath=None):
        '''
        Provided a filepath or given a filepath, load into class a settings_dict
        and return original parse to user
        '''
        self.parser_logger.info("Loading %s into parser %s" % (filepath, self.__class__))
        if not self.filepath:#if a filepath has not been loaded
            if not filepath:
                self.parser_logger.error("No filepath found or provided in %s" % (self.__class__))
                self.simple_logger.error("FAILURE TO INCLUDE FILEPATH")
                raise ParseException("No filepath specified in __init__ or load")
            self.filepath = filepath

        self.parser_logger.info("Converting %s to dict" % (filepath))
        self.input_dict = File_Parser.json_to_dict(self.filepath)
        self.parser_logger.info("Data conversion loading of %s is successful" % (self.filepath))
        return self

    def validate(self, filepath=None):
        raise NotImplementedError("Class %s does not implement the 'parse' method" % (str(self.__class__)))




class Credentials_Parser(File_Parser):
    '''
    credentials parser will parse a "creds.json" file for important
    paramaters needed to run coracle
    '''
    def validate(self, filepath=PATH_TO_DEFAULT_CREDENTIALS_FILE):
        '''
        given a filepath, parse the correct info from credentials
        and return the dict if correctly formatted
        '''
        self.load(filepath)

        self.parser_logger.info("Validating %s in %s" % (self.filepath, self.__class__))

        self.is_valid_credentials("ITS")
        self.is_valid_credentials("Outlook")

        self.parser_logger.info("%s successfully validated in %s, no errors" % (self.filepath, self.__class__))
        self.simple_logger.info("SUCCESSFUL CREDENTIALS FORMAT")

        return self.get_dict()
    
    def check_username_password(self, creds_dict):
        '''provided some dictionary, check to make sure username and password key exist
        '''
        self.parser_logger.info("Validating username and password")
        try:
            username = creds_dict["username"]
            password = creds_dict["password"]

            if not isinstance(username, unicode):
                self.parser_logger.error("Invalid type %s for 'username'" % (type(username)))
                raise TypeError("'username' in %s is malformed or wrong type" % (self.filepath))
            if not isinstance(password, unicode):
                self.parser_logger.error("Invalid type %s for 'password'" % (type(password)))
                raise TypeError("'password' in %s is malformed or wrong type" % (self.filepath))
        except KeyError, e:
            self.parser_logger.error("'username' and/or 'password' missing")
            raise ParseException("Unable to find username and/or password in %s" % (self.filepath))

    def is_valid_credentials(self, key):
        '''provided a dict, and given a key, check to make sure that key has 'username' and 'password'
        '''
        self.check_loaded()
        
        self.parser_logger.info("Validating %s credentials" % (key))
        try:
            creds = self.get_dict()[key]
        
            if not isinstance(creds, dict):
                self.parser_logger.error("Invalid type %s for '%s'" % (type(username), str(key)))
                raise TypeError("'%s' paramater malformed, not in dict format in %s" % (key, self.filepath))
            self.check_username_password(creds)
        except KeyError, e:
            self.parser_logger.error("Missing paramater %s in %s" % (str(key), self.filepath)) 
            raise ParseException("No '%s' paramater listed in %s" % (key, self.filepath))

class Settings_Parser(File_Parser):
    '''
    settings_parse will parse a "settings.json" file for important
    paramaters needed to run coracle
    '''
    def validate(self, filepath=PATH_TO_DEFAULT_SETTINGS_FILE):
        '''
        Given a filepath in the init of the class, parse the correct info
        from the file and create an authenticated "settings" dict
        '''
        self.load(filepath)

        self.parser_logger.info("Validating %s in %s" % (self.filepath, self.__class__))

        self.is_valid_active()
        self.is_valid_logging()
        self.is_valid_notification_email()
        self.is_valid_refresh()
        self.is_valid_dates()

        self.parser_logger.info("%s successfully validated in %s, no errors" % (self.filepath, self.__class__))
        self.simple_logger.info("SUCCESSFUL SETTINGS FORMAT")

        return self.get_dict()

    def is_valid_active(self):
        '''provided a settings_dict, make sure "active" is set properly
        '''
        self.check_loaded()

        self.parser_logger.info("Validating 'active' in %s" % (self.filepath))
        try:
            active = self.get_dict()["active"]

            if not isinstance(active, int):
                self.parser_logger.error("Invalid type %s for 'active'" % (type(active)))
                raise TypeError("'active' needs to be an integer in " + self.filepath)
            if active < -1:
                self.parser_logger.error("%s not within range for 'active'" % (active))
                raise ValueError("'active' is not within bounds -2 < x < infinity in " + self.filepath)
        except KeyError, e:
            self.parser_logger.error("Missing paramater 'active' in %s" % (self.filepath))
            raise ParseException("No 'active' paramater set in %s" % (self.filepath))

    def is_valid_logging(self):
        '''provided a settings_dict, make sure "logging" is set properly
        '''
        self.check_loaded()

        self.parser_logger.info("Validating 'logging' in %s" % (self.filepath))
        try:
            logging = self.get_dict()["advanced_logging"]

            if not isinstance(logging, bool):
                self.parser_logger.error("Invalid type %s for 'logging'" % (type(logging)))
                raise TypeError("'logging' needs to be a bool in %s" % (self.filepath))
        except KeyError, e:
            self.parser_logger.warning("'logging' paramater not set, defaulting to false")
            self.get_dict()["logging"] = False
        
    def is_valid_notification_email(self):
        '''provided a settings_dict, make sure "notification_email" is set properly
        '''
        self.check_loaded()

        self.parser_logger.info("Validating 'notification_email' in %s" % (self.filepath))
        try:
            email = self.get_dict()["notification_email"]
            if not isinstance(email, unicode):
                self.parser_logger.error("Invalid type %s for 'notification_email'" % (type(email)))
                raise TypeError("'notification_email' needs to be a str in %s" % (self.filepath))
        except KeyError, e:
            self.parser_logger.warning("'notification_email' paramater not set, no notification email will be sent")
            self.get_dict()["notification_email"] = ""

    def is_valid_refresh(self):
        '''provided a settings_dict, make sure "active" is set properly
        '''
        self.check_loaded()

        self.parser_logger.info("Validating 'refresh' in %s" % (self.filepath))
        try:
            refresh = self.get_dict()["refresh"]

            if not isinstance(refresh, int):
                self.parser_logger.error("Invalid type %s for 'refresh'" % (type(refresh)))
                raise TypeError("'refresh' needs to be an integer in %s" % (self.filepath))
            if refresh < -1:
                self.parser_logger.error("%s not within range for 'refresh'" % (refresh))
                raise ValueError("'refresh' is not within bounds 0 < x < infinity in %s" % (self.filepath))
        except KeyError, e:
            self.parser_logger.error("Missing paramater 'refresh' in %s" % (self.filepath))
            raise ParseException("No 'refresh' paramater set in %s" % (self.filepath))

    def is_valid_date_range(self, date_range):
        '''Provided a date_range, be sure the date_range is valid with datetime, or is "all"
        '''
        self.parser_logger.info("--Validating date_range %s" % (date_range))
        try:
            if date_range == "all":
                return []
            date1, date2 = date_range.split("-")
            d1 = datetime.datetime.strptime(date1, "%m/%d/%y")
            d2 = datetime.datetime.strptime(date2, "%m/%d/%y")
        except ValueError:
            self.parser_logger.error("Invalid format")
            raise ValueError("date_range %s is malformed, must be in mm/dd/yy-mm/dd/yy format" % (date_range))
        return [d1, d2]

    def is_valid_hour_range(self, hour_range):
        '''provided an hour_range, check to see if it is correctly formatted
        '''
        self.parser_logger.info("------Validating hour_range")
        try:
            if hour_range == "all":
                return []
            time1, time2 = hour_range.split("-")
            t1 = datetime.datetime.strptime(time1, "%H:%M%p")
            t2 = datetime.datetime.strptime(time2, "%H:%M%p")
        except ValueError:
            self.parser_logger.error("Invalid format")
            raise ValueError("hour_range %s is malformed, must be in hh:mmAM/PM format" % (date_range))
        return [t1, t2]

    def is_valid_weekday(self, weekday):
        '''provided a weekday, be sure location, and hours are valid
        '''
        self.parser_logger.info("----Validating locations")
        try:
            locations = weekday["locations"]

            if not isinstance(locations, list):
                self.parser_logger.error("Invalid type %s for 'locations'" % (type(locations)))
                raise TypeError("'locations' must be a in 'list' format in %s" % (self.filepath))
            if locations == []:
                self.parser_logger.warning("No 'locations' provided, default any location")
                weekday["locations"] = LOCATIONS[:]
            if len(set(locations).difference(set(LOCATIONS))) > 0:
                self.parser_logger.error("Invalid location(s) %s" % (set(locations).difference(set(LOCATIONS))))
                raise ParseException("One or more locations in %s are invalid" % (locations))
        except KeyError:
            self.parser_logger.warning("No 'locations' provided, default any location")
            weekday["locations"] = LOCATIONS[:]

        self.parser_logger.info("----Validating hours")
        try:
            hours = weekday["hours"]
            new_hours = deepcopy(hours)

            if not isinstance(hours, dict):
                self.parser_logger.error("Invalid type %s for 'hours'" % (type(hours)))
                raise TypeError("'hours' must be a in 'dict' format in %s" % (self.filepath))
            for hour_key, actions in hours.iteritems():
                hour_range = self.is_valid_hour_range(hour_key)
                new_hours[hour_key+"_range"] = hour_range
                self.parser_logger.info("------Validating actions")
                if not isinstance(actions, list):
                    self.parser_logger.error("Invalid type %s for 'actions'" % (type(actions)))
                    raise TypeError("'actions' is in an invalid format in %s" % (self.filepath))
                if len(set(actions).difference(set(SHIFT_ACTIONS))) > 0:
                    self.parser_logger.error("Invalid action(s) %s for 'actions'" % (str(actions)))
                    raise ParseException("One or more acitons in %s are invalid" % (actions))
            return new_hours
        except KeyError:
            self.parser_logger.error("Missing paramater 'hours' in %s" % (self.filepath))
            raise ParseException("'hours' argument is missing from %s" % (self.filepath))

    def is_valid_dates(self):
        '''provided settings dict, make sure each date is well formatted 
        '''
        self.check_loaded()

        self.parser_logger.info("Validating dates")
        try:
            dates = self.get_dict()["dates"]
            new_dates = deepcopy(dates)
            for date_key, date in dates.iteritems():
                new_dates[date_key]["range"] = self.is_valid_date_range(date_key)
                for weekday_key, weekday in date.iteritems():
                    self.parser_logger.info("--Validating Weekday")
                    weekday_key = str(weekday_key)
                    if weekday_key not in WEEKDAYS and weekday_key not in WEEKDAYS_INITIALS and weekday_key != "all":
                        self.parser_logger.error("Invalid weekday %s" % (weekday_key))
                        raise ParseException("weekday %s is not valid" % (weekday_key))
                    new_dates[date_key][weekday_key] = self.is_valid_weekday(weekday)
            self.input_dict["dates"] = new_dates
        except KeyError, e:
            self.parser_logger.error("Missing paramater 'dates' in %s" % (self.filepath))
            raise ParseException("No 'dates' paramater set in " + self.filepath)


class Init_Parser(File_Parser):
    '''
    Init_Parser just checks advanced_logging to determine for the real
    parsers if they should use advanced_loggin
    '''
    def validate(self, filepath=PATH_TO_DEFAULT_SETTINGS_FILE):
        '''
        Just check to make sure 'logging' is correct. NO INTERNAL LOGGING
        '''
        self.load(filepath)

        try:
            logging = self.get_dict()["advanced_logging"]

            if not isinstance(logging, bool):
                self.parser_logger.error("Invalid type %s for 'logging'" % (type(logging)))
                raise TypeError("'logging' needs to be a bool in %s" % (self.filepath))
        except KeyError, e:
            self.parser_logger.warning("'logging' paramater not set, defaulting to false")
            self.get_dict()["advanced_logging"] = False

        return self.get_dict()["advanced_logging"]
