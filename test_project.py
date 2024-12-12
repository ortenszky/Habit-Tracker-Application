from datetime import datetime, timedelta
from habit import Habit
from analyse import get_longest_streak, get_longest_streak_all_habits
from db import get_habits_list, get_habits_by_periodicity, get_counter, get_db
from db_example_db import preload_example_data
import sqlite3


def setup_test_database():
    """
    Setup a temporary in-memory database with preloaded example data for testing.
    """
    db = sqlite3.connect(':memory:')  # Use an in-memory database
    preload_example_data(db)  # Load example data into the in-memory database
    return db  # Return the database connection


def test_habit_creation():
    db = setup_test_database()


    # Create and save a new habit
    habit_name = "Test Habit Creation"
    habit_description = "This is a test habit for creation functionality."
    habit_periodicity = "daily"
    new_habit = Habit(name=habit_name, description=habit_description, periodicity=habit_periodicity)
    new_habit.save_to_db(db)

    # Retrieve the habit from the database
    cursor = db.cursor()
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
    db = setup_test_database()

    # Create a new habit
    habit_name = "Test Increment Habit"
    habit_description = "A habit to test increment functionality."
    habit_periodicity = "daily"
    new_habit = Habit(name=habit_name, description=habit_description, periodicity=habit_periodicity)
    habit_id = new_habit.save_to_db(db)

    # Increment the habit multiple times
    increment_dates = [
        datetime.now(),
        datetime.now() - timedelta(days=1),
        datetime.now() - timedelta(days=2),
    ]
    for increment_date in increment_dates:
        new_habit.increment(db, increment_date)

        # Retrieve the number of increments from the database
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM counters WHERE habit_id = ?', (habit_id,))
    count = cursor.fetchone()[0]

    # Assertions to validate the count of increments
    assert count == len(increment_dates) # 3

    db.close()


def test_habit_resetting():
    """
    Test resetting a habit to ensure its counters are cleared from the database.
    """
    db = setup_test_database()
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
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM counters WHERE habit_id = ?', (habit_id,))
    count_before_reset = cursor.fetchone()[0]
    assert count_before_reset == len(increment_dates) # 3

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
    db = setup_test_database()
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
    cursor = db.cursor()
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
    Test retrieving the list of habits from the preloaded database.
    """
    db = setup_test_database()

    # Retrieve the list of habits
    habits_list = get_habits_list(db)

    # Expected habits from db_example_db
    expected_habits = ["Play the guitar", "Make the bed", "Reading", "Cleaning", "Drink a protein shake"]

    # Assertions
    assert set(habits_list) == set(expected_habits)

    db.close()


def test_get_habits_by_periodicity():
    """
    Test retrieving habits filtered by periodicity using the preloaded database.
    """
    db = setup_test_database()

    # Retrieve daily habits
    daily_habits = get_habits_by_periodicity(db, "daily")
    expected_daily_habits = ["Play the guitar", "Make the bed", "Reading", "Drink a protein shake"]  # From db_example_db
    assert set(daily_habits) == set(expected_daily_habits)

    # Retrieve weekly habits
    weekly_habits = get_habits_by_periodicity(db, "weekly")
    expected_weekly_habits = ["Cleaning"]  # From db_example_db
    assert set(weekly_habits) == set(expected_weekly_habits)

    db.close()


def test_get_counter():
    """
    Test retrieving the counter (increment count) for a specific habit using the preloaded database.
    """
    db = setup_test_database()

    # Select a preloaded habit
    habit_name = "Reading"  # Preloaded habit from db_example_db
    expected_increment_count = 12  # Based on preloaded increment dates in db_example_db

    # Retrieve the counter for the habit
    counter = get_counter(db, habit_name)

    # Assertions
    assert counter == expected_increment_count

    # Test for a non-existent habit
    counter_non_existent = get_counter(db, "Non-Existent Habit")
    assert counter_non_existent == 0

    db.close()


def test_get_longest_streak():
    """
    Test the `get_longest_streak` function to ensure it correctly calculates the longest streak for a specific habit using the preloaded database.
    """
    db = setup_test_database()

    # Select a preloaded habit
    habit_name = "Reading"  # Preloaded habit from db_example_db
    expected_streak = 5  # Longest streak based on preloaded increment dates in db_example_db

    # Calculate the longest streak
    longest_streak = get_longest_streak(db, habit_name)

    # Assertions
    assert longest_streak == expected_streak, \
        f"Expected longest streak to be {expected_streak}, but got {longest_streak}."

    # Test for a habit with no increments
    habit_name_empty = "Empty Habit"
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO habits (name, description, periodicity, creation_date)
        VALUES (?, ?, ?, ?)
    ''', (habit_name_empty, "No increments", "daily", datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
    db.commit()

    # Calculate the longest streak for the empty habit
    longest_streak_empty = get_longest_streak(db, habit_name_empty)
    assert longest_streak_empty == 0, \
        f"Expected longest streak for an empty habit to be 0, but got {longest_streak_empty}."

    db.close()


def test_get_longest_streak_all_habits():
    """
    Test the `get_longest_streak_all_habits` function to ensure it correctly calculates the longest streak across all habits.
    """
    db = setup_test_database()

    # Expected longest streak from the preloaded data
    # Reading (daily): Increment dates include a 5-day streak: 11/11/2024 to 15/11/2024
    # Cleaning (weekly): Increment dates include a 3-week streak: 01/11/2024 to 17/11/2024
    expected_longest_streak = 21  # Longest streak is 21 consecutive days "01/11/2024 10:15:25", "08/11/2024 14:45:32", "11/11/2024 11:35:18"

    # Calculate the longest streak across all habits
    longest_streak = get_longest_streak_all_habits(db)

    # Assertions
    assert longest_streak == expected_longest_streak

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
