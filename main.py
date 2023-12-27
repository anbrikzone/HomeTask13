import sqlite3

class Database:
    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name VARCHAR(40),
                last_name VARCHAR(40),
                age INTEGER,
                birt_date DATE,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.connection.commit()


class BaseModel:
    def __init__(self, db, table):
        self.db = db
        self.cursor = db.cursor
        self.table = table

    def get(self, id):
        self.cursor.execute('SELECT * FROM {} WHERE id = ?'.format(self.table), (id,))
        return self.cursor.fetchone()

    def get_all(self):
        self.cursor.execute('SELECT * FROM {}'.format(self.table))
        return self.cursor.fetchall()

    def delete(self, id):
        self.cursor.execute('DELETE FROM {} WHERE id = ?'.format(self.table), (id,))
        self.db.connection.commit()

    def save(self, data):
        if 'id' in data:
            self.cursor.execute('UPDATE {} SET '.format(self.table) + ', '.join(['{} = ?'.format(key) for key in data.keys()]) + ' WHERE id = ?', tuple(data.values()) + (data['id'],))
        else:
            self.cursor.execute('INSERT INTO {} ('.format(self.table) + ', '.join(data.keys()) + ') VALUES (' + ', '.join(['?'] * len(data)) + ')', tuple(data.values()))
        self.db.connection.commit()


class Users(BaseModel):
    def __init__(self, db):
        super().__init__(db, 'users')

    def get_by_email(self, email):
        self.cursor.execute('SELECT * FROM {} WHERE email = ?'.format(self.table), (email,))
        return self.cursor.fetchone()

    def get_user_with_info(self, id):
        self.cursor.execute(
            'SELECT users.username, users.email, user_info.first_name, user_info.last_name, user_info.age, user_info.birth_date FROM {} JOIN user_info ON users.id = user_info.user_id WHERE users.id = ?'.format(self.table), (id,)
        )
        return self.cursor.fetchone()


class UserInfo(BaseModel):
    def __init__(self, db):
        super().__init__(db, 'user_info')


db = Database('db.sqlite3')
users = Users(db)

print(users.get_user_with_info(1))

print(users.get_all())
