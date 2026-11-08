"""
Country definitions: territory enum, continent helpers,
and Country class that tracks territory game state.
"""

from enum import Enum

# Territory id ranges for each continent:
# 0 = North America, 1 = South America, 2 = Africa,
# 3 = Europe, 4 = Asia, 5 = Australia
CONTINENT_RANGES = [
    range(0, 9),
    range(9, 13),
    range(13, 19),
    range(19, 26),
    range(26, 38),
    range(38, 42),
]


class CountryEnum(Enum):
    """Every territory numbered in the order of edges.txt"""

    # NORTH AMERICA
    ALASKA = 0
    ALBERTA = 1
    CENTRAL_AMERICA = 2
    EASTERN_US = 3
    GREENLAND = 4
    NORTHWEST_TERRITORY = 5
    ONTARIO = 6
    QUEBEC = 7
    WESTERN_US = 8

    # SOUTH AMERICA
    ARGENTINA = 9
    BRAZIL = 10
    PERU = 11
    VENEZUELA = 12

    # AFRICA
    CONGO = 13
    EAST_AFRICA = 14
    EGYPT = 15
    MADAGASCAR = 16
    NORTH_AFRICA = 17
    SOUTH_AFRICA = 18

    # EUROPE
    GREAT_BRITAIN = 19
    ICELAND = 20
    NORTHERN_EUROPE = 21
    SCANDANAVIA = 22
    SOUTHERN_EUROPE = 23
    UKRAINE = 24
    WESTERN_EUROPE = 25

    # ASIA
    AFGHANISTAN = 26
    CHINA = 27
    INDIA = 28
    IRKUTSK = 29
    JAPAN = 30
    KAMCHATKA = 31
    MIDDLE_EAST = 32
    MONGOLIA = 33
    SIAM = 34
    SIBERIA = 35
    URAL = 36
    YAKUTSK = 37

    # AUSTRALIA
    EASTERN_AUSTRALIA = 38
    NEW_GUINEA = 39
    INDONESIA = 40
    WESTERN_AUSTRALIA = 41

    @staticmethod
    def countries_in_continent(continent):
        """
        Returns territory ids that belong to the continent id.
        """
        if 0 <= continent < len(CONTINENT_RANGES):
            return list(CONTINENT_RANGES[continent])
        return []

    @staticmethod
    def country_id_to_continent_id(country):
        """
        Returns position of a territory within its own continent.
        Used to label map buttons
        """
        country_id = country.value if isinstance(country, CountryEnum) else country

        for continent in CONTINENT_RANGES:
            if country_id in continent:
                return country_id - continent.start

        return country_id - CONTINENT_RANGES[-1].start


class Country:
    """A single territory: adjacency list, owner, and army count."""

    def __init__(self, country_type):
        self.type = country_type
        self.adj: list[int] = []
        # set to a Player when territory is claimed
        self.owner = None
        self.armies: int = 0
