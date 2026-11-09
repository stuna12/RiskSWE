import arcade

def schedule(method, duration, *args):
    arcade.schedule_once(lambda _dt: method(*args), duration)