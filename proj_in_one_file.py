from math import *
from tkinter import *
from enum import Enum

screen_width = 600
screen_height = 400
dt = 0.2  # физический шаг времени между кадрами обсчёта
g = -9.8  # гравитационное ускорение
V_max = 50
fps = 30  # количество кадров в секунду
sleep_time = round(1000 / fps)
default_target_born_time = 5  # секунд
scores_format = 'очки: %d'
sum1 = 0
sum2 = 0
pl_nom = 0
players_number = 2
gm_finished = False

def screen(physical_x, physical_y):
    screen_x = physical_x
    screen_y = screen_height - physical_y
    return screen_x, screen_y


def physical(screen_x, screen_y):
    physical_x = screen_x
    physical_y = screen_height - screen_y
    return physical_x, physical_y


class GameState(Enum):
    TANK_IS_AIMING = 1
    SHELL_IS_FLYING = 2


class MainWindow:
    def __init__(self, root):
        global canvas
        canvas = Canvas(root)
        canvas["width"] = screen_width
        canvas["height"] = screen_height
        canvas.pack()
        img = PhotoImage(file='usa_kapitoliy.png')
        canvas.create_image(0, 0, anchor=NW, image=img)
        label = Label(image=img)
        label.image = img

        self.terra = Terra()
        self.tanks = []

        x = 70
        y = screen_height - 100
        self.tanks.append(Tank(x, y))

        x = screen_width - 70
        y = screen_height - 100
        self.tanks.append(Tank(x, y))

        self.current_player = 0
        self.shells = []
        self.scores = sum1
        self.scores_text = canvas.create_text(screen_width - 50, 10,
                                              text=scores_format % self.scores)
        canvas.bind("<Button-1>", self.mouse_click)
        canvas.bind("<Motion>", self.mouse_motion)

        self.game_state = GameState.TANK_IS_AIMING

    def key_pressed(self, event):
        if event.char == 'a':
            print('a')
        elif event.char == 'd':
            print('d')


    def mouse_motion(self, event):
        if self.game_state != GameState.TANK_IS_AIMING:
            return  # ничего не делаем
        tank = self.tanks[self.current_player]
        x, y = physical(event.x, event.y)
        tank.aim(x, y)

    def mouse_click(self, event):
        """ Проверяем, далеко ли шарик, и, если в него попали, то "лопаем" его,
            создаём новый шарик, а за старый начисляем очки.
        """
        if self.game_state != GameState.TANK_IS_AIMING:
            return  # ничего не делаем
        tank = self.tanks[self.current_player]
        x, y = physical(event.x, event.y)
        tank.aim(x, y)
        shell = tank.shoot(x, y)
        self.shells.append(shell)
        # смена состояния игры - танки замирают на время полёта снаряда
        self.game_state = GameState.SHELL_IS_FLYING
        canvas.after(sleep_time, self.shell_flying)  # запуск полёта снаряда
        # смена игрока по кругу
        self.current_player = (self.current_player + 1) % players_number

    def shell_flying(self, *ignore):
        if self.game_state != GameState.SHELL_IS_FLYING:
            return  # ничего не делаем

        canvas.after(sleep_time, self.shell_flying)  # перезапуск цикла

        # смещаем цели и снаряды
        for shell in self.shells:
            shell.move()
        # проверяем столкновение снаряда с землёй
        for shell in self.shells:
            if self.terra.check_contact(shell):
                self.terra.excavate(shell)
                self.game_state = GameState.TANK_IS_AIMING
        if self.game_state != GameState.SHELL_IS_FLYING:
            self.shells.clear()  # Убираем все снаряды, если хотя бы один взорвался


class Ball:
    def __init__(self, x, y, r, Vx, Vy, color):
        self.x, self.y, self.r = x, y, r
        self.Vx, self.Vy = Vx, Vy
        self.avatar = canvas.create_oval(screen(x - r, y - r),
                                         screen(x + r, y + r), fill=color)

    def check_contact(self, x, y):
        l = ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5
        return l <= self.r

    def destroy(self):
        canvas.delete(self.avatar)

    def move(self):
        """ сдвинуть шарик на его скорость """
        ax = 0
        ay = g
        self.x += self.Vx * dt
        self.y += self.Vy * dt - 10 * dt
        self.Vx += ax * dt
        self.Vy += ay * dt
        # отражения слева, справа, снизу
        if self.x - self.r <= 0:
            self.Vx = -self.Vx
            self.x = self.r + 1
        if self.x + self.r >= screen_width:
            self.Vx = -self.Vx
            self.x = screen_width - self.r - 1
        if self.y + self.r <= 0:
            self.Vy = -self.Vy
            self.y = self.r + 1

        x1, y1 = screen(self.x - self.r, self.y - self.r)
        x2, y2 = screen(self.x + self.r, self.y + self.r)
        canvas.coords(self.avatar, x1, y1, x2, y2)


