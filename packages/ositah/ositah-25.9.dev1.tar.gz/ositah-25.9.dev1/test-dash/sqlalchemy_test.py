#!/usr/bin/env python
#
# Test script for SQLAlchemy with SQLite

import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text

# Add to Python path the apps module which resides at the same level as this script parent dir
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from hito_tools.utils import sql_longtext_to_list  # noqa: E402

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///c:\\temp\\hito-dev.sqlite"
db = SQLAlchemy(app)


class Agent(db.Model):
    __tablename__ = "agent"

    id = Column(Integer, primary_key=True)
    nom = Column(String)
    roles = Column(Text)

    def __repr__(self):
        return f"<Agent(nom={self.nom}, roles={sql_longtext_to_list(self.roles)})>"


print("Information sur Jouvin")
for agent in Agent.query.filter_by(nom="JOUVIN"):
    print(agent)

agents = Agent.query.all()
print()
print(f"Liste de tous les agents ({len(agents)}) et leurs roles")
for agent in sorted(agents, key=lambda x: x.nom.upper()):
    print(agent)
