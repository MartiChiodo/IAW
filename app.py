#import module
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date, datetime, timedelta

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import annunci_dao, utenti_dao, prenotazioni_dao

from models import User

# Import the Image module from the PIL (Python Imaging Library) package. Used to preprocess the images uploaded by the users. 
from PIL import Image
FOTO_IMG_WIDTH = 300


# create the application
app = Flask(__name__)

app.config['SECRET_KEY'] = 'Caterina'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):

    db_user = utenti_dao.get_user_by_id(user_id)
    if db_user is not None:
        user = User(id=db_user['id'], email=db_user['email'],	password=db_user['password'], nominativo=db_user['nominativo'], ruolo=db_user['ruolo'])
    else:
        user = None

    return user

# define the homepage: di default si entra nella pagina ordinata per prezzo decrescente
@app.route('/')
def home_prezzo():
    annunci_prezzo = annunci_dao.get_annunci_per_prezzo()

    return render_template('home_prezzo.html', annunci=annunci_prezzo)


@app.route('/home2')
def home_numlocali():
    annunci_numlocali = annunci_dao.get_annunci_per_numlocali()
       
        
    return render_template('home_numlocali.html', annunci=annunci_numlocali)


#pagina del singolo anuncio  
@app.route('/annunci/<int:id>')
def single_annuncio(id):
    annuncio_db = annunci_dao.get_annuncio_by_id(id)

    #mi salvo la data odierna e quella fra sette giorni, queste due date mi serviranno per impostare il max e il min nel form per le prenotazioni
    today = date.today()
    possibili_date = []
    slot_orari = ["9-12", "12-14", "14-17", "17-20"]    
    
    #creo una lista con le possibili fasce orario: ogni indice contiene una lista con la data e lo slot orario e T/F
    for k in range(1,8):
        for slot in slot_orari:
            data = (today+timedelta(days=k)).strftime('%d/%m/%Y')
            disp = prenotazioni_dao.verifica_diponibilita_slot_orario(data, slot, id)
            possibili_date.append([data, slot, disp])
    
    
    return render_template('single_annuncio.html', annuncio=annuncio_db, possibili_date=possibili_date)


#gestione delle iscrizioni
@app.route('/iscriviti')
def iscriviti():
    return render_template('iscriviti.html')

@app.route('/iscriviti', methods=['POST'])
def iscriviti_post():

    nuovo_utente_form = request.form.to_dict()
    
    #verifico che i dati inseriti nel form non siano nulli o solo spazi
    if nuovo_utente_form.get('email').isspace() or nuovo_utente_form.get('email')=="":
        flash('Inserire una email valida', 'danger')
        return redirect(url_for('iscriviti'))
    if nuovo_utente_form.get('password').isspace() or nuovo_utente_form.get('password')=="":
        flash('Inserire una password valida', 'danger')
        return redirect(url_for('iscriviti'))
    if nuovo_utente_form.get('nominativo').isspace() or nuovo_utente_form.get('nominativo')=="":
        flash('Inserire un nominativo valido', 'danger')
        return redirect(url_for('iscriviti'))
    if nuovo_utente_form.get('ruolo') != 'LOCATORE' and nuovo_utente_form.get('ruolo') != 'CLIENTE' :
        flash('Scegliere un ruolo', 'danger')
        return redirect(url_for('iscriviti'))
    

    user_in_db = utenti_dao.get_user_by_email(nuovo_utente_form.get('email'))

    if user_in_db:
        flash('C\'è già un utente registrato con questa email', 'danger')
        return redirect(url_for('iscriviti'))
    else:        
        nuovo_utente_form['password'] = generate_password_hash(nuovo_utente_form.get('password'))
        
        success = utenti_dao.add_user(nuovo_utente_form)

        if success:
            flash('Utente creato correttamente', 'success')
            return redirect(url_for('home_prezzo'))
        else:
            flash('Errore nella creazione del utente: riprova!', 'danger')

    return redirect(url_for('home_prezzo'))


