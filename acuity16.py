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
from send2trash import send2trash
import pickle

#TODO
#nice graphs

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

img_dir = "f:/Temp/test/10/"   # \ does not work as expected
out_dir = data_dir
files = glob.glob(os.path.join(img_dir, '*.jpg'))
filenames = []
for filepath in files:
    filenames.append(os.path.basename(filepath))
batch_length = len(files)
fieldsize = 250 #bredd och höjd på analyserat område (ej radie)
group_size = 10 # OBS OBS OBS GLÖM INTE ÄNDRA!!!                     <<<------------- GLÖM INTE ------------ <<<
workers = 3

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
            pixelacuity[0] = max(get_bright(image, array[x][y]), get_bright(image, array[x][y-1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x][y-1]))
            pixelacuity[1] = max(get_bright(image, array[x][y]), get_bright(image, array[x+1][y-1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x+1][y-1]))
            pixelacuity[2] = max(get_bright(image, array[x][y]), get_bright(image, array[x+1][y])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x+1][y]))
            pixelacuity[3] = max(get_bright(image, array[x][y]), get_bright(image, array[x+1][y+1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x+1][y+1]))
            pixelacuity[4] = max(get_bright(image, array[x][y]), get_bright(image, array[x][y+1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x][y+1]))
            pixelacuity[5] = max(get_bright(image, array[x][y]), get_bright(image, array[x-1][y+1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x-1][y+1]))
            pixelacuity[6] = max(get_bright(image, array[x][y]), get_bright(image, array[x-1][y])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x-1][y]))
            pixelacuity[7] = max(get_bright(image, array[x][y]), get_bright(image, array[x-1][y-1])) \
                                / min(get_bright(image, array[x][y]), get_bright(image, array[x-1][y-1]))

            # pixelacuity_sum = sum(pixelacuity) / 8.0
            # image_acuties.append(pixelacuity_sum)
            pixelacuity.sort()
            image_acuties.append(pixelacuity[7])
    image_acuties.sort()
    length = len(image_acuties)
    # part = int(length * 0.95)
    part = int(length * 0.999)
    image_acuity = image_acuties[part]
    # part_low = image_acuties[0:part]
    # part_high = image_acuties[part:length]
    # part_low_acuity = sum(part_low) / len(part_low)
    # part_high_acuity = sum(part_high) / len(part_high)
    # image_acuity = (part_low_acuity+part_high_acuity) / 2
    # image_acuity = part_high_acuity
    # image_acuity = sum(image_acuties)*1.0/length*100 - 100
    return (index, image_acuity)

def fake_process_image(index, fieldsize): #for faster testing of printed output
    num = random.random()*10
    num = int(num*1000)/1000.0
    print("WARNING FAKE PROCESS")
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
    mid = len(new_list)//2   # truncating division
    if len(new_list) % 2 == 0:  # take the avg of middle two
        return (srtd[mid-1] + srtd[mid]) / 2.0
    else:
        return srtd[mid]


def load_results():
    saved_results = {}
    try:
        path = os.path.join(img_dir, "results.acuity")
        saved_results_file = open(path, "rb") #rb is read mode, bytes mode
        saved_results = pickle.load(saved_results_file)
        saved_results_file.close()
        print("Loaded saved results.")
    except FileNotFoundError:
        print("No saved results to load, continuing.")
    return saved_results

def save_results(saved_results):
    path = os.path.join(img_dir, "results.acuity")
    saved_results_file = open(path, "wb") #rb is read mode, bytes mode
    pickle.dump(saved_results, saved_results_file)
    saved_results_file.close()
    print("Saved results to results.acuity.")
    return


def main():



    pygame.init()
    screen = pygame.display.set_mode((320, 200), 0)

    saved_results = load_results()

    ### PROCESS and store future results in futures.
    futures = []
    saved_results_list = []
    batch_pos = batch_length-1
    while batch_pos >= 0: #for every round this loop creates and finishes processes, thus memory is freed
        with ProcessPoolExecutor(max_workers=workers) as executor: #this seems to be what actually finishes off processes
            for x in range(workers): #every round this loop creates a set of processes
                if batch_pos >= 0:
                    print(batch_pos+1, "of", batch_length)
                    if filenames[batch_pos] in saved_results:
                        saved_results_list.append((batch_pos, saved_results[filenames[batch_pos]]))
                        batch_pos -= 1
                    else:
                        futures.append(executor.submit(process_image, batch_pos, fieldsize))
                        batch_pos -= 1
                    

    ### GATHER results from futures and saved results
    results = []
    for f in as_completed(futures):
        results.append(f.result())
    results.extend(saved_results_list)
    results.sort()
    
    # for x in range(0,batch_length): #fake results for testing
    #     results.append((x, int(random.random()*1000)/1000.0))

    ### SAVE result to a file
    saved_results = {}
    for item in results:
        saved_results[filenames[item[0]]] = item[1]
    save_results(saved_results)

    ### SORT results into groups
    groups = []
    amount_of_groups = int(math.ceil(1.0*batch_length/group_size))
    for i in range(amount_of_groups):
        groups.append(results[i*group_size:(i+1)*group_size])


    ### CALCULATE statistics
    groups_mean = []
    groups_median = []
    tops_for_groups = []
    lows_for_groups = []
    for g in groups:
        g.sort(key = itemgetter(1), reverse = True)
        groups_mean.append(int(mean_pos(g, 1)*10000)/10000.0)
        groups_median.append(int(median_pos(g, 1)*10000)/10000.0)
        gcopy = g
        tops_for_groups.append(gcopy.pop(0))
        for item in gcopy:
            lows_for_groups.append(item)
    tops_for_groups.sort()
    lows_for_groups.sort()
    results_per_acuity = sorted(results, key = itemgetter(1), reverse = True)

    ### List of files to delete
    file_delete_list = []
    for item in lows_for_groups:
        file_delete_list.append(files[item[0]])

    
    ### PRINT
    print()

    print("  Mean acuity, groups",groups_mean)
    print("Median acuity, groups", groups_median)
    print("Weird results? Did you set the group size?")
    print()

    for x in range(len(tops_for_groups)):
        item = tops_for_groups[x]
        print("Top acuity file per group")
        print("Group:",x,"File:",files[item[0]], "Acuity:", item[1])
    print()

    # print("All files")
    # for item in results:
    #     print(files[item[0]], item[1])
    # print()

    # print("All files per acuity")
    # for item in results_per_acuity:
    #     print(files[item[0]], item[1])
    # print()

    # print("Lowest acuity files per group")
    # for x in range(len(lows_for_groups)):
    #     item = lows_for_groups[x]
    #     print("Group:",x,"File:",files[item[0]], "Acuity:", item[1])
    # print()

    # if len(file_delete_list) > 0:
    #     print("Low acuity list contains:", len(file_delete_list), "items,")
    #     print("representing", 1.0*len(file_delete_list)/len(files)*100, "% of",len(files), "files in folder.")
    #     print("Delete (to trash) files in low acuity list? Y/N")
    #     going=False
    #     while going:
    #         for event in pygame.event.get():
    #             if event.type == KEYDOWN and event.key == K_y:
    #                 for afile in file_delete_list:
    #                     send2trash(afile)
    #                     print("Moved to trash:", afile)
    #                 going = False
    #             elif event.type == KEYDOWN:
    #                 print("Exit.")
    #                 going = False


if __name__ == '__main__':
    main()