import maya.cmds as cmds
import math

def calculate_distance_between_points(point1, point2):
    """
    计算两个点之间的三维距离
    """
    distance = math.sqrt(
        (point1[0] - point2[0]) ** 2 +
        (point1[1] - point2[1]) ** 2 +
        (point1[2] - point2[2]) ** 2
    )
    return distance

def get_joint_midpoint(joint1, joint2):
    """
    计算两个骨骼节点的中点
    """
    # 获取两个骨骼的世界坐标位置
    pos1 = cmds.xform(joint1, query=True, translation=True, worldSpace=True)
    pos2 = cmds.xform(joint2, query=True, translation=True, worldSpace=True)
    
    # 计算中点
    midpoint = [
        (pos1[0] + pos2[0]) / 2,
        (pos1[1] + pos2[1]) / 2,
        (pos1[2] + pos2[2]) / 2
    ]
    return midpoint

def calculate_midpoint_distance(joint1, joint2, target_joint):
    """
    计算两个骨骼节点的中点到目标骨骼节点的距离
    """
    # 获取中点
    midpoint = get_joint_midpoint(joint1, joint2)
    
    # 获取目标骨骼的世界坐标位置
    target_pos = cmds.xform(target_joint, query=True, translation=True, worldSpace=True)
    
    # 计算中点到目标点的距离
    distance = calculate_distance_between_points(midpoint, target_pos)
    return distance

def main():
    # 定义骨骼节点名称（左右两侧）
    joints_to_calculate = [
        {
            "joint1": "wrist_outer_r",
            "joint2": "wrist_inner_r",
            "target": "middle_03_r_end"
        },
        {
            "joint1": "wrist_outer_l",
            "joint2": "wrist_inner_l",
            "target": "middle_03_l_end"
        }
    ]
    
    # 遍历每组骨骼节点并计算距离
    for joint_group in joints_to_calculate:
        joint1 = joint_group["joint1"]
        joint2 = joint_group["joint2"]
        target = joint_group["target"]
        
        # 检查骨骼节点是否存在
        if not cmds.objExists(joint1) or not cmds.objExists(joint2) or not cmds.objExists(target):
            cmds.warning(f"骨骼节点 {joint1}, {joint2} 或 {target} 不存在，请检查名称是否正确。")
            continue
        
        # 计算中点到目标点的距离
        distance = calculate_midpoint_distance(joint1, joint2, target)
        
        # 输出结果
        print(f"骨骼节点 {joint1} 和 {joint2} 的中点到 {target} 的距离为: {distance:.4f}")

# 执行主函数
main()