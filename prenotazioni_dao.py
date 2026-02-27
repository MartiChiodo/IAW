import sqlite3

def nuova_prenotazione(pren):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO prenotazioni(id_cliente, id_annuncio, data, mod_visita, stato, fascia_oraria) VALUES (?,?,?,?,?,?)'
    cursor.execute(sql, (int(pren['id_cliente']), int(pren['id_annuncio']), str(pren['data']), str(pren['mod_visita']), str(pren['stato']), str(pren['fascia_oraria'])))
    
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
    
def get_prenotazioni_by_id_annuncio(id):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT prenotazioni.id, prenotazioni.id_annuncio, prenotazioni.data, prenotazioni.mod_visita, prenotazioni.stato, prenotazioni.fascia_oraria, utenti.nominativo, prenotazioni.motivazione FROM prenotazioni, utenti WHERE prenotazioni.id_cliente=utenti.id AND id_annuncio = ?'
    cursor.execute(sql, (id,))
    prenotazioni = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return prenotazioni

def accetta_prenotazione(id):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'UPDATE prenotazioni SET stato = ? WHERE id = ?;'
    cursor.execute(sql, (str("ACCETTATA"),id))
    
    
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

def rifiuta_prenotazione(id, mot):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'UPDATE prenotazioni SET stato = ?, motivazione=? WHERE id = ?;'
    cursor.execute(sql, (str("RIFIUTATA"), str(mot), id))
    
    
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

def get_prenotazioni_by_id(id):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM prenotazioni WHERE id = ?'
    cursor.execute(sql, (id,))
    pren = cursor.fetchone()

    cursor.close()
    conn.close()
    
    return pren

def get_prenotazioni_by_id_cliente(id_cliente):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT prenotazioni.id_annuncio, prenotazioni.data, prenotazioni.fascia_oraria, prenotazioni.mod_visita, prenotazioni.stato, prenotazioni.motivazione, annunci.titolo, annunci.id, utenti.nominativo, annunci.indirizzo FROM prenotazioni, annunci, utenti WHERE prenotazioni.id_annuncio=annunci.id AND prenotazioni.id_cliente=utenti.id AND id_cliente = ?'
    cursor.execute(sql, (id_cliente,))
    pren = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return pren

def verifica_non_duplica_prenotazioni(user_id, id_annuncio):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT stato FROM prenotazioni WHERE id_cliente = ? AND id_annuncio = ? AND  (stato=? OR stato=?)'
    cursor.execute(sql, (user_id, id_annuncio, "ACCETTATA", "RICHIESTA"))
    stato = cursor.fetchone()

    cursor.close()
    conn.close()
    
    return stato

def verifica_diponibilita_slot_orario(data, orario, id_annuncio):
    conn = sqlite3.connect('db/database_esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM prenotazioni WHERE id_annuncio = ? AND data = ? AND fascia_oraria = ? AND stato=?'
    cursor.execute(sql, (id_annuncio, data, orario, "ACCETTATA"))
    disp = cursor.fetchall()

    cursor.close()
    conn.close()
    
    disponibilita = False
    if disp == None or disp==[]:
        disponibilita = True
    
    return disponibilita
