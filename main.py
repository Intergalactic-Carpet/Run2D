from shapely.geometry import Polygon
from math import cos, sin, pi, radians, sqrt
from time import time, sleep
from queue import Queue
# from PIL import Image
import configparser
import keyboard
import pygame
import random
import playsound
import os

if playsound == 1:
    raise playsound.PlaysoundException

pygame.init()
screen_width, screen_height = 800, 600
screen_dim = screen_width, screen_height
screen = pygame.display.set_mode((screen_width, screen_height), pygame.HWSURFACE | pygame.DOUBLEBUF)
screen.fill((255, 255, 255))
screen_name = 'Run2D'
pygame.display.set_caption(screen_name)
# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHTGREY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GOLD = (212, 175, 55)
GREY = (100, 100, 100)
BG = (43, 43, 43)
# Main Variables
# ma
mouse_delta = 0
active_inputs = []
pressed = False
press_check = False
queue = Queue()
debug = False
sleep(0.1)
script_dir = os.path.dirname(os.path.abspath(__file__))
window_focused = True


class CreateGraph:
    """
    :param xcor: The bottom left x position of the graph
    :param ycor: The bottom left y position of the graph
    :param width: The width of the graph
    :param height: The height of the graph
    :param max_var_on_display: How many variables on display at a time (0 == infinity)
    :param initial_var: an initial number to start it off (not required)
    :param dot: Whether dots are displayed
    :param line: Whether graph lines are displayed
    :param side_increment: The vertical scale increment (may not work as intended)
    :param low_scale: The horizontal scale (doesn't look very good at the moment)
    :param side_scale: The vertical scale
    :param line_scale: The lines marking the left and bottom
    :param box_: Whether the graph is encased in a box
    :param max_points: How many points to be stored (erases old points if exceeded, 0 == infinity)
    :param last_point_bar: A line extending from the last point to the xcor
    :param last_point_bar_colour: Colour of the last point bar
    :param scale_colour: Colour of the scale
    :param line_colour: Colour of the line
    :param dot_colour: Colour of the dots
    :param all_point_bar: A line extending from each point to the xcor
    :param broken_graphics: A which when True, can make some interesting optical illusions
        (depending on point positions)
    :param fancy_graphics: Curvy lines (doesn't work as intended yet)
    :param max_high: The Maximum High
    """

    def __init__(self, xcor, ycor, width, height, max_var_on_display=0, initial_var=0, dot=False, line=True,
                 side_increment=10, low_scale=False, side_scale=True, line_scale=True, box_=False, max_points=200,
                 last_point_bar=False, last_point_bar_colour='midnightblue', scale_colour='black', line_colour='black',
                 dot_colour='black', all_point_bar=False, broken_graphics=False, fancy_graphics=False,
                 show_decimals_on_side=True, max_high=float('inf'), man_high=0, refuse_same=False):
        self.last_point_bar = last_point_bar
        self.show_decimal = show_decimals_on_side
        self.fancy_graphics = fancy_graphics
        self.broken = broken_graphics
        self.last_point_bar_colour = last_point_bar_colour
        self.all_point_bar = all_point_bar
        self.scale_colour = scale_colour
        self.line_colour = line_colour
        self.dot_colour = dot_colour
        self.max_high = max_high
        self.man_high = man_high
        if max_var_on_display == 0:
            max_var_on_display = float('inf')
        if height <= 15:
            height = 16
        self.line_scale = line_scale
        self.box = box_
        self.xcor = xcor
        self.ycor = ycor
        self.width = width
        self.height = height
        self.var = [initial_var]
        self.increment = width / len(self.var)
        self.high = 1
        self.low = 0
        self.v_distance = height / self.high
        self.new = True
        self.max_var = max_var_on_display
        self.display_var = self.var
        self.dot = dot
        self.line = line
        self.si = side_increment
        self.side_scale = side_scale
        self.lower_scale = low_scale
        if max_points < self.max_var:
            max_points = self.max_var
        self.max_points = max_points
        self.rs = refuse_same

    def update_data(self):
        self.v_distance = self.height / self.high
        if len(self.var) > self.max_var:
            count = 0
            self.display_var = []
            for _ in range(len(self.var)):
                if count >= len(self.var) - self.max_var:
                    temp_var = str(self.var[count])
                    self.display_var = self.display_var + [temp_var]
                count += 1
        else:
            self.display_var = self.var
        if self.max_var == float('inf'):
            self.increment = self.width / len(self.display_var)
        else:
            self.increment = self.width / self.max_var

    def update_graph(self, var):
        if self.max_var < 2:
            self.max_var = 2
        if self.max_points < 2:
            self.max_points = 2
        if float(var) > self.man_high != 0:
            var = self.high
        if len(self.var) == 1 and self.new:
            self.new = False
            self.var = [var]
        elif not (self.rs and str(self.var[-1]) == str(var)):
            self.var = self.var + [str(var)]
        if self.max_points < 10:
            self.max_points = 10
        if len(self.var) > self.max_points:
            v = []
            for _ in range(len(self.var)):
                if _ >= (len(self.var) - self.max_points):
                    v = v + [self.var[_]]
            self.var = v
        self.var = all_float(self.var)
        self.high, self.low = float(max(self.var)), float(min(self.var))
        if self.man_high != 0:
            self.high = self.man_high
        elif self.high > self.max_high:
            self.high = self.max_high
        if self.high == 0:
            self.high = 1
        self.v_distance = self.height / self.high

    def reset_graph(self):
        self.high = 1
        self.low = 1
        self.var = [0]
        self.display_var = self.var

    def draw_graph(self):
        self.update_data()
        if self.high * self.v_distance > self.height:
            self.v_distance -= 1
        if self.side_scale:
            scale = self.height / 16
            si = self.height / scale
            for _ in range(remove_decimal(scale)):
                text_ = round_to((self.high / scale) * (_ + 1))
                if len(self.var) > 50:
                    text_ = remove_decimal(round(float(text_)))
                if len(str(text_)) > 1:
                    if str(text_)[-1] == '0' and str(text_)[-2] == '.':
                        text_ = int(remove_decimal(text_))
                    else:
                        text_ = float(text_)
                else:
                    text_ = float(text_)
                text_ = f'{remove_decimal(text_)} - '
                if _ == 0 and self.low >= 0:
                    draw_text(self.xcor - 15, self.ycor - 4, '0 - ', 0.1)
                x = -5
                for i in range(len(text_)):
                    x += 5
                draw_text(self.xcor - x, self.ycor - si * _ * 1.02 - 20, text_, 0.1)
        for _ in range(len(self.display_var)):
            x = (self.increment * _) + 4 + self.xcor
            y = ((float(self.display_var[_]) / self.high) * -(self.height - 1)) + self.ycor - 1
            if _ == 0 and _ != len(self.display_var) - 1:
                draw_line(self.xcor, y, x, y)
            elif _ == len(self.display_var) - 1 or _ == len(self.display_var):
                gx = (self.increment * (_ - 1)) + 4 + self.xcor
                gy = ((float(self.display_var[_ - 1]) / self.high) * -(self.height - 1)) + self.ycor - 1
                draw_line(gx, gy, self.xcor + self.width - 2, y, colour=GREY)
            else:
                gx = (self.increment * (_ - 1)) + 4 + self.xcor
                gy = ((float(self.display_var[_ - 1]) / self.high) * -(self.height - 1)) + self.ycor - 1
                draw_line(gx, gy, x, y)
            if self.line_scale or self.box:
                draw_rect(self.xcor + self.width, self.ycor - self.height, 10, self.height, fill=True,
                          colour=(43, 43, 43))
                draw_rect(self.xcor, self.ycor - self.height, self.width, self.height, colour=LIGHTGREY)
            if self.dot:
                pass
            if self.last_point_bar and _ == len(self.display_var) - 1 or self.all_point_bar:
                pass


def all_float(in_):
    out_ = []
    for _ in range(len(in_)):
        try:
            out_ = out_ + [float(in_[_])]
        except ValueError:
            out_ = out_ + [0]
    return out_


def round_to(in_, decimal=1):
    in_ = str(in_)
    decimal_index = None
    out = ''
    for _ in range(len(in_)):
        if '.' in in_[_]:
            decimal_index = _
            out = out + in_[_]
        elif decimal_index is None:
            out = out + in_[_]
        elif _ <= decimal_index + decimal:
            out = out + in_[_]
    return out


def find_high_low(var):
    high = remove_decimal(var[0])
    low = remove_decimal(var[0])
    for _ in range(len(var)):
        z_ = remove_decimal(var[_])
        if z_ > high:
            high = z_
        elif z_ < low:
            low = z_
    return high, low


def remove_decimal(in_):
    in_ = str(in_)
    out_ = ''
    for _ in range(len(in_)):
        if '.' not in in_[_]:
            out_ = out_ + in_[_]
        else:
            break
    return int(out_)


def close_to(var, var2, thresh):
    re = False
    if thresh > (var - var2) > -thresh:
        re = True
    return re


def find_and_filter_out(in_, rejected):
    in_ = str(in_)
    out_ = ''
    for _ in range(len(in_)):
        if rejected not in in_[_]:
            out_ = out_ + in_[_]
    return out_


def round_10(round_):
    if round_ > 10 or round_ < -10:
        round_ = str(remove_decimal(round_))
        if int(round_[-1]) > 4:
            mid = str(int(round_[-2]) + 1)
        else:
            mid = str((round_[-2]))
        for _ in range(2):
            round_ = remove_text(round_, len(round_) - 1)
        round_ = float(str(round_) + mid + '0')
    elif 10 > round_ > 0:
        round_ = str(remove_decimal(round_))
        if int(round_[-1]) > 4:
            round_ = '10'
        else:
            round_ = '0'
    elif -10 < round_ < 0:
        round_ = str(remove_decimal(round_))
        if int(round_[-1]) > 4:
            round_ = '-10'
        else:
            round_ = '0'
    else:
        if round_ < 0:
            round_ = '-' + str(remove_decimal(round_))
        else:
            round_ = str(remove_decimal(round_))
    return round_


def remove_text(text_, point):
    output = ''
    for _ in range(len(text_)):
        if _ != point:
            output = output + text_[_]
    return output


def number_converter(num_input):
    """
    Removes all characters except numbers and periods
    :param num_input: String to convert
    :return: Number
    """
    num_input = str(num_input)
    num_len = len(num_input)
    allowed_chars = '1234567890.'
    chars_length = len(allowed_chars)
    index = 0
    output = ''
    for _ in range(num_len):
        indexed = num_input[index]
        index_2 = 0
        for i in range(chars_length):
            second_indexed = allowed_chars[index_2]
            if indexed in second_indexed:
                output = output + indexed
            index_2 += 1
        index += 1
    return output


def test_for(test, match):
    return str(match) in str(test)


