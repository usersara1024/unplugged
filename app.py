import os
import json
import random
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
# È fondamentale impostare una chiave segreta robusta in un'applicazione reale
app.secret_key = os.urandom(24)

# Impostazioni predefinite
DEFAULT_TIME_LIMIT = 600  # 10 minuti
CORRECT_ANSWER_BONUS = 30 # 30 secondi bonus

# --- Funzione Placeholder per Gemini ---
def generate_question_from_gemini(topics):
    """
    Placeholder per la chiamata all'API di Gemini.
    Restituisce una domanda fittizia in formato JSON basata sugli argomenti.
    """
    print(f"--- Chiamata Fittizia a Gemini con argomenti: {topics} ---")
    # Scegli un argomento a caso dalla lista fornita
    chosen_topic = random.choice(topics) if topics else "un argomento generico"

    # Genera casualmente un tipo di domanda
    question_type = random.choice(["multipla", "aperta"])

    if question_type == "multipla":
        possible_answers = [f"Risposta A per {chosen_topic}", f"Risposta B per {chosen_topic}", f"Risposta C per {chosen_topic}", f"Risposta D per {chosen_topic}"]
        correct_index = random.randint(0, len(possible_answers) - 1)
        return {
          "domanda": f"Domanda a scelta multipla su: {chosen_topic}?",
          "tipo": "multipla",
          "risposte": possible_answers,
          "indice_risposta_corretta": correct_index
        }
    else: # Tipo "aperta"
         return {
          "domanda": f"Descrivi apertamente qualcosa riguardo: {chosen_topic}.",
          "tipo": "aperta"
        }
# -------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
    """Pagina iniziale per la selezione del ruolo."""
    session.clear() # Pulisce la sessione precedente all'accesso
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type in ['professor', 'parent', 'student']:
            session['user_type'] = user_type
            # Carica le impostazioni predefinite o salvate (qui usiamo le predefinite)
            session['time_limit'] = DEFAULT_TIME_LIMIT
            session['topics'] = ["Argomento Default 1", "Argomento Default 2"] # Argomenti predefiniti
            session['timer_start_time'] = 0
            session['time_remaining'] = DEFAULT_TIME_LIMIT
            session['timer_running'] = False
            session['current_question'] = None # Resetta domanda precedente
            session['score'] = 0 # Inizializza punteggio

            if user_type in ['professor', 'parent']:
                return redirect(url_for('professor_parent_setup'))
            elif user_type == 'student':
                # Per lo studente, usa direttamente le impostazioni caricate/predefinite
                 session['time_remaining'] = session.get('time_limit', DEFAULT_TIME_LIMIT)
                 return redirect(url_for('student_view'))
        else:
            # Gestire caso di user_type non valido se necessario
            return render_template('index.html', error="Ruolo non valido selezionato.")
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def professor_parent_setup():
    """Pagina per professori/genitori per impostare tempo e argomenti."""
    if session.get('user_type') not in ['professor', 'parent']:
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Salva le impostazioni nella sessione
            time_limit_input = request.form.get('time_limit')
            # Assicurati che sia un intero positivo, altrimenti usa il default
            session['time_limit'] = int(time_limit_input) if time_limit_input and time_limit_input.isdigit() and int(time_limit_input) > 0 else DEFAULT_TIME_LIMIT

            topics_input = request.form.get('topics', '')
            # Salva gli argomenti, rimuovendo spazi bianchi e righe vuote
            session['topics'] = [topic.strip() for topic in topics_input.splitlines() if topic.strip()]
            # Se non vengono inseriti argomenti, metti un default generico
            if not session['topics']:
                 session['topics'] = ["Argomento Generico"]

            # Resetta il tempo rimanente all'avvio per lo studente
            session['time_remaining'] = session['time_limit']
            session['timer_running'] = False
            session['timer_start_time'] = 0

            # NOTA: Qui potresti salvare 'time_limit' e 'topics' nel file data/topics.json
            # Esempio:
            # settings = {"time_limit": session['time_limit'], "topics": session['topics']}
            # try:
            #     os.makedirs('data', exist_ok=True) # Crea la cartella se non esiste
            #     with open('data/topics.json', 'w') as f:
            #         json.dump(settings, f, indent=2)
            # except IOError as e:
            #     print(f"Errore nel salvataggio del file JSON: {e}")

            print(f"Impostazioni salvate in sessione: Tempo={session['time_limit']}, Argomenti={session['topics']}")
            # Non reindirizziamo allo studente, ma mostriamo un messaggio di conferma
            return render_template('professor_parent.html',
                                   current_time_limit=session['time_limit'],
                                   current_topics="\n".join(session['topics']),
                                   message="Impostazioni salvate con successo!")

        except ValueError:
             return render_template('professor_parent.html',
                                   current_time_limit=session.get('time_limit', DEFAULT_TIME_LIMIT),
                                   current_topics="\n".join(session.get('topics', [])),
                                   error="Inserisci un valore numerico valido per il tempo limite.")

    # GET request: Mostra i valori correnti dalla sessione
    return render_template('professor_parent.html',
                           current_time_limit=session.get('time_limit', DEFAULT_TIME_LIMIT),
                           current_topics="\n".join(session.get('topics', ["Argomento Default 1"])))

