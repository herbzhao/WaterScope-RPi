from datetime import datetime
def update_filepath(
    image_number=1,
    folder='/home/pi/Desktop/photos/',
    filename='{:%Y%m%d}-image.jpg'.format(datetime.today())):
    # Keep track of change of folder and filename and update filepath immediately"""
    filename = filename.split('.')
    filename = filename[0] + '-{:03}'.format(image_number) + filename[1]
    filepath = folder + filename
    print(filepath)
    return filepath

#folder='/home/pi/Desktop/photos/'
image_number=1
filename='{:%Y%m%d}-image.jpg'.format(datetime.today())


for i in range(0,10):
    image_number = i
    update_filepath(image_number, folder, filename) # how to use default value without specifying?

update_filepath()