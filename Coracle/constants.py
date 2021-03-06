ITS_URL = "https://snowball.itsli.albany.edu/punchcard/ut/"
ITS_EMAIL = "atat@ALBANY.EDU"
LOCATIONS = ["LC-27a", "LC-27b", "LI-Circ", "LI-106", "SciLib"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
WEEKDAYS_INITIALS = ["M", "Tu", "W", "Th", "F"]
SHIFT_TYPES = ["TempShift", "PermShift"]
SHIFT_ACTIONS = ["TempTake", "TempDrop", "PermTake", "PermDrop"]
SHIFT_ACTIONS_MAP = {
    "Temp":["TempTake", "TempDrop"],
    "Perm":["PermTake", "PermDrop"],
    "Take":["TempTake", "PermTake"],
    "Drop":["TempDrop", "PermDrop"]
}
ITS_LOCATION_MAP = {
    "https://snowball.itsli.albany.edu/punchcard/ut/":"login", 
    "https://snowball.itsli.albany.edu/punchcard/ut/index.php":"home", 
    "https://snowball.itsli.albany.edu/punchcard/ut/show_shifts.php":"schedule",
    "https://snowball.itsli.albany.edu/punchcard/ut/shift_confirm.php":"confirm"
}

FALL_SEMESTER_DATE_RANGE = "8/10/2010 - 12/10/3005" #No matter what you say or what you do
SPRING_SEMESTER_DATE_RANGE = "1/10/1900 - 5/10/3005"

PHANTOMJS_SERVICE_ARGS = ['--ignore-ssl-errors=true', '--ssl-protocol=any'] #For depreciated versions of phantomjs that do not utilize ssl

#All paths are relative to files in the parse dir for referencing
PATH_TO_DEFAULT_SETTINGS_FILE = "../../settings/settings.json"
PATH_TO_DEFAULT_CREDENTIALS_FILE = "../../settings/creds.json"

#paths relative to inside coracle
PATH_TO_DEFAULT_LOGGING_FILE = "./log/logging.ini"
PATH_TO_DEFAULT_HISTORY_DIR = "./history"

IMAP4_OUTLOOK_HOST = 'outlook.office365.com'
