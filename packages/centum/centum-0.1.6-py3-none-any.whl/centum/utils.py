'''
Utilities for analyzing evapotranspiration (ET) data using xarray.
'''


def get_CLC_code_def():
    
    clc_codes = {
        "111": "Continuous urban fabric",
        "112": "Discontinuous urban fabric",
        "121": "Industrial or commercial units",
        "122": "Road and rail networks and associated land",
        "123": "Port areas",
        "124": "Airports",
        "131": "Mineral extraction sites",
        "132": "Dump sites",
        "133": "Construction sites",
        "141": "Green urban areas",
        "142": "Sport and leisure facilities",
        "211": "Non-irrigated arable land",
        "212": "Permanently irrigated land",
        "213": "Rice fields",
        "221": "Vineyards",
        "222": "Fruit trees and berry plantations",
        "223": "Olive groves",
        "231": "Pastures",
        "241": "Annual crops associated with permanent crops",
        "242": "Complex cultivation patterns",
        "243": "Land principally occupied by agriculture, with significant areas of natural vegetation",
        "244": "Agro-forestry areas",
        "311": "Broad-leaved forest",
        "312": "Coniferous forest",
        "313": "Mixed forest",
        "321": "Natural grasslands",
        "322": "Moors and heathland",
        "323": "Sclerophyllous vegetation",
        "324": "Transitional woodland-shrub",
        "331": "Beaches, dunes, sands",
        "332": "Bare rocks",
        "333": "Sparsely vegetated areas",
        "334": "Burnt areas",
        "335": "Glaciers and perpetual snow",
        "411": "Inland marshes",
        "412": "Peat bogs",
        "421": "Salt marshes",
        "422": "Salines",
        "423": "Intertidal flats",
        "511": "Water courses",
        "512": "Water bodies",
        "521": "Coastal lagoons",
        "522": "Estuaries",
        "523": "Sea and ocean"
    }
    
    return clc_codes



