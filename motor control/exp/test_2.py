def test():
    global number_of_image
    try: 
        number_of_image
    except NameError:
        number_of_image = 1
        print(number_of_image)
    print('{}'.format(number_of_image))
    return 'number_of_image'

a = test()
b = number_of_image + 1
print(b)