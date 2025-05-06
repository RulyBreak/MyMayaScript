import maya.cmds as cmds
import math

def get_midpoint(joint1, joint2):
    # 获取两个关节的世界坐标
    pos1 = cmds.xform(joint1, query=True, worldSpace=True, translation=True)
    pos2 = cmds.xform(joint2, query=True, worldSpace=True, translation=True)
    
    # 计算中点
    midpoint = [(pos1[0] + pos2[0]) / 2, (pos1[1] + pos2[1]) / 2, (pos1[2] + pos2[2]) / 2]
    return midpoint

def calculate_distance(point1, point2):
    # 计算两点之间的欧几里得距离
    distance = math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)
    return distance

# 定义骨骼名称
lowerarm_joints = ['lowerarm_in_l', 'lowerarm_out_l', 'lowerarm_fwd_l', 'lowerarm_bck_l']
wrist_joints = ['wrist_inner_l', 'wrist_outer_l']

# 计算lowerarm骨骼的中点
lowerarm_midpoint = [0, 0, 0]
for joint in lowerarm_joints:
    pos = cmds.xform(joint, query=True, worldSpace=True, translation=True)
    lowerarm_midpoint[0] += pos[0]
    lowerarm_midpoint[1] += pos[1]
    lowerarm_midpoint[2] += pos[2]

lowerarm_midpoint = [coord / len(lowerarm_joints) for coord in lowerarm_midpoint]

# 计算wrist骨骼的中点
wrist_midpoint = get_midpoint(wrist_joints[0], wrist_joints[1])

# 计算两个中点之间的距离
distance = calculate_distance(lowerarm_midpoint, wrist_midpoint)

# 输出结果
print("Lowerarm midpoint: {}".format(lowerarm_midpoint))
print("Wrist midpoint: {}".format(wrist_midpoint))
print("Distance between midpoints: {}".format(distance))