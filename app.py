from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import random
import os
import csv

app = Flask(__name__)

# Subject mapping
subjects = {
    "Air Law": ("ECQB-PPL-10-ALW.csv", 20),
    "Human Performance": ("ECQB-PPL-20-HPL.csv", 12),
    "Meteorology": ("ECQB-PPL-30-MET.csv", 20),
    "Communications": ("ECQB-PPL-40-COM.csv", 12),
    "Principles of Flight": ("ECQB-PPL-51-PFA.csv", 12),
    "Operational Procedures": ("ECQB-PPL-60-OPR.csv", 12),
    "Flight Performance and Planning": ("ECQB-PPL-70-FPP.csv", 12),
    "Aircraft General Knowledge": ("ECQB-PPL-80-AGK.csv", 12),
    "Navigation": ("ECQB-PPL-90-NAV.csv", 20)
}

BASE_DIR = os.path.join(os.path.dirname(__file__), "PPL(A)_AirAcademy")
TRACK_FILE = os.path.join(os.path.dirname(__file__), "answer_history")
TMP_DIR = os.path.join(os.path.dirname(__file__), "tmp")
os.makedirs(TRACK_FILE, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)


def load_questions(filename, amount=None):
    csv_path = os.path.join(BASE_DIR, filename)
    df = pd.read_csv(csv_path, sep=';', on_bad_lines='skip')
    if amount:
        df = df.sample(n=amount)
    questions = []
    for _, row in df.iterrows():
        options = [row["Option A"], row["Option B"], row["Option C"], row["Option D"]]
        random.shuffle(options)
        questions.append({
            "text": row["Question"],
            "options": options,
            "correct": row["Answer"],
            "annex": row["Annex"] if not pd.isna(row["Annex"]) else ""
        })
    return questions


def log_answer(subject, question, correct, user_answer):
    correct_flag = user_answer == correct

    file_path = os.path.join(TRACK_FILE, f"{subject.replace(' ', '_')}.csv")

    # Se o ficheiro não existe, cria-o com cabeçalhos
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Question", "Correct", "Answered", "CorrectFlag", "Count"])

    lines = []
    found = False

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Question"] == question:
                row["Answered"] = user_answer or ""
                row["CorrectFlag"] = str(correct_flag)

                if not correct_flag:
                    # Incrementa apenas se errou
                    row["Count"] = str(int(row["Count"]) + 1)

                found = True
            lines.append(row)

    if not found:
        lines.append({
            "Question": question,
            "Correct": correct,
            "Answered": user_answer or "",
            "CorrectFlag": str(correct_flag),
            "Count": "0" if correct_flag else "1"
        })

    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Question", "Correct", "Answered", "CorrectFlag", "Count"])
        writer.writeheader()
        writer.writerows(lines)


@app.route("/")
def select_subject():
    return render_template("subjects.html", subjects=subjects)


