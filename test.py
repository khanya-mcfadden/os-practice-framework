import sqlite3

# Connect to or create the database
connection = sqlite3.connect("your_database_name.db")

# Create a cursor object
cursor = connection.cursor()

# Create the 'students' table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        grade TEXT
    )
""")

# Insert data into the 'students' table
cursor.execute("""
    INSERT INTO students (name, age, grade) 
    VALUES ('Alice', 20, 'A')
""")

# Insert multiple rows at once
students = [
    ('Bob', 22, 'B'),
    ('Charlie', 19, 'C')
]
cursor.executemany("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", students)

# Commit the changes
connection.commit()

# Query data from the table
cursor.execute("SELECT * FROM students")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
connection.close()
