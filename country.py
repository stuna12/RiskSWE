from enum import Enum
import player

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
    def countries_in_continent(continent : int) -> list[int]: 
        if continent == 0: # NA
            return list(range(0, 9))
        if continent == 1: # SA
            return list(range(9, 13))
        if continent == 2: # Africa
            return list(range(13, 19))
        if continent == 3: # Europe
            return list(range(19, 26))
        if continent == 4: # Asia
            return list(range(26, 38))
        if continent == 5: # Oceania
            return list(range(38, 42))
        return []

    @staticmethod
    def country_id_to_continent_id(country : "CountryEnum | int") -> int:
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

        else:
            return id - 38

class Country:
    def __init__(self, type: CountryEnum):
        self.type = type
        self.adj: list[int] = []
        self.owner: "player.Player | None" = None
        self.armies: int = 0
