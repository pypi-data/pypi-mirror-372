# encoding: utf-8


def uncovered(thing):
    for shrub_candidate in thing.location.contents():
        if (shrub_candidate.name[:5] == 'shrub'):
            return False
    thing.engine.info('kobold uncovered')
    return True


def sametile(thing):
    try:
        return (thing['location'] == thing.character.thing['kobold']['location'])
    except KeyError:
        return False


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


def standing_still(thing):
    return (('destination' not in thing) or (thing['destination'] == thing.location))
