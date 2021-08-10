import pygame, sys, random, time
from pygame.color import THECOLORS
import math
from pygame import gfxdraw

pygame.init()
screen = pygame.display.set_mode([640, 480])
screen.fill([255, 255, 255])
clock = pygame.time.Clock()
delay = 100
interval = 50
pygame.key.set_repeat(delay, interval)
bezier_color = (242, 190, 110)
circle_color = (228, 232, 213)
o_circle_color = (181, 37, 47)


# OverflowError: Python int too large to convert to C long
def convert_C(num):
    if num < 1e-16:
        num = 0
    elif num > 1e+6:
        num = 1e+6
    return math.ceil(num)


def covert_C_list(pos_list):
    covert_list = []
    for pos in pos_list:
        covert_list.append((convert_C(pos[0]), convert_C(pos[1])))
    return covert_list


class Bezier():
    @classmethod
    # step为计算精度，越大 点越密集，图线越精细、计算量越大，默认值为流畅上限
    def bezier(cls, point_list, step=10000):
        pos_list = []
        for i in range(step + 1):
            t = i / step
            pos = None
            if len(point_list) == 3:
                pos = (cls.bezier_2(point_list[0][0], point_list[1][0], point_list[2][0], t),
                       cls.bezier_2(point_list[0][1], point_list[1][1], point_list[2][1], t))
            elif len(point_list) == 4:
                pos = (cls.bezier_3(point_list[0][0], point_list[1][0], point_list[2][0], point_list[3][0], t),
                       cls.bezier_3(point_list[0][1], point_list[1][1], point_list[2][1], point_list[3][1], t))
            if pos:
                pos_list.append(pos)
        return pos_list

    @classmethod
    # 二阶公式
    def bezier_2(cls, point_left, point_control, point_right, t):
        point_left *= ((1 - t) ** 2)
        point_control *= (2 * t * (1 - t))
        point_right *= (t ** 2)
        return point_left + point_control + point_right

    @classmethod
    # 三阶公式
    def bezier_3(cls, point_left, point_control_left, point_control_right, point_right, t):
        b_point_left = point_left * ((1 - t) ** 3)
        b_point_control_left = point_control_left * (3 * t * ((1 - t) ** 2))
        b_point_control_right = point_control_right * (3 * (t ** 2) * (1 - t))
        b_point_right = point_right * (t ** 3)
        return b_point_left + b_point_control_left + b_point_control_right + b_point_right

    @classmethod
    # 官方使用不抗锯齿的绘制完整曲线
    def draw_bezier(cls, surface, point_left, point_control, point_right, m_color=bezier_color, step=10000):
        point_left, point_control, point_right = covert_C_list((point_left, point_control, point_right))
        gfxdraw.bezier(surface, (point_left, point_control, point_right), step, m_color)


# 大量点连成线
def draw_lines(pos_list, m_color=bezier_color):
    if anti_aliasing:
        pygame.draw.aalines(screen, m_color, False, pos_list, 2)
    else:
        pygame.draw.lines(screen, m_color, False, pos_list, 2)


# 两点连成线
def draw_line(pos_list, m_color=bezier_color):
    if anti_aliasing:
        pygame.draw.aaline(screen, m_color, pos_list[0], pos_list[1])
    else:
        pygame.draw.line(screen, m_color, pos_list[0], pos_list[1])


# 填充区域 两个点集
def draw_area(pos_list, symmetry_pos_list, m_color=bezier_color):
    pos_len = len(symmetry_pos_list)
    if len(pos_list) > pos_len:
        pos_len = len(pos_list)
    for i in range(pos_len):
        draw_line((get_pos_by_length(i, pos_list), get_pos_by_length(i, symmetry_pos_list)), m_color)
        # 填充间隙
        if i > 0:
            left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos = covert_C_list(
                (get_pos_by_length(i - 1, pos_list), get_pos_by_length(i - 1, symmetry_pos_list),
                 get_pos_by_length(i, symmetry_pos_list), get_pos_by_length(i, pos_list)))
            gfxdraw.filled_polygon(screen, (left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos)
                                   , m_color)


# 点 依据轴连成横线，行成区域
def draw_area_axis(pos_list, axis_pos=(screen.get_width() / 2, 0), m_color=bezier_color):
    # 轴对称
    symmetry_pos_list = pos_axis_symmetry(pos_list, axis_pos)
    draw_area(pos_list, symmetry_pos_list, m_color)


# 填充区域 单个点集 拆分成两个点集
def draw_area_self(pos_list, divide_progress=0.5, m_color=bezier_color):
    draw_area(pos_list[:int(len(pos_list) * divide_progress)], pos_list[:int(len(pos_list) * (1 - divide_progress)):-1],
              m_color)


def get_pos_by_length(i, pos_list):
    if i >= len(pos_list):
        i = len(pos_list) - 1
    return pos_list[i]


