"""Helpers for scheduling delayed game actions."""

import arcade


def schedule(method, duration, *args, callback = None):
    """Call method(*args) after duration seconds, and calls callback with the result as a parameter"""
    def run(_dt):
        result = method(*args)
        if callback is not None:
            callback(result)

    arcade.schedule_once(run, duration)
