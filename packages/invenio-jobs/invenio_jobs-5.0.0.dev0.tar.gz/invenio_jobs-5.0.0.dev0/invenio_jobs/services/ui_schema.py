# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""UI schemas."""

from marshmallow import Schema, fields
from marshmallow_oneofschema import OneOfSchema


class IntervalScheduleUISchema(Schema):
    """Schema for an interval schedule based on ``datetime.timedelta``."""

    microseconds = fields.Integer(metadata={"title": "Microseconds", "order": 1})
    milliseconds = fields.Integer(metadata={"title": "Milliseconds", "order": 2})
    seconds = fields.Integer(metadata={"title": "Seconds", "order": 3})
    minutes = fields.Integer(metadata={"title": "Minutes", "order": 4})
    hours = fields.Integer(metadata={"title": "Hours", "order": 5})
    days = fields.Integer(metadata={"title": "Days", "order": 6})
    weeks = fields.Integer(metadata={"title": "Weeks", "order": 7})


class CrontabScheduleUISchema(Schema):
    """Schema for a crontab schedule."""

    minute = fields.String(load_default="*", metadata={"title": "Minute", "order": 1})
    hour = fields.String(load_default="*", metadata={"title": "Hour", "order": 2})
    day_of_week = fields.String(
        load_default="*", metadata={"title": "Day of Week", "order": 3}
    )
    day_of_month = fields.String(
        load_default="*", metadata={"title": "Day of Month", "order": 4}
    )
    month_of_year = fields.String(
        load_default="*", metadata={"title": "Month of Year", "order": 5}
    )


class ScheduleUISchema(OneOfSchema):
    """Schema for a schedule."""

    interval = fields.Nested(IntervalScheduleUISchema, dump_only=True)
    crontab = fields.Nested(CrontabScheduleUISchema, dump_only=True)
