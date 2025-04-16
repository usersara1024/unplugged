from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import time
import random

app = Flask(__name__)
app.secret_key = 'la_tua_chiave_segreta'  # Importante per la sessione

# Variabili di stato
default_time_limit = 60
question_duration = 30
topics = []
current_question_data = None
questions = [
    {"domanda": "Qual è la capitale d'Italia?", "risposta": "Roma"},
    {"domanda": "Quanto fa 2 + 2?", "risposta": "4"},
    {"domanda": "Qual è un linguaggio di programmazione molto usato?", "risposta": "Python"}
    # Aggiungi qui altre domande e risposte!
]

@app.route('/', methods=['GET', 'POST'])
def index():
    session.clear()  # Pulisce la sessione all'inizio
    if request.method == 'POST':
        user_type = request.form['user_type']
        session['user_type'] = user_type
        if user_type == 'professor' or user_type == 'parent':
            return redirect(url_for('professor_parent_setup'))
        elif user_type == 'student':
            session['time_limit'] = default_time_limit
            session['time_remaining'] = default_time_limit
            session['timer_running'] = False
            session['timer_start_time'] = 0
            return redirect(url_for('student_view'))
    return render_template('index.html')

@app.route('/setup', methods=['GET', 'POST'])
def professor_parent_setup():
    if session.get('user_type') not in ['professor', 'parent']:
        return redirect(url_for('index'))
    if request.method == 'POST':
        time_limit = int(request.form['time_limit'])
        topics_str = request.form['topics']
        session['time_limit'] = time_limit
        session['time_remaining'] = time_limit
        session['topics'] = [topic.strip() for topic in topics_str.split('\n') if topic.strip()]
        return redirect(url_for('student_view'))
    return render_template('professor_parent.html')

@app.route('/student')
def student_view():
    if session.get('user_type') != 'student' and session.get('user_type') not in ['professor', 'parent']:
        return redirect(url_for('index'))
    return render_template('student.html', time_remaining=session.get('time_remaining', 0), timer_running=session.get('timer_running', False))

@app.route('/start_timer')
def start_timer():
    session['timer_running'] = True
    session['timer_start_time'] = time.time()
    return redirect(url_for('student_view'))

@app.route('/get_time')
def get_time():
    time_left = session.get('time_remaining', 0)
    is_running = session.get('timer_running', False)
    if is_running and time_left > 0:
        elapsed_time = time.time() - session['timer_start_time']
        session['time_remaining'] = max(0, session['time_limit'] - int(elapsed_time))
        if session['time_remaining'] <= 0:
            session['timer_running'] = False
    return jsonify({'time_remaining': session.get('time_remaining', 0), 'timer_running': is_running})

@app.route('/ask')
def ask_question():
    if session.get('timer_running', False) and session.get('time_remaining', 0) <= 0:
        if session.get('topics'):
            topic_questions = [q for q in questions if any(topic.lower() in q['domanda'].lower() for topic in session['topics'])]
            if topic_questions:
                session['current_question_data'] = random.choice(topic_questions)
                return render_template('question.html', question=session['current_question_data']['domanda'])
            else:
                return render_template('question.html', question="Nessuna domanda disponibile per questi argomenti.")
        else:
            session['current_question_data'] = random.choice(questions)
            return render_template('question.html', question=session['current_question_data']['domanda'])
    else:
        return redirect(url_for('student_view'))

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    if session.get('current_question_data'):
        user_answer = request.form['answer']
        correct_answer = session['current_question_data']['risposta']
        del session['current_question_data']
        if user_answer.strip().lower() == correct_answer.lower():
            session['time_remaining'] = session.get('time_remaining', 0) + question_duration
            return render_template('result.html', message=f"Risposta corretta! +{question_duration} secondi.")
        else:
            return render_template('result.html', message=f"Risposta errata. La risposta corretta era: {correct_answer}.")
    return redirect(url_for('student_view'))

if __name__ == '__main__':
    app.run(debug=True)