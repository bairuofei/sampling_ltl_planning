import time
import math
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
    def __init__(self, init_pos=[0, 0, 0], robot_task=[], task_wait=[], controller_para=[2, 15], body_color='k', trace_color='b', name='', text_name=''):
        self.x = init_pos[0]
        self.y = init_pos[1]
        self.theta = init_pos[2]      # radian
        self.radius = 2
        self.body_color = body_color
        self.trace_color = trace_color
        self.robot_task = robot_task
        self.robot_task_index = 1
        self.task_wait = task_wait
        self.controller = Controller(
            kp_d=controller_para[0], kp_theta=controller_para[1])

        self.target_x = self.x
        self.target_y = self.y

        self.name = name
        self.text_name = text_name

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
        self.model_scale = 2.5

        self.hover_lin_vel = 20
        self.hover_ang_vel = 5

    def set_target(self, region_list):
        region_name = self.robot_task[self.robot_task_index]
        self.target_x, self.target_y = region_list[region_index[region_name]
                                                   ]['region_center']
        self.robot_task_index += 1

    def get_current_pos(self):
        return self.x, self.y, self.theta

    def modify_pose(self, region_list, is_task_complete):
        if self.controller.reach_target:  # 刚开始由于起点和终点相同，因此立即进入这个部分
            self.modify_robot_state(is_task_complete)
            if self.robot_task_index == len(self.robot_task):
                lin_vel = self.hover_lin_vel
                ang_vel = self.hover_ang_vel
            else:
                if self.check_wait_set(is_task_complete):
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
            drone_patches, match_original=False, facecolor=self.body_color, alpha=0.8)
        return motor_collection

    def modify_trace(self, ax):
        trace_line_x = [self.last_x, self.x]
        trace_line_y = [self.last_y, self.y]
        line = mlines.Line2D(trace_line_x, trace_line_y,
                             lw=1.5, alpha=0.1, color=self.trace_color)
        ax.add_line(line)

    def modify_collection(self, ax):
        ax.add_collection(self.modify_motor_collection())
        # ax.add_collection(self.modify_arm_collection())

    def modify_robot_label(self, ax):
        ax.text(x=self.x, y=self.y+2*self.radius, s=self.text_name, fontsize=6)

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
    def __init__(self, kp_d=1, kp_theta=1, ki_d=0.6, dist_tolerance=3, theta_tolerance=math.pi/18):
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
    def __init__(self, region_list, range=[(0, 100), (0, 100)]):
        # region_list由多个list组成，每个list组成[形状，中心坐标，参数list，背景色]
        self.x_range = range[0]
        self.y_range = range[1]
        self.region_list = region_list

        Path = mpath.Path
        self.rader_path = [(Path.MOVETO, [-0.1, 0]),
                           (Path.CURVE4, [-0.5, -0.5]),
                           (Path.CURVE4, [-2, 0]),
                           (Path.CURVE4, [-2.5, 0.8]),
                           (Path.LINETO, [1.5, 3]),
                           (Path.CURVE4, [1.5, 2]),
                           (Path.CURVE4, [1, 0.5]),
                           (Path.CURVE4, [0.1, 0]),
                           (Path.LINETO, [1, -1]),
                           (Path.LINETO, [-1, -1]),
                           (Path.CLOSEPOLY, [0.1, 0])]
        self.command_path = [(Path.MOVETO, [0, 1]),
                             (Path.LINETO, [1.5, 0]),
                             (Path.LINETO, [1.5, -1]),
                             (Path.LINETO, [-1.5, -1]),
                             (Path.LINETO, [-1.5, 0]),
                             (Path.CLOSEPOLY, [0, 1])]
        self.missile_path = [(Path.MOVETO, [1, 0]),
                             (Path.LINETO, [-2, 1.5]),
                             (Path.CURVE4, [-2, 1.6]),
                             (Path.CURVE4, [-1.85, 1.75]),
                             (Path.CURVE4, [-1.75, 1.75]),
                             (Path.LINETO, [2, 0]),
                             (Path.LINETO, [1.75, -0.25]),
                             (Path.LINETO, [1.75, -0.75]),
                             (Path.LINETO, [1.5, -0.75]),
                             (Path.CURVE4, [1.5, -1.25]),
                             (Path.CURVE4, [0.75, -1.25]),
                             (Path.CURVE4, [0.75, -0.75]),

                             (Path.LINETO, [-0.5, -0.75]),
                             (Path.CURVE4, [-0.5, -1.25]),
                             (Path.CURVE4, [-1.25, -1.25]),
                             (Path.CURVE4, [-1.25, -0.75]),

                             (Path.LINETO, [-1.5, -0.75]),
                             (Path.LINETO, [-1.5, 0]),
                             (Path.LINETO, [-1.25, 0.5]),
                             (Path.LINETO, [-0.75, 0.5]),
                             (Path.LINETO, [-0.75, 0]),
                             (Path.CLOSEPOLY, [1, 0])]

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
            elif region['region_type'] == 3:
                codes, verts = zip(*self.rader_path)
                path = mpath.Path(np.array(verts)*6, codes)
                path.vertices += np.array(region['region_center'])
                one_region_patch = mpatches.PathPatch(
                    path, facecolor=region['region_color'])
            elif region['region_type'] == 4:
                codes, verts = zip(*self.command_path)
                path = mpath.Path(np.array(verts)*8, codes)
                path.vertices += np.array(region['region_center'])
                one_region_patch = mpatches.PathPatch(
                    path, facecolor=region['region_color'])
            elif region['region_type'] == 5:
                codes, verts = zip(*self.missile_path)
                path = mpath.Path(np.array(verts)*6.5, codes)
                path.vertices += np.array(region['region_center'])
                one_region_patch = mpatches.PathPatch(
                    path, facecolor=region['region_color'])

            ax.text(x=region['region_center'][0]-8, y=region['region_center']
                    [1]-15, s=region['region'], fontsize=6)
            region_patches.append(one_region_patch)

        region_collection = PatchCollection(
            region_patches, match_original=True, edgecolors='none', alpha=0.5)
        return region_collection

    def modify_region_collection(self, ax):
        ax.add_collection(self.get_region_collection(ax))