def replace_index(string_or_list, replacement, index, is_list):
    in_ = string_or_list
    if is_list:
        out = []
        for _ in range(len(in_)):
            if _ == index:
                out = out + [replacement]
            else:
                out = out + [in_[_]]
    else:
        out = ''
        for _ in range(len(in_)):
            if _ == index:
                out = out + replacement
            else:
                out = out + in_[_]
    return out


def replace_instance(string_or_list, replacement, is_list, target):
    in_ = string_or_list
    if is_list:
        out = []
        for _ in range(len(in_)):
            out2 = ''
            for i in range(len(in_[_])):
                if target in in_[_][i]:
                    out2 = out2 + replacement
                else:
                    out2 = out2 + in_[_][i]
            out = out + [out2]
    else:
        out = ''
        for _ in range(len(in_)):
            if target in in_[_]:
                out = out + replacement
            else:
                out = out + in_[_]
    return out


def swap_chars(string_, rep_a, rep_b):
    out = ''
    for _ in range(len(string_)):
        if rep_a in string_[_]:
            out = out + rep_b
        elif rep_b in string_[_]:
            out = out + rep_a
        else:
            out = out + string_[_]
    return out


def text_filter(text_input, allowed_chars):
    """
    Removes all characters that aren't specified as allowed
    :param text_input: The text to be filtered
    :param allowed_chars: The characters allowed in the text
    :return: The filtered text
    """
    text_input = str.lower(str(text_input))
    text_length = len(text_input)
    chars_length = len(allowed_chars)
    index = 0
    output = ''
    for _ in range(text_length):
        indexed = text_input[index]
        index_2 = 0
        for i in range(chars_length):
            second_indexed = allowed_chars[index_2]
            if indexed in second_indexed:
                output = output + indexed
            index_2 += 1
        index += 1
    return output


def extract_decimal(in_):
    ints = ''
    dec_found = False
    dec_count = 2
    for _ in range(len(str(in_))):
        if str(in_)[_] == '.':
            dec_found = True
        elif not dec_found:
            ints = ints + str(in_)[_]
        else:
            dec_count += 1
    ints = int(ints)
    in_ = in_ - ints
    out_ = ''
    for _ in range(dec_count):
        out_ = out_ + str(in_)[_]
    return float(out_)


class Throttling:
    def __init__(self, retriever, sender=None, timing=1, start_=None):
        self.r = retriever
        self.s = sender
        self.t = timing
        self.n = time()
        self.store = start_

    def update(self):
        t = time() - self.n
        if t > self.t:
            d = self.r()
            if self.s is not None:
                self.s(d)
            self.store = d
            self.n = time()


class TargetController:
    """
    Slowly increase in speed towards the target before slowing down when reaching the target
    :param target: What to go to
    :param transition_time: How long to reach target
    """

    def __init__(self, target, transition_time=1.0):
        self.target = target
        self.transition_time = transition_time
        self.output = 0.0
        self.t = 0.0
        self.velocity = 0.0

    def change_target(self, target):
        self.target = remove_decimal(target)
        self.t = 0.0
        self.velocity = 0.0

    def update(self, elapsed_time):
        self.t += elapsed_time
        if self.t > self.transition_time:
            self.output = self.target
            self.velocity = 0.0
            return

        t = self.t / self.transition_time
        self.output = self.target * t + (1 - t) * self.output
        self.velocity = (self.target - self.output) / elapsed_time


class NumberAverager:
    def __init__(self, time_last, process_on_average=True):
        self.numbers = []
        self.t = time_last
        self.poa = process_on_average

    def add_number(self, num):
        self.numbers.append((num, time()))

    def get_average(self):
        if self.poa:
            self.remove_old_numbers()
        if not self.numbers:
            return 0
        return sum(num[0] for num in self.numbers) / len(self.numbers)

    def remove_old_numbers(self):
        now = time()
        self.numbers = [(num, timestamp) for (num, timestamp) in self.numbers if now - timestamp <= self.t]


def draw_lines(x, y, text_, center=False, size=20, bg_colour=BG, fill=False, font_colour=LIGHTGREY,
               padding=5, line_space=1.3, bg_transparency=0):
    line_space = min(line_space, 2)
    bg_transparency = max(0, min(1, bg_transparency))
    size = int(size)
    font = pygame.font.SysFont('Arial', size=size)
    oy = y
    ml = 0
    for line in text_:
        text = font.render(str(line), True, font_colour)
        text_rect = text.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.x = x
            text_rect.y = y
        # if fill:
        #     bg_surface = pygame.Surface(text.get_size())
        #     bg_surface.fill(bg_colour)
        #     # bg_surface.blit(text, (text_rect.x, text_rect.y))
        #     screen.blit(bg_surface, (text_rect.x, text_rect.y))
        # screen.blit(text, text_rect)
        # draw_circle(text_rect.x, text_rect.y + size, 2, fill=True)
        ml = ml if ml >= text.get_size()[0] else text.get_size()[0]
        # y += size * line_space

    s = pygame.Surface((ml + padding * 2, len(text_) * line_space * size + padding * 2), flags=pygame.SRCALPHA)
    s2 = pygame.Surface((ml + padding * 2, len(text_) * line_space * size + padding * 2), flags=pygame.SRCALPHA)
    if bg_transparency == 0 or bg_transparency == 1:
        s.set_alpha((1 - bg_transparency) * 255)

    if fill:
        # draw_rect(x - padding, oy - padding, ml + padding * 2, len(text_) * size * line_space + padding * 2,
        #           colour=bg_colour, fill=True)
        pygame.draw.rect(s if bg_transparency == 0 or bg_transparency == 1 else screen, bg_colour,
                         [x - padding, oy - padding, ml + padding * 2, len(text_) * size * line_space + padding * 2],
                         0 if fill else 1)
    # y = oy
    # for _ in range(len(text_)):
    #     if fill:
    #         draw_rect(x, y + size, ml, size * (line_space - 1), fill=True, colour=bg_colour)
    #         y += size * line_space

    y = oy
    for line in text_:
        text = font.render(str(line), True, font_colour)
        text_rect = text.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.x = x
            text_rect.y = y
        # if fill:
        #     bg_surface = pygame.Surface(text.get_size())
        #     bg_surface.fill(bg_colour)
        #     # bg_surface.blit(text, (text_rect.x, text_rect.y))
        #     screen.blit(bg_surface, (text_rect.x, text_rect.y))
        if bg_transparency == 0 or bg_transparency == 1:
            s2.blit(text, (text_rect.x, text_rect.y))
        else:
            screen.blit(text, (text_rect.x, text_rect.y))
        ml = ml if ml >= text.get_size()[0] else text.get_size()[0]
        y += size * line_space
    if bg_transparency == 0 or bg_transparency == 1:
        screen.blit(s, (x - padding, oy - padding))
        screen.blit(s2, (x - padding, oy - padding))


def draw_content(x, y, heading, body, text_length, center=False, heading_size=25, body_size=20, bg_colour=WHITE,
                 fill=False, font_colour=LIGHTGREY):
    size = int(heading_size)
    font = pygame.font.SysFont('Arial', size=size)
    text = font.render(str(heading), True, font_colour)
    text_rect = text.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.x = x
        text_rect.y = y
    if fill:
        bg_surface = pygame.Surface(text.get_size())
        bg_surface.fill(bg_colour)
        bg_surface.blit(text, (text_rect.x, text_rect.y))
        screen.blit(bg_surface, (text_rect.x, text_rect.y))
    screen.blit(text, text_rect)
    body = format_paragraph(body, text_length)
    y += heading_size * 1.3
    draw_lines(x, y, body, center, body_size, bg_colour, fill, font_colour)
    return text.get_size()


def draw_text(x, y, text='', center=False, size=20, bg_colour=WHITE, fill=False, font_colour=LIGHTGREY, display=None):
    size = int(size)
    font = pygame.font.SysFont('Arial', size=size)
    text = font.render(str(text), True, font_colour)
    text_rect = text.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.x = x
        text_rect.y = y
    if fill:
        bg_surface = pygame.Surface(text.get_size())
        bg_surface.fill(bg_colour)
        bg_surface.blit(text, (text_rect.x, text_rect.y))
        screen.blit(bg_surface, (text_rect.x, text_rect.y))
    if display is None:
        screen.blit(text, text_rect)
    else:
        display.blit(text, text_rect)
    return text.get_size()


def draw_line(start_x, start_y, end_x, end_y, colour=LIGHTGREY):
    pygame.draw.line(screen, colour, (start_x, start_y), (end_x, end_y))


def draw_rect(x, y, width, height, fill=False, colour=LIGHTGREY):
    if fill:
        border = 0
    else:
        border = 1
    pygame.draw.rect(screen, colour, (x, y, width, height), border)


def draw_circle(x: float, y: float, radius: float, fill=False, colour=BLACK):
    if fill:
        border = 0
    else:
        border = 1
    pygame.draw.circle(screen, colour, (x, y), radius, border)


def draw_arc(x, y, width, height, start_angle, end_angle, fill=False, colour=BLACK):
    if fill:
        border = 0
    else:
        border = 1
    pygame.draw.arc(screen, colour, (x, y, width, height), start_angle, end_angle, border)


def get_mouse():
    x, y = pygame.mouse.get_pos()
    return x, y


def active_inputs_on():
    on = False
    for _ in range(len(active_inputs)):
        if active_inputs[_].on:
            on = True
    return on


def if_pressed():
    global pressed
    pressed = pygame.mouse.get_pressed()[0] and not active_inputs_on()
    return pressed and not press_check


def draw_button(x, y, text, size=20, bg_colour=(43, 43, 43), font_colour=LIGHTGREY, center=False, fill=False,
                border=True, lock=False, cont_press=False, display=None):
    if lock:
        font_colour = GREY
    text = str(text)
    display = screen if display is None else display
    font = pygame.font.SysFont('Arial', size=size)
    tw, th = font.size(text)
    if center:
        x -= tw / 2
    if fill:
        # draw_rect(x - 3, y, tw + 7, th + 2, colour=(43, 43, 43), fill=True)
        pygame.draw.rect(display, bg_colour, [x - 3, y, tw + 7, th + 2])
    if border:
        # draw_rect(x - 3, y, tw + 7, th + 2, colour=font_colour, fill=False)
        pygame.draw.rect(display, font_colour, [x - 3, y, tw + 7, th + 2], width=1)
    draw_text(x, y, text, size=size, fill=False, bg_colour=bg_colour, font_colour=font_colour, display=display)
    # x -= 3
    tw += 6
    th += 2
    mx, my = get_mouse()
    if not cont_press:
        return x - 3 < mx < (x + tw + 6) and y - 3 < my < (y + size + 6) and if_pressed() and not lock
    else:
        return x - 3 < mx < (x + tw + 6) and y - 3 < my < (y + size + 6) and pygame.mouse.get_pressed()[0] and not lock


def is_pressing(x, y, width, height):
    mx, my = get_mouse()
    return x < mx < (x + width) and y < my < (y + height) and if_pressed()


