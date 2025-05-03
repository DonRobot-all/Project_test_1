import sqlite3

conn = sqlite3.connect('project_db.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Dogs (
    dog_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    breed VARCHAR(50) NOT NULL,
    photo
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Owners (
    owner_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(50) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    residence VARCHAR(50)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Seekers (
    seeker_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    participation VARCHAR(50)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Searches (
    search_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    coordinates VARCHAR(50) NOT NULL,
    dog_id INTEGER,
    owner_id INTEGER,
    seeker_id INTEGER,
    FOREIGN KEY (dog_id) REFERENCES Dogs(dog_id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES Owners(owner_id) ON DELETE CASCADE,
    FOREIGN KEY (seeker_id) REFERENCES Seekers(seeker_id) ON DELETE CASCADE
);
''')


conn.commit()

conn.close()

print("Таблицы и данные успешно добавлены!")
