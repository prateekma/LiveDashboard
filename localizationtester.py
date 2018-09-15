import math
import tkinter as tk
import matplotlib
import numpy as np
import sys
import base64

matplotlib.use('agg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from networktables import NetworkTables

from matplotlib.image import imread
from matplotlib.figure import Figure
from matplotlib import animation
from matplotlib import font_manager as fm


class Main(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.title(self, 'FRC 5190 Localization Tester')
        tk.Tk.iconbitmap(self, 'images/dashicon.ico')

        self.state('zoomed')
        self.configure(background='white')

        ip = ''
        if len(sys.argv) > 1 and sys.argv[1] == "local":
            ip = '127.0.1.1'
        else:
            ip = '10.51.90.2'

        Dashboard(parent=self, ip=ip).pack(side=tk.TOP)


class Dashboard(tk.Frame):
    def __init__(self, parent, ip):
        tk.Frame.__init__(self, parent)

        # Initialize Network Tables
        NetworkTables.initialize(server=ip)
        nt_instance = NetworkTables.getTable('Live Dashboard')

        # Font
        kanit_italic = fm.FontProperties(fname='kanitfont/kanit-italic.otf')

        # Figure
        fig = Figure(figsize=(13, 9), dpi=90)
        field_plot = fig.add_subplot(111)
        fig.set_tight_layout('True')

        # Localizer A Values
        loc_a_x_values = [1.5]
        loc_a_y_values = [23.5]
        loc_a_heading_values = [0.0]

        # Localizer B Values
        loc_b_x_values = [1.5]
        loc_b_y_values = [23.5]
        loc_b_heading_values = [0.0]

        # Localizer C Values
        loc_c_x_values = [1.5]
        loc_c_y_values = [23.5]
        loc_c_heading_values = [0.0]

        # Localizer D Values
        loc_d_x_values = [1.5]
        loc_d_y_values = [23.5]
        loc_d_heading_values = [0.0]

        # Robot Location Display
        robot_x_display = field_plot.text(
            0, -2, '', fontproperties=kanit_italic, size=11, color='#690a0f')
        robot_y_display = field_plot.text(
            0, -3, '', fontproperties=kanit_italic, size=11, color='#690a0f')
        robot_heading_display = field_plot.text(
            0, -4, '', fontproperties=kanit_italic, size=11, color='#690a0f')

        # Title Display
        field_plot.text(
            0, 27.7, 'FRC 5190 Localization Tester', fontproperties=kanit_italic, size=20, color='#690a0f')

        def draw_field(subplot):
            subplot.set_axis_off()

            red_alliance = imread('images/red_alliance.png')
            blue_alliance = imread('images/blue_alliance.png')

            subplot.imshow(red_alliance, extent=[0, 32, 0, 27])
            subplot.imshow(blue_alliance, extent=[22, 54, 0, 27])

        def rotate_point(p, center, angle):
            sin = math.sin(angle)
            cos = math.cos(angle)

            px = p[0] - center[0]
            py = p[1] - center[1]
            pxn = px * cos - py * sin
            pyn = px * sin + py * cos

            px = pxn + center[0]
            py = pyn + center[1]
            return px, py

        def gen_robot_square(p, heading):
            robot_width = 33.0 / 12.0
            robot_length = 2.458

            top_left = (p[0] - robot_width / 2.0, p[1] + robot_length / 2.0)
            top_right = (p[0] + robot_width / 2.0, p[1] + robot_length / 2.0)
            bottom_left = (p[0] - robot_width / 2.0, p[1] - robot_length / 2.0)
            bottom_right = (p[0] + robot_width / 2.0,
                            p[1] - robot_length / 2.0)

            mid = (top_right[0] + 0.5, (top_right[1] + bottom_right[1]) / 2)

            top_left = rotate_point(top_left, p, heading)
            top_right = rotate_point(top_right, p, heading)
            bottom_left = rotate_point(bottom_left, p, heading)
            bottom_right = rotate_point(bottom_right, p, heading)
            mid = rotate_point(mid, p, heading)

            box = [top_left, top_right, mid,
                   bottom_right, bottom_left, top_left]
            return box

        def update_text(lax, lay, lah):
            robot_x_display.set_text('Robot X: ' + str(lax))
            robot_y_display.set_text('Robot Y: ' + str(lay))
            robot_heading_display.set_text(
                'Robot Heading: ' + str(np.degrees(lah)) + '°')

            return [robot_x_display, robot_y_display, robot_heading_display]

        def reset_arrays():
            del loc_a_x_values[:]
            del loc_a_y_values[:]
            del loc_a_heading_values[:]
            del loc_b_x_values[:]
            del loc_b_y_values[:]
            del loc_b_heading_values[:]
            del loc_c_x_values[:]
            del loc_c_y_values[:]
            del loc_c_heading_values[:]
            del loc_d_x_values[:]
            del loc_d_y_values[:]
            del loc_d_heading_values[:]

        def update_plot(_, robot, loc_a, loc_b, loc_c, loc_d):

            if nt_instance.getBoolean('Reset', False):
                reset_arrays()
                nt_instance.putBoolean('Reset', False)

            sp = nt_instance.getString('Starting Position', 'Left')
            ssa = nt_instance.getString('Same Side Auto', '3 Scale')
            ca = nt_instance.getString('Cross Auto', '2 Scale')

            default_y = 23.5
            default_heading = 0

            lax = nt_instance.getNumber('Robot (A) X', 1.5)
            lay = nt_instance.getNumber('Robot (A) Y', default_y)
            lah = nt_instance.getNumber('Robot (A) Heading', default_heading)

            lbx = nt_instance.getNumber('Robot (B) X', 1.5)
            lby = nt_instance.getNumber('Robot (B) Y', default_y)
            lbh = nt_instance.getNumber('Robot (B) Heading', default_heading)

            lcx = nt_instance.getNumber('Robot (C) X', 1.5)
            lcy = nt_instance.getNumber('Robot (C) Y', default_y)
            lch = nt_instance.getNumber('Robot (C) Heading', default_heading)

            ldx = nt_instance.getNumber('Robot (D) X', 1.5)
            ldy = nt_instance.getNumber('Robot (D) Y', default_y)
            ldh = nt_instance.getNumber('Robot (D) Heading', default_heading)

            if NetworkTables.isConnected():
                c = 'Connected'
            else:
                c = 'Disconnected'
                reset_arrays()

            loc_a_x_values.append(lax)
            loc_a_y_values.append(lay)
            loc_a_heading_values.append(lah)

            loc_b_x_values.append(lbx)
            loc_b_y_values.append(lby)
            loc_b_heading_values.append(lbh)

            loc_c_x_values.append(lcx)
            loc_c_y_values.append(lcy)
            loc_c_heading_values.append(lch)

            loc_d_x_values.append(ldx)
            loc_d_y_values.append(ldy)
            loc_d_heading_values.append(ldh)

            robot_data = gen_robot_square((lax, lay), lah)

            robot.set_data([p[0] for p in robot_data], [p[1]
                                                        for p in robot_data])
            loc_a.set_data(loc_a_x_values, loc_a_y_values)
            loc_b.set_data(loc_b_x_values, loc_b_y_values)
            loc_c.set_data(loc_c_x_values, loc_c_y_values)
            loc_d.set_data(loc_d_x_values, loc_d_y_values)

            return [robot, loc_a, loc_b, loc_c, loc_d, *update_text(lax, lay, lah)]

        draw_field(field_plot)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack()

        starting_robot = gen_robot_square(
            (loc_a_x_values[0], loc_a_y_values[0]), 0.0)
        robot, = field_plot.plot([p[0] for p in starting_robot], [
                                 p[1] for p in starting_robot], color='#690a0f')

        loc_a, = field_plot.plot(loc_a_x_values, loc_a_y_values, color='black')
        loc_b, = field_plot.plot(loc_b_x_values, loc_b_y_values, color='red')
        loc_c, = field_plot.plot(loc_c_x_values, loc_c_y_values, color='blue')
        loc_d, = field_plot.plot(loc_d_x_values, loc_d_y_values, color='green')

        field_plot.set_ylim(bottom=-7.25, top=28.5)

        ani = animation.FuncAnimation(fig, update_plot, frames=20, interval=20,
                                      fargs=(robot, loc_a, loc_b,
                                             loc_c, loc_d),
                                      blit=True)

        canvas.draw()


app = Main()
app.mainloop()
