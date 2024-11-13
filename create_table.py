from flask import Flask, render_template
import sqlite3
connection = sqlite3.connect("users.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)")
cursor.execute("INSERT INTO users (username, email, password) VALUES ('admin', 'admin@gmail.com', 'oR!LE?QTM@_GXC95Yl1')")
connection.commit()

connection.close()