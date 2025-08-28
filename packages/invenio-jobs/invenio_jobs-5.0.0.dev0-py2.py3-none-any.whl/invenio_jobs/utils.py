# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Jobs is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities."""

import ast
from datetime import datetime

from jinja2.sandbox import SandboxedEnvironment

jinja_env = SandboxedEnvironment()


def eval_tpl_str(val, ctx):
    """Evaluate a Jinja template string."""
    if not isinstance(val, str):
        return val

    tpl = jinja_env.from_string(val)
    res = tpl.render(**ctx)

    try:
        res = ast.literal_eval(res)
    except Exception:
        pass

    return res


def walk_values(obj, transform_fn):
    """Recursively apply a function in-place to the value of dictionary or list."""
    if isinstance(obj, dict):
        items = obj.items()
    elif isinstance(obj, list):
        items = enumerate(obj)
    else:
        return transform_fn(obj)

    for key, val in items:
        if isinstance(val, (dict, list)):
            walk_values(val, transform_fn)
        else:
            obj[key] = transform_fn(val)


def job_arg_json_dumper(obj):
    """Handle non-serializable values such as datetimes when dumping the arguments of a job run."""
    if isinstance(obj, datetime):
        return obj.isoformat()

    return obj
