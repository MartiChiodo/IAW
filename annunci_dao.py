import sqlite3

def get_annunci_per_prezzo():
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT annunci.id, titolo, indirizzo, tipo, num_locali,id_locatore, utenti.nominativo, descrizione, arredata, prezzo, disponibile, foto1, foto2, foto3, foto4, foto5 FROM annunci, utenti WHERE utenti.id = annunci.id_locatore AND disponibile=? ORDER BY prezzo DESC'
    cursor.execute(sql, ("SI",))
    annunci = cursor.fetchall()

    cursor.close()
    conn.close()

    return annunci

def get_annunci_per_numlocali():
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT  annunci.id, titolo, indirizzo, tipo, num_locali,id_locatore, utenti.nominativo, descrizione, arredata, prezzo, disponibile, foto1, foto2, foto3, foto4, foto5 FROM annunci, utenti WHERE utenti.id=annunci.id_locatore AND disponibile=? ORDER BY num_locali ASC'
    cursor.execute(sql, ("SI",))
    annunci = cursor.fetchall()

    cursor.close()
    conn.close()

    return annunci


def add_annuncio(ann):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO annunci(titolo, indirizzo, tipo, num_locali, id_locatore, descrizione, arredata, disponibile, prezzo, foto1, foto2, foto3, foto4, foto5) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    cursor.execute(sql, (str(ann['titolo']), str(ann['indirizzo']), str(ann['tipo']), int(ann['num_locali']), int(ann['id_locatore']),  str(ann['descrizione']), str(ann['arredata']), str(ann['disponibile']), float(ann['prezzo']), str(ann['foto1']), str(ann['foto2']), str(ann['foto3']), str(ann['foto4']), str(ann['foto5'])))
    
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def get_annunci_visibili_by_id_locatore(id_loc):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT  annunci.id, titolo, indirizzo, tipo, num_locali,id_locatore, utenti.nominativo, descrizione, arredata, disponibile, prezzo, foto1, foto2, foto3, foto4, foto5 FROM annunci, utenti WHERE utenti.id=annunci.id_locatore AND id_locatore = ? AND disponibile = ?'
    cursor.execute(sql, (id_loc, "SI"))
    annunci = cursor.fetchall()

    cursor.close()
    conn.close()

    return annunci

def get_annunci_nascosti_by_id_locatore(id_loc):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT  annunci.id, titolo, indirizzo, tipo, num_locali,id_locatore, utenti.nominativo, descrizione, arredata, disponibile, prezzo, foto1, foto2, foto3, foto4, foto5 FROM annunci, utenti WHERE utenti.id=annunci.id_locatore AND id_locatore = ? AND disponibile = ?'
    cursor.execute(sql, (id_loc, "NO"))
    annunci = cursor.fetchall()

    cursor.close()
    conn.close()

    return annunci


def nascondi_annuncio(id):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'UPDATE annunci SET disponibile = ? WHERE id = ?;'
    cursor.execute(sql, (str("NO"), id))
    
    
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def rendi_annuncio_disponibile(id):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'UPDATE annunci SET disponibile = ? WHERE id = ?;'
    cursor.execute(sql, (str("SI"), id))
    
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success


def get_annuncio_by_id(id_annuncio):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT  annunci.id, titolo, indirizzo, tipo, num_locali, id_locatore, utenti.nominativo, descrizione, arredata, disponibile, prezzo, foto1, foto2, foto3, foto4, foto5 FROM annunci, utenti WHERE utenti.id=annunci.id_locatore AND annunci.id = ?'
    cursor.execute(sql, (id_annuncio,))
    ann = cursor.fetchone()

    cursor.close()
    conn.close()

    return ann

def modifica_info_annuncio(ann, id_annuncio):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'UPDATE annunci SET titolo=?, tipo=?, num_locali=?, id_locatore=?, descrizione=?, arredata=?, disponibile=?, prezzo=? WHERE id = ?;'
    cursor.execute(sql, (str(ann['titolo']),  str(ann['tipo']), int(ann['num_locali']), int(ann['id_locatore']), str(ann['descrizione']), str(ann['arredata']), str(ann['disponibile']), float(ann['prezzo']), id_annuncio))
    
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success


def modifica_foto(id_annuncio, foto):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'UPDATE annunci SET foto1=?, foto2=?, foto3=?, foto4=?, foto5=? WHERE id = ?;'
    cursor.execute(sql, (foto['foto1'], foto['foto2'], foto['foto3'], foto['foto4'], foto['foto5'], id_annuncio))
    
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success