from flask import Flask, render_template, request, send_file, url_for, redirect, flash, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import os
import json
import random
from data import db_session
from data.users import User
from data.game_results import GameResult

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty123'
socketio = SocketIO(app, cors_allowed_origins="*")


def load_quiz_data():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'questions.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка чтения questions.json: {e}")
    return {
        "formulaToName": [
            {"question": "H₂O", "answer": "Вода", "options": ["Вода", "Аммиак", "Углекислый газ", "Серная кислота"]},
            {"question": "CO₂", "answer": "Углекислый газ",
             "options": ["Метан", "Углекислый газ", "Угарный газ", "Сероводород"]},
            {"question": "HCl", "answer": "Хлороводород",
             "options": ["Азотная кислота", "Серная кислота", "Хлороводород", "Фосфорная кислота"]},
            {"question": "H₂SO₄", "answer": "Серная кислота",
             "options": ["Плавиковая кислота", "Уксусная кислота", "Азотная кислота", "Серная кислота"]},
            {"question": "NaOH", "answer": "Гидроксид натрия",
             "options": ["Гидроксид натрия", "Гидроксид калия", "Гидроксид кальция", "Гидроксид алюминия"]},
            {"question": "NH₃", "answer": "Аммиак", "options": ["Метан", "Аммиак", "Этан", "Пропан"]},
            {"question": "CH₄", "answer": "Метан", "options": ["Этан", "Пропан", "Метан", "Бутан"]},
            {"question": "NaCl", "answer": "Хлорид натрия",
             "options": ["Хлорид магния", "Хлорид кальция", "Хлорид калия", "Хлорид натрия"]},
            {"question": "CaCO₃", "answer": "Карбонат кальция",
             "options": ["Карбонат кальция", "Карбонат бария", "Карбонат натрия", "Карбонат магния"]},
            {"question": "HNO₃", "answer": "Азотная кислота",
             "options": ["Соляная кислота", "Азотная кислота", "Серная кислота", "Фосфорная кислота"]},
            {"question": "H₃PO₄", "answer": "Фосфорная кислота",
             "options": ["Уксусная кислота", "Серная кислота", "Фосфорная кислота", "Азотная кислота"]},
            {"question": "KOH", "answer": "Гидроксид калия",
             "options": ["Гидроксид алюминия", "Гидроксид кальция", "Гидроксид натрия", "Гидроксид калия"]},
            {"question": "Fe₂O₃", "answer": "Оксид железа(III)",
             "options": ["Оксид железа(III)", "Оксид меди", "Оксид алюминия", "Оксид железа(II)"]},
            {"question": "Al₂O₃", "answer": "Оксид алюминия",
             "options": ["Оксид магния", "Оксид алюминия", "Оксид цинка", "Оксид железа"]},
            {"question": "CuSO₄", "answer": "Сульфат меди(II)",
             "options": ["Сульфат натрия", "Сульфат железа", "Сульфат меди(II)", "Сульфат цинка"]},
            {"question": "Na₂CO₃", "answer": "Карбонат натрия",
             "options": ["Карбонат магния", "Карбонат кальция", "Карбонат калия", "Карбонат натрия"]},
            {"question": "H₂CO₃", "answer": "Угольная кислота",
             "options": ["Угольная кислота", "Фосфорная кислота", "Серная кислота", "Азотная кислота"]},
            {"question": "SO₂", "answer": "Оксид серы(IV)",
             "options": ["Серная кислота", "Оксид серы(IV)", "Оксид серы(VI)", "Сероводород"]},
            {"question": "SO₃", "answer": "Оксид серы(VI)",
             "options": ["Сернистая кислота", "Серная кислота", "Оксид серы(VI)", "Оксид серы(IV)"]},
            {"question": "NO₂", "answer": "Оксид азота(IV)",
             "options": ["Азотная кислота", "Аммиак", "Оксид азота(II)", "Оксид азота(IV)"]},
            {"question": "N₂O", "answer": "Оксид азота(I)",
             "options": ["Оксид азота(I)", "Аммиак", "Оксид азота(II)", "Оксид азота(IV)"]},
            {"question": "NO", "answer": "Оксид азота(II)",
             "options": ["Азотная кислота", "Оксид азота(II)", "Оксид азота(I)", "Оксид азота(IV)"]},
            {"question": "H₂S", "answer": "Сероводород",
             "options": ["Серная кислота", "Сероуглерод", "Сероводород", "Сернистый газ"]},
            {"question": "P₂O₅", "answer": "Оксид фосфора(V)",
             "options": ["Фосфин", "Фосфорная кислота", "Оксид фосфора(III)", "Оксид фосфора(V)"]},
            {"question": "CaO", "answer": "Оксид кальция",
             "options": ["Оксид кальция", "Оксид цинка", "Оксид магния", "Оксид бария"]},
            {"question": "MgO", "answer": "Оксид магния",
             "options": ["Оксид натрия", "Оксид магния", "Оксид кальция", "Оксид алюминия"]},
            {"question": "ZnO", "answer": "Оксид цинка",
             "options": ["Оксид свинца", "Оксид меди", "Оксид цинка", "Оксид железа"]},
            {"question": "PbO", "answer": "Оксид свинца(II)",
             "options": ["Оксид олова", "Оксид цинка", "Оксид свинца(IV)", "Оксид свинца(II)"]},
            {"question": "AgNO₃", "answer": "Нитрат серебра",
             "options": ["Нитрат серебра", "Нитрат кальция", "Нитрат калия", "Нитрат натрия"]},
            {"question": "KCl", "answer": "Хлорид калия",
             "options": ["Хлорид магния", "Хлорид калия", "Хлорид натрия", "Хлорид кальция"]},
            {"question": "FeCl₃", "answer": "Хлорид железа(III)",
             "options": ["Хлорид меди", "Хлорид алюминия", "Хлорид железа(III)", "Хлорид железа(II)"]},
            {"question": "CuCl₂", "answer": "Хлорид меди(II)",
             "options": ["Хлорид цинка", "Хлорид железа", "Хлорид меди(I)", "Хлорид меди(II)"]},
            {"question": "NaHCO₃", "answer": "Гидрокарбонат натрия",
             "options": ["Гидрокарбонат натрия", "Карбонат кальция", "Гидрокарбонат калия", "Карбонат натрия"]},
            {"question": "Ca(OH)₂", "answer": "Гидроксид кальция",
             "options": ["Гидроксид бария", "Гидроксид кальция", "Гидроксид натрия", "Гидроксид магния"]},
            {"question": "Ba(OH)₂", "answer": "Гидроксид бария",
             "options": ["Гидроксид стронция", "Гидроксид кальция", "Гидроксид бария", "Гидроксид магния"]},
            {"question": "FeSO₄", "answer": "Сульфат железа(II)",
             "options": ["Сульфат цинка", "Сульфат меди", "Сульфат железа(III)", "Сульфат железа(II)"]},
            {"question": "Fe₂(SO₄)₃", "answer": "Сульфат железа(III)",
             "options": ["Сульфат железа(III)", "Сульфат меди", "Сульфат алюминия", "Сульфат железа(II)"]},
            {"question": "NaNO₃", "answer": "Нитрат натрия",
             "options": ["Нитрат серебра", "Нитрат натрия", "Нитрат калия", "Нитрат кальция"]},
            {"question": "KNO₃", "answer": "Нитрат калия",
             "options": ["Нитрат бария", "Нитрат натрия", "Нитрат калия", "Нитрат кальция"]},
            {"question": "Ca(NO₃)₂", "answer": "Нитрат кальция",
             "options": ["Нитрат стронция", "Нитрат магния", "Нитрат бария", "Нитрат кальция"]},
            {"question": "Na₂SO₄", "answer": "Сульфат натрия",
             "options": ["Сульфат натрия", "Сульфат алюминия", "Сульфат калия", "Сульфат магния"]},
            {"question": "K₂SO₄", "answer": "Сульфат калия",
             "options": ["Сульфат бария", "Сульфат калия", "Сульфат натрия", "Сульфат кальция"]},
            {"question": "CaSO₄", "answer": "Сульфат кальция",
             "options": ["Сульфат стронция", "Сульфат магния", "Сульфат кальция", "Сульфат бария"]},
            {"question": "BaSO₄", "answer": "Сульфат бария",
             "options": ["Сульфат алюминия", "Сульфат кальция", "Сульфат магния", "Сульфат бария"]},
            {"question": "Na₃PO₄", "answer": "Фосфат натрия",
             "options": ["Фосфат натрия", "Фосфат магния", "Фосфат калия", "Фосфат кальция"]},
            {"question": "K₃PO₄", "answer": "Фосфат калия",
             "options": ["Фосфат алюминия", "Фосфат калия", "Фосфат натрия", "Фосфат кальция"]},
            {"question": "Ca₃(PO₄)₂", "answer": "Фосфат кальция",
             "options": ["Фосфат железа", "Фосфат магния", "Фосфат кальция", "Фосфат бария"]},
            {"question": "Na₂S", "answer": "Сульфид натрия",
             "options": ["Сульфид алюминия", "Сульфид калия", "Сульфид кальция", "Сульфид натрия"]},
            {"question": "K₂S", "answer": "Сульфид калия",
             "options": ["Сульфид калия", "Сульфид магния", "Сульфид натрия", "Сульфид кальция"]},
            {"question": "CaS", "answer": "Сульфид кальция",
             "options": ["Сульфид железа", "Сульфид кальция", "Сульфид магния", "Сульфид бария"]},
            {"question": "AlCl₃", "answer": "Хлорид алюминия",
             "options": ["Хлорид меди", "Хлорид железа", "Хлорид алюминия", "Хлорид цинка"]},
            {"question": "ZnCl₂", "answer": "Хлорид цинка",
             "options": ["Хлорид алюминия", "Хлорид меди", "Хлорид железа", "Хлорид цинка"]},
            {"question": "HgCl₂", "answer": "Хлорид ртути(II)",
             "options": ["Хлорид ртути(II)", "Хлорид серебра", "Хлорид свинца", "Хлорид ртути(I)"]},
            {"question": "AgCl", "answer": "Хлорид серебра",
             "options": ["Хлорид бария", "Хлорид серебра", "Хлорид натрия", "Хлорид кальция"]},
            {"question": "PbCl₂", "answer": "Хлорид свинца(II)",
             "options": ["Хлорид ртути", "Хлорид олова", "Хлорид свинца(II)", "Хлорид свинца(IV)"]},
            {"question": "SnCl₂", "answer": "Хлорид олова(II)",
             "options": ["Хлорид цинка", "Хлорид свинца", "Хлорид олова(IV)", "Хлорид олова(II)"]},
            {"question": "SnCl₄", "answer": "Хлорид олова(IV)",
             "options": ["Хлорид олова(IV)", "Хлорид ртути", "Хлорид свинца", "Хлорид олова(II)"]},
            {"question": "NH₄Cl", "answer": "Хлорид аммония",
             "options": ["Хлорид кальция", "Хлорид аммония", "Хлорид натрия", "Хлорид калия"]},
            {"question": "NH₄NO₃", "answer": "Нитрат аммония",
             "options": ["Нитрат кальция", "Нитрат натрия", "Нитрат аммония", "Нитрат калия"]},
            {"question": "(NH₄)₂SO₄", "answer": "Сульфат аммония",
             "options": ["Сульфат кальция", "Сульфат натрия", "Сульфат калия", "Сульфат аммония"]},
            {"question": "NaBr", "answer": "Бромид натрия",
             "options": ["Бромид натрия", "Бромид магния", "Бромид калия", "Бромид кальция"]},
            {"question": "KBr", "answer": "Бромид калия",
             "options": ["Бромид алюминия", "Бромид калия", "Бромид натрия", "Бромид кальция"]},
            {"question": "CaBr₂", "answer": "Бромид кальция",
             "options": ["Бромид стронция", "Бромид магния", "Бромид кальция", "Бромид бария"]},
            {"question": "NaI", "answer": "Иодид натрия",
             "options": ["Иодид магния", "Иодид калия", "Иодид кальция", "Иодид натрия"]},
            {"question": "KI", "answer": "Иодид калия",
             "options": ["Иодид калия", "Иодид алюминия", "Иодид натрия", "Иодид кальция"]},
            {"question": "CaI₂", "answer": "Иодид кальция",
             "options": ["Иодид стронция", "Иодид кальция", "Иодид магния", "Иодид бария"]},
            {"question": "NaF", "answer": "Фторид натрия",
             "options": ["Фторид магния", "Фторид калия", "Фторид натрия", "Фторид кальция"]},
            {"question": "KF", "answer": "Фторид калия",
             "options": ["Фторид алюминия", "Фторид натрия", "Фторид кальция", "Фторид калия"]},
            {"question": "CaF₂", "answer": "Фторид кальция",
             "options": ["Фторид кальция", "Фторид стронция", "Фторид магния", "Фторид бария"]},
            {"question": "Al₂(SO₄)₃", "answer": "Сульфат алюминия",
             "options": ["Сульфат меди", "Сульфат алюминия", "Сульфат железа", "Сульфат цинка"]},
            {"question": "ZnSO₄", "answer": "Сульфат цинка",
             "options": ["Сульфат алюминия", "Сульфат меди", "Сульфат цинка", "Сульфат железа"]},
            {"question": "Cu(NO₃)₂", "answer": "Нитрат меди(II)",
             "options": ["Нитрат серебра", "Нитрат железа", "Нитрат меди(I)", "Нитрат меди(II)"]},
            {"question": "Ag₂SO₄", "answer": "Сульфат серебра",
             "options": ["Сульфат серебра", "Сульфат кальция", "Сульфат натрия", "Сульфат калия"]},
            {"question": "Pb(NO₃)₂", "answer": "Нитрат свинца(II)",
             "options": ["Нитрат ртути", "Нитрат свинца(II)", "Нитрат олова", "Нитрат свинца(IV)"]},
            {"question": "Hg(NO₃)₂", "answer": "Нитрат ртути(II)",
             "options": ["Нитрат серебра", "Нитрат свинца", "Нитрат ртути(II)", "Нитрат ртути(I)"]},
            {"question": "Fe(NO₃)₃", "answer": "Нитрат железа(III)",
             "options": ["Нитрат меди", "Нитрат алюминия", "Нитрат железа(II)", "Нитрат железа(III)"]},
            {"question": "Cr₂O₃", "answer": "Оксид хрома(III)",
             "options": ["Оксид хрома(III)", "Оксид алюминия", "Оксид железа", "Оксид хрома(VI)"]},
            {"question": "CrO₃", "answer": "Оксид хрома(VI)",
             "options": ["Оксид ванадия", "Оксид хрома(VI)", "Оксид марганца", "Оксид хрома(III)"]},
            {"question": "MnO₂", "answer": "Оксид марганца(IV)",
             "options": ["Оксид железа", "Оксид хрома", "Оксид марганца(IV)", "Оксид марганца(II)"]},
            {"question": "KMnO₄", "answer": "Перманганат калия",
             "options": ["Перманганат бария", "Перманганат натрия", "Перманганат кальция", "Перманганат калия"]},
            {"question": "K₂Cr₂O₇", "answer": "Дихромат калия",
             "options": ["Дихромат калия", "Дихромат аммония", "Дихромат натрия", "Дихромат кальция"]},
            {"question": "Na₂CrO₄", "answer": "Хромат натрия",
             "options": ["Хромат бария", "Хромат натрия", "Хромат калия", "Хромат кальция"]},
            {"question": "K₂CrO₄", "answer": "Хромат калия",
             "options": ["Хромат алюминия", "Хромат кальция", "Хромат калия", "Хромат натрия"]},
            {"question": "Na₂SiO₃", "answer": "Силикат натрия",
             "options": ["Силикат магния", "Силикат калия", "Силикат кальция", "Силикат натрия"]},
            {"question": "K₂SiO₃", "answer": "Силикат калия",
             "options": ["Силикат калия", "Силикат бария", "Силикат натрия", "Силикат кальция"]},
            {"question": "CaSiO₃", "answer": "Силикат кальция",
             "options": ["Силикат алюминия", "Силикат кальция", "Силикат магния", "Силикат бария"]},
            {"question": "NaNO₂", "answer": "Нитрит натрия",
             "options": ["Нитрит бария", "Нитрит калия", "Нитрит натрия", "Нитрит кальция"]},
            {"question": "KNO₂", "answer": "Нитрит калия",
             "options": ["Нитрит аммония", "Нитрит натрия", "Нитрит кальция", "Нитрит калия"]},
            {"question": "Ca(NO₂)₂", "answer": "Нитрит кальция",
             "options": ["Нитрит кальция", "Нитрит стронция", "Нитрит магния", "Нитрит бария"]},
            {"question": "Na₂O₂", "answer": "Пероксид натрия",
             "options": ["Пероксид бария", "Пероксид натрия", "Пероксид калия", "Пероксид кальция"]},
            {"question": "K₂O₂", "answer": "Пероксид калия",
             "options": ["Пероксид алюминия", "Пероксид кальция", "Пероксид калия", "Пероксид натрия"]},
            {"question": "CaO₂", "answer": "Пероксид кальция",
             "options": ["Пероксид стронция", "Пероксид магния", "Пероксид бария", "Пероксид кальция"]},
            {"question": "BaO₂", "answer": "Пероксид бария",
             "options": ["Пероксид бария", "Пероксид алюминия", "Пероксид кальция", "Пероксид магния"]},
            {"question": "H₂O₂", "answer": "Пероксид водорода",
             "options": ["Азотная кислота", "Пероксид водорода", "Вода", "Серная кислота"]},
            {"question": "C₂H₅OH", "answer": "Этанол", "options": ["Бутанол", "Метанол", "Этанол", "Пропанол"]},
            {"question": "CH₃OH", "answer": "Метанол", "options": ["Бутанол", "Метанол", "Этанол", "Пропанол"]},
            {"question": "C₃H₇OH", "answer": "Пропанол", "options": ["Бутанол", "Пропанол", "Метанол", "Этанол"]},
            {"question": "C₄H₉OH", "answer": "Бутанол", "options": ["Бутанол", "Метанол", "Этанол", "Пропанол"]},
            {"question": "CH₃COOH", "answer": "Уксусная кислота",
             "options": ["Пропионовая кислота", "Уксусная кислота", "Муравьиная кислота", "Масляная кислота"]},
            {"question": "HCOOH", "answer": "Муравьиная кислота",
             "options": ["Пропионовая кислота", "Масляная кислота", "Уксусная кислота", "Муравьиная кислота"]},
            {"question": "C₃H₇COOH", "answer": "Масляная кислота",
             "options": ["Пропионовая кислота", "Масляная кислота", "Муравьиная кислота", "Уксусная кислота"]},
            {"question": "C₂H₅COOH", "answer": "Пропионовая кислота",
             "options": ["Масляная кислота", "Пропионовая кислота", "Муравьиная кислота", "Уксусная кислота"]},
            {"question": "C₆H₁₂O₆", "answer": "Глюкоза", "options": ["Лактоза", "Глюкоза", "Фруктоза", "Сахароза"]},
            {"question": "C₁₂H₂₂O₁₁", "answer": "Сахароза", "options": ["Лактоза", "Сахароза", "Глюкоза", "Фруктоза"]},
            {"question": "C₆H₆", "answer": "Бензол", "options": ["Нафталин", "Бензол", "Толуол", "Ксилол"]},
            {"question": "C₇H₈", "answer": "Толуол", "options": ["Нафталин", "Толуол", "Бензол", "Ксилол"]},
            {"question": "C₈H₁₀", "answer": "Ксилол", "options": ["Нафталин", "Ксилол", "Бензол", "Толуол"]},
            {"question": "C₁₀H₈", "answer": "Нафталин", "options": ["Нафталин", "Бензол", "Толуол", "Ксилол"]}
        ],
        "nameToFormula": [
            {"question": "Вода", "answer": "H₂O", "options": ["H₂O", "NH₃", "CO₂", "CH₄"]},
            {"question": "Серная кислота", "answer": "H₂SO₄", "options": ["H₃PO₄", "H₂SO₄", "HCl", "HNO₃"]},
            {"question": "Аммиак", "answer": "NH₃", "options": ["CO₂", "CH₄", "NH₃", "H₂O"]},
            {"question": "Метан", "answer": "CH₄", "options": ["C₄H₁₀", "C₂H₆", "C₃H₈", "CH₄"]},
            {"question": "Углекислый газ", "answer": "CO₂", "options": ["CO₂", "NO₂", "CO", "SO₂"]},
            {"question": "Хлороводород", "answer": "HCl", "options": ["HF", "HCl", "HBr", "HI"]},
            {"question": "Азотная кислота", "answer": "HNO₃", "options": ["HClO₄", "H₂SO₄", "HNO₃", "H₃PO₄"]},
            {"question": "Фосфорная кислота", "answer": "H₃PO₄", "options": ["H₂CO₃", "HNO₃", "H₂SO₄", "H₃PO₄"]},
            {"question": "Уксусная кислота", "answer": "CH₃COOH",
             "options": ["CH₃COOH", "C₃H₇COOH", "HCOOH", "C₂H₅COOH"]},
            {"question": "Муравьиная кислота", "answer": "HCOOH",
             "options": ["C₃H₇COOH", "HCOOH", "CH₃COOH", "C₂H₅COOH"]},
            {"question": "Гидроксид натрия", "answer": "NaOH", "options": ["Mg(OH)₂", "KOH", "NaOH", "Ca(OH)₂"]},
            {"question": "Гидроксид калия", "answer": "KOH", "options": ["Al(OH)₃", "NaOH", "Ca(OH)₂", "KOH"]},
            {"question": "Гидроксид кальция", "answer": "Ca(OH)₂", "options": ["Ca(OH)₂", "Ba(OH)₂", "NaOH", "KOH"]},
            {"question": "Гидроксид алюминия", "answer": "Al(OH)₃",
             "options": ["Cu(OH)₂", "Al(OH)₃", "Fe(OH)₃", "Zn(OH)₂"]},
            {"question": "Оксид кальция", "answer": "CaO", "options": ["Al₂O₃", "MgO", "CaO", "Na₂O"]},
            {"question": "Оксид магния", "answer": "MgO", "options": ["ZnO", "CaO", "BaO", "MgO"]},
            {"question": "Оксид алюминия", "answer": "Al₂O₃", "options": ["Al₂O₃", "SiO₂", "Fe₂O₃", "Cr₂O₃"]},
            {"question": "Оксид железа(III)", "answer": "Fe₂O₃", "options": ["Cr₂O₃", "Fe₂O₃", "FeO", "Fe₃O₄"]},
            {"question": "Оксид углерода(II)", "answer": "CO", "options": ["CH₄", "CO₂", "CO", "C₃O₂"]},
            {"question": "Оксид серы(IV)", "answer": "SO₂", "options": ["H₂S", "H₂SO₄", "SO₃", "SO₂"]},
            {"question": "Оксид серы(VI)", "answer": "SO₃", "options": ["SO₃", "H₂SO₃", "SO₂", "H₂SO₄"]},
            {"question": "Оксид азота(II)", "answer": "NO", "options": ["N₂O₅", "NO", "NO₂", "N₂O"]},
            {"question": "Оксид азота(IV)", "answer": "NO₂", "options": ["N₂O₄", "NO", "N₂O", "NO₂"]},
            {"question": "Пероксид водорода", "answer": "H₂O₂", "options": ["H₃O", "H₂O₂", "H₂O", "HO₂"]},
            {"question": "Хлорид натрия", "answer": "NaCl", "options": ["MgCl₂", "KCl", "CaCl₂", "NaCl"]},
            {"question": "Хлорид калия", "answer": "KCl", "options": ["KCl", "RbCl", "NaCl", "LiCl"]},
            {"question": "Хлорид кальция", "answer": "CaCl₂", "options": ["SrCl₂", "CaCl₂", "MgCl₂", "BaCl₂"]},
            {"question": "Хлорид алюминия", "answer": "AlCl₃", "options": ["CuCl₂", "FeCl₃", "AlCl₃", "ZnCl₂"]},
            {"question": "Сульфат натрия", "answer": "Na₂SO₄", "options": ["MgSO₄", "K₂SO₄", "CaSO₄", "Na₂SO₄"]},
            {"question": "Сульфат калия", "answer": "K₂SO₄", "options": ["K₂SO₄", "CaSO₄", "Na₂SO₄", "(NH₄)₂SO₄"]},
            {"question": "Сульфат кальция", "answer": "CaSO₄", "options": ["SrSO₄", "CaSO₄", "BaSO₄", "MgSO₄"]},
            {"question": "Сульфат алюминия", "answer": "Al₂(SO₄)₃",
             "options": ["ZnSO₄", "Fe₂(SO₄)₃", "CuSO₄", "Al₂(SO₄)₃"]},
            {"question": "Карбонат натрия", "answer": "Na₂CO₃", "options": ["Na₂CO₃", "MgCO₃", "K₂CO₃", "CaCO₃"]},
            {"question": "Карбонат кальция", "answer": "CaCO₃", "options": ["SrCO₃", "CaCO₃", "MgCO₃", "BaCO₃"]},
            {"question": "Нитрат калия", "answer": "KNO₃", "options": ["NH₄NO₃", "NaNO₃", "Ca(NO₃)₂", "KNO₃"]},
            {"question": "Нитрат серебра", "answer": "AgNO₃", "options": ["AgNO₃", "Hg(NO₃)₂", "Cu(NO₃)₂", "Pb(NO₃)₂"]},
            {"question": "Фосфат кальция", "answer": "Ca₃(PO)₂",
             "options": ["Mg₃(PO)₂", "CaHPO₄", "Ca(H₂PO₄)₂", "Ca₃(PO)₂"]},
            {"question": "Сульфид железа(II)", "answer": "FeS", "options": ["FeS", "ZnS", "Fe₂S₃", "CuS"]},
            {"question": "Перманганат калия", "answer": "KMnO₄", "options": ["KNO₃", "KMnO₄", "K₂Cr₂O₇", "KClO₃"]},
            {"question": "Дихромат калия", "answer": "K₂Cr₂O₇", "options": ["KClO₄", "K₂CrO₄", "KMnO₄", "K₂Cr₂O₇"]},
            {"question": "Хромат натрия", "answer": "Na₂CrO₄", "options": ["Na₂CO₃", "Na₂Cr₂O₇", "Na₂SO₄", "Na₂CrO₄"]},
            {"question": "Гидрокарбонат натрия", "answer": "NaHCO₃",
             "options": ["Ca(HCO₃)₂", "NaHCO₃", "Na₂CO₃", "KHCO₃"]},
            {"question": "Сероводород", "answer": "H₂S", "options": ["HSO₃", "SO₂", "H₂SO₄", "H₂S"]},
            {"question": "Этанол", "answer": "C₂H₅OH", "options": ["C₄H₉OH", "C₂H₅OH", "CH₃OH", "C₃H₇OH"]},
            {"question": "Метанол", "answer": "CH₃OH", "options": ["C₄H₉OH", "CH₃OH", "C₂H₅OH", "C₃H₇OH"]},
            {"question": "Глюкоза", "answer": "C₆H₁₂O₆", "options": ["C₄H₈O₂", "C₁₂H₂₂O₁₁", "C₅H₁₀O₅", "C₆H₁₂O₆"]},
            {"question": "Сахароза", "answer": "C₁₂H₂₂O₁₁", "options": ["C₄H₈O₂", "C₁₂H₂₂O₁₁", "C₆H₁₂O₆", "C₅H₁₀O₅"]},
            {"question": "Бензол", "answer": "C₆H₆", "options": ["C₁₀H₈", "C₇H₈", "C₈H₁₀", "C₆H₆"]},
            {"question": "Толуол", "answer": "C₇H₈", "options": ["C₁₀H₈", "C₇H₈", "C₆H₆", "C₈H₁₀"]},
            {"question": "Ацетилен", "answer": "C₂H₂", "options": ["C₂H₆", "CH₄", "C₂H₄", "C₂H₂"]},
            {"question": "Этилен", "answer": "C₂H₄", "options": ["C₂H₆", "C₂H₄", "CH₄", "C₂H₂"]},
            {"question": "Пропан", "answer": "C₃H₈", "options": ["C₄H₁₀", "CH₄", "C₂H₆", "C₃H₈"]},
            {"question": "Бутан", "answer": "C₄H₁₀", "options": ["C₅H₁₂", "C₄H₁₀", "C₂H₆", "C₃H₈"]},
            {"question": "Пентан", "answer": "C₅H₁₂", "options": ["C₆H₁₄", "C₅H₁₂", "C₃H₈", "C₄H₁₀"]},
            {"question": "Гексан", "answer": "C₆H₁₄", "options": ["C₇H₁₆", "C₄H₁₀", "C₅H₁₂", "C₆H₁₄"]},
            {"question": "Ацетат натрия", "answer": "CH₃COONa",
             "options": ["C₂H₅COONa", "CH₃COONa", "CH₃COOK", "CH₃COOH"]},
            {"question": "Фторид кальция", "answer": "CaF₂", "options": ["MgF₂", "NaF", "KF", "CaF₂"]},
            {"question": "Бромид калия", "answer": "KBr", "options": ["MgBr₂", "KBr", "NaBr", "CaBr₂"]},
            {"question": "Иодид натрия", "answer": "NaI", "options": ["MgI₂", "NaI", "KI", "CaI₂"]},
            {"question": "Сульфид натрия", "answer": "Na₂S", "options": ["MgS", "K₂S", "CaS", "Na₂S"]},
            {"question": "Сульфит натрия", "answer": "Na₂SO₃", "options": ["Na₂CO₃", "Na₂SO₄", "Na₂S", "Na₂SO₃"]},
            {"question": "Тиосульфат натрия", "answer": "Na₂S₂O₃", "options": ["Na₂S", "Na₂SO₄", "Na₂SO₃", "Na₂S₂O₃"]},
            {"question": "Гипохлорит натрия", "answer": "NaClO", "options": ["NaClO₄", "NaClO", "NaClO₂", "NaClO₃"]},
            {"question": "Хлорат калия", "answer": "KClO₃", "options": ["KClO₄", "KClO₃", "KClO", "KClO₂"]},
            {"question": "Перхлорат натрия", "answer": "NaClO₄", "options": ["NaClO₄", "NaClO", "NaClO₂", "NaClO₃"]},
            {"question": "Цианид калия", "answer": "KCN", "options": ["Mg(CN)₂", "KCN", "NaCN", "Ca(CN)₂"]},
            {"question": "Силикат натрия", "answer": "Na₂SiO₃", "options": ["MgSiO₃", "Na₂SiO₃", "K₂SiO₃", "CaSiO₃"]},
            {"question": "Ацетат свинца(II)", "answer": "Pb(CH₃COO)₂",
             "options": ["Pb(NO₃)₂", "PbCl₂", "PbSO₄", "Pb(CH₃COO)₂"]},
            {"question": "Сульфат бария", "answer": "BaSO₄", "options": ["Ba(NO₃)₂", "BaSO₄", "BaCO₃", "BaCl₂"]},
            {"question": "Карбид кальция", "answer": "CaC₂", "options": ["Ca(OH)₂", "CaC₂", "CaCO₃", "CaO"]},
            {"question": "Гидрид лития", "answer": "LiH", "options": ["CaH₂", "LiH", "NaH", "KH"]},
            {"question": "Озон", "answer": "O₃", "options": ["CO₂", "O₃", "O₂", "H₂O₂"]},
            {"question": "Фосген", "answer": "COCl₂", "options": ["CHCl₃", "COCl₂", "CO₂", "CCl₄"]},
            {"question": "Хлороформ", "answer": "CHCl₃", "options": ["CH₃Cl", "CHCl₃", "CCl₄", "CH₂Cl₂"]},
            {"question": "Тетрахлорметан", "answer": "CCl₄", "options": ["CH₃Cl", "CCl₄", "CHCl₃", "CH₂Cl₂"]},
            {"question": "Формальдегид", "answer": "HCHO", "options": ["C₆H₅CHO", "HCHO", "CH₃CHO", "C₂H₅CHO"]},
            {"question": "Ацетон", "answer": "CH₃COCH₃", "options": ["CH₃COOH", "CH₃COCH", "CH₃CHO", "C₂H₅OH"]},
            {"question": "Мочевина", "answer": "CO(NH₂)₂", "options": ["(NH₄)₂SO₄", "CO(NH₂)₂", "NH₄Cl", "NH₄NO₃"]},
            {"question": "Гидроксид меди(II)", "answer": "Cu(OH)₂", "options": ["CuSO₄", "Cu(OH)₂", "CuO", "CuCl₂"]},
            {"question": "Оксид цинка", "answer": "ZnO", "options": ["Zn(OH)₂", "ZnO", "ZnCl₂", "ZnSO₄"]},
            {"question": "Сульфид свинца(II)", "answer": "PbS", "options": ["PbSO₄", "PbS", "PbO", "PbCl₂"]},
            {"question": "Нитрит натрия", "answer": "NaNO₂", "options": ["Na₂CO₃", "NaNO₂", "NaNO₃", "Na₂SO₃"]},
            {"question": "Пероксид натрия", "answer": "Na₂O₂", "options": ["NaH", "Na₂O₂", "Na₂O", "NaOH"]},
            {"question": "Гидрид кальция", "answer": "CaH₂", "options": ["CaCO₃", "CaH₂", "CaO", "Ca(OH)₂"]},
            {"question": "Карбид кремния", "answer": "SiC", "options": ["SiH₄", "SiC", "SiO₂", "SiCl₄"]},
            {"question": "Силицид магния", "answer": "Mg₂Si", "options": ["MgSO₄", "Mg₂Si", "MgO", "MgCl₂"]},
            {"question": "Фторид водорода", "answer": "HF", "options": ["HI", "HF", "HCl", "HBr"]},
            {"question": "Бромид водорода", "answer": "HBr", "options": ["HF", "HBr", "HCl", "HI"]},
            {"question": "Иодид водорода", "answer": "HI", "options": ["H₂S", "HI", "HCl", "HBr"]},
            {"question": "Сульфат меди(II)", "answer": "CuSO₄", "options": ["CuO", "CuSO₄", "CuCl₂", "Cu(NO₃)₂"]},
            {"question": "Нитрат меди(II)", "answer": "Cu(NO₃)₂", "options": ["CuO", "Cu(NO₃)₂", "CuSO₄", "CuCl₂"]},
            {"question": "Хлорид меди(II)", "answer": "CuCl₂", "options": ["CuO", "CuCl₂", "CuSO₄", "Cu(NO₃)₂"]},
            {"question": "Оксид меди(II)", "answer": "CuO", "options": ["CuSO₄", "CuO", "Cu₂O", "CuCl₂"]},
            {"question": "Оксид меди(I)", "answer": "Cu₂O", "options": ["CuSO₄", "Cu₂O", "CuO", "CuCl"]},
            {"question": "Сульфат железа(II)", "answer": "FeSO₄", "options": ["FeCl₃", "FeSO₄", "Fe₂(SO₄)₃", "FeCl₂"]},
            {"question": "Хлорид железа(III)", "answer": "FeCl₃", "options": ["Fe₂O₃", "FeCl₃", "FeCl₂", "FeSO₄"]},
            {"question": "Оксид хрома(III)", "answer": "Cr₂O₃", "options": ["K₂Cr₂O₇", "Cr₂O₃", "CrO", "CrO₃"]},
            {"question": "Оксид хрома(VI)", "answer": "CrO₃", "options": ["K₂CrO₄", "CrO₃", "CrO", "Cr₂O₃"]},
            {"question": "Дихромат аммония", "answer": "(NH₄)₂Cr₂O₇",
             "options": ["(NH₄)₂SO₄", "(NH₄)₂Cr₂O₇", "NH₄Cl", "NH₄NO₃"]},
            {"question": "Хромат калия", "answer": "K₂CrO₄", "options": ["KClO₄", "K₂CrO₄", "K₂Cr₂O₇", "KMnO₄"]},
            {"question": "Персульфат калия", "answer": "K₂S₂O₈", "options": ["K₂SO₃", "K₂S₂O₈", "K₂SO₄", "K₂S"]},
            {"question": "Тиоцианат калия", "answer": "KSCN", "options": ["KMnO₄", "KSCN", "KCN", "KClO₃"]},
            {"question": "Ферроцианид калия", "answer": "K₄[Fe(CN)₆]",
             "options": ["KCN", "K₄[Fe(CN)₆]", "K₃[Fe(CN)₆]", "KSCN"]},
            {"question": "Феррицианид калия", "answer": "K₃[Fe(CN)₆]",
             "options": ["KCN", "K₃[Fe(CN)₆]", "K₄[Fe(CN)₆]", "KSCN"]},
            {"question": "Гексацианоферрат(II) калия", "answer": "K₄[Fe(CN)₆]",
             "options": ["KMnO₄", "K₄[Fe(CN)₆]", "K₃[Fe(CN)₆]", "K₂Cr₂O₇"]},
            {"question": "Гексацианоферрат(III) калия", "answer": "K₃[Fe(CN)₆]",
             "options": ["KSCN", "K₃[Fe(CN)₆]", "K₄[Fe(CN)₆]", "K₂CrO₄"]}
        ],
        "valency": [
            {"question": "Валентность водорода", "answer": "I", "options": ["I", "IV", "II", "III"]},
            {"question": "Валентность кислорода", "answer": "II", "options": ["IV", "II", "I", "III"]},
            {"question": "Валентность азота в NH₃", "answer": "III", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность углерода в CH₄", "answer": "IV", "options": ["III", "I", "II", "IV"]},
            {"question": "Валентность серы в H₂S", "answer": "II", "options": ["II", "IV", "I", "III"]},
            {"question": "Валентность хлора в HCl", "answer": "I", "options": ["IV", "I", "II", "III"]},
            {"question": "Валентность фтора в HF", "answer": "I", "options": ["IV", "II", "I", "III"]},
            {"question": "Валентность азота в N₂", "answer": "III", "options": ["IV", "II", "III", "I"]},
            {"question": "Валентность фосфора в PH₃", "answer": "III", "options": ["IV", "I", "II", "III"]},
            {"question": "Валентность кремния в SiH₄", "answer": "IV", "options": ["III", "IV", "I", "II"]},
            {"question": "Валентность брома в HBr", "answer": "I", "options": ["IV", "II", "III", "I"]},
            {"question": "Валентность йода в HI", "answer": "I", "options": ["IV", "I", "II", "III"]},
            {"question": "Валентность серы в SO₂", "answer": "IV", "options": ["I", "VI", "II", "IV"]},
            {"question": "Валентность серы в SO₃", "answer": "VI", "options": ["I", "II", "IV", "VI"]},
            {"question": "Валентность азота в NO", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность азота в NO₂", "answer": "IV", "options": ["V", "II", "III", "IV"]},
            {"question": "Валентность углерода в CO₂", "answer": "IV", "options": ["I", "II", "III", "IV"]},
            {"question": "Валентность углерода в CCl₄", "answer": "IV", "options": ["III", "I", "II", "IV"]},
            {"question": "Валентность алюминия в AlCl₃", "answer": "III", "options": ["IV", "I", "II", "III"]},
            {"question": "Валентность натрия в NaCl", "answer": "I", "options": ["IV", "II", "III", "I"]},
            {"question": "Валентность калия в KBr", "answer": "I", "options": ["IV", "II", "I", "III"]},
            {"question": "Валентность магния в MgO", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность кальция в CaCl₂", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность бария в BaSO₄", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность железа в FeCl₂", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность железа в FeCl₃", "answer": "III", "options": ["I", "II", "IV", "III"]},
            {"question": "Валентность меди в CuO", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность цинка в ZnO", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность серебра в Ag₂O", "answer": "I", "options": ["IV", "II", "III", "I"]},
            {"question": "Валентность ртути в HgCl₂", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность марганца в MnO₂", "answer": "IV", "options": ["VII", "II", "III", "IV"]},
            {"question": "Валентность хрома в CrCl₃", "answer": "III", "options": ["VI", "II", "IV", "III"]},
            {"question": "Валентность свинца в PbO", "answer": "II", "options": ["III", "I", "IV", "II"]},
            {"question": "Валентность олова в SnCl₂", "answer": "II", "options": ["III", "I", "IV", "II"]},
            {"question": "Валентность вольфрама в WO₃", "answer": "VI", "options": ["III", "II", "IV", "VI"]},
            {"question": "Валентность ванадия в V₂O₅", "answer": "V", "options": ["IV", "II", "III", "V"]},
            {"question": "Валентность титана в TiO₂", "answer": "IV", "options": ["I", "II", "III", "IV"]},
            {"question": "Валентность никеля в NiO", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность кобальта в CoCl₂", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность бериллия в BeO", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность лития в Li₂O", "answer": "I", "options": ["IV", "II", "III", "I"]},
            {"question": "Валентность рубидия в RbCl", "answer": "I", "options": ["IV", "II", "III", "I"]},
            {"question": "Валентность цезия в CsF", "answer": "I", "options": ["IV", "II", "III", "I"]},
            {"question": "Валентность бора в BCl₃", "answer": "III", "options": ["IV", "I", "II", "III"]},
            {"question": "Валентность германия в GeH₄", "answer": "IV", "options": ["I", "II", "III", "IV"]},
            {"question": "Валентность сурьмы в SbCl₃", "answer": "III", "options": ["II", "V", "I", "III"]},
            {"question": "Валентность висмута в Bi₂O₃", "answer": "III", "options": ["II", "V", "I", "III"]},
            {"question": "Валентность мышьяка в AsH₃", "answer": "III", "options": ["I", "V", "II", "III"]},
            {"question": "Валентность селена в H₂Se", "answer": "II", "options": ["I", "IV", "VI", "II"]},
            {"question": "Валентность теллура в H₂Te", "answer": "II", "options": ["I", "IV", "VI", "II"]},
            {"question": "Валентность урана в UO₂", "answer": "IV", "options": ["II", "III", "VI", "IV"]},
            {"question": "Валентность тория в ThO₂", "answer": "IV", "options": ["I", "II", "III", "IV"]},
            {"question": "Валентность палладия в PdCl₂", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность платины в PtCl₄", "answer": "IV", "options": ["III", "II", "I", "IV"]},
            {"question": "Валентность золота в AuCl₃", "answer": "III", "options": ["IV", "I", "II", "III"]},
            {"question": "Валентность гафния в HfO₂", "answer": "IV", "options": ["I", "II", "III", "IV"]},
            {"question": "Валентность циркония в ZrCl₄", "answer": "IV", "options": ["I", "II", "III", "IV"]},
            {"question": "Валентность ниобия в NbCl₅", "answer": "V", "options": ["II", "III", "IV", "V"]},
            {"question": "Валентность молибдена в MoO₃", "answer": "VI", "options": ["III", "II", "IV", "VI"]},
            {"question": "Валентность технеция в Tc₂O₇", "answer": "VII", "options": ["II", "IV", "VI", "VII"]},
            {"question": "Валентность рения в Re₂O₇", "answer": "VII", "options": ["III", "IV", "VI", "VII"]},
            {"question": "Валентность тантала в TaCl₅", "answer": "V", "options": ["II", "III", "IV", "V"]},
            {"question": "Валентность осмия в OsO₄", "answer": "VIII", "options": ["II", "IV", "VI", "VIII"]},
            {"question": "Валентность рутения в RuO₄", "answer": "VIII", "options": ["II", "IV", "VI", "VIII"]},
            {"question": "Валентность родия в RhCl₃", "answer": "III", "options": ["I", "II", "IV", "III"]},
            {"question": "Валентность иридия в IrCl₃", "answer": "III", "options": ["I", "II", "IV", "III"]},
            {"question": "Валентность кадмия в CdO", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность индия в InCl₃", "answer": "III", "options": ["IV", "I", "II", "III"]},
            {"question": "Валентность таллия в TlCl", "answer": "I", "options": ["IV", "II", "III", "I"]},
            {"question": "Валентность олова в SnO₂", "answer": "IV", "options": ["III", "II", "I", "IV"]},
            {"question": "Валентность свинца в PbO₂", "answer": "IV", "options": ["III", "II", "I", "IV"]},
            {"question": "Валентность висмута в BiCl₅", "answer": "V", "options": ["II", "III", "I", "V"]},
            {"question": "Валентность сурьмы в SbCl₅", "answer": "V", "options": ["II", "III", "I", "V"]},
            {"question": "Валентность теллура в TeO₂", "answer": "IV", "options": ["I", "II", "VI", "IV"]},
            {"question": "Валентность полония в PoO₂", "answer": "IV", "options": ["I", "II", "VI", "IV"]},
            {"question": "Валентность актиния в AcCl₃", "answer": "III", "options": ["I", "II", "IV", "III"]},
            {"question": "Валентность протактиния в PaCl₅", "answer": "V", "options": ["II", "III", "IV", "V"]},
            {"question": "Валентность нептуния в NpO₂", "answer": "IV", "options": ["VI", "III", "V", "IV"]},
            {"question": "Валентность плутония в PuO₂", "answer": "IV", "options": ["VI", "III", "V", "IV"]},
            {"question": "Валентность америция в AmCl₃", "answer": "III", "options": ["V", "II", "IV", "III"]},
            {"question": "Валентность кюрия в CmCl₃", "answer": "III", "options": ["V", "II", "IV", "III"]},
            {"question": "Валентность берклия в BkCl₃", "answer": "III", "options": ["V", "II", "IV", "III"]},
            {"question": "Валентность калифорния в CfCl₃", "answer": "III", "options": ["V", "II", "IV", "III"]},
            {"question": "Валентность эйнштейния в EsCl₃", "answer": "III", "options": ["V", "II", "IV", "III"]},
            {"question": "Валентность фермия в FmCl₃", "answer": "III", "options": ["V", "II", "IV", "III"]},
            {"question": "Валентность менделевия в MdCl₃", "answer": "III", "options": ["V", "II", "IV", "III"]},
            {"question": "Валентность нобелия в NoCl₃", "answer": "III", "options": ["V", "II", "IV", "III"]},
            {"question": "Валентность лоуренсия в LrCl₃", "answer": "III", "options": ["V", "II", "IV", "III"]},
            {"question": "Валентность резерфордия в RfCl₄", "answer": "IV", "options": ["II", "III", "V", "IV"]},
            {"question": "Валентность дубния в DbCl₅", "answer": "V", "options": ["VI", "III", "IV", "V"]},
            {"question": "Валентность сиборгия в SgO₃", "answer": "VI", "options": ["III", "IV", "V", "VI"]},
            {"question": "Валентность бория в Bh₂O₇", "answer": "VII", "options": ["IV", "V", "VI", "VII"]},
            {"question": "Валентность хассия в HsO₄", "answer": "VIII", "options": ["IV", "VI", "VII", "VIII"]},
            {"question": "Валентность мейтнерия в MtCl₄", "answer": "IV", "options": ["V", "II", "III", "IV"]},
            {"question": "Валентность дармштадтия в DsCl₄", "answer": "IV", "options": ["V", "II", "III", "IV"]},
            {"question": "Валентность рентгения в RgCl", "answer": "I", "options": ["IV", "II", "III", "I"]},
            {"question": "Валентность коперниция в CnCl₂", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность нихония в NhCl₃", "answer": "III", "options": ["IV", "I", "II", "III"]},
            {"question": "Валентность флеровия в FlCl₂", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность московия в McCl₃", "answer": "III", "options": ["IV", "I", "II", "III"]},
            {"question": "Валентность ливермория в LvCl₂", "answer": "II", "options": ["IV", "I", "III", "II"]},
            {"question": "Валентность теннессина в TsCl", "answer": "I", "options": ["IV", "II", "III", "I"]},
            {"question": "Валентность оганесона (предположительно)", "answer": "0", "options": ["IV", "I", "II", "0"]}
        ],
        "oxidation": [
            {"question": "Степень окисления кислорода в H₂O", "answer": "-2", "options": ["+2", "-2", "-1", "0"]},
            {"question": "Степень окисления водорода в HCl", "answer": "+1", "options": ["+2", "-1", "0", "+1"]},
            {"question": "Степень окисления натрия в NaCl", "answer": "+1", "options": ["+2", "-1", "0", "+1"]},
            {"question": "Степень окисления хлора в Cl₂", "answer": "0", "options": ["+2", "-1", "+1", "0"]},
            {"question": "Степень окисления магния в MgO", "answer": "+2", "options": ["-2", "+1", "0", "+2"]},
            {"question": "Степень окисления алюминия в Al₂O₃", "answer": "+3", "options": ["+2", "-3", "0", "+3"]},
            {"question": "Степень окисления серы в H₂S", "answer": "-2", "options": ["+2", "-1", "0", "-2"]},
            {"question": "Степень окисления азота в NH₃", "answer": "-3", "options": ["+5", "0", "+3", "-3"]},
            {"question": "Степень окисления углерода в CH₄", "answer": "-4", "options": ["+4", "0", "+2", "-4"]},
            {"question": "Степень окисления фтора в HF", "answer": "-1", "options": ["+2", "0", "+1", "-1"]},
            {"question": "Степень окисления серы в SO₂", "answer": "+4", "options": ["0", "-2", "+6", "+4"]},
            {"question": "Степень окисления азота в NO", "answer": "+2", "options": ["0", "-3", "+5", "+2"]},
            {"question": "Степень окисления хрома в Cr₂O₃", "answer": "+3", "options": ["0", "+2", "+6", "+3"]},
            {"question": "Степень окисления марганца в MnO₂", "answer": "+4", "options": ["0", "+2", "+7", "+4"]},
            {"question": "Степень окисления железа в Fe₂O₃", "answer": "+3", "options": ["0", "+2", "+4", "+3"]},
            {"question": "Степень окисления углерода в CO₂", "answer": "+4", "options": ["0", "-4", "+2", "+4"]},
            {"question": "Степень окисления меди в CuO", "answer": "+2", "options": ["0", "+1", "+3", "+2"]},
            {"question": "Степень окисления свинца в PbO₂", "answer": "+4", "options": ["0", "+2", "+6", "+4"]},
            {"question": "Степень окисления серы в SO₃", "answer": "+6", "options": ["0", "+4", "-2", "+6"]},
            {"question": "Степень окисления азота в N₂O₅", "answer": "+5", "options": ["0", "+3", "-3", "+5"]},
            {"question": "Степень окисления серы в H₂SO₄", "answer": "+6", "options": ["0", "+4", "-2", "+6"]},
            {"question": "Степень окисления азота в HNO₃", "answer": "+5", "options": ["0", "+3", "-3", "+5"]},
            {"question": "Степень окисления фосфора в H₃PO₄", "answer": "+5", "options": ["0", "+3", "-3", "+5"]},
            {"question": "Степень окисления хлора в HClO₄", "answer": "+7", "options": ["-1", "+1", "+5", "+7"]},
            {"question": "Степень окисления серы в H₂SO₃", "answer": "+4", "options": ["0", "+6", "-2", "+4"]},
            {"question": "Степень окисления хрома в K₂Cr₂O₇", "answer": "+6", "options": ["0", "+3", "+2", "+6"]},
            {"question": "Степень окисления марганца в KMnO₄", "answer": "+7", "options": ["0", "+2", "+4", "+7"]},
            {"question": "Степень окисления железа в Fe(OH)₃", "answer": "+3", "options": ["0", "+2", "+4", "+3"]},
            {"question": "Степень окисления меди в Cu(OH)₂", "answer": "+2", "options": ["0", "+1", "+3", "+2"]},
            {"question": "Степень окисления азота в NH₄OH", "answer": "-3", "options": ["0", "+3", "+5", "-3"]},
            {"question": "Степень окисления серы в Na₂SO₄", "answer": "+6", "options": ["0", "+4", "-2", "+6"]},
            {"question": "Степень окисления азота в NaNO₃", "answer": "+5", "options": ["0", "+3", "-3", "+5"]},
            {"question": "Степень окисления углерода в CaCO₃", "answer": "+4", "options": ["0", "-4", "+2", "+4"]},
            {"question": "Степень окисления хлора в NaClO", "answer": "+1", "options": ["+7", "-1", "+5", "+1"]},
            {"question": "Степень окисления хлора в NaClO₃", "answer": "+5", "options": ["+7", "-1", "+1", "+5"]},
            {"question": "Степень окисления железа в FeSO₄", "answer": "+2", "options": ["0", "+3", "+4", "+2"]},
            {"question": "Степень окисления меди в CuCl₂", "answer": "+2", "options": ["0", "+1", "+3", "+2"]},
            {"question": "Степень окисления алюминия в AlCl₃", "answer": "+3", "options": ["0", "+1", "+5", "+3"]},
            {"question": "Степень окисления серебра в AgNO₃", "answer": "+1", "options": ["0", "+2", "+3", "+1"]},
            {"question": "Степень окисления цинка в ZnSO₄", "answer": "+2", "options": ["0", "+1", "+3", "+2"]},
            {"question": "Степень окисления кислорода в H₂O₂", "answer": "-1", "options": ["+1", "-2", "0", "-1"]},
            {"question": "Степень окисления калия в KO₂", "answer": "+1", "options": ["0", "+2", "-1", "+1"]},
            {"question": "Степень окисления кислорода в Na₂O₂", "answer": "-1", "options": ["+1", "-2", "0", "-1"]},
            {"question": "Степень окисления углерода в C₂H₅OH", "answer": "-2", "options": ["+4", "-4", "+2", "-2"]},
            {"question": "Степень окисления серы в Na₂S₂O₃", "answer": "+2", "options": ["0", "+4", "+6", "+2"]},
            {"question": "Степень окисления железа в Fe₃O₄", "answer": "+8/3", "options": ["0", "+2", "+3", "+8/3"]},
            {"question": "Степень окисления азота в NH₄NO₃ (в NH₄⁺)", "answer": "-3",
             "options": ["0", "+5", "+3", "-3"]},
            {"question": "Степень окисления азота в NH₄NO₃ (в NO₃⁻)", "answer": "+5",
             "options": ["0", "-3", "+3", "+5"]},
            {"question": "Степень окисления серы в Na₂S₄O₆", "answer": "+2.5", "options": ["+6", "+2", "+4", "+2.5"]},
            {"question": "Степень окисления углерода в C₆H₁₂O₆", "answer": "0", "options": ["+4", "-4", "+2", "0"]}
        ],
        "bond": [
            {"question": "Какой тип реакции: 2H₂ + O₂ → 2H₂O?", "answer": "Соединения",
             "options": ["Обмена", "Разложения", "Замещения", "Соединения"]},
            {"question": "Какой тип реакции: S + O₂ → SO₂?", "answer": "Соединения",
             "options": ["Обмена", "Разложения", "Замещения", "Соединения"]},
            {"question": "Какой тип реакции: 2Na + Cl₂ → 2NaCl?", "answer": "Соединения",
             "options": ["Обмена", "Разложения", "Замещения", "Соединения"]},
            {"question": "Какой тип реакции: CaO + H₂O → Ca(OH)₂?", "answer": "Соединения",
             "options": ["Обмена", "Разложения", "Замещения", "Соединения"]},
            {"question": "Какой тип реакции: 4Fe + 3O₂ → 2Fe₂O₃?", "answer": "Соединения",
             "options": ["Обмена", "Разложения", "Замещения", "Соединения"]},
            {"question": "Какой тип реакции: 2H₂O → 2H₂ + O₂?", "answer": "Разложения",
             "options": ["Обмена", "Соединения", "Замещения", "Разложения"]},
            {"question": "Какой тип реакции: 2HgO → 2Hg + O₂?", "answer": "Разложения",
             "options": ["Обмена", "Соединения", "Замещения", "Разложения"]},
            {"question": "Какой тип реакции: CaCO₃ → CaO + CO₂?", "answer": "Разложения",
             "options": ["Обмена", "Соединения", "Замещения", "Разложения"]},
            {"question": "Какой тип реакции: 2KClO₃ → 2KCl + 3O₂?", "answer": "Разложения",
             "options": ["Обмена", "Соединения", "Замещения", "Разложения"]},
            {"question": "Какой тип реакции: 2Ag₂O → 4Ag + O₂?", "answer": "Разложения",
             "options": ["Обмена", "Соединения", "Замещения", "Разложения"]},
            {"question": "Какой тип реакции: Zn + 2HCl → ZnCl₂ + H₂?", "answer": "Замещения",
             "options": ["Обмена", "Соединения", "Разложения", "Замещения"]},
            {"question": "Какой тип реакции: Fe + CuSO₄ → FeSO₄ + Cu?", "answer": "Замещения",
             "options": ["Обмена", "Соединения", "Разложения", "Замещения"]},
            {"question": "Какой тип реакции: 2Al + 3H₂SO₄ → Al₂(SO₄)₃ + 3H₂?", "answer": "Замещения",
             "options": ["Обмена", "Соединения", "Разложения", "Замещения"]},
            {"question": "Какой тип реакции: Cl₂ + 2NaBr → 2NaCl + Br₂?", "answer": "Замещения",
             "options": ["Обмена", "Соединения", "Разложения", "Замещения"]},
            {"question": "Какой тип реакции: Mg + 2AgNO₃ → Mg(NO₃)₂ + 2Ag?", "answer": "Замещения",
             "options": ["Обмена", "Соединения", "Разложения", "Замещения"]},
            {"question": "Какой тип реакции: HCl + NaOH → NaCl + H₂O?", "answer": "Обмена",
             "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
            {"question": "Какой тип реакции: AgNO₃ + NaCl → AgCl↓ + NaNO₃?", "answer": "Обмена",
             "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
            {"question": "Какой тип реакции: BaCl₂ + Na₂SO₄ → BaSO₄↓ + 2NaCl?", "answer": "Обмена",
             "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
            {"question": "Какой тип реакции: H₂SO₄ + 2KOH → K₂SO₄ + 2H₂O?", "answer": "Обмена",
             "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
            {"question": "Какой тип реакции: CaCO₃ + 2HCl → CaCl₂ + H₂O + CO₂↑?", "answer": "Обмена",
             "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
            {"question": "Какой тип реакции: CH₄ + 2O₂ → CO₂ + 2H₂O?", "answer": "Горения",
             "options": ["Обмена", "Нейтрализации", "Разложения", "Горения"]},
            {"question": "Какой тип реакции: C + O₂ → CO₂?", "answer": "Горения",
             "options": ["Обмена", "Нейтрализации", "Разложения", "Горения"]},
            {"question": "Какой тип реакции: HCl + KOH → KCl + H₂O?", "answer": "Нейтрализации",
             "options": ["Обмена", "Горения", "Разложения", "Нейтрализации"]},
            {"question": "Какой тип реакции: 2H₂ + O₂ → 2H₂O + энергия?", "answer": "Экзотермическая",
             "options": ["Обратимая", "Эндотермическая", "Каталитическая", "Экзотермическая"]},
            {"question": "Какой тип реакции: N₂ + 3H₂ ⇌ 2NH₃?", "answer": "Обратимая",
             "options": ["Экзотермическая", "Эндотермическая", "Каталитическая", "Обратимая"]},
            {"question": "Какой тип реакции: 2KClO₃ → 2KCl + 3O₂↑ (с нагреванием)?", "answer": "Разложения",
             "options": ["Обмена", "Соединения", "Замещения", "Разложения"]},
            {"question": "Какой тип реакции: CuO + H₂ → Cu + H₂O?", "answer": "Восстановления",
             "options": ["Обмена", "Окисления", "Замещения", "Восстановления"]},
            {"question": "Какой тип реакции: 2Fe + 3Cl₂ → 2FeCl₃?", "answer": "Соединения",
             "options": ["Обмена", "Разложения", "Замещения", "Соединения"]},
            {"question": "Какой тип реакции: 2Na + 2H₂O → 2NaOH + H₂↑?", "answer": "Замещения",
             "options": ["Обмена", "Соединения", "Разложения", "Замещения"]},
            {"question": "Какой тип реакции: CaO + CO₂ → CaCO₃?", "answer": "Соединения",
             "options": ["Обмена", "Разложения", "Замещения", "Соединения"]}
        ],
        "atomicmass": [
            {"question": "Атомная масса водорода (H)", "answer": "1", "options": ["4", "2", "3", "1"]},
            {"question": "Атомная масса гелия (He)", "answer": "4", "options": ["5", "2", "3", "4"]},
            {"question": "Атомная масса лития (Li)", "answer": "7", "options": ["9", "6", "8", "7"]},
            {"question": "Атомная масса бериллия (Be)", "answer": "9", "options": ["11", "8", "10", "9"]},
            {"question": "Атомная масса бора (B)", "answer": "11", "options": ["13", "10", "12", "11"]},
            {"question": "Атомная масса углерода (C)", "answer": "12", "options": ["15", "13", "14", "12"]},
            {"question": "Атомная масса азота (N)", "answer": "14", "options": ["16", "13", "15", "14"]},
            {"question": "Атомная масса кислорода (O)", "answer": "16", "options": ["18", "15", "17", "16"]},
            {"question": "Атомная масса фтора (F)", "answer": "19", "options": ["21", "18", "20", "19"]},
            {"question": "Атомная масса неона (Ne)", "answer": "20", "options": ["22", "19", "21", "20"]},
            {"question": "Атомная масса натрия (Na)", "answer": "23", "options": ["25", "22", "24", "23"]},
            {"question": "Атомная масса магния (Mg)", "answer": "24", "options": ["26", "23", "25", "24"]},
            {"question": "Атомная масса алюминия (Al)", "answer": "27", "options": ["29", "26", "28", "27"]},
            {"question": "Атомная масса кремния (Si)", "answer": "28", "options": ["30", "27", "29", "28"]},
            {"question": "Атомная масса фосфора (P)", "answer": "31", "options": ["33", "30", "32", "31"]},
            {"question": "Атомная масса серы (S)", "answer": "32", "options": ["34", "31", "33", "32"]},
            {"question": "Атомная масса хлора (Cl)", "answer": "35.5", "options": ["36", "34", "35", "35.5"]},
            {"question": "Атомная масса аргона (Ar)", "answer": "40", "options": ["41", "38", "39", "40"]},
            {"question": "Атомная масса калия (K)", "answer": "39", "options": ["41", "38", "40", "39"]},
            {"question": "Атомная масса кальция (Ca)", "answer": "40", "options": ["42", "39", "41", "40"]},
            {"question": "Атомная масса скандия (Sc)", "answer": "45", "options": ["47", "44", "46", "45"]},
            {"question": "Атомная масса титана (Ti)", "answer": "48", "options": ["50", "47", "49", "48"]},
            {"question": "Атомная масса ванадия (V)", "answer": "51", "options": ["53", "50", "52", "51"]},
            {"question": "Атомная масса хрома (Cr)", "answer": "52", "options": ["54", "51", "53", "52"]},
            {"question": "Атомная масса марганца (Mn)", "answer": "55", "options": ["57", "54", "56", "55"]},
            {"question": "Атомная масса железа (Fe)", "answer": "56", "options": ["58", "55", "57", "56"]},
            {"question": "Атомная масса кобальта (Co)", "answer": "59", "options": ["61", "58", "60", "59"]},
            {"question": "Атомная масса никеля (Ni)", "answer": "59", "options": ["61", "58", "60", "59"]},
            {"question": "Атомная масса меди (Cu)", "answer": "63.5", "options": ["64", "62", "63", "63.5"]},
            {"question": "Атомная масса цинка (Zn)", "answer": "65", "options": ["67", "64", "66", "65"]},
            {"question": "Атомная масса галлия (Ga)", "answer": "70", "options": ["72", "69", "71", "70"]},
            {"question": "Атомная масса германия (Ge)", "answer": "73", "options": ["75", "72", "74", "73"]},
            {"question": "Атомная масса мышьяка (As)", "answer": "75", "options": ["77", "74", "76", "75"]},
            {"question": "Атомная масса селена (Se)", "answer": "79", "options": ["81", "78", "80", "79"]},
            {"question": "Атомная масса брома (Br)", "answer": "80", "options": ["82", "79", "81", "80"]},
            {"question": "Атомная масса криптона (Kr)", "answer": "84", "options": ["86", "83", "85", "84"]},
            {"question": "Атомная масса рубидия (Rb)", "answer": "85.5", "options": ["86", "84", "85", "85.5"]},
            {"question": "Атомная масса стронция (Sr)", "answer": "88", "options": ["90", "87", "89", "88"]},
            {"question": "Атомная масса иттрия (Y)", "answer": "89", "options": ["91", "88", "90", "89"]},
            {"question": "Атомная масса циркония (Zr)", "answer": "91", "options": ["93", "90", "92", "91"]},
            {"question": "Атомная масса ниобия (Nb)", "answer": "93", "options": ["95", "92", "94", "93"]},
            {"question": "Атомная масса молибдена (Mo)", "answer": "96", "options": ["98", "95", "97", "96"]},
            {"question": "Атомная масса технеция (Tc)", "answer": "98", "options": ["100", "97", "99", "98"]},
            {"question": "Атомная масса рутения (Ru)", "answer": "101", "options": ["103", "100", "102", "101"]},
            {"question": "Атомная масса родия (Rh)", "answer": "103", "options": ["105", "102", "104", "103"]},
            {"question": "Атомная масса палладия (Pd)", "answer": "106", "options": ["108", "105", "107", "106"]},
            {"question": "Атомная масса серебра (Ag)", "answer": "108", "options": ["110", "107", "109", "108"]},
            {"question": "Атомная масса кадмия (Cd)", "answer": "112", "options": ["114", "111", "113", "112"]},
            {"question": "Атомная масса индия (In)", "answer": "115", "options": ["117", "114", "116", "115"]},
            {"question": "Атомная масса олова (Sn)", "answer": "119", "options": ["121", "118", "120", "119"]},
            {"question": "Атомная масса сурьмы (Sb)", "answer": "122", "options": ["124", "121", "123", "122"]},
            {"question": "Атомная масса теллура (Te)", "answer": "128", "options": ["130", "127", "129", "128"]},
            {"question": "Атомная масса йода (I)", "answer": "127", "options": ["129", "126", "128", "127"]},
            {"question": "Атомная масса ксенона (Xe)", "answer": "131", "options": ["133", "130", "132", "131"]},
            {"question": "Атомная масса цезия (Cs)", "answer": "133", "options": ["135", "132", "134", "133"]},
            {"question": "Атомная масса бария (Ba)", "answer": "137", "options": ["139", "136", "138", "137"]},
            {"question": "Атомная масса лантана (La)", "answer": "139", "options": ["141", "138", "140", "139"]},
            {"question": "Атомная масса церия (Ce)", "answer": "140", "options": ["142", "139", "141", "140"]},
            {"question": "Атомная масса празеодима (Pr)", "answer": "141", "options": ["143", "140", "142", "141"]},
            {"question": "Атомная масса неодима (Nd)", "answer": "144", "options": ["146", "143", "145", "144"]},
            {"question": "Атомная масса прометия (Pm)", "answer": "145", "options": ["147", "144", "146", "145"]},
            {"question": "Атомная масса самария (Sm)", "answer": "150", "options": ["152", "149", "151", "150"]},
            {"question": "Атомная масса европия (Eu)", "answer": "152", "options": ["154", "151", "153", "152"]},
            {"question": "Атомная масса гадолиния (Gd)", "answer": "157", "options": ["159", "156", "158", "157"]},
            {"question": "Атомная масса тербия (Tb)", "answer": "159", "options": ["161", "158", "160", "159"]},
            {"question": "Атомная масса диспрозия (Dy)", "answer": "163", "options": ["165", "162", "164", "163"]},
            {"question": "Атомная масса гольмия (Ho)", "answer": "165", "options": ["167", "164", "166", "165"]},
            {"question": "Атомная масса эрбия (Er)", "answer": "167", "options": ["169", "166", "168", "167"]},
            {"question": "Атомная масса тулия (Tm)", "answer": "169", "options": ["171", "168", "170", "169"]},
            {"question": "Атомная масса иттербия (Yb)", "answer": "173", "options": ["175", "172", "174", "173"]},
            {"question": "Атомная масса лютеция (Lu)", "answer": "175", "options": ["177", "174", "176", "175"]},
            {"question": "Атомная масса гафния (Hf)", "answer": "178", "options": ["180", "177", "179", "178"]},
            {"question": "Атомная масса тантала (Ta)", "answer": "181", "options": ["183", "180", "182", "181"]},
            {"question": "Атомная масса вольфрама (W)", "answer": "184", "options": ["186", "183", "185", "184"]},
            {"question": "Атомная масса рения (Re)", "answer": "186", "options": ["188", "185", "187", "186"]},
            {"question": "Атомная масса осмия (Os)", "answer": "190", "options": ["192", "189", "191", "190"]},
            {"question": "Атомная масса иридия (Ir)", "answer": "192", "options": ["194", "191", "193", "192"]},
            {"question": "Атомная масса платины (Pt)", "answer": "195", "options": ["197", "194", "196", "195"]},
            {"question": "Атомная масса золота (Au)", "answer": "197", "options": ["199", "196", "198", "197"]},
            {"question": "Атомная масса ртути (Hg)", "answer": "201", "options": ["203", "200", "202", "201"]},
            {"question": "Атомная масса таллия (Tl)", "answer": "204", "options": ["206", "203", "205", "204"]},
            {"question": "Атомная масса свинца (Pb)", "answer": "207", "options": ["209", "206", "208", "207"]},
            {"question": "Атомная масса висмута (Bi)", "answer": "209", "options": ["211", "208", "210", "209"]},
            {"question": "Атомная масса полония (Po)", "answer": "209", "options": ["211", "208", "210", "209"]},
            {"question": "Атомная масса астата (At)", "answer": "210", "options": ["212", "209", "211", "210"]},
            {"question": "Атомная масса радона (Rn)", "answer": "222", "options": ["223", "220", "221", "222"]},
            {"question": "Атомная масса франция (Fr)", "answer": "223", "options": ["225", "222", "224", "223"]},
            {"question": "Атомная масса радия (Ra)", "answer": "226", "options": ["228", "225", "227", "226"]},
            {"question": "Атомная масса актиния (Ac)", "answer": "227", "options": ["229", "226", "228", "227"]},
            {"question": "Атомная масса тория (Th)", "answer": "232", "options": ["234", "231", "233", "232"]},
            {"question": "Атомная масса протактиния (Pa)", "answer": "231", "options": ["233", "230", "232", "231"]},
            {"question": "Атомная масса урана (U)", "answer": "238", "options": ["240", "237", "239", "238"]},
            {"question": "Атомная масса нептуния (Np)", "answer": "237", "options": ["239", "236", "238", "237"]},
            {"question": "Атомная масса плутония (Pu)", "answer": "244", "options": ["246", "243", "245", "244"]},
            {"question": "Атомная масса америция (Am)", "answer": "243", "options": ["245", "242", "244", "243"]},
            {"question": "Атомная масса кюрия (Cm)", "answer": "247", "options": ["249", "246", "248", "247"]},
            {"question": "Атомная масса берклия (Bk)", "answer": "247", "options": ["249", "246", "248", "247"]},
            {"question": "Атомная масса калифорния (Cf)", "answer": "251", "options": ["253", "250", "252", "251"]},
            {"question": "Атомная масса эйнштейния (Es)", "answer": "252", "options": ["254", "251", "253", "252"]},
            {"question": "Атомная масса фермия (Fm)", "answer": "257", "options": ["259", "256", "258", "257"]}
        ],
        "OVR": [
            {"question": "Какой из этих элементов является сильным окислителем?", "answer": "F₂",
             "options": ["Ca", "Na", "H₂", "F₂"]},
            {"question": "Какой из этих элементов является типичным восстановителем?", "answer": "Na",
             "options": ["F₂", "Cl₂", "O₂", "Na"]},
            {"question": "Какое вещество в реакции выступает окислителем: 2Na + Cl₂ → 2NaCl?", "answer": "Cl₂",
             "options": ["Никакое", "Na", "Оба", "Cl₂"]},
            {"question": "Какое вещество в реакции выступает восстановителем: Zn + CuSO₄ → ZnSO₄ + Cu?", "answer": "Zn",
             "options": ["Никакое", "CuSO₄", "Оба", "Zn"]},
            {"question": "Какой ион является окислителем в реакции: Fe²⁺ → Fe³⁺ + e?", "answer": "Fe³⁺",
             "options": ["Никакой", "Fe²⁺", "Оба", "Fe³⁺"]},
            {"question": "Что является окислителем в реакции горения метана: CH₄ + 2O₂ → CO₂ + 2H₂O?", "answer": "O₂",
             "options": ["H₂O", "CH₄", "CO₂", "O₂"]},
            {"question": "Что является восстановителем в реакции: 2H₂S + SO₂ → 3S + 2H₂O?", "answer": "H₂S",
             "options": ["Никакое", "SO₂", "Оба", "H₂S"]},
            {"question": "Какой процесс происходит с азотом в реакции: NH₃ → NO?", "answer": "Окисление",
             "options": ["Диспропорционирование", "Восстановление", "Ни то, ни другое", "Окисление"]},
            {"question": "Как изменяется степень окисления марганца в реакции: KMnO₄ → Mn²⁺?", "answer": "Уменьшается",
             "options": ["Сначала увеличивается, потом уменьшается", "Увеличивается", "Не изменяется", "Уменьшается"]},
            {"question": "Какое вещество может быть только окислителем?", "answer": "F₂",
             "options": ["SO₂", "H₂", "Fe²⁺", "F₂"]},
            {"question": "Какое из этих соединений - сильный окислитель?", "answer": "KMnO₄",
             "options": ["CO₂", "NaCl", "H₂O", "KMnO₄"]},
            {"question": "Какой окислитель используется в органическом синтезе для мягкого окисления?",
             "answer": "K₂Cr₂O₇", "options": ["Cl₂", "O₃", "HNO₃", "K₂Cr₂O₇"]},
            {
                "question": "Какое вещество является окислителем в реакции: 2KMnO₄ + 5H₂SO₃ → 2MnSO₄ + K₂SO₄ + 3H₂SO₄ + 2H₂O?",
                "answer": "KMnO₄", "options": ["Никакое", "H₂SO₃", "Оба", "KMnO₄"]},
            {"question": "Какой процесс происходит с серой в реакции: H₂SO₃ → H₂SO₄?", "answer": "Окисление",
             "options": ["Диcпропорционирование", "Восстановление", "Ни то, ни другое", "Окисление"]},
            {"question": "Какое вещество может быть как окислителем, так и восстановителем?", "answer": "H₂O₂",
             "options": ["Na", "KMnO₄", "F₂", "H₂O₂"]},
            {"question": "Какое из этих веществ - типичный восстановитель?", "answer": "H₂",
             "options": ["F₂", "O₂", "Cl₂", "H₂"]},
            {"question": "Какой металл - самый сильный восстановитель?", "answer": "Li",
             "options": ["Cu", "Au", "Fe", "Li"]},
            {"question": "Какое вещество является восстановителем в реакции: Sn²⁺ → Sn⁴⁺ + 2e⁻?", "answer": "Sn²⁺",
             "options": ["Никакое", "Sn⁴⁺", "Оба", "Sn²⁺"]},
            {"question": "Какой процесс происходит с железом в реакции: Fe²⁺ → Fe³⁺ + e⁻?", "answer": "Окисление",
             "options": ["Диcпропорционирование", "Восстановление", "Ни то, ни другое", "Окисление"]},
            {"question": "Какое вещество может быть только восстановителем?", "answer": "Na",
             "options": ["SO₂", "O₂", "H₂O₂", "Na"]},
            {"question": "Какое вещество в реакции диспропорционирования является и окислителем, и восстановителем?",
             "answer": "Cl₂", "options": ["O₂", "NaCl", "HCl", "Cl₂"]},
            {"question": "Какой процесс происходит с пероксидом водорода в реакции: 2H₂O₂ → 2H₂O + O₂?",
             "answer": "Диспропорционирование",
             "options": ["Ничего", "Окисление", "Восстановление", "Диспропорционирование"]},
            {"question": "Какое вещество является окислителем в реакции: CuO + H₂ → Cu + H₂O?", "answer": "CuO",
             "options": ["Никакое", "H₂", "Оба", "CuO"]},
            {"question": "Как изменяется степень окисления хрома в реакции: K₂Cr₂O₇ → Cr³⁺?", "answer": "Уменьшается",
             "options": ["Сначала увеличивается, потом уменьшается", "Увеличивается", "Не изменяется", "Уменьшается"]},
            {"question": "Какое вещество может выступать как окислителем, так и восстановителем?", "answer": "SO₂",
             "options": ["KMnO₄", "Na", "F₂", "SO₂"]},
            {"question": "Что является восстановителем в реакции: 2FeCl₃ + H₂S → 2FeCl₂ + S + 2HCl?", "answer": "H₂S",
             "options": ["Никакое", "FeCl₃", "Оба", "H₂S"]},
            {"question": "Какой процесс происходит с йодом в реакции: I₂ → 2I⁻?", "answer": "Восстановление",
             "options": ["Диcпропорционирование", "Окисление", "Ни то, ни другое", "Восстановление"]},
            {"question": "Какое вещество является окислителем в реакции: 2KBr + Cl₂ → 2KCl + Br₂?", "answer": "Cl₂",
             "options": ["Никакое", "KBr", "Оба", "Cl₂"]},
            {"question": "Как изменяется степень окисления серы в реакции: H₂SO₄ → SO₂?", "answer": "Уменьшается",
             "options": ["Сначала увеличивается, потом уменьшается", "Увеличивается", "Не изменяется", "Уменьшается"]},
            {"question": "Какое вещество может быть только окислителем?", "answer": "O₃",
             "options": ["SO₂", "H₂", "H₂O₂", "O₃"]}
        ]
    }


QUIZ_DATA = load_quiz_data()


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=120)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password',
                                                                                             message='Пароли должны совпадать')])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


rooms = {}


def send_question(room_id):
    room = rooms[room_id]
    q_index = room['current_question']
    if q_index >= len(room['questions']):
        end_game(room_id)
        return
    question_data = room['questions'][q_index].copy()
    random.shuffle(question_data['options'])
    emit('new_question', {
        'question_num': q_index + 1,
        'total': len(room['questions']),
        'question': question_data['question'],
        'options': question_data['options']
    }, room=room_id)
    room['answers'] = {}


def check_answer_in_room(room, question_index, answer):
    questions = room.get('questions', [])
    if question_index >= len(questions):
        return False
    return answer == questions[question_index]['answer']


def start_game(room_id):
    room = rooms[room_id]
    theme = room['theme']
    available_questions = QUIZ_DATA.get(theme, QUIZ_DATA.get("formulaToName", []))
    if not available_questions:
        emit('error', {'message': 'Нет вопросов для выбранной темы'})
        return
    questions_copy = available_questions.copy()
    random.shuffle(questions_copy)
    room['questions'] = questions_copy[:10]
    room['game_started'] = True
    room['current_question'] = 0
    room['answers'] = {}

    for player_id in room['players']:
        room['players'][player_id]['score'] = 0
        room['players'][player_id]['ready'] = False

    emit('game_start', {
        'theme': theme,
        'players': room['players'],
        'total_questions': len(room['questions'])
    }, room=room_id)

    send_question(room_id)


def end_game(room_id):
    if room_id not in rooms:
        return
    room = rooms[room_id]
    sorted_players = sorted(room['players'].items(), key=lambda x: x[1]['score'], reverse=True)
    db_sess = db_session.create_session()
    for player_id, player_data in sorted_players:
        result = GameResult(
            user_id=int(player_id),
            score=player_data['score'],
            mode='multiplayer',
            theme=room['theme']
        )
        db_sess.add(result)
        user = db_sess.query(User).get(int(player_id))
        if user:
            user.games_played += 1
    db_sess.commit()

    emit('game_end', {'results': sorted_players, 'players': room['players']}, room=room_id)
    del rooms[room_id]


@socketio.on('create_room')
def handle_create_room(data):
    user_id = session.get('user_id')
    user_email = session.get('user_email', 'Аноним')
    if not user_id:
        emit('error', {'message': 'Необходимо войти в систему'})
        return

    room_id = data.get('room_id')
    theme = data.get('theme', 'formulaToName')

    if not room_id:
        room_id = str(user_id) + datetime.now().strftime('%H%M%S')

    if room_id not in rooms:
        rooms[room_id] = {
            'players': {},
            'theme': theme,
            'game_started': False,
            'current_question': 0,
            'questions': [],
            'answers': {},
            'room_id': room_id
        }

    join_room(room_id)
    rooms[room_id]['players'][user_id] = {'email': user_email, 'score': 0, 'ready': False}

    emit('room_created', {'room_id': room_id, 'players': rooms[room_id]['players'], 'theme': theme}, room=room_id)
    emit('joined_room', {'room_id': room_id, 'players': rooms[room_id]['players']}, to=request.sid)


@socketio.on('join_room')
def handle_join_room(data):
    user_id = session.get('user_id')
    user_email = session.get('user_email', 'Аноним')
    room_id = data.get('room_id')

    if not user_id:
        emit('error', {'message': 'Необходимо войти в систему'})
        return

    if room_id not in rooms:
        emit('error', {'message': 'Комната не найдена'})
        return

    if rooms[room_id]['game_started']:
        emit('error', {'message': 'Игра уже началась'})
        return

    join_room(room_id)
    rooms[room_id]['players'][user_id] = {'email': user_email, 'score': 0, 'ready': False}

    emit('player_joined', {'players': rooms[room_id]['players']}, room=room_id)
    emit('joined_room', {'room_id': room_id, 'players': rooms[room_id]['players']}, to=request.sid)


@socketio.on('player_ready')
def handle_player_ready(data):
    user_id = session.get('user_id')
    room_id = data.get('room_id')

    if room_id not in rooms:
        return

    if user_id in rooms[room_id]['players']:
        rooms[room_id]['players'][user_id]['ready'] = True

    all_ready = all(p['ready'] for p in rooms[room_id]['players'].values())
    players_count = len(rooms[room_id]['players'])

    emit('player_status',
         {'players': rooms[room_id]['players'], 'all_ready': all_ready, 'players_count': players_count}, room=room_id)

    if all_ready and players_count >= 2:
        start_game(room_id)


@socketio.on('submit_answer')
def handle_submit_answer(data):
    user_id = session.get('user_id')
    room_id = data.get('room_id')
    answer = data.get('answer')
    time_taken = data.get('time_taken', 0)

    if not user_id or room_id not in rooms:
        return

    room = rooms[room_id]
    if user_id in room['answers']:
        return

    q_index = room['current_question']
    is_correct = check_answer_in_room(room, q_index, answer)
    points = 0

    if is_correct:
        points = max(10, 100 - int(time_taken / 10))
        if points > 100: points = 100
        room['players'][user_id]['score'] += points

    room['answers'][user_id] = {'answer': answer, 'correct': is_correct, 'points': points}
    correct_answer_text = room['questions'][q_index]['answer']

    emit('answer_result', {
        'correct': is_correct,
        'points': points,
        'new_score': room['players'][user_id]['score'],
        'correct_answer': correct_answer_text
    }, to=request.sid)

    emit('scores_update', {
        'players': {pid: p['score'] for pid, p in room['players'].items()}
    }, room=room_id)

    if len(room['answers']) >= len(room['players']):
        emit('show_correct_answer', {'correct_answer': room['questions'][q_index]['answer']}, room=room_id)
        socketio.sleep(2)
        room['current_question'] += 1
        room['answers'] = {}
        if room['current_question'] >= len(room['questions']):
            end_game(room_id)
        else:
            send_question(room_id)

@socketio.on('get_players')
def handle_get_players(data):
    room_id = data.get('room_id')
    if room_id in rooms:
        emit('player_list_update', {'players': rooms[room_id]['players']}, to=request.sid)


@socketio.on('leave_room')
def handle_leave_room(data):
    user_id = session.get('user_id')
    room_id = data.get('room_id')
    if room_id in rooms:
        if user_id in rooms[room_id]['players']:
            del rooms[room_id]['players'][user_id]
        emit('player_left', {'players': rooms[room_id]['players']}, room=room_id)
        leave_room(room_id)
        if len(rooms[room_id]['players']) == 0:
            del rooms[room_id]


@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    for room_id, room in list(rooms.items()):
        if user_id in room['players']:
            del room['players'][user_id]
            emit('player_left', {'players': room['players']}, room=room_id)
            if len(room['players']) == 0:
                del rooms[room_id]
            break


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if 'user_id' in session:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        existing_user = db_sess.query(User).filter(User.email == form.email.data).first()
        if existing_user:
            flash('Пользователь с таким email уже существует', 'danger')
            return render_template("signup.html", form=form)

        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('sign_in'))
    return render_template("signup.html", form=form)


@app.route("/signin", methods=['GET', 'POST'])
def sign_in():
    if 'user_id' in session:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['user_email'] = user.email
            flash(f'Добро пожаловать, {user.email}!', 'success')
            return redirect(url_for('game'))
        else:
            flash('Неверный email или пароль', 'danger')
    return render_template("signin.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


@app.route("/game")
def game():
    return render_template("game.html")


@app.route("/multiplayer")
def multiplayer():
    if 'user_id' not in session:
        flash('Войдите в систему, чтобы играть в мультиплеер', 'warning')
        return redirect(url_for('sign_in'))
    return render_template("multiplayer.html")


@app.route("/save_result", methods=['POST'])
def save_result():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json()
    db_sess = db_session.create_session()

    result = GameResult(
        user_id=session['user_id'],
        score=data['score'],
        mode=data['mode'],
        theme=data['theme']
    )

    user = db_sess.query(User).get(session['user_id'])
    if user:
        user.games_played += 1

    db_sess.add(result)
    db_sess.commit()

    return jsonify({'success': True})


@app.route("/check_auth")
def check_auth():
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'user_id': session['user_id'], 'email': session['user_email']})
    return jsonify({'authenticated': False})


@app.route("/rating")
def rating():
    mode = request.args.get('mode', 'time')
    theme = request.args.get('theme', 'formulaToName')

    db_sess = db_session.create_session()
    results = db_sess.query(
        User,
        db_session.sa.func.max(GameResult.score).label('best_score')
    ).join(
        GameResult, User.id == GameResult.user_id
    ).filter(
        GameResult.mode == mode,
        GameResult.theme == theme
    ).group_by(
        User.id
    ).order_by(
        db_session.sa.func.max(GameResult.score).desc()
    ).limit(20).all()

    return render_template(
        "rating.html",
        results=results,
        current_mode=mode,
        current_theme=theme
    )


@app.route("/table")
def table():
    return render_template("table.html")


@app.route("/images/<img_name>")
def image(img_name):
    return send_file(f"./static/images/{img_name}")


@app.route("/api/elements")
def get_elements():
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'elements.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    return {"error": "File not found"}, 404


if __name__ == '__main__':
    db_session.global_init("db/chemquest.db")
    socketio.run(app, debug=True, host='0.0.0.0', port=5089, allow_unsafe_werkzeug=True)
