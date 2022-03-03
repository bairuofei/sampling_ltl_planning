import time
import math
import matplotlib.image as img
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.path as mpath
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
from matplotlib.collections import LineCollection
import matplotlib.animation as animation


class Quadcoptor:
    def __init__(self, init_pos=[0, 0, 0], task_wait=[], controller_para=[2, 15], body_color='k', trace_color='b', name='', text_name='Quadrotor', pref=[], suf=[]):
        self.x = init_pos[0]
        self.y = init_pos[1]
        self.theta = init_pos[2]      # radian
        self.radius = 2
        self.body_color = body_color
        self.trace_color = trace_color
        self.robot_task_index = 1
        self.task_wait = task_wait
        self.controller = Controller(
            kp_d=controller_para[0], kp_theta=controller_para[1])

        self.pref = pref
        self.suf = suf
        self.robot_task = self.pref + self.suf

        self.target_x = self.x
        self.target_y = self.y

        self.name = name
        self.text_name = text_name

        self.count = 0
        self.task_complete = False

        self.landing = False
        self.land_cnt = 0

        self.model_scale = 2.5

        self.hover_lin_vel = 20
        self.hover_ang_vel = 7

        Path = mpath.Path
        self.drone_outline = [
            (Path.MOVETO, [0, 0]),
            (Path.LINETO, [1, 0.7]),
            (Path.LINETO, [2.5, -0.3]),
            (Path.LINETO, [3, 0.2]),
            (Path.LINETO, [1, 1.7]),
            (Path.LINETO, [0, 2.7]),
            (Path.LINETO, [-1, 1.7]),
            (Path.LINETO, [-3, 0.2]),
            (Path.LINETO, [-2.5, -0.3]),
            (Path.LINETO, [-1, 0.7]),
            (Path.CLOSEPOLY, [0, 0])]

    def set_target(self, region_list):
        region_name = self.robot_task[self.robot_task_index]
        self.target_x, self.target_y = region_list[region_index[region_name]
                                                   ]['region_center']
        self.robot_task_index += 1

    def get_current_pos(self):
        return self.x, self.y, self.theta

    def modify_pose(self, region_list, is_task_complete):
        if self.controller.reach_target:  # 刚开始由于起点和终点相同，因此立即进入这个部分
            if self.robot_task_index == len(self.robot_task):
                self.robot_task_index = len(self.pref)
                return
                # if not self.landing:
                #     if self.land_cnt >= 100:  # 结束任务之后的循环时间
                #         self.landing = True
                #     self.land_cnt += 1
                #     lin_vel = self.hover_lin_vel
                #     ang_vel = self.hover_ang_vel
                # else:
                #     lin_vel = 0
                #     ang_vel = 0
            else:
                self.modify_robot_state(is_task_complete)
                if self.check_wait_set(is_task_complete):
                    # region_name = self.robot_task[self.robot_task_index-1]
                    self.set_target(region_list)
                    self.controller.reach_target = False
                    return
                else:
                    lin_vel = self.hover_lin_vel
                    ang_vel = self.hover_ang_vel
        else:
            [lin_vel, ang_vel] = self.controller.control_input(self)
        self.last_x = self.x
        self.last_y = self.y
        self.x += dt*lin_vel*math.cos(self.theta)
        self.y += dt*lin_vel*math.sin(self.theta)
        raw_theta = self.theta + dt*ang_vel
        self.set_theta(raw_theta)

    def modify_motor_collection(self):
        codes, verts = zip(*self.drone_outline)
        path = mpath.Path(np.array(verts)*self.model_scale, codes)
        path = path.transformed(mpl.transforms.Affine2D(
        ).rotate_deg(-90+math.degrees(self.theta)))
        path.vertices += np.array([self.x, self.y])
        drone_path_patch = mpatches.PathPatch(path)
        drone_patches = []
        drone_patches.append(drone_path_patch)
        motor_collection = PatchCollection(
            drone_patches, match_original=False, facecolor=self.body_color, alpha=0.9)
        return motor_collection

    def modify_trace(self, ax):
        trace_line_x = [self.last_x, self.x]
        trace_line_y = [self.last_y, self.y]
        line = mlines.Line2D(trace_line_x, trace_line_y,
                             lw=2, alpha=0.2, color=self.trace_color)
        ax.add_line(line)

    def modify_collection(self, ax):
        ax.add_collection(self.modify_motor_collection())

    def modify_robot_label(self, ax):
        ax.text(x=self.x, y=self.y+2*self.radius,
                s=self.text_name, color="white", fontsize=10)

    def modify_robot_state(self, is_task_complete):
        if not is_task_complete[self.name][self.robot_task_index-1]:
            is_task_complete[self.name][self.robot_task_index-1] = True

    def check_wait_set(self, is_task_complete):
        try:
            for wait_robot in self.task_wait[self.robot_task_index-1]:
                if not is_task_complete[wait_robot][self.robot_task_index-1]:
                    return False
        except IndexError:
            print('haha')
        return True

    def set_theta(self, raw_theta):
        self.theta = raw_theta
        if self.theta < -1*math.pi:
            self.theta += 2*math.pi
        elif self.theta > math.pi:
            self.theta -= 2*math.pi


