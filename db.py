import sqlite3
from habit import Habit


def get_db():
    """
        Initialize and return the database connection, creating tables if they do not exist.

        Returns:
        -------
        sqlite3.Connection
            The database connection object.
        """
    db = sqlite3.connect('main.db')
    cursor = db.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                periodicity TEXT NOT NULL,
                creation_date TEXT
            )
        ''')
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS counters (
                id INTEGER PRIMARY KEY,
                habit_id INTEGER NOT NULL,
                increment_date TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )
        ''')
    db.commit()
    return db


def get_habits_list(db):
    """
       Retrieve a list of all habit names from the database.

       Parameters:
       ----------
       db : sqlite3.Connection
           The database connection object.

       Returns:
       -------
       List[str]
           A list of habit names.
       """
    cursor = db.cursor()
    cursor.execute('SELECT name FROM habits')
    return [row[0] for row in cursor.fetchall()]


def get_habits_by_periodicity(db, periodicity):
    """
    Retrieve a list of habit names filtered by their periodicity.

    Parameters:
    ----------
    db : sqlite3.Connection
        The database connection object.
    periodicity : str
        The periodicity to filter by.

    Returns:
    -------
    List[str]
        A list of habit names matching the given periodicity.
    """
    cursor = db.cursor()
    cursor.execute('SELECT name habits WHERE periodicity = ?', (periodicity,))
    return[row[0]for row in cursor.fetchall()]


def get_counter(db, name):
    """
       Retrieve a Counter object for a given habit name.

       Parameters:
       ----------
       db : sqlite3.Connection
           The database connection object.
       name : str
           The name of the habit.

       Returns:
       -------
       Optional[Counter]
           A Counter object if the habit exists, otherwise None.
    """
    cursor = db.cursor()
    cursor.execute('SELECT * FROM habits WHERE name = ?', (name,))
    habit = cursor.fetchone()
    if habit:
        return Habit(name=habit[1], description=habit[2], periodicity=habit[3], id=habit[0])
    else:
        return None