@app.route("/exam", methods=["POST"])
def exam():
    subject_name = request.form.get("subject")
    mode = request.form.get("mode")  # full, exam, improve

    if subject_name not in subjects:
        return "Invalid subject.", 400

    filename, amount = subjects[subject_name]
    all_questions = load_questions(filename, None)

    if mode == "improve":
        amount = 10  # fixo para improve
        track_path = os.path.join(TRACK_FILE, f"{subject_name.replace(' ', '_')}.csv")

        if os.path.exists(track_path):
            df = pd.read_csv(track_path)
            df["CorrectFlag"] = df["CorrectFlag"].astype(str).str.lower()
            df["Count"] = pd.to_numeric(df["Count"], errors="coerce").fillna(0).astype(int)

            # Erros primeiro
            df_errors = df[df["CorrectFlag"] == "false"].sort_values(by="Count", ascending=False)
            error_questions = df_errors["Question"].tolist()

            # Depois acertos com Count alto
            df_corrects = df[df["CorrectFlag"] == "true"].sort_values(by="Count", ascending=False)
            correct_questions = df_corrects["Question"].tolist()

            # Combinar sem repetir
            combined_questions = error_questions + [q for q in correct_questions if q not in error_questions]

            selected_questions = []
            for q_text in combined_questions:
                match = next((q for q in all_questions if q["text"] == q_text), None)
                if match and match not in selected_questions:
                    selected_questions.append(match)
                if len(selected_questions) >= amount:
                    break

            # Se ainda faltarem perguntas, preenche aleatoriamente
            if len(selected_questions) < amount:
                remaining = [q for q in all_questions if q not in selected_questions]
                selected_questions += random.sample(remaining, min(amount - len(selected_questions), len(remaining)))
        else:
            selected_questions = random.sample(all_questions, amount)

    elif mode == "full":
        selected_questions = all_questions
        return render_template("view_all.html", questions=selected_questions, subject=subject_name)

    else:
        selected_questions = random.sample(all_questions, amount)

    exam_durations = {
        'Air Law': 40,
        'Human Performance': 25,
        'Meteorology': 40,
        'Communications': 25,
        'Principles of Flight': 25,
        'Operational Procedures': 25,
        'Flight Performance and Planning': 25,
        'Aircraft General Knowledge': 25,
        'Navigation': 60
    }
    timer_minutes = exam_durations.get(subject_name, 25)

    exam_path = os.path.join(TMP_DIR, 'exam.csv')
    with open(exam_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Question', 'Answer', 'Option A', 'Option B', 'Option C', 'Option D', 'Annex'])
        for q in selected_questions:
            writer.writerow([q['text'], q['correct'], *q['options'], q['annex']])

    return render_template("exam.html", questions=selected_questions, subject=subject_name, timer_minutes=timer_minutes)


@app.route("/result", methods=["POST"])
def result():
    subject = request.form.get("subject")
    answers = request.form.to_dict()

    exam_path = os.path.join(TMP_DIR, "exam.csv")
    questions = []

    with open(exam_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append({
                "text": row["Question"],
                "options": [row["Option A"], row["Option B"], row["Option C"], row["Option D"]],
                "correct": row["Answer"]
            })

    results = []
    score = 0

    for i, question in enumerate(questions):
        user_answer = answers.get(f'answer_{i}', '').strip()
        correct = question["correct"].strip()
        is_correct = user_answer and user_answer == correct

        if is_correct:
            score += 1

        results.append({
            "question": question["text"],
            "options": question["options"],
            "answer": user_answer if user_answer else "-",
            "correct": correct,
            "is_correct": is_correct
        })

        log_answer(subject, question["text"], correct, user_answer)

    result_path = os.path.join(TMP_DIR, "exam_answers.csv")
    with open(result_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Correct", "Answered", "CorrectFlag"])
        for r in results:
            writer.writerow([r["question"], r["correct"], r["answer"], r["is_correct"]])

    total = len(questions)
    passed = score >= (total * 0.75)

    return render_template("result.html", subject=subject, score=score, total=total, passed=passed, results=results)


@app.route("/result_all", methods=["POST"])
def result_all():
    subject = request.form.get("subject")
    answers = request.form.to_dict()

    filename, _ = subjects[subject]
    all_questions = load_questions(filename, None)

    results = []
    score = 0

    for i, question in enumerate(all_questions):
        user_answer = answers.get(f'answer_{i}', '').strip()
        correct = question["correct"].strip()
        is_correct = user_answer and user_answer == correct

        if is_correct:
            score += 1

        results.append({
            "question": question["text"],
            "options": question["options"],
            "answer": user_answer if user_answer else "-",
            "correct": correct,
            "is_correct": is_correct
        })

        log_answer(subject, question["text"], correct, user_answer)

    total = len(all_questions)
    passed = score >= total * 0.75

    return render_template("result_all.html", results=results, score=score, total=total, passed=passed, subject=subject)


@app.route('/clear_tmp')
def clear_tmp():
    import shutil
    shutil.rmtree('tmp', ignore_errors=True)
    os.makedirs('tmp', exist_ok=True)
    return redirect('/')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