@app.route('/student')
def student_view():
    """Pagina principale per lo studente con il timer."""
    if session.get('user_type') != 'student':
        # Se un prof/genitore accede a /student, usa le impostazioni salvate
         if session.get('user_type') in ['professor', 'parent']:
             pass # Possono vedere la pagina studente con le impostazioni correnti
         else:
             return redirect(url_for('index')) # Altrimenti torna all'inizio

    # Assicurati che il tempo rimanente sia inizializzato correttamente
    if 'time_remaining' not in session:
         session['time_remaining'] = session.get('time_limit', DEFAULT_TIME_LIMIT)
    if 'timer_running' not in session:
         session['timer_running'] = False

    # Sfondi disponibili (solo nomi per ora)
    available_backgrounds = ["Default", "Forest", "Space", "Abstract"]

    return render_template('student.html',
                           time_remaining=session['time_remaining'],
                           timer_running=session['timer_running'],
                           backgrounds=available_backgrounds,
                           score=session.get('score', 0))

@app.route('/start_timer', methods=['POST'])
def start_timer():
    """Avvia il timer per lo studente."""
    if session.get('user_type') == 'student' and not session.get('timer_running', False):
        session['timer_running'] = True
        # Registra il tempo di inizio *server-side*
        session['timer_start_time'] = time.time()
        # Imposta il tempo rimanente iniziale al momento dell'avvio effettivo
        session['time_remaining'] = session.get('time_limit', DEFAULT_TIME_LIMIT)
        print("Timer avviato!")
        return jsonify({'success': True, 'time_remaining': session['time_remaining']})
    return jsonify({'success': False, 'error': 'Timer già avviato o utente non autorizzato.'})

@app.route('/get_time')
def get_time():
    """Endpoint per aggiornare il tempo rimanente via JavaScript."""
    if 'user_type' not in session:
        return jsonify({'error': 'Utente non autenticato'}), 401

    is_running = session.get('timer_running', False)
    time_left = session.get('time_remaining', 0)
    should_redirect = False

    if is_running:
        start_time = session.get('timer_start_time', 0)
        limit = session.get('time_limit', DEFAULT_TIME_LIMIT)

        # Calcola il tempo trascorso dal momento in cui è stato avviato
        elapsed_time = time.time() - start_time
        # Calcola il tempo rimanente basato sul limite e il tempo trascorso
        current_remaining = max(0, limit - int(elapsed_time))

        # Aggiorna il tempo rimanente nella sessione solo se è cambiato
        if current_remaining != time_left:
            session['time_remaining'] = current_remaining

        time_left = current_remaining # Usa il valore appena calcolato

        if time_left <= 0:
            session['timer_running'] = False # Ferma il timer logico
            is_running = False
            should_redirect = True # Indica al frontend di reindirizzare

    return jsonify({
        'time_remaining': time_left,
        'timer_running': is_running,
        'should_redirect': should_redirect,
        'redirect_url': url_for('ask_question') # URL a cui reindirizzare
    })