def is_pressing_constantly(x, y, width, height):
    mx, my = get_mouse()
    return x < mx < (x + width) and y < my < (y + height) and pygame.mouse.get_pressed()[0]


def format_paragraph(paragraph, max_chars_per_line):
    words = paragraph.split()

    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars_per_line:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            while len(word) > max_chars_per_line:
                lines.append(word[:max_chars_per_line - 1] + "-")
                word = word[max_chars_per_line - 1:]
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    return lines


class CreateNotificationCenter:
    def __init__(self, x, y, size=20, time_last=5, default=None):
        self.x = x + 2
        self.y = y
        self.s = size
        self.tl = time_last
        self.notes = []
        self.w = 0
        self.types = ['click', 'time']
        self.default = default if default is not None else self.time()

    def click(self):
        return self.types[self.types.index('click')]

    def time(self):
        return self.types[self.types.index('time')]

    def find(self, title, changes=None, description=None):
        found = False
        index = None
        for _ in range(len(self.notes)):
            if str.lower(title) == str.lower(self.notes[_][0]):
                found = True
            if description is not None:
                if str.lower(description) == str.lower(self.notes[_][1]):
                    found = found and True
                else:
                    found = False
            if found:
                index = _
        if index is not None and changes is not None:
            for j in range(len(changes)):
                self.notes[index][changes[j][0]] = changes[j][1]
        self.get_width()
        return found

    def draw(self):
        self.remove()
        self.get_width()
        for _ in range(len(self.notes)):
            try:
                data = self.notes[_]
            except IndexError:
                data = self.notes[0]
            y = _ * (self.s * 2.7) + self.y
            draw_rect(self.x - 2, y, self.w + 4, self.s * 2.7 - 1, fill=True, colour=(43, 43, 43))
            draw_text(self.x, y, data[0], size=self.s)
            draw_text(self.x, y + self.s * 1.3, data[1], size=self.s / 1.5)
            draw_rect(self.x - 2, y, self.w + 4, self.s * 2.7 - 1)
            if data[5] == self.time():
                if time() - data[2] > 0.021:
                    draw_rect(self.x - 2, y + self.s * 2.2, ((time() - data[2]) / data[4]) * self.w + 4, self.s / 2 - 1,
                              fill=True, colour=LIGHTGREY)
            elif data[5] == self.click():
                draw_rect(self.x - 2, y + self.s * 2.2, self.w + 4, self.s / 2 - 1,
                          fill=True, colour=GREY)

                if is_pressing(self.x - 2, y + self.s * 2.2, self.w + 4, self.s / 2 - 1):
                    self.remove_spec(self.notes[_][0])

                draw_text(self.x + self.w / 2, y + self.s * 2.2 + (self.s / 4) - 1, 'Continue', center=True,
                          size=self.s / 2)

            draw_rect(self.x - 2, y + self.s * 2.2, self.w + 4, self.s / 2 - 1)

    def remove(self):
        n = []
        for _ in range(len(self.notes)):
            if self.notes[_][5] == self.time():
                if (time() - self.notes[_][2]) < self.notes[_][4]:
                    n.append(self.notes[_])
            else:
                n.append(self.notes[_])
        self.notes = n

    def remove_spec(self, name):
        n = []
        for _ in range(len(self.notes)):
            if self.notes[_][0] != name:
                n.append(self.notes[_])
        self.notes = n

    def get_width(self):
        if len(self.notes) > 0:
            widths = [draw_text(-1000, -1000, 'Continue', size=self.s / 2)[0] + 4]
            for _ in range(len(self.notes)):
                widths.append(self.notes[_][3])
            self.w = max(widths)

    def add(self, title, description, time_last=None, type_of=None):
        w1 = draw_text(-1000, -1000, title, size=self.s)[0]
        w2 = draw_text(-1000, -1000, description, size=self.s / 1.5)[0]
        if type_of is None:
            type_of = self.default
        try:
            type_of = self.types[self.types.index(type_of)]
        except ValueError:
            type_of = None
        if w1 > w2:
            w = w1
        else:
            w = w2
        if time_last is None:
            tl = self.tl
        else:
            tl = time_last
        if type_of not in self.types:
            notification.add('Notification Error',
                             f"'{title}' has unknown type '{type_of}'", type_of=self.click())
            type_of = self.default
        if not self.find(title, [(2, time())], description):
            self.notes.append([title, description, float(time()), w, tl, type_of])


class CreateScrollingText:
    def __init__(self, x, y, width, height, text, scroll_width=10, size=20):
        self.x = x
        self.y = y
        self.w = width
        self.sw = scroll_width
        self.s = size
        self.sc = 0
        self.h = height
        self.ot = text
        text_ = 'h'
        for _ in range(999):
            text_ = 'a' + text_
        tl = len(text_)
        tw = draw_text(-1000, -1000, text_, size=size)[0]
        if tw > width:
            while tw > width:
                t = format_paragraph(text_, tl)[0]
                if len(t) == 0:
                    t = format_paragraph(text_, tl)[1]
                tw = draw_text(-1000, -1000, t, size=size)[0]
                tl -= 1
        self.tl = tl
        texts = []
        for _ in range(len(text)):
            string_ = format_paragraph(text[_], tl)
            for j in range(len(string_)):
                texts.append(string_[j])
        self.t = texts
        self.p = False
        self.mp = 0

    def change_text(self, text):
        texts = []
        for _ in range(len(text)):
            if len(text[_]) > 1:
                string_ = format_paragraph(text[_], self.tl)
                for j in range(len(string_)):
                    texts.append(string_[j])
            else:
                texts.append(' ')
        self.t = texts

    def draw(self):
        draw_rect(self.x - 3, 0, self.w + 6, screen_height, colour=(43, 43, 43), fill=True)
        draw_lines(self.x, self.y - (self.s * 1.4 * len(self.t)) * self.sc, self.t, center=False)
        draw_rect(self.x - 3, self.h + self.y, self.w + 6 + self.sw, screen_height - self.y - self.h,
                  colour=(43, 43, 43), fill=True)
        draw_rect(self.x - 3, 0, self.w + 6, self.y, colour=(43, 43, 43), fill=True)
        draw_rect(self.x - 3, self.y, self.w + 6 + self.sw, self.h, colour=LIGHTGREY)
        if is_pressing_constantly(self.x, self.y, self.w + self.sw, self.h) or self.p:
            self.mp = get_mouse()[1]
            self.p = True
        else:
            self.mp += mouse_delta * 3
        sc = self.mp - 10
        if sc < self.y:
            sc = self.y
        elif sc > self.y + self.h:
            sc = self.y + self.h
        self.sc = (sc - self.y) / self.h
        if not pygame.mouse.get_pressed()[0]:
            self.p = False
        if self.sc > 0.94:
            sc = 0.945
        else:
            sc = self.sc
        draw_rect(self.x + self.w + 3, self.y + (self.h * sc) + 1, self.sw - 2, 20, fill=True, colour=GREY)


def list_true(bools):
    index = 0
    out = False
    for _ in range(len(bools)):
        if bools[_]:
            out = True
            index = _
    return out, index


class CreateMenu:
    def __init__(self, x, y, name='Menu', size=20):
        self.x = x
        self.y = y
        self.n = name
        self.b = []
        self.o = []
        self.s = size
        self.w = 1
        self.ws = []
        self.wn = draw_text(-1000, -1000, name, size=self.s)[0]
        self.open = True
        self.t = 0
        self.t2 = self.wn + 7
        self.h = 1

    def find(self, name):
        found = False
        index = 0
        for _ in range(len(self.b)):
            if name == self.b[_][0]:
                found = True
                index = _
        return found, index

    def add(self, name):
        if self.find(name)[0]:
            self.remove(name)
        self.b.append((name, str.lower(name)))
        self.ws.append(draw_text(-1000, -1000, name, size=int(round(self.s * 0.75)))[0])
        self.o.append(False)
        self.get_width()
        pygame.mouse.get_rel()

    def remove(self, name):
        n = []
        for _ in range(len(self.b)):
            if name not in self.b[_]:
                n.append(self.b[_])
        self.b = n

    def get_width(self):
        if len(self.ws) > 0:
            self.w = max(self.ws + [self.wn]) + 6

    def replace(self, replaced, replacer):
        found, _ = self.find(replaced)
        if found:
            self.ws[_] = draw_text(-1000, -1000, replacer, size=int(round(self.s * 0.75)))[0]
            self.b[_] = (str.title(replacer), str.lower(replacer))
            self.get_width()
        else:
            notification.add('Menu Failure', f'{self.n} Failed to Replace Button',
                             type_of=notification.click())

    def draw(self):
        self.get_width()
        x = self.x
        y = self.y
        s = int(round(self.s * 0.75))
        self.h = 4 * self.t + 1 + self.s * self.t * (len(self.b) + 1)
        draw_rect(x - 3, y, self.w, 4 * self.t + 1 + self.s * self.t * (len(self.b) + 1), colour=(43, 43, 43),
                  fill=True)
        y += 4 * self.t + 1
        if self.t > 0.01 and self.t2 > self.w - 1:
            for _ in range(len(self.b)):
                y += (self.s - 2) * self.t
                draw_rect(x - 2, y, self.w, self.s + 3, colour=(43, 43, 43), fill=True)
                if self.o[_]:
                    colour = GOLD
                else:
                    colour = LIGHTGREY
                draw_button(x, y, self.b[_][0], size=s, bg_colour=(43, 43, 43), fill=True, border=False,
                            font_colour=colour)
                if is_pressing(x - 2, y, self.w + 4, s) and self.t > 0.99:
                    self.o[_] = not self.o[_]
                if _ + 1 == len(self.b):
                    add = -1
                else:
                    add = 3
                draw_rect(x - 3, y, self.w, self.s + add, colour=LIGHTGREY)
        if self.open and self.t2 > self.w - 1:
            self.t -= (self.t - 1) / 5
        else:
            self.t -= self.t / 5
        if self.t > 0.01 or self.open:
            self.t2 -= (self.t2 - self.w) / 4
        else:
            self.t2 -= (self.t2 - (self.wn + 7)) / 5
        x = self.x
        y = self.y
        draw_rect(x - 2, y, self.w, self.s + 3, colour=(43, 43, 43), fill=True)
        if draw_button(x, y, self.n, size=self.s, fill=False, border=False):
            self.open = not self.open
        if self.t > 0.01 and self.t2 > self.w - 1:
            draw_rect(self.x - 3, self.y, self.w, self.s + 3, colour=LIGHTGREY)
        else:
            draw_rect(x - 3, y, self.t2, self.s + 3, colour=LIGHTGREY)
        return self.o


