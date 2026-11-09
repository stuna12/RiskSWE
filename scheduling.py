"""Helpers for scheduling delayed game actions."""

import arcade


def schedule(method, duration, *args):
    """Call method(*args) after duration seconds"""
    arcade.schedule_once(lambda _dt: method(*args), duration)
