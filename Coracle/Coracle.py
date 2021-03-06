from selenium import webdriver
from time import time, sleep
import argparse

import imaplib
from imaplib import IMAP4
import email
import email.mime.multipart
import smtplib
import datetime
from os.path import abspath, dirname, realpath, join

import logging
import logging.config

from constants import *
from parse import Settings_Parser, Credentials_Parser, Init_Parser
from outlookclient import outlookclient
from ITSdriver import ITSdriver

current_filepath = dirname(realpath(__file__))

logging.config.fileConfig(join(current_filepath, PATH_TO_DEFAULT_LOGGING_FILE))

class Coracle(object):
	'''
	coracle holds a phantomjs webdriver and an outlook webdriver
	utilized in conjunction with eachother to automate the ITS 
	shift system
	'''

	def __init__(self):
		self.i_parser = Init_Parser()
		self.s_parser = None
		self.c_parser = None

		self.advanced_logging = None

		self.outlookcl = None
		self.ITSdr = None

		self.coracle_logger = logging.getLogger("Coracle")
		self.simple_logger = logging.getLogger("simple_log")

	def dict_configure(self, **config):
		'''Provided a dictionary, load 
		'''
		self.set_logging(config["settings_filepath"])
		self.load_settings(config["settings_filepath"])
		self.load_credentials(config["credentials_filepath"])
		self.validate()

	def load_settings(self, filepath=None):
		'''provided a filepath, load it into settings parser
		'''
		self.coracle_logger.info("Loading settings and initializing Settings Parser")
		self.s_parser = Settings_Parser(
			filepath=filepath, 
			advanced_logging=self.advanced_logging
			)

	def load_credentials(self, filepath=None):
		'''provided a filepath, load it into credentials parser
		'''
		self.coracle_logger.info("Loading credentials and initializing credentials Parser")
		self.c_parser = Credentials_Parser(
			filepath=filepath, 
			advanced_logging=self.advanced_logging
			)
		
	def validate(self):
		'''Provided the 2 main parsers, Validate both parsers
		'''
		self.coracle_logger.info("Validating Settings and Credentials by parsers")
		self.s_parser.validate()
		self.c_parser.validate()

	def set_logging(self, filepath=None):
		'''Sets the logging handlers from settings, for advanced/simple logging
		'''
		if not filepath:
			self.advanced_logging = self.i_parser.validate(filepath)
		else:
			self.advanced_logging = self.i_parser.validate()

		if self.advanced_logging:
			self.simple_logger.handlers = [h for h in self.simple_logger.handlers if type(h) != logging.StreamHandler]
		else:
			self.coracle_logger.handlers = [h for h in self.coracle_logger.handlers if type(h) != logging.StreamHandler]

		self.coracle_logger.info("Logging initialization test")
		self.simple_logger.info("LOGGING INITIALIZATION TEST")

	def init_clients(self, adv_log=None):
		'''Provided or given advanced logging, init both clients for coracle
		'''
		self.coracle_logger.info("Initializing outlookclient and ITSdriver")
		self.outlookcl = outlookclient(self.advanced_logging)
		self.ITSdr = ITSdriver(self.advanced_logging)

	def run(self, **Config):
		'''TIME TO RUN
		'''
		settings = self.s_parser.get_dict()
		credentials = self.c_parser.get_dict()

		self.init_clients()

		starttime = time()
		is_active = lambda: (time() - starttime) < settings["active"]
		is_in_range = lambda i,r:r[0] <= i <= r[1] if len(r)==2 else True

		while is_active():
			for ITS_email in self.outlookcl.get_ITS_email_info(True):
				# if email is within date range
				for date_key, date in settings["dates"].iteritems():
					if is_in_range(ITS_email["start_date"], date["range"]) and is_in_range(ITS_email["end_date"], date["range"]):
						for weekday_key, weekday in date.iteritems():
							if ITS_email["weekday"] in WEEKDAYS or ITS_email["weekday"] in WEEKDAYS_INITIALS or ITS_email["weekday"] == "all":
								for hour, actions in weekday["hours"].iteritems():
									if "_range" in hour:continue
									if is_in_range(ITS_email["start_time"], weekday[hour+"_range"]) and is_in_range(ITS_email["end_time"], weekday[hour+"_range"]):
										self.ITSdriver.grab_shift(ITS_email)
							else:
								continue
					else:
						continue
			sleep(settings["refresh"])
