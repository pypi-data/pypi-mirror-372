"""Utility helpers.""""
from __future__ import annotations

import json


def pretty_json(obj):
    return json.dumps(obj, indent=2, default=str)
