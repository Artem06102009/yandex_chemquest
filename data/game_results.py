import datetime
from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm

class GameResult(SqlAlchemyBase):
    __tablename__ = "game_results"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    score = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    mode = sqlalchemy.Column(sqlalchemy.String(20), nullable=False)
    theme = sqlalchemy.Column(sqlalchemy.String(50), nullable=False)
    played_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.utcnow)

    user = orm.relationship('User', backref='results')