import maya.cmds as cmds

def reset_joint_orientation_recursive(joint):
    """
    递归重置骨骼及其子级骨骼的内置方向为0
    """
    # 重置当前骨骼的内置方向
    cmds.setAttr(joint + ".jointOrientX", 0)
    cmds.setAttr(joint + ".jointOrientY", 0)
    cmds.setAttr(joint + ".jointOrientZ", 0)
    print("已重置骨骼 {} 的内置方向为0。".format(joint))

    # 获取当前骨骼的所有子级骨骼
    children = cmds.listRelatives(joint, children=True, type='joint') or []
    
    # 递归处理每个子级骨骼
    for child in children:
        reset_joint_orientation_recursive(child)

def reset_joint_orientation(include_children=True):
    """
    重置选中骨骼的内置方向为0
    :param include_children: 是否包含所有子级骨骼
    """
    # 获取选中的骨骼
    selected_joints = cmds.ls(selection=True, type='joint')
    
    if not selected_joints:
        cmds.warning("请选择一个或多个骨骼。")
        return
    
    # 遍历选中的骨骼
    for joint in selected_joints:
        if include_children:
            # 包含所有子级骨骼
            reset_joint_orientation_recursive(joint)
        else:
            # 仅处理当前选中骨骼
            cmds.setAttr(joint + ".jointOrientX", 0)
            cmds.setAttr(joint + ".jointOrientY", 0)
            cmds.setAttr(joint + ".jointOrientZ", 0)
            print("已重置骨骼 {} 的内置方向为0。".format(joint))

def create_ui():
    """
    创建UI窗口
    """
    # 如果窗口已经存在，则删除
    if cmds.window("resetJointOrientUI", exists=True):
        cmds.deleteUI("resetJointOrientUI")
    
    # 创建窗口
    cmds.window("resetJointOrientUI", title="重置骨骼内置方向", widthHeight=(300, 100))
    cmds.columnLayout(adjustableColumn=True)
    
    # 添加选项
    cmds.radioButtonGrp("includeChildrenRadio", label="处理范围 :   ", labelArray2=["仅选中骨骼", "包含所有子级"], numberOfRadioButtons=2, select=2)
    
    # 添加执行按钮
    cmds.button(label="执行", command=lambda *args: execute_reset())
    
    # 显示窗口
    cmds.showWindow("resetJointOrientUI")

def execute_reset():
    """
    执行重置操作
    """
    # 获取选项状态
    include_children = cmds.radioButtonGrp("includeChildrenRadio", query=True, select=True) == 2
    
    # 调用重置函数
    reset_joint_orientation(include_children)

# 创建UI窗口
create_ui()