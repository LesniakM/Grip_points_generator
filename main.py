import math
from math import cos, sin, atan, sqrt, radians, acos, degrees, asin

import cv2
from PIL import Image
from PIL import ImageTk
import imutils
from tkinter import Tk, Label, StringVar, Button, ttk, IntVar, Canvas, PhotoImage
import tkinter.filedialog


def convert_image_to_tk(cv2_image):
    blue, green, red, alpha = cv2.split(cv2_image)
    merged_img = cv2.merge((red, green, blue, alpha))
    image_array = Image.fromarray(merged_img)
    tk_image = ImageTk.PhotoImage(image=image_array)
    return tk_image


def save_img_to_file(name, img):
    cv2.imwrite('output/' + name + '.png', img)


class ImageEditor:
    def __init__(self):
        self.rotate_scale_factor = 16
        self.load_method = cv2.IMREAD_UNCHANGED
        self.scale_up_method = cv2.INTER_NEAREST
        self.scale_down_method = cv2.INTER_AREA
        self.scale_default_method = cv2.INTER_NEAREST

        self.allowed_angles = (0,
                               11.31,  # 1/5
                               18.43,  # 1/3
                               26.57,  # 1/2
                               33.69,  # 2/3
                               )

    def load_image(self, path):
        image = cv2.imread(path, self.load_method)
        return image

    def rotate_image(self, image, deg, scale=None):
        if scale is None:
            scale = self.rotate_scale_factor
        if scale != 0:
            scaled_up = self.resize(image, scale, self.scale_up_method)
            rotated_image = imutils.rotate_bound(scaled_up, angle=deg)
            scaled_down = self.resize(rotated_image, 1 / scale, self.scale_down_method)
            return scaled_down
        else:
            rotated_image = imutils.rotate_bound(image, angle=deg)
            return rotated_image

    def resize(self, image, scale_factor, interpolation):
        width = int(image.shape[1] * scale_factor)
        height = int(image.shape[0] * scale_factor)
        dim = (width, height)
        resized = cv2.resize(image, dim, interpolation=interpolation)
        return resized

    def get_allowed_angles_list(self):
        angle_list = []
        angle_amt = len(self.allowed_angles)
        for n in range(40):
            angle = self.allowed_angles[n - int(n / angle_amt) * angle_amt] + int(n / angle_amt) * 45
            angle_list.append(angle)
        return angle_list


