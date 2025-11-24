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
current_balance = 0

# format the the date to ISO 8601
def isodate(date) -> str:
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
            return datetime.strptime(date, format).date() # converting what was typed into a datetime object (datetime module) using "format"
        except ValueError:
            continue # if there's an error/exception, just continue to loop through possible date formates

    # if input is just year and month. This loops is the same as above, only with just year and month
    for format2 in ("%Y-m", "%m-%Y", "%m/Y", "%Y/m"):
        try:
            return datetime.strptime(date, format2).date()
        except ValueError:
            continue

    # error if the program doesn't recognize the input date format
    raise ValueError ("Unrecognized date format. Samples of date format: YYYY/MM/DD or MM-DD-YYYY, etc.")


# saving the new data when either adding an expense or editing an expense
def save_data(data: dict):

    global current_balance
    
    # This condition is a guard to make sure the parameter "data" is a dictionary
    # and that it contains the "entries" key inside it. If not, an error will be printed
    if not isinstance(data, dict) or "entries" not in data:
        print("Error saving data. Expects entries from the date provided.")
        return
    
    # by default, if data is None or empty, we set entries to
    # an empty dictionary and balance to current_balance
    entries = data.get("entries", {})
    balance = data.get("balance", current_balance)

    raw_entries = {} # preparing a dictionary "raw entries" for JSON serialization

    # this iteration will make sure that the date which was inputted from "add_expense" will be parsed properly into the JSON file
    # the date_key is the key, which is a date string, and the paired value for this date_key would be an array/list of all the items
    # entered on that specific date. It will then be paired with the "entries" string inside a dictionary called "ledger" and
    # and then written into the JSON file. The "ledger" dictionary will also contain the "balance" key paired with the current balance value
    # then finally, the "ledger" dictionary will be serialized into JSON and written into the file path specified by "LEDGER_FILE"
    # all this makes sure that all the dates with entries and the current balance is saved properly as key-pair objects and arrays
    try:
        for date_key, item_list in entries.items():
            raw_entries[date_key] = []
            # item_list should be an iterable of dict-like objects
            for item in item_list:
                item_entry_copy = dict(item)
                raw_entries[date_key].append(item_entry_copy)
    except TypeError as error:
        print("Error saving data:", error)
        return

    # updating "entries" string to pair with new "raw_entries", setting new balance, and parsing the "ledger" into the JSON file
    current_balance = balance

    ledger = {
        "entries": raw_entries,
        "balance": current_balance
    }
    
    LEDGER_FILE.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf_8")
    print("Log: save successful")


# loads the saved data from the directory chosen by the "LEDGER_FILE" variable
def load_data():

    global current_balance

    # just incase this is the first time you're using this program
    # this will generate the file initially with an 'entries' and 'balance' root
    if not LEDGER_FILE.exists():
        LEDGER_FILE.write_text(json.dumps({"entries": {}, "balance": 0}, ensure_ascii=False, indent=2), encoding="utf_8")

    # let's attempt to decode the JSON file into Python
    try:
        raw_data = json.loads(LEDGER_FILE.read_text(encoding="utf_8"))
        entries_raw = raw_data.get("entries", {})
        decoded_data = {}

        # each date is a key, and it's value will be an array of possible items
        # entered on that specific date ## see "sample_expenses_ledger.json"
        for date_key, item_entry in entries_raw.items():
            decoded_data[date_key] = []
            for copy in item_entry:
                item_entry_copy = dict(copy)
                decoded_data[date_key].append(item_entry_copy)

        # load balance if present
        current_balance = raw_data.get("balance", 0)
        print("Log: load successful")

        return decoded_data

    # just in case any kind of error occurs (such as corruption of the file)
    # this function will return an empty Python dictionary
    except Exception:
        print("Unable to load file. Trying again.")
        return {}
    

