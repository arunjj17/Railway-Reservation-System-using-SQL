import tkinter as tk
from tkinter import Button, Entry, Label, Scrollbar, Text, END
import sqlite3
import pandas as pd

# Initialize Tkinter
root = tk.Tk()
root.title("Railway Reservation System")

# Connect to SQLite database
conn = sqlite3.connect('project.db')  # Replace 'your_database_name' with your actual database name
cursor = conn.cursor()

# Create tables if not exists
create_tables_query = '''
CREATE TABLE IF NOT EXISTS Train (
    TrainNumber INTEGER PRIMARY KEY,
    TrainName TEXT,
    PremiumFair INTEGER,
    GeneralFair INTEGER,
    SourceStation TEXT,
    DestinationStation TEXT
);

CREATE TABLE IF NOT EXISTS Train_Status (
    TrainDate TEXT,
    TrainName TEXT,
    PremiumSeatsAvailable INTEGER,
    GenSeatsAvailable INTEGER,
    PremiumSeatsOccupied INTEGER,
    GenSeatsOccupied INTEGER
);

CREATE TABLE IF NOT EXISTS Passenger (
    SSN INTEGER PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT,
    Address TEXT,
    City TEXT,
    County TEXT,
    Phone TEXT,
    BirthDate TEXT
);

CREATE TABLE IF NOT EXISTS Booked (
    PassengerSSN INTEGER,
    TrainNumber INTEGER,
    TicketType TEXT,
    Status TEXT,
    FOREIGN KEY (PassengerSSN) REFERENCES Passenger(SSN),
    FOREIGN KEY (TrainNumber) REFERENCES Train(TrainNumber)
);
'''
cursor.executescript(create_tables_query)
conn.commit()

# Load data from CSV files
train_data = pd.read_csv('Train.csv')
train_status_data = pd.read_csv('Train_Status.csv')
passenger_data = pd.read_csv('Passenger.csv')
booked_data = pd.read_csv('Booked.csv')

train_data.to_sql('Train', conn, if_exists='replace', index=False)
train_status_data.to_sql('Train_Status', conn, if_exists='replace', index=False)
passenger_data.to_sql('Passenger', conn, if_exists='replace', index=False)
booked_data.to_sql('Booked', conn, if_exists='replace', index=False)

# Functions
def execute_query(query, parameters=None):
    try:
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        column_names = [description[0] for description in cursor.description] if cursor.description else []
        return column_names, result
    except Exception as e:
        return None, str(e)

def display_result(column_names, result):
    text_result.delete('1.0', END)
    if column_names:
        text_result.insert(END, ', '.join(map(str, column_names)) + '\n')
        if result:
            for row in result:
                text_result.insert(END, ', '.join(map(str, row)) + '\n')
        else:
            text_result.insert(END, 'No results found.')
    else:
        text_result.insert(END, 'No results found.')

# Query 1: User input the passenger’s last name and first name and retrieve all trains they are booked on.
def search_passenger_trains():
    first_name = entry_first_name.get()
    last_name = entry_last_name.get()
    query = f'''
        SELECT Train.TrainNumber, Train.TrainName, Booked.TicketType, Booked.Status
        FROM Passenger
        JOIN Booked ON Passenger.SSN = Booked.PassengerSSN
        JOIN Train ON Booked.TrainNumber = Train.TrainNumber
        WHERE LOWER(Passenger.FirstName) = LOWER(?) AND LOWER(Passenger.LastName) = LOWER(?)
    '''
    column_names, result = execute_query(query, (first_name, last_name))
    display_result(column_names, result)

# Query 2: User input the Date and list of passengers traveling on the entered day with confirmed tickets displays on UI.
def list_passengers_on_date():
    selected_date = entry_date.get()
    query = f'''
        SELECT Passenger.FirstName, Passenger.LastName, Booked.TicketType, Booked.Status
        FROM Booked
        JOIN Passenger ON Booked.PassengerSSN = Passenger.SSN
        WHERE Booked.Status = 'Booked' AND Booked.TrainNumber IN (
        SELECT TrainNumber FROM Train_Status Join Train on Train.TrainName = Train_Status.TrainName WHERE Train_Status.TrainDate = '{selected_date}')
    '''
    column_names, result = execute_query(query)
    print(column_names,result)
    display_result(column_names, result)
