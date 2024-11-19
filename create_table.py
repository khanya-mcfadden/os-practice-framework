from flask import Flask, render_template
import sqlite3
connection = sqlite3.connect("users.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL, email TEXT NOT NULL, password TEXT NOT NULL, admin BOOLEAN NOT NULL DEFAULT FALSE)") # Create a table with the name users
cursor.execute("INSERT INTO users (username, email, password, admin) VALUES ('admin', 'admin@gmail.com', '123456789', TRUE)")

cursor.execute("CREATE TABLE IF NOT EXISTS bookings (booking_id INTEGER PRIMARY KEY, courses text, username text, date TEXT, time TEXT, FOREIGN KEY(username) REFERENCES users(username))")
connection.commit()

connection.close()