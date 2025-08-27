# encoding: utf-8


def breakcover(thing):
    if (thing.engine.random() < thing['sprint_chance']):
        thing.engine.info('kobold breaking cover')
        return True


def not_traveling(thing):
    return (('destination' not in thing) or (thing['destination'] == thing.location))


def kobold_alive(thing):
    return ('kobold' in thing.character.thing)


def aware(thing):
    from math import hypot
    try:
        bold = thing.character.thing['kobold']
    except KeyError:
        return False
    (dx, dy) = bold['location']
    (ox, oy) = thing['location']
    xdist = abs((dx - ox))
    ydist = abs((dy - oy))
    dist = hypot(xdist, ydist)
    return (dist <= thing['sight_radius'])


def unmerciful(thing):
    return thing.get('kill', False)


def kobold_not_here(thing):
    return ('kobold' not in thing.location.content)