#gestione dei login e dei logout
@app.route('/login', methods=['POST'])
def login():

  utente_form = request.form.to_dict()

  utente_db = utenti_dao.get_user_by_email(utente_form['email'])

  if not utente_db or not check_password_hash(utente_db['password'], utente_form['password']):
    flash('Credenziali non valide, riprova', 'danger')
    return redirect(url_for('home_prezzo'))
  else:
    new = User(id=utente_db['id'], email=utente_db['email'], password=utente_db['password'], nominativo=utente_db['nominativo'], ruolo=utente_db['ruolo'] )
    login_user(new, True)
    flash('Bentornato/a ' + utente_db['nominativo'] + '!', 'success')

    return redirect(url_for('home_prezzo'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_prezzo'))


#pagine personali degli utenti
@app.route('/utenti/<int:id>')
@login_required
def profilo_utente(id): 
    utente_db = utenti_dao.get_user_by_id(id)
    
    if utente_db['ruolo']=="CLIENTE":
        prenotazioni_fatte = prenotazioni_dao.get_prenotazioni_by_id_cliente(current_user.id)
        return render_template('profilo_utente.html', utente= utente_db, prenotazioni_fatte=prenotazioni_fatte)
    elif utente_db['ruolo']=="LOCATORE":
        
        annunci_visibili_by_loc = annunci_dao.get_annunci_visibili_by_id_locatore(id)
        annunci_nascosti_by_loc = annunci_dao.get_annunci_nascosti_by_id_locatore(id)
        
        prenotazioni_ric={}
        for elem in annunci_visibili_by_loc:
            prenotazione = prenotazioni_dao.get_prenotazioni_by_id_annuncio(elem['id'])
            if prenotazione:
                prenotazioni_ric[elem['id']] = prenotazione
                
        for elem in annunci_nascosti_by_loc:
            prenotazione = prenotazioni_dao.get_prenotazioni_by_id_annuncio(elem['id'])
            if prenotazione:
                prenotazioni_ric[elem['id']] = prenotazione
                
                
        prenotazioni_fatte = prenotazioni_dao.get_prenotazioni_by_id_cliente(current_user.id)
        
        return render_template('profilo_utente.html', utente= utente_db, annunci_visibili=annunci_visibili_by_loc, annunci_nascosti = annunci_nascosti_by_loc, prenotazioni_ricevute=prenotazioni_ric, prenotazioni_fatte=prenotazioni_fatte)
    

#inserimento di un nuovo annuncio
@app.route('/annunci/new', methods=['POST'])
@login_required
def new_annuncio():
    
    if str(current_user.ruolo) != "LOCATORE":
        flash('Non sei autorizzato a pubblicare un nuovo annuncio', 'danger')
        return redirect(url_for('home_prezzo'))
    
    newAnn_form = request.form.to_dict()
    
    #controllo che i campi non siano vuoti o composti solo da spazi
    if newAnn_form['titolo'] == '':
        app.logger.error('Il titolo dell\'annuncio non può essere vuoto!')
        flash('Il titolo dell\'annuncio non può essere vuoto!', 'warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    elif newAnn_form['titolo'].isspace():
        app.logger.error('Il titolo dell\'annuncio non può essere composto solo da spazi!')
        flash('Il titolo dell\'annuncio non può essere composto solo da spazi!', 'warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if newAnn_form['indirizzo'] == '':
        app.logger.error('L\'indirizzo dell\'annuncio non può essere vuoto!')
        flash('L\'indirizzo dell\'annuncio non può essere vuoto!', 'warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    elif newAnn_form['indirizzo'].isspace():
        app.logger.error('L\'indirizzo dell\'annuncio non può essere composto solo da spazi!')
        flash('L\'indirizzo dell\'annuncio non può essere composto solo da spazi!', 'warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if newAnn_form['tipo'] != 'loft' and newAnn_form['tipo'] != 'appartamento' and newAnn_form['tipo'] != 'villa' and newAnn_form['tipo'] != 'casa indipendente':
        app.logger.error('Selezionare il tipo di abitazione!')
        flash('Selezionare il tipo di abitazione!','warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if int(newAnn_form['num_locali']) < 1 or int(newAnn_form['num_locali']) > 5:
        app.logger.error('Selezionare il numero di locali!')
        flash('Selezionare il numero di locali!', 'warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if newAnn_form['descrizione'] == '':
        app.logger.error('La descrizione dell\'annuncio non può essere vuota!')
        flash('La descrizione dell\'annuncio non può essere vuota!', 'warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    elif newAnn_form['descrizione'].isspace():
        app.logger.error('La descrizione dell\'annuncio non può essere composta solo da spazi!')
        flash('La descrizione dell\'annuncio non può essere composta solo da spazi!','warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if newAnn_form['arredata'] != 'SI' and newAnn_form['arredata'] != 'NO':
        app.logger.error('Indica se l\'abitazione è arredata!')
        flash('Indica se l\'abitazione è arredata!','warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if newAnn_form['prezzo-unità'] == '':
        app.logger.error('Inserisci un prezzo per l\'annuncio!')
        flash('Inserisci un prezzo per l\'annuncio!','warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if newAnn_form['disponibile']!='SI' and newAnn_form['disponibile']!='NO':
        app.logger.error('Errore nella compilazione dei campi.')
        flash('Scegli se render l\'annuncio disponibile.','warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    
    
    img1 = request.files['foto1']
    img2 = request.files['foto2']
    img3 = request.files['foto3']
    img4 = request.files['foto4']
    img5 = request.files['foto5']
    img=[img1, img2, img3, img4, img5]
    imgnonvuote = []
    k=0 
    for elem in img:
        if elem:
            # Open the user-provided image using the Image module
            try:
                picture = Image.open(elem)
            except:
                app.logger.info('Sono accettati solo file in formato png, jpeg e jpg.')
                flash('Sono accettati solo file in formato png, jpeg e jpg.', 'warning')        
                return redirect(url_for('profilo_utente', id=current_user.id))     
            # Get the width and height of the image
            width, height = picture.size
            # Calculate the new height while maintaining the aspect ratio based on the desired width
            new_height = height/width * FOTO_IMG_WIDTH
            # Define the size for thumbnail creation with the desired width and calculated height
            size = FOTO_IMG_WIDTH, new_height
            picture.thumbnail(size, Image.Resampling.LANCZOS)
            # Extracting file extension from the image filename
            ext = elem.filename.split('.')[-1]
            # Getting the current timestamp in seconds
            secondi = int(datetime.now().timestamp()) 
            # Associo un nome unico alle foto
            picture.save('static/@foto'+str(k) + str(current_user.id).lower() + '-' + str(secondi) + '.' + ext)
            imgnonvuote.append('@foto'+str(k) + str(current_user.id).lower() + '-' + str(secondi) + '.' + ext)  
            k+=1    
            
    #ciclo sulle variabili della tabella in modo che le immagini siano nelle prime variabili libere per non avere problemi con il carosello
    fotoDEF = {'foto1':'', 'foto2':'', 'foto3':'', 'foto4':'','foto5':''}
    for foto in imgnonvuote:
        if fotoDEF['foto1']=='':
            fotoDEF['foto1']=foto
        elif fotoDEF['foto2']=='':
            fotoDEF['foto2']=foto
        elif fotoDEF['foto3']=='':
            fotoDEF['foto3']=foto
        elif fotoDEF['foto4']=='':
            fotoDEF['foto4']=foto
        elif fotoDEF['foto5']=='':
            fotoDEF['foto5']=foto   
        
        
    prezzo = float(str(newAnn_form['prezzo-unità'])+'.'+str(newAnn_form['prezzo-centesimi']))
    new_annuncio={'titolo':newAnn_form['titolo'], 'indirizzo':newAnn_form['indirizzo'], 'tipo':newAnn_form['tipo'], 'num_locali':int(newAnn_form['num_locali']), 'descrizione':newAnn_form['descrizione'], 'arredata':newAnn_form['arredata'], 'disponibile': newAnn_form['disponibile'],'prezzo':prezzo ,'foto1':fotoDEF['foto1'],'foto2':fotoDEF['foto2'] , 'foto3':fotoDEF['foto3'], 'foto4':fotoDEF['foto4'], 'foto5':fotoDEF['foto5']}
    new_annuncio['id_locatore'] = int(current_user.id)  
    
    success = annunci_dao.add_annuncio(new_annuncio)
        
    if success:
        app.logger.info('Annuncio creato correttamente')
        flash('Annuncio creato correttamente','success')
    else:
        app.logger.error('Errore nella creazione dell\'annuncio: riprova!')
        flash('Errore nella creazione dell\'annuncio: riprova!','warning')

    return redirect(url_for('home_prezzo'))


#gestisco ile modifiche negli annunci
@app.route('/annunci/nascondi/<int:id>')
@login_required
def nascondi_annuncio(id):
    
    annuncio_db=annunci_dao.get_annuncio_by_id(id)
    if str(current_user.ruolo) != "LOCATORE":
        flash('Non sei autorizzato a modificare lo stato di un annuncio', 'danger')
        return redirect(url_for('profilo_utente', id= current_user.id))
    if int(current_user.id) != annuncio_db['id_locatore']:
        flash('Non sei autorizzato a modificare lo stato di questo annuncio', 'danger')
        return redirect(url_for('profilo_utente', id= current_user.id))
    
    success = annunci_dao.nascondi_annuncio(id)
    
    if success:
        flash('L\'annuncio è stato nascosto correttamente!', 'success')
        return redirect(url_for('profilo_utente', id= current_user.id))
    else:
        flash('C\'è stato un problema con la sua richiesta, riprova!', 'warning')
        return redirect(url_for('profilo_utente', id= current_user.id))
        
@app.route('/annunci/mostra/<int:id>')
@login_required
def mostra_annuncio(id):
    
    annuncio_db=annunci_dao.get_annuncio_by_id(id)
    if str(current_user.ruolo) != "LOCATORE":
        flash('Non sei autorizzato a modificare lo stato di un annuncio', 'danger')
        return redirect(url_for('profilo_utente', id= current_user.id))
    if int(current_user.id) != annuncio_db['id_locatore']:
        flash('Non sei autorizzato a modificare lo stato di questo annuncio', 'danger')
        return redirect(url_for('profilo_utente', id= current_user.id))
    
    success = annunci_dao.rendi_annuncio_disponibile(id)
    
    if success:
        flash('L\'annuncio verrà ora mostrato!', 'success')
        return redirect(url_for('profilo_utente', id= current_user.id))
    else:
        flash('C\'è stato un problema con la sua richiesta, riprova!', 'warning')
        return redirect(url_for('profilo_utente', id= current_user.id))
    
@app.route('/ann/modifica/<int:id>')
@login_required
def modifica_ann(id):
    ann_db = annunci_dao.get_annuncio_by_id(id)
    if current_user.id != ann_db['id_locatore']:
        app.logger.info('Non sei autorizzato a modifcare questo annuncio!')
        return redirect(url_for('home_prezzo'))
    else:
        prezzo = str(ann_db['prezzo'])
        [prezzo_unita, prezzo_decimali] = prezzo.split('.')
        prezzo_unita = int(prezzo_unita)
        prezzo_decimali = int(prezzo_decimali)
        return render_template('modifica_ann.html', ann=ann_db, pu = prezzo_unita, pd = prezzo_decimali)
    

@app.route('/annunci/modifica_info/<int:id>', methods=['POST'])
@login_required
def modifica_info_annuncio(id):
    
    annuncio_db=annunci_dao.get_annuncio_by_id(id)
    if str(current_user.ruolo) != "LOCATORE":
        flash('Non sei autorizzato a modificare un annuncio', 'danger')
        return redirect(url_for('home_prezzo'))
    if int(current_user.id) != annuncio_db['id_locatore']:
        flash('Non sei autorizzato a modificare questo annuncio', 'danger')
        return redirect(url_for('home_prezzo'))
    
    modAnn_form = request.form.to_dict()
    
    #controllo che i campi non siano vuoti o composti solo da spazi
    if modAnn_form['titolo'] == '':
        app.logger.error('Il titolo dell\'annuncio non può essere vuoto!')
        flash('Il titolo dell\'annuncio non può essere vuoto!', 'warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    elif modAnn_form['titolo'].isspace():
        app.logger.error('Il titolo dell\'annuncio non può essere composto solo da spazi!')
        flash('Il titolo dell\'annuncio non può essere composto solo da spazi!', 'warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if modAnn_form['tipo'] != 'loft' and modAnn_form['tipo'] != 'appartamento' and modAnn_form['tipo'] != 'villa' and modAnn_form['tipo'] != 'casa indipendente':
        app.logger.error('Selezionare il tipo di abitazione!')
        flash('Selezionare il tipo di abitazione!','warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if int(modAnn_form['num_locali']) < 1 or int(modAnn_form['num_locali']) > 5:
        app.logger.error('Selezionare il numero di locali!')
        flash('Selezionare il numero di locali!', 'warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if modAnn_form['descrizione'] == '':
        app.logger.error('La descrizione dell\'annuncio non può essere vuota!')
        flash('La descrizione dell\'annuncio non può essere vuota!', 'warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    elif modAnn_form['descrizione'].isspace():
        app.logger.error('La descrizione dell\'annuncio non può essere composta solo da spazi!')
        flash('La descrizione dell\'annuncio non può essere composta solo da spazi!','warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if modAnn_form['arredata'] != 'SI' and modAnn_form['arredata'] != 'NO':
        app.logger.error('Indica se l\'abitazione è arredata!')
        flash('Indica se l\'abitazione è arredata!','warning')
        return redirect(url_for('profilo_utente', id = current_user.id))
    if modAnn_form['prezzo-unità'] == '':
        app.logger.error('Inserisci un prezzo per l\'annuncio!')
        flash('Inserisci un prezzo per l\'annuncio!','warning')
        return redirect(url_for('profilo_utente', id = current_user.id))

    
    prezzo = float(str(modAnn_form['prezzo-unità'])+'.'+str(modAnn_form['prezzo-centesimi']))
    mod_annuncio= {'titolo':modAnn_form['titolo'], 'tipo':modAnn_form['tipo'], 'num_locali':int(modAnn_form['num_locali']), 'descrizione':modAnn_form['descrizione'], 'arredata':modAnn_form['arredata'],'prezzo':prezzo}
    mod_annuncio['id_locatore'] = int(annuncio_db['id_locatore'])  
    mod_annuncio['nom_locatore'] = current_user.nominativo
    mod_annuncio['disponibile'] = str(annuncio_db['disponibile'])
    id_annuncio = int(id)
    success = annunci_dao.modifica_info_annuncio(mod_annuncio, id_annuncio)

    if success:
        app.logger.info('Annuncio modificato correttamente')
        flash('Annuncio modificato correttamente','success')
    else:
        app.logger.error('Errore nella modifica dell\'annuncio: riprova!')
        flash('Errore nella modifica dell\'annuncio: riprova!','warning')

    return redirect(url_for('home_prezzo'))

@app.route('/annunci/modifica_foto/<int:id>', methods=['POST'])
@login_required
def modifica_foto_annuncio(id):
    
    annuncio_db=annunci_dao.get_annuncio_by_id(id)
    if str(current_user.ruolo) != "LOCATORE":
        flash('Non sei autorizzato a modificare un annuncio', 'danger')
        return redirect(url_for('home_prezzo'))
    if int(current_user.id) != annuncio_db['id_locatore']:
        flash('Non sei autorizzato a modificare questo annuncio', 'danger')
        return redirect(url_for('home_prezzo'))
    
    modAnn_form = request.form.to_dict()
    
    stringhe_nome_foto =[]
    img1 = request.files['newimg1']
    img2 = request.files['newimg2']
    img3 = request.files['newimg3']
    img4 = request.files['newimg4']
    img5 = request.files['newimg5']
    img = [img1, img2, img3, img4, img5]
    newimg=[]
    
    for elem in img:
        if elem:
            newimg.append(elem)
    
    #conto quante foto sono state caricate e verifico che siano >0 e <=5
    numFoto = 0
    if 'foto1' in modAnn_form.keys():
        stringhe_nome_foto.append(modAnn_form['foto1'])
        numFoto+=1
    if 'foto2' in modAnn_form.keys():
        stringhe_nome_foto.append(modAnn_form['foto2'])
        numFoto+=1
    if 'foto3' in modAnn_form.keys():
        stringhe_nome_foto.append(modAnn_form['foto3'])
        numFoto+=1
    if 'foto4' in modAnn_form.keys():
        stringhe_nome_foto.append(modAnn_form['foto4'])
        numFoto+=1
    if 'foto5' in modAnn_form.keys():
        stringhe_nome_foto.append(modAnn_form['foto5'])
        numFoto+=1
    numFoto += len(newimg)
    
    if numFoto == 0 or numFoto>5:
        flash('Si prega di selezionare dalle 1 alle 5 foto!', 'warning')
        return redirect(url_for('modifica_ann', id=id))
    
    i=0
    for foto in newimg:
        # Open the user-provided image using the Image module
        try:
            picture = Image.open(foto)
        except:
            app.logger.info('Sono accettati solo file in formato png, jpeg e jpg.')
            flash('Sono accettati solo file in formato png, jpeg e jpg.', 'warning')        
            return redirect(url_for('profilo_utente', id=current_user.id))     
        # Get the width and height of the image
        width, height = picture.size
        # Calculate the new height while maintaining the aspect ratio based on the desired width
        new_height = height/width * FOTO_IMG_WIDTH
        # Define the size for thumbnail creation with the desired width and calculated height
        size = FOTO_IMG_WIDTH, new_height
        picture.thumbnail(size, Image.Resampling.LANCZOS)
        # Extracting file extension from the image filename
        ext = foto.filename.split('.')[-1]
        # Getting the current timestamp in seconds
        secondi = int(datetime.now().timestamp())
        picture.save('static/@foto'+ str(i) + str(current_user.id).lower() + '-' + str(secondi) + '.' + ext)
        stringhe_nome_foto.append('@foto'+ str(i) + str(current_user.id).lower() + '-' + str(secondi) + '.' + ext)
        i+=1
    
    fotoDEF = {'foto1':'', 'foto2':'', 'foto3':'', 'foto4':'','foto5':''}
    for elem in stringhe_nome_foto:
        if fotoDEF['foto1']=='':
            fotoDEF['foto1']=elem
        elif fotoDEF['foto2']=='':
            fotoDEF['foto2']=elem
        elif fotoDEF['foto3']=='':
            fotoDEF['foto3']=elem
        elif fotoDEF['foto4']=='':
            fotoDEF['foto4']=elem
        elif fotoDEF['foto5']=='':
            fotoDEF['foto5']=elem
        
    success = annunci_dao.modifica_foto(id, fotoDEF)
    if success:
        flash('Foto modificate correttamente', 'success')
        return redirect(url_for('profilo_utente', id=current_user.id))
    else:
        flash('E\' stato riscontrato un\'errore nella modifica delle foto', 'danger')
        return redirect(url_for('profilo_utente', id=current_user.id))
 
#gestione delle prenotazioni
@app.route('/prenotazioni/new/<int:id_annuncio>', methods=['POST'])
@login_required
def nuova_prenotazione(id_annuncio):
    
    today = datetime.today()
    in7days = today+timedelta(days=7)       
    
    newPren_form = request.form.to_dict()
    annuncio_db = annunci_dao.get_annuncio_by_id(id_annuncio)
    #mi salvo la data odierna e quella fra sette giorni, queste due date mi serviranno per controllare che la data inserit nel form sia valida
    in7days = today + timedelta(days=7)
    
    #controllo che un locatore non posa fare una prenotazione per una sua abitazione
    if current_user.id == annuncio_db['id_locatore']:
        flash('Non puoi fare una prenotazione per il tuo stesso appartamento', 'warning')
        return redirect(url_for('single_annuncio', id= id_annuncio))
    
    #controllo che un cliente non stia facendo una prenotazione per un'abitazione per cui ha già una prenotazione non rifiutata
    stato = prenotazioni_dao.verifica_non_duplica_prenotazioni(current_user.id, id_annuncio)
    if stato!=None:
        flash('Hai già una prenotazione ' + stato['stato'].lower() + ' per questo annuncio!', 'warning')
        return redirect(url_for('single_annuncio', id= id_annuncio))
    
    #verifico che i campi siano validi
    if newPren_form['mod_visita'] != "DI PERSONA" and newPren_form['mod_visita'] != "DA REMOTO":
        app.logger.error('Modalità di visita non valida')
        flash('Inserisci una modalità di visita valida', 'warning')
        return redirect(url_for('single_annuncio', id= id_annuncio))
    
    data_ora = newPren_form['data_ora'].split('+')
    
    #gestisco il caso in cui la stringa non venga riconosciuta come data
    try:
        data=datetime.strptime(data_ora[0], '%d/%m/%Y')
    except:
        app.logger.error('Data non valida')
        flash('Inserisci una data valida 1', 'warning')
        return redirect(url_for('single_annuncio', id= id_annuncio))
    
    
    fascia_oraria=data_ora[1]
    
    if data < today or data=="" or data > in7days:
        app.logger.error('Data non valida')
        flash('Inserisci una data valida', 'warning')
        return redirect(url_for('single_annuncio', id= id_annuncio))
    if fascia_oraria != "9-12" and fascia_oraria!= "12-14" and fascia_oraria!= "14-17" and fascia_oraria != "17-20":
        app.logger.error('Fascia oraria non valida')
        flash('Inserisci una fascia oraria valida', 'warning')
        return redirect(url_for('single_annuncio', id= id_annuncio))
    
    newPren_form['id_cliente'] = int(current_user.id)
    newPren_form['id_annuncio'] = int(id_annuncio)
    newPren_form['data'] = data.strftime('%d/%m/%Y') 
    newPren_form['stato'] = "RICHIESTA"
    newPren_form['fascia_oraria'] = fascia_oraria
    
    #verifico che lo slot sia libero
    libero = prenotazioni_dao.verifica_diponibilita_slot_orario(newPren_form['data'], newPren_form['fascia_oraria'],newPren_form['id_annuncio'])
    if not libero:
        flash('Siamo spiacenti ma lo slot orario selezionato è già occupato', 'warning')
        return redirect(url_for('single_annuncio', id= id_annuncio))
        
    success = prenotazioni_dao.nuova_prenotazione(newPren_form)

    if success:
        app.logger.info('Prenotazione inserita correttamente')
        flash('La sua prenotazione è stata presa a carico','success')
    else:
        app.logger.error('Errore nell\'inserimento della prenotazione: riprova!')
        flash('Errore nell\'inserimento della prenotazione: riprova!','warning')
    

    return redirect(url_for('single_annuncio', id= id_annuncio))

@app.route('/prenotazioni/accetta/<int:id_prenotazione>')
@login_required
def accetta_prenotazione(id_prenotazione):
    
    #verifico che colui che sta modificando lo stato della prenotazione sia effettivamente colui che ha pubblicato l'annuncio che ha ricevuto la prentazione
    pren = prenotazioni_dao.get_prenotazioni_by_id(id_prenotazione)
    ann = annunci_dao.get_annuncio_by_id(pren['id_annuncio'])
    if current_user.id != ann['id_locatore']:
        flash('Non sei autorizzato a modificare lo stato di questa prenotazione', 'danger')
        return redirect(url_for('home_prezzo'))
    
    success = prenotazioni_dao.accetta_prenotazione(id_prenotazione)

    if success:
        app.logger.info('Prenotazione accettata correttamente')
        flash('La prenotazione è stata accettata','success')
    else:
        app.logger.error('Errore nell\'accettazione della prenotazione: riprova!')
        flash('Errore nell\'accettazione della prenotazione: riprova!','warning')
    

    return redirect(url_for('profilo_utente', id=current_user.id))

@app.route('/prenotazioni/rifiuta/<int:id_prenotazione>', methods=['POST'])
@login_required
def rifiuta_prenotazione(id_prenotazione):
    
    #verifico che colui che sta modificando lo stato della prenotazione sia effettivamente colui che ha pubblicato l'annuncio che ha ricevuto la prentazione
    pren = prenotazioni_dao.get_prenotazioni_by_id(id_prenotazione)
    ann = annunci_dao.get_annuncio_by_id(pren['id_annuncio'])
    if current_user.id != ann['id_locatore']:
        flash('Non sei autorizzato a modificare lo stato di questa prenotazione', 'danger')
        return redirect(url_for('home_prezzo'))
    
    mot = request.values.get('motivazione')
   
    #verifico che sia stata inserita una motivazione
    if mot=='':
        flash('Inserisca una motivazione valida', 'warning')
        return redirect(url_for('profilo_utente', id=current_user.id))
    elif mot.isspace():
        flash('Inserisca una motivazione valida', 'warning')
        return redirect(url_for('profilo_utente', id=current_user.id))
    
    success = prenotazioni_dao.rifiuta_prenotazione(id_prenotazione, mot)

    if success:
        app.logger.info('Prenotazione rifiutata correttamente')
        flash('La prenotazione è stata rifiuatata','success')
    else:
        app.logger.error('Errore nel rifiutare la prenotazione: riprova!')
        flash('Errore nel rifiutare la prenotazione: riprova!','warning')
    
    return redirect(url_for('profilo_utente', id=current_user.id))



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)