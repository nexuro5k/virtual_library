"""
Library Simulation

This script simulates a library system where books can be borrowed and returned. 
The simulation runs through multiple days, tracking book transactions and providing daily summaries.

Dependencies:
- pandas

Usage:
Run the script to start the library simulation. The simulation will iterate through days, simulating book borrowing, returns, and providing daily summaries.

"""
from collections import Counter
import random
import time
from datetime import datetime, timedelta

import pandas as pd


DB_FILENAME: str = "book_db.csv"
DEFAULT_DATE: datetime = datetime(1970, 1, 1, 1, 1)


def action(func: callable):
    """
    A decorator to wrap methods with error handling.

    Args:
        func (callable): The method to be wrapped.

    Returns:
        wrapper: The wrapped method with error handling.
    """

    def wrapper(*args):
        try:
            func(*args)
        except Exception as ex:
            print(f"({func.__name__}): {ex}")
            return False
        return True

    return wrapper


class Book:
    """
    Class representing a book in the library.

    Attributes:
        title (str): The title of the book.
        author (str): The author of the book.
        return_time (datetime): The expected return time of the book.
        returned (bool): A flag indicating if the book has been returned.
        borrowed (bool): A flag indicating if the book is currently borrowed.

    Methods:
        __init__: Initializes a Book object.
    """

    title: str
    author: str
    return_time: datetime
    returned: bool
    borrowed: bool

    def __init__(
        self,
        title: str,
        author: str,
        return_time: datetime = DEFAULT_DATE,
        returned: bool = False,
        borrowed: bool = False,
    ):
        self.title = title
        self.author = author
        self.return_time = return_time
        self.returned = returned
        self.borrowed = borrowed


class ChancesAndTime:
    """
    Class handling random events and time calculations for the simulation.

    Attributes:
        start_time (datetime): The starting time of the library operation.
        end_time (datetime): The ending time of the library operation.

    Methods:
        __init__: Initializes a ChancesAndTime object.
        return_diceroll: Simulates a dice roll for book returns.
        borrow_diceroll: Simulates a dice roll for book borrowings.
        random_book: Randomly selects a book from the provided list.
        random_return_time: Generates a random return time for a borrowed book.
        date_up_to_minutes: Returns a new datetime object up to minutes precision.
        prefixed_print: Prints a formatted message with a day count and time.
    """

    start_time: datetime
    end_time: datetime

    def __init__(self):
        current_time = datetime.now()
        self.start_time = datetime(
            current_time.year, current_time.month, current_time.day, 10, 0
        )  # Start time at 10:00 AM
        self.end_time = datetime(
            current_time.year, current_time.month, current_time.day, 20, 0
        )  # End time at 20:00 PM

    def return_diceroll(self) -> bool:
        # 95% chance to return a book
        diceroll = random.randint(1, 100)
        if diceroll > 5:
            return True

        return False

    def borrow_diceroll(self) -> bool:
        # 50% chance to borrow a book
        diceroll = random.randint(1, 2)
        if diceroll > 1:
            return True

        return False

    def random_book(self, books: list) -> Book:
        book_index = random.randint(0, len(books) - 1)
        return books[book_index]

    def random_return_time(self, simulation_current_time: datetime) -> datetime:
        # Calculate the time difference in minutes.
        time_difference = (
            self.end_time - simulation_current_time
        ).total_seconds() // 60

        # Generate a random return time using the minute time difference.
        return_time = simulation_current_time + timedelta(
            minutes=round(random.randint(0, time_difference))
        )

        return datetime(
            year=return_time.year,
            month=return_time.month,
            day=return_time.day,
            hour=return_time.hour,
            minute=return_time.minute,
        )

    def date_up_to_minutes(self, input_datetime: datetime) -> datetime:
        return datetime(
            year=input_datetime.year,
            month=input_datetime.month,
            day=input_datetime.day,
            hour=input_datetime.hour,
            minute=input_datetime.minute,
        )

    def prefixed_print(self, day_count: int, time: str, txt: str):
        print(f"Day {day_count} {time}: {txt}")


