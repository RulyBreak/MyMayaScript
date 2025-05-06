import os
import maya.cmds as cmds
import re

# 指定顶级目录
base_dir = r"C:\Users\34000\Desktop\P10_scan\3D_Model"

# 获取所有子文件夹列表，并根据名称中的数字排序
subfolders = [f.path for f in os.scandir(base_dir) if f.is_dir()]

# 使用正则表达式提取文件夹名中的数字进行排序
subfolders.sort(key=lambda x: int(re.search(r'(\d+)', os.path.basename(x)).group(1)))

# 初始化偏移量
x_offset = 0
z_offset = 0
spacing = 150
models_per_row = 10

# 遍历每个子文件夹
for index, folder in enumerate(subfolders):
    # 构建完整的.obj文件路径
    obj_path = os.path.join(folder, "beauty_texture.obj")
    # obj_path = os.path.join(folder, "texture.obj")
    
    # 检查文件是否存在
    if os.path.exists(obj_path):
        # 在导入之前获取现有的对象列表
        existing_objects = set(cmds.ls(assemblies=True, long=True))
        
        # 导入.obj文件
        cmds.file(obj_path, i=True, type="OBJ", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace=":", options="mo=1", pr=True)
        
        # 获取新导入的对象
        imported_objects = set(cmds.ls(assemblies=True, long=True)) - existing_objects
        new_model = list(imported_objects)[-1] if imported_objects else None
        
        if new_model:
            # 获取文件夹名称
            folder_name = os.path.basename(folder)
            
            # 生成新的模型名称
            new_name = f"b_{folder_name}"
	        # new_name = f"m_{folder_name}"
            
            # 重命名模型并检查是否成功
            try:
                cmds.rename(new_model, new_name)
            except RuntimeError as e:
                print(f"Error renaming {new_model} to {new_name}: {e}")
                continue
            
            # 移动模型到指定位置
            cmds.move(x_offset, 0, z_offset, new_name)
            
            # 更新X轴偏移量
            x_offset += spacing
            
            # 每10个模型换行
            if (index + 1) % models_per_row == 0:
                x_offset = 0
                z_offset -= spacing
        else:
            print(f"No new model found in {folder}")
