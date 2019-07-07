import data
import math


# Part codes
BELT_DOME_ENG = 1
DECK_ENG = 2
UPPER_DECK = 3
SKY_WINDOW_ENG = 4
WATER_BELT_DOME_ENG = 5
WATER_TDS_ENG = 6
BELT_DOME_MAG = 7
DECK_MAG = 8
SKY_WINDOW_MAG = 9
WATER_BELT_DOME_MAG = 10
WATER_TDS_MAG = 11


# Damage levels
RICOCHET = 1000
BLOCKED = 1001
ROOM = 1002
CITADEL = 1003
ENGINE = 1004
MAGAZINE = 1005
OVER = 1006
LIGHT = 1007


class Shot:
    def __init__(self, distance: int, velocity: float, v_angle: float, h_angle: float, shell: data.ShipData):
        self.distance = distance
        self.caliber = shell["Caliber"]
        self.ef = shell["AP-ef"]
        self.mass = shell["AP-mass"]
        self.v_angle = v_angle
        self.h_angle = h_angle
        self.velocity = velocity

    def penetrate_able(self) -> bool:
        return self.velocity > 0

    def __str__(self):
        return "v: {}, angle: {}, dist: {}".format(self.velocity, self.v_angle, self.distance)


class Ship:
    def __init__(self, ship_data: data.ShipData):
        self.ship_data = ship_data

    def receive_shot(self, shot: Shot, part: int):
        if part == BELT_DOME_ENG:
            return shot_belt_dome_eng(shot, self.ship_data)
        elif part == BELT_DOME_MAG:
            pass
        elif part == DECK_ENG:
            return shot_deck_eng(shot, self.ship_data)


def shot_deck_eng(shot: Shot, ship: data.ShipData):
    deck = ship["Deck-engine"]
    steel = ship["Deck-steel"]
    return shot_deck(shot, ship, deck * steel, ENGINE)


def shot_deck_mag(shot: Shot, ship: data.ShipData):
    deck = ship["Deck-magazine"]
    steel = ship["Deck-steel"]
    return shot_deck(shot, ship, deck * steel, MAGAZINE)


def shot_deck(shot: Shot, ship: data.ShipData, main_deck_thickness: float, worst_result):
    outer = ship["Deck-outer"]
    inner = ship["Deck-inner"]
    if penetration(shot, outer, 0):
        if penetration(shot, main_deck_thickness, 0):
            return worst_result
        else:
            return ROOM
    else:
        return RICOCHET


def shot_belt_dome_eng(shot: Shot, ship: data.ShipData):
    belt = ship["Belt-engine"]
    belt_steel = ship["Belt-steel"]
    dome = ship["Dome-engine"]
    dome_steel = ship["Deck-steel"]
    return shot_belt_dome(shot, ship, belt * belt_steel, dome * dome_steel, ENGINE)


def shot_belt_dome_mag(shot: Shot, ship: data.ShipData):
    belt = ship["Belt-magazine"]
    belt_steel = ship["Belt-steel"]
    dome = ship["Dome-magazine"]
    dome_steel = ship["Deck-steel"]
    return shot_belt_dome(shot, ship, belt * belt_steel, dome * dome_steel, MAGAZINE)


def shot_belt_dome(shot: Shot, ship: data.ShipData, belt_thickness, dome_thickness, worst_result):
    outer = ship["Belt-outer"]
    # inner = ship["Belt-inner"]
    belt_angle = ship["Belt-angle"] + 90
    dome_angle = ship["Dome-angle"]

    if penetration(shot, outer, belt_angle):
        if penetration(shot, belt_thickness, belt_angle):
            if penetration(shot, dome_thickness, dome_angle):
                return worst_result
            else:
                return ROOM
        else:
            return BLOCKED
    else:
        return RICOCHET


class ShipGame:
    def __init__(self):
        self.data_set = data.DataSet()

    def self_immune_zone(self, ship_name: str):
        return self.immune_zone(ship_name, ship_name)

    def immune_zone(self, shoot_ship_name: str, ship_name: str):
        shoot_ship = self.data_set.get_ship(shoot_ship_name)
        ship = self.data_set.get_ship(ship_name)
        belt_eng = belt_immune_eng(shoot_ship, ship)
        belt_mag = belt_immune_mag(shoot_ship, ship)
        deck_eng = deck_immune_eng(shoot_ship, ship)
        deck_mag = deck_immune_mag(shoot_ship, ship)
        return {"Engine": (belt_eng, deck_eng), "Magazine": (belt_mag, deck_mag)}

    def fire_shot(self, ship_name: str, distance: int, h_angle: float):
        return fire_shot(self.data_set.get_ship(ship_name), distance, h_angle)

    def firing_range(self, ship_name: str):
        ship = self.data_set.get_ship(ship_name)
        close = 0
        far = 100000
        while far - close > 1:
            mid = (far - close) // 2 + close
            try:
                fire_shot(ship, mid, 0)
            except OutOfFiringRange:
                far = mid
            else:
                close = mid
        return close


