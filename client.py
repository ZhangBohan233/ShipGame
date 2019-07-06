if __name__ == "__main__":
    from data import *
    from calculations import *

    sg = ShipGame()
    zl02 = Ship(sg.data_set.get_ship("ZL02"))
    shot = sg.fire_shot("ZL02", 15000, 0)
    print(zl02.receive_shot(shot, BELT_DOME_ENG))
    shot = sg.fire_shot("ZL02", 30000, 0)
    print(shot)
    print(zl02.receive_shot(shot, DECK_ENG))
    print(sg.self_immune_zone("ZL02"))