class App:
    def __init__(self):
        self.gui = Tk(className='Python Examples - Window Size')
        self.gui.geometry("1400x600")
        self.gui.title("Welcome to Grip pointer app")
        self.gui.tk_setPalette(background='#3C3F41', foreground='#CCCCCC',
                               activeBackground='black', activeForeground='#40E0D0')

        self.combo_style = ttk.Style()
        self.combo_style.theme_use('clam')
        self.combo_style.configure("TCombobox", fieldbackground='#3C3F41', foreground='#CCCCCC', background='#3C3F41',
                                   activeBackground='black', activeForeground='#40E0D0', bordercolor='#111111')

        self.img_edit = ImageEditor()

        self.mirrored = StringVar(value="False")
        self.image_path = StringVar()
        self.dimensions_var = StringVar()
        self.preview_scale_var = IntVar(value=4)
        self.load_scale_var = IntVar(value=1)

        self.mouse_var_right = StringVar(value="(0,0)")
        self.mouse_var_middle = StringVar(value="(0,0)")
        self.mouse_pos_right = [0, 0]
        self.mouse_pos_middle = [0, 0]
        self.points_angle = 0
        self.gui.bind("<Button 3>", self.get_mouse_click_pos_right)
        self.gui.bind("<Button 2>", self.get_mouse_click_pos_middle)

        self.dimensions_label_info = None
        self.dimensions_label = None
        self.preview_scale_box = None
        self.mirrored_label = None
        self.mirrored_box = None
        self.load_scale_label = None
        self.preview_scale_label = None
        self.load_scale_box = None
        self.preview_canvas = None
        self.preview_image = None
        self.image_on_canvas = None
        self.preview_canvas_grip_indicator = None
        self.preview_canvas_tip_indicator = None
        self.preview_canvas_line = None
        self.info_label = None
        self.path_label = None
        self.grip_pos_label = None
        self.tip_pos_label = None
        self.select_button = None
        self.save_points_button = None
        self.add_points_button = None
        self.image_data = None
        self.char_grip_list = None

        self.angles_list = self.img_edit.get_allowed_angles_list()
        self.best_suited_img = None

        self.create_ui_elements()
        self.gui.mainloop()

    # noinspection PyTypeChecker
    def create_ui_elements(self):
        self.dimensions_label_info = Label(self.gui, text="Dimensions:")
        self.dimensions_label = Label(self.gui, textvariable=self.dimensions_var)

        self.preview_scale_label = Label(self.gui, text="Preview scale:")
        self.preview_scale_box = ttk.Combobox(self.gui,
                                              textvariable=self.preview_scale_var,
                                              values=[1, 2, 4, 6, 8],
                                              background='#3C3F41',
                                              foreground='#CCCCCC')



        self.load_scale_label = Label(self.gui, text="Load pre-scale:")
        self.load_scale_box = ttk.Combobox(self.gui, textvariable=self.load_scale_var,
                                           values=[1, 2, 4],
                                           background='#3C3F41',
                                           foreground='#CCCCCC')

        self.mirrored_label = Label(self.gui, text="Mirrored:")
        self.mirrored_box = ttk.Combobox(self.gui, textvariable=self.mirrored, values=[True, False],
                                         background='#3C3F41',
                                         foreground='#CCCCCC')

        # self.preview_image = PhotoImage(file=r'preview.png')
        self.preview_canvas = Canvas(self.gui, width=0, height=0, bg='#AAAAAA')
        self.image_on_canvas = self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
        self.info_label = Label(self.gui, text="Path:")
        self.path_label = Label(self.gui, textvariable=self.image_path)

        self.grip_pos_label = Label(self.gui, textvariable=self.mouse_var_right)
        self.tip_pos_label = Label(self.gui, textvariable=self.mouse_var_middle)

        self.select_button = Button(self.gui, text="Select image", command=self.select_image)
        self.add_points_button = Button(self.gui, text="Select image", command=self.append_grip_point)
        self.save_points_button = Button(self.gui, text="Save points!", command=self.save_grip_points)

        self.organize_ui()

    def organize_ui(self):
        row_height = 26
        col_width = 100
        left_pad = 6
        top_pad = 6

        self.dimensions_var.set("Load image first, please!")
        self.image_path.set("Load image first, please!")

        self.preview_canvas.place(x=col_width*0+left_pad, y=row_height*7+top_pad)

        self.info_label.place(x=col_width*0+left_pad, y=row_height*0+top_pad)
        self.path_label.place(x=col_width*1+left_pad, y=row_height*0+top_pad)
        self.select_button.place(x=col_width*0+left_pad, y=row_height*1+top_pad)
        self.save_points_button.place(x=col_width*1+left_pad, y=row_height*1+top_pad)

        self.grip_pos_label.place(x=col_width*0+left_pad, y=row_height*2+top_pad)
        self.tip_pos_label.place(x=col_width*1+left_pad, y=row_height*2+top_pad)

        self.dimensions_label_info.place(x=col_width*0+left_pad, y=row_height*3+top_pad)
        self.dimensions_label.place(x=col_width*1+left_pad, y=row_height*3+top_pad)

        self.preview_scale_label.place(x=col_width*0+left_pad, y=row_height*4+top_pad)
        self.preview_scale_box.place(x=col_width*1+left_pad, y=row_height*4+top_pad)
        self.preview_scale_box.bind('<<ComboboxSelected>>', self.refresh_preview_img)

        self.load_scale_label.place(x=col_width*0+left_pad, y=row_height*5+top_pad)
        self.load_scale_box.place(x=col_width*1+left_pad, y=row_height*5+top_pad)

        self.mirrored_label.place(x=col_width*0+left_pad, y=row_height*6+top_pad)
        self.mirrored_box.place(x=col_width*1+left_pad, y=row_height*6+top_pad)

    def select_image(self):
        path = tkinter.filedialog.askopenfilename()
        self.image_path.set("..." + path[-48:])
        self.img_edit.input_path = path
        self.image_data = self.img_edit.load_image(path)
        if self.load_scale_var.get() != 1:
            self.image_data = self.img_edit.resize(self.image_data, self.load_scale_var.get(),
                                                   self.img_edit.scale_default_method)
        self.refresh_preview_img()

    def refresh_preview_img(self, *args):
        if self.image_data is not None:
            if self.preview_scale_var.get() != 1:
                new_image = self.img_edit.resize(self.image_data, self.preview_scale_var.get(),
                                                 self.img_edit.scale_default_method)
                new_image = convert_image_to_tk(new_image)
            else:
                new_image = convert_image_to_tk(self.image_data)
            self.preview_image = new_image  # GC prevention!
            self.preview_canvas.itemconfigure(self.image_on_canvas, image=new_image)
            self.preview_canvas.config(width=new_image.width(), height=new_image.height())
            dimension_string = str(len(self.image_data[0])) + "x" + str(len(self.image_data)) + \
                               "(Preview:" + str(new_image.width()) + "x" + str(new_image.height()) + ")"
            self.dimensions_var.set(dimension_string)

    def save_grip_points(self):
        with open("output/char_grip_list.txt", "w") as f:
            for grip in self.char_grip_list:
                f.write(str(grip) + "\n")
        f.close()

    def get_mouse_click_pos_right(self, event_origin):
        self.mouse_pos_right[0] = int(event_origin.x)
        self.mouse_pos_right[1] = int(event_origin.y)
        scale = self.preview_scale_var.get()
        if self.preview_canvas_grip_indicator is not None:
            self.preview_canvas.delete(self.preview_canvas_grip_indicator)
        mouse = [0, 0]
        mouse[0] = self.mouse_pos_right[0] // scale
        mouse[1] = self.mouse_pos_right[1] // scale
        self.preview_canvas_grip_indicator = self.draw_click_indicator(mouse[0], mouse[1],)
        self.refresh_angle()
        self.mouse_var_right.set("Grip:" + str(mouse))

    def get_mouse_click_pos_middle(self, event_origin):
        self.mouse_pos_middle[0] = int(event_origin.x)
        self.mouse_pos_middle[1] = int(event_origin.y)
        scale = self.preview_scale_var.get()
        if self.preview_canvas_tip_indicator is not None:
            self.preview_canvas.delete(self.preview_canvas_tip_indicator)
        mouse = [0, 0]
        mouse[0] = self.mouse_pos_middle[0] // scale
        mouse[1] = self.mouse_pos_middle[1] // scale
        self.preview_canvas_tip_indicator = self.draw_click_indicator(mouse[0], mouse[1], fill='red')
        self.refresh_angle()
        self.mouse_var_middle.set("Tip:" + str(mouse) + "angle:" + str(self.points_angle)[:5])

    def draw_click_indicator(self, x, y, fill='white'):
        if self.preview_canvas_line is not None:
            self.preview_canvas.delete(self.preview_canvas_line)
        self.preview_canvas_line = self.preview_canvas.create_line(self.mouse_pos_middle[0], self.mouse_pos_middle[1],
                                                                   self.mouse_pos_right[0], self.mouse_pos_right[1],
                                                                   dash=(4, 2))
        scale = self.preview_scale_var.get()
        rect = self.preview_canvas.create_rectangle(
            (x * scale,
             y * scale,
             x * scale + scale,
             y * scale + scale),
            fill=fill)
        return rect

    def refresh_angle(self):
        dy = self.mouse_pos_middle[1] - self.mouse_pos_right[1]
        dx = self.mouse_pos_middle[0] - self.mouse_pos_right[0]
        self.points_angle = degrees(math.atan2(dy, dx)) + 90
        if self.points_angle < 0:
            self.points_angle = self.points_angle + 360
        best_suited = min(enumerate(self.angles_list), key=lambda x: abs(x[1] - self.points_angle))
        if self.mirrored.get() == "True":
            self.best_suited_img = best_suited[0] + 40
        else:
            self.best_suited_img = best_suited[0]
        print(self.points_angle, best_suited, self.best_suited_img)


    def append_grip_point(self):
        self.char_grip_list.append("points")


app = App()
