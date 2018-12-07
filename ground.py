from tkinter import *
import random
import math


root = Tk()
fr = Frame(root)
root.geometry('800x600')
canvas = Canvas(root, bg='white')
canvas.pack(fill=BOTH, expand=1)

WIDTH = 800
HEIGHT = 600


class polygon:
    def __init__(self):
        self.x = 50
        self.y = 500
        self.r = 20


class Ground:

    def __init__(self):
        self.height = list()
        self.min_height = 400
        self.max_height = 500
        self.dx = int(WIDTH)
        self.generate()


    def generate(self):
        height = random.randint(self.min_height, self.max_height)
        for i in range(800):
            self.height.append(height)
            dh = random.randint(-2, 2)
            height += dh


    def draw(self):
        for i in range(800):
            canvas.create_line(i, HEIGHT, i+1, self.height[i], width=5, fill='green')



gr = Ground()
gr.draw()
sh = polygon()


mainloop()
