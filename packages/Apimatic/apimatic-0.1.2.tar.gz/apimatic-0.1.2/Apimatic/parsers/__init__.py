from __future__ import annotations
from typing import Callable, Dict
from .flask import parse_flask_routes
from .fastapi import parse_fastapi_routes
from .django import parse_django_routes
from .express import parse_express_routes

PARSERS: Dict[str, Callable] = {
    "flask": parse_flask_routes,
    "fastapi": parse_fastapi_routes,
    "django": parse_django_routes,
    "express": parse_express_routes,
}


def get_parser(name: str):
    return PARSERS.get(name.lower())
