import math
import cv2
import tkinter.filedialog

from image_manager import ImageManager
from math import degrees
from tkinter import Tk, Label, StringVar, Button, ttk, IntVar, Canvas


def save_img_to_file(name, img):
    cv2.imwrite('output/' + name + '.png', img)


class App:
    def __init__(self):
        self.gui = Tk(className='Python Examples - Window Size')
        self.gui.geometry("1400x600")
        self.gui.title("Welcome to Grip pointer app")

        self.img_mng = ImageManager()

        self.mirrored = StringVar(value="False")
        self.image_path = StringVar(value="Load image first, please!")
        self.preview_scale_var = IntVar(value=2)
        self.load_scale_var = IntVar(value=4)

        self.mouse_var_right = StringVar(value="(0,0)")
        self.mouse_var_middle = StringVar(value="(0,0)")
        self.mouse_pos_right = [0, 0]
        self.mouse_pos_middle = [0, 0]
        self.points_angle = 0
        self.gui.bind("<Button 3>", self.get_mouse_click_pos_right)
        self.gui.bind("<Button 2>", self.get_mouse_click_pos_middle)

        self.char_image = None
        self.weapon_image = None
        self.preview_canvas_grip_indicator = None
        self.preview_canvas_tip_indicator = None
        self.preview_canvas_line = None
        self.image_data = None
        self.char_grip_list = []
        self.char_grip_list_var = StringVar(value=str(self.char_grip_list))

        self.angles_list = self.img_mng.get_allowed_angles_list()
        self.best_suited_img = None

        self.combo_style = None
        self.set_color_palettes()
        self.create_ui_elements()
        self.gui.mainloop()

    # noinspection PyTypeChecker
    def create_ui_elements(self):
        self.dimensions_label_info = Label(self.gui, text="Dimensions:")
        self.dimensions_var = StringVar(value="Load image first, please!")
        self.dimensions_label = Label(self.gui, textvariable=self.dimensions_var)

        self.preview_scale_label = Label(self.gui, text="Preview scale:")
        self.preview_scale_box = ttk.Combobox(self.gui,
                                              textvariable=self.preview_scale_var,
                                              values=[1, 2, 4, 6, 8])

        self.load_scale_label = Label(self.gui, text="Load pre-scale:")
        self.load_scale_box = ttk.Combobox(self.gui, textvariable=self.load_scale_var,
                                           values=[1, 2, 4])

        self.mirrored_label = Label(self.gui, text="Mirrored:")
        self.mirrored_box = ttk.Combobox(self.gui, textvariable=self.mirrored, values=[True, False])

        self.preview_canvas = Canvas(self.gui, width=0, height=0, bg='#AAAAAA')
        self.image_on_canvas = self.preview_canvas.create_image(0, 0, anchor="nw", image=self.char_image)
        self.info_label = Label(self.gui, text="Path:")
        self.path_label = Label(self.gui, textvariable=self.image_path)

        self.grip_pos_label = Label(self.gui, textvariable=self.mouse_var_right)
        self.tip_pos_label = Label(self.gui, textvariable=self.mouse_var_middle)
        self.char_grip_list_label = Label(self.gui, textvariable=self.char_grip_list_var)

        self.select_button = Button(self.gui, text="Select image", command=self.select_image)
        self.add_points_button = Button(self.gui, text="Add points to list", command=self.append_grip_point)
        self.save_points_button = Button(self.gui, text="Save list!", command=self.save_grip_points)

        self.organize_ui()

    def organize_ui(self):
        row_height = 26
        col_width = 100
        left_pad = 6
        top_pad = 6

        self.preview_canvas.place(x=col_width * 0 + left_pad, y=row_height * 7 + top_pad)

        self.info_label.place(x=col_width * 0 + left_pad, y=row_height * 0 + top_pad)
        self.path_label.place(x=col_width * 1 + left_pad, y=row_height * 0 + top_pad)
        self.select_button.place(x=col_width * 0 + left_pad, y=row_height * 1 + top_pad)
        self.save_points_button.place(x=col_width * 1 + left_pad, y=row_height * 1 + top_pad)

        self.grip_pos_label.place(x=col_width * 0 + left_pad, y=row_height * 2 + top_pad)
        self.tip_pos_label.place(x=col_width * 1 + left_pad, y=row_height * 2 + top_pad)

        self.dimensions_label_info.place(x=col_width * 0 + left_pad, y=row_height * 3 + top_pad)
        self.dimensions_label.place(x=col_width * 1 + left_pad, y=row_height * 3 + top_pad)

        self.preview_scale_label.place(x=col_width * 0 + left_pad, y=row_height * 4 + top_pad)
        self.preview_scale_box.place(x=col_width * 1 + left_pad, y=row_height * 4 + top_pad)
        self.preview_scale_box.bind('<<ComboboxSelected>>', self.refresh_preview_img)

        self.load_scale_label.place(x=col_width * 0 + left_pad, y=row_height * 5 + top_pad)
        self.load_scale_box.place(x=col_width * 1 + left_pad, y=row_height * 5 + top_pad)

        self.mirrored_label.place(x=col_width * 0 + left_pad, y=row_height * 6 + top_pad)
        self.mirrored_box.place(x=col_width * 1 + left_pad, y=row_height * 6 + top_pad)
        self.add_points_button.place(x=col_width * 2.5 + left_pad, y=row_height * 6 + top_pad)

        self.char_grip_list_label.place(x=col_width * 0 + left_pad, y=row_height * 7 + top_pad)

    def set_color_palettes(self):
        background_color = '#3C3F41'
        foreground_color = '#CCCCCC'
        active_background_color = '#DDDDDD'
        active_foreground_color = '#222222'

        self.gui.tk_setPalette(background=background_color,
                               foreground=foreground_color,
                               activeBackground=active_background_color,
                               activeForeground=active_foreground_color)

        self.combo_style = ttk.Style()
        self.combo_style.theme_use('default')
        self.combo_style.configure("TCombobox",
                                   fieldbackground=background_color,
                                   foreground=foreground_color,
                                   background=background_color,
                                   activeBackground=active_background_color)

    def select_image(self):
        path = tkinter.filedialog.askopenfilename()
        self.image_path.set("..." + path[-48:])
        self.img_mng.input_path = path
        self.image_data = self.img_mng.load_image(path)
        if self.load_scale_var.get() != 1:
            self.image_data = self.img_mng.resize(self.image_data, self.load_scale_var.get(),
                                                  self.img_mng.scale_default_method)
        self.refresh_preview_img()

    def refresh_preview_img(self, *args):
        if self.image_data is not None:
            if self.preview_scale_var.get() != 1:
                new_image = self.img_mng.resize(self.image_data, self.preview_scale_var.get(),
                                                self.img_mng.scale_default_method)
                new_image = self.img_mng.convert_image_to_tk(new_image)
            else:
                new_image = self.img_mng.convert_image_to_tk(self.image_data)
            self.char_image = new_image  # GC prevention!
            self.preview_canvas.itemconfigure(self.image_on_canvas, image=new_image)
            self.preview_canvas.config(width=new_image.width(), height=new_image.height())
            dimension_string = str(len(self.image_data[0])) + "x" + str(len(self.image_data)) + \
                "(Preview:" + str(new_image.width()) + "x" + str(new_image.height()) + ")"

            self.dimensions_var.set(dimension_string)
            self.char_grip_list_label.place(x=6, y=26 * 7 + 10 + new_image.height())

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
        self.preview_canvas_grip_indicator = self.draw_click_indicator(mouse[0], mouse[1], )
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
            if best_suited[0] == 0:
                self.best_suited_img = 40
            else:
                self.best_suited_img = 80 - best_suited[0]
        else:
            self.best_suited_img = best_suited[0]
        print(self.points_angle, best_suited, self.best_suited_img)

    def append_grip_point(self):
        image_width = len(self.image_data[0])
        image_height = len(self.image_data)
        if image_height != image_width:
            frames = image_width // image_height
        grip_points = self.mouse_var_right.get().split(":")[1]
        image_index = ", " + str(self.best_suited_img) + ")"
        tupled = grip_points.replace("[", "(").replace("]", image_index)
        self.char_grip_list.append(tupled)
        self.char_grip_list_var.set(str(self.char_grip_list))


app = App()
