import maya.cmds as cmds
import math

def calculate_top_view_distance(mesh, point_index1, point_index2):
    """
    计算模型上两个点在顶视视角下的距离
    :param mesh: 模型的名称
    :param point_index1: 第一个点的索引
    :param point_index2: 第二个点的索引
    :return: 顶视视角下两点之间的距离
    """
    point1_pos = cmds.pointPosition('{}.vtx[{}]'.format(mesh, point_index1), world=True)
    point2_pos = cmds.pointPosition('{}.vtx[{}]'.format(mesh, point_index2), world=True)
    x1, _, z1 = point1_pos
    x2, _, z2 = point2_pos
    distance = math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2)
    return round(distance, 4)

def highlight_points(mesh, point_indices):
    """
    高亮显示模型上指定索引的点
    :param mesh: 模型的名称
    :param point_indices: 点索引列表
    """
    point_names = ['{}.vtx[{}]'.format(mesh, index) for index in point_indices]
    cmds.select(point_names)

def calculate_foot_length(*args):
    mesh_name = cmds.textFieldButtonGrp('meshNameField', query=True, text=True)
    option = cmds.radioButtonGrp('optionRadio', query=True, select=True)
    
    if option == 1:  # 渲染体
        distance1 = calculate_top_view_distance(mesh_name, 10356, 11560)
        distance2 = calculate_top_view_distance(mesh_name, 8071, 9277)
        all_point_indices = [10356, 11560, 8071, 9277]
    else:  # 碰撞体
        distance1 = calculate_top_view_distance(mesh_name, 2230, 191)
        distance2 = calculate_top_view_distance(mesh_name, 4465, 2514)
        all_point_indices = [2230, 191, 4465, 2514]
    
    cmds.text('resultText', edit=True, label="左脚掌长度: {}\n右脚掌长度: {}".format(distance1, distance2))
    highlight_points(mesh_name, all_point_indices)

def select_mesh(mesh_field):
    """选择模型"""
    selected = cmds.ls(selection=True, type='transform')
    if selected:
        shapes = cmds.listRelatives(selected[0], shapes=True, type='mesh')
        if shapes:
            cmds.textFieldButtonGrp(mesh_field, edit=True, text=selected[0])
        else:
            cmds.warning("选择的对象不是有效的模型。")
    else:
        cmds.warning("请选择一个模型。")

def set_vertex_display(size):
    """设置顶点显示大小"""
    cmds.polyOptions(sizeVertex=size)

def create_ui():
    if cmds.window('footLengthWindow', exists=True):
        cmds.deleteUI('footLengthWindow')
    
    cmds.window('footLengthWindow', title="计算脚长", widthHeight=(300, 250))
    cmds.columnLayout(adjustableColumn=True)
    
    cmds.text(label="选择模型:")
    mesh_field = cmds.textFieldButtonGrp('meshNameField', buttonLabel='选择', buttonCommand=lambda: select_mesh('meshNameField'), columnAlign=(1, "left"))
    
    cmds.separator(height=20)
    
    cmds.text(label="选择计算类型:")
    cmds.radioButtonGrp('optionRadio', labelArray2=['渲染体', '碰撞体'], numberOfRadioButtons=2, select=1)
    
    cmds.separator(height=20)
    
    cmds.text(label="调整顶点大小:")
    size_slider = cmds.floatSliderGrp('vertexSizeSlider', label='Size', field=True, minValue=1.0, maxValue=100.0, value=1.0, columnAlign=(1, "left"), changeCommand=lambda x: set_vertex_display(x))
    
    cmds.separator(height=20)
    
    cmds.button(label='计算', command=calculate_foot_length)
    
    cmds.separator(height=20)
    
    cmds.text('resultText', label="结果将显示在这里")
    
    cmds.showWindow('footLengthWindow')

create_ui()