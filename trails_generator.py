from PIL import Image, ImageDraw
from math import tan, radians, sin, cos, sqrt


class TrailsGen:
    def __init__(self):
        pass

    @staticmethod
    def get_equations(point1: tuple[int, int, float], point2: tuple[int, int, float]) -> tuple:
        """
        There are some weird, kinda random at first glance minuses, but they are there to compensate fact, that
        y coordinate is 0 on top and max at the bottom of image.
        :param point1:
        :param point2:
        :return:
        """
        x1 = point1[0]
        y1 = -point1[1]
        if 90 <= point1[2] < 270:
            a1 = tan(radians(point1[2]+180))
        elif 270 <= point1[2] < 360:
            a1 = tan(radians(point1[2] + 360))
        else:
            a1 = tan(radians(point1[2]))
        b1 = y1 - a1 * x1
        x2 = point2[0]
        y2 = -point2[1]
        if 90 <= point1[2] < 270:
            a2 = tan(radians(point2[2]+180))
        elif 270 <= point1[2] < 360:
            a2 = tan(radians(point2[2]+360))
        else:
            a2 = tan(radians(point2[2]))
        b2 = y2 - a2 * x2
        return (-a1, -b1,), (-a2, -b2)

    @staticmethod
    def get_intersection(functions: tuple[tuple[float, float], tuple[float, float]]) -> tuple[int, int]:
        a1, b1 = functions[0]
        a2, b2 = functions[1]
        intersection_x = round((b2 - b1) / (a1 - a2))
        intersection_y = round(a1 * intersection_x + b1)
        return intersection_x, intersection_y

    @staticmethod
    def get_points_distance(point1: tuple[int, int], point2: tuple[int, int]) -> float:
        delta_x = point2[0] - point1[0]
        delta_y = point2[1] - point1[1]
        distance = sqrt(delta_x**2 + delta_y**2)
        return distance

    @staticmethod
    def get_polygons(point1: tuple[int, int, float],
                     point2: tuple[int, int, float],
                     sections=4,
                     weapon_length=100) -> list:
        intersection_point = TrailsGen.get_intersection(TrailsGen.get_equations(point1, point2))
        distance1 = TrailsGen.get_points_distance(intersection_point, point1[:2])
        distance2 = TrailsGen.get_points_distance(intersection_point, point2[:2])
        avg_distance = (distance1 + distance2) / 2 + weapon_length / 10
        delta_angle = point2[2] - point1[2]
        points = []
        for i in range(sections+1):
            angle = point1[2] + delta_angle*i/(sections)
            delta_x = avg_distance * cos(radians(angle))
            delta_y = avg_distance * sin(radians(angle))
            delta_x2 = (avg_distance + weapon_length * 0.75) * cos(radians(angle))
            delta_y2 = (avg_distance + weapon_length * 0.75) * sin(radians(angle))
            points.append((round(intersection_point[0] + delta_x), round(intersection_point[1] - delta_y)))
            points.append((round(intersection_point[0] + delta_x2), round(intersection_point[1] - delta_y2)))

        return points

    @staticmethod
    def generate_trail(point1: tuple[int, int, float], point2: tuple[int, int, float], size, weapon_length, sections=4):
        xy = TrailsGen.get_polygons(point1, point2, sections, weapon_length=weapon_length)
        img = Image.new("RGBA", size)
        num_of_poly = (len(xy) // 2) - 1

        print(xy)

        for poly in range(num_of_poly):
            p1, p2, p3, p4 = xy[poly * 2], xy[poly * 2 + 1], xy[poly * 2 + 2], xy[poly * 2 + 3]
            color = (208, 207, 200, round(255 / num_of_poly * (poly + 1)))
            part = ImageDraw.Draw(img, "RGBA")
            part.polygon((p2, p1, p3, p4), fill=color, outline=color)
        return img
