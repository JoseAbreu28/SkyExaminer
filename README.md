# ECQB-PPL Exam Trainer

A lightweight exam preparation tool for the **EASA PPL (Private Pilot Licence)** based on the official **AirAcademy ECQB-PPL** question database.

This tool allows students to simulate real exams, track their progress, and improve their performance over time by reviewing past mistakes.

---

## ✈️ Features

- ✅ Uses official questions from [AirAcademy ECQB-PPL](https://aircademy.com/ecqb-ppl-en/)
- 🔀 **Dynamic question variants**: question answer options are shuffled each time to increase entropy
- 📊 **Performance tracking**: after each exam, incorrect answers are logged to allow analysis of repeated errors
- 📅 **3 Exam Modes**:
  - **Real Exam Simulation** (with countdown timer and real question count)
  - **General Practice Mode**
  - **Improve Mode** (focuses on questions previously answered incorrectly)
- 🧮 **Built-in E6B Navigation Tool**: integrated support for navigational questions via [UND E6B Trainer](https://mediafiles.aero.und.edu/aero.und.edu/aviation/trainers/e6b/)

---

## 📁 Folder Structure

- `answer_history/` — stores per-subject logs of incorrect answers with counts
- `questions/` — contains the ECQB question database in CSV format
- `exam_results/` — stores results and scores of previous exams
- `main.py` — main execution file (CLI or GUI depending on implementation)

---

## 💻 Installation (Windows)

1. **Clone or download** the repository:
```bash
git clone https://github.com/your-username/ecqb-ppl-trainer.git
cd ecqb-ppl-trainer
```

2. **Run the app**:
```bash
python main.py
```

Make sure you have Python 3.x installed. No external dependencies are required unless GUI is implemented.

---

## 🧠 Future Improvements

- Web interface for mobile/tablet access
- Detailed stats dashboard
- Question flagging and notes
- Custom exam configuration

---

## 📜 License

This project is intended for **personal educational use only**. The question content belongs to [AirAcademy](https://aircademy.com) and is subject to their licensing terms.

---

## ✉️ Credits

Developed for PPL students and hobbyist aviators who want to practice with high realism and track their weak areas efficiently.
