# Library Simulation

This Python script simulates a basic library system where users can borrow and return books. The simulation runs through multiple days, and random events such as book borrowing, returns, and summaries are generated to mimic a dynamic library environment.

## Dependencies
- pandas

## Usage
1. Ensure you have the required dependencies installed.
   ```bash
   pip install pandas

2. Run the script.
   ```bash
   python library.py

3. The simulation will start, and you'll see daily operations, including book transactions and summaries.
Description of Classes
----------------------

### Book

Represents a book in the library with attributes like title, author, return time, and borrowing status.

### ChancesAndTime

Manages random events and time calculations for the simulation, such as dice rolls for returns and borrowings.

### Library

Handles library operations, including book database initialization, borrowing, returning, and displaying summaries.

### Simulation

Initiates and manages the overall simulation, tracking days, and providing daily summaries.

How It Works
------------

The simulation starts with an initialized library, and each day simulates book transactions and user interactions. At the end of each day, a summary is displayed, including the most borrowed book and the number of books borrowed.

Note
----

-   The script relies on a CSV file (`book_db.csv`) for the initial book database. Ensure this file is present and correctly formatted before running the simulation.

Feel free to explore and modify the script to customize the simulation or integrate additional features.
