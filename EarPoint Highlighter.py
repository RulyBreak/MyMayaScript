import maya.cmds as cmds   
import os
   
def read_points_from_file(file_path):
    """读取文件中的点序值"""
    try:
        with open(file_path, 'r') as file:
            points = [int(line.strip()) for line in file.readlines() if line.strip().isdigit()]
        return points
    except Exception as e:
        cmds.error(f"读取文件失败: {e}")
        return []
   
def highlight_points(mesh, points):
    """高亮显示指定点"""
    cmds.select(clear=True)
    point_names = [f"{mesh}.vtx[{pt}]" for pt in points]
    cmds.select(point_names)
   
def set_vertex_display(size):
    """设置顶点显示大小"""
    cmds.polyOptions(sizeVertex=size)
   
def create_ui():
    """创建用户界面"""
    if cmds.window("pointHighlighterUI", exists=True):
        cmds.deleteUI("pointHighlighterUI")

    window = cmds.window("pointHighlighterUI", title="Point Highlighter", widthHeight=(400, 300))
    cmds.columnLayout(adjustableColumn=True, columnAlign="left")

    cmds.text(label="选择模型:")
    mesh_field = cmds.textFieldButtonGrp(buttonLabel='选择', buttonCommand=lambda: select_mesh(mesh_field), columnAlign=(1, "left"))

    cmds.text(label="选择TXT文件:")
    file_field = cmds.textFieldButtonGrp(buttonLabel='选择', buttonCommand=lambda: select_file(file_field, points_field), columnAlign=(1, "left"))

    cmds.text(label="输入点序 (换行分隔):")
    points_field = cmds.scrollField(wordWrap=True, height=100)

    cmds.text(label="调整顶点大小:")
    size_slider = cmds.floatSliderGrp(label='Size', field=True, minValue=1.0, maxValue=100.0, value=1.0, columnAlign=(1, "left"))

    cmds.button(label="加载并显示", command=lambda _: load_and_display(mesh_field, file_field, points_field, size_slider), align="left")
    
    cmds.showWindow(window)
   
def select_mesh(mesh_field):
    """选择模型"""
    selected = cmds.ls(selection=True, type='transform')
    if selected:
        shapes = cmds.listRelatives(selected[0], shapes=True, type='mesh')
        if shapes:
            cmds.textFieldButtonGrp(mesh_field, edit=True, text=shapes[0])
        else:
            cmds.warning("选择的对象不是有效的模型。")
    else:
        cmds.warning("请选择一个模型。")
   
def select_file(file_field, points_field):
    """选择TXT文件"""
    file_path = cmds.fileDialog2(fileFilter="Text Files (*.txt)", dialogStyle=2, fileMode=1)
    if file_path:
        cmds.textFieldButtonGrp(file_field, edit=True, text=file_path[0])
        points = read_points_from_file(file_path[0])
        cmds.scrollField(points_field, edit=True, text='\n'.join(map(str, points)))
   
def load_and_display(mesh_field, file_field, points_field, size_slider):
    """加载点并显示在模型上"""
    mesh_name = cmds.textFieldButtonGrp(mesh_field, query=True, text=True)
    size = cmds.floatSliderGrp(size_slider, query=True, value=True)

    if not mesh_name:
        cmds.warning("请确保选择了有效的模型。")
        return

    points_text = cmds.scrollField(points_field, query=True, text=True)
    points = []
    if points_text:
        try:
            points = [int(pt.strip()) for pt in points_text.split('\n') if pt.strip().isdigit()]
        except ValueError:
            cmds.warning("点序输入格式不正确，请使用换行分隔的整数。")
            return

    highlight_points(mesh_name, points)
    set_vertex_display(size)
   
# 执行主函数   
create_ui()
