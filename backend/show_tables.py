import sqlite3

# connect to database
conn = sqlite3.connect("memories.db")
cursor = conn.cursor()

def show_table(name):
    print(f"\n===== {name.upper()} TABLE STRUCTURE =====")
    cursor.execute(f"PRAGMA table_info({name})")
    print(cursor.fetchall())

    print(f"\n===== {name.upper()} TABLE ROWS =====")
    try:
        cursor.execute(f"SELECT * FROM {name}")
        print(cursor.fetchall())
    except:
        print("(No rows or table does not exist)")

print("\n==============================")
print("   PERSONAL MEMORY ASSISTANT")
print("     DATABASE INFORMATION")
print("==============================")

show_table("memories")
show_table("reminders")
show_table("images")

conn.close()

print("\n==============================")
print("         END OF REPORT")
print("==============================")
