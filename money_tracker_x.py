# money_tracker_x
# keep track of all your household expenses

# we will need the datetime module for date objects
# sys module so we can direct the .json file containing the record
# of coursse, we import the json module too
# we will also import csv for exporting the records as csv
# uuid module for creating unique entry IDs for each item recorded
# lastly, pathlib module's Path for saving the file in your local directory

from datetime import date, time, datetime
from pathlib import Path
import sys
import uuid
import json
import csv

LEDGER_FILE = Path.home() / "expenses_ledger.json"

# format the the date to ISO 8601

def isodate(date):
    return date.isoformat()


# let's parse the date for the intepreter

def parse_date(date) -> str:

    # if no input, defaults to today's date
    if not date or date.strip() == "":
        return date.today()
    
    # if input is complete date, checks in what format
    for format in (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y"
        ):

        try:
            return datetime.strptime(date, format).date()
        except:
            continue

    # if input is just year and month
    for format2 in ("%Y-m", "%m-%Y", "%m/Y", "%Y/m"):
        try:
            return datetime.strptime(date, format2).date()
        except:
            continue

    # error if the program doesn't recognize the input date format
    raise ValueError ("Unrecognized date format. Samples of date format: YYYY/MM/DD or MM-DD-YYYY, etc.")


# saving the new data when either adding an expense or editing an expense
def save_data(data):
    
    # this will set it up as a JSON object for saving it as a .json file
    raw_data = {}

    # let's attempt to encode the pairing of the date
    # with it's corresponding entry in the JSON
    try:
        # each date is a key, and it's value will be an array of possible items
        # entered on that specific date ## see "sample_expenses_ledger.json"
        for date_key, item_entry in data.items():
            raw_data[date_key] = []
            for copy in item_entry:
                item_entry_copy = dict(copy)
                raw_data[date_key].append(item_entry_copy)
                print("Log: save succesful")

    # there might be a type error with the "for copy in item_entry" loop
    except TypeError as ex:
        print ("Error saving data:", ex)
        return

    # time to write everything into the JSON file
    LEDGER_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf_8")


# loads the saved data from the directory chosen by the "LEDGER_FILE" variable
def load_data():

    # just incase this is the first time you're using this program
    # this will generate the file initially
    if not LEDGER_FILE.exists():
        raw_data = {}
        LEDGER_FILE.write_text(json.dumps(raw_data, ensure_ascii=False, indent=2), encoding="utf_8")

    # let's attempt to decode the JSON file into Python
    try:
        raw_data = json.loads(LEDGER_FILE.read_text(encoding="utf_8"))
        decoded_data = {}

        # each date is a key, and it's value will be an array of possible items
        # entered on that specific date ## see "sample_expenses_ledger.json"
        for date_key, item_entry in raw_data.items():
            decoded_data[date_key] = []
            for copy in item_entry:
                item_entry_copy = dict(copy)
                decoded_data.append(item_entry_copy)
                print("Log: load succesful")

    # returning the newly decoded data into Python objects
        return decoded_data
    
    # just in case any kind of error occurs (such as corruption of the file)
    # this function will return an empty Python dictionary
    except Exception:
        print("Unable to load file. Trying again.")
        return {}



# help command to bring up other available commands 

def show_commands():
    print("'add' - add expense"
          "\n'gained' - add gained"
          "\n'edit' - edit a record"
          "\n'show m' - show month total"
          "\n'show d' - show day total"
    )