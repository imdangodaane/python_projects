#!/usr/bin/env python3
import pyglet
import argparse
import time


def bubble_sort(lst):
    # Repeat i = len(lst) times
    for i in range(len(lst)):
        # Swap if next number greater than current number
        for j in range(len(lst) - 1):
            if lst[j] > lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
                # Show current lst
                print(" ".join(str(x) for x in lst))


def insert_sort(lst):
    for i in range(1, len(lst)):
        # Find the wrong order number
        if lst[i] < lst[i - 1]:
            for j in range(i):
                # Insert wrong order number to right position
                if lst[i] <= lst[j]:
                    lst.insert(j, lst[i])
                    del(lst[i + 1])
                    print(" ".join(str(x) for x in lst))
                    break


def partition(arr, low, high):
    i = (low - 1)
    # Use pivot as highest order number
    pivot = arr[high]
    # If number <= pivot, move number to head of list
    # with increment order i
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    # Move pivot to right position
    arr[i+1], arr[high] = arr[high], arr[i+1]
    # Print for clearly observing
    print("Pivot = ", pivot)
    print(" ".join(str(x) for x in arr))
    # return pivot for next group to partition
    return (i+1)

def quick_sort(lst, low, high):
    if low < high:
        # Find partition
        pi = partition(lst, low, high)
        # Quick sort left group
        quick_sort(lst, low, pi-1)
        # Quick sort right group
        quick_sort(lst, pi+1, high)


def merge_sort(lst):
    if len(lst) > 1:
        # Seperate list
        m = int(len(lst)/2)
        L = lst[:m]
        R = lst[m:]
        merge_sort(L)
        merge_sort(R)
        # Sort as group
        i = j = k = 0
        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                lst[k] = L[i]
                i += 1
            else:
                lst[k] = R[j]
                j += 1
            k += 1
        while i < len(L):
            lst[k] = L[i]
            i += 1
            k += 1
        while j < len(R):
            lst[k] = R[j]
            j += 1
            k += 1
        print(' '.join(str(x) for x in lst))

    
def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('N', nargs='+', action='store', type=int,
                        help='an integer for the list to sort')
    parser.add_argument('--algo', metavar='ALGO', default='bubble',
                        help='specify which algorithm to use for sorting among\
                        [bubble|insert|quick|merge], default bubble')
    parser.add_argument('--gui', action='store_true',
                        help='visualise the algorithm in GUI mode')
    return parser.parse_args()


def pyglet_running(algo):
    # Making window
    display = pyglet.canvas.get_display()
    screen = display.get_default_screen()
    gui_window = pyglet.window.Window(width=screen.width-100,
                                      height=screen.height-100,
                                      resizable=True,
                                      caption="Sorting Algorithms: "+algo.capitalize()+" Sort")
    # Making label
    label = pyglet.text.Label("I should do it later ~",
                          font_name="Ubuntu Mono",
                          font_size=36,
                          x=gui_window.width//2, y=gui_window.height//2,
                          anchor_x="center", anchor_y="center")
    # Window event for drawing
    @gui_window.event
    def on_draw():
        gui_window.clear()
        label.draw()
    # Running pyglet
    pyglet.app.run()

if __name__ == "__main__":
    # Create parser
    args = make_parser()
    # Choose sorting algorithm
    if args.algo == 'bubble':
        bubble_sort(args.N)
    elif args.algo == 'insert':
        insert_sort(args.N)
    elif args.algo == 'quick':
        quick_sort(args.N, 0, len(args.N) - 1)
    elif args.algo == 'merge':
        merge_sort(args.N)
    else:
        bubble_sort(args.N)
    # Pyglet
    if args.gui is True:
        pyglet_running(args.algo)
