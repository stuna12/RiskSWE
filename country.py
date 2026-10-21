from enum import Enum

class CountryEnum(Enum):
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
    def country_id_to_continent_id(country):
        if isinstance(country, CountryEnum):
            id = country.value
        else:
            id = country

        if id <= 8:
            return id

        if id <= 12:
            return id - 9

        if id <= 18:
            return id - 13
        
        if id <= 25:
            return id - 19

        if id <= 37:
            return id - 26

        if id <= 41:
            return id - 38

class Country:
    def __init__(self, type: CountryEnum):
        self.type = type
        self.adj: list[int] = []
        self.owner = None
        self.armies: int = 0
