Railway Reservation System using SQL

Created a GUI for the RRS database SQL Queries. Used Python programming languages to develop a GUI interface and Sqlite3 for the data base. 

This system helps to maintain the records of different trains, the train’s status, and passengers.
The database consists of 4 tables:

• Train: Train Number, Train Name, Premium Fair, General Fair, Source Station, Destination Station

• Train_Status: TrainDate, TrainName, PremiumSeatsAvailable, GenSeatsAvailable, PremiumSeatsOccupied, GenSeatsOccupied

• Passenger: first_name, last_name, address, city, county, phone, SSN, bdate

• Booked: Passanger_ssn, Train_Number, Ticket_Type, Status

Note: As the system is very large and is not feasible to develop therefore there are some
assumptions that need to be considered, for example:
• Only two categories of tickets are available: Premium and General Ticket

• The total number of tickets can be booked in each category (Premium and General) is 10

• Number of tickets in waiting list is 2

• Total Number of trains are 5

• Any stops made by a train before its destination and their bookings are not considered