# 画圆
def draw_circle(circle_pos, circle_radius, m_color=bezier_color):
    if anti_aliasing:
        gfxdraw.aacircle(screen, int(circle_pos[0]), int(circle_pos[1]), int(circle_radius), m_color)
    else:
        pygame.draw.circle(screen, m_color, circle_pos, circle_radius)
    # 填充
    # gfxdraw.filled_circle(screen, int(circle_pos[0]), int(circle_pos[1]), int(circle_radius), m_color)


# 画四边形
def draw_box(rect, m_color=bezier_color):
    if anti_aliasing:
        # (left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos)
        gfxdraw.aapolygon(screen, rect, m_color)
    else:
        # 画矩形 [left, top, width, height]
        # pygame.draw.rect(screen, m_color, rect, 3)
        # 画四边形 (left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos)
        gfxdraw.polygon(screen, rect, m_color)
    # 填充
    # gfxdraw.filled_polygon(screen, (left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos), m_color)
    # gfxdraw.box(screen, rect, m_color)


# 填充四边形
def draw_box_area(rect, m_color=bezier_color):
    gfxdraw.filled_polygon(screen, rect, m_color)


# [left, top, width, height] --> (left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos)
def get_box_by_w_h(rect):
    [left, top, width, height] = rect
    left_top_pos = (left, top)
    right_top_pos = (left + width, top)
    left_bottom_pos = (left, top + height)
    right_bottom_pos = (left + width, top + height)
    return (left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos)


# 实心圆点
def draw_point(pos_list, m_color=bezier_color, r_circle=3):
    for pos in pos_list:
        # gfxdraw.pixel(screen, convert_C(pos[0]), convert_C(pos[1]), m_color)
        pos = (convert_C(pos[0]), convert_C(pos[1]))
        r_circle = int(r_circle)
        gfxdraw.filled_circle(screen, pos[0], pos[1], r_circle, m_color)
        draw_circle((pos[0], pos[1]), r_circle, m_color)


# 绘制结束
def submit_draw():
    pygame.time.delay(80)
    pygame.display.flip()


# 转换成窗口内焦点
def get_mouse_pos(mouse_pos):
    mouse_pos_left, mouse_pos_top = mouse_pos
    #
    if mouse_pos_left < screen.get_rect().left:
        mouse_pos_left = screen.get_rect().left
    elif mouse_pos_left > screen.get_rect().right:
        mouse_pos_left = screen.get_rect().right
    #
    if mouse_pos_top < screen.get_rect().top:
        mouse_pos_top = screen.get_rect().top
    elif mouse_pos_top > screen.get_rect().bottom:
        mouse_pos_top = screen.get_rect().bottom
    return (mouse_pos_left, mouse_pos_top)


# 右P2点
def get_right_pos(m_circle_pos, m_circle_radius, angle):
    x = m_circle_pos[0] - m_circle_radius * math.sin(angle)
    y = m_circle_pos[1] + m_circle_radius * math.cos(angle)
    return (x, y)


# 控制点
def get_center_pos(right_pos, angle):
    if angle == 0:
        x = 0
    else:
        x = right_pos[0] - right_pos[1] / math.tan(angle)
    y = 0
    return (x, y)


# 依据进度获取弧度制角度
def get_angle(m_progress):
    return math.pi * m_progress


# 计算比例
def get_progress(m_height, rect_height=screen.get_height()):
    return abs(m_height / rect_height)


# 依据圆心获取贝塞尔关键点
def get_bezier_pos(m_circle_pos, m_circle_radius, m_progress):
    angle = get_angle(m_progress)
    right_pos = get_right_pos(m_circle_pos, m_circle_radius, angle)
    center_pos = get_center_pos(right_pos, angle)
    left_pos = (m_circle_pos[0] * m_progress, 0)
    return left_pos, center_pos, right_pos


# 点 轴对称
def pos_axis_symmetry(pos_list, axis_pos=(screen.get_width() / 2, 0)):
    symmetry_pos_list = []
    if axis_pos[0] == 0:
        axis_index = 1
    else:
        axis_index = 0
    axis_symmetry = axis_pos[axis_index]
    for pos in pos_list:
        dis = axis_symmetry - pos[axis_index]
        if axis_index == 0:
            symmetry_pos_list.append((pos[0] + 2 * dis, pos[1]))
        else:
            symmetry_pos_list.append((pos[0], pos[1] + 2 * dis))
    return symmetry_pos_list


# 自定义
def draw_my_bezier(point_left, point_control, point_right):
    # 计算贝塞尔点
    bezier_pos_list_left = Bezier.bezier((point_left, point_control, point_right), bezier_accuracy)
    # 左左对称
    bezier_pos_list_left_left = pos_axis_symmetry(bezier_pos_list_left, (point_left[0], 0))
    # 轴对称获得右边
    bezier_pos_list_right = pos_axis_symmetry(bezier_pos_list_left)
    bezier_pos_list_right_right = pos_axis_symmetry(bezier_pos_list_left_left)
    # 曲线
    draw_lines(bezier_pos_list_left)
    # draw_lines(bezier_pos_list_left_left)
    draw_lines(bezier_pos_list_right)
    # draw_lines(bezier_pos_list_right_right)
    # 填充
    draw_area_axis(bezier_pos_list_left)
    # 绘制左边关键点
    # draw_point((point_left, point_control, point_right), o_circle_color)


