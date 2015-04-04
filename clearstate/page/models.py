# -*- coding: utf-8 -*-
from pytz import common_timezones
from clearstate.database import (
    Column,
    db,
    Model,
    ReferenceCol,
    relationship,
    SurrogatePK,
)

timezones = list(common_timezones)


class Page(SurrogatePK, Model):
    __tablename__ = 'page'

    name = Column(db.String(50), unique=True, nullable=False)
    site_url = Column(db.String(50), unique=True, nullable=False)
    about_page = Column(db.Text())
    timezone = Column(db.Enum(*timezones), nullable=True)
