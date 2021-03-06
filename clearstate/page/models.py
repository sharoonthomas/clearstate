# -*- coding: utf-8 -*-
from datetime import datetime
from itertools import groupby
from collections import OrderedDict

from dateutil.relativedelta import relativedelta
import pytz
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

    @property
    def effective_tz(self):
        """
        Returns the effective timezone.

        UTC if no timezone is defined for the page.
        """
        return pytz.timezone(
            self.timezone if self.timezone else 'UTC'
        )

    def get_incidents(self, till_date, days):
        """
        Returns an iterator that returns a date and incidents pair or
        an empty list
        """
        for delta_days in range(days):
            date = till_date - relativedelta(days=delta_days)
            start_time = datetime.combine(date, datetime.min.time())
            end_time = datetime.combine(date, datetime.max.time())

            # XXX: Does timezone matter here ?
            yield date, Incident.query.filter(
                Incident.page_id == self.id,
                Incident.create_time >= start_time,
                Incident.create_time <= end_time,
            ).all()


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

    create_time = Column(
        db.DateTime, nullable=False,
        default=datetime.utcnow,
    )

    @property
    def message(self):
        """
        The message of the incident is the last message on the updates
        """
        if self.last_update:
            return self.last_update.message

    @property
    def status(self):
        """
        Status of the most recent update
        """
        if self.last_update:
            return self.last_update.status

    @property
    def last_update(self):
        """
        Return the most recent update on the incident.
        """
        return IncidentUpdate.query.filter(
            IncidentUpdate.incident_id == self.id,
        ).order_by(
            IncidentUpdate.update_time.desc(),
            IncidentUpdate.create_time.desc(),
        ).first()

    @property
    def first_update(self):
        """
        Return the first update on the incident.
        """
        return IncidentUpdate.query.filter(
            IncidentUpdate.incident_id == self.id,
        ).order_by(IncidentUpdate.create_time.asc()).first()

    @property
    def update_time(self):
        """
        Return the last updated time based on the updates
        """
        return max(filter(None, [
            self.last_update.create_time,
            self.last_update.update_time,
        ]))

    @property
    def icon(self):
        """
        Based on incident type return a suitable icon
        """
        return {
            'Investigating': 'fa-exclamation-triangle',
            'Identified': 'fa-dot-circle-o',
            'Watching': 'fa-eye',
            'Fixed': 'fa-check-circle',
        }[self.status]

    @property
    def date(self):
        return max(
            filter(None, [self.create_time, self.update_time])
        ).date()


class IncidentUpdate(SurrogatePK, Model):
    __tablename__ = 'page_incident_update'

    statuses = [
        'Investigating',
        'Identified',
        'Watching',
        'Fixed',
    ]
    status = Column(db.Enum(*statuses), nullable=False)
    message = Column(db.Text(), nullable=False)

    incident_id = Column(db.ForeignKey('page_incident.id'), nullable=False)
    incident = relationship('Incident', backref='updates')

    create_time = Column(
        db.DateTime, nullable=False,
        default=datetime.utcnow,
    )
    update_time = Column(
        db.DateTime, nullable=False,
        onupdate=datetime.utcnow,
        default=datetime.utcnow,
    )
