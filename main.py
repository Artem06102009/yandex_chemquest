# from flask import Flask, render_template, request, send_file, url_for, redirect, flash, session, jsonify, global_init, create_session
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, BooleanField, SubmitField
# from wtforms.validators import DataRequired, Email, EqualTo, Length
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime
# import os
# import json
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'qwerty123'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chemquest.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db = SQLAlchemy(app)
#
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     games_played = db.Column(db.Integer, default=0)
#
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
#
#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
#
#
# class GameResult(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     score = db.Column(db.Integer, nullable=False)
#     mode = db.Column(db.String(20), nullable=False)
#     theme = db.Column(db.String(50), nullable=False)
#     played_at = db.Column(db.DateTime, default=datetime.utcnow)
#
#     user = db.relationship('User', backref=db.backref('results', lazy=True))
#
#
# class RegistrationForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=120)])
#     password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=100)])
#     confirm_password = PasswordField('Повторите пароль',
#                                      validators=[DataRequired(),
#                                                  EqualTo('password', message='Пароли должны совпадать')])
#     submit = SubmitField('Зарегистрироваться')
#
#
# class LoginForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Пароль', validators=[DataRequired()])
#     remember_me = BooleanField('Запомнить меня')
#     submit = SubmitField('Войти')
#
#
# with app.app_context():
#     db.create_all()
#
#
# @app.route("/")
# def index():
#     return render_template("index.html")
#
#
# @app.route("/signup", methods=['GET', 'POST'])
# def sign_up():
#     if 'user_id' in session:
#         return redirect(url_for('index'))
#
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         existing_user = User.query.filter_by(email=form.email.data).first()
#         if existing_user:
#             flash('Пользователь с таким email уже существует', 'danger')
#             return render_template("signup.html", form=form)
#
#         user = User(email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#
#         flash('Регистрация успешна! Теперь вы можете войти.', 'success')
#         return redirect(url_for('sign_in'))
#
#     return render_template("signup.html", form=form)
#
#
# @app.route("/signin", methods=['GET', 'POST'])
# def sign_in():
#     if 'user_id' in session:
#         return redirect(url_for('index'))
#
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and user.check_password(form.password.data):
#             session['user_id'] = user.id
#             session['user_email'] = user.email
#             flash(f'Добро пожаловать, {user.email}!', 'success')
#             return redirect(url_for('game'))
#         else:
#             flash('Неверный email или пароль', 'danger')
#
#     return render_template("signin.html", form=form)
#
#
# @app.route("/logout")
# def logout():
#     session.clear()
#     flash('Вы вышли из системы', 'info')
#     return redirect(url_for('index'))
#
#
# @app.route("/game")
# def game():
#     return render_template("game.html")
#
#
# @app.route("/save_result", methods=['POST'])
# def save_result():
#     if 'user_id' not in session:
#         return jsonify({'error': 'Not authenticated'}), 401
#
#     data = request.get_json()
#     result = GameResult(
#         user_id=session['user_id'],
#         score=data['score'],
#         mode=data['mode'],
#         theme=data['theme']
#     )
#
#     user = User.query.get(session['user_id'])
#     user.games_played += 1
#
#     db.session.add(result)
#     db.session.commit()
#
#     return jsonify({'success': True})
#
#
# @app.route("/check_auth")
# def check_auth():
#     if 'user_id' in session:
#         return jsonify({'authenticated': True, 'user_id': session['user_id']})
#     return jsonify({'authenticated': False})
#
#
# @app.route("/rating")
# def rating():
#     mode = request.args.get('mode', 'time')
#     theme = request.args.get('theme', 'formulaToName')
#
#     from sqlalchemy import func
#
#     results = db.session.query(User, func.max(GameResult.score).label('best_score')).join(
#         GameResult
#     ).filter(
#         GameResult.mode == mode,
#         GameResult.theme == theme
#     ).group_by(
#         User.id
#     ).order_by(
#         func.max(GameResult.score).desc()
#     ).limit(20).all()
#
#     global_init("chemquest.db")
#     db_sess = create_session()
#
#     # Находим максимальные очки по user_id
#     max_scores = db_sess.query(
#         GameResult.user_id,
#         GameResult.score.label('best_score')
#     ).filter(
#         GameResult.mode == mode,
#         GameResult.theme == theme
#     ).order_by(
#         GameResult.score.desc()
#     ).all()
#
#     # Создаём словарь {user_id: best_score}
#     best_scores = {}
#     user_ids = set()
#     for user_id, score in max_scores:
#         if user_id not in best_scores:
#             best_scores[user_id] = score
#             user_ids.add(user_id)
#
#     # Получаем пользователей и сортируем
#     users = db_sess.query(User).filter(User.id.in_(user_ids)).all()
#
#     # Собираем результаты
#     results = []
#     for user in users:
#         results.append((user, best_scores[user.id]))
#
#     # Сортируем по очкам
#     results.sort(key=lambda x: x[1], reverse=True)
#     results = results[:20]
#
#     # Используем
#     for user, best_score in results:
#         print(user.email, best_score)
#         # Что-то делаем
#         user.games_played += 1  # например
#
#     db_sess.commit()
#
#     return render_template("rating.html", results=results, current_mode=mode, current_theme=theme)
#
#
# @app.route("/images/<img_name>")
# def image(img_name):
#     return send_file(f"./static/images/{img_name}")
#
#
# @app.route("/api/elements")
# def get_elements():
#     with open(os.path.join(app.static_folder, 'data', 'elements.json'), 'r', encoding='utf-8') as f:
#         data = json.load(f)
#     return data
#
#
# @app.route("/table")
# def table():
#     return render_template("table.html")
#
#
# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, send_file, url_for, redirect, flash, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chemquest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ========== БАЗА ВОПРОСОВ ДЛЯ МУЛЬТИПЛЕЕРА ==========
QUIZ_DATA = {
    "formulaToName": [
        {"question": "H₂O", "answer": "Вода", "options": ["Углекислый газ", "Серная кислота", "Вода", "Аммиак"]},
        {"question": "CO₂", "answer": "Углекислый газ",
         "options": ["Угарный газ", "Углекислый газ", "Сероводород", "Метан"]},
        {"question": "HCl", "answer": "Хлороводород",
         "options": ["Азотная кислота", "Хлороводород", "Фосфорная кислота", "Серная кислота"]},
        {"question": "H₂SO₄", "answer": "Серная кислота",
         "options": ["Азотная кислота", "Уксусная кислота", "Серная кислота", "Плавиковая кислота"]},
        {"question": "NaOH", "answer": "Гидроксид натрия",
         "options": ["Гидроксид калия", "Гидроксид натрия", "Гидроксид кальция", "Гидроксид алюминия"]},
        {"question": "NH₃", "answer": "Аммиак", "options": ["Аммиак", "Метан", "Этан", "Пропан"]},
        {"question": "CH₄", "answer": "Метан", "options": ["Этан", "Метан", "Пропан", "Бутан"]},
        {"question": "NaCl", "answer": "Хлорид натрия",
         "options": ["Хлорид калия", "Хлорид кальция", "Хлорид натрия", "Хлорид магния"]},
        {"question": "CaCO₃", "answer": "Карбонат кальция",
         "options": ["Карбонат натрия", "Карбонат кальция", "Карбонат магния", "Карбонат бария"]},
        {"question": "HNO₃", "answer": "Азотная кислота",
         "options": ["Азотная кислота", "Серная кислота", "Фосфорная кислота", "Соляная кислота"]},
        {"question": "H₃PO₄", "answer": "Фосфорная кислота",
         "options": ["Азотная кислота", "Фосфорная кислота", "Серная кислота", "Уксусная кислота"]},
        {"question": "KOH", "answer": "Гидроксид калия",
         "options": ["Гидроксид натрия", "Гидроксид калия", "Гидроксид кальция", "Гидроксид алюминия"]},
        {"question": "Fe₂O₃", "answer": "Оксид железа(III)",
         "options": ["Оксид железа(II)", "Оксид железа(III)", "Оксид алюминия", "Оксид меди"]},
        {"question": "Al₂O₃", "answer": "Оксид алюминия",
         "options": ["Оксид железа", "Оксид алюминия", "Оксид цинка", "Оксид магния"]},
        {"question": "CuSO₄", "answer": "Сульфат меди(II)",
         "options": ["Сульфат железа", "Сульфат меди(II)", "Сульфат цинка", "Сульфат натрия"]},
        {"question": "Na₂CO₃", "answer": "Карбонат натрия",
         "options": ["Карбонат кальция", "Карбонат натрия", "Карбонат калия", "Карбонат магния"]},
        {"question": "H₂CO₃", "answer": "Угольная кислота",
         "options": ["Серная кислота", "Угольная кислота", "Азотная кислота", "Фосфорная кислота"]},
        {"question": "SO₂", "answer": "Оксид серы(IV)",
         "options": ["Оксид серы(IV)", "Оксид серы(VI)", "Сероводород", "Серная кислота"]},
        {"question": "SO₃", "answer": "Оксид серы(VI)",
         "options": ["Оксид серы(IV)", "Оксид серы(VI)", "Сернистая кислота", "Серная кислота"]},
        {"question": "NO₂", "answer": "Оксид азота(IV)",
         "options": ["Оксид азота(II)", "Оксид азота(IV)", "Аммиак", "Азотная кислота"]},
    ],
    "nameToFormula": [
        {"question": "Вода", "answer": "H₂O", "options": ["CO₂", "H₂O", "NH₃", "CH₄"]},
        {"question": "Серная кислота", "answer": "H₂SO₄", "options": ["HCl", "HNO₃", "H₂SO₄", "H₃PO₄"]},
        {"question": "Аммиак", "answer": "NH₃", "options": ["NH₃", "CH₄", "CO₂", "H₂O"]},
        {"question": "Метан", "answer": "CH₄", "options": ["C₂H₆", "CH₄", "C₃H₈", "C₄H₁₀"]},
        {"question": "Углекислый газ", "answer": "CO₂", "options": ["CO", "CO₂", "SO₂", "NO₂"]},
        {"question": "Хлороводород", "answer": "HCl", "options": ["HCl", "HBr", "HI", "HF"]},
        {"question": "Азотная кислота", "answer": "HNO₃", "options": ["HNO₃", "H₂SO₄", "H₃PO₄", "HClO₄"]},
        {"question": "Фосфорная кислота", "answer": "H₃PO₄", "options": ["HNO₃", "H₂SO₄", "H₃PO₄", "H₂CO₃"]},
        {"question": "Уксусная кислота", "answer": "CH₃COOH", "options": ["HCOOH", "CH₃COOH", "C₂H₅COOH", "C₃H₇COOH"]},
        {"question": "Муравьиная кислота", "answer": "HCOOH", "options": ["HCOOH", "CH₃COOH", "C₂H₅COOH", "C₃H₇COOH"]},
        {"question": "Гидроксид натрия", "answer": "NaOH", "options": ["NaOH", "KOH", "Ca(OH)₂", "Mg(OH)₂"]},
        {"question": "Гидроксид калия", "answer": "KOH", "options": ["NaOH", "KOH", "Ca(OH)₂", "Al(OH)₃"]},
        {"question": "Гидроксид кальция", "answer": "Ca(OH)₂", "options": ["NaOH", "KOH", "Ca(OH)₂", "Ba(OH)₂"]},
        {"question": "Оксид кальция", "answer": "CaO", "options": ["CaO", "MgO", "Na₂O", "Al₂O₃"]},
        {"question": "Оксид магния", "answer": "MgO", "options": ["MgO", "CaO", "BaO", "ZnO"]},
        {"question": "Оксид алюминия", "answer": "Al₂O₃", "options": ["Al₂O₃", "Fe₂O₃", "Cr₂O₃", "SiO₂"]},
        {"question": "Оксид железа(III)", "answer": "Fe₂O₃", "options": ["FeO", "Fe₂O₃", "Fe₃O₄", "Cr₂O₃"]},
        {"question": "Хлорид натрия", "answer": "NaCl", "options": ["NaCl", "KCl", "CaCl₂", "MgCl₂"]},
        {"question": "Хлорид калия", "answer": "KCl", "options": ["NaCl", "KCl", "LiCl", "RbCl"]},
        {"question": "Сульфат натрия", "answer": "Na₂SO₄", "options": ["Na₂SO₄", "K₂SO₄", "CaSO₄", "MgSO₄"]},
    ],
    "valency": [
        {"question": "Валентность водорода", "answer": "I", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность кислорода", "answer": "II", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность азота в NH₃", "answer": "III", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность углерода в CH₄", "answer": "IV", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность серы в H₂S", "answer": "II", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность хлора в HCl", "answer": "I", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность фтора в HF", "answer": "I", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность серы в SO₂", "answer": "IV", "options": ["II", "IV", "VI", "I"]},
        {"question": "Валентность серы в SO₃", "answer": "VI", "options": ["II", "IV", "VI", "I"]},
        {"question": "Валентность азота в NO", "answer": "II", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность азота в NO₂", "answer": "IV", "options": ["II", "III", "IV", "V"]},
        {"question": "Валентность углерода в CO₂", "answer": "IV", "options": ["II", "III", "IV", "I"]},
        {"question": "Валентность алюминия в AlCl₃", "answer": "III", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность натрия в NaCl", "answer": "I", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность магния в MgO", "answer": "II", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность кальция в CaCl₂", "answer": "II", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность железа в FeCl₂", "answer": "II", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность железа в FeCl₃", "answer": "III", "options": ["II", "III", "IV", "I"]},
        {"question": "Валентность меди в CuO", "answer": "II", "options": ["I", "II", "III", "IV"]},
        {"question": "Валентность цинка в ZnO", "answer": "II", "options": ["I", "II", "III", "IV"]},
    ],
    "oxidation": [
        {"question": "Степень окисления кислорода в H₂O", "answer": "-2", "options": ["-2", "-1", "0", "+2"]},
        {"question": "Степень окисления водорода в HCl", "answer": "+1", "options": ["-1", "0", "+1", "+2"]},
        {"question": "Степень окисления натрия в NaCl", "answer": "+1", "options": ["-1", "0", "+1", "+2"]},
        {"question": "Степень окисления хлора в Cl₂", "answer": "0", "options": ["-1", "0", "+1", "+2"]},
        {"question": "Степень окисления магния в MgO", "answer": "+2", "options": ["-2", "0", "+1", "+2"]},
        {"question": "Степень окисления алюминия в Al₂O₃", "answer": "+3", "options": ["-3", "0", "+3", "+2"]},
        {"question": "Степень окисления серы в H₂S", "answer": "-2", "options": ["-2", "-1", "0", "+2"]},
        {"question": "Степень окисления азота в NH₃", "answer": "-3", "options": ["-3", "0", "+3", "+5"]},
        {"question": "Степень окисления серы в SO₂", "answer": "+4", "options": ["-2", "+4", "+6", "0"]},
        {"question": "Степень окисления азота в NO", "answer": "+2", "options": ["-3", "+2", "+5", "0"]},
        {"question": "Степень окисления серы в SO₃", "answer": "+6", "options": ["+4", "+6", "-2", "0"]},
        {"question": "Степень окисления азота в N₂O₅", "answer": "+5", "options": ["+3", "+5", "-3", "0"]},
        {"question": "Степень окисления серы в H₂SO₄", "answer": "+6", "options": ["+4", "+6", "-2", "0"]},
        {"question": "Степень окисления азота в HNO₃", "answer": "+5", "options": ["+3", "+5", "-3", "0"]},
        {"question": "Степень окисления фосфора в H₃PO₄", "answer": "+5", "options": ["+3", "+5", "-3", "0"]},
        {"question": "Степень окисления хрома в K₂Cr₂O₇", "answer": "+6", "options": ["+3", "+6", "+2", "0"]},
        {"question": "Степень окисления марганца в KMnO₄", "answer": "+7", "options": ["+2", "+4", "+7", "0"]},
        {"question": "Степень окисления железа в FeSO₄", "answer": "+2", "options": ["+2", "+3", "+4", "0"]},
        {"question": "Степень окисления кислорода в H₂O₂", "answer": "-1", "options": ["-2", "-1", "0", "+1"]},
        {"question": "Степень окисления углерода в CO₂", "answer": "+4", "options": ["-4", "+2", "+4", "0"]},
    ],
    "bond": [
        {"question": "Какой тип реакции: 2H₂ + O₂ → 2H₂O?", "answer": "Соединения",
         "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
        {"question": "Какой тип реакции: 2H₂O → 2H₂ + O₂?", "answer": "Разложения",
         "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
        {"question": "Какой тип реакции: Zn + 2HCl → ZnCl₂ + H₂?", "answer": "Замещения",
         "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
        {"question": "Какой тип реакции: HCl + NaOH → NaCl + H₂O?", "answer": "Обмена",
         "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
        {"question": "Какой тип реакции: CH₄ + 2O₂ → CO₂ + 2H₂O?", "answer": "Горения",
         "options": ["Горения", "Нейтрализации", "Разложения", "Обмена"]},
        {"question": "Какой тип реакции: CaCO₃ → CaO + CO₂?", "answer": "Разложения",
         "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
        {"question": "Какой тип реакции: Fe + CuSO₄ → FeSO₄ + Cu?", "answer": "Замещения",
         "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
        {"question": "Какой тип реакции: AgNO₃ + NaCl → AgCl↓ + NaNO₃?", "answer": "Обмена",
         "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
        {"question": "Какой тип реакции: 2KClO₃ → 2KCl + 3O₂?", "answer": "Разложения",
         "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
        {"question": "Какой тип реакции: Cl₂ + 2NaBr → 2NaCl + Br₂?", "answer": "Замещения",
         "options": ["Соединения", "Разложения", "Замещения", "Обмена"]},
    ],
    "atomicmass": [
        {"question": "Атомная масса водорода (H)", "answer": "1", "options": ["1", "2", "3", "4"]},
        {"question": "Атомная масса углерода (C)", "answer": "12", "options": ["12", "13", "14", "15"]},
        {"question": "Атомная масса кислорода (O)", "answer": "16", "options": ["15", "16", "17", "18"]},
        {"question": "Атомная масса натрия (Na)", "answer": "23", "options": ["22", "23", "24", "25"]},
        {"question": "Атомная масса железа (Fe)", "answer": "56", "options": ["55", "56", "57", "58"]},
        {"question": "Атомная масса азота (N)", "answer": "14", "options": ["13", "14", "15", "16"]},
        {"question": "Атомная масса хлора (Cl)", "answer": "35.5", "options": ["34", "35", "35.5", "36"]},
        {"question": "Атомная масса кальция (Ca)", "answer": "40", "options": ["39", "40", "41", "42"]},
        {"question": "Атомная масса алюминия (Al)", "answer": "27", "options": ["26", "27", "28", "29"]},
        {"question": "Атомная масса серы (S)", "answer": "32", "options": ["31", "32", "33", "34"]},
        {"question": "Атомная масса магния (Mg)", "answer": "24", "options": ["23", "24", "25", "26"]},
        {"question": "Атомная масса калия (K)", "answer": "39", "options": ["38", "39", "40", "41"]},
        {"question": "Атомная масса меди (Cu)", "answer": "63.5", "options": ["62", "63", "63.5", "64"]},
        {"question": "Атомная масса цинка (Zn)", "answer": "65", "options": ["64", "65", "66", "67"]},
        {"question": "Атомная масса серебра (Ag)", "answer": "108", "options": ["107", "108", "109", "110"]},
        {"question": "Атомная масса золота (Au)", "answer": "197", "options": ["196", "197", "198", "199"]},
        {"question": "Атомная масса ртути (Hg)", "answer": "201", "options": ["200", "201", "202", "203"]},
        {"question": "Атомная масса свинца (Pb)", "answer": "207", "options": ["206", "207", "208", "209"]},
        {"question": "Атомная масса урана (U)", "answer": "238", "options": ["237", "238", "239", "240"]},
        {"question": "Атомная масса лития (Li)", "answer": "7", "options": ["6", "7", "8", "9"]},
    ],
    "OVR": [
        {"question": "Какой из этих элементов является сильным окислителем?", "answer": "F₂",
         "options": ["Na", "F₂", "H₂", "Ca"]},
        {"question": "Какой из этих элементов является типичным восстановителем?", "answer": "Na",
         "options": ["Cl₂", "O₂", "Na", "F₂"]},
        {"question": "Какое вещество в реакции выступает окислителем: 2Na + Cl₂ → 2NaCl?", "answer": "Cl₂",
         "options": ["Na", "Cl₂", "Оба", "Никакое"]},
        {"question": "Какое вещество может быть только окислителем?", "answer": "F₂",
         "options": ["H₂", "F₂", "Fe²⁺", "SO₂"]},
        {"question": "Какое вещество может быть как окислителем, так и восстановителем?", "answer": "H₂O₂",
         "options": ["H₂O₂", "KMnO₄", "F₂", "Na"]},
        {"question": "Какое вещество в реакции выступает восстановителем: Zn + CuSO₄ → ZnSO₄ + Cu?", "answer": "Zn",
         "options": ["Zn", "CuSO₄", "Оба", "Никакое"]},
        {"question": "Что является окислителем в реакции горения метана: CH₄ + 2O₂ → CO₂ + 2H₂O?", "answer": "O₂",
         "options": ["CH₄", "O₂", "CO₂", "H₂O"]},
        {"question": "Какое из этих соединений - сильный окислитель?", "answer": "KMnO₄",
         "options": ["NaCl", "KMnO₄", "H₂O", "CO₂"]},
        {"question": "Какой процесс происходит с азотом в реакции: NH₃ → NO?", "answer": "Окисление",
         "options": ["Окисление", "Восстановление", "Ни то, ни другое", "Диспропорционирование"]},
        {"question": "Какое вещество в реакции диспропорционирования является и окислителем, и восстановителем?",
         "answer": "Cl₂", "options": ["Cl₂", "NaCl", "HCl", "O₂"]},
        {"question": "Какой процесс происходит с пероксидом водорода в реакции: 2H₂O₂ → 2H₂O + O₂?",
         "answer": "Диспропорционирование",
         "options": ["Окисление", "Восстановление", "Диспропорционирование", "Ничего"]},
        {"question": "Какое вещество является окислителем в реакции: CuO + H₂ → Cu + H₂O?", "answer": "CuO",
         "options": ["CuO", "H₂", "Оба", "Никакое"]},
        {"question": "Какой металл - самый сильный восстановитель?", "answer": "Li",
         "options": ["Li", "Au", "Fe", "Cu"]},
        {"question": "Какое вещество может выступать как окислителем, так и восстановителем?", "answer": "SO₂",
         "options": ["SO₂", "Na", "F₂", "KMnO₄"]},
        {"question": "Что является восстановителем в реакции: 2FeCl₃ + H₂S → 2FeCl₂ + S + 2HCl?", "answer": "H₂S",
         "options": ["FeCl₃", "H₂S", "Оба", "Никакое"]},
        {"question": "Какое вещество является окислителем в реакции: 2KBr + Cl₂ → 2KCl + Br₂?", "answer": "Cl₂",
         "options": ["KBr", "Cl₂", "Оба", "Никакое"]},
        {"question": "Какое вещество может быть только окислителем?", "answer": "O₃",
         "options": ["H₂", "O₃", "H₂O₂", "SO₂"]},
        {"question": "Как изменяется степень окисления марганца в реакции: KMnO₄ → Mn²⁺?", "answer": "Уменьшается",
         "options": ["Увеличивается", "Уменьшается", "Не изменяется", "Сначала увеличивается, потом уменьшается"]},
        {"question": "Как изменяется степень окисления хрома в реакции: K₂Cr₂O₇ → Cr³⁺?", "answer": "Уменьшается",
         "options": ["Увеличивается", "Уменьшается", "Не изменяется", "Сначала увеличивается, потом уменьшается"]},
        {"question": "Какое вещество является окислителем в реакции: 2KMnO₄ + 5H₂SO₃ → 2MnSO₄ + K₂SO₄ + 3H₂SO₄ + 2H₂O?",
         "answer": "KMnO₄", "options": ["KMnO₄", "H₂SO₃", "Оба", "Никакое"]},
    ],
}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    games_played = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    theme = db.Column(db.String(50), nullable=False)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('results', lazy=True))


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=120)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=100)])
    confirm_password = PasswordField('Повторите пароль',
                                     validators=[DataRequired(),
                                                 EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


with app.app_context():
    db.create_all()

rooms = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if 'user_id' in session:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Пользователь с таким email уже существует', 'danger')
            return render_template("signup.html", form=form)

        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('sign_in'))

    return render_template("signup.html", form=form)


@app.route("/signin", methods=['GET', 'POST'])
def sign_in():
    if 'user_id' in session:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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
    result = GameResult(
        user_id=session['user_id'],
        score=data['score'],
        mode=data['mode'],
        theme=data['theme']
    )

    user = User.query.get(session['user_id'])
    user.games_played += 1

    db.session.add(result)
    db.session.commit()

    return jsonify({'success': True})


@app.route("/check_auth")
def check_auth():
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'user_id': session['user_id'], 'email': session['user_email']})
    return jsonify({'authenticated': False})


@app.route("/api/elements")
def get_elements():
    json_path = os.path.join(app.static_folder, 'data', 'elements.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    return {"error": "File not found"}, 404


@app.route("/rating")
def rating():
    mode = request.args.get('mode', 'time')
    theme = request.args.get('theme', 'formulaToName')

    from sqlalchemy import func

    subquery = db.session.query(
        GameResult.user_id,
        func.max(GameResult.score).label('best_score')
    ).filter(
        GameResult.mode == mode,
        GameResult.theme == theme
    ).group_by(GameResult.user_id).subquery()

    results = db.session.query(
        User,
        subquery.c.best_score
    ).join(
        subquery, User.id == subquery.c.user_id
    ).order_by(
        subquery.c.best_score.desc()
    ).limit(20).all()

    return render_template("rating.html", results=results, current_mode=mode, current_theme=theme)


@app.route("/table")
def table():
    return render_template("table.html")


@app.route("/images/<img_name>")
def image(img_name):
    return send_file(f"./static/images/{img_name}")


# ========== SOCKETIO МУЛЬТИПЛЕЕР ==========

@socketio.on('create_room')
def handle_create_room(data):
    """Создание новой игровой комнаты"""
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
    rooms[room_id]['players'][user_id] = {
        'email': user_email,
        'score': 0,
        'ready': False
    }

    emit('room_created', {
        'room_id': room_id,
        'players': rooms[room_id]['players'],
        'theme': theme
    }, room=room_id)

    emit('joined_room', {
        'room_id': room_id,
        'players': rooms[room_id]['players']
    }, to=request.sid)


@socketio.on('join_room')
def handle_join_room(data):
    """Подключение к существующей комнате"""
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
    rooms[room_id]['players'][user_id] = {
        'email': user_email,
        'score': 0,
        'ready': False
    }

    emit('player_joined', {
        'players': rooms[room_id]['players']
    }, room=room_id)

    emit('joined_room', {
        'room_id': room_id,
        'players': rooms[room_id]['players']
    }, to=request.sid)


@socketio.on('player_ready')
def handle_player_ready(data):
    """Игрок готов начать"""
    user_id = session.get('user_id')
    room_id = data.get('room_id')

    if room_id not in rooms:
        return

    if user_id in rooms[room_id]['players']:
        rooms[room_id]['players'][user_id]['ready'] = True

    all_ready = all(p['ready'] for p in rooms[room_id]['players'].values())
    players_count = len(rooms[room_id]['players'])

    emit('player_status', {
        'players': rooms[room_id]['players'],
        'all_ready': all_ready,
        'players_count': players_count
    }, room=room_id)

    if all_ready and players_count >= 2:
        start_multiplayer_game(room_id)


def start_multiplayer_game(room_id):
    """Запуск мультиплеерной игры"""
    room = rooms[room_id]
    theme = room['theme']

    # Загружаем вопросы из QUIZ_DATA
    questions = QUIZ_DATA.get(theme, QUIZ_DATA["formulaToName"])
    random.shuffle(questions)
    room['questions'] = questions[:10]
    room['game_started'] = True
    room['current_question'] = 0
    room['answers'] = {}

    # Сброс очков и готовности
    for player_id in room['players']:
        room['players'][player_id]['score'] = 0
        room['players'][player_id]['ready'] = False

    emit('game_start', {
        'theme': theme,
        'players': room['players'],
        'total_questions': len(room['questions'])
    }, room=room_id)

    send_question(room_id)


def send_question(room_id):
    """Отправка вопроса всем игрокам в комнате"""
    room = rooms[room_id]
    q_index = room['current_question']

    if q_index >= len(room['questions']):
        end_multiplayer_game(room_id)
        return

    question_data = room['questions'][q_index]

    emit('new_question', {
        'question_num': q_index + 1,
        'total': len(room['questions']),
        'question': question_data['question'],
        'options': question_data['options']
    }, room=room_id)

    room['answers'] = {}


def check_answer_in_room(room, question_index, answer):
    """Проверка правильности ответа"""
    questions = room.get('questions', [])
    if question_index >= len(questions):
        return False

    correct_answer = questions[question_index]['answer']
    return answer == correct_answer


@socketio.on('submit_answer')
def handle_submit_answer(data):
    """Обработка ответа игрока"""
    user_id = session.get('user_id')
    room_id = data.get('room_id')
    answer = data.get('answer')
    time_taken = data.get('time_taken', 0)

    if not user_id or room_id not in rooms:
        return

    room = rooms[room_id]

    # Проверяем, не ответил ли уже этот игрок
    if user_id in room['answers']:
        return

    q_index = room['current_question']
    is_correct = check_answer_in_room(room, q_index, answer)

    # Начисляем очки (чем быстрее ответ, тем больше очков)
    points = 0
    if is_correct:
        points = max(10, 100 - int(time_taken / 10))
        if points > 100:
            points = 100
        room['players'][user_id]['score'] += points

    room['answers'][user_id] = {
        'answer': answer,
        'correct': is_correct,
        'points': points
    }

    correct_answer = room['questions'][q_index]['answer'] if not is_correct else None

    emit('answer_result', {
        'correct': is_correct,
        'points': points,
        'new_score': room['players'][user_id]['score'],
        'correct_answer': correct_answer
    }, to=request.sid)

    # Оповещаем всех об обновлении очков
    emit('scores_update', {
        'players': {pid: p['score'] for pid, p in room['players'].items()}
    }, room=room_id)

    # Проверяем, все ли ответили
    if len(room['answers']) >= len(room['players']):
        emit('show_correct_answer', {
            'correct_answer': room['questions'][q_index]['answer']
        }, room=room_id)

        def next_question():
            room['current_question'] += 1
            room['answers'] = {}

            if room['current_question'] >= len(room['questions']):
                end_multiplayer_game(room_id)
            else:
                send_question(room_id)

        socketio.sleep(2)
        next_question()


@socketio.on('get_players')
def handle_get_players(data):
    room_id = data.get('room_id')
    if room_id in rooms:
        emit('player_list_update', {
            'players': rooms[room_id]['players']
        }, to=request.sid)


@socketio.on('leave_room')
def handle_leave_room(data):
    """Выход из комнаты"""
    user_id = session.get('user_id')
    room_id = data.get('room_id')

    if room_id in rooms:
        if user_id in rooms[room_id]['players']:
            del rooms[room_id]['players'][user_id]

        emit('player_left', {
            'players': rooms[room_id]['players']
        }, room=room_id)

        leave_room(room_id)

        if len(rooms[room_id]['players']) == 0:
            del rooms[room_id]


def end_multiplayer_game(room_id):
    """Завершение мультиплеерной игры"""
    room = rooms[room_id]

    sorted_players = sorted(
        room['players'].items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )

    for player_id, player_data in sorted_players:
        result = GameResult(
            user_id=int(player_id),
            score=player_data['score'],
            mode='multiplayer',
            theme=room['theme']
        )
        db.session.add(result)

        user = User.query.get(int(player_id))
        if user:
            user.games_played += 1

    db.session.commit()

    emit('game_end', {
        'results': sorted_players,
        'players': room['players']
    }, room=room_id)

    del rooms[room_id]


@socketio.on('disconnect')
def handle_disconnect():
    """Обработка отключения пользователя"""
    user_id = session.get('user_id')
    for room_id, room in list(rooms.items()):
        if user_id in room['players']:
            del room['players'][user_id]
            emit('player_left', {
                'players': room['players']
            }, room=room_id)

            if len(room['players']) == 0:
                del rooms[room_id]
            break


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5089, allow_unsafe_werkzeug=True)