import Coracle
from Coracle.constants import *
import argparse

parser = argparse.ArgumentParser(description='Perform Coracle')

parser.add_argument('-s', action="store", dest="settings_filepath", default=PATH_TO_DEFAULT_SETTINGS_FILE, help='path for settings configuration')
parser.add_argument('-c', action="store", dest="credentials_filepath", default=PATH_TO_DEFAULT_CREDENTIALS_FILE, help='path for credentials configuration')

args = parser.parse_args()
kwargs = dict(args._get_kwargs())

c = Coracle.Coracle()
c.dict_configure(**kwargs)
c.run()
