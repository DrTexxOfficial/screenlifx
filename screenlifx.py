#!/usr/bin/env python3

# some quick & dirty code to set LIFX color with the average
# screen color. Works for VLC, some games, etc.

# use the LIFX LAN protocol via the excellent library by Meghan Clark
# https://github.com/mclarkk/lifxlan
from lifxlan import *

from mss import mss
from PIL import Image
import time, os, colorsys

# helper for colors conversion/scaling
def rgb2hsv(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    h = h * 0xffff
    s = s * 0xffff
    v = v * 0xffff
    return(h, s, v)

def main():
    # start with the LIFX business...
    lifx = LifxLAN(None)
    print("Discovering lights...")
    devices = lifx.get_lights()
    for d in devices:
        print("{} ({}) HSBK: {}".format(d.get_label(), d.mac_addr, d.get_color()))
    print()

    # the block of data to analyze.
    # PIL resizing to 1x1 seems to do strange things; a bigger box works better
    # and still plenty fast...
    rx = 64
    ry = 36
    totpixels = rx * ry

    # screen scanning loop
    while True:
        with mss() as sct: image_file = sct.shot()
        img_org = Image.open(image_file)
        width_org, height_org = img_org.size
        width = int(width_org * 0.75)
        height = int(height_org * 0.75)
        # best down-sizing filter
        #img_resized = img_org.resize((width, height), Image.ANTIALIAS)
        # quickest down-sizing filter
        img_resized = img_org.resize((width, height), Image.NEAREST)
        img = img_resized
        t1 = time.process_time()
        # let PIL to shrink the image into a more manageable size
        # (just few ms in your average machine)
        img = img.resize((rx, ry))
        red = green = blue = 0
        for y in range(0, img.size[1]):
            for x in range(0, img.size[0]):
                c = img.getpixel((x,y))
                red = red + c[0]
                green = green + c[1]
                blue = blue + c[2]
        red = red / totpixels
        green = green / totpixels
        blue = blue / totpixels
        t2 = time.process_time()

        print("\rRGB {:.1f} {:.1f} {:.1f}".format(red, green, blue))
        print("- Time {}".format(t2-t1))

        h, s, v = rgb2hsv(red, green, blue)
        color = (h, s, v, 0)
        lifx.set_color_all_lights(color, 150, rapid=True)

        time.sleep(1/50)

if __name__ == '__main__':
    main()