def belt_immune_mag(shoot_ship: data.ShipData, ship: data.ShipData):
    return belt_immune(shoot_ship, ship, shot_belt_dome_mag, MAGAZINE)


def belt_immune_eng(shoot_ship: data.ShipData, ship: data.ShipData):
    return belt_immune(shoot_ship, ship, shot_belt_dome_eng, ENGINE)


def belt_immune(shoot_ship: data.ShipData, ship: data.ShipData, fn, penetrate_code):
    close = 0
    far = 100000
    while far > 0:
        mid = (far - close) // 2 + close
        try:
            shot1 = fire_shot(shoot_ship, mid, 0)
        except OutOfFiringRange:
            far = mid
        else:
            if fn(shot1, ship) == penetrate_code:
                shot2 = fire_shot(shoot_ship, mid + 1, 0)
                if fn(shot2, ship) != penetrate_code:
                    return mid + 1
                else:
                    close = mid
            else:
                far = mid
    return 0


def deck_immune_eng(shoot_ship: data.ShipData, ship: data.ShipData):
    return deck_immune(shoot_ship, ship, shot_deck_eng, ENGINE)


def deck_immune_mag(shoot_ship: data.ShipData, ship: data.ShipData):
    return deck_immune(shoot_ship, ship, shot_deck_mag, MAGAZINE)


def deck_immune(shoot_ship: data.ShipData, ship: data.ShipData, fn, penetrate_code):
    close = 0
    far = 100000
    while True:
        mid = (far - close) // 2 + close
        try:
            shot1 = fire_shot(shoot_ship, mid, 0)
        except OutOfFiringRange:
            far = mid
        else:
            if fn(shot1, ship) != penetrate_code:
                try:
                    shot2 = fire_shot(shoot_ship, mid + 1, 0)
                except OutOfFiringRange:
                    return float('inf')

                if fn(shot2, ship) == penetrate_code:
                    return mid + 1
                else:
                    close = mid
            else:
                far = mid


def fire_shot(ship: data.ShipData, distance: int, h_angle: float) -> Shot:
    mass = ship["AP-mass"]
    init = ship["AP-velocity"]
    resist = ship["AP-resist"]

    v_reduce_rate = (resist / mass) ** 0.72
    h_reduced = v_reduce_rate * distance ** 0.93 / 1.72
    h_v = init - h_reduced
    v_v = v_reduce_rate ** 0.5 * distance ** 1.15 / 115

    ele = ship["Elevation"]
    max_ratio = ele * 0.01125
    if v_v / init > max_ratio:
        raise OutOfFiringRange()
    velocity = math.sqrt(h_v ** 2 + v_v ** 2)
    # print(h_v, v_v)
    landing_angle = math.degrees(math.atan(v_v / h_v))

    return Shot(distance, velocity, landing_angle, h_angle, ship)


def total_angle(landing_angle: float, shooting_angle: float, armor_angle: float) -> float:
    """
    This result may not be correct, but enough.

    :param landing_angle: shell landing vertical angle, 0 for horizontal
    :param shooting_angle: shell path horizontal angle, 0 for perpendicular to ship side
    :param armor_angle: armor angle, 0 for horizontal
    :return: the total angle, 0 for perpendicular to armor
    """
    v_angle = landing_angle + armor_angle - 90
    if armor_angle == 0:
        return abs(v_angle)
    v_sec = 1 / math.cos(math.radians(v_angle))
    rect_diag = 1 / math.cos(math.radians(shooting_angle))
    vol_diag = v_sec * rect_diag
    total_ang = math.acos(1 / vol_diag)
    deg = math.degrees(total_ang)
    return deg


def velocity_need(shot: Shot, armor_thickness: float, armor_angle: float) -> float:
    """

    :param shot:
    :param armor_thickness:
    :param armor_angle: vertical as 90, horizontal as 0
    :return:
    """
    landing_angle = total_angle(shot.v_angle, shot.h_angle, armor_angle)
    e = mm_to_inches(armor_thickness)
    d = mm_to_inches(shot.caliber)
    m = kilo_to_pounds(shot.mass)
    coe = 6 * (e/d - 0.45) * (landing_angle ** 2 + 2000) + 40000
    vl = coe * math.sqrt(e) * d / (41.57 * math.sqrt(m) * math.cos(math.radians(landing_angle)))
    return feet_to_meters(vl)


def penetration(shot: Shot, thickness: float, armor_angle: float) -> bool:
    vn = velocity_need(shot, thickness / shot.ef, armor_angle)
    if vn >= shot.velocity:
        shot.velocity = 0
        return False
    else:
        shot_energy = shot.velocity ** 2
        lost_energy = vn ** 2
        remain_energy = shot_energy - lost_energy
        shot.velocity = remain_energy ** 0.5
        if thickness * 5 >= shot.caliber:
            shot.ef -= 0.1
        return True


def mm_to_inches(mm: float) -> float:
    return mm / 25.4


def kilo_to_pounds(kg: float):
    return kg / 0.454


def feet_to_meters(ft: float):
    return ft * 0.3048


class OutOfFiringRange(Exception):
    def __init__(self, msg=""):
        Exception.__init__(self, msg)
