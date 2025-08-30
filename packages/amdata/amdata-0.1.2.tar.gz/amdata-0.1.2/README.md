# AMdata

### A Simple Tool for SQLite Databases

This library was created by **Amjad** to simplify common database operations such as creating, inserting, and selecting data. It is designed to be intuitive and easy to use for all programmers.

**Note on Contributions:**
All changes and modifications to this library must be clearly documented in the source code files and a change log. The original creator, **Amjad**, and the tool's name, **AMdata**, must be explicitly and clearly mentioned in any derivative work.

---

## Installation

You can install the library easily using pip:
```bash
pip install amdata


Usage
1. Connecting to the database and creating a table

from amdata.db import DB

# Connect to a database file named 'my_app.db'
# If the file does not exist, it will be created automatically.
db = DB('my_app.db')

# Create a table named 'users' with two columns: 'username' and 'password'
db.create_table('users', username='TEXT', password='TEXT')

2. Inserting data

# Insert a new user record
db.insert('users', username='amjad', password='1234')

# Note: The check_duplicate method is integrated.
# This will prevent adding a duplicate username.

db.insert('users', username='amjad', password='5678')


3. Updating and Deleting data

# Update the password for user 'amjad'
db.update('users', "username = 'amjad'", password='5678')

# Delete a user record
db.delete('users', "username = 'amjad'")


4. Retrieving data


# Select all data from the 'users' table
all_users = db.select('users')
print(all_users)



