from flask import Flask, render_template
import sqlite3
connection = sqlite3.connect("users.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)")
cursor.execute("INSERT INTO user (username, email, password) VALUES ('admin', 'admin@gmail.com', 'admin')")
connection.commit()

connection.close()