from db import get_db
from habit import Habit
from datetime import datetime

import sqlite3
from datetime import datetime

def preload_example_data():
    """
    Preload the database with predefined habits and their respective increment dates.
    """
    db = sqlite3.connect(':memory:')  # Create an in-memory database
    cursor = db.cursor()

    # Create tables if they do not exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
                        id INTEGER PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        periodicity TEXT NOT NULL,
                        creation_date TEXT
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS counters (
                        id INTEGER PRIMARY KEY,
                        habit_id INTEGER,
                        increment_date TEXT,
                        FOREIGN KEY (habit_id) REFERENCES habits (id)
                    )''')
    db.commit()

    # Clear existing data
    cursor.execute('DELETE FROM counters')
    cursor.execute('DELETE FROM habits')
    db.commit()

    # Example habits
    habits = [
        ("Play the guitar", "Practices scales for at least 10 minutes", "daily"),
        ("Make the bed", "Make the bed in the morning before leaving the house", "daily"),
        ("Reading", "Read 25 pages of a book", "daily"),
        ("Cleaning", "Clean the whole house", "weekly"),
    ]

    # Add habits to the database
    habit_ids = []
    for habit in habits:
        cursor.execute('''
               INSERT INTO habits (name, description, periodicity, creation_date)
               VALUES (?, ?, ?, ?)
           ''', (habit[0], habit[1], habit[2], datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        habit_ids.append(cursor.lastrowid)
    db.commit()

    # Define specific increment dates for each habit
    increment_dates = {
        habit_ids[0]: [  # Play the guitar
            "01/11/2024 19:45:23", "02/11/2024 20:30:12", "03/11/2024 21:15:48",
            "05/11/2024 19:10:35", "06/11/2024 20:50:07", "07/11/2024 21:25:54",
            "09/11/2024 20:00:16", "10/11/2024 19:35:49", "11/11/2024 20:45:31",
            "13/11/2024 21:05:42", "14/11/2024 20:20:08", "15/11/2024 19:55:26"
        ],
        habit_ids[1]: [  # Make the bed
            "01/11/2024 08:05:23", "02/11/2024 08:15:32", "03/11/2024 08:45:41",
            "06/11/2024 08:10:17", "07/11/2024 08:50:12", "10/11/2024 09:05:03",
            "13/11/2024 08:20:54", "14/11/2024 08:35:28", "15/11/2024 08:55:44",
            "17/11/2024 08:30:37", "18/11/2024 09:10:15"
        ],
        habit_ids[2]: [  # Reading
            "01/11/2024 16:15:13", "02/11/2024 17:25:45", "03/11/2024 18:35:22",
            "04/11/2024 20:45:37", "06/11/2024 21:25:59", "07/11/2024 22:50:16",
            "08/11/2024 16:10:44", "11/11/2024 17:35:21", "12/11/2024 19:40:08",
            "13/11/2024 22:50:32", "14/11/2024 23:05:57", "15/11/2024 21:30:41"
        ],
        habit_ids[3]: [  # Cleaning
            "01/11/2024 10:15:25", "08/11/2024 14:45:32", "11/11/2024 11:35:18",
            "28/11/2024 16:20:43"
        ]
    }

    # Insert increment dates for each habit
    for habit_id, dates in increment_dates.items():
        for date in dates:
            cursor.execute('''
                   INSERT INTO counters (habit_id, increment_date)
                   VALUES (?, ?)
               ''', (habit_id, date))  # Store date as a string
    db.commit()

    print("Example data preloaded successfully.")
    return db  # Return the database connection


