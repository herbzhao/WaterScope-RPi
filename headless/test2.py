import os

filename = "timelapse_data/20200622-18:33:07/0_0002_20200622-18:39:49.jpg"
if os.path.exists(filename.replace('.jpg', '_result.txt')):
    with open(filename.replace('.jpg', '_result.txt')) as file:
        lines = file.readlines()
        result = {}
        for line in lines:
            bacteria_name = line.split(':')[0].replace(' ', '').replace('\t','').replace('\n', '')
            count = line.split(':')[1].replace(' ', '').replace('\t','').replace('\n', '')
            result[bacteria_name] =  count

print(result)