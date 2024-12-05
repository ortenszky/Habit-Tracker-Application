import sqlite3


def get_db():
    """
        Initialize and return the database connection, creating the tables habits and counters if they do not exist.

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
       Retrieve a list of all the habits from the database.

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
        The periodicity to filter by. (daily or weekly)

    Returns:
    -------
    List[str]
        A list of habit names matching the given periodicity.
    """
    cursor = db.cursor()
    cursor.execute('SELECT name FROM habits WHERE periodicity = ?', (periodicity,))
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
    cursor.execute('SELECT id FROM habits WHERE name = ?', (name,))
    habit = cursor.fetchone()
    if not habit:
        return 0

    habit_id = habit[0]

    cursor.execute('SELECT COUNT(*) FROM counters WHERE habit_id = ?', (habit_id,))
    count = cursor.fetchone()[0]

    return count