# Query 3: User input the age of the passenger (50 to 60) and UI displays the train information (Train
# Number, Train Name, Source and Destination) and passenger information (Name, Address, Category, ticket status)
# of passengers who are between the ages of 50 to 60.
def display_passengers_by_age():
    min_age = 1
    max_age = 100
    query = f'''
    SELECT Train.TrainNumber, Train.TrainName, Train.SourceStation, strftime('%Y', 'now'),
           Passenger.FirstName, Passenger.LastName, Passenger.Address, Passenger.City,
           Passenger.County, Passenger.Phone, Passenger.bdate, Booked.TicketType, Booked.Status
    FROM Booked
    JOIN Train ON Booked.TrainNumber = Train.TrainNumber
    JOIN Passenger ON Booked.PassengerSSN = Passenger.SSN
    WHERE (CAST(strftime('%Y', 'now') AS INTEGER) - CAST(substr(Passenger.bdate, 7, 11) AS INTEGER)) BETWEEN 50 AND 60;
    '''
    column_names, result = execute_query(query)
    print(result)
    display_result(column_names, result)

# Query 4: List all the train names along with the count of passengers it is carrying.
def list_train_passenger_count():
    query = '''
        SELECT Train.TrainNumber, Train.TrainName, COUNT(Booked.PassengerSSN) as PassengerCount
        FROM Train
        LEFT JOIN Booked ON Train.TrainNumber = Booked.TrainNumber
        GROUP BY Train.TrainNumber, Train.TrainName;
    '''
    column_names, result = execute_query(query)
    display_result(column_names, result)

# Query 5: Enter a train name and retrieve all the passengers with confirmed status traveling in that train.
def retrieve_passengers_by_train():
    entered_train_name = entry_train_name.get()
    query = f'''
        SELECT Passenger.FirstName, Passenger.LastName, Booked.TicketType, Booked.Status
        FROM Booked
        JOIN Train ON Booked.TrainNumber = Train.TrainNumber
        JOIN Passenger ON Booked.PassengerSSN = Passenger.SSN
        WHERE Train.TrainName = '{entered_train_name}' AND Booked.Status = 'Booked';
    '''
    column_names, result = execute_query(query)
    print(entered_train_name,result)
    display_result(column_names, result)

# Query 6: User Cancel a ticket (delete a record) and show that passenger in the waiting list get ticket confirmed.
def cancel_ticket_and_confirm_waiting():
    passenger_ssn = entry_passenger_ssn.get()
    train_number = entry_train_number.get()

    # Delete the existing record
    delete_query = f"DELETE FROM Booked WHERE PassengerSSN = '{passenger_ssn}' AND TrainNumber = {train_number};"
    execute_query(delete_query)

    # Check if there's a passenger in the waiting list and confirm their ticket
    confirm_waiting_query = f'''
        UPDATE Booked
        SET Status = 'Booked'
        WHERE TrainNumber = {train_number} AND Status = 'WaitL'
        Order by RANDOM()
        LIMIT 1;
    '''
    execute_query(confirm_waiting_query)
    # Display the updated results
    retrieve_passengers_by_train()


# ...

# Functions (Continued)
def check_passenger_data():
    query = 'SELECT * FROM Passenger'
    column_names, result = execute_query(query)
    display_result(column_names, result)

def check_booked_data():
    query = 'SELECT * FROM Booked'
    column_names, result = execute_query(query)
    display_result(column_names, result)

def check_count_of_booked():
    query = "SELECT COUNT(*) FROM Booked WHERE Status = 'Booked';"
    column_names, result = execute_query(query)
    display_result(column_names, result)

def check_count_of_waitlist():
    query = "SELECT COUNT(*) FROM Booked WHERE Status = 'WaitL';"
    column_names, result = execute_query(query)
    display_result(column_names, result)


def list_tables():
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    column_names, result = execute_query(query)
    display_result(column_names, result)

def describe_table():
    table_name = entry_describe_table.get()
    query_info = f"PRAGMA table_info({table_name});"
    column_info_names, column_info_result = execute_query(query_info)

    query_rows = f"SELECT * FROM {table_name};"
    rows_column_names, rows_result = execute_query(query_rows)

    text_result.delete('1.0', END)
    text_result.insert(END, 'Column Information:\n')
    display_result(column_info_names, column_info_result)

    text_result.insert(END, '\n\nAll Rows in the Table:\n')
    display_result(rows_column_names, rows_result)


