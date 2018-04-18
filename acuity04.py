# coding: utf-8
import os, pygame
import sys
from pygame.locals import *
#from PIL import Image()
import glob
# import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, as_completed
import random
from operator import itemgetter
import math

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

def mean_pos(lst, pos):
    get_pos = itemgetter(pos)
    new_list = []
    for item in lst:
        new_list.append(get_pos(item))
    return 1.0*sum(new_list)/len(new_list)

def median_pos(lst, pos):
    get_pos = itemgetter(pos)
    new_list = []
    for item in lst:
        new_list.append(get_pos(item))
    srtd = sorted(new_list) # returns a sorted copy
    mid = len(new_list)/2   # remember that integer division truncates
    if len(new_list) % 2 == 0:  # take the avg of middle two
        return (srtd[mid-1] + srtd[mid]) / 2.0
    else:
        return srtd[mid]


def main():

    pygame.init()
    
    # futures = []
    # batch_pos = batch_length
    # while batch_pos > 0:
    #     with ProcessPoolExecutor(max_workers=workers) as executor:
    #         for x in range(workers):
    #             if batch_pos > 0:
    #                 print batch_pos, "of", batch_length
    #                 futures.append(executor.submit(fake_process, batch_pos-1, fieldsize))
    #                 batch_pos -= 1
                    


    # results_per_acuity = []
    results_per_index = []
    groups= []
    # for f in as_completed(futures):
    #     results_per_index.append(f.result())
    # results_per_index.sort()
    global batch_length
    batch_length = 6

    for x in xrange(0,batch_length):
        results_per_index.append((x, int(random.random()*1000)/1000.0))

    amount_of_groups = int(math.ceil(1.0*batch_length/group_size))
    for i in xrange(amount_of_groups):
        groups.append(results_per_index[i*group_size:(i+1)*group_size])
    print groups

    groups_mean = []
    groups_median = []
    for g in groups:
        g.sort(key = itemgetter(1), reverse = True)
        groups_mean.append(int(mean_pos(g, 1)*1000)/1000.0)
        groups_median.append(median_pos(g, 1))
        print files[g[0][0]], g[0][1]

    print groups
    print "Mean",groups_mean
    print "Median", groups_median

        


    # results_per_acuity = sorted(results_per_index, key=itemgetter(1), reverse=True)
    # print results_per_index
    # print results_per_acuity



    # batch_pos = batch_length-1
    # groups = []
    # group_index = 0
    # while batch_pos >= 0:
    #     groups.append([])
    #     for a in range(group_size):
    #         groups[group_index].append((files[batch_pos], results_per_index[batch_pos][1]))
    #         batch_pos -= 1
    #     groups[group_index].sort()
    #     group_index +=1
    #     print ""
    # print groups


if __name__ == '__main__':
    main()