class Library:
    """
    Class representing the library and its operations.

    Attributes:
        book_db (pd.DataFrame): The database of books.
        filter (list): List of allowed filter attributes for book queries.
        books (list[Book]): List of Book objects representing available copies in the library.

    Methods:
        __init__: Initializes a Library object.

        _get_book: Retrieves books from the database based on search criteria.
        _init_book_db: Initializes the book database.
        _init_filter: Initializes the filter attribute.
        _init_books: Initializes the list of available books.
        _load_book_db: Loads the book database from a CSV file.
        _is_book_borrowable: Checks if a book is available for borrowing.
        _remove_book_copy: Decreases the available copies of a book.
        _add_book_copy: Increases the available copies of a book.

        borrow_book: Borrows a book from the library.
        return_book: Returns a borrowed book to the library.
        get_book_by_title: Retrieves book information based on the title.
        get_books_by_author: Retrieves books written by a specific author.
        get_books_by_publication_year: Retrieves books published in a specific year.
        another_chance_to_return: Adjusts the return time for books for the next day.
        process_row: Processes a row from the book database and adds book copies to the library.
    """

    book_db: pd.DataFrame
    filter: list
    books: list[Book]

    def __init__(self):
        self._init_book_db()
        self._init_filter()
        self._init_books()

    def _get_book(self, search_for: str, search_value: tuple[str, int]) -> pd.DataFrame:
        if search_for not in self.filter:
            return pd.DataFrame()

        return self.book_db[self.book_db[search_for] == search_value]

    @action
    def _init_book_db(self):
        if not self._load_book_db():
            print("Couldn't load the book database.")

    def _init_filter(self):
        self.filter = (
            "title",
            "author",
            "publication_year",
        )

    def _init_books(self):
        self.books = []

        self.book_db.apply(self.process_row, axis=1)

    def process_row(self, row):
        title = row["title"]
        author = row["author"]
        available_copies = row["available_copies"]

        for _ in range(available_copies):
            book_copy = Book(title, author)
            self.books.append(book_copy)

    @action
    def _load_book_db(self):
        self.book_db = pd.read_csv(DB_FILENAME)

    def _is_book_borrowable(self, book_title: str) -> bool:
        book = self.get_book_by_title(book_title)
        return True if book["available_copies"] > 0 else False

    @action
    def _remove_book_copy(self, book_title: str):
        self.book_db.loc[self.book_db["title"] == book_title, "available_copies"] -= 1
        self.book_db.to_csv(DB_FILENAME, index=False)

    @action
    def _add_book_copy(self, book_title: str):
        self.book_db.loc[self.book_db["title"] == book_title, "available_copies"] += 1
        self.book_db.to_csv(DB_FILENAME, index=False)

    def borrow_book(self, book_title: str) -> bool:
        if self._is_book_borrowable(book_title):
            return self._remove_book_copy(book_title)

        return False

    def return_book(self, book_title: str) -> bool:
        return self._add_book_copy(book_title)

    def get_book_by_title(self, title: str) -> dict:
        # Assuming there are no duplicate titles in the CSV.
        try:
            return self._get_book("title", title).to_dict("records")[0]
        except IndexError:
            return {}

    def get_books_by_author(self, author: str) -> list:
        return self._get_book("author", author).to_dict("records")

    def get_books_by_publication_year(self, year: int) -> list:
        return self._get_book("publication_year", year).to_dict("records")

    def another_chance_to_return(self):
        for book in self.books:
            book.return_time += timedelta(days=1)


class Simulation:
    """
    Class representing the simulation of library operations over multiple days.

    Attributes:
        start_time (datetime): The starting time of the simulation.
        end_time (datetime): The ending time of the simulation.
        current_day (int): The current day in the simulation.
        library (Library): The library object for the simulation.
        common (ChancesAndTime): The ChancesAndTime object for random events and time calculations.

    Methods:
        __init__: Initializes a Simulation object.
        unreturned_books: Returns the count of books that are currently borrowed and not returned.
        most_popular_book: Returns the most borrowed book and its borrowing count.
        simulate_day: Simulates a day of library operations, including book transactions and summaries.
        daily_summary: Displays a summary of the day's library operations.
    """

    start_time: datetime
    end_time: datetime
    current_day: int
    library: Library
    common: ChancesAndTime

    def __init__(self):
        self.library = Library()
        self.common = ChancesAndTime()

        self.current_time = self.common.start_time
        self.end_time = self.common.end_time
        self.current_day = 1

    def unreturned_books(self) -> list:
        return sum(
            1 for book in self.library.books if not book.returned and book.borrowed
        )

    def most_popular_book(self) -> tuple:
        return Counter(
            book.title for book in self.library.books if book.borrowed
        ).most_common(1)[0]

    def simulate_day(self):
        current_loop_time = self.common.start_time
        print(f"--- Starting day {self.current_day} ---")
        while current_loop_time < self.common.end_time:
            # Display current hour and minute
            time_msg = current_loop_time.strftime("%H:%M")

            for book in self.library.books:
                current_time_minutes = self.common.date_up_to_minutes(current_loop_time)

                # Check if any books should be returned at this time.
                if (
                    book.return_time == current_time_minutes
                    and book.borrowed is True
                    and book.returned is False
                ) and self.common.return_diceroll():
                    if self.library.return_book(book.title):
                        self.common.prefixed_print(
                            self.current_day,
                            time_msg,
                            f"{book.title} has been returned.",
                        )
                        book.returned = True
                    else:
                        self.common.prefixed_print(
                            self.current_day,
                            time_msg,
                            f"The book {book.title} couldn't be returned.",
                        )

            if self.common.borrow_diceroll():
                book = self.common.random_book(self.library.books)

                if book.borrowed is False and self.library.borrow_book(book.title):
                    book.borrowed = True
                    book.returned = False
                    book.return_time = self.common.random_return_time(
                        current_time_minutes
                    )

                    self.common.prefixed_print(
                        self.current_day, time_msg, f"{book.title} has been borrowed."
                    )
                else:
                    self.common.prefixed_print(
                        self.current_day,
                        time_msg,
                        f"The book {book.title} couldn't be borrowed.",
                    )

            current_loop_time += timedelta(minutes=1)
            time.sleep(0.05)

        self.daily_summary(self.current_day)
        self.current_day += 1
        self.simulate_day()

    def daily_summary(self, day: int):
        most_popular_book, times_borrowed = self.most_popular_book()
        num_borrowed = sum(1 for book in self.library.books if book.borrowed)
        print(f"End of Day {day} summary: \n")
        print(f"{num_borrowed} books were borrowed.")
        print(
            f"The most popular book was: {most_popular_book}, borrowed {times_borrowed} times."
        )

        print(f"{self.unreturned_books()} books were not returned.")
        self.library.another_chance_to_return()

        time.sleep(5)


if __name__ == "__main__":
    library = Simulation()
    library.simulate_day()