# GUI Setup
label_first_name = Label(root, text='First Name:')
entry_first_name = Entry(root)
label_last_name = Label(root, text='Last Name:')
entry_last_name = Entry(root)
button_search_passenger_trains = Button(root, text='Search Trains', command=search_passenger_trains)

label_date = Label(root, text='Date (DD-MM-YYYY):')
entry_date = Entry(root)
button_list_passengers_on_date = Button(root, text='List Passengers on Date', command=list_passengers_on_date)

label_age = Label(root, text='Age (50 to 60):')
button_display_passengers_by_age = Button(root, text='Display Passengers by Age', command=display_passengers_by_age)

button_list_train_passenger_count = Button(root, text='List Train Passenger Count', command=list_train_passenger_count)

label_train_name = Label(root, text='Train Name:')
entry_train_name = Entry(root)
button_retrieve_passengers_by_train = Button(root, text='Retrieve Passengers by Train', command=retrieve_passengers_by_train)

label_passenger_ssn = Label(root, text='Passenger SSN:')
entry_passenger_ssn = Entry(root)
label_train_number = Label(root, text='Train Number:')
entry_train_number = Entry(root)
button_cancel_ticket_and_confirm_waiting = Button(root, text='Cancel Ticket and Confirm Waiting', command=cancel_ticket_and_confirm_waiting)

button_check_passenger_data = Button(root, text='Check Passenger Data', command=check_passenger_data)
button_check_booked_data = Button(root, text='Check Booked Data', command=check_booked_data)
button_check_count_of_booked = Button(root, text='Check Count of Booked', command=check_count_of_booked)
button_check_count_of_waitlist = Button(root, text='Check Count of Waitlist', command=check_count_of_waitlist)

button_list_tables = Button(root, text='List Tables', command=list_tables)

label_describe_table = Label(root, text='Table Name:')
entry_describe_table = Entry(root)
button_describe_table = Button(root, text='Describe Table', command=describe_table)

text_result = Text(root, wrap='word', height=15, width=80)
scrollbar = Scrollbar(root, command=text_result.yview)
text_result.configure(yscrollcommand=scrollbar.set)

# Place widgets in the grid
label_first_name.grid(row=0, column=0, padx=10, pady=5)
entry_first_name.grid(row=0, column=1, padx=10, pady=5)
label_last_name.grid(row=0, column=2, padx=10, pady=5)
entry_last_name.grid(row=0, column=3, padx=10, pady=5)
button_search_passenger_trains.grid(row=0, column=4, padx=10, pady=5)

label_date.grid(row=1, column=0, padx=10, pady=5)
entry_date.grid(row=1, column=1, padx=10, pady=5)
button_list_passengers_on_date.grid(row=1, column=2, padx=10, pady=5)

label_age.grid(row=2, column=0, padx=10, pady=5)
button_display_passengers_by_age.grid(row=2, column=1, padx=10, pady=5)

button_list_train_passenger_count.grid(row=3, column=0, padx=10, pady=5)

label_train_name.grid(row=4, column=0, padx=10, pady=5)
entry_train_name.grid(row=4, column=1, padx=10, pady=5)
button_retrieve_passengers_by_train.grid(row=4, column=2, padx=10, pady=5)

label_passenger_ssn.grid(row=5, column=0, padx=10, pady=5)
entry_passenger_ssn.grid(row=5, column=1, padx=10, pady=5)
label_train_number.grid(row=5, column=2, padx=10, pady=5)
entry_train_number.grid(row=5, column=3, padx=10, pady=5)
button_cancel_ticket_and_confirm_waiting.grid(row=5, column=4, padx=10, pady=5)

button_check_passenger_data.grid(row=6, column=0, padx=10, pady=5)
button_check_booked_data.grid(row=6, column=1, padx=10, pady=5)
button_check_count_of_booked.grid(row=6, column=2, padx=10, pady=5)
button_check_count_of_waitlist.grid(row=6, column=3, padx=10, pady=5)

button_list_tables.grid(row=7, column=0, padx=10, pady=5)

label_describe_table.grid(row=8, column=0, padx=10, pady=5)
entry_describe_table.grid(row=8, column=1, padx=10, pady=5)
button_describe_table.grid(row=8, column=2, padx=10, pady=5)

text_result.grid(row=9, columnspan=5, padx=10, pady=5)
scrollbar.grid(row=9, column=5, sticky='ns')

# Run the GUI
root.mainloop()

# Close the database connection when the GUI is closed
conn.close()
