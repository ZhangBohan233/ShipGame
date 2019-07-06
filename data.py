import xlrd


class ShipData:
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return str(self.data)

    def __getitem__(self, item):
        return self.data[item]


class DataSet:
    def __init__(self):
        self.ships = {}
        table = xlrd.open_workbook("data/ships.xlsx")
        ship_table = table.sheet_by_index(0)
        keys = ship_table.col_values(0)
        rows = ship_table.nrows
        columns = ship_table.ncols
        for ch in range(2, columns):
            dic = {}
            for k in range(rows):
                key = keys[k]
                val = ship_table.cell(k, ch).value
                if key != "":
                    dic[keys[k]] = val
            number = dic["Number"]
            self.ships[number] = ShipData(dic)

    def get_ship(self, number: str) -> ShipData:
        return self.ships[number]