class CreateScreenMenu:
    def __init__(self, x, y, default, name='Menu', size=20, reset_if_duplicate=False, replace_key='home'):
        self.x = x
        self.y = y
        self.n = name
        self.b = []
        self.bn = []
        self.o = []
        self.s = size
        self.w = 1
        self.ws = []
        self.wn = draw_text(-1000, -1000, name, size=self.s)[0]
        self.open = False
        self.t = 0
        self.t2 = self.wn + 7
        self.h = 1
        self.output = default
        self.rid = reset_if_duplicate
        self.rk = replace_key

    def find(self, name):
        found = False
        index = 0
        for _ in range(len(self.b)):
            if name == self.b[_][0]:
                found = True
                index = _
        return found, index

    def add(self, name):
        if self.find(name)[0]:
            self.remove(name)
        self.b.append((name, str.lower(name)))
        self.bn.append(name)
        self.ws.append(draw_text(-1000, -1000, name, size=int(round(self.s * 0.75)))[0])
        self.o.append(False)
        self.get_width()

    def find_multiple(self):
        found = False
        for _ in range(len(self.b)):
            for j in range(len(self.b)):
                if _ != j and str.lower(self.b[_][0]) == str.lower(self.b[j][0]):
                    notification.add('Menu Error', 'Menu Duplicate found, reset menu',
                                     type_of=notification.click())
                    self.output = self.rk
                    self.b = []
                    self.ws = []
                    self.o = []
                    for i in range(len(self.bn)):
                        self.add(self.bn[i])
        return found

    def remove(self, name):
        self.find_multiple()
        n = []
        nb = []
        for _ in range(len(self.b)):
            if name not in self.b[_]:
                n.append(self.b[_])
                nb.append(self.b[_][0])
        self.b = n
        self.bn = nb

    def get_width(self):
        if len(self.ws) > 0:
            self.w = max(self.ws + [self.wn]) + 6

    def replace(self, replaced, replacer):
        found, _ = self.find(replaced)
        if found:
            self.ws[_] = draw_text(-1000, -1000, replacer, size=int(round(self.s * 0.75)))[0]
            self.b[_] = (str.title(replacer), str.lower(replacer))
            self.get_width()
        else:
            notification.add('Menu Failure', f'{self.n} Failed to Replace Button',
                             type_of=notification.click())

    def draw(self):
        self.find_multiple()
        self.get_width()
        x = self.x
        y = self.y
        s = int(round(self.s * 0.75))
        self.h = 4 * self.t + 1 + self.s * self.t * (len(self.b) + 1)
        draw_rect(x - 3, y, self.w, 4 * self.t + 1 + self.s * self.t * (len(self.b) + 1), colour=(43, 43, 43),
                  fill=True)
        self.o = []
        y += 4 * self.t + 1
        if self.t > 0.01 and self.t2 > self.w - 1:
            for _ in range(len(self.b)):
                y += (self.s - 2) * self.t
                draw_rect(x - 2, y, self.w, self.s + 3, colour=(43, 43, 43), fill=True)
                self.o.append(draw_button(x, y, self.b[_][0], size=s, bg_colour=(43, 43, 43), fill=True, border=False)
                              and self.t > 0.99)
                if _ + 1 == len(self.b):
                    add = -1
                else:
                    add = 3
                draw_rect(x - 3, y, self.w, self.s + add, colour=LIGHTGREY)
        else:
            for _ in range(len(self.b)):
                self.o.append(False)
        if self.open and self.t2 > self.w - 1:
            self.t -= (self.t - 1) / 5
        else:
            self.t -= self.t / 5
        if self.t > 0.01 or self.open:
            self.t2 -= (self.t2 - self.w) / 4
        else:
            self.t2 -= (self.t2 - (self.wn + 7)) / 5
        x = self.x
        y = self.y
        draw_rect(x - 2, y, self.w, self.s + 3, colour=(43, 43, 43), fill=True)
        if draw_button(x, y, self.n, size=self.s, fill=False, border=False):
            self.open = not self.open
        if self.t > 0.01 and self.t2 > self.w - 1:
            draw_rect(self.x - 3, self.y, self.w, self.s + 3, colour=LIGHTGREY)
        else:
            draw_rect(x - 3, y, self.t2, self.s + 3, colour=LIGHTGREY)
        if list_true(self.o)[0]:
            self.open = False
            alias_n = self.b[list_true(self.o)[1]][1]
            self.replace(str.title(self.b[list_true(self.o)[1]][1]), str.title(self.output))
            self.output = alias_n
        return self.o


class DefineActiveInput:
    def __init__(self, x, y, title, type_, start, size=20, reset_on_click=False, allow=None, allow_none=False):
        self.x = x
        self.y = y
        self.s = size
        self.n = title
        self.i = start
        self.o = start
        self.on = False
        self.t = type_
        self.roc = reset_on_click
        self.al = allow
        self.aln = allow_none
        self.lock = False
        self.error = False
        active_inputs.append(self)

    def update(self, draw=True):
        if not window_focused:
            self.on = False
        error = True
        temp = ''
        if self.on and self.lock:
            self.on = False
        if self.t == 'int':
            try:
                if not self.on:
                    self.o = float(self.i)
                temp = float(self.i)
                error = False
            except ValueError:
                error = True
        elif self.t == 'str':
            try:
                temp = str(self.i)
                found = False
                if self.al is not None:
                    temp2 = text_filter(temp, self.al)
                    found = temp2 != temp
                    # draw_lines(get_mouse()[0] + 25, get_mouse()[1], (temp, temp2, self.al, self.o))
                    temp = temp2
                error = False
                if (not self.aln and len(temp) == 0 or found) and self.al is not None:
                    error = True
                if not self.on and not error and not found:
                    self.o = temp
            except ValueError:
                error = True
        elif self.t == 'bool':
            self.i = str.lower(str(self.i))
            if ('true' in self.i and len(self.i) == 4) or ('false' in self.i and len(self.i) == 5):
                error = False
                self.i = str.title(self.i)
                if not self.on:
                    self.o = bool(self.i)
        elif self.t == 'key':
            try:
                self.i = str.title(str(self.i))
                temp = keyboard.is_pressed(str(self.i)) and window_focused
                if not self.on:
                    self.o = str(self.i)
                error = False
            except ValueError:
                error = True
        if self.on and not error:
            colour = (178, 230, 170)
        elif error:
            if self.on:
                colour = (230, 154, 154)
            else:
                colour = (237, 57, 57)
                notification.add(f'{self.n} Invalid', f"{self.n}'s input is invalid")
        else:
            colour = LIGHTGREY
        if temp == float('inf'):
            pass
        if draw:
            if draw_button(self.x, self.y, f'{self.n}: {self.i}', size=self.s, font_colour=colour):
                if self.roc:
                    self.i = ''
                self.on = not self.on
        if keyboard.is_pressed('alt') and self.on and window_focused:
            if self.t == 'int':
                self.i = remove_decimal(self.o)
            else:
                self.i = self.o
            self.on = False
        self.error = error


def on_press_callback(event):
    if event.event_type == 'down' and window_focused:
        key = str.lower(str(event.name))
        for _ in range(len(active_inputs)):
            if active_inputs[_].on:
                keys = str(active_inputs[_].i)
                if key == 'backspace':
                    keys = keys[:-1]
                elif key == 'space':
                    keys = keys + ' '
                elif key == 'enter':
                    active_inputs[_].on = False
                elif len(key) > 1:
                    pass
                else:
                    if keyboard.is_pressed('shift'):
                        if len(key) == 1:
                            keys = keys + str.upper(key[-1])
                    else:
                        keys = keys + str.lower(key)
                active_inputs[_].i = keys


def add_line_to_txt(path, newline):
    with open(path, 'r') as f:
        lines = f.readlines()
        f.close()
    if len(lines) > 0:
        lines[-1] = lines[-1] + '\n'
    lines.append(newline)
    with open(path, 'w') as f:
        f.writelines(lines)
        f.close()


def rotate_point(point, center, angle_degrees):
    angle_radians = radians(angle_degrees)
    x, y = point
    cx, cy = center

    dx = x - cx
    dy = y - cy

    new_x = dx * cos(angle_radians) - dy * sin(angle_radians)
    new_y = dx * sin(angle_radians) + dy * cos(angle_radians)

    return new_x + cx, new_y + cy


def rotate_polygon(polygon, center, angle_degrees):
    return [rotate_point(point, center, angle_degrees) for point in polygon]


def circle_to_polygon(radius, num_points=360):
    polygon = []
    angle_increment = 2 * pi / num_points

    for i in range(num_points):
        angle = i * angle_increment
        x = radius * cos(angle)
        y = radius * sin(angle)
        polygon.append((x, y))

    return polygon


def oval_to_polygon(horizontal_radius, vertical_radius, num_points=360):
    polygon = []
    angle_increment = 2 * pi / num_points

    for i in range(num_points):
        angle = i * angle_increment
        x = horizontal_radius * cos(angle)
        y = vertical_radius * sin(angle)
        polygon.append((x, y))

    return polygon


def hollow_oval_to_polygon(outer_horizontal_radius, outer_vertical_radius, num_points=360):
    ih = outer_horizontal_radius - 5
    iv = outer_vertical_radius - 5
    poly = []
    angle_increment = 2 * pi / num_points

    for i in range(num_points):
        angle = i * angle_increment
        outer_x = outer_horizontal_radius * cos(angle)
        outer_y = outer_vertical_radius * sin(angle)
        poly.append((outer_x, outer_y))

    for i in range(num_points):
        angle = i * angle_increment
        inner_x = ih * cos(angle)
        inner_y = iv * sin(angle)
        poly.append((inner_x, inner_y))

    return poly


def draw_polygon(x, y, poly, fill=False, colour=LIGHTGREY, rotation=0, rot_center=(0, 0)):
    poly = rotate_polygon(poly, rot_center, rotation)
    poly = [(x + x2, y + y2) for x2, y2 in poly]
    fill = 0 if fill else 1
    pygame.draw.polygon(screen, colour, poly, fill)


# Screen Stuff ^
high_score = 1
total = 0
score = 0
games = 1
difficulty = 2
pname = None
is_admin = False
playtime = 0

throttle = 'w'
turn_left = 'a'
turn_right = 'd'
brake = 's'
pause_key = 'esc'


# Game Variables ^


def thruster_vector(angle, total_thrust):
    rad = radians(angle)
    x_velocity = round(total_thrust * sin(rad), 2)
    y_velocity = round(total_thrust * cos(rad), 2)
    return x_velocity, y_velocity


