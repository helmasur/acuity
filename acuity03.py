# coding: utf-8
import os, pygame
import sys
from pygame.locals import *
#from PIL import Image()
import glob
# import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, as_completed
import random

#TODO
#none!

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')
img_dir = "f:\Temp"
out_dir = data_dir #"f:\_berg1mirrors"
files = glob.glob(os.path.join(img_dir, '*.jpg'))
batch_length = len(files)
fieldsize = 400 # 451ok 452ok 451ok 453err 454err 600err
group_size = 3
workers = 3
#print "Files found:", len(files)

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
        return (index, image_acuity)

def fake_process(index, fieldsize):
    num = random.random()*10
    num = int(num*1000)/1000.0
    return (index, num)

def get_bright(image, pixel):
        rgb = image.unmap_rgb(pixel)
        return rgb[0]+rgb[1]+rgb[2]


def main():

    pygame.init()
    
    # images_acuity = [0 for x in range(batch)]
    futures = []
    batch_pos = batch_length
    while batch_pos > 0:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for x in range(workers):
                if batch_pos > 0:
                    print batch_pos, "of", batch_length
                    futures.append(executor.submit(fake_process, batch_pos-1, fieldsize))
                    batch_pos -= 1
                    


    results_per_acuity = []
    results_per_index = []
    for f in as_completed(futures):
        results_per_index.append(f.result())
        results_per_acuity.append( (f.result()[1], f.result()[0]) )
    results_per_index.sort()
    results_per_index.reverse()
    results_per_acuity.sort()
    # print results_per_index
    # print results_per_acuity

    batch_pos = batch_length-1
    groups = []
    group_index = 0
    while batch_pos >= 0:
        groups.append([])
        for a in range(group_size):
            groups[group_index].append((files[batch_pos], results_per_index[batch_pos][1]))
            batch_pos -= 1
        groups[group_index].sort()
        group_index +=1
        print ""
    print groups


if __name__ == '__main__':
    main()