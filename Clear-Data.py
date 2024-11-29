import sqlite3


def clear_users_table():
    try:
        # Connect to the database
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Clear data from the users table
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM bookings")
        cursor.execute("DELETE FROM courses")

        # Commit the changes
        conn.commit()
        print("Data cleared from the users table successfully.")

    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    clear_users_table()
