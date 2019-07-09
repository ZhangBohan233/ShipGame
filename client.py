from data import *
from calculations import *


def print_shot(ship_name: str, range_):
    for i in range(0, range_, 5000):
        try:
            print(sg.fire_shot(ship_name, i, 0))
        except OutOfFiringRange:
            break


if __name__ == "__main__":
    sg = ShipGame()
    zl02 = Ship(sg.data_set.get_ship("ZL02"))
    shot = sg.fire_shot("GLBS-26", 35000, 0)
    # print_shot("Iowa", 60000)
    # print(zl02.receive_shot(shot, DECK_ENG))
    # print(sg.self_immune_zone("XBC1"))
    # print(sg.immune_zone("XBC1", "FBC7"))
    print(sg.firing_range("FBC7"))

    print(shot)
    ship = sg.ship_instance("GLBS-26")
    print(ship.receive_shot(shot, TURRET_SHIELD))
    print(parse_list([0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1]))
    print(sg.self_turret_immune_zone("GLBS-26"))
