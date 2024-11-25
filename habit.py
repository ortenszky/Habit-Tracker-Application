from datetime import datetime


class Habit:
    """
        A class to represent a habit and manage its tracking in a database.

        Attributes:
            name (str): The name of the habit.
            description (str): A brief description of the habit.
            periodicity (str): The frequency of the habit (e.g., daily, weekly).
            id (int, optional): The database ID of the habit. Defaults to None.
            creation_date (str): The timestamp when the habit was created.
        """

    def __init__(self, name, description, periodicity, id=None):
        """
               Initialize a Habit instance.

               Parameters:
                   name (str): The name of the habit.
                   description (str): A brief description of the habit.
                   periodicity (str): The frequency of the habit.
                   id (int, optional): The database ID of the habit. Defaults to None.
               """
        self.name = name
        self.description = description
        self.periodicity = periodicity
        self.id = id
        self.creation_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def save_to_db(self, db):
        """
                Save the habit to the database.

                Parameter:
                    db: The database connection object.

                Returns:
                    int: The ID of the newly created habit in the database.
                """
        cursor = db.cursor()
        cursor.execute('''INSERT INTO habits (name, description, periodicity, creation_date)
                        VALUES (?, ?, ?, ?)''', (self.name, self.description, self.periodicity, self.creation_date))
        db.commit()
        self.id = cursor.lastrowid
        return self.id

    def increment(self, db, increment_date=None):
        """
              Increment the habit counter.

              Parameters:
                  db: The database connection object.
                  increment_date (datetime, optional): The date and time of the increment.
                                                       Defaults to the current time.

              Raises:
                  ValueError: If the habit has not been saved to the database.
              """
        if self.id is None:
            raise ValueError("Habit must be saved to the database before incrementing.")
        current_time = increment_date.strftime("%d/%m/%Y %H:%M:%S") if increment_date else datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S")
        cursor = db.cursor()
        cursor.execute('''INSERT INTO counters (habit_id, increment_date) VALUES (?, ?)''', (self.id, current_time))
        db.commit()

    def reset(self, db):
        """
                Reset the habit's counter.

                Parameters:
                    db: The database connection object.

                Raises:
                    ValueError: If the habit has not been saved to the database.
                """
        if self.id is None:
            raise ValueError("Habit must be saved to the database before resetting.")
        cursor = db.cursor()
        cursor.execute('''DELETE FROM counters WHERE habit_id = ?''', (self.id,))
        db.commit()

    def delete(self, db):
        """
                Delete the habit and its associated counters from the database.

                Parame:
                    db: The database connection object.

                Raises:
                    ValueError: If the habit has not been saved to the database.
                """
        if self.id is None:
            raise ValueError("Habit must be saved to the database before deleting.")
        cursor = db.cursor()
        cursor.execute('''DELETE FROM habits WHERE id = ?''', (self.id,))
        cursor.execute('''DELETE FROM counters WHERE habit_id = ?''', (self.id,))
        db.commit()