class Obstacles:
    def __init__(self, poly, step, max_level, difficulty_):
        self.obs = []
        self.min_y = 0
        self.max_y = screen_height
        self.min_x = screen_width / 4
        self.max_x = self.min_x * 3
        self.max_level = max_level
        self.poly = poly
        self.step = step
        self.obs_size = 25 if not difficulty else 30
        self.difficulty = difficulty_

    def add_ob(self, level=None):
        if level is None:
            level = random.randint(0, self.max_level * 100) / 100
        if level > self.max_level:
            level = self.max_level
        if level < 0:
            level = 0
        ran = (self.max_x - self.min_x) * 100
        x = self.min_x + random.randint(0, round(ran)) / 100
        poly = [(x + px, self.min_y - level + py) for px, py in self.poly]
        self.obs.append({'x': x, 'y': self.min_y - level, 'raw_poly': self.poly, 'poly': poly, 'exists': True,
                         'xv': 0, 'yv': 0, 'cont': True, 'size': self.obs_size, 'hp': 1, 'ticks': 0,
                         'obs_size': self.obs_size})

    def update(self, replace=True, x=0, speed=1):
        obs = []
        draw_line(self.min_x - self.obs_size - 2, self.max_y, self.min_x - self.obs_size - 2, self.min_y)
        draw_line(self.max_x + self.obs_size + 2, self.max_y, self.max_x + self.obs_size + 2, self.min_y)
        for _ in range(len(self.obs)):
            self.obs[_]['y'] += self.step + self.obs[_]['yv'] * speed
            self.obs[_]['x'] += self.obs[_]['xv'] * speed
            # if not self.obs[_]['cont']:
            self.obs[_]['xv'] -= (self.obs[_]['xv'] - self.obs[_]['xv'] * 0.999) * speed
            self.obs[_]['yv'] -= (self.obs[_]['yv'] - self.obs[_]['yv'] * 0.999) * speed
            if self.obs[_]['x'] < self.min_x - 20:
                if self.obs[_]['xv'] < 0:
                    self.obs[_]['xv'] = -self.obs[_]['xv']
            if self.obs[_]['x'] > self.max_x + 15:
                if self.obs[_]['xv'] > 0:
                    self.obs[_]['xv'] = -self.obs[_]['xv']
            if self.obs[_]['y'] > self.max_y * 2 or self.obs[_]['size'] <= 0.1:
                obs.append(_)

            self.obs[_]['size'] = self.obs[_]['obs_size'] * self.obs[_]['hp']
            self.obs[_]['raw_poly'] = circle_to_polygon(self.obs[_]['size'],
                                                        round(20 * (self.obs[_]['obs_size'] / self.obs_size)))
            self.obs[_]['poly'] = [(self.obs[_]["x"] + px, self.obs[_]["y"] + py) for px, py in self.obs[_]['raw_poly']]
            self.obs[_]['ticks'] += 1 * speed
            if self.obs[_]['ticks'] > 3600 / difficulty * 2:
                # self.obs[_]['obs_size'] += 0.1 * self.difficulty / 2
                self.obs[_]['yv'] += max(min(screen_height / 2 - self.obs[_]['y'], 0.1), -0.1)
                self.obs[_]['xv'] += max(min(x + screen_width / 2 - self.obs[_]['x'], 0.1), -0.1)

        for ob in obs:
            # print(self.obs[ob]['size'])
            try:
                if self.obs[ob]['y'] > self.max_y * 2 or self.obs[ob]['size'] <= 0.1:
                    self.obs[ob]['exists'] = False
                    if replace:
                        self.add_ob()
                    del self.obs[ob]
            except IndexError:
                pass
        # print(self.obs)


def find_closest_coordinate(target, coordinates):
    closest_coordinate = None
    closest_distance = None

    for coord in coordinates:
        dist = distance(target, coord)
        if closest_distance is None or dist < closest_distance:
            closest_coordinate = coord
            closest_distance = dist

    return [closest_coordinate[0], closest_coordinate[1]]


def distance(coord1, coord2):
    return sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


def polarity(a):
    try:
        b = a
        if b < 0:
            b = -b
        return a / b
    except ZeroDivisionError:
        return 0


def xor(a, b):
    return (a or b) and not (a and b)


class Screen:
    def __init__(self, size=(screen_width, screen_height), flags=0, depth=0):
        self.screen = pygame.Surface(size=size, flags=flags, depth=depth)


