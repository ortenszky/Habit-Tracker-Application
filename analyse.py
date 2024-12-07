from datetime import datetime, timedelta

def get_longest_streak(db, habit_name):
    """
    Calculate the longest streak for a given habit, taking periodicity into account.
    """
    cursor = db.cursor()
    cursor.execute('''SELECT increment_date, periodicity FROM counters
                      INNER JOIN habits ON counters.habit_id = habits.id
                      WHERE habits.name = ?
                      ORDER BY increment_date ASC''', (habit_name,))
    rows = cursor.fetchall()

    if not rows:
        return 0

    # Determine periodicity from the first row
    periodicity = rows[0][1].lower()  # "daily" or "weekly"

    # Extract unique dates (ignore time) as a sorted list of datetime.date objects
    unique_days = sorted({datetime.strptime(row[0], "%d/%m/%Y %H:%M:%S").date() for row in rows})

    longest_streak = 0
    current_streak = 1

    # Define gap threshold based on periodicity
    gap_threshold = 1 if periodicity == "daily" else 7

    for i in range(1, len(unique_days)):
        if (unique_days[i] - unique_days[i - 1]).days <= gap_threshold:
            current_streak += 1
        else:
            longest_streak = max(longest_streak, current_streak)
            current_streak = 1

    # Final check for the last streak
    longest_streak = max(longest_streak, current_streak)

    # Convert weekly streak to days
    if periodicity == "weekly":
        longest_streak *= 7

    return longest_streak


def get_longest_streak_all_habits(db):
    """
    Calculate the longest streak across all habits, taking periodicity into account.
    """
    cursor = db.cursor()
    cursor.execute('''SELECT increment_date, periodicity FROM counters
                      INNER JOIN habits ON counters.habit_id = habits.id
                      ORDER BY increment_date ASC''')
    rows = cursor.fetchall()

    if not rows:
        return 0

    # Group increment dates by periodicity
    daily_dates = sorted({
        datetime.strptime(row[0], "%d/%m/%Y %H:%M:%S").date()
        for row in rows if row[1].lower() == "daily"
    })
    weekly_dates = sorted({
        datetime.strptime(row[0], "%d/%m/%Y %H:%M:%S").date()
        for row in rows if row[1].lower() == "weekly"
    })

    # Helper function to calculate streaks
    def calculate_streak(dates, is_daily):
        if not dates:
            return 0

        longest_streak = 1
        current_streak = 1
        gap_threshold = 1 if is_daily else 7

        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days <= gap_threshold:
                current_streak += 1
            else:
                longest_streak = max(longest_streak, current_streak)
                current_streak = 1

        # Final check for the last streak
        longest_streak = max(longest_streak, current_streak)

        # Convert weekly streak to days for consistent scoring
        if not is_daily:
            longest_streak *= 7

        return longest_streak

    # Calculate longest streaks for daily and weekly habits
    longest_daily_streak = calculate_streak(daily_dates, is_daily=True)
    longest_weekly_streak = calculate_streak(weekly_dates, is_daily=False)

    # Return the overall longest streak in days
    return max(longest_daily_streak, longest_weekly_streak)