@app.route('/ask')
def ask_question():
    """Genera e mostra una domanda quando il tempo scade."""
    # Verifica se l'utente è uno studente e se il tempo è scaduto
    # O se un professore/genitore vuole vedere l'anteprima
    user_type = session.get('user_type')
    time_remaining = session.get('time_remaining', -1)

    # Permetti l'accesso solo se studente con tempo scaduto O prof/genitore
    if not ( (user_type == 'student' and time_remaining <= 0) or \
             (user_type in ['professor', 'parent']) ):
         # Se il timer è ancora attivo per lo studente, rimanda alla pagina studente
        if user_type == 'student' and session.get('timer_running', False):
             return redirect(url_for('student_view'))
        # Altrimenti, se non autorizzato, torna all'index
        return redirect(url_for('index'))


    # Genera una nuova domanda solo se non ce n'è una attiva nella sessione
    # O se l'utente è prof/genitore (per vedere diverse domande)
    if not session.get('current_question') or user_type in ['professor', 'parent']:
         topics = session.get('topics', ["Argomento Generico"])
         # Chiama la funzione (placeholder) per ottenere la domanda
         question_data = generate_question_from_gemini(topics)
         session['current_question'] = question_data
         print(f"Domanda generata: {question_data}")
    else:
        # Usa la domanda già presente nella sessione (es. se l'utente ricarica la pagina)
        question_data = session.get('current_question')

    if not question_data:
        # Fallback nel caso la generazione fallisca
        return "Errore nella generazione della domanda.", 500

    return render_template('question.html', question_data=question_data)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Verifica la risposta dello studente."""
    if session.get('user_type') != 'student':
        return redirect(url_for('index'))

    question_data = session.get('current_question')
    if not question_data:
        # Se non c'è una domanda attiva, torna alla vista studente
        return redirect(url_for('student_view'))

    user_answer = None
    is_correct = False
    correct_answer_display = "N/A" # Cosa mostrare come risposta corretta

    # Gestione risposta multipla
    if question_data.get('tipo') == 'multipla':
        user_answer_index = request.form.get('answer') # Ottiene l'indice selezionato
        try:
            user_answer_index = int(user_answer_index)
            correct_index = question_data.get('indice_risposta_corretta')
            if user_answer_index == correct_index:
                is_correct = True
            # Prendi il testo della risposta corretta per mostrarlo
            if correct_index is not None and 0 <= correct_index < len(question_data.get('risposte', [])):
                correct_answer_display = question_data['risposte'][correct_index]
            else:
                 correct_answer_display = "(Indice corretto non valido)"
        except (ValueError, TypeError):
            # Gestisce il caso in cui l'indice non sia un numero valido
            pass # is_correct rimane False

    # Gestione risposta aperta
    elif question_data.get('tipo') == 'aperta':
        user_answer = request.form.get('answer')
        # Per le domande aperte, non c'è una verifica automatica in questo prototipo
        # Consideriamo la risposta "corretta" ai fini del bonus tempo, ma potresti
        # implementare una logica più complessa (es. keyword matching o valutazione AI)
        is_correct = True # Placeholder: consideriamo sempre corretto per il bonus
        correct_answer_display = "(Domanda Aperta - Verifica Manuale Necessaria)"

    # Prepara il messaggio di risultato
    if is_correct:
        message = f"Risposta Corretta!"
        # Applica bonus tempo solo se la risposta è corretta
        current_remaining = session.get('time_remaining', 0)
        new_time = current_remaining + CORRECT_ANSWER_BONUS
        session['time_remaining'] = new_time
        # Aggiorna anche il limite (per coerenza se il timer riparte)
        session['time_limit'] = session.get('time_limit', DEFAULT_TIME_LIMIT) + CORRECT_ANSWER_BONUS
        message += f" Hai guadagnato {CORRECT_ANSWER_BONUS} secondi bonus!"
        session['score'] = session.get('score', 0) + 1 # Incrementa punteggio
    else:
        message = f"Risposta Errata."
        if question_data.get('tipo') == 'multipla':
             message += f" La risposta corretta era: '{correct_answer_display}'"

    # Rimuovi la domanda corrente dalla sessione dopo averla processata
    session.pop('current_question', None)

    # Reindirizza alla pagina dei risultati
    return render_template('result.html', message=message)


if __name__ == '__main__':
    # Crea la directory 'static/js' se non esiste
    os.makedirs('static/js', exist_ok=True)
    # Aggiungi: Crea la directory 'static/css' se non esiste
    os.makedirs('static/css', exist_ok=True) # <<< AGGIUNGI QUESTA LINEA
    app.run(debug=True, port=5001)