import os
import sys
import concurrent.futures
#print "begin"

def square(number):
    return number*number

def main():

    for i in range(5):
        with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
            print executor.submit(square, i).result()

    print "done"

if __name__ == '__main__':
    main()