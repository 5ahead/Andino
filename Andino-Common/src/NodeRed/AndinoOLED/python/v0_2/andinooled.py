# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time
import digitalio
import board
import adafruit_ssd1306
import urllib, json
import socket

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

# Raspberry Pi pin configuration:
oled_reset = digitalio.DigitalInOut(board.D4)

# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 64  # Change to 64 if needed
BORDER = 5
i2c = board.I2C()
disp = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)


# Initialize library.

url = "http://oeebox/fsm/monitor.dal"


disp.fill(0)

# Clear display.
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
#draw.rectangle((0,0,width,height), outline=0, fill=0)
draw.rectangle((0,0,width,height), outline=1, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 2


# Load default font.
font = ImageFont.load_default()
fontC = ImageFont.truetype(r"/usr/share/fonts/truetype/FIRACODE.TTF", 30)

# global variables
dualMode = False
modes = [10, 20]
lines = [["l1", "l2", "l3", "l4", "l5", "l6"], ["l1", "l2", "l3", "l4", "l5", "l6"]]
scrolling = [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
offset = 0


# Reads the msg content and stores it in the global variables
def readmsg(msg):
    msgdata = msg.split("$#")

    # scrolling array
    for loop in range(0, 6):
        scrolling[0][loop] = msgdata[3 + (loop * 2)]
        scrolling[1][loop] = msgdata[15 + (loop * 2)]

    # lines array
    for loop in range(0, 6):
        lines[0][loop] = msgdata[2 + (loop * 2)]
        lines[1][loop] = msgdata[14 + (loop * 2)]

    # modes array
    modes[0] = int(msgdata[0])
    modes[1] = int(msgdata[1])

    # check for dualMode
    global dualMode
    if modes[1] != -1:
        dualMode = True
    else:
        dualMode = False


# Prints the content of the global variables on the display
def printdisplay():
    global dualMode
    global modes
    global lines
    global scrolling
    global offset

    print('dual ' + str(dualMode))
    print('modes ' + str(modes))
    print('lines ' + str(lines))
    print('scrolling ' + str(scrolling))
    print('offset ' + str(offset))

    # runs while loop twice if dualMode is True
    runs = 1;
    if dualMode:
        runs = 2

    i = 0
    while i < runs:
        # Reset offset on first run
        if i == 0:
            offset = 0

        # clear the image with a black rectangle
        draw.rectangle((0 + offset, top, width, height), outline=0, fill=0)
        offset += 1

        # 1 Line, 3 Chars mode
        if modes[i] == 10:
            fontC = ImageFont.truetype(r"/usr/share/fonts/truetype/FIRACODE.TTF", 60)

            draw.text((x + offset, top), lines[i][0], font=fontC, fill=255)

        # 1 Line, 4 Chars mode
        if modes[i] == 11:
            fontC = ImageFont.truetype(r"/usr/share/fonts/truetype/FIRACODE.TTF", 30)
            draw.rectangle((0, 0, width - 1, height - 1), outline=1, fill=0)
            draw.text((x + offset + 20, top + 20), lines[i][0], font=fontC, fill=255)

        # 2 Line, 6 Chars
        if modes[i] == 20:
            fontC = ImageFont.truetype(r"/usr/share/fonts/truetype/FIRACODE.TTF", 30)
            draw.text((x + offset, top), lines[i][0], font=fontC, fill=255)
            draw.text((x + offset, top + 35), lines[i][1], font=fontC, fill=255)

        # 2 Line, 9 Chars
        if modes[i] == 21:
            fontC = ImageFont.truetype(r"/usr/share/fonts/truetype/FIRACODE.TTF", 22)
            draw.text((x + offset, top + 5), lines[i][0], font=fontC, fill=255)
            draw.text((x + offset, top + 40), lines[i][1], font=fontC, fill=255)

        # 3 Line, 9 Chars
        if modes[i] == 30:
            fontC = ImageFont.truetype(r"/usr/share/fonts/truetype/FIRACODE.TTF", 20)
            draw.text((x + offset, top + 2), lines[i][0], font=fontC, fill=255)
            draw.text((x + offset, top + 24), lines[i][1], font=fontC, fill=255)
            draw.text((x + offset, top + 46), lines[i][2], font=fontC, fill=255)

        # 3 Line, 12 Chars
        if modes[i] == 31:
            fontC = ImageFont.truetype(r"/usr/share/fonts/truetype/FIRACODE.TTF", 16)
            draw.text((x + offset, top + 2), lines[i][0], font=fontC, fill=255)
            draw.text((x + offset, top + 27), lines[i][1], font=fontC, fill=255)
            draw.text((x + offset, top + 52), lines[i][2], font=fontC, fill=255)

        # 4 Line, 14 Chars
        if modes[i] == 40:
            fontC = ImageFont.truetype(r"/usr/share/fonts/truetype/FIRACODE.TTF", 14)
            draw.text((x + offset, top + 1), lines[i][0], font=fontC, fill=255)
            draw.text((x + offset, top + 17), lines[i][1], font=fontC, fill=255)
            draw.text((x + offset, top + 34), lines[i][2], font=fontC, fill=255)
            draw.text((x + offset, top + 51), lines[i][3], font=fontC, fill=255)

        # 6 Line
        if modes[i] == 60:
            fontC = ImageFont.truetype(r"/usr/share/fonts/truetype/FIRACODE.TTF", 8)
            draw.text((x + offset, top + 3), lines[i][0], font=fontC, fill=255)
            draw.text((x + offset, top + 13), lines[i][1], font=fontC, fill=255)
            draw.text((x + offset, top + 23), lines[i][2], font=fontC, fill=255)
            draw.text((x + offset, top + 33), lines[i][3], font=fontC, fill=255)
            draw.text((x + offset, top + 43), lines[i][4], font=fontC, fill=255)
            draw.text((x + offset, top + 53), lines[i][5], font=fontC, fill=255)

        # Set offset to half of the display width for dual mode, increase i
        offset = width / 2
        i += 1

        # Display image.
        disp.image(image)
        disp.show()


# TCP socket (server)
HOST = "localhost"  # Standard loopback interface address (localhost)
PORT = 2961        # Port to listen on (non-privileged ports are > 1023)
msg = ' '
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
print('Server is available on ' + HOST + ':' + str(PORT))

while True:
    s.listen(0)
    print('Listening for client sockets...')
    conn, addr = s.accept()
    print('Connection established!', addr)
    while True:
        data = conn.recv(1024)
        if not data:
            break
        msg = data.decode("utf-8")
        readmsg(msg)
        printdisplay()

