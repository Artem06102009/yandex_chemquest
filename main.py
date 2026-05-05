from flask import Flask, render_template, request, send_file, url_for, redirect, flash, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chemquest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


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
        return jsonify({'authenticated': True, 'user_id': session['user_id']})
    return jsonify({'authenticated': False})


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


@app.route("/images/<img_name>")
def image(img_name):
    return send_file(f"./static/images/{img_name}")


@app.route("/api/elements")
def get_elements():
    with open(os.path.join(app.static_folder, 'data', 'elements.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


@app.route("/table")
def table():
    return render_template("table.html")


if __name__ == '__main__':
    app.run(debug=True)
