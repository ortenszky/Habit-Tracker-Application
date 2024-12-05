import questionary
from datetime import datetime
from db import get_habits_list, get_habits_by_periodicity
from habit import Habit
from analyse import get_longest_streak, get_longest_streak_all_habits
from db_example_db import preload_example_data
import sqlite3



def is_database_empty(db):
    """
    Check if the database is empty by verifying if any habits exist.
    """
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM habits")
    result = cursor.fetchone()
    return result[0] == 0  # Returns True if there are no habits


def main():
    db_path = "main.db"
    db = sqlite3.connect(db_path)

    # Check if the database is empty
    if is_database_empty(db):
        load_data = questionary.confirm(
            "The database is empty. Do you want to load the example data?"
        ).ask()

        if load_data:
            preload_example_data(db_path)
            print("\nExample data has been loaded successfully.")
        else:
            print("\nStarting with an empty database.")

    print("Welcome to the Habit Tracker App!")
    main_menu(db)


def main_menu(db):
    while True:
        choice = questionary.select(
            "Choose an action:",
            choices=[
                "Manage habits",
                "Analyse habits",
                "Exit",
            ]
        ).ask()

        if choice == "Manage habits":
            manage_habits_menu(db)
        elif choice == "Analyse habits":
            analyse_habits_menu(db)
        elif choice == "Exit":
            print("Thank you for using Habits! Goodbye!")
            break


def manage_habits_menu(db):
    while True:
        choice = questionary.select(
            "Habit Management Options",
            choices=[
                "View all habits",
                "View habits by periodicity",
                "Add a new habit",
                "Check off habit",
                "Reset habit",
                "Delete habit",
                "Back to Main Menu",
            ],
        ).ask()

        if choice == "View all habits":
            view_all_habits(db)
        elif choice == "View habits by periodicity":
            habits_by_periodicity(db)
        elif choice == "Add a new habit":
            add_habit(db)
        elif choice == "Check off habit":
            increment_habit(db)
        elif choice == "Reset habit":
            reset_habit(db)
        elif choice == "Delete habit":
            delete_habit(db)
        elif choice == "Back to Main Menu":
            break


def analyse_habits_menu(db):
    while True:
        choice = questionary.select(
            "Habit Analyse Options:",
            choices=[
                "Get longest streak (specific habit)",
                "Get longest streak (all habits)",
                "Back to Main Menu",
            ],
        ).ask()

        if choice == "Get longest streak (specific habit)":
            longest_streak_specific(db)
        elif choice == "Get longest streak (all habits)":
            longest_streak_all(db)
        elif choice == "Back to Main Menu":
            break


def view_all_habits(db):
    habits = get_habits_list(db)
    if habits:
        print("\nYour current habits are:")
        for habit in habits:
            print(f"- {habit}")
    else:
        print("\nThere are no habits found")


def habits_by_periodicity(db):
    periodicity = questionary.select(
        "Select periodicity to filter habits:",
        choices=["daily", "weekly"],
    ).ask()

    try:
        habits = get_habits_by_periodicity(db, periodicity)
        if habits:
            print(f"\nHabits with {periodicity} periodicity:")
            for habit in habits:
                print(f"- {habit}")
        else:
            print(f"\nNo habits found with {periodicity} periodicity.")
    except Exception as e:
        print(f"\nError: {e}")


def add_habit(db):
    name = questionary.text("Enter the name of the habit:").ask()
    description = questionary.text("Enter a brief description of the habit:").ask()
    periodicity = questionary.select(
        "Select the periodicity of the habit:",
        choices=["daily", "weekly"]
    ).ask()

    new_habit = Habit(name=name, description=description, periodicity=periodicity)
    try:
        new_habit.save_to_db(db)
        print(f"\nHabit '{name}' has been saved successfully.")
    except Exception as e:
        print(f"\nError: {e}")


def increment_habit(db):
    habits = get_habits_list(db)
    if not habits:
        print("\nThere are no habits found")
        return

    habit_name = questionary.select("Select a habit to check off:", choices=habits).ask()

    try:
        habit = Habit.get_by_name(db, habit_name)
        increment_date = datetime.now()
        habit.increment(db, increment_date)
        print(f"\nHabit '{habit_name}' has been checked off successfully.")
    except Exception as e:
        print(f"\nError: {e}")


def reset_habit(db):
    habits = get_habits_list(db)
    if not habits:
        print("\nThere are no habits found")
        return

    habit_name = questionary.select("Select a habit to reset:", choices=habits).ask()
    try:
        habit = Habit.get_by_name(db, habit_name)
        habit.reset(db)
        print(f"\nHabit '{habit_name}' has been reset successfully.")
    except Exception as e:
        print(f"\nError: {e}")


def delete_habit(db):
    habits = get_habits_list(db)
    if not habits:
        print("\nNo habits found.")
        return

    habit_name = questionary.select("Select a habit to delete:", choices=habits).ask()
    confirm = questionary.confirm(f"Are you sure you want to delete '{habit_name}' habit?").ask()

    if confirm:
        try:
            habit = Habit.get_by_name(db, habit_name)
            habit.delete(db)
            print(f"\nHabit '{habit_name}' has been deleted successfully.")
        except Exception as e:
            print(f"\nError: {e}")
    else:
        print("\nDeleting habits cancelled.")
        return


def longest_streak_specific(db):
    habits = get_habits_list(db)
    if not habits:
        print("\nNo habits found.")
        return

    habit_name = questionary.select("Select a habit:", choices=habits).ask()
    try:
        streak = get_longest_streak(db, habit_name)
        print(f"\nThe longest streak for '{habit_name}' is {streak} days.")
    except Exception as e:
        print(f"\nError: {e}")


def longest_streak_all(db):
    try:
        streak = get_longest_streak_all_habits(db)
        print(f"\nThe longest streak for all habits is {streak} days.")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
