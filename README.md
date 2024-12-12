# Habit Tracker CLI Application

Introducing my Habit Tracker Application project for the Object-Oriented and Functional Programming with Python Course at the IU International University of Applied Sciences. 
It is a simple and easy to use command-line interface (CLI) application to help users track and analyse their daily and weekly habits. This app allows users to manage their habits effectively and analyse their streaks, helping them to build consistency and achieve their goals.

## Installation

1. Make sure you have Python 3.13= installed on your computer.
2. Download all the files from GitHub:
https://github.com/ortenszky/Habit-Tracker-Application
3. Install the required libraries with the following command:
```shell
pip install -r requirements.txt
```

## Usage Guide
1. Run `python main.py` to start the App.
2. Loading up for the first time the database will be empty so the app will ask if the user wants to have some predefined habits and 4 weeks of example data. Choose Y/n (yes or no) when the question "The database is empty. Do you want to load the example data?" pops up.
3. Throughout the application use the arrow keys to navigate and choose an option by pressing enter.

The application is structured into two main sections: **Manage Habits** and **Analyse Habits**

### Main Menu
**Choose an action:**
- Manage Habits
- Analyze Habits
- Exit

### Manage Habits
- **View All Habits:**
        Displays all currently tracked habits.
- **Filter Habits by Periodicity:**
        View habits grouped as daily or weekly.
- **Add a New Habit:**
        Create a new habit by specifying its name, description, and periodicity (daily or weekly).
- **Check Off Habit:**
        Mark a habit as completed for the current date and time.
- **Reset Habit:**
        Clear all progress for a selected habit.
- **Delete Habit:**
        Permanently delete a habit and its associated data.

### Analyse Habits

- **Get Longest Streak (Specific Habit):**
        Calculate the longest streak for a selected habit.
- **Get Longest Streak (All Habits):**
        Identify the habit with the longest streak across all habits.

### Exit
To exit the application select the "Exit" option.

## Testing
This app includes unit tests to ensure all functionalities work as expected.

### Test Coverage
- Habit creation, incrementing, resetting, and deletion.
- Analytics functions, including streak calculations.
- Integration with the database.

Run the test using the following command: 
```shell
python pytest .
```
## Future Improvements
- Add monthly and custom periodicity.
- Visualize streak data using graphs.
- Add more analytic functions.
- Add the option to login as a user so more people can track their habits on the same device without getting their habits mixed up.
- Add a Graphic User Interface