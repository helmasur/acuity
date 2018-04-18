# coding: utf-8
import os, pygame
import sys
from pygame.locals import *
#from PIL import Image()
import glob
import concurrent.futures

#TODO
#none!

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')
img_dir = "f:\Temp"
out_dir = data_dir #"f:\_berg1mirrors"
files = glob.glob(os.path.join(img_dir, '*.jpg'))
batch = 50 #len(files)
fieldsize = 500
print "Files found:", len(files)

def process_image(index, fieldsize):
        image = pygame.image.load(files[index])
        array = pygame.PixelArray(image)
        width = image.get_rect().width
        height = image.get_rect().height
        posx = int(width/2 - fieldsize/2)
        posy = int(height/2 - fieldsize/2)
        image_acuties = []
        for x in range(posx, posx+fieldsize):
            for y in range(posy, posy+fieldsize):
                pixelacuity = [0,0,0,0,0,0,0,0]
                pixelacuity[0] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x][y-1])) / min(get_bright(image, array[x][y]), get_bright(image, array[x][y-1]))
                pixelacuity[1] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x+1][y-1])) / min(get_bright(image, array[x][y]), get_bright(image, array[x+1][y-1]))
                pixelacuity[2] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x+1][y])) / min(get_bright(image, array[x][y]), get_bright(image, array[x+1][y]))
                pixelacuity[3] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x+1][y+1])) / min(get_bright(image, array[x][y]), get_bright(image, array[x+1][y+1]))
                pixelacuity[4] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x][y+1])) / min(get_bright(image, array[x][y]), get_bright(image, array[x][y+1]))
                pixelacuity[5] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x-1][y+1])) / min(get_bright(image, array[x][y]), get_bright(image, array[x-1][y+1]))
                pixelacuity[6] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x-1][y])) / min(get_bright(image, array[x][y]), get_bright(image, array[x-1][y]))
                pixelacuity[7] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x-1][y-1])) / min(get_bright(image, array[x][y]), get_bright(image, array[x-1][y-1]))
                pixelacuity_sum = sum(pixelacuity) / 8.0
                image_acuties.append(pixelacuity_sum)
        length = len(image_acuties)
        image_acuity = sum(image_acuties)*1.0/length*100 - 100
        #self.images_acuity[index] = image_acuity
        del image
        del array
        print image_acuity
        return image_acuity

def get_bright(image, pixel):
        rgb = image.unmap_rgb(pixel)
        return rgb[0]+rgb[1]+rgb[2]


def main():

    pygame.init()
    
    images_acuity = [0 for x in range(batch)]
    for i in range(batch):
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(process_image, i, fieldsize)


if __name__ == '__main__':
    main()