def game():
    global high_score, total, score, pressed, press_check, games, playtime, window_focused
    clock = pygame.time.Clock()
    rot = 0
    velocity = 0
    max_speed = 5
    min_speed = -3.5
    poly = circle_to_polygon(25, 20)
    osp = velocity
    poly = [(x + 25, y) for x, y in poly]
    obs = Obstacles(poly, velocity, screen_height, difficulty)
    mo = 15 * difficulty / 2
    x = 0
    turn = 0
    wp = []
    hp = 100
    prog = 0
    dw = 0
    dmg_cool_pre = 0.05
    dmg_cool = 0
    hp_reg = 1
    player_engaged = 0
    ple = 1.15
    fps_pre = NumberAverager(2)
    ldp = Polygon([(0, 0), (obs.min_x - 37, 0), (obs.min_x - 37, screen_height), (0, screen_height)])
    rdp = Polygon(
        [(obs.max_x + 37, 0), (screen_width, 0), (screen_width, screen_height), (obs.max_x + 37, screen_height)])
    co = (150, 150, 150)
    car = ImageLoader()
    car.load_file(None)
    obstacle = ImageLoader()
    obstacle.load_file(None)
    pause = False
    pause_level = 0
    game_speed = 0
    leave = False
    start_time = time()
    pause_cooldown = time()
    play_level = 100
    while True:
        speed = velocity * polarity(velocity)
        if dw <= 0.1:
            hp += min(100 - hp, 1 / hp_reg) * game_speed
            hp_reg += max(10 - hp_reg, -0.01) * game_speed
        else:
            hp_reg = 1000
        if pressed:
            if not press_check:
                pressed = True
                press_check = True
            else:
                pressed = False
        else:
            pressed = False
            press_check = False
        screen.fill(BG)

        dp = [(-25, -45), (25, -45), (25, 45), (-25, 45)]
        dp = rotate_polygon(dp, (0, 45), rot)
        dp = [(px + screen_width / 2 + x, py + screen_height / 2) for px, py in dp]

        draw_rect(obs.min_x - 37, obs.min_y, 10, screen_height, colour=GREY, fill=True)
        draw_rect(obs.max_x + 27, obs.min_y, 10, screen_height, colour=GREY, fill=True)
        draw_rect(0, obs.min_y, obs.min_x - 37, screen_height, fill=True, colour=co)
        draw_rect(obs.max_x + 37, obs.min_y, screen_width - obs.max_x, screen_height, fill=True, colour=co)
        if (Polygon(dp).intersects(ldp) or Polygon(dp).intersects(rdp) or
                not (obs.max_x + 35 > x + screen_width / 2 > obs.min_x - 35)):
            hp -= (min(0.1, hp) * difficulty / 2 if speed > 0.5 else 0) * game_speed
            dw = 10

        fps_pre.add_number(clock.get_fps())
        fps = fps_pre.get_average()
        if fps == 0:
            fps = 1
        # start
        prog += obs.step
        score = prog / 30 + hp * 2
        if score >= high_score:
            high_score = score
        es = velocity

        if max_speed / 2 > es > min_speed / 2:
            if not -1 < es < 1:
                es = max_speed / 2 * polarity(es)
            else:
                es = velocity * 2
        rot -= (turn * es / 5) * game_speed
        plc = False
        if hp > 0:
            if keyboard.is_pressed(turn_left) and window_focused and not pause:
                turn += 0.1
                plc = True
            if keyboard.is_pressed(turn_right) and window_focused and not pause:
                turn -= 0.1
                plc = True
            turn = turn * 0.93
            while rot > 360:
                rot -= 360
            if keyboard.is_pressed(brake) and window_focused and not pause:
                plc = True
                if velocity > 1:
                    velocity -= velocity / fps * 3
                else:
                    velocity -= (velocity - min_speed) / 3 / fps
            elif keyboard.is_pressed(throttle) and window_focused and not pause:
                plc = True
                velocity -= (velocity - max_speed) / 3 / fps
            else:
                velocity -= (velocity / 16 / fps) * game_speed
            if player_engaged < ple:
                velocity -= (velocity - max_speed) / fps
        else:
            velocity -= velocity / fps * 3
            pause = False
        # if plc and ple + 2 / 60 > player_engaged > ple:
        #     for _ in range(mo):
        #         obs.add_ob()
        if plc:
            player_engaged += 1 / 60
        elif player_engaged < ple:
            player_engaged -= player_engaged / 60
        acceleration = velocity - osp
        osp = velocity
        x2, y = thruster_vector(rot, velocity)
        y = y * game_speed
        x += x2 * game_speed
        if player_engaged > ple:
            obs.step = y
        obs.update(False, x, game_speed)
        if player_engaged > ple:
            while len(obs.obs) < mo:
                obs.add_ob()
        poly = rotate_polygon([(-25, -50), (0, -45), (25, -50), (25, 50), (-25, 50)], (0, 45), rot)
        # trails
        if (xor(keyboard.is_pressed(turn_left) and window_focused,
                keyboard.is_pressed(turn_right) and window_focused)
                and velocity > max_speed / 2 and hp > 0 and (turn * polarity(turn)) > 1.15):
            if obs.max_x + 35 > dp[0][0] > obs.min_x - 35:
                wp.append({'pos': [dp[0][0], dp[0][1]],
                           'time': time(),
                           'poly': [(2.5, -5), (2.5, 5), (-5, 5), (-5, -5)],
                           'rot': rot - turn * 10,
                           'dif': [0, 255, 0],
                           'fade': False})
            if obs.max_x + 35 > dp[1][0] > obs.min_x - 35:
                wp.append({'pos': [dp[1][0], dp[1][1]],
                           'time': time(),
                           'poly': [(-2.5, -5), (-2.5, 5), (5, 5), (5, -5)],
                           'rot': rot - turn * 10,
                           'dif': [0, 255, 0],
                           'fade': False})

        if ((acceleration > 0.015 or acceleration < -0.015) and
                (keyboard.is_pressed(throttle) or keyboard.is_pressed(brake)) and window_focused):
            if obs.max_x + 35 > dp[2][0] > obs.min_x - 35:
                wp.append({'pos': [dp[2][0], dp[2][1]],
                           'time': time(),
                           'poly': [(-2.5, -5), (-2.5, 5), (5, 5), (5, -5)],
                           'rot': rot - turn * 10,
                           'dif': [0, 255, 0],
                           'fade': False})
            if obs.max_x + 35 > dp[3][0] > obs.min_x - 35:
                wp.append({'pos': [dp[3][0], dp[3][1]],
                           'time': time(),
                           'poly': [(2.5, -5), (2.5, 5), (-5, 5), (-5, -5)],
                           'rot': rot - turn * 10,
                           'dif': [0, 0, 0],
                           'fade': False})
        dele = []
        # print(len(wp))
        for _ in range(len(wp)):
            # c = wp[_]['dif']
            # if len(wp) > 1000 and not wp[_]['fade']:
            #     dif = 1
            # else:
            #     dif = 0
            # c[1] -= dif
            # if c[1] != -1:
            #     c[0] += dif
            # else:
            #     c[0] -= dif * 2
            # if c[1] < 0:
            #     c[1] = 0
            # if c[0] < 0:
            #     c[0] = 0
            # if c[0] > 255:
            #     c[0] = 255
            # wp[_]['dif'] = c
            # if c[0] <= 0 and c[1] <= 0 and c[2] <= 0 or wp[_]['fade']:
            #     wp[_]['fade'] = True
            #     c[0] += min(BG[0] - c[0], 0.1)
            #     c[1] += min(BG[1] - c[1], 0.1)
            #     c[2] += min(BG[2] - c[2], 0.1)
            # c = tuple(c)
            cp = max(0, min(BG[0], (len(wp) - _) / 30))
            c = (cp, cp, cp)
            if close_to(c[0], BG[0], 1):
                dele.append(_)
            wp[_]['pos'][1] += y
            draw_polygon(wp[_]['pos'][0], wp[_]['pos'][1], wp[_]['poly'], colour=c, rotation=wp[_]['rot'], fill=False)
        for d in dele:
            try:
                del wp[d]
            except IndexError:
                pass
        # draw + calc
        for _ in range(len(obs.obs)):
            # obs.obs[_]['poly'] = circle_to_polygon(obs.obs[_]['size'], 20)
            # obs.obs[_]['poly'] = [(x + obs.obs[_]['x'], y + obs.obs[_]['y']) for x, y in obs.obs[_]['poly']]
            if obstacle.img_data is None:
                draw_polygon(0, 0, obs.obs[_]['poly'], fill=True, colour=GOLD)
            else:
                scale = 1
                for y in range(len(obstacle.img_data)):
                    for x in range(len(obstacle.img_data[y])):
                        col = obstacle.img_data[y][x]
                        if col[3] > 0:
                            draw_rect(x * scale, y * scale, scale, scale, True, col)

            if Polygon(dp).intersects(Polygon(obs.obs[_]['poly'])):
                # velocity = -velocity * 10
                haj = 0
                if velocity > 0:
                    mult = velocity / max_speed
                else:
                    mult = -velocity / (min_speed * polarity(min_speed))
                if obs.obs[_]['cont']:
                    if dmg_cool == 0:
                        haj += 5 * mult
                        dmg_cool = dmg_cool_pre
                        dw = 10
                    sp = y * polarity(y)
                    spo = obs.obs[_]['yv'] * polarity(obs.obs[_]['yv'])
                    obs.obs[_]['cont'] = False
                    obs.obs[_]['xv'] += x2
                    if spo < sp and obs.obs[_]['y'] \
                            < find_closest_coordinate((0, 0), [(dp[0][1], 0), (dp[1][1], 0)])[0]:
                        obs.obs[_]['yv'] -= obs.step
                    velocity = velocity * 0.75
                elif dmg_cool == 0:
                    dmg_cool = dmg_cool_pre * 0.5
                    haj += 1 * mult
                    dw = 10
                hp -= obs.obs[_]['hp'] * haj / 2 * difficulty
                obs.obs[_]['hp'] -= min(haj, 0.2)
                if obs.obs[_]['hp'] < 0:
                    obs.obs[_]['hp'] = 0
        draw_polygon(dp[0][0], dp[0][1], [(2.5, -5), (2.5, 5), (-5, 5), (-5, -5)], rotation=rot - turn * 10, fill=True,
                     colour=GREY)
        draw_polygon(dp[1][0], dp[1][1], [(-2.5, -5), (-2.5, 5), (5, 5), (5, -5)], rotation=rot - turn * 10, fill=True,
                     colour=GREY)

        dw -= dw / 250
        draw_polygon(dp[2][0], dp[2][1], [(-2.5, -5), (-2.5, 5), (5, 5), (5, -5)], rotation=rot, fill=True, colour=GREY)
        draw_polygon(dp[3][0], dp[3][1], [(2.5, -5), (2.5, 5), (-5, 5), (-5, -5)], rotation=rot, fill=True, colour=GREY)
        if car.img_data is None:
            draw_polygon(screen_width / 2 + x, screen_height / 2, poly, fill=True,
                         colour=(max(LIGHTGREY[0], dw / 10 * 255), LIGHTGREY[1], LIGHTGREY[2]))
            draw_polygon(screen_width / 2 + x, screen_height / 2, poly, fill=False, colour=(dw / 10 * 255, 0, 0))
        else:
            scale = 3
            c_pos = (x + screen_width / 2 - car.img.size[0] / 2 * scale,
                     screen_height / 2 - car.img.size[1] / 2 * scale)
            img_surf = pygame.Surface((car.img.size[0] * scale, car.img.size[1] * scale), pygame.SRCALPHA)
            for y2 in range(len(car.img_data)):
                for x2 in range(len(car.img_data[y2])):
                    col = car.img_data[y2][x2]
                    if col[3] > 0:
                        # draw_rect(x2 * scale + c_pos[0], y2 * scale + c_pos[1], scale, scale, True, col)
                        pygame.draw.rect(img_surf, col,
                                         [x2 * scale, y2 * scale, scale, scale])
            img_surf = pygame.transform.rotate(img_surf, -rot)
            screen.blit(img_surf, c_pos)
        # other
        dmg_cool -= min(dmg_cool, 0.1 / fps) * game_speed
        if (draw_button(screen_width - 100, 5, 'Pause', fill=True, bg_colour=BG) or
                (time() - pause_cooldown > 1 and keyboard.is_pressed(pause_key))):
            pause_cooldown = time()
            pause = True
        draw_lines(5, 5, [f'{round(speed / max_speed * 60)} Km/h',
                          f'HP: {max(round(hp, 2), 0)}%',
                          f'Score: {round(score)}',
                          f'High Score: {round(high_score)}',
                          f'Progress: {round(prog / 50, 1)}m'],
                   bg_colour=((BG[0] + co[0]) / 2, (BG[1] + co[1]) / 2, (BG[2] + co[2]) / 2),
                   fill=True, bg_transparency=0.5)

        s = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        s.set_alpha(max(1 - player_engaged, 0) * 255)
        draw_text(screen_width / 2, screen_width / 4, 'Hold W to start', center=True, display=s)
        screen.blit(s, (0, 0))

        s = pygame.Surface((screen_width, screen_height))
        s.set_alpha(pause_level * 100)
        s.fill(BLACK)
        screen.blit(s, (0, 0))
        pause_level += ((1 if pause else 0) - pause_level) / 30
        game_speed = 1 - pause_level
        draw_text(5, screen_height - 25, f'{round(fps, 1)} FPS')

        if pause or game_speed < 0.99:
            s = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            s.set_alpha(pause_level * 255)
            pygame.draw.rect(s, BG, [screen_width / 3, screen_height / 3, screen_width / 3, screen_height / 3])
            draw_text(screen_width / 2, screen_height / 3 + 25, 'Paused', center=True, display=s)
            if (draw_button(screen_width / 2, screen_height / 2, 'Continue', center=True, display=s) or
                    (time() - pause_cooldown > 1 and keyboard.is_pressed(pause_key))):
                pause_cooldown = time()
                pause = False

            if draw_button(screen_width / 2, screen_height / 2 + 35, 'Exit', center=True, display=s):
                leave = True
            s = smoothscale_by(s, pause_level)
            screen.blit(s, (screen_width / 2 * (1 - pause_level), 0))

        if play_level > 1:
            play_level += -play_level / 60
            s = pygame.Surface((screen_width, screen_height))  # the size of your rect
            s.set_alpha(play_level / 100 * 255)  # alpha level
            s.fill(BLACK)  # this fills the entire surface
            screen.blit(s, (0, 0))

        if 0.1 > velocity > -0.1 and hp <= 0 or leave:
            games += 1
            total += score
            notification.add('You Died!', 'Game Over')
            playtime += time() - start_time
            for _ in range(50):
                s = pygame.Surface((screen_width, screen_height))  # the size of your rect
                s.set_alpha(_)  # alpha level
                s.fill(BLACK)  # this fills the entire surface
                screen.blit(s, (0, 0))
                sleep(0.025)
                pygame.display.flip()
            break
        elif hp < 0:
            dw = 10

        # draw_text(get_mouse()[0], get_mouse()[1] - 20, str(turn))
        # s = pygame.Surface((screen_width, screen_height))  # the size of your rect
        # s.set_alpha(min((1 - hp / 100), 25) * 255)  # alpha level
        # s.fill(BLACK)  # this fills the entire surface
        # screen.blit(s, (0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.WINDOWFOCUSLOST:
                window_focused = False
            elif event.type == pygame.WINDOWFOCUSGAINED:
                window_focused = True
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        clock.tick(60)


def smoothscale_by(surface, scale_factor):
    return pygame.transform.smoothscale(surface,
                                        (int(surface.get_width() * scale_factor),
                                         int(surface.get_height() * scale_factor)))


def get_saves(path='users.ini', print_data=True):
    config = configparser.ConfigParser()
    # path = os.path.join(script_dir, path)
    config.read(path)
    if print_data:
        print(f'Loading Data from: {path}')

    users_ = config.sections()
    users = []
    for user in users_:
        if print_data:
            print(f'Loading User: {user}')
        u = {'name': user}
        for node in config.options(user):
            d = config.get(user, node)
            try:
                d = float(d)
            except ValueError:
                pass

            if print_data:
                print(f'{node}: {d}')
            u[node] = d
        users.append(u)
    return users


def load_ini_file(path, print_data=False, default_settings=None):
    config = configparser.ConfigParser()
    config.read(path)
    if print_data:
        print(f'Loading Data from: {path}')

    data = config.sections()
    sections = default_settings if default_settings is not None else {}
    for section in data:
        if print_data:
            print(f'Loading Section: {section}')
        u = {}
        for node in config.options(section):
            d = config.get(section, node)
            try:
                d = float(d)
            except ValueError:
                pass

            if print_data:
                print(f'{node}: {d}')
            u[node] = d
        sections[section] = u
    return sections


def transition(a, b, mult):
    # a, b = min(a, b), max(a, b)
    return a + (b - a) * mult


class ImageLoader:
    def __init__(self):
        self.path = None
        self.img = None
        self.img_data = None

    def load_file(self, path):
        """
        Loads the file on
        :param path:
        :return:
        """
        self.path = path
        if self.img is None and self.path is not None:
            # self.img = Image.open(self.path)
            self.reload_data()

    def reload_data(self):
        if self.img is not None:
            self.img_data = []
            for y in range(self.img.size[1]):
                col = []
                for x in range(self.img.size[0]):
                    col.append(self.img.getpixel((x, y)))
                self.img_data.append(col)


