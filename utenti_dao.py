import sqlite3

def get_user_by_id(id):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti WHERE id = ?'
    cursor.execute(sql, (id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user

def get_nominativo_by_id(id):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT nominativo FROM utenti WHERE id = ?'
    cursor.execute(sql, (id,))
    nominativo = cursor.fetchone()

    cursor.close()
    conn.close()

    return nominativo


def get_user_by_email(email):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti WHERE email = ?'
    cursor.execute(sql, (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user


def add_user(utente):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO utenti(email, password, nominativo, ruolo) VALUES(?,?,?,?)'

    try:
        cursor.execute(sql, (utente['email'], utente['password'], utente['nominativo'], utente['ruolo']))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success
