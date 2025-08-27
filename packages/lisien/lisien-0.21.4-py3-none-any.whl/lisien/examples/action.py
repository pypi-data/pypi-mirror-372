# encoding: utf-8

def time_slipping(character, *, daylen: int, nightlen: int, twilightlen: float=0.0):
    if ('hour' not in character.stat):
        character.stat['hour'] = 0
        character.stat['day_period'] = ('dawn' if twilightlen else 'day')
        return
    twi_margin = (twilightlen / 2)
    hour = character.stat['hour'] = ((character.stat['hour'] + 1) % (daylen + nightlen))
    if twilightlen:
        if ((hour < twi_margin) or (hour > ((daylen + nightlen) - twi_margin))):
            character.stat['day_period'] = 'dawn'
        elif (twi_margin < hour < (daylen - twi_margin)):
            character.stat['day_period'] = 'day'
        elif ((daylen - twi_margin) < hour < (daylen + twi_margin)):
            character.stat['day_period'] = 'dusk'
        else:
            character.stat['day_period'] = 'night'
    else:
        character.stat['day_period'] = ('day' if (hour < daylen) else 'night')

def shrubsprint(thing):
    shrub_places = sorted(list(thing['shrub_places']))
    if (thing['location'] in shrub_places):
        shrub_places.remove(thing['location'])
        assert (thing['location'] not in shrub_places)
    whereto = thing.engine.choice(shrub_places)
    thing['destination'] = whereto
    thing.travel_to(whereto)

def fight(thing):
    method = thing.engine.method
    return ('Kill kobold?', [('Kill', method.set_kill_flag), ('Spare', None)])

def kill_kobold(thing):
    del thing.character.thing['kobold']
    del thing['kill']

def go2kobold(thing):
    thing.travel_to(thing.character.thing['kobold']['location'])


def wander(thing):
    from lisien.util import sort_set
    dests = sort_set(thing.character.place.keys())
    dests.remove(thing['location'])
    thing.travel_to(thing.engine.choice(dests))
