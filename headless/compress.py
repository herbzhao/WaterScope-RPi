from PIL import Image
image = Image.open('0000_20200909-23:15:16.jpg')
image.save('compressed.jpg',quality=80,optimize=True)