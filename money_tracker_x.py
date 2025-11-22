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
        "%m-%d-%Y",
        "%m/%d/%Y"
        ):

        try:
            return datetime.strptime(date, format).date()
        except ValueError:
            continue

    # if input is just year and month
    for format2 in ("%Y-m", "%m-%Y", "%m/Y", "%Y/m"):
        try:
            return datetime.strptime(date, format2).date()
        except ValueError:
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
                decoded_data[date_key].append(item_entry_copy)
        print("Log: load succesful")

    # returning the newly decoded data into Python objects
        return decoded_data
    
    # just in case any kind of error occurs (such as corruption of the file)
    # this function will return an empty Python dictionary
    except Exception:
        print("Unable to load file. Trying again.")
        return {}


# this is the star of the show... records expenditure(s) for a date
def add_expense(data: dict):
    
    # first, input the date
    try:
        date_key_raw = input("Date (format YYYY/MM/DD or MM-DD-YYYY): ").strip()
        # this expression parses the date using the function "parse_date"
        date_key = parse_date(date_key_raw)
    # ValueError guard if parsing fails
    except ValueError as ex:
        print(ex)
        return

    # input the name of the item
    item = input("Name of item: ")
    if not item or item == "":
            print("Item name can't be blank")
            return
    
    # input the price. it will be converted into a float
    price_string = input("The item's price: ")
    price = float(price_string)
    try:
        # guard if price not set
        if not price_string or price_string == "":
            print("Please input the price")
            return
    except ValueError:
        print("Invalid price. Must be a number/integer.")
    
    # input how many of the item was purchased
    quantity_string = input("How many?: ")
    # the variable "quantity" is set to default at 1 below:
    quantity = 1

    # if user inputs a positive number, the
    # default will be replaced with the input
    if quantity_string:
        try:
            quantity = int(quantity_string)
            if quantity == 0:
                print("Quantity can't be 0.")
                return
        except:
            print("Invalid quantity input. Defaulted to 1")
            quantity = 1
            return

    # notes about this item
    notes = input("Any notes or reminders?: ")
    if not notes or notes == "":
        print("Blank note")
        notes = None

    # the "item_entry" variable is a dictionary converted from
    # the JSON objects. Inside are key-pair values for each item
    item_entry = {
        "item": item,
        "price": price,
        "quantity": int(quantity),
        "notes": notes,
        "created_at": datetime.now().isoformat(),
        "item_id": uuid.uuid4().hex
    }

    # after all inputs are done, we save the data
    date_key = isodate(date_key) # converting date to ISO format
    data.setdefault(date_key, []).append(item_entry) # adding the item entry for that date
    save_data(data) # saving the data into the JSON file
    print(f"New expenditure saved \n {quantity} x of '{item}' valued at {price}. Total: {price * quantity}")


# this functions shows all entries for a specific date along with the total expenditure for that date
def show_day_total(raw_data: dict):

    # first, input the date to be displayed
    target_date_input = input("Input a date to be displayed: ").strip()

    # this parses the daet using the function "parse_date"
    # it's in a try-except block to incase there's a ValueError
    # but there shouldn't be any since the input is controlled by the parse_date function
    try:
        target_date_parsed = parse_date(target_date_input)
    except ValueError as error:
        print(error)
        return

    # now we convert the parsed date into ISO format to match the keys in the JSON
    target_key = isodate(target_date_parsed)

    # now we retrieve the list of entries for that specific date
    entries = raw_data.get(target_key, [])

    # initializing "total" variable
    total = float(0)
    
    # guard if there are no entries for that date
    if not entries:
        print(f"No entries found for {target_key}")
        return
    
    # the magic for displaying each entry and calculating the total
    print(f"Entries for {target_key}:")

    # iterating through each entry for that date and assigning a number to each
    for i, entry in enumerate(entries, start=1):
        # calculating the line total for each entry
        line_total = entry["price"] * entry.get("quantity", 1)
        total += line_total
        
        # displaying the entry details from the JSON save file
        print(f" {i}. [{entry['item']}. Item ID: {entry['item_id'][:8]}] {entry['quantity']}. Total: {float(entry['price'])} -> {float(line_total)}")
        if entry.get("notes"):
            print(f" Notes: {entry['notes']}")

        # displays the total that was calculated earlier
        print(f"Total for {target_key}: {float(line_total)}")


def add_gained():
    gained_amount_string = input("Enter gained money amount: ")
    if gained_amount_string:
        try:
            gained_amount = gained_amount_string
        except ValueError as ex:
            print(ex)
    else:
        print("Amount can't be blank.")
        return

def load_balance():
    current_balance = {}


# help command to bring up other available commands 

def show_commands():
    print("'add' - add expense"
          "\n'gained' - add gained"
          "\n'edit' - edit a record"
          "\n'show d' - show day total"
          "\n'show m' - show month total"
    )


def main_program():
    print("Test phase \n type an available function")
    print("'add' adds an expenditure for the record"
          "\n'show d' - show day total"
          )

    the_record_file = load_data()
    

    while True:
        typed_command = input("Input the keyword of the command: ").strip().lower()
        if typed_command == "add":
            add_expense(the_record_file)
        elif typed_command == "show d":
            show_day_total(the_record_file)
        elif typed_command == "gained":
            add_gained()
        else:
            print("Please input a command")

main_program()