# init函数会被执行两次


def init():
    battle_environment.modify_region_collection(ax)
    for robot in robot_set:
        robot.modify_collection(ax)
        robot.modify_collection(ax)
    return ax.collections


def animate(i):
    print(i)
    if i > 80:
        del ax.collections[1:]
        if len(ax.texts) > len(region_list):
            del ax.texts[len(region_list):]
        for robot in robot_set:
            robot.modify_pose(region_list, is_task_complete)
            robot.modify_collection(ax)
            robot.modify_trace(ax)
            robot.modify_robot_label(ax)
        if len(ax.lines) > 1200:
            del ax.lines[0:10]
    return ax.collections+ax.lines+ax.texts


if __name__ == '__main__':
    dt = 0.01

    # region_type：1：circle, para: [radius];
    #              2: rectangle, para: [width,height]
    region_list = [{'region_name': 'u1', 'region_type': 1, 'region': 'Data Upload',
                    'region_center': [15, 130], 'region_para': [10], 'region_color': 'c'},
                   {'region_name': 's1', 'region_type': 2, 'region': 'Airport',
                    'region_center': [15, 70], 'region_para': [15, 15], 'region_color': 'lightblue'},
                   {'region_name': 'z1', 'region_type': 5, 'region': 'Enemy Fire 1',
                    'region_center': [75, 140], 'region_para': [15, 15], 'region_color': 'r'},
                   {'region_name': 'z2', 'region_type': 5, 'region': 'Enemy Fire 2',
                    'region_center': [75, 70], 'region_para': [15, 15], 'region_color': 'r'},
                   {'region_name': 'l1', 'region_type': 3, 'region': 'Enemy Radar1',
                    'region_center': [135, 170], 'region_para': [15], 'region_color': 'navy'},
                   {'region_name': 'l2', 'region_type': 3, 'region': 'Enemy Radar2',
                    'region_center': [115, 100], 'region_para': [15], 'region_color': 'navy'},
                   {'region_name': 'l3', 'region_type': 3, 'region': 'Enemy Radar3',
                    'region_center': [135, 30], 'region_para': [15], 'region_color': 'navy'},
                   {'region_name': 'c1', 'region_type': 4, 'region': 'Enemy Command',
                    'region_center': [190, 100], 'region_para': [20, 20], 'region_color': 'darkgreen'}]

    region_index = {'u1': 0, 's1': 1, 'z1': 2,
                    'z2': 3, 'l1': 4, 'l2': 5, 'l3': 6, 'c1': 7}

    battle_environment = Environment(region_list, range=[(0, 200), (0, 200)])

    task_set = {'robot1': ['s1', 'l1', 'l2', 'l3', 'c1', 'l1', 'u1'],
                'robot2': ['s1', 's1', 's1', 's1', 's1', 's1', 's1', 'l1'],
                'robot3': ['s1', 's1', 's1', 's1', 's1', 's1', 's1', 'l2'],
                'robot4': ['s1', 's1', 's1', 's1', 's1', 's1', 's1', 'l3'],
                'robot5': ['s1', 's1', 's1', 's1', 's1', 's1', 's1', 's1', 'z1', 'z2', 'l1', 'l2', 'l3', 'c1', 'l2', 'z1', 'u1', 's1']}

    is_task_complete = {}
    for robot_name in task_set.keys():
        is_task_complete[robot_name] = []
        for task in task_set[robot_name]:
            is_task_complete[robot_name].append(False)

    # task_wait_set = {'robot1': [['robot2', 'robot3'], []],
    #                  'robot2': [],
    #                  'robot3': []}

    task_wait_set = {}
    for robot_name in task_set.keys():
        task_wait_set[robot_name] = []
        for i in range(len(task_set[robot_name])):
            wait_list = []
            for potienal_wait_robot in task_set.keys():
                if i < len(task_set[potienal_wait_robot]):
                    wait_list.append(potienal_wait_robot)
            wait_list.remove(robot_name)
            task_wait_set[robot_name].append(wait_list)

    robot1 = Quadcoptor(init_pos=region_list[region_index['s1']]['region_center']+[0],
                        robot_task=task_set['robot1'], task_wait=task_wait_set['robot1'],
                        body_color='g', trace_color='g', name='robot1', text_name='R-drone1')
    robot2 = Quadcoptor(init_pos=region_list[region_index['s1']]['region_center']+[0],
                        robot_task=task_set['robot2'], task_wait=task_wait_set['robot2'],
                        body_color='m', trace_color='m', name='robot2', text_name='E-drone1')
    robot3 = Quadcoptor(init_pos=region_list[region_index['s1']]['region_center']+[0],
                        robot_task=task_set['robot3'], task_wait=task_wait_set['robot3'],
                        body_color='m', trace_color='m', name='robot3', text_name='E-drone2')
    robot4 = Quadcoptor(init_pos=region_list[region_index['s1']]['region_center']+[0],
                        robot_task=task_set['robot4'], task_wait=task_wait_set['robot4'],
                        body_color='m', trace_color='m', name='robot4', text_name='E-drone3')
    robot5 = Quadcoptor(init_pos=region_list[region_index['s1']]['region_center']+[0],
                        robot_task=task_set['robot5'], task_wait=task_wait_set['robot5'],
                        body_color='k', trace_color='k', name='robot5', text_name='Fighter1')
    # robot4 = Quadcoptor(init_pos=region_list[region_index['p1']]['region_center']+[0],
    #                     robot_task=task_set['robot4'], task_wait=task_wait_set['robot4'],
    #                     body_color='b', trace_color='b', name='robot4')

    robot_set = [robot1, robot2, robot3, robot4, robot5]

    fig, ax = plt.subplots()
    ax.set_xlim(battle_environment.x_range)
    ax.set_ylim(battle_environment.y_range)
    ax.axis('equal')
    ax.axis('off')

    # save_count代表视频存储的frame数  save_count=1400
    ani = animation.FuncAnimation(
        fig, animate, init_func=init, interval=80, blit=True)
    # ani.save('single_pendulum_nodecay.gif', writer='imagemagick')  # , fps=100
    # ani.save('robot_navigation.mp4', fps=45, extra_args=['-vcodec', 'libx264'])
    plt.show()