# this function allows the user to choose an entry by its index number
# it can be used by any function that needs to select an entry from a list
def choose_entry_by_index(listed_entries):

    # guard if there are no item entries for the specified date
    if not listed_entries:
        print("No entries available.")
        return None
    
    # displaying all entries with their index numbers (starting at 1)
    for i, entry in enumerate(listed_entries, start=1):
        # use the actual keys saved in entries: item, item_id, price, quantity
        print(f" {i}. [{entry.get('item')}] Item ID: {entry.get('item_id', '')[:8]} x {entry.get('quantity')} - Unit: {float(entry.get('price'))} Total: {float(entry.get('price')) * int(entry.get('quantity'))}")

    # the famous input for selecting an entry by its index number
    # and out of range and invalid input guards
    select_num = input(f"Select entry by number (or leave blank to cancel): ").strip() # input the number

    if not select_num: # can't be blank
        return None
    
    # converting the input string into an integer
    # and checking if it's in range of the listed entries
    try:
        index_num = int(select_num)
        if 1 <= index_num <= len(listed_entries):
            return index_num - 1
        else:
            print("Out of range.")
            return None
    except ValueError:
        print("Invalid selection.")
        return None


# this is the star of the show... records expenditure(s) for a date
def add_expense(data: dict):
    global current_balance
    # first, input the date
    try:
        date_key_raw = input("Date (format YYYY/MM/DD or MM-DD-YYYY): ").strip()
        # this expression parses the date using the function "parse_date"
        date_key = parse_date(date_key_raw)
    # ValueError guard if parsing fails
    except ValueError as error:
        print(error)
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

    # the same expression from "save_data" function
    ledger = {
        "entries": data,
        "balance": current_balance - (price * quantity)
    }

    save_data(ledger) # saving the data into the JSON file
    print(f"New expenditure saved \n {quantity} x of '{item}' valued at {price}. Total: {price * quantity}")


# this functions edits an existing record
def edit_record(raw_data: dict):
    global current_balance

    # as usual, input the date to be checked first
    try:
        date_key_input = input("Select a date (format YYYY/MM/DD or MM-DD-YYYY): ").strip()
        if not date_key_input:
            print("Please input a specific date to edit.")
            return
        date_key_parsed = parse_date(date_key_input) # parsing the date input into proper date object
    except ValueError as error:
        print(error)
        return

    date_key = isodate(date_key_parsed) # converting the parsed date into ISO format

    entries_for_date = raw_data.get(date_key, []) # retrieving the list of item entries for that date

    # guard if there are actually no entries for that date
    if not entries_for_date:
        print(f"No record for {date_key}.")
        return
    
    # lists entries and allows user to choose one by index number
    chosen_index_num = choose_entry_by_index(entries_for_date)

    # guard if no entry was chosen
    if chosen_index_num is None:
        return

    # get the selected entry
    entry = entries_for_date[chosen_index_num]

    # show current values and allow blank input to keep the current value/name
    print(f"Now editing '{entry.get('item')}'.")
    print("\nLeave blank to keep current value.")
    new_item = input(f"New name of [{entry.get('item')}]: ").lower() or entry.get('item')

    price_input = input(f"The item's price [{entry.get('price')}]: ").lower()
    if price_input == "":
        new_price = float(entry.get('price'))
    else:
        try:
            new_price = float(price_input)
        except ValueError:
            print("Invalid price. Aborting edit.")
            return

    quantity_input = input(f"How many? [{entry.get('quantity')}]: ").lower()
    if quantity_input == "":
        new_quantity = int(entry.get('quantity'))
    else:
        try:
            new_quantity = int(quantity_input)
            if new_quantity == 0:
                print("Quantity can't be 0. Aborting edit.")
                return
        except ValueError:
            print("Invalid quantity. Aborting edit.")
            return

    notes_input = input(f"Any notes or reminders? [{entry.get('notes')}]: ").lower()
    new_notes = notes_input if notes_input != "" else entry.get('notes')

    # compute against old total and update new balance
    old_total = float(entry.get('price')) * int(entry.get('quantity'))
    new_total = float(new_price) * int(new_quantity)
    delta = new_total - old_total
    # expenses reduce the balance; if new_total is larger, balance should decrease by delta
    current_balance -= delta

    # update the entry in place
    entry['item'] = new_item
    entry['price'] = new_price
    entry['quantity'] = int(new_quantity)
    entry['notes'] = new_notes
    entry['created_at'] = datetime.now().isoformat()
    # keep existing item_id

    save_data({"entries": raw_data, "balance": current_balance}) # save changes
    print(f"Record updated. Old total: {old_total} New total: {new_total}. New balance: {current_balance}")


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
        line_total = entry.get("price") * entry.get("quantity")
        total += line_total
        
        # displaying the entry details from the JSON save file
        print(f" {i}. [{entry['item']}. Price: {float(entry['price'])}]. Item ID: {entry['item_id'][:8]}. Quantity: {entry['quantity']}. Total: {float(entry['price']) * float(entry['quantity'])}")
        if entry.get("notes"):
            print(f" Notes: {entry['notes']}")
        
    # displays the total that was calculated earlier
    print(f"Total for {target_key}: {total}")