class Controller():
    def __init__(self, kp_d=1.3, kp_theta=2.5, ki_d=0.6, dist_tolerance=0.5, theta_tolerance=math.pi/18):
        self.kp_d = kp_d
        self.kp_theta = kp_theta
        self.ki_d = ki_d
        self.dist_tolerance = dist_tolerance    # 到达目标点的允许误差，防止震荡
        self.theta_tolerance = theta_tolerance

        self.dist_integral = 0
        self.dist_integral_lim = 30  # 控制积分误差累积量的大小
        self.lin_vel_lim = 90        # 速度控制的上限

        self.reach_target = False

    def compute_dist(self, current_pos, target_pos):
        dist = math.sqrt((current_pos[0]-target_pos[0]) ** 2 +
                         (current_pos[1]-target_pos[1]) ** 2)
        if dist <= self.dist_tolerance:
            dist = 0
            self.dist_integral = 0
            self.reach_target = True
        else:
            self.dist_integral += dist
            if self.dist_integral > self.dist_integral_lim:
                self.dist_integral = self.dist_integral_lim
        return dist

    def compute_angle_diff(self, robot_direction, target_direction):
        angle_diff = target_direction-robot_direction
        if angle_diff < -1*math.pi:
            angle_diff += 2*math.pi
        elif angle_diff > math.pi:
            angle_diff -= 2*math.pi
        return angle_diff

    def control_input(self, robot):
        current_pos = [robot.x, robot.y]
        target_pos = [robot.target_x, robot.target_y]
        dist = self.compute_dist(current_pos, target_pos)
        # math.atan 由tan的值得到相应的弧度
        # math..atan2 由y,x得到相应的弧度
        target_direction = math.atan2(target_pos[1]-current_pos[1],
                                      target_pos[0]-current_pos[0])
        angle_diff = self.compute_angle_diff(robot.theta, target_direction)

        lin_vel = self.kp_d*dist+self.ki_d*self.dist_integral
        if lin_vel > self.lin_vel_lim:
            lin_vel = self.lin_vel_lim
        return lin_vel, self.kp_theta*angle_diff


class Environment():
    def __init__(self, region_list, range=[(0, 200), (0, 200)]):
        # region_list由多个list组成，每个list组成[形状，中心坐标，参数list，背景色]
        self.x_range = range[0]
        self.y_range = range[1]
        self.region_list = region_list

    def get_region_collection(self, ax):
        region_patches = []
        for region in region_list:  # return a dict
            if region['region_type'] == 1:
                one_region_patch = mpatches.Circle(
                    region['region_center'], radius=region['region_para'][0], facecolor=region['region_color'])

            elif region['region_type'] == 2:
                xy = [region['region_center'][0]-region['region_para'][0]/2,
                      region['region_center'][1]-region['region_para'][1]/2]
                one_region_patch = mpatches.Rectangle(
                    xy=xy, width=region['region_para'][0], height=region['region_para'][1], facecolor=region['region_color'])
            if region['region_name'] == 'start':
                s = 'Mobile Patrol Car'
                ax.text(x=region['region_center'][0]-7, y=region['region_center']
                        [1]-10, s=s, fontsize=10)
            elif region['region_name'][0] != "v" and region['region_name'] != "end":
                s = 'Electric Tower '+region['region_name'].upper()
                ax.text(x=region['region_center'][0]-7, y=region['region_center']
                        [1]-10, s=s, fontsize=6)
            region_patches.append(one_region_patch)

        region_collection = PatchCollection(
            region_patches, match_original=True, edgecolors='none', alpha=0.1)
        return region_collection

    def modify_region_collection(self, ax):
        ax.add_collection(self.get_region_collection(ax))