# 通过焦点绘制粘性曲线
def draw_bezier_by_click_pos(mouse_pos):
    screen.fill([255, 255, 255])
    # 拖拽比例
    progress = get_progress(mouse_pos[1] - last_mouse_down_pos[1])
    # 加速粘性效果，并抑制曲线交叉
    if progress < 0.075:
        progress *= 2
    elif progress > 0.65:
        return
    # print(progress)
    # 拖拽比例高度
    circle_pos_height = screen.get_height() * progress / 1.5
    # 相切外圆半径
    out_circle_radius = circle_radius + 6
    # 圆心
    circle_pos = (screen.get_width() / 2, circle_pos_height)
    # 获得左边三个点
    point_left, point_control, point_right = get_bezier_pos(circle_pos, out_circle_radius, progress)

    # 自定义
    draw_my_bezier(point_left, point_control, point_right)
    # 外圆
    draw_circle(circle_pos, out_circle_radius)
    # 内圆
    draw_circle(circle_pos, circle_radius, circle_color)
    # 内圆使用图片
    # screen.blit(image, (circle_pos[0] - circle_radius, circle_pos[1] - circle_radius))

    # 官方 如何填充，振荡
    # 上下对称
    # point_left, point_control, point_right = pos_axis_symmetry((point_left, point_control, point_right),
    #                                                            (0, screen.get_height() / 2))
    # Bezier.draw_bezier(screen, point_left, point_control, point_right, bezier_color, bezier_accuracy)
    # point_left, point_control, point_right = pos_axis_symmetry((point_left, point_control, point_right))
    # Bezier.draw_bezier(screen, point_left, point_control, point_right, bezier_color, bezier_accuracy)
    # (circle_pos,) = pos_axis_symmetry((circle_pos,), (0, screen.get_height() / 2))
    # # 外圆
    # draw_circle(circle_pos, out_circle_radius)
    # # 内圆
    # # draw_circle(circle_pos, circle_radius, circle_color)
    # # 内圆使用图片
    # screen.blit(image, (circle_pos[0] - circle_radius, circle_pos[1] - circle_radius))
    #
    submit_draw()


# 振幅
def setting_vibration_speed(mouse_pos):
    global vibration_speed, last_mouse_down_pos, vibration_angle
    vibration_speed = get_progress(mouse_pos[1] - last_mouse_down_pos[1])
    last_mouse_down_pos = (0, 0)
    vibration_angle = vibration_angle_final


# 光标
last_mouse_down_pos = (0, 0)
# 半径
circle_radius_final = 30
circle_radius = circle_radius_final
# 图片
img_file = "./bg_img/no.png"
image = pygame.image.load(img_file).convert()
width, height = image.get_size()
# 对图片进行缩放
image = pygame.transform.smoothscale(image, (circle_radius * 2, circle_radius * 2))
# 抗锯齿
anti_aliasing = True
# 精度
bezier_accuracy = 500
# 弹跳速度
vibration_speed = 0
vibration_angle_final = math.pi / 2
vibration_angle = math.pi / 2

if __name__ == '__main__':
    held_town = False
    # 清理窗口
    # screen.fill([255, 255, 255])
    # submit_draw()
    # 拉伸操作的观感连贯性
    draw_bezier_by_click_pos((0, 0))
    # 精度高时加上抗锯齿计算过大
    if bezier_accuracy > 9999:
        anti_aliasing = False
    #
    while 1:
        # 清理窗口
        screen.fill([255, 255, 255])
        for event in pygame.event.get():
            # print(event.type)
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                held_town = True
                mouse_pos = get_mouse_pos(event.pos)
                last_mouse_down_pos = mouse_pos
                # submit_draw()
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = get_mouse_pos(event.pos)
                if held_town:
                    held_town = False
                    setting_vibration_speed(mouse_pos)
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = get_mouse_pos(event.pos)
                if held_town:
                    draw_bezier_by_click_pos(mouse_pos)
            # 丢失焦点,有时需要松开鼠标才能触发
            elif event.type == pygame.ACTIVEEVENT:
                # 移出窗口时认为松开鼠标
                if held_town:
                    mouse_pos = (0, screen.get_height())
                    held_town = False
                    setting_vibration_speed(mouse_pos)
        # 震荡曲线趋近于sin曲线
        if not held_town and vibration_speed != 0:
            # 振幅、振角
            vibration_speed_height = screen.get_height() * vibration_speed / 1.5
            vibration_angle += math.pi / 8
            # 振荡损耗
            vibration_speed -= 0.02
            if vibration_angle > math.pi * 6 or vibration_speed < 0:
                vibration_speed = 0
            # 振荡结束隐藏
            #     submit_draw()
            # else:
            #     draw_bezier_by_click_pos((0, vibration_speed_height * math.sin(vibration_angle)))
            # 保留似乎更流畅
            draw_bezier_by_click_pos((0, vibration_speed_height * math.sin(vibration_angle)))
        clock.tick(60)
