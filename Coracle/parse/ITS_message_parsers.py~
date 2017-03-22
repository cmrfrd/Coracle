import datetime
from string import printable

from constants import *

norm = lambda s:filter(lambda i:i in set(printable),str(s)).lower().replace(" ", "")
normeq = lambda x, y: norm(x) == norm(y)

def get_info_from_schedule_block(info):
    '''provided a string of 'info' return the relevant information
    '''
    time_range_str, date_range_str = info.split('\n')[:2]
    
    start_time, end_time = get_time_range(time_range_str)
    start_date, end_date = get_date_range(date_range_str)

    return start_time, end_time, start_date, end_date

def get_time_range(time_str):
    '''Provided a time_str, return a time range
    '''
    time_str = time_str.replace(" ","")
    start, end = time_str.split("-")
    
    start_time = datetime.datetime.strptime(start, "%I:%M%p")
    end_time = datetime.datetime.strptime(end, "%I:%M%p")

    return start_time, end_time

def get_date_range(date_str):
    '''Provided a date_str, return a date range
    '''
    date_str = date_str.replace(" ","")
    start, end = date_str.split("-") if "-" in date_str else [date_str, date_str]

    start_date = datetime.datetime.strptime(start, "%m/%d")
    end_date = datetime.datetime.strptime(end, "%m/%d")

    return start_date, end_date

def which_semester(date):
    '''Provided a datetime, check which semester it is and return 'fall' or 'spring'
    '''
    fall_start_str = FALL_SEMESTER_DATE_RANGE.split("-")[0].strip()
    fall_end_str = FALL_SEMESTER_DATE_RANGE.split("-")[1].strip()

    fall_start = datetime.datetime.strptime(fall_start_str, "%m/%d/%Y")
    fall_end = datetime.datetime.strptime(fall_end_str, "%m/%d/%Y")

    spring_start_str = SPRING_SEMESTER_DATE_RANGE.split("-")[0].strip()
    spring_end_str = SPRING_SEMESTER_DATE_RANGE.split("-")[1].strip()

    spring_start = datetime.datetime.strptime(spring_start_str, "%m/%d/%Y")
    spring_end = datetime.datetime.strptime(spring_end_str, "%m/%d/%Y")


    if fall_start <= date <= fall_end:
        return "fall", fall_start, fall_end
    elif spring_start <= date <= spring_end:
        return "spring", spring_start, spring_end
    else:
        return False, False, False

#these 3 functions are mean to parse shift blocks
def get_info_from_shift_block(day_time_str, shift_info_str):
    '''provided 2 strings with the shift information, extract the info
    '''
    weekday, start_time, end_time = get_day_time_from_string(day_time_str)
    start_date, end_date, location, shift_type, actions = get_time_range_from_shift_info(shift_info_str)

    return start_date, end_date, weekday, start_time, end_time, shift_type, location, actions

def get_day_time_from_string(day_time_str):
    '''provided a string with the weekday and the shift time, extract that info into datetime
    '''
    weekday_str = day_time_str.split()[0]

    time_range_str = "".join(day_time_str.split()[1:])
    start_time_str = time_range_str.split("-")[0].strip()
    end_time_str = time_range_str.split("-")[1].strip()

    weekday = datetime.datetime.strptime(weekday_str.strip(), "%A")
    start_time = datetime.datetime.strptime(start_time_str.strip(), "%I:%M %p")
    end_time = datetime.datetime.strptime(end_time_str.strip(), "%I:%M %p")

    return weekday, start_time, end_time

def get_time_range_from_shift_info(shift_info_str):
    '''provided a string with the shift info, extract the into and return
    '''
    shift_identifier = shift_info_str.split()[0].lower()

    if shift_identifier.lower() == "temp":
        start_date_str, end_date_str = "".join(shift_info_str.split()[3:6]).split("to")
        start_date = datetime.datetime.strptime(start_date_str.strip(), "%m/%d")
        end_date = datetime.datetime.strptime(end_date_str.strip(), "%m/%d")
        
        location = "".join(shift_info_str.split()[-1]).strip().replace(".","")
        shift_type = SHIFT_TYPES[0]
        actions = ["TempDrop"]

    elif shift_identifier.lower() == "shift":
        start_end_date_str = "".join(shift_info_str.split()[-3])
        
        start_date = datetime.datetime.strptime(start_end_date_str.strip(), "%m/%d")
        end_date = datetime.datetime.strptime(start_end_date_str.strip(), "%m/%d")

        location = "".join(shift_info_str.split()[-1]).strip().replace(".","")
        shift_type = SHIFT_TYPES[1]
        actions = ["PermDrop", "TempDrop"]

    else:
        raise ParseException("Unable to parse shift block:\n%s" % (shift_info_str))        

    return start_date, end_date, location, shift_type, actions


#These three functions are hand written to parse ITS emails
def get_time_range_from_email(ITS_email):
    '''provided an str email, return a start, end, weekday, timerange all in datetime format
    '''
    action = get_shift_status_from_email(ITS_email)
    time_line = "-".join(ITS_email.split('\n')[2].split("-")[1:]).replace(" ","")

    if action in SHIFT_ACTIONS_MAP["Temp"]:
        date, time_start_str, time_end_str = time_line.split("-")
        weekday, date = date.strip().split(",")
        
        start_end_weekday = datetime.datetime.strptime(weekday.strip(), "%A")
        start_end_date = datetime.datetime.strptime(date.strip(), "%m/%d")

        start_time = datetime.datetime.strptime(time_start_str.strip(), "%I:%M%p")
        end_time = datetime.datetime.strptime(time_end_str.strip(), "%I:%M%p")

        shift_type = SHIFT_TYPES[0]
        actions = ["TempTake"] if action in SHIFT_ACTIONS_MAP["Drop"] else []

        return start_end_date, start_end_date, start_end_weekday, start_time, end_time, shift_type, actions

    elif action in SHIFT_ACTIONS_MAP["Perm"]:
        day_str, date_time_str = time_line.split(",")
        dates_str = "-".join(date_time_str.split("-")[:2])
        time_str = "-".join(date_time_str.split("-")[2:])
        start_end_weekday = datetime.datetime.strptime(day_str.strip(), "%A")

        start_date_str, end_date_str = dates_str.strip().split("-")
        start_date = datetime.datetime.strptime(start_date_str.strip(), "%m/%d")
        end_date = datetime.datetime.strptime(end_date_str.strip(), "%m/%d")

        time_start_str, time_end_str = time_str.split("-")
        start_time = datetime.datetime.strptime(time_start_str.strip(), "%I:%M%p")
        end_time = datetime.datetime.strptime(time_end_str.strip(), "%I:%M%p")

        shift_type = SHIFT_TYPES[0]
        actions = ["PermTake"] if action in SHIFT_ACTIONS_MAP["Drop"] else []

        return start_date, end_date, start_end_weekday, start_time, end_time, shift_type, actions
    else:
        raise ParseException("Unable to parse email:\n%s" % (ITS_email))

def get_person_from_email(ITS_email):
    '''provided an email, get the person who performed the action
    '''
    return ITS_email.split('\n')[0].split()[3:]

def get_shift_status_from_email(ITS_email):
    '''provided an email, get the status of the shift
    '''
    return "".join(ITS_email.split('\n')[2].split()[:2]).replace(" ","")
