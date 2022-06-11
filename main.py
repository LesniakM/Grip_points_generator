import math
import cv2
import tkinter.filedialog

from trails_generator import TrailsGen as TG
from image_manager import ImageManager
from math import degrees
from tkinter import Tk, Label, StringVar, Button, ttk, IntVar, Canvas

from PIL import ImageTk


def save_img_to_file(name: str, img):
    cv2.imwrite('output/' + name + '.png', img)


class App:
    def __init__(self):
        self.gui = Tk(className='Python Examples - Window Size')
        self.gui.geometry("1400x600")
        self.gui.title("Welcome to Grip pointer app")

        self.img_mng = ImageManager()

        self.mirrored = StringVar(value="False")
        self.image_path = StringVar(value="Load image first, please!")
        self.preview_scale_var = IntVar(value=1)
        self.load_scale_var = IntVar(value=4)

        self.mouse_var_right = StringVar(value="(0,0)")
        self.mouse_var_middle = StringVar(value="(0,0)")
        self.mouse_pos_right = [0, 0]
        self.mouse_pos_middle = [0, 0]
        self.points_angle = 0
        self.gui.bind("<Button 3>", self.get_mouse_click_pos_right)
        self.gui.bind("<Button 2>", self.get_mouse_click_pos_middle)

        self.weapon_image_cv2 = self.img_mng.load_image("preview_weapon.png")
        self.weapon_image = self.img_mng.convert_image_to_tk(self.weapon_image_cv2)
        self.preview_canvas_grip_indicator = None
        self.preview_canvas_tip_indicator = None
        self.preview_canvas_line = None
        self.preview_canvas_weapon_indicator = None
        self.char_image = None
        self.image_data = None
        self.tk_tails_images = []
        self.real_points_list = []
        self.char_grip_list = []
        self.char_grip_list_var = StringVar(value=str(self.char_grip_list))

        self.angles_list = self.img_mng.get_allowed_angles_list()
        self.best_suited_img = None

        self.combo_style = None
        self.set_color_palettes()

        self.wpn_rtd_img_cv = []
        self.wpn_rtd_img_tk = []
        self.wpn_angles = []
        self.wpn_grip = []

        self.wpn_rtd_img_cv, self.wpn_rtd_img_tk, self.wpn_angles, self.wpn_grip = \
            self.img_mng.pixel_friendly_rotates(self.weapon_image_cv2, selected_px=(13, 54))

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

        self.character_canvas = Canvas(self.gui, width=0, height=0, bg='#AAAAAA')
        self.image_on_canvas = self.character_canvas.create_image(0, 0, anchor="nw", image=self.char_image)

        self.weapon_label = Label(self.gui, text="Preview weapon:")
        self.weapon_image_label = Label(self.gui, image=self.weapon_image)

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

        self.character_canvas.place(x=col_width * 0 + left_pad, y=row_height * 7 + top_pad)

        self.info_label.place(x=col_width * 0 + left_pad, y=row_height * 0 + top_pad)
        self.path_label.place(x=col_width * 1 + left_pad, y=row_height * 0 + top_pad)

        self.select_button.place(x=col_width * 0 + left_pad, y=row_height * 1 + top_pad)
        self.save_points_button.place(x=col_width * 1 + left_pad, y=row_height * 1 + top_pad)
        self.weapon_label.place(x=col_width * 2.5 + left_pad, y=row_height * 1 + top_pad)

        self.grip_pos_label.place(x=col_width * 0 + left_pad, y=row_height * 2 + top_pad)
        self.tip_pos_label.place(x=col_width * 1 + left_pad, y=row_height * 2 + top_pad)
        self.weapon_image_label.place(x=col_width * 3 + left_pad, y=row_height * 2 + top_pad)

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
            self.character_canvas.itemconfigure(self.image_on_canvas, image=new_image)
            self.character_canvas.config(width=new_image.width(), height=new_image.height())
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
            self.character_canvas.delete(self.preview_canvas_grip_indicator)
        mouse = [0, 0]
        mouse[0] = self.mouse_pos_right[0] // scale
        mouse[1] = self.mouse_pos_right[1] // scale
        self.preview_canvas_grip_indicator = self.draw_click_indicator(mouse[0], mouse[1], )
        self.refresh_angle()
        self.mouse_var_right.set("Grip:" + str(mouse))
        self.draw_weapon(self.mouse_pos_right)

    def get_mouse_click_pos_middle(self, event_origin):
        self.mouse_pos_middle[0] = int(event_origin.x)
        self.mouse_pos_middle[1] = int(event_origin.y)
        scale = self.preview_scale_var.get()
        if self.preview_canvas_tip_indicator is not None:
            self.character_canvas.delete(self.preview_canvas_tip_indicator)
        mouse = [0, 0]
        mouse[0] = self.mouse_pos_middle[0] // scale
        mouse[1] = self.mouse_pos_middle[1] // scale
        self.preview_canvas_tip_indicator = self.draw_click_indicator(mouse[0], mouse[1], fill='red')
        self.refresh_angle()
        self.mouse_var_middle.set("Tip:" + str(mouse) + "angle:" + str(self.points_angle)[:5])
        self.draw_weapon(self.mouse_pos_right)

    def draw_click_indicator(self, x, y, fill='white'):
        if self.preview_canvas_line is not None:
            self.character_canvas.delete(self.preview_canvas_line)
        self.preview_canvas_line = self.character_canvas.create_line(self.mouse_pos_middle[0], self.mouse_pos_middle[1],
                                                                     self.mouse_pos_right[0], self.mouse_pos_right[1],
                                                                     dash=(4, 2))
        scale = self.preview_scale_var.get()
        rect = self.character_canvas.create_rectangle(
            (x * scale,
             y * scale,
             x * scale + scale,
             y * scale + scale),
            fill=fill)
        return rect

    def draw_weapon(self, pos: list[int, int], permanent=False):
        if self.preview_canvas_weapon_indicator is not None:
            self.character_canvas.delete(self.preview_canvas_weapon_indicator)
        weapon_x = pos[0] - self.wpn_grip[self.best_suited_img][0]
        weapon_y = pos[1] - self.wpn_grip[self.best_suited_img][1]
        if permanent:
            self.character_canvas.create_image(weapon_x, weapon_y,
                                               anchor="nw",
                                               image=self.wpn_rtd_img_tk[self.best_suited_img])
        else:
            self.preview_canvas_weapon_indicator = self.character_canvas.create_image(weapon_x, weapon_y,
                                                                                      anchor="nw",
                                                                                      image=self.wpn_rtd_img_tk[
                                                                                          self.best_suited_img])

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

    def append_grip_point(self):
        image_width = len(self.image_data[0])
        image_height = len(self.image_data)
        if image_height != image_width:
            frames = image_width // image_height
        else:
            frames = 1
        grip_points = self.mouse_var_right.get().split(":")[1]
        global_x = int(grip_points.replace("[", ""). split(", ")[0])
        global_y = int(grip_points.replace("]", "").split(", ")[1])
        frame = global_x // image_height
        frame_center_x = int(global_x - frame * image_height - (image_width/2) / frames)
        frame_center_y = int(global_y - image_height/2)
        image_index = self.best_suited_img
        output = (frame_center_x, frame_center_y, image_index)
        self.char_grip_list.append(output)
        self.real_points_list.append((global_x, global_y, self.points_angle))
        self.char_grip_list_var.set(str(self.char_grip_list))
        if len(self.char_grip_list) > 1:
            self.draw_trail()
        self.draw_weapon(self.mouse_pos_right, permanent=True)

    def draw_trail(self):
        if len(self.real_points_list) < 4:
            x1 = self.real_points_list[-2][0] - len(self.image_data)*(len(self.real_points_list)-3)
            y1 = self.real_points_list[-2][1]
            a1 = 360 - self.real_points_list[-2][2] + 90
        else:
            x1 = self.real_points_list[-3][0] - len(self.image_data) * (len(self.real_points_list) - 4)
            y1 = self.real_points_list[-3][1]
            a1 = 360 - self.real_points_list[-3][2] + 90

        x2 = self.real_points_list[-1][0] - len(self.image_data)*(len(self.real_points_list)-2)
        y2 = self.real_points_list[-1][1]
        a2 = 360 - self.real_points_list[-1][2] + 90
        size = (len(self.image_data[0]), len(self.image_data))
        point1 = (x1, y1, a1)
        point2 = (x2, y2, a2)
        trail = TG.generate_trail(point1, point2, size, 50, 8)
        self.tk_tails_images.append(ImageTk.PhotoImage(trail))
        # trail.show()
        self.character_canvas.create_image(len(self.image_data)*(len(self.real_points_list)-2), 0,
                                           anchor="nw",
                                           image=self.tk_tails_images[-1])


app = App()
