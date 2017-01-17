image_number = 1
folder = 'teeheee'
def update_filepath():
    global image_number, filepath
    filepath = 'hello world {}'.format(image_number)
    filepath = folder + filepath
    return filepath

def snap():
    global image_number, filepathd, folder
    image_number += 1
    folder = 'aaaaa'
    filepath = update_filepath()
    print(filepath)

def snap_2():
    filepath = update_filepath()
    print(filepath)


print(filepath)