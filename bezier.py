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
    def bezier(cls, point_left, point_control, point_right, step=10000):
        pos_list = []
        for i in range(step + 1):
            t = i / step
            pos = (cls.bezier_2(point_left[0], point_control[0], point_right[0], t),
                   cls.bezier_2(point_left[1], point_control[1], point_right[1], t))
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


# 点 连成竖线，行成区域
def draw_v_area(pos_list, m_color=bezier_color):
    for pos in pos_list:
        draw_line(((pos[0], 0), pos), m_color)


# 点 依据轴连成横线，行成区域
def draw_h_area(pos_list, axis_pos=(screen.get_width() / 2, 0), m_color=bezier_color):
    # 轴对称
    symmetry_pos_list = pos_axis_symmetry(pos_list, axis_pos)
    for i in range(len(symmetry_pos_list)):
        draw_line((pos_list[i], symmetry_pos_list[i]), m_color)
        # 填充间隙
        if i > 0:
            left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos = covert_C_list(
                (pos_list[i - 1], symmetry_pos_list[i - 1], symmetry_pos_list[i], pos_list[i]))
            gfxdraw.filled_polygon(screen, (left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos)
                                   , m_color)


# 画圆
def draw_circle(circle_pos, circle_radius, m_color=bezier_color):
    if anti_aliasing:
        gfxdraw.aacircle(screen, int(circle_pos[0]), int(circle_pos[1]), int(circle_radius), m_color)
    else:
        pygame.draw.circle(screen, m_color, circle_pos, circle_radius)
    # 填充
    gfxdraw.filled_circle(screen, int(circle_pos[0]), int(circle_pos[1]), int(circle_radius), m_color)


# 画矩形
def draw_box(rect, m_color=bezier_color):
    [left, top, width, height] = rect
    left_top_pos = (left, top)
    right_top_pos = (left + width, top)
    left_bottom_pos = (left, top + height)
    right_bottom_pos = (left + width, top + height)
    if anti_aliasing:
        gfxdraw.aapolygon(screen, (left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos), m_color)
    else:
        pygame.draw.rect(screen, m_color, [left, top, width, height], 3)
        # gfxdraw.polygon(screen, (left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos), m_color)
    # 填充
    # gfxdraw.filled_polygon(screen, (left_top_pos, right_top_pos, right_bottom_pos, left_bottom_pos), m_color)
    # gfxdraw.box(screen, rect, m_color)


# 实心圆点
def draw_point(pos_list, m_color=bezier_color):
    for pos in pos_list:
        # gfxdraw.pixel(screen, convert_C(pos[0]), convert_C(pos[1]), m_color)
        gfxdraw.filled_circle(screen, convert_C(pos[0]), convert_C(pos[1]), 3, m_color)


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
    bezier_pos_list_left = Bezier.bezier(point_left, point_control, point_right, bezier_accuracy)
    # 轴对称获得右边
    bezier_pos_list_right = pos_axis_symmetry(bezier_pos_list_left)
    # 曲线
    draw_lines(bezier_pos_list_left)
    draw_lines(bezier_pos_list_right)
    # 填充
    draw_h_area(bezier_pos_list_left)
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
    point_left, point_control, point_right = pos_axis_symmetry((point_left, point_control, point_right),
                                                               (0, screen.get_height() / 2))
    Bezier.draw_bezier(screen, point_left, point_control, point_right, bezier_color, bezier_accuracy)
    point_left, point_control, point_right = pos_axis_symmetry((point_left, point_control, point_right))
    Bezier.draw_bezier(screen, point_left, point_control, point_right, bezier_color, bezier_accuracy)
    (circle_pos,) = pos_axis_symmetry((circle_pos,), (0, screen.get_height() / 2))
    # 外圆
    draw_circle(circle_pos, out_circle_radius)
    # 内圆
    # draw_circle(circle_pos, circle_radius, circle_color)
    # 内圆使用图片
    screen.blit(image, (circle_pos[0] - circle_radius, circle_pos[1] - circle_radius))
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
image = pygame.image.load(img_file)
width, height = image.get_size()
# 对图片进行缩放
image = pygame.transform.smoothscale(image, (circle_radius * 2, circle_radius * 2))
# 抗锯齿
anti_aliasing = True
# 精度
bezier_accuracy = 100
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
                submit_draw()
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
