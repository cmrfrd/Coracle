from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from string import printable
import time
from os.path import dirname, realpath, join

import logging
import logging.config

from constants import *
from parse.ITS_message_parsers import *
from coracle_exceptions import SessionException

current_filepath = dirname(realpath(__file__))

logging.config.fileConfig(join(current_filepath, PATH_TO_DEFAULT_LOGGING_FILE))

class ITSdriver(webdriver.PhantomJS):
    '''
    Special sublass of phantomjs for ease of use when interacting
    with the ITS site. 
    '''
    def __init__(self, advanced_logging=False, *args, **kwargs):
        super(ITSdriver, self).__init__(*args, **kwargs)
        self.session_start = False
        self.current_location = None

        self.ITSdriver_logger = logging.getLogger("ITSdriver")
        self.simple_logger = logging.getLogger("simple_log")

        if advanced_logging:
            self.simple_logger.handlers = [h for h in self.simple_logger.handlers if type(h) != logging.StreamHandler]
        else:
            self.ITSdriver_logger.handlers = [h for h in self.ITSdriver_logger.handlers if type(h) != logging.StreamHandler]

        self.ITSdriver_logger.info("%s object initialized" % (self.__class__))

    def init_session(self):
        '''given the albany url, initialize your session and flag it
        '''
        self.get(ITS_URL)
        self.session_start = True
        self.ITSdriver_logger.info("ITS punchcard session initialized")

    def is_started(self):
        '''Given a session_start flag, check it to be true
        '''
        return self.session_start == True

    def check_started(self):
        '''Given a session_start flag, raise error if false
        '''
        if not self.is_started():
            self.ITSdriver_logger.info("ITS punchcard session not initialized")
            raise SessionException("ITS session not started")

    def loaded(self):
        '''On the ITS website, wait and check if the header is loaded, raise exception if fail
        '''
        try:
            WebDriverWait(self, 5).until(
                EC.presence_of_element_located((By.ID, "its_logo"))
                )
            return True
        except TimeoutException:
            raise SessionException("location not loading in time. Check connectivity")

    def go_to_location(self, location):
        '''Provided a location, check that location and 'get' it with phantomjs
        '''
        if self.location_exists(location):
            ITS_LOCATION_MAP_INVERT = {v: k for k, v in ITS_LOCATION_MAP.items()}
            self.get(ITS_LOCATION_MAP_INVERT[location])
            self.ITSdriver_logger.info("Going to location: %s" % (location))
            self.loaded()
        else:
            self.ITSdriver_logger.error("Location %s not found" % (location))
            raise SessionException("Unknown location %s" % (location))

    def at_location(self, location):
        '''Given a driver is at a location, be sure its in an existing location
        '''
        return self.location_exists(location) and self.check_location(location)

    def location_exists(self, location):
        '''Provided a location, check that location exists
        '''
        return location in ITS_LOCATION_MAP.values()

    def check_location(self, location):
        '''Given the hashmap "ITS_LOCATION_MAP" and a location, check the location
        '''
        try:
            return ITS_LOCATION_MAP[self.current_url] == location
        except KeyError:
            self.ITSdriver_logger.error("ITSdriver in unknown location %s" % (location))
            raise SessionException("ITSdriver is at an unknown url location %s. Re-init session" % (self.current_url))

    def login(self, username, password):
        '''provided a username and a password, wait till loaded and login to the ITS website
        '''
        self.simple_logger.info("LOGGING INTO ITS PUNCHCARD")
        self.ITSdriver_logger.info("ITSdriver logging in to ITS punchcard")
        
        self.init_session()
        self.check_started()
        if not self.at_location("login"):
            return False

        try:
            login_form = WebDriverWait(self, 10).until(
                EC.presence_of_element_located((By.ID, "loginForm"))
                )

            login_form.find_element_by_id("user").send_keys(username)
            login_form.find_element_by_id("pass").send_keys(password)
            login_form.find_elements_by_tag_name("input")[-1].click()
            self.save_screenshot("test.png")
            self.loaded()
            self.ITSdriver_logger.info("Login Session Initialized")

        except Exception, e:
            self.simple_logger.error("UNABLE TO LOG IN GIVEN CREDENTIALS")
            self.ITSdriver_logger.error("Unable to log in via ITSdriver")
            raise SessionException("Unable to log in to ITS website")

    def get_user_shifts(self):
        '''
        Given driver is at a location home, iterate through 'My Shifts' and extract
        the type, actions, location, and time information into a list of dicts and 
        return
        '''
        self.ITSdriver_logger.info("Getting user shifts from 'home'")

        self.check_started()
        self.go_to_location("home")
        if not self.at_location("home"):
            return False

        shift_box = WebDriverWait(self, 10).until(
            EC.presence_of_element_located((By.ID, "index_my_shifts"))
            )
        self.ITSdriver_logger.info("Found shift_box from 'home', %d shifts found" % (len(shift_box.find_elements_by_class_name("index_perm_shift"))))

        shifts = []
        for shift in shift_box.find_elements_by_class_name("index_perm_shift"):
            day_time_str = shift.textContent
            shift_info_str = shift.find_element_by_tag_name("p").textContent

            info_tuple = get_info_from_shift_bloack(day_time_str, shift_info_str)
            start_date, end_date, weekday, start_time, end_time, shift_type, location, actions = info_tuple

            shift_block_info = {}
            
            shift_block_info["start_date"] = start_date
            shift_block_info["end_date"] = end_date
            shift_block_info["weekday"] = weekday
            shift_block_info["start_time"] = start_time
            shift_block_info["end_time"] = end_time

            shift_block_info["location"] = location
            shift_block_info["type"] = shift_type
            shift_block_info["actions"] = actions

            shifts.append(shift_block_info)

        self.ITSdriver_logger.info("%d shifts analyzed and returned" % (len(shifts)))
        return shifts

    def navigate_calander(self, date):
        '''
        Given a driver is on the schedule page, navigate the calander based on a datetime
        '''
        self.check_started()
        self.go_to_location("schedule")
        self.check_started()
        if not self.at_location("schedule"):
            return False

        self.simple_logger.info("NAVIGATING TO %s" % (date.strftime("%d-%b")))
        self.ITSdriver_logger.info("Navigating ITS calendar to: %s" % (date.strftime("%d-%b-%Y")))
        calendar = WebDriverWait(self, 5).until(
            EC.presence_of_element_located((By.ID, "right_menu"))
            )
        
        long_navigations = calendar.find_element_by_tag_name("h4").find_elements_by_tag_name("a")
        back_one_month, forward_one_month, go_to_today = long_navigations

        selected_month, selected_year = filter(lambda x:x in set(printable), calendar.find_element_by_tag_name("h4").text).split()[:2]
        selected_day = calendar.find_element_by_class_name("highlighted").text
        selected_date_str = "%s-%s-%s" % (selected_month, selected_day, selected_year)
        selected_date = datetime.datetime.strptime(selected_date_str, "%B-%d-%Y")
        self.ITSdriver_logger.info("Selected date: %s" % (selected_date_str))
        
        month_diff = selected_date.month - date.month
        self.ITSdriver_logger.info("Moving %d months" % (month_diff))

        for month_move in range(abs(month_diff)):
            WebDriverWait(self, 5).until(
                EC.presence_of_element_located((By.ID, "right_menu"))
                )
            if month_diff < 0:
                back_one_month.click()
            elif month_diff > 0:
                forward_one_month.click()

        days_elements = WebDriverWait(self, 5).until(
            EC.presence_of_element_located((By.ID, "right_menu"))
            ).find_element_by_tag_name("tbody")
        days_elements = days_elements.find_elements_by_tag_name("tr")[1:]

        days_elements_td = []
        for days in days_elements:
            days_elements_td.extend(days.find_elements_by_tag_name("td"))

        days_links = []
        for days in days_elements_td:
            link_class = days.get_attribute("class")
            if (link_class != "prevMonth") or (link_class != "nextMonth"):
                days_links.extend(days.find_elements_by_tag_name("a"))

        self.ITSdriver_logger.info("Selecting day %d" % (date.day))

        filter(lambda d:str(d.text) == str(date.day), days_links)[0].click()

        calendar = WebDriverWait(self, 5).until(
            EC.presence_of_element_located((By.ID, "right_menu"))
            )
        selected_month, selected_year = filter(lambda x:x in set(printable), calendar.find_element_by_tag_name("h4").text).split()[:2]
        selected_day = calendar.find_element_by_class_name("highlighted").text
        selected_date_str = "%s-%s-%s" % (selected_month, selected_day, selected_year)
        selected_date = datetime.datetime.strptime(selected_date_str, "%B-%d-%Y")
        self.ITSdriver_logger.info("Selected date: %s" % (selected_date_str))

    def grab_shift(self, shift):
        '''
        Given that an option is selected for a particular shift. Confirm the shift
        '''
        self.check_started()

        if self.select_shift(shift):
            if not self.at_location("schedule"):
                self.ITSdriver_logger.error("ITSdriver not at location schedule to grab shift")
                return False

            shifts = WebDriverWait(self, 5).until(
                EC.presence_of_element_located((By.ID, "shifts_by_day"))
                )

            submit_button = self.find_element_by_tag_name("input").click()

            if not self.at_location("confirm"):
                self.ITSdriver_logger.error("ITSdriver not at location confirm to grab shift")
                return False

            confirm_form = WebDriverWait(self, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
            confirm_form.submit()
            
            if not self.at_location("schedule"):
                self.ITSdriver_logger.warning("ITSdriver not at location schedule to grab shift")
                return False
            else:
                self.ITSdriver_logger.info("Shift Successfully grabbed")
                return True
        else:
            self.simple_logger.warning("UNABLE TO GRAB SHIFT")
            self.ITSdriver_logger.warning("Unable to grab shift because unable to select: %s %s %s" % (shift["actions"], shift["user"], shift["start_time"]))
            return False

    def select_shift(self, shift):
        '''
        Provided a shift, based on the settings of the shift, perform
        an action on the shift

        shift needs a locations, time slot, and action 
        '''
        self.simple_logger.info("GRABBING NEW %s SHIFT" % (shift["actions"]))
        self.ITSdriver_logger.info("Grabbing new shift: %s %s %s" % (shift["actions"], shift["user"], shift["start_time"]))

        self.check_started()
        self.go_to_location("schedule")
        if not self.at_location("schedule"):
            return False

        self.ITSdriver_logger.info("Navigating calendar to %s" % (shift["start_date"]))
        self.navigate_calander(shift["start_date"])

        self.ITSdriver_logger.info("Checking prescence of shift")
        menu_schedule = WebDriverWait(self, 5).until(
            EC.presence_of_element_located((By.ID, "shifts_by_day"))
            )

        shifts_schedule = menu_schedule.find_element_by_tag_name("tbody")
        shifts_blocks = shifts_schedule.find_elements_by_tag_name("tr")[1]

        for location_index in [LOCATIONS.index(i) for i in shift["locations"]]:
            location_shifts = shifts_blocks.find_elements_by_tag_name("td")[1+location_index]
            
            schedule_block_divs = []
            for block in location_shifts.find_elements_by_tag_name("div")[1::2]:
                inner_div = block.find_elements_by_tag_name("div")[0]
                schedule_block_divs.append(inner_div)

            for block in schedule_block_divs:
                start_time, end_time, start_date, end_date = get_info_from_schedule_block(block.text)
                time_check_start = (start_time <= shift["start_time"] <= end_time)
                time_check_end = (start_time <= shift["end_time"] <= end_time)

                date_check_start = (start_date <= shift["start_date"] <= end_date)
                date_check_end = (start_date <= shift["end_date"] <= end_date)

                if time_check_start and time_check_end and date_check_start and date_check_end:
                    try:
                        options = block.find_element_by_tag_name("select")
                        for option in options.find_elements_by_tag_name("option"):
                            norm_option = option.text.lower().replace(" ","")
                            norm_action = shift["action"].lower().replace(" ","")
                            if norm_option == norm_action:
                                option.click()
                                return True
                        else:
                            self.ITSdriver_logger.warning("Action %s cannot be performed on shift. Action not available" % (shift["action"]))
                            self.simple_logger.debug("%s ACTION NOT AVAILABLE FOR SHIFT" % (shift["action"]))
                            return False
                    except NoSuchElementException:
                        self.ITSdriver_logger.warning("No actions can be performed on shift. Shift is taken")
                        self.simple_logger.warning("SHIFT ALREADY TAKEN")
                        return False
                else:
                    pass#wrong shift, on to the next
        self.ITSdriver_logger.warning("Unable to locate shift for %s" % (shift["start_time"]))
        self.simple_logger.warning("Unable to select shift")
        return False


if __name__ == "__main__":
    d = ITSdriver(True, service_args=PHANTOMJS_SERVICE_ARGS)

    shift = {
                'end_date': datetime.datetime(1900, 10, 7, 0, 0), 
                'start_time': datetime.datetime(1900, 1, 1, 14, 0), 
                'locations': ["SciLib"], 
                'actions': ['TempTake'], 
                'action':"TempTake",
                'end_time': datetime.datetime(1900, 1, 1, 15, 0), 
                'weekday': datetime.datetime(1900, 1, 1, 0, 0), 
                'type': 'TempShift', 
                'start_date': datetime.datetime(1900, 10, 7, 0, 0), 
                'user': ['Adam', 'Mrowca']
            }
    
    d.login("", "") # can't leave username and password in the repo 
    d.grab_shift(shift)
