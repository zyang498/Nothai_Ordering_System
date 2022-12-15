def get_locations(fname=None, locations=None):
    locations_list = []
    if not fname:
        for item in locations:
            location = item.find("p").text.split("\n")[0]
            locations_list.append(location)
        fname = 'Locations.txt'
        with open(fname, 'w') as f:
            for location in locations_list:
                f.write(f"{location}\n")
    else:
        with open(fname, 'r') as f:
            for line in f:
                locations_list.append(line.strip())
    return locations_list