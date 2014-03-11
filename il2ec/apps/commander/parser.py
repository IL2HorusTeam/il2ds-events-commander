# -*- coding: utf-8 -*-
"""
Custom parsers of DS output.
"""
import re

from il2ds_middleware.parser import (ConsoleParser as BaseConsoleParser,
    DeviceLinkParser as BaseDeviceLinkParser, )


class ConsoleParser(BaseConsoleParser):
    """
    Custom console parser.
    """

    def users_common_info(self, lines):
        """
        Parse strings of table containing common players info and produce a
        dictionary of pilot infos. E.g.:

        [
            " N      Name           Ping    Score   Army        Aircraft",
            " 1      user1          3       0      (0)None             ",
            " 2      user2          1       490    (1)Red      * Red 90    Il-2M_Late",
        ]

        will result into:

        {
            'user1': {
                'ping': 3,
                'score': 0,
                'army_code': 0,
            },
            'user2': {
                'ping': 1,
                'score': 490,
                'army_code': 1,
                'designation': '* Red 90',
                'aircraft_code': 'Il-2M_Late',
            },
        }
        """
        result = {}

        for line in lines[1:]:
            raw_info = re.split('\s{2,}', line.strip())[1:]

            callsign = raw_info.pop(0)
            info = {}
            result[callsign] = info

            info['ping'] = int(raw_info.pop(0))
            info['score'] = int(raw_info.pop(0))
            info['army_code'] = int(re.findall('\d+', raw_info.pop(0))[0])

            if raw_info:
                info['designation'], info['aircraft_code'] = raw_info

        return result

    def users_statistics(self, lines):
        """
        Process a sequence of tables with users' statistics. Lines example:

        [
            "-------------------------------------------------------",
            "Name: \t\t=user1",
            "Score: \t\t0",
            "State: \t\tIn Flight",
            "Enemy Aircraft Kill: \t\t0",
            "Enemy Static Aircraft Kill: \t\t0",
            "Enemy Tank Kill: \t\t0",
            "Enemy Car Kill: \t\t0",
            "Enemy Artillery Kill: \t\t0",
            "Enemy AAA Kill: \t\t0",
            "Enemy Wagon Kill: \t\t0",
            "Enemy Ship Kill: \t\t0",
            "Enemy Radio Kill: \t\t0",
            "Friend Aircraft Kill: \t\t0",
            "Friend Static Aircraft Kill: \t\t0",
            "Friend Tank Kill: \t\t0",
            "Friend Car Kill: \t\t0",
            "Friend Artillery Kill: \t\t0",
            "Friend AAA Kill: \t\t0",
            "Friend Wagon Kill: \t\t0",
            "Friend Ship Kill: \t\t0",
            "Friend Radio Kill: \t\t0",
            "Fire Bullets: \t\t0",
            "Hit Bullets: \t\t0",
            "Hit Air Bullets: \t\t0",
            "Fire Roskets: \t\t0",
            "Hit Roskets: \t\t0",
            "Fire Bombs: \t\t0",
            "Hit Bombs: \t\t0",
            "-------------------------------------------------------",
            "Name: \t\tuser0",
            "Score: \t\t0",
            "State: \t\tIn Flight",
            "Enemy Aircraft Kill: \t\t0",
            "Enemy Static Aircraft Kill: \t\t0",
            "Enemy Tank Kill: \t\t0",
            "Enemy Car Kill: \t\t0",
            "Enemy Artillery Kill: \t\t0",
            "Enemy AAA Kill: \t\t0",
            "Enemy Wagon Kill: \t\t0",
            "Enemy Ship Kill: \t\t0",
            "Enemy Radio Kill: \t\t0",
            "Friend Aircraft Kill: \t\t0",
            "Friend Static Aircraft Kill: \t\t0",
            "Friend Tank Kill: \t\t0",
            "Friend Car Kill: \t\t0",
            "Friend Artillery Kill: \t\t0",
            "Friend AAA Kill: \t\t0",
            "Friend Wagon Kill: \t\t0",
            "Friend Ship Kill: \t\t0",
            "Friend Radio Kill: \t\t0",
            "Fire Bullets: \t\t120",
            "Hit Bullets: \t\t12",
            "Hit Air Bullets: \t\t0",
            "Fire Roskets: \t\t0",
            "Hit Roskets: \t\t0",
            "Fire Bombs: \t\t0",
            "Hit Bombs: \t\t0",
            "-------------------------------------------------------",
        ]
        """
        def get_blank_info():
            """
            Prepares blank statistics info.
            """
            info = {
                'kills': {
                    'enemy': {},
                    'friend': {},
                },
                'weapons': {
                    'bullets': {},
                    'rockets': {},
                    'bombs': {},
                }
            }
            return info

        def to_key(key):
            """
            Turns strings into dictionary keys.
            """
            return key.lower().replace(' ', '_')

        result = {}

        callsign = None
        info = get_blank_info()

        for line in lines[1:]:
            if line.startswith('-'):
                result[callsign] = info
                info = get_blank_info()
                continue

            attr, value = line.replace('\\t', '').split(': ')

            if attr == "Name":
                callsign = value

            elif attr == "Score":
                info['score'] = int(value)

            elif attr == "State":
                info['state'] = value

            elif attr.endswith("Kill"):
                side, target = attr.rsplit(' ', 1)[0].split(' ', 1)
                side = to_key(side)
                target = to_key(target)
                info['kills'][side][target] = int(value)

            else:
                attr, weapon = attr.rsplit(' ', 1)
                attr = to_key(attr)
                weapon = to_key(weapon).replace('sk', 'ck')
                info['weapons'][weapon][attr] = int(value)

        return result


class DeviceLinkParser(BaseDeviceLinkParser):

    def _parse_pos(self, data, name_attr='name', strip_idx=False):
        idx, info = data.split(':')

        try:
            attr, x, y, z = info.split(';')
        except ValueError:
            return None

        if strip_idx:
            attr = attr[:attr.rindex("_")]
        return {
            'id': int(idx),
            name_attr: attr,
            'pos': {
                'x': int(x),
                'y': int(y),
                'z': int(z),
            },
        }
