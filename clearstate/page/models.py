# -*- coding: utf-8 -*-
from itertools import groupby
from collections import OrderedDict

from pytz import common_timezones
from clearstate.database import (
    Column,
    db,
    Model,
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
    active = Column(db.Boolean(), default=True)

    @property
    def component_count(self):
        """
        Returns the number of components
        """
        return Component.query.filter(
            Component.page_id == self.id
        ).count()

    @property
    def incident_count(self):
        """
        Returns the number of incidents that have ever happened
        """
        return Incident.query.filter(
            Incident.page_id == self.id,
        ).count()

    def components_by_group(self):
        """
        Returns all the components in the page grouped by their
        component group. Since the component group is not mandatory, the
        group could be none.
        """
        key = lambda component: component.group
        return groupby(
            sorted(self.components, key=key), key=key
        )


class ComponentGroup(SurrogatePK, Model):
    __tablename__ = 'page_component_group'

    name = Column(db.String(50), nullable=False)
    page_id = Column(db.ForeignKey('page.id'), nullable=False)
    page = relationship('Page', backref='component_groups')


class Component(SurrogatePK, Model):
    __tablename__ = 'page_component'

    status_map = OrderedDict([
        ('Operational', 'success'),
        ('Performance Issues', 'info'),
        ('Partial Outage', 'warning'),
        ('Major Outage', 'danger'),
    ])

    name = Column(db.String(50), nullable=False)
    description = Column(db.Text())
    link = Column(db.String(100))
    status = Column(
        db.Enum(*status_map.keys()),
        nullable=False, default='Operational'
    )

    page_id = Column(db.ForeignKey('page.id'), nullable=False)
    page = relationship('Page', backref='components')

    group_id = Column(
        db.ForeignKey('page_component_group.id'), nullable=True
    )
    group = relationship('ComponentGroup', backref='components')

    @property
    def status_css(self):
        return self.status_map[self.status]


class Incident(SurrogatePK, Model):
    __tablename__ = 'page_incident'

    title = Column(db.String(100), nullable=False)
    page_id = Column(db.ForeignKey('page.id'), nullable=False)
    page = relationship('Page', backref='incidents')
    type = Column(
        db.Enum(
            'Investigating',
            'Identified',
            'Watching',
            'Fixed',
        ),
        nullable=False
    )
