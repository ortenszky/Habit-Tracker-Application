import sqlite3
from datetime import datetime, timedelta
from habit import Habit
from analyse import get_longest_streak, get_longest_streak_all_habits
from db import get_habits_list, get_habits_by_periodicity, get_counter


def setup_database():
    db = sqlite3.connect(':memory:')
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE habits (
                        id INTEGER PRIMARY KEY,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        periodicity TEXT NOT NULL,
                        creation_date TEXT
                    )''')
    cursor.execute('''CREATE TABLE counters (
                        id INTEGER PRIMARY KEY,
                        habit_id INTEGER,
                        increment_date TEXT,
                        FOREIGN KEY (habit_id) REFERENCES habits (id)
                    )''')
    return db

def test_habit_creation():
    db = setup_database()
    cursor = db.cursor()

    # Create and save a new habit
    habit_name = "Test Habit"
    habit_description = "This is a test habit"
    habit_periodicity = "daily"
    new_habit = Habit(name=habit_name, description=habit_description,periodicity=habit_periodicity)
    new_habit.save_to_db(db)

    # Retrieve the habit from the database
    cursor.execute('SELECT name, description, periodicity FROM habits WHERE name = ?', (habit_name,))
    result = cursor.fetchone()

    # Assertions to validate the habit creation
    assert result is not None
    assert result[0] == habit_name
    assert result[1] == habit_description
    assert result[2] == habit_periodicity

    db.close()


def test_habit_incrementation():
    """
    Test the incrementing of a habit and the correct storage of the increment in the database.
    """
    # Set up an in-memory database
    db = setup_database()
    cursor = db.cursor()

    # Create a new habit
    habit_name = "Test Increment Habit"
    habit_description = "A habit to test increment functionality."
    habit_periodicity = "daily"
    new_habit = Habit(name=habit_name, description=habit_description, periodicity=habit_periodicity)
    habit_id = new_habit.save_to_db(db)

    # Increment the habit
    increment_date = datetime.now()
    new_habit.increment(db, increment_date)

    # Retrieve the increment from the database
    cursor.execute('SELECT habit_id, increment_date FROM counters WHERE habit_id = ?', (habit_id,))
    result = cursor.fetchone()

    # Assertions to validate the increment
    assert result is not None
    assert result[0] == habit_id
    assert result[1] == increment_date.strftime("%d/%m/%Y %H:%M:%S")

    db.close()


def test_habit_resetting():
    """
    Test resetting a habit to ensure its counters are cleared from the database.
    """
    db = setup_database()
    cursor = db.cursor()
    habit_name = "Test Reset Habit"
    habit_description = "A habit to test reset functionality."
    habit_periodicity = "daily"
    new_habit = Habit(name=habit_name, description=habit_description, periodicity=habit_periodicity)
    habit_id = new_habit.save_to_db(db)

    # Increment the habit multiple times
    increment_dates = [
        datetime.now(),
        datetime.now() - timedelta(days=1),
        datetime.now() - timedelta(days=2)
    ]
    for date in increment_dates:
        new_habit.increment(db, date)

    # Verify increments are recorded
    cursor.execute('SELECT COUNT(*) FROM counters WHERE habit_id = ?', (habit_id,))
    count_before_reset = cursor.fetchone()[0]
    assert count_before_reset == len(increment_dates)

    # Reset the habit
    new_habit.reset(db)

    # Verify all counters for the habit are deleted
    cursor.execute('SELECT COUNT(*) FROM counters WHERE habit_id = ?', (habit_id,))
    count_after_reset = cursor.fetchone()[0]
    assert count_after_reset == 0

    db.close()


def test_habit_deletion():
    """
    Test deleting a habit and ensuring all associated counters are removed.
    """
    db = setup_database()
    cursor = db.cursor()
    habit_name = "Test Delete Habit"
    habit_description = "A habit to test deletion functionality."
    habit_periodicity = "daily"
    new_habit = Habit(name=habit_name, description=habit_description, periodicity=habit_periodicity)
    habit_id = new_habit.save_to_db(db)

    # Increment the habit multiple times
    increment_dates = [
        datetime.now(),
        datetime.now() - timedelta(days=1),
        datetime.now() - timedelta(days=2)
    ]
    for date in increment_dates:
        new_habit.increment(db, date)

        # Verify the habit and its increments exist in the database
    cursor.execute('SELECT COUNT(*) FROM habits WHERE id = ?', (habit_id,))
    habit_count = cursor.fetchone()[0]
    assert habit_count == 1

    cursor.execute('SELECT COUNT(*) FROM counters WHERE habit_id = ?', (habit_id,))
    increment_count = cursor.fetchone()[0]
    assert increment_count == len(increment_dates)

    # Delete the habit
    new_habit.delete(db)

    # Verify the habit and its increments are deleted
    cursor.execute('SELECT COUNT(*) FROM habits WHERE id = ?', (habit_id,))
    habit_count_after_delete = cursor.fetchone()[0]
    assert habit_count_after_delete == 0

    cursor.execute('SELECT COUNT(*) FROM counters WHERE habit_id = ?', (habit_id,))
    increment_count_after_delete = cursor.fetchone()[0]
    assert increment_count_after_delete == 0

    db.close()

def test_get_habits_list():
    """
    Test retrieving the list of habits from the database.
    """
    # Set up an in-memory database
    db = setup_database()

    # Define test habits
    test_habits = [
        Habit(name="Habit 1", description="Description for Habit 1", periodicity="daily"),
        Habit(name="Habit 2", description="Description for Habit 2", periodicity="weekly"),
        Habit(name="Habit 3", description="Description for Habit 3", periodicity="daily"),
    ]

    # Save habits to the database
    for habit in test_habits:
        habit.save_to_db(db)

    # Retrieve the list of habits
    habits_list = get_habits_list(db)

    # Assertions
    expected_habits = [habit.name for habit in test_habits]
    assert habits_list == expected_habits, \
        f"Expected habits list {expected_habits}, but got {habits_list}."

    # Cleanup
    db.close()


def test_get_habits_by_periodicity():
    """
    Test retrieving habits filtered by periodicity.
    """
    db = setup_database()
    cursor = db.cursor()

    test_habits = [
        Habit(name="Habit 1", description="Description for Habit 1", periodicity="daily"),
        Habit(name="Habit 2", description="Description for Habit 2", periodicity="weekly"),
        Habit(name="Habit 3", description="Description for Habit 3", periodicity="daily"),
        Habit(name="Habit 4", description="Description for Habit 4", periodicity="weekly"),
    ]
    for habit in test_habits:
        habit.save_to_db(db)

    # Retrieve daily habits
    daily_habits = get_habits_by_periodicity(db, "daily")
    expected_daily_habits = [habit.name for habit in test_habits if habit.periodicity == "daily"]
    assert daily_habits == expected_daily_habits

    # Retrieve weekly habits
    weekly_habits = get_habits_by_periodicity(db, "weekly")
    expected_weekly_habits = [habit.name for habit in test_habits if habit.periodicity == "weekly"]
    assert weekly_habits == expected_weekly_habits

    db.close()

def test_get_counter():
    """
    Test retrieving the counter (increment count) for a specific habit.
    """
    db = setup_database()
    cursor = db.cursor()

    # Create a new habit
    habit_name = "Test Counter Habit"
    habit_description = "A habit to test the get_counter function."
    habit_periodicity = "daily"
    new_habit = Habit(name=habit_name, description=habit_description, periodicity=habit_periodicity)

    # Save the habit to the database
    habit_id = new_habit.save_to_db(db)

    # Increment the habit a few times
    increment_dates = [
        datetime.now(),
        datetime.now() - timedelta(days=1),
        datetime.now() - timedelta(days=2),
    ]
    for date in increment_dates:
        new_habit.increment(db, date)

    # Retrieve the counter for the habit
    counter = get_counter(db, habit_name)

    # Assertions
    assert counter == len(increment_dates)

    # Test for a non-existent habit
    counter_non_existent = get_counter(db, "Non-Existent Habit")
    assert counter_non_existent == 0

    db.close()

def test_get_longest_streak():
    """
    Test the `get_longest_streak` function to ensure it correctly calculates the longest streak for a specific habit.
    """
    db = setup_database()
    habit_name = "Test Longest Streak Habit"
    habit_description = "A habit to test longest streak calculation."
    habit_periodicity = "daily"
    new_habit = Habit(name=habit_name, description=habit_description, periodicity=habit_periodicity)
    new_habit.save_to_db(db)

    # Define increment dates with gaps to simulate streaks
    increment_dates = [
        datetime.now() - timedelta(days=6),  # 6 days ago
        datetime.now() - timedelta(days=5),  # 5 days ago
        datetime.now() - timedelta(days=4),  # 4 days ago
        datetime.now() - timedelta(days=2),  # 2 days ago
        datetime.now() - timedelta(days=1),  # 1 day ago
    ]

    # Increment the habit on the specified dates
    for date in increment_dates:
        new_habit.increment(db, date)

    # Calculate the longest streak
    longest_streak = get_longest_streak(db, habit_name)

    # Expected streak: 3 consecutive days (6, 5, 4 days ago)
    expected_streak = 3

    # Assertions
    assert longest_streak == expected_streak

    # Test for a habit with no increments
    habit_name_empty = "Empty Habit"
    new_empty_habit = Habit(name=habit_name_empty, description="No increments", periodicity="daily")
    new_empty_habit.save_to_db(db)

    longest_streak_empty = get_longest_streak(db, habit_name_empty)
    assert longest_streak_empty == 0

    db.close()

def test_get_longest_streak_all_habits():
    """
       Test the `get_longest_streak_all_habits` function to ensure it correctly calculates the longest streak across all habits.
       """
    db = setup_database()
    habit_1 = Habit(name="Habit 1", description="Test habit 1", periodicity="daily")
    habit_2 = Habit(name="Habit 2", description="Test habit 2", periodicity="daily")
    habit_1.save_to_db(db)
    habit_2.save_to_db(db)

    # Define increment dates for both habits
    increment_dates_habit_1 = [
        datetime.now() - timedelta(days=6),  # 6 days ago
        datetime.now() - timedelta(days=5),  # 5 days ago
        datetime.now() - timedelta(days=4),  # 4 days ago
    ]
    increment_dates_habit_2 = [
        datetime.now() - timedelta(days=2),  # 2 days ago
        datetime.now() - timedelta(days=1),  # 1 day ago
    ]

    # Increment the habits on the specified dates
    for date in increment_dates_habit_1:
        habit_1.increment(db, date)

    for date in increment_dates_habit_2:
        habit_2.increment(db, date)

    # Calculate the longest streak across all habits
    longest_streak = get_longest_streak_all_habits(db)

    # Expected streak: 3 consecutive days (6, 5, 4 days ago) from Habit 1
    expected_streak = 3

    # Assertions
    assert longest_streak == expected_streak

    # Second test: reset the habits and check
    habit_1.reset(db)  # Clear counters for Habit 1
    habit_2.reset(db)  # Clear counters for Habit 2
    longest_streak_after_reset = get_longest_streak_all_habits(db)

    assert longest_streak_after_reset == 0

    db.close()








if __name__ == '__main__':
    test_habit_creation()
    test_habit_incrementation()
    test_habit_resetting()
    test_habit_deletion()
    test_get_habits_list()
    test_get_habits_by_periodicity()
    test_get_counter()
    test_get_longest_streak()
    test_get_longest_streak_all_habits()
    print('All tests passed!')