class Shell(Ball):
    def __init__(self, x, y, r, Vx, Vy):
        super().__init__(x, y, r, Vx, Vy, "red")
        self.damage = 10
        self.damage_radius = 40


class Tank:
    max_cannon_length = 40
    shell_radius = 5

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.lx = 0
        self.ly = 20
        self.line = canvas.create_line(screen(self.x, self.y),
                                       screen(self.x + self.lx, self.y + self.ly),
                                       width=5, fill='yellow')

    def aim(self, x, y):
        self.lx = (x - self.x)
        self.ly = (y - self.y)
        l = (self.lx ** 2 + self.ly ** 2) ** 0.5
        self.lx = self.max_cannon_length * self.lx / l
        self.ly = self.max_cannon_length * self.ly / l

        x1, y1 = screen(self.x, self.y)
        x2, y2 = screen(self.x + self.lx, self.y + self.ly)
        canvas.coords(self.line, x1, y1, x2, y2)

    def shoot(self, x, y):
        self.aim(x, y)
        Vx = 1 * self.lx
        Vy = 1 * self.ly
        return Shell(self.x + self.lx, self.y + self.ly, self.shell_radius, Vx, Vy)


class Terra:
    def __init__(self):
        self.y = [(1.6 - sin(4 * x / screen_width)) * 70
                  for x in range(screen_width)]
        self.avatar = [canvas.create_line(screen(x, 0), screen(x, self.y[x]),
                                          fill='yellow',
                                          activefill='red')
                       for x in range(screen_width)]

    def check_contact(self, shell):
        """ True если снаряд касается земли"""
        terra_level = self.y[round(shell.x)]
        if shell.y <= terra_level:
            return True

    def excavate(self, shell):
        """ Уничтожает часть земли, задетой взрывом снаряда"""
        global sum1, sum2, pl_nom, gm_finished
        count = 0
        x_min = max(0, round(shell.x - shell.damage_radius + 1))
        x_max = min(screen_width - 1, round(shell.x + shell.damage_radius - 1))
        r = shell.damage_radius
        for x in range(x_min, x_max):
            dx = x - shell.x
            dy = (r ** 2 - dx ** 2) ** 0.5
            y1 = round(shell.y - dy)
            y2 = round(shell.y + dy)
            terra_above = max(self.y[x] - y2, 0)
            self.y[x] = min(self.y[x], y1 + terra_above)
            count += 1
        self.redraw()
        shell.destroy()
        pl_nom = (pl_nom+1)%2
        if pl_nom ==1 :
            sum1 += count
            canvas.create_polygon(5, 150, 95, 150, 95, 190, 5, 190, fill = "DarkOliveGreen1")
            canvas.create_text(50, 170, text="score: " + str(sum1))
        else:
            sum2 += count
            canvas.create_polygon(595, 150, 505, 150, 505, 190, 595, 190, fill = "MediumPurple1")
            canvas.create_text(550, 170, text="score: " + str(sum1))
        if sum1 > 850 and gm_finished == False:
            canvas.create_polygon(0, 0, 600, 0, 600, 400, 0, 400, fill = "DarkOliveGreen1")
            canvas.create_text(300, 200,text="Джобс победил!")
            gm_finished = True
        if sum2 > 850 and gm_finished == False:
            canvas.create_polygon(0, 0, 600, 0, 600, 400, 0, 400, fill = "MediumPurple1")
            canvas.create_text(300, 200,text="Гейтс победил!")
            gm_finished = True

    def redraw(self):
        for x in range(screen_width):
            x1, y1 = screen(x, 0)
            x2, y2 = screen(x, self.y[x])
            canvas.coords(self.avatar[x], x1, y1, x2, y2)


root_window = Tk()
window = MainWindow(root_window)
root_window.mainloop()
