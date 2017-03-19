import json
import datetime
from copy import deepcopy

import logging
import logging.config

from constants import *
from parse.ITS_message_parsers import *
from coracle_exceptions import ParseException

current_filepath = dirname(realpath(__file__))

logging.config.fileConfig(join(current_filepath, PATH_TO_DEFAULT_LOGGING_FILE))

class History_Manager(object):
    '''
    History_Manager manages a json file containing all the history information.

    Stores all history information into a json. Format as follows

    [{shift_info}, ...]
    '''

    def __init__(self, *args, **kwargs):
        self._file = open(mode="rw+", *args, **kwargs)
        self._history = []

        self.historymanager_logger = logging.getLogger("historymanager")
        self.simple_logger = logging.getLogger("simple_log")

        if advanced_logging:
            self.simple_logger.handlers = [h for h in self.simple_logger.handlers if type(h) != logging.StreamHandler]
        else:
            self.historymanager_logger.handlers = [h for h in self.outlookclient_logger.handlers if type(h) != logging.StreamHandler]

    def __enter__(self):
        return json.loads(self._file.read())

    def __exit__(self):
        self._file.close()

    @property
    def history(self):
        return self._history

    def save(self):
        self._file.truncate()
        self._file.write(str(self._history))
        self.historymanager_logger.info("Saving %d history shifts to %s" % (len(self.history), self._file.name))

    def add_shift(self, shift):
        '''Check if the shift isn't in the history, then add it to 'history'
        '''
        if shift not in self.history:
            self.history.append(shift)

    def remove_shift(self, shift):
        '''index and remove provided shift in history
        '''
        self.history.remove(shift)

    def replace_shift(self, old_shift, new_shift):
        '''index and remove old shift, then add new_shift
        '''
        self.remove_shift(old_shift)
        self.add_shift(new_shift)

    def update_shift(self, shift, update_info={}):
        '''provided a shift and a dict, replace the shift with new info
        '''
        self.replace(shift, shift.update(update_info))

    def transform_perm_shift(self, perm_shift):
        '''
        Input a perm_shift and transform it to a bunch of temp_shifts
        each containing their own weekly shift
        '''
        assert perm_shift["start_date"] <= perm_shift["end_date"], "Start must be before the end"

        if perm_shift["type"] != "PermShift":
            return [perm_shift]

        shifts = []
        weeks = (shift["end_date"] - shift["start_date"]).days / 7
        for week_num in range(weeks):
            decomposed_shift = deepcopy(perm_shift)
            decomposed_shift["start_date"] = shift["start_date"] + datetime.timedelta(weeks=week_num)
            decomposed_shift["end_date"] = decomposed_shift["start_date"]
            decomposed_shift["type"] = "TempShift"
            decomposed_shift["actions"] = "TempTake"

            shifts.append(decomposed_shift)

        return shifts

    def get_shifts_in_date_range(self, start, end):
        '''
        Look through shifts and return shifts only within range.
        If the shift is a TempTake, return that one shift, if it
        is a PermTake, return all the TempTakes in the PerTake range
        '''
        self.historymanager_logger.info("Returning shifts in daterange %s to %s" % (start, end))
        assert start <= end, "Start must be before the end"

        in_arg_range = lambda d: start <= d <= end
        in_shift_range = lambda shift, date: shift["start_date"] <= date <= shift["end_date"]

        delete_shifts = []
        return_shifts = []
        for shift in self.history:
            if shift["type"] == "TempShift":
                assert shift["start_date"] == shift["end_date"], "Improper shift label"
                if in_arg_range(shift["start_date"]):
                    return_shifts.append(shift)
            elif shift["type"] == "PermShift":
                if in_arg_range(shift["start_date"]) and in_arg_range(shift["end_date"]):
                    return_shifts.append(shift)
                    
                deconstructed_temp_shifts = self.transform_perm_shift(shift)

                filtered_temp_shifts = []
                for deconstructed_temp_shift in deconstructed_temp_shifts:
                    if start <= deconstructed_temp_shift["start_date"] <= end:
                        filtered_temp_shifts.append(deconstructed_temp_shift)

                return_shifts.extend(filtered_temp_shifts)
            else:
                self.historymanager_logger.error("Improperly labeled shift %s" % (shift))
                self.historymanager_logger.error("Deleting shift")
                delete_shifts.append(shift)
        
        for delete_shift in delete_shifts:
            self.remove_shift(delete_shift)

        return return_shifts