# init函数会被执行两次


def init():
    for robot in robot_set:
        robot.modify_collection(ax)
    return ax.collections


def animate(i):
    if i > 20:  # 80
        print(i)
        del ax.collections[:]
        # if len(ax.texts) > len(region_list):
        if len(ax.texts) > 8:
            del ax.texts[8:]
        for robot in robot_set:
            robot.modify_pose(region_list, is_task_complete)
            robot.modify_trace(ax)
            robot.modify_collection(ax)
            robot.modify_robot_label(ax)
        if len(ax.lines) > 160:  # 600
            del ax.lines[0:10]
    return ax.collections+ax.lines+ax.texts


if __name__ == '__main__':
    dt = 0.02

    # region_type：1：circle, para: [radius];
    #              2: rectangle, para: [width,height]
    region_list = [{'region_name': 'pg', 'region_type': 1,
                    'region_center': [35, 45], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'j', 'region_type': 1,
                    'region_center': [109, 36], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'n', 'region_type': 1,
                    'region_center': [148, 47], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'gz', 'region_type': 1,
                    'region_center': [48, 101], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'g', 'region_type': 1,
                    'region_center': [35, 136], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'z', 'region_type': 1,
                    'region_center': [24, 170], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 's', 'region_type': 1,
                    'region_center': [89, 170], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'k', 'region_type': 1,
                    'region_center': [163, 173], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'l', 'region_type': 1,
                    'region_center': [175, 116], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'y', 'region_type': 1,
                    'region_center': [132, 140], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'm', 'region_type': 1,
                    'region_center': [145, 79], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'h', 'region_type': 1,
                    'region_center': [178, 89], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'r', 'region_type': 1,
                    'region_center': [92, 127], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'b', 'region_type': 1,
                    'region_center': [78, 157], 'region_para': [0.01], 'region_color': 'b'},
                   {'region_name': 'p', 'region_type': 1,
                    'region_center': [85, 97], 'region_para': [0.01], 'region_color': 'b'}]

    tower_set = {}
    # tower_set = {'pg','j','n','gz','g','z','s', 'k', 'l','y', 'm','h', 'r', 'b','p'}
    region_index = {}
    for i, item in enumerate(region_list):
        region_index[item["region_name"]] = i

    # battle_environment = Environment(region_list)

    # task_set = {'robot1': [['j', 'n', 'n', 'm', 'm', 'j', 'm', 'h', 'm', 'm', 'm', 'j', 'pg', 'j', 'j', 'j'], ['n', 'm', 'h', 'h', 'm', 'j']],
    #             'robot2': [['j', 'pg', 'gz', 'g', 'gz', 'pg', 'j', 'm', 'j', 'pg', 'pg', 'gz', 'g', 'b', 'g', 'g'], ['z', 'z', 'z', 'g', 'b', 'g']],
    #             'robot3': [['j', 'j', 'j', 'j', 'j', 'j', 'n', 'j', 'm', 'j', 'j', 'j', 'j', 'pg', 'j', 'j'], ['pg', 'j', 'n', 'n', 'j', 'j']],
    #             'robot4': [['j', 'm', 'p', 'p', 'm', 'j', 'm', 'm', 'n', 'j', 'pg', 'pg', 'gz', 'g', 'z', 'z'], ['z', 'z', 'g', 'g', 'g', 'z']],
    #             'robot5': [['j', 'n', 'j', 'pg', 'pg', 'j', 'm', 'j', 'j', 'm', 'n', 'n', 'j', 'j', 'pg', 'pg'], ['j', 'j', 'j', 'pg', 'pg', 'pg']]}
    # task_set = {"robot1": [['j', 'j', 'pg', 'pg', 'pg', 'gz', 'g', 'gz', 'g', 'gz', 'gz', 'g', 'b', 'g', 'g'], ['z', 'g', 'g', 'gz', 'g', 'b', 'g']],
    #             "robot2": [['j', 'm', 'n', 'm', 'n', 'j', 'm', 'j', 'pg', 'pg', 'j', 'pg', 'pg', 'pg', 'pg'], ['j', 'm', 'n', 'm', 'm', 'j', 'pg']],
    #             "robot3": [['j', 'pg', 'pg', 'gz', 'g', 'gz', 'pg', 'j', 'm', 'h', 'm', 'j', 'j', 'm', 'm'], ['h', 'h', 'l', 'h', 'm', 'j', 'm']],
    #             "robot4": [['j', 'm', 'm', 'p', 'm', 'h', 'm', 'm', 'j', 'n', 'n', 'n', 'n', 'm', 'm'], ['m', 'h', 'm', 'h', 'm', 'm', 'm']],
    #             "robot5": [['j', 'j', 'j', 'pg', 'gz', 'g', 'g', 'b', 'g', 'z', 'g', 'gz', 'gz', 'g', 'g'], ['gz', 'p', 'p', 'gz', 'gz', 'gz', 'g']]}
    # "ltl_task":"([]<> e_g) && ([]<> e_pg) && ([]<> e_n) && (<> e_h) && (<> e_b) && ([](! e_p)) && (<> f_pg) && (<> f_g) && (<> f_n) && (!f_pg U e_pg) && (!f_g U e_g) && (!f_n U e_n)",
    # task_set = {"robot1": [['j', 'n', 'm', 'h', 'l', 'h', 'h', 'm', 'j', 'j', 'n', 'n', 'n', 'm', 'j', 'pg', 'pg'], ['pg', 'pg']],
    #             "robot2": [['j', 'j', 'j', 'n', 'j', 'pg', 'pg', 'gz', 'gz', 'g', 'b', 'g', 'gz', 'gz', 'gz', 'g', 'g'], ['g', 'g']],
    #             "robot3": [['j', 'pg', 'pg', 'j', 'j', 'n', 'm', 'n', 'j', 'pg', 'j', 'm', 'n', 'n', 'n', 'm', 'm'], ['n', 'm']],
    #             "robot4": [['j', 'pg', 'j', 'm', 'm', 'p', 'r', 'p', 'p', 'p', 'r', 'r', 'p', 'r', 'r', 'p', 'p'], ['p', 'p']],
    #             "robot5": [['j', 'n', 'm', 'm', 'p', 'p', 'gz', 'pg', 'gz', 'g', 'gz', 'g', 'gz', 'pg', 'pg', 'pg', 'pg'], ['pg', 'pg']]}
    # ltl task: ([]<> e_g) && ([]<> e_pg) && ([]<> e_n) && ([]<> e_h) && ([]<> e_b) && ([](! e_p)) && (<> f_pg) && (<> f_g) && (<> f_n) && (!f_pg U e_pg) && (!f_g U e_g) && (!f_n U e_n)
    # task_set = {"robot1": [['j', 'n', 'j', 'm', 'm', 'n', 'n', 'j', 'n', 'j', 'm', 'm', 'h', 'm', 'm', 'm'], ['h', 'h', 'l', 'l', 'h', 'l', 'l', 'h', 'm', 'm']],
    #             "robot2": [['j', 'm', 'm', 'm', 'm', 'j', 'm', 'j', 'pg', 'gz', 'g', 'b', 'b', 'b', 's', 's'], ['s', 'b', 'g', 'g', 'gz', 'g', 'b', 's', 'b', 's']],
    #             "robot3": [['j', 'n', 'j', 'pg', 'gz', 'gz', 'g', 'gz', 'pg', 'pg', 'j', 'n', 'j', 'm', 'n', 'n'], ['j', 'n', 'm', 'j', 'pg', 'pg', 'j', 'n', 'm', 'n']]}
    task_set = {"robot1": [['j', 'm', 'p', 'gz', 'g', 'z', 'g', 'gz', 'p', 'r', 'y', 'k', 'y', 'l', 'y'], ['r', 'p', 'gz', 'g', 'z', 'g', 'gz', 'p', 'r', 'y', 'k', 'y', 'l', 'y']],
                "robot2": [['j', 'm', 'p', 'r', 'y', 's', 'y', 'r', 'p', 'gz', 'p', 'r', 'y', 'r'], ['p', 'm', 'p', 'r', 'y', 's', 'y', 'r', 'p', 'gz', 'p', 'r', 'y', 'r']],
                "robot3": [['j', 'm', 'p', 'r', 'y', 'k', 'y', 's', 'y', 'l', 'y', 'r', 'p', 'r'], ['y', 'k', 'y', 's', 'y', 'l', 'y', 'r', 'p', 'r']],
                "robot4": [['j', 'm', 'p', 'gz', 'g', 'z', 'g', 'gz', 'p', 'm', 'p', 'r', 'y', 'l', 'y'], ['r', 'p', 'gz', 'g', 'z', 'g', 'gz', 'p', 'm', 'p', 'r', 'y', 'l', 'y']],

                "robot5": [['j', 'pg', 'gz', 'g', 'gz', 'pg', 'gz', 'g', 'b', 's', 'y', 'l', 'h', 'm', 'n', 'm'], ['h', 'l', 'y', 's', 'b', 'g', 'gz', 'pg', 'gz', 'g', 'b', 's', 'y', 'l', 'h', 'm', 'n', 'm']],
                "robot6": [['j', 'pg', 'j', 'n', 'm', 'h', 'l', 'y', 's', 'b', 'g', 'gz'], ['pg', 'j', 'n', 'm', 'h', 'l', 'y', 's', 'b', 'g', 'gz']],
                "robot7": [['j', 'pg', 'gz', 'g', 'b', 'g'], ['b', 'g']],

                "robot8": [['j', 'm', 'h', 'h', 'h', 'h', 'h', 'h'], ['h', 'h', 'm', 'n']],
                "robot9": [['j', 'j', 'm', 'p', 'gz', 'g', 'b', 'g'], ['b', 'g', 'b', 'g']],
                "robot10": [['j', 'j', 'pg', 'j', 'n', 'j'], ['pg', 'j', 'n', 'j']],
                "robot11": [['j', 'j', 'm', 'h', 'l', 'y', 's', 'b', 's', 'y', 'l', 'h', 'm', 'n', 'm'], ['h', 'l', 'y', 's', 'b', 's', 'y', 'l', 'h', 'm', 'n', 'm']]}

    is_task_complete = {}
    for key, value in task_set.items():
        is_task_complete[key] = [False for _ in range(
            len(value[0]))] + [False for _ in range(len(value[1]))]

    task_wait_set = {}
    for key, value in task_set.items():
        task_wait_set[key] = [[] for _ in range(len(value[0]) + len(value[1]))]

    for key in ["robot9", "robot10", "robot11"]:
        for i in range(3):
            task_wait_set[key][i].append("robot8")

    robot_set = []
    color = ["lime", "red", "deeppink"]
    color_assign = [1, 1, 1, 1, 0, 0, 0, 0, 2, 2, 2]
    for i in range(11):
        robot_str = "robot" + str(i+1)
        col = color[color_assign[i]]
        robot = Quadcoptor(init_pos=region_list[region_index['j']]['region_center']+[0],
                           task_wait=task_wait_set[robot_str],
                           body_color=col,
                           trace_color=col,
                           name=robot_str,
                           text_name='Q' + str(i+1),
                           pref=task_set[robot_str][0],
                           suf=task_set[robot_str][1])
        robot_set.append(robot)

    fig, ax = plt.subplots()
    ax.set_xlim([0, 200])
    ax.set_ylim([0, 200])
    ax.axis('equal')
#    ax.set_xticks([])
#    ax.set_yticks([])
    ax.axis('off')

#    bgimg = img.imread("./background3.png")
    bgimg = img.imread("./env2.png")
    # 图片选自网络https://m.ruan8.com/gonglue/22892.html
    # fig.figimage(bgimg, xo=100, yo=100, alpha=0.1, origin='upper',
    #              resize=True)
    ax.imshow(bgimg, alpha=1,
              extent=[0, 200, 0, 200])
    # pltfig(fig)

    # save_count代表视频存储的frame数  save_count=1400
    ani = animation.FuncAnimation(
        fig, animate, init_func=init, interval=30, blit=True)
    # ani.save('5-sim.gif', fps=100, writer='imagemagick')  # , fps=100
    # ani.save('robot_navigation.mp4', fps=60, extra_args=['-vcodec', 'libx264'])
    plt.show()
