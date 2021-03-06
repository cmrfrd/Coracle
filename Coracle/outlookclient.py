import imaplib
import email
import smtplib
import datetime
from os.path import abspath, dirname, realpath, join
import email.mime.multipart

import logging
import logging.config

from itertools import islice

from constants import *
from parse.ITS_message_parsers import *
from coracle_exceptions import ParseException

current_filepath = dirname(realpath(__file__))

logging.config.fileConfig(join(current_filepath, PATH_TO_DEFAULT_LOGGING_FILE))

class outlookclient(object):
    '''
    outlook client grabs email from ITS, and parsers through the email for specific information.
    '''

    def __init__(self, advanced_logging=False):
        self.is_login = False

        self.today = (datetime.datetime.now()-datetime.timedelta(1)).strftime("%d-%b-%Y")
        self.imap = None

        self.outlookclient_logger = logging.getLogger("outlookclient")
        self.simple_logger = logging.getLogger("simple_log")
        
        current_semester, start, end = which_semester(datetime.datetime.today())
        self.current_semester = current_semester
        self.start_semester = start
        self.end_semester = end

        current_year = datetime.datetime.today().year
        self.start_semester.replace(year=current_year)
        self.end_semester.replace(year=current_year)

        if advanced_logging:
            self.simple_logger.handlers = [h for h in self.simple_logger.handlers if type(h) != logging.StreamHandler]
        else:
            self.outlookclient_logger.handlers = [h for h in self.outlookclient_logger.handlers if type(h) != logging.StreamHandler]

        self.outlookclient_logger.info("%s object initialized" % (self.__class__))

    def init_IMAP(self):
        '''Given self.imap, initialize imap ssl with the specific constant hostname
        '''
        self.outlookclient_logger.info("Initializing imap client")
        try:
            self.imap = imaplib.IMAP4_SSL(IMAP4_OUTLOOK_HOST)
        except KeyboardInterrupt, e:
            self.outlookclient_logger.error("Keyboard Interrupt, Stopping program")
            raise e
        except Exception, e:
            self.outlookclient_logger.error("Unable to initialize imap client")
            raise e

    def login(self, username, password, attempts=3):
        '''
        When provided a username and a password, login to outlook
        webmail with the username and password using imap. If error
        try again. If failed login, break and return false
        '''
        if not self.is_login:
            self.init_IMAP()

        self.outlookclient_logger.info("Attempting login with username and password in config file")
        for attempt in range(1, attempts+1):
            self.outlookclient_logger.info("Attempting login #%d." % (attempt))
            try:
                success, response = self.imap.login(username, password)            
                if success != "OK":
                    raise imaplib.IMAP4.abort("Login failed.\nInvalid Username: %s or invalid Password: %s" % (username, password))

                self.outlookclient_logger.info("Login Success to outlook.office365.com")
                self.simple_logger.info("LOGIN SUCCESS")
                self.is_login = True
                break
            
            except imaplib.IMAP4.abort, e:
                self.outlookclient_logger.error("Recieved not okay response.")
                self.outlookclient_logger.error("Unable to login with username and password provided by user")
                self.simple_logger.error("UNABLE TO LOGIN WITH USERNAME AND PASSWORD")
                self.is_login = False
                break

            except Exception, e:
                self.outlookclient_logger.error("Attempt #%d, login failure: %s" % (attempt, e))
                self.simple_logger.error("LOGIN FAILURE")
                self.is_login = False
        
        return self.is_login

    def select(self, select_str):
        '''Provided a string, select that folder with imap
        '''
        if not self.is_login:
            self.outlookclient_logger.error("Attempting select without login. NO RESPONSE")
            self.simple_logger.error("MUST LOGIN FIRST BEFORE ACTING")
            return 

        self.outlookclient_logger.info("Attempting select %s" % (select_str))
        return self.imap.select(select_str)

    def get_ITS_email_ids(self, unseen=False):
        '''
        given an imap, and provided an unseen flag, return all or unseen 
        emails from ITS from the current semester.
        '''
        if not self.is_login:
            self.outlookclient_logger.error("Attempting to get IDS without login. NO RESPONSE")
            self.simple_logger.error("MUST LOGIN FIRST BEFORE ACTING")
            return

        self.select("Notes")

        search_args = [None]
        
        search_args.append("UNSEEN") if unseen else search_args.append("ALL")
        
        search_args.append("FROM")
        search_args.append(ITS_EMAIL)

        since = datetime.datetime.strftime(self.start_semester, "%d-%b-%Y")
        search_args.append("SINCE")
        search_args.append(since)

        before = datetime.datetime.strftime(self.end_semester, "%d-%b-%Y")
        search_args.append("BEFORE")
        search_args.append(before)

        self.outlookclient_logger.info("Submitting IMAP search query %s" % (str(search_args)))
        try:
            success, response = self.imap.search(*search_args)
            if success != "OK":
                self.outlookclient_logger.error("Unsuccessful response. Throwing IMAP4 abort")
                raise imaplib.IMAP4.abort("Invalid search")
            return response[0].split()[::-1]
        except imaplib.IMAP4.abort, e:
            self.outlookclient_logger.error("Search failed, exception caught, rethrowing IMAP4 abort")
            raise e            

    def is_authentic_email(self, select_email):
        '''
        Provided an email, return bool based on email being from ITS and containing
        the correct information. Correct type, payload is a single message, source
        is from ITS, and content contains 'Visit Punchcard'
        '''
        authentic = True

        authentic &= (select_email.__module__ == email.message.__name__)
        authentic &= (isinstance(select_email.get_payload(), str))
        authentic &= ("Visit PunchCard" in select_email.get_payload())
        authentic &= (select_email.get("From") == "<%s>" % (ITS_EMAIL))

        return authentic

    def get_date_from_email(self, email):
        '''Provided an email return a datetime of when it was ecieved
        '''
        date = email["date"]
        return datetime.datetime.strptime(date.strip(), "%a, %d %b %Y %H:%M:%S")

    def get_info_from_emails(self, emails):
        '''
        Provided a list of emails, authenticate the email, if email is invalid, skip
        then generate info from status, user, and shift information and yield
        '''
        self.outlookclient_logger.info("Iterating through emails for authenticity, and information")

        authentic_emails = 0
        non_authentic_emails = 0

        for select_email in emails:
            if not self.is_authentic_email(select_email):
                non_authentic_emails += 1
                continue

            email_info = {}
            email_info["user"] = get_person_from_email(select_email.get_payload())

            start_date, end_date, weekday, start_time, end_time, shift_type, actions = get_time_range_from_email(select_email.get_payload())

            email_info["type"] = shift_type
            email_info["actions"] = actions
            email_info["start_date"] = start_date
            email_info["end_date"] = end_date
            email_info["weekday"] = weekday
            email_info["start_time"] = start_time
            email_info["end_time"] = end_time

            email_info["location"] = "" #location is not provided in email

            authentic_emails += 1
            yield email_info
        self.outlookclient_logger.info("Finish iterating through emails. Authentic: %d, Non Authentic: %d" % (authentic_emails, non_authentic_emails))

    def iter_emails_from_ids(self, ids, num_emails):
        '''Provided a list of ids, yield the emails using imap.fetch
        '''
        if not self.is_login:
            self.outlookclient_logger.error("Attempting to get email from ids without login. Must login to proceed")
            self.simple_logger.error("MUST LOGIN FIRST BEFORE ACTING")
            return 
        
        ids = ids[:num_emails]
        self.outlookclient_logger.info("Reduced ids to %d id(s)" % (len(ids)))
        
        try:
            success, response = self.imap.fetch(",".join(ids), "(RFC822)")
            if success != "OK":
                self.outlookclient_logger.error("Unable to complete fetch. %s" % (response))
                raise imaplib.IMAP4.abort("Fetch came back with %s success response" % (success))
            
            self.outlookclient_logger.info("Fetching success, yielding %d emails" % (len(ids)))
            for email_index in range(0, len(response), 2):
                yield email.message_from_string(response[email_index][1])
        except imaplib.IMAP4.abort, e:
            self.outlookclient_logger.error("Unable to get emails from imap. %s")
            raise e
        
    def get_ITS_email_info(self, unseen_flag=False, num_emails=-1):
        '''
        MAIN FUNCTION
        Given/Provided an unseen bool flag, return the info dict from the 
        correct authenticated emails from ITS indicating shift actions.
        '''
        if not self.is_login:
            self.outlookclient_logger.error("Attempting to get email info without login. Must login to proceed")
            self.simple_logger.error("MUST LOGIN FIRST BEFORE ACTING")
            return 

        self.simple_logger.info("GETTING EMAIL INFO")
        self.outlookclient_logger.info("Getting ITS email ids")
        ITS_email_ids = self.get_ITS_email_ids(unseen_flag)

        self.outlookclient_logger.info("%d ids retrieved" % (len(ITS_email_ids)))        
        if num_emails == -1:
            num_emails = len(ITS_email_ids)
            
        self.outlookclient_logger.info("Creating iter for %d emails from %d ITS email ids" % (num_emails, len(ITS_email_ids)))
        ITS_emails = self.iter_emails_from_ids(ITS_email_ids, num_emails)

        self.outlookclient_logger.info("Yielding info from ITS email iterator")
        for ITS_email in self.get_info_from_emails(ITS_emails):
            yield ITS_email
            


if __name__ == "__main__":
     o = outlookclient(True)

     o.login("", "")

     o.select("Inbox")
     #for email_dict in o.get_ITS_email_info(num_emails=10):
     #    print email_dict
     #    print email_dict["user"], email_dict["start_date"], email_dict["start_time"], email_dict["type"]

     
     try:
         success, response = o.imap.search(None, "(All)")
         if success != "OK":
                 raise imaplib.IMAP4.abort("Invalid search")
         print response[0].split()[::-1]
     except imaplib.IMAP4.abort, e:
         raise e            
             
