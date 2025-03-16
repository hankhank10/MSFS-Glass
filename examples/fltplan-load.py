import configparser

config = configparser.ConfigParser()
config_file = "test.flt"
config.read(config_file)

gps_lines = config["GPS_Engine"]

count_wp = int(gps_lines["CountWP"])

wp_arr = []

for i in range(count_wp):
    wp_arr.append(gps_lines["WPinfo" + str(i)].replace(" ", "").split(","))

print(wp_arr)







