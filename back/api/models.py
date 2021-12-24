import enum
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class SettingTypes(enum.Enum):
    str = 'str'
    int = 'int'


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    value = db.Column(db.String, nullable=False)
    type = db.Column(
        db.Enum(SettingTypes), default=SettingTypes.str, nullable=False)
