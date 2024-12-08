from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import os
import csv
import pandas as pd

app = Flask(__name__)
app.secret_key = 'wecs8798oiqewdascq79'

audio_data = []
with open('audios.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        audio_data.append(row)

random.shuffle(audio_data)

# Use /tmp for Excel file in Vercel's serverless environment
EXCEL_FILE = '/tmp/quiz_results.xlsx'

def init_excel():
    if not os.path.isfile(EXCEL_FILE):
        df = pd.DataFrame(columns=['name', 'score', 'total_questions', 'timestamp'])
        df.to_excel(EXCEL_FILE, index=False)

init_excel()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    session['score'] = 0
    session['current_index'] = 0
    session['name'] = request.form['name']
    session['questions_seen'] = 0
    return redirect(url_for('question'))

@app.route('/question')
def question():
    current_index = session.get('current_index', 0)
    if current_index >= len(audio_data):
        return redirect(url_for('result'))
    audio_file = audio_data[current_index]['filename']
    if not audio_file.endswith('.mp3'):
        audio_file += '.mp3'
    full_audio_path = os.path.join(app.static_folder, 'audios', audio_file)
    if not os.path.exists(full_audio_path):
        return jsonify({"error": "File not found", "file": full_audio_path}), 404
    audio_url = url_for('static', filename=f'audios/{audio_file}')
    score = session.get('score', 0)
    current_index += 1
    return render_template('question.html', audio_url=audio_url, score=score, current_index=current_index, total_questions=len(audio_data))

@app.route('/answer', methods=['POST'])
def answer():
    user_answer = request.form['answer']
    current_index = session.get('current_index', 0)
    correct_answer = ''
    is_correct = False

    if current_index < len(audio_data):
        correct_answer = audio_data[current_index]['ground_truth']
        if user_answer == correct_answer:
            session['score'] += 1
            is_correct = True

    session['is_correct'] = is_correct
    session['correct_answer'] = correct_answer
    session['questions_seen'] = session.get('questions_seen', 0) + 1

    return jsonify({
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'score': session['score'],
        'current_index': current_index + 1,
        'total_questions': len(audio_data)
    })

@app.route('/next', methods=['POST'])
def next_question():
    session['current_index'] += 1
    return redirect(url_for('question'))

@app.route('/result')
def result():
    save_quiz()
    score = session.get('score', 0)
    total_questions = session.get('questions_seen', 0)
    return render_template('result.html', score=score, total_questions=total_questions)

@app.route('/stop_quiz', methods=['POST'])
def stop_quiz():
    save_quiz()
    return redirect(url_for('result'))

@app.route('/stop')
def stop():
    return redirect(url_for('index'))

def save_quiz():
    score = session.get('score', 0) 
    total_questions = session.get('questions_seen', 0)
    name = session.get('name', 'Guest')
    timestamp = pd.Timestamp.now()

    # Append the results to the Excel file located in /tmp
    df = pd.read_excel(EXCEL_FILE)
    new_entry = pd.DataFrame({'name': [name], 'score': [score], 'total_questions': [total_questions], 'timestamp': [timestamp]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

if __name__ == '__main__':
    app.run(debug=True)