# this loads the current balance saved inside the JSON file
# and assigns it to the global variable "current_balance"
def load_balance():

    global current_balance

    # attempt to read the balance from the JSON file
    try:
        raw = json.loads(LEDGER_FILE.read_text(encoding="utf_8"))
        current_balance = raw.get("balance", 0)
        print("Load balance successful")
    except:
        print("Unable to get current balance")


# this saves the current balance into the JSON file
def save_balance(bal):

    global current_balance

    # set current_balance and write it while preserving entries
    current_balance = bal

    try:
        raw = json.loads(LEDGER_FILE.read_text(encoding="utf_8"))
    except Exception:
        raw = {}

    entries = raw.get("entries", {})

    # updating ledger with new balance. If this isn't done
    # the entries won't be saved into the JSON file
    ledger = {
        "entries": entries,
        "balance": current_balance
        }
    
    # formal update of the JSON file
    LEDGER_FILE.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf_8")


# this function tracks money that was gained (such as salary, gifts, etc.)
def add_gained():

    # the global variable "current_balance" will
    # always be updated through this function
    global current_balance

    # input the amount gained
    gained_amount_string = input("Enter gained money amount: ").strip()

    # guard for blank input or invalid number
    if not gained_amount_string:
        print("Amount can't be blank.")
        return
    try:
        gained_amount = float(gained_amount_string)
    except ValueError:
        print("Invalid amount. Must be a number.")
        return

    # the gained amount will now be added to the current balance
    current_balance += gained_amount

    save_balance(current_balance) # saving the new balance into the JSON file
    print(f"Gained {gained_amount}. New balance: {current_balance}")


# just a simple function to check the current balance
def check_balance():

    global current_balance

    print(f"Current balance: {current_balance}")


# help command to bring up other available commands to the user
def show_commands():
    print("'add' - add expense"
          "\n'edit' - edit a record"
          "\n'gain' - add gained"
          "\n'bal' - shows balance"
          "\n'show d' - show day total"
    )


def main_program():
    print("Test phase \n type an available function")
    show_commands()

    the_record_file = load_data() # load existing data from the JSON file
    load_balance() # load existing balance from the JSON file
    
    # main loop for the user input of what the heck he wants to do
    while True:
        typed_command = input("Input the keyword of the command: ").strip().lower()
        if typed_command == "add":
            add_expense(the_record_file)
        elif typed_command == "edit":
            edit_record(the_record_file)
        elif typed_command == "show d":
            show_day_total(the_record_file)
        elif typed_command == "gain":
            add_gained()
        elif typed_command == "bal":
            check_balance()
        else:
            print("Unknown command. Please input a command")

main_program()