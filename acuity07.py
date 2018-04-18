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


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

img_dir = "f:\Temp"
out_dir = data_dir
files = glob.glob(os.path.join(img_dir, '*.jpg'))
batch_length = 3 #len(files)
fieldsize = 500
group_size = 3
workers = 3

def process_image(index, fieldsize):
    image = pygame.image.load(files[index])
    array = pygame.PixelArray(image)
    width = image.get_rect().width
    height = image.get_rect().height
    posx = int(width/2 - fieldsize/2)
    posy = int(height/2 - fieldsize/2)
    image_acuties = []
    for x in xrange(posx, posx+fieldsize):
        for y in xrange(posy, posy+fieldsize):
            pixelacuity = [0,0,0,0,0,0,0,0]
            pixelacuity[0] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x][y-1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x][y-1]))
            pixelacuity[1] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x+1][y-1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x+1][y-1]))
            pixelacuity[2] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x+1][y])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x+1][y]))
            pixelacuity[3] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x+1][y+1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x+1][y+1]))
            pixelacuity[4] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x][y+1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x][y+1]))
            pixelacuity[5] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x-1][y+1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x-1][y+1]))
            pixelacuity[6] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x-1][y])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x-1][y]))
            pixelacuity[7] = 1.0 * max(get_bright(image, array[x][y]), get_bright(image, array[x-1][y-1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x-1][y-1]))
            pixelacuity_sum = sum(pixelacuity) / 8.0
            image_acuties.append(pixelacuity_sum)
    length = len(image_acuties)
    image_acuity = sum(image_acuties)*1.0/length*100 - 100
    return (index, image_acuity)

def fake_process(index, fieldsize): #for faster testing of printed output
    num = random.random()*10
    num = int(num*1000)/1000.0
    print "WARNING FAKE PROCESS"
    return (index, num)

def get_bright(image, pixel):
    rgb = image.unmap_rgb(pixel)
    rgb_sum = sum(rgb)
    if rgb_sum == 0: #to prevent later division by zero error
        return 1
    else:
        return rgb_sum

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


    ### PROCESS and store future results in futures.
    futures = []
    batch_pos = batch_length
    while batch_pos > 0: #for every round this loop creates and finishes processes, thus memory is freed
        with ProcessPoolExecutor(max_workers=workers) as executor: #this seems to be what actually finishes off processed
            for x in xrange(workers): #every round this loop creates a set of processes
                if batch_pos > 0:
                    print batch_pos, "of", batch_length
                    futures.append(executor.submit(process_image, batch_pos-1, fieldsize))
                    batch_pos -= 1
                    

    ### GATHER results from futures
    results = []    
    for f in as_completed(futures):
        results.append(f.result())
    results.sort()

    # for x in xrange(0,batch_length): #fake results for testing
    #     results.append((x, int(random.random()*1000)/1000.0))


    ### SORT results into groups
    groups = []
    amount_of_groups = int(math.ceil(1.0*batch_length/group_size))
    for i in xrange(amount_of_groups):
        groups.append(results[i*group_size:(i+1)*group_size])


    ### CALCULATE statistics
    groups_mean = []
    groups_median = []
    tops_for_groups = []
    lows_for_groups = []
    for g in groups:
        g.sort(key = itemgetter(1), reverse = True)
        groups_mean.append(int(mean_pos(g, 1)*1000)/1000.0)
        groups_median.append(int(median_pos(g, 1)*1000)/1000.0)
        gcopy = g
        tops_for_groups.append(gcopy.pop(0))
        for item in gcopy:
            lows_for_groups.append(item)
    tops_for_groups.sort()
    lows_for_groups.sort()
    results_per_acuity = sorted(results, key = itemgetter(1), reverse = True)

    
    ### PRINT
    print ""
    for item in tops_for_groups:
        print "Tops", item
    print ""
    print "Mean acuity %, groups",groups_mean
    print "Median acuity %, groups", groups_median
    print ""
    for item in lows_for_groups:
        print "Lows", item
    print ""
    print "All files"
    for item in results:
        print files[item[0]], item[1]
    print ""
    print "All files per acuity"
    for item in results_per_acuity:
        print files[item[0]], item[1]

        


    # results_per_acuity = sorted(results, key=itemgetter(1), reverse=True)
    # print results
    # print results_per_acuity



    # batch_pos = batch_length-1
    # groups = []
    # group_index = 0
    # while batch_pos >= 0:
    #     groups.append([])
    #     for a in range(group_size):
    #         groups[group_index].append((files[batch_pos], results[batch_pos][1]))
    #         batch_pos -= 1
    #     groups[group_index].sort()
    #     group_index +=1
    #     print ""
    # print groups


if __name__ == '__main__':
    main()