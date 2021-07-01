import pygame, sys
from random import *

pygame.init()
screen = pygame.display.set_mode([640, 480])
background = pygame.Surface(screen.get_size())
background.fill([255, 255, 255])
img_file = "./bg_img/no.png"
clock = pygame.time.Clock()
delay = 100
interval = 50
pygame.key.set_repeat(delay, interval)
group = pygame.sprite.Group()


# 在一条轴上两点靠近或远离 大于零靠近，不大于零远离
def axis_point_move(before_axis, after_axis, speed_axis, point_move_type=1):
    speed_gap = after_axis - before_axis
    speed_type = speed_axis * speed_gap * point_move_type
    if speed_type < 0:
        speed_axis *= -1
    return speed_axis


# 质点接近或远离 大于零靠近，不大于零远离
def point_center_move(before_point_center, after_point_center, speed, point_move_type=1):
    speed[0] = axis_point_move(before_point_center.centerx, after_point_center.centerx, speed[0], point_move_type)
    speed[1] = axis_point_move(before_point_center.centery, after_point_center.centery, speed[1], point_move_type)
    return speed


class Ball(pygame.sprite.Sprite):
    def __init__(self, image_file, speed, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location
        self.speed = speed

    def set_speed(self, new_speed):
        self.speed = new_speed

    def move(self):
        self.update_speed()
        newpos = self.rect.move(self.speed)
        self.rect = newpos

    # 碰撞边界处理
    def update_speed(self, screen_rect=screen.get_rect()):
        # print(self.rect, screen_rect, self.speed)
        # 发生越界，回归轴中心
        if self.rect.left <= screen_rect.left or self.rect.right >= screen_rect.right:
            self.speed[0] = axis_point_move(self.rect.centerx, screen_rect.centerx, self.speed[0])
        #
        if self.rect.top <= screen_rect.top or self.rect.bottom >= screen_rect.bottom:
            self.speed[1] = axis_point_move(self.rect.centery, screen_rect.centery, self.speed[1])


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


def animate(group):
    screen.fill([255, 255, 255])
    if not held_town:
        my_ball.move()
    #
    for ball in group:
        ball.move()
    for ball in group:
        group.remove(ball)
        collide_ball_list = pygame.sprite.spritecollide(ball, group, False)
        # 与组内球碰撞
        if collide_ball_list:
            if len(collide_ball_list) == 1:
                ball.set_speed(point_center_move(ball.rect, collide_ball_list[0].rect, ball.speed, -1))
            else:
                ball.speed[0] = -ball.speed[0]
                ball.speed[1] = -ball.speed[0]
        # 与点击球碰撞
        if pygame.sprite.collide_circle(ball, my_ball):
            ball.set_speed(point_center_move(ball.rect, my_ball.rect, ball.speed, -1))
            my_ball.set_speed(point_center_move(my_ball.rect, ball.rect, my_ball.speed, -1))
        group.add(ball)
        screen.blit(ball.image, ball.rect)
    #
    screen.blit(my_ball.image, my_ball.rect)
    #
    pygame.display.flip()
    # pygame.time.delay(20)


my_ball = Ball("./bg_img/no.png", [10, 0], [20, 20])
held_town = False
last_hold_down_pos = []
for row in range(0, 2):
    for column in range(0, 2):
        location = [randint(1, screen.get_width()), randint(1, screen.get_height())]
        ball_speed = [choice([-2, 2]), choice([-2, 2])]
        ball = Ball(img_file, ball_speed, location)
        group.add(ball)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                my_ball.rect.top = my_ball.rect.top - 10
            elif event.key == pygame.K_DOWN:
                my_ball.rect.top = my_ball.rect.top + 10
        elif event.type == pygame.MOUSEBUTTONDOWN:
            held_town = True
            mouse_pos = get_mouse_pos(event.pos)
            click_select = False
            # 点中则交换点击球
            for o_ball in group:
                if o_ball.rect.collidepoint(mouse_pos) == 1:
                    group.add(my_ball)
                    my_ball = o_ball
                    group.remove(o_ball)
                    click_select = True
                    break
            # 未选中则定位上一次
            if not click_select:
                my_ball.rect.center = mouse_pos
        elif event.type == pygame.MOUSEBUTTONUP:
            held_town = False
            # 抬起焦点计算速度
            if len(last_hold_down_pos) > 1:
                mouse_pos = get_mouse_pos(event.pos)
                speed = [mouse_pos[0] - last_hold_down_pos[-2][0], mouse_pos[1] - last_hold_down_pos[-2][1]]
                my_ball.set_speed(speed)
                last_hold_down_pos = []
        elif event.type == pygame.MOUSEMOTION:
            # 记录点击
            if held_town:
                mouse_pos = get_mouse_pos(event.pos)
                my_ball.rect.center = mouse_pos
                last_hold_down_pos.append(mouse_pos)
    #
    animate(group)
    clock.tick(50)
