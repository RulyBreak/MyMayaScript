import maya.cmds as cmds
   
def set_ambient_color_to_zero():
    # 获取所有材质
    all_materials = cmds.ls(materials=True)
    
    # 遍历每个材质
    for material in all_materials:
        # 检查材质是否有 Ambient Color 属性
        if cmds.attributeQuery('ambientColor', node=material, exists=True):
            # 将 Ambient Color 设置为 [0, 0, 0]
            cmds.setAttr(f'{material}.ambientColor', 0, 0, 0, type='double3')
            print(f'Set ambientColor of {material} to [0, 0, 0]')
   
# 执行函数   
set_ambient_color_to_zero()
