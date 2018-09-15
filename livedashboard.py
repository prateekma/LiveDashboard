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
        tk.Tk.title(self, 'FRC 5190 Live Dashboard')
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

        # Robot Values
        robot_x_values = [1.5]
        robot_y_values = [23.5]
        robot_heading_values = [0.0]

        # Path Values
        path_x_values = [1.5]
        path_y_values = [23.5]
        path_heading_values = [0.0]

        # Lookahead Values
        lookahead_x_values = [3.5]
        lookahead_y_values = [23.5]

        # Robot Location Display
        robot_x_display = field_plot.text(
            0, -2, '', fontproperties=kanit_italic, size=11, color='#690a0f')
        robot_y_display = field_plot.text(
            0, -3, '', fontproperties=kanit_italic, size=11, color='#690a0f')
   
        robot_heading_display = field_plot.text(
            10, -2, '', fontproperties=kanit_italic, size=11, color='#690a0f')
    

        # Auto Display
        starting_pos_display = field_plot.text(
            53.9, -2, '', fontproperties=kanit_italic, size=9, horizontalalignment='right', color='#303030')
        same_side_auto_display = field_plot.text(
            53.9, -3, '', fontproperties=kanit_italic, size=9, horizontalalignment='right', color='#303030')
        cross_auto_display = field_plot.text(
            53.9, -4, '', fontproperties=kanit_italic, size=9, horizontalalignment='right', color='#303030')

        # Subsystems Display
        subsystems_display = field_plot.text(
            0, -6, '', fontproperties=kanit_italic, size=8, color='#a4969b')
        climb_display = field_plot.text(
            0, -7, '', fontproperties=kanit_italic, size=8, color='#a4969b')

        # Robot Status Display
        connection_display = field_plot.text(
            53.9, -6, '', fontproperties=kanit_italic, size=8, color='#a4969b', horizontalalignment='right')
        is_enabled_display = field_plot.text(
            53.9, -7, '', fontproperties=kanit_italic, size=8, color='#a4969b', horizontalalignment='right')

        # Game Data Display
        game_data_display = field_plot.text(
            53.9, 27.7, '', fontproperties=kanit_italic, size=12, color='#303030', horizontalalignment='right', alpha=0.9)

        # Title Display
        field_plot.text(
            0, 27.7, 'FRC 5190 Live Dashboard', fontproperties=kanit_italic, size=20, color='#690a0f')

        # IP Display
        field_plot.text(17, 27.7, ip, fontproperties=kanit_italic, size=10, color="#303030", alpha=0.5)

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

        def update_text(rx, ry, rh, sp, ssa, ca, dle, dlp, dla, dre, drp, dra, ee, ep, ea, ae, ap, aa, ce, cp, cam, ic, c, e, gd):
            robot_x_display.set_text('Robot X: ' + "%.3f" % (rx))
            robot_y_display.set_text('Robot Y: ' + "%.3f" % (ry))
     
            robot_heading_display.set_text(
                'Robot Angle: ' + "{0:.3f}".format(np.degrees(rh)) + '°')

 
            starting_pos_display.set_text('Starting Position: ' + sp)

            if sp == 'Center':
                same_side_auto_display.set_text('Switch Auto: 1.5 Switch')
                cross_auto_display.set_text('')
            else:
                same_side_auto_display.set_text('Same Side Auto: ' + ssa)
                cross_auto_display.set_text('Cross Auto: ' + ca)

            subsystem_str = 'LEFT DRIVE enc ' + \
                str(dle) + ': ' + str(dlp) + '% at ' + str(dla) + 'A'
            subsystem_str += '     '
            subsystem_str += 'RIGHT DRIVE enc ' + \
                str(dre) + ': ' + str(drp) + '% at ' + str(dra) + 'A'
            subsystem_str += '     '
            subsystem_str += 'ELEVATOR enc ' + \
                str(ee) + ': ' + str(ep) + '% at ' + str(ea) + 'A'
            subsystem_str += '     '
            subsystem_str += 'ARM enc ' + \
                str(ae) + ': ' + str(ap) + '% at ' + str(aa) + 'A'

            subsystems_display.set_text(subsystem_str)

            if (ic):
                climb_display.set_text(
                    'CLIMB enc ' + str(ce) + ': ' + str(cp) + '% at ' + str(cam) + 'A')
            else:
                climb_display.set_text('')

            connection_display.set_text('Robot ' + c)
            is_enabled_display.set_text(e)

            game_data_display.set_text('Game Data: ' + gd)

            return [robot_x_display, robot_y_display,
                    robot_heading_display,
                    starting_pos_display, same_side_auto_display, cross_auto_display,
                    subsystems_display, climb_display,
                    connection_display, is_enabled_display,
                    game_data_display]

        def reset_arrays():
            del robot_x_values[:]
            del robot_y_values[:]
            del robot_heading_values[:]
            del path_x_values[:]
            del path_y_values[:]
            del path_heading_values[:]

        def update_plot(_, robot_point, path_point, lookahead_point, robot, robot_path, path):
            if nt_instance.getBoolean('Reset', False):
                reset_arrays()
                nt_instance.putBoolean('Reset', False)

            sp = nt_instance.getString('Starting Position', 'Left')
            ssa = nt_instance.getString('Near Scale Auto Mode', 'ThreeCube')
            ca = nt_instance.getString('Far Scale Auto Mode', 'ThreeCube')

            default_y = 23.5
            default_heading = np.pi

            if sp == 'Right':
                default_heading = np.pi
                default_y = 27 - default_y

            elif sp == 'Center':
                default_y = 13.25
                default_heading = 0

            rx = nt_instance.getNumber('Robot X', 1.5)
            ry = nt_instance.getNumber('Robot Y', default_y)
         
            rh = nt_instance.getNumber('Robot Heading', default_heading)

            px = nt_instance.getNumber('Path X', 1.5)
            py = nt_instance.getNumber('Path Y', default_y)
            ph = nt_instance.getNumber('Path Heading', default_heading)

            lx = nt_instance.getNumber('Lookahead X', 3.5)
            ly = nt_instance.getNumber('Lookahead Y', default_y)

            dle = nt_instance.getNumber('Drive Left Encoder', 0)
            dlp = nt_instance.getNumber('Drive Left Pct', 0.0)
            dla = nt_instance.getNumber('Drive Left Amps', 0.0)

            dre = nt_instance.getNumber('Drive Right Encoder', 0)
            drp = nt_instance.getNumber('Drive Right Pct', 0.0)
            dra = nt_instance.getNumber('Drive Right Amps', 0.0)

            ee = nt_instance.getNumber('Elevator Encoder', 0)
            ep = nt_instance.getNumber('Elevator Pct', 0.0)
            ea = nt_instance.getNumber('Elevator Amps', 0.0)

            ae = nt_instance.getNumber('Arm Encoder', 0)
            ap = nt_instance.getNumber('Arm Pct', 0.0)
            aa = nt_instance.getNumber('Arm Amps', 0.0)

            ce = nt_instance.getNumber('Climb Encoder', 0)
            cp = nt_instance.getNumber('Climb Pct', 0.0)
            cam = nt_instance.getNumber('Climb Amps', 0.0)

            ic = nt_instance.getBoolean('Is Climbing', False)

            c = ''

            if NetworkTables.isConnected():
                c = 'Connected'
            else:
                c = 'Disconnected'

            e = nt_instance.getString('Is Enabled', 'Disabled')

            gd = nt_instance.getString('Game Data', 'None')

            if rx > 0.01 or ry > .01:
                robot_x_values.append(rx)
                robot_y_values.append(ry)
                robot_heading_values.append(rh)

            if px > 0.01 or py > .01:
                path_x_values.append(px)
                path_y_values.append(py)
                path_heading_values.append(ph)

            robot_point.set_data(np.array([rx, ry]))
            path_point.set_data(np.array([px, py]))
            lookahead_point.set_data(np.array([lx, ly]))

            robot_data = gen_robot_square((rx, ry), rh)

            robot.set_data([p[0] for p in robot_data], [p[1]
                                                        for p in robot_data])
            robot_path.set_data(robot_x_values, robot_y_values)
            path.set_data(path_x_values, path_y_values)

            return [robot_point, path_point, lookahead_point, robot, robot_path, path,
                    *update_text(rx, ry, rh, sp, ssa, ca, dle, dlp, dla, dre, drp, dra, ee, ep, ea, ae, ap, aa, ce, cp, cam, ic, c, e, gd)]

        def on_click(event):
            if event.ydata < -1.5:
                # Change Starting Position
                if event.xdata > 45 and event.xdata < 54 and event.ydata > -2.5:

                    current = nt_instance.getString(
                        'Starting Position', 'Left')
                    to_set = ''

                    if current == 'Left':
                        to_set = 'Center'
                        reset_arrays()
                    elif current == 'Center':
                        to_set = 'Right'
                        reset_arrays()
                    else:
                        to_set = 'Left'
                        reset_arrays()

                    nt_instance.putString('Starting Position', to_set)


                # Change Same Side Auto
                elif 45 < event.xdata < 54 and event.ydata > -3.5 and nt_instance.getString('Starting Position', 'Left') != 'Center':

                    current = nt_instance.getString(
                        'Near Scale Auto Mode', 'ThreeCube')

                    if current == 'ThreeCube':
                        to_set = 'Baseline'
                    else:
                        to_set = 'ThreeCube'
                 
                    nt_instance.putString('Near Scale Auto Mode', to_set)

                # Change Cross Auto
                elif 45 < event.xdata < 54 and event.ydata > -4.5 and nt_instance.getString('Starting Position', 'Left') != 'Center':

                    current = nt_instance.getString('Far Scale Auto Mode', 'ThreeCube')
                    to_set = ''

                    if current == 'ThreeCube':
                        to_set = 'Baseline'
                    else:
                        to_set = 'ThreeCube'

                    nt_instance.putString('Near Scale Auto Mode', to_set)

        draw_field(field_plot)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack()

        fig.canvas.mpl_connect('button_press_event', on_click)

        target_path, = field_plot.plot(
            path_x_values, path_y_values, color='red', alpha=0.5)
        actual_path, = field_plot.plot(
            robot_x_values, robot_y_values, color='black', alpha=0.25)

        path_point, = field_plot.plot(
            path_x_values[0], path_y_values[0], marker='o', markersize=2, color='green')
        robot_point, = field_plot.plot(
            robot_x_values[0], robot_y_values[0], marker='o', markersize=2, color='blue')
        lookahead_point, = field_plot.plot(lookahead_x_values[0], lookahead_y_values[0], marker='*', markersize=5,
                                           color='black')
        starting_robot = gen_robot_square(
            (robot_x_values[0], robot_y_values[0]), 0.0)
        robot, = field_plot.plot([p[0] for p in starting_robot], [
                                 p[1] for p in starting_robot], color='#690a0f')
        field_plot.set_ylim(bottom=-7.25, top=28.5)

        ani = animation.FuncAnimation(fig, update_plot, frames=20, interval=20,
                                      fargs=(
                                          robot_point, path_point, lookahead_point, robot, actual_path, target_path),
                                      blit=True)

        canvas.draw()


app = Main()
app.mainloop()