def main():
    global pressed, press_check, total, high_score, score, games, difficulty, pname, is_admin, playtime, mouse_delta, \
        window_focused, throttle, brake, turn_left, turn_right, pause_key
    mouse_speed = 0
    clock = pygame.time.Clock()
    #
    start_tutorial = False
    try:
        open('users.ini', 'r')
    except FileNotFoundError:
        start_tutorial = True
    get_saves()
    print()
    load_ini_file('settings.ini', True)
    print()
    page = 'home'
    notification.add('Users Loaded', f'Users loaded from: {"users.ini"}')
    notification.add('Settings Loaded', f'Settings loaded from: {"settings.ini"}')
    disp = 255
    keybind_startup = True

    changelog = [
        "- Version 0.90 - 7/11/2023",
        "   - Released base game",
        "",
        "- Version 0.91 - 8/11/2023",
        "   - Fixed Window Title",
        "   - Added back button for the new save screen",
        "   - Added changelog and restructured settings permissions to fit",
        "   - Added tooltip for difficulty settings",
        "   - Added impossible difficulty",
        "   - Started preparation for upcoming tutorial",
        "   - Added scrolling for changelog",
        "   - Tweaked darkness reveal speed",
        "   - Button presses now only register if the screen is in focus",
        "   - Added mouse wheel delta recording to system (for scrolling the changelog)",
        "   - Added version counter",
        "   - Transferred changelog to integrated form to allow for .exe construction",
        "   - Removed artifact from v0.9 relating to settings permissions",
        "",
        "- Version 0.92 - 14/11/23",
        "   - Added bug report feature in the event of a crash",
        "   - Fixed capitalisation for stats",
        "   - Added tutorial",
        "   - Added 'replay tutorial' button",
        "   - Added Pause menu",
        "   - Added game_speed attribute",
        "   - Tweaked startup notifications",
        "   - Added settings.ini",
        "   - Added keybinds + settings",
        "   - Added esc keybind to toggle pause menu",
        "   - Removed Admin (it was useless anyways)",
        "   - Prepared for cheats",
        "   - Fixed version counter",
        "   - Added soft-constraints for scrolling changelog and keybinds",
        "   - Added paragraph parsing system for changelog",
        "   - Reduced changelog lag by only rendering whats on the screen",
        "   - Reduced changelog lag by parsing all special characters at the beginning",
        "",
        "- Version 0.93 - 15/11/2023 - Minor Bug fixes",
        "   - Added start text for game",
        "   - Fixed jump when you open keybinds",
        "   - Health no longer regenerates whilst paused",
        "   - Discovered glitch which gives you infinite health for a while in impossible difficulty",
        "",
        "- Version 0.94 - 21/11/2023 - ",
        "   - Fixed parsing error in changelog for overflowing text",
        "   - Added Fade when entering game",
        "   - Keybinds now clear when clicked",
        "   - Fixed game crashing when pausing",
        "",
        "",
        "   --- KNOWN BUGS ---",
        "   - Lag when pausing game",
        "   - Wheels become out of sync when turning fast",
        "",
        "",
        "   --- UPCOMING FEATURES ---",
        "   - Animations in tutorial",
    ]
    ch = []
    for line in changelog:
        if len(line) > 0:
            if "   " in line:
                line = '>' + f'{line} '[3:-1]
            parse = format_paragraph(line, 77)
            for li in parse:
                ch.append(li)
                # print(li, 'para')
            for _ in range(len(parse)):
                # print(ch[-1 - _], 'pre')
                ch[-1 - _] = ch[-1 - _].strip('\n').replace('>', '    ')
                # print(ch[-1 - _], 'parse')
            # print()
        else:
            ch.append('')
    changelog = ch
    changelog_position = 0
    keybind_position = 0

    throttle_keybind = DefineActiveInput(screen_width / 3, screen_height / 3,
                                         'Throttle', 'str', 'W')
    steer_l_keybind = DefineActiveInput(screen_width / 3, screen_height / 3 + 60,
                                        'Steer Left', 'str', 'A')
    steer_r_keybind = DefineActiveInput(screen_width / 3, screen_height / 3 + 90,
                                        'Steer Right', 'str', 'D')
    brake_keybind = DefineActiveInput(screen_width / 3, screen_height / 3 + 30,
                                      'Brake', 'str', 'S')
    pause_keybind = DefineActiveInput(screen_width / 3, screen_height / 3 + 120,
                                      'Pause/Unpause', 'str', 'ESC')
    tp = 1
    play = False
    play_level = 0
    while True:
        if pressed:
            if not press_check:
                pressed = True
                press_check = True
            else:
                pressed = False
        else:
            pressed = False
            press_check = False
        screen.fill(BG)
        mouse_speed += mouse_delta
        mouse_speed = mouse_speed * 0.89
        settings = load_ini_file('settings.ini',
                                 default_settings={
                                     'keybinds': {
                                         'throttle': 'w',
                                         'brake': 's',
                                         'turn_left': 'a',
                                         'turn_right': 'd',
                                         'pause': 'esc',
                                     },
                                 })
        users = get_saves(print_data=False)

        turn_left = settings['keybinds']['turn_left']
        turn_right = settings['keybinds']['turn_right']
        brake = settings['keybinds']['brake']
        throttle = settings['keybinds']['throttle']
        pause_key = settings['keybinds']['pause']
        if play:
            play_level += 1
        if play and play_level >= 100:
            play = False
            play_level = 0
            disp = 255
            game()

        if keybind_startup:
            keybind_startup = False
            steer_l_keybind.i = turn_left
            steer_r_keybind.i = turn_right
            brake_keybind.i = brake
            throttle_keybind.i = throttle
            pause_keybind.i = pause_key

        # start
        if start_tutorial:
            text = ''
            page = None
            if tp == 1:
                draw_text(screen_width / 2, 75, 'Driving', center=True, size=25)
                text = [
                    'Driving in Run2D is relatively easy,',
                    "going fast isn't all that good as it reduces your turning circle,",
                    "this means that it'll take longer to turn the faster you go, like in real life.",
                    "High speeds also increases the damage you take and makes it harder to stop"
                ]
            elif tp == 2:
                draw_text(screen_width / 2, 75, 'Obstacles', center=True, size=25)
                text = [
                    "In front of you, obstacles will appear, hitting them makes you take damage.",
                    "These obstacles decrease in size the more you hit them, also decreasing damage taken,",
                    "though don't slow too much to avoid these, as they start to get angry when you stay",
                    "in one place for too long."
                    "To your sides is the sidewalk, its unsuitable surface will quickly destroy",
                    "even the hardiest of tyres",
                ]
            elif tp == 3:
                draw_text(screen_width / 2, 75, 'Health and Progress', center=True, size=25)
                text = [
                    "As you move forward, your score will increase from 200,",
                    "when you take damage, your score will also decrease by up to 200 total.",
                    "If you do not take damage for a period of time, your car will start to",
                    "repair itself, faster and faster"
                ]
            elif tp == 4:
                draw_text(screen_width / 2, 75, 'Controls', center=True, size=25)
                text = [
                    f"Clutch/Brake - {throttle}/{brake}",
                    f"Steering - {turn_left}/{turn_right}",
                    "Good luck!",
                ]
            y = -len(text) / 2
            for line in text:
                draw_text(screen_width / 2, screen_height / 2 + y * 30, line, center=True)
                y += 1

            if tp < 4:
                if draw_button(screen_width / 2, screen_height / 4 * 3, 'Continue', center=True):
                    tp += 1
            else:
                if draw_button(screen_width / 2, screen_height / 4 * 3, 'Finish', center=True):
                    start_tutorial = False
                    page = 'home'
            if tp > 1:
                if draw_button(screen_width / 2, screen_height / 4 * 3 + 30, 'Back', center=True):
                    tp -= 1
        if page == 'stats':
            draw_text(screen_width / 2, 75, 'Stats', center=True, size=25)
            draw_text(screen_width / 3, screen_height / 3, f'Username: {pname}')
            draw_text(screen_width / 3, screen_height / 3 + 30, f'Total Score: {round(total, 2)}')
            draw_text(screen_width / 3, screen_height / 3 + 60, f'High Score: {round(high_score, 2)}')
            draw_text(screen_width / 3, screen_height / 3 + 90, f'Last Score: {round(score, 2)}')
            draw_text(screen_width / 3, screen_height / 3 + 120, f'Games Played: {round(games)}')
            draw_text(screen_width / 3, screen_height / 3 + 150,
                      f'Average Points per game: {round(total / games, 2)}')
            draw_text(screen_width / 3, screen_height / 3 + 180, f'Total Playtime: {round(playtime / 60)}m')
            if draw_button(screen_width / 2, screen_height / 2 + 200, 'Back', center=True):
                page = 'home'
        elif page == 'keybinds':
            throttle_keybind.update()
            brake_keybind.update()
            steer_l_keybind.update()
            steer_r_keybind.update()
            pause_keybind.update()

            throttle_keybind.y = screen_height / 3 + keybind_position
            brake_keybind.y = screen_height / 3 + keybind_position + 30
            steer_l_keybind.y = screen_height / 3 + keybind_position + 60
            steer_r_keybind.y = screen_height / 3 + keybind_position + 90
            pause_keybind.y = screen_height / 3 + keybind_position + 120

            keybind_position = max(min(keybind_position, -80), -80)

            if not steer_l_keybind.on:
                settings['keybinds']['turn_left'] = steer_l_keybind.o

            if not steer_r_keybind.on:
                settings['keybinds']['turn_right'] = steer_r_keybind.o

            if not throttle_keybind.on:
                settings['keybinds']['throttle'] = throttle_keybind.o

            if not brake_keybind.on:
                settings['keybinds']['brake'] = brake_keybind.o

            if not pause_keybind.on:
                settings['keybinds']['pause'] = pause_keybind.o

            draw_rect(0, 0, screen_width, 105, colour=BG, fill=True)
            draw_rect(0, screen_height / 2 + 195, screen_width, screen_height / 2 - 190, colour=BG, fill=True)

            draw_text(screen_width / 2, 75, 'Keybinds', center=True, size=25)

            if draw_button(screen_width / 2, screen_height / 2 + 150, 'Reset Keybinds', center=True):
                settings['keybinds']['throttle'] = 'W'
                settings['keybinds']['brake'] = 'S'
                settings['keybinds']['turn_left'] = 'A'
                settings['keybinds']['turn_right'] = 'D'
                settings['keybinds']['pause'] = 'ESC'
                keybind_startup = True

            if draw_button(screen_width / 2, screen_height / 2 + 200, 'Back', center=True):
                page = 'settings'
            keybind_position += mouse_speed * 5
        elif page == 'del_saves':
            draw_text(screen_width / 2, 75, 'Delete Save', center=True, size=25)
            y = 150
            buttons = [False for _ in range(len(users))]
            for _ in range(len(users)):
                user = users[_]
                if draw_button(screen_width / 2, y, user['name'], center=True):
                    buttons[_] = True
                y += 30
            for _ in range(len(buttons)):
                if buttons[_]:
                    if users[_]['name'] == pname:
                        pname = None
                        is_admin = False
                        notification.add('Profile Unloaded', f"'{users[_]['name']}' Unloaded")
                    notification.add('Save File Deleted', f"'{users[_]['name']}' Deleted Successfully")
                    del users[_]
                    sleep(0.1)
                    break
            if draw_button(screen_width / 2, screen_height / 2 + 200, 'Back', center=True) or len(users) == 0:
                page = 'settings'
        elif page == 'changelog':
            for _ in range(len(changelog)):
                if 0 < screen_height / 2 + 150 - _ * 30 + changelog_position < screen_height:
                    draw_text(screen_width / 4, screen_height / 2 + 150 - _ * 30 + changelog_position,
                              changelog[-_ - 1])

            changelog_position = min(max(changelog_position, 0), len(changelog) * 30 - screen_height / 2)

            draw_rect(0, 0, screen_width, 105, colour=BG, fill=True)
            draw_rect(0, screen_height / 2 + 195, screen_width, screen_height / 2 - 190, colour=BG, fill=True)

            draw_text(screen_width / 2, 75, 'Changelog', center=True, size=25)
            if draw_button(screen_width / 2, screen_height / 2 + 200, 'Back', center=True):
                page = 'settings'

            changelog_position += mouse_speed * 5
            # print(pygame.mouse.get_focused())
        elif page == 'home':
            draw_text(screen_width / 2, screen_height / 4, 'Run 2D', size=30, center=True)
            if draw_button(screen_width / 3, screen_height / 3, 'New') and len(users) < 10:
                inp = DefineActiveInput(screen_width / 2 - 60, screen_height / 2, 'Name', 'str', 'New Save')
                save = False
                while True:
                    screen.fill(BG)
                    inp.update()
                    if not inp.error:
                        if draw_button(screen_width / 2, screen_height / 2 + 40, 'Create', center=True):
                            save = True
                            notification.add('Save File Created', f"'{inp.o}' Created Successfully")
                            break
                    else:
                        draw_button(screen_width / 2, screen_height / 2 + 40, 'Create', center=True, lock=True)
                    draw_text(screen_width / 2, screen_height / 2 - 50, 'Please Input Save Name', size=30, center=True)
                    if draw_button(screen_width / 2, screen_height / 2 + 80, 'Back', center=True):
                        break
                    for event in pygame.event.get():
                        if event.type == pygame.WINDOWFOCUSLOST:
                            window_focused = False
                        elif event.type == pygame.WINDOWFOCUSGAINED:
                            window_focused = True
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            quit()
                    pygame.display.flip()
                if save:
                    users.append({'name': inp.o,
                                  'points': 0,
                                  'max': 1,
                                  'difficulty': 2,
                                  'total': 0,
                                  'games': 0})
            elif len(users) >= 10 and draw_button(screen_width / 3, screen_height / 3, 'New'):
                notification.add('Maximum Saves Reached', 'Delete some to free up space',
                                 type_of=notification.click())
            if draw_button(screen_width / 3, screen_height / 3 + 30, 'Load', lock=len(users) == 0):
                page = 'saves'
            if draw_button(screen_width / 3, screen_height / 3 + 60, 'Settings'):
                page = 'settings'
            if draw_button(screen_width / 3, screen_height / 3 + 90, 'Stats', lock=pname is None or games <= 0):
                page = 'stats'
            if draw_button(screen_width / 3, screen_height / 3 - 30, 'Start', lock=pname is None or play):
                play = True
            if draw_button(screen_width / 3, screen_height / 3 + 120, 'Exit'):
                pygame.quit()
                break
        elif page == 'saves':
            draw_text(screen_width / 2, 75, 'Load', center=True, size=25)
            y = 150
            buttons = [False for _ in range(len(users))]
            for _ in range(len(users)):
                user = users[_]
                if draw_button(screen_width / 2, y, user['name'], center=True):
                    buttons[_] = True
                y += 30
            for _ in range(len(buttons)):
                if buttons[_]:
                    user = users[_]
                    high_score = user['max']
                    score = user['points']
                    difficulty = user['difficulty']
                    total = user['total']
                    games = user['games']
                    pname = user['name']
                    try:
                        playtime = user['playtime']
                    except KeyError:
                        playtime = 0
                    try:
                        is_admin = user['is_admin'] == 1
                    except KeyError:
                        is_admin = False
                    page = 'home'
                    notification.add('Save File Loaded', f"'{user['name']}' Loaded Successfully")
                    break
            if draw_button(screen_width / 2, screen_height / 2 + 200, 'Back', center=True):
                page = 'home'
        elif page == 'settings':
            draw_text(screen_width / 2, 75, 'Settings', center=True, size=25)
            if draw_button(screen_width / 3, screen_height / 3 + 30, 'Delete Save', lock=len(users) == 0):
                page = 'del_saves'
            if draw_button(screen_width / 3, screen_height / 3 + 60, 'Difficulty', lock=pname is None):
                page = 'diff'
            if draw_button(screen_width / 3, screen_height / 3 + 90, 'Cheats', lock=True):
                pass
            if draw_button(screen_width / 3, screen_height / 3 + 120, 'Changelog'):
                page = 'changelog'
                changelog_position = 0
            if draw_button(screen_width / 3, screen_height / 3 + 150, 'Restart tutorial', lock=False):
                tp = 1
                start_tutorial = True
            if draw_button(screen_width / 3, screen_height / 3 + 180, 'Keybinds'):
                page = 'keybinds'
                keybind_position = -80
            if draw_button(screen_width / 2, screen_height / 2 + 200, 'Back', center=True):
                page = 'home'
        elif page == 'diff':
            draw_text(screen_width / 2, 75, 'Difficulty', center=True, size=25)
            if draw_button(screen_width / 2, screen_height / 2 + 200, 'Back', center=True):
                page = 'settings'
            ts = 25
            if draw_button(screen_width / 2, screen_height / 2 - (ts + 10), 'Easy', center=True, size=ts,
                           lock=difficulty == 1):
                difficulty = 1
            if draw_button(screen_width / 2, screen_height / 2, 'Normal', center=True, size=ts,
                           lock=difficulty == 2):
                difficulty = 2
            if draw_button(screen_width / 2, screen_height / 2 + (ts + 10), 'Hard', center=True, size=ts,
                           lock=difficulty == 3):
                difficulty = 3
            if draw_button(screen_width / 2, screen_height - 25, 'Impossible', center=True, size=15,
                           lock=difficulty == 25):
                difficulty = 25
            # draw_text(get_mouse()[0] + 10, get_mouse()[1] + 10, get_mouse())
            # 1 - 374, 262, 426, 292
            # 2 - 365, 300, 435 327
            # 3 - 375, 333, 425, 362
            object_count = None
            damage_multiplier = None
            time_for_chase = None
            if 374 < get_mouse()[0] < 426 and 262 < get_mouse()[1] < 292:
                object_count = 8
                damage_multiplier = 0.5
                time_for_chase = 120
            elif 365 < get_mouse()[0] < 435 and 300 < get_mouse()[1] < 327:
                object_count = 15
                damage_multiplier = 1
                time_for_chase = 60
            elif 375 < get_mouse()[0] < 425 and 333 < get_mouse()[1] < 362:
                object_count = 23
                damage_multiplier = 1.5
                time_for_chase = 40
            if object_count is not None:
                # draw_lines(get_mouse()[0] + 10, get_mouse()[1] + 10, [f'Objects: {object_count}',
                #                                                       f'Damage Multiplier: {damage_multiplier}',
                #                                                       f'Chase time: {time_for_chase}'],
                #            fill=True)
                lines = [f'Objects: {object_count}',
                         f'Damage Multiplier: {damage_multiplier}',
                         f'Chase time (at 60fps): {time_for_chase}s']
                ms = 0
                for line in lines:
                    ms = max(draw_text(-1000, -1000, line)[0], ms)
                draw_rect(get_mouse()[0] + 15, get_mouse()[1] + 15, ms + 10, len(lines) * 25 + 5, colour=BG, fill=True)
                draw_rect(get_mouse()[0] + 15, get_mouse()[1] + 15, ms + 10, len(lines) * 25 + 5)
                for _ in range(len(lines)):
                    draw_text(get_mouse()[0] + 20, get_mouse()[1] + 20 + _ * 25, lines[_])
        config = configparser.ConfigParser()
        config.read('users.ini')
        for section in config.sections():
            found = False
            for user in users:
                if section == user['name']:
                    found = True
            if not found:
                config.remove_section(section)
        for user in users:
            if user['name'] == pname:
                user['max'] = high_score
                user['points'] = score
                user['difficulty'] = difficulty
                user['total'] = total
                user['games'] = games
                user['playtime'] = playtime
                break
        for user in users:
            if not config.has_section(user['name']):
                config.add_section(user['name'])
            config.set(user['name'], 'points', str(user['points']))
            config.set(user['name'], 'max', str(user['max']))
            config.set(user['name'], 'difficulty', str(user['difficulty']))
            config.set(user['name'], 'total', str(user['total']))
            config.set(user['name'], 'games', str(user['games']))
            for thing in user:
                if thing not in ['points', 'max', 'difficulty', 'total', 'games']:
                    config.set(user['name'], thing, str(user[thing]))

        with open('users.ini', 'w') as f:
            config.write(f)

        config = configparser.ConfigParser()
        config.read('settings.ini')

        for section in settings:
            if not config.has_section(section):
                config.add_section(section)

            for option in settings[section]:
                config.set(section, option, settings[section][option])

        with open('settings.ini', 'w') as f:
            config.write(f)

        # debug
        for _ in range(len(active_inputs)):
            active_inputs[_].update(False)
        if disp < 200:
            notification.draw()
        if disp > 0:
            disp -= min(disp, 2.5)
            s = pygame.Surface((screen_width, screen_height))  # the size of your rect
            s.set_alpha(disp)  # alpha level
            s.fill(BLACK)  # this fills the entire surface
            screen.blit(s, (0, 0))
        if play_level > 0:
            s = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)  # the size of your rect
            s.set_alpha(play_level / 100 * 255)  # alpha level
            s.fill(BLACK)  # this fills the entire surface
            screen.blit(s, (0, 0))
        draw_text(5, screen_height - 25, 'v0.94')
        # draw debug

        # draw_line(screen_width, 0, 0, screen_height, colour=RED)
        # draw_line(0, 0, screen_width, screen_height, colour=RED)
        # draw_line(screen_width / 2, 0, screen_width / 2, screen_height, colour=RED)
        # draw_line(0, screen_height / 2, screen_width, screen_height / 2, colour=RED)
        pygame.display.flip()
        mouse_delta = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEWHEEL:
                mouse_delta = event.y
            if event.type == pygame.WINDOWFOCUSLOST:
                window_focused = False
            elif event.type == pygame.WINDOWFOCUSGAINED:
                window_focused = True
        clock.tick(60)


notification = CreateNotificationCenter(5, 5)
keyboard.on_press(on_press_callback)
if __name__ == '__main__':
    try:
        main()
        # game()

    except Exception as e:
        if 'display Surface quit' not in str(e):
            pygame.quit()
            raise e
            # print()
            # print('Ohno! It seems this program has run into an unexpected error.')
            # print('If you would like to report this, please email the following \n'
            #       'error data to the developer at spacerug.bugreports@gmail.com')
            # print()
            # print(e)
            # print()
            # sleep(5)
            # print('Press ESC to exit program')
            # while True:
            #     if keyboard.is_pressed('esc'):
            #         break
