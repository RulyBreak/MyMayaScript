import maya.cmds as cmds
import maya.api.OpenMaya as om
import time
import numpy as np
from scipy.spatial import cKDTree

def assign_vertex_colors(obj, colors):
    if obj:
        start_time = time.time()
        shape_node = cmds.listRelatives(obj, shapes=True)[0]
        sel_list = om.MSelectionList()
        sel_list.add(shape_node)
        mesh = om.MFnMesh(sel_list.getDagPath(0))
        
        color_set = 'vertexColorSet'
        vertex_color_representation = om.MFnMesh.kRGB
        mesh.createColorSet(color_set, vertex_color_representation)
        mesh.setCurrentColorSetName(color_set)
        
        np_colors = np.array(colors, dtype=np.float32)
        mesh.setVertexColors(om.MColorArray(np_colors.tolist()), list(range(len(colors))))
        cmds.polyOptions(obj, colorShadedDisplay=True)
        
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"assign_vertex_colors execution time: {execution_time:.5f} seconds")
    else:
        print("No object selected. Please select an object and run the script again.")

def calculate_hausdorff_distance(obj1, obj2):
    sel_list1 = om.MGlobal.getSelectionListByName(obj1)
    dag_path1 = sel_list1.getDagPath(0)
    
    sel_list2 = om.MGlobal.getSelectionListByName(obj2)
    dag_path2 = sel_list2.getDagPath(0)
    
    mesh1 = om.MFnMesh(dag_path1)
    mesh2 = om.MFnMesh(dag_path2)
    
    vertices1 = mesh1.getPoints(om.MSpace.kWorld)
    vertices2 = mesh2.getPoints(om.MSpace.kWorld)
    
    np_vertices1 = np.array([[v.x, v.y, v.z] for v in vertices1])
    np_vertices2 = np.array([[v.x, v.y, v.z] for v in vertices2])
    
    kdtree1 = cKDTree(np_vertices1)
    kdtree2 = cKDTree(np_vertices2)
    
    distances1, _ = kdtree2.query(np_vertices1)
    hausdorff_dist1 = np.max(distances1)

    distances2, _ = kdtree1.query(np_vertices2)
    hausdorff_dist2 = np.max(distances2)
    
    hausdorff_dist = max(hausdorff_dist1, hausdorff_dist2)
    
    return hausdorff_dist1, hausdorff_dist2

def calculate_max_dimension(obj1, obj2):
    bbox1 = cmds.exactWorldBoundingBox(obj1)
    bbox2 = cmds.exactWorldBoundingBox(obj2)
    max_dimension = max(bbox1[3] - bbox1[0], bbox1[4] - bbox1[1], bbox1[5] - bbox1[2],
                        bbox2[3] - bbox2[0], bbox2[4] - bbox2[1], bbox2[5] - bbox2[2])
    return max_dimension    

def calculate_similarity_percentage(obj1, obj2):
    distances1, distances2 = calculate_hausdorff_distance(obj1, obj2)
    print(f"Hausdorff distance1 obj1 -> obj2: {distances1:.3f}")
    print(f"Hausdorff distance1 obj2 -> obj1: {distances2:.3f}")

    max_dimension = calculate_max_dimension(obj1, obj2)
    # max_dimension = 170
    print(f"Max dimension: {max_dimension:.3f}")

    similarity1 = 1 - (distances1 / max_dimension)
    similarity_percentage1 = similarity1 * 100

    similarity2 = 1 - (distances2 / max_dimension)
    similarity_percentage2 = similarity2 * 100

    # print(f"Similarity1 percentage: {similarity_percentage1:.2f}%")
    # print(f"Similarity2 percentage: {similarity_percentage2:.2f}%")
    hausdorff_similarity_percentage = min(similarity_percentage1, similarity_percentage2)
    # if hausdorff_similarity_percentage > 98:
    #     hausdorff_similarity_percentage += 0.65
    print(f"Hausdorff Similarity percentage: {hausdorff_similarity_percentage:.2f}%")
    
    return hausdorff_similarity_percentage

def calculate_min_distances(obj1, obj2):
    start_time = time.time()
    sel_list1 = om.MGlobal.getSelectionListByName(obj1)
    dag_path1 = sel_list1.getDagPath(0)

    sel_list2 = om.MGlobal.getSelectionListByName(obj2)
    dag_path2 = sel_list2.getDagPath(0)
    
    mesh1 = om.MFnMesh(dag_path1)
    mesh2 = om.MFnMesh(dag_path2)
        
    vertices1 = mesh1.getPoints(om.MSpace.kWorld)
    vertices2 = mesh2.getPoints(om.MSpace.kWorld)
    
    np_vertices1 = np.array([[v.x, v.y, v.z] for v in vertices1])
    np_vertices2 = np.array([[v.x, v.y, v.z] for v in vertices2])
    
    kd_tree = cKDTree(np_vertices2)
    distances, _ = kd_tree.query(np_vertices1)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"calculate_min_distances execution time: {execution_time:.5f} seconds")
    return distances.tolist()

def map_distances_to_colors(distances, use_binary_color=False, obj1=None, obj2=None, similarity_threshold=99.5):
    start_time = time.time()
    min_distance = min(distances)
    max_distance = max(distances)
    normalized_distances = [(d - min_distance) / (max_distance - min_distance) for d in distances]

    palette = [
        (0.0, 0.0, 1.0),   # Blue
        (0.0, 1.0, 1.0),   # Cyan
        (0.0, 1.0, 0.0),   # Green
        (1.0, 1.0, 0.0),   # Yellow
        (1.0, 0.0, 0.0)    # Red
    ]
    
    colors = []
    max_dimension = calculate_max_dimension(obj1, obj2)
    threshold_distance = max_dimension * (1 - similarity_threshold / 100)
    
    for d in distances:
        if d <= threshold_distance:
            # 如果距离小于阈值距离（即相似度高于阈值），设置为蓝色
            color = palette[0]
        else:
            # 对于其他情况，使用颜色插值
            normalized_d = (d - min_distance) / (max_distance - min_distance)
            if normalized_d <= 0:
                color = palette[0]
            elif normalized_d >= 1.0:
                color = palette[-1]
            else:
                index = int(normalized_d * (len(palette) - 1))
                t = normalized_d * (len(palette) - 1) - index
                color1 = palette[index]
                color2 = palette[index + 1]
                color = tuple(c1 + (c2 - c1) * t for c1, c2 in zip(color1, color2))
        colors.append(color)
    
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"map_distances_to_colors execution time: {execution_time:.5f} seconds")    
    return colors

def visualize_object_proximity(obj1, obj2, use_binary_color, similarity_threshold):
    distances = calculate_min_distances(obj1, obj2)
    colors = map_distances_to_colors(distances, use_binary_color, obj1, obj2, similarity_threshold)
    assign_vertex_colors(obj1, colors)

def calculate_similarity_only(obj1, obj2):
    """Calculate Hausdorff similarity without visualization"""
    similarity_percentage = calculate_similarity_percentage(obj1, obj2)
    print("\n################### Hausdorff Distance Result ###################")
    print(f"Similarity percentage: {similarity_percentage:.2f}%")
    print("################### Hausdorff Distance Result ###################\n")

def visualize_similarity(use_binary_color, with_visualization=True, similarity_threshold=99.5, *args):
    selected_objects = cmds.ls(selection=True)

    if len(selected_objects) == 2:
        obj1 = selected_objects[0]
        obj2 = selected_objects[1]
        
        if with_visualization:
            visualize_object_proximity(obj1, obj2, use_binary_color, similarity_threshold)
            visualize_object_proximity(obj2, obj1, use_binary_color, similarity_threshold)
        
        similarity_percentage = calculate_similarity_percentage(obj1, obj2)
        
        if not with_visualization:
            print("\n################### Hausdorff Distance Result ###################")
            print(f"Similarity percentage: {similarity_percentage:.2f}%")
            print("################### Hausdorff Distance Result ###################\n")
    else:
        print("Please select exactly two objects.")

def is_descendant_of(joint, ancestor):
    while joint:
        parent = cmds.listRelatives(joint, parent=True)
        if parent:
            if parent[0] == ancestor:
                return True
            joint = parent[0]
        else:
            break
    return False

def print_related_joint_names():
    selected_obj = cmds.ls(selection=True, type='transform')
    
    if selected_obj:
        related_joints = []
        skin_cluster = 'skinCluster1'
        if cmds.objExists(skin_cluster):
            influence_joints = cmds.skinCluster(skin_cluster, query=True, influence=True)
            related_joints.extend(influence_joints)
        
        blend_shape = 'BODY_BS'
        if cmds.objExists(blend_shape):
            blend_targets = cmds.blendShape(blend_shape, query=True, target=True)
            for target in blend_targets:
                target_joints = cmds.listConnections(target, type='joint')
                if target_joints:
                    related_joints.extend(target_joints)
        
        joints_with_children = []
        for joint in related_joints:
            child_joints = cmds.listRelatives(joint, children=True, type='joint')
            if child_joints:
                joints_with_children.append(joint)
        
        if joints_with_children:
            print("Related Joint Names with Child Joints:")
            for joint in set(joints_with_children):
                print(joint)
        else:
            print("No related joints with child joints found for the selected object.")
        
    else:
        print("No object selected. Please select an object and try again.")

def calculate_total_edge_length(edges):
    total_length = 0
    for edge in edges:
        edge_length = cmds.arclen(edge)
        total_length += edge_length
    
    print(f"Number of Edges: {len(edges)}")
    print(f"Total length of selected edges: {total_length}")  
    return total_length  

def boolean_difference(obj1, obj2):
    duplicated_obj1 = cmds.duplicate(obj1)
    duplicated_obj2 = cmds.duplicate(obj2)
    boolean_result = cmds.polyCBoolOp(duplicated_obj2, duplicated_obj1, op=2, n="boolean_result")
    cmds.delete(boolean_result, constructionHistory=True)
    cmds.hide(boolean_result[0])
    print("Boolean Difference operation completed.")
    return boolean_result[0]

def get_longest_edge_loop(obj):
    edges = cmds.ls(cmds.polyListComponentConversion(obj, toEdge=True), flatten=True)
    edge_loops = []
    for edge in edges:
        cmds.select(edge, replace=True)
        cmds.polySelectSp(loop=True)
        edge_loop = cmds.ls(selection=True, flatten=True)
        if edge_loop not in edge_loops:
            edge_loops.append(edge_loop)

    longest_edge_loop = max(edge_loops, key=len)
    print(f"Longest edge loop: {longest_edge_loop}")
    cmds.select(clear=True)
    return longest_edge_loop

def calculate_surface_length(obj, plane_obj):
    boolean_result = boolean_difference(obj, plane_obj)
    longest_edge_loop = get_longest_edge_loop(boolean_result)
    surface_length = calculate_total_edge_length(longest_edge_loop)   
    return surface_length

def surface_length_similarity(len1, len2):
    similarity = (1 - abs(len1 - len2) / max(len1, len2)) * 100
    print(f"Surface length similarity: {similarity:.2f}%")

def merge_vertices(mesh, distance=0.01, all_meshes=True, construction_history=False):
    if not cmds.objExists(mesh):
        raise ValueError(f"Mesh '{mesh}' does not exist.")

    if not cmds.objectType(mesh, isType="transform"):
        raise ValueError(f"Object '{mesh}' is not a valid mesh.")

    cmds.polyMergeVertex(mesh, distance=distance, alwaysMergeTwoVertices=all_meshes, constructionHistory=construction_history)

def calculate_surface_length_similarity(*args):
    selected_objects = cmds.ls(selection=True)
    
    if len(selected_objects) == 3:
        object_a, object_b, object_plane = selected_objects
        print(f"obj_a: {object_a}, obj_b: {object_b}")
        merge_vertices(object_a)
        merge_vertices(object_b)
        surface_length1 = calculate_surface_length(object_a, object_plane)
        surface_length2 = calculate_surface_length(object_b, object_plane)
        print(f"surface_length1: {surface_length1}, surface_length2: {object_b}")

        print("\n################### Surface Length Result ###################")
        print(f"Surface length of {object_a}: {surface_length1:4f} cm")  
        print(f"Surface length of {object_b}: {surface_length2:4f} cm")  
        surface_length_similarity(surface_length1, surface_length2)
        print("################### Surface Length Result ###################\n")
    else:
        print("Please select exactly three objects.")

def measure_circumference(*args):
    selected_objects = cmds.ls(selection=True)
    
    if len(selected_objects) == 2:
        object_a, object_plane = selected_objects
        merge_vertices(object_a)
        surface_length1 = calculate_surface_length(object_a, object_plane)

        print("\n################### Surface Length Result ###################")
        print(f"Surface length of {object_a}: {surface_length1}")  
        print("################### Surface Length Result ###################\n")
    else:
        print("Please select exactly two objects.")

def create_polyplane(*args):
    cmds.polyPlane(subdivisionsWidth=1, subdivisionsHeight=1, width=50, height=50, name="polyplane")[0]

def on_click_calculate_selected_edge_length(*args):
    selected_edges = cmds.ls(selection=True, flatten=True)

    if not selected_edges:
        print("No edge loop selected. Please select an edge loop.")
        return

    if not cmds.polySelectSp(selected_edges, q=True, loop=True):
        print("Selected components do not form a valid edge loop.")
        return
        
    calculate_total_edge_length(selected_edges)

def on_click_calculate_mesh_max_edge_loop_length(*args):
    selected_object= cmds.ls(selection=True, flatten=True)
    longest_edge_loop = get_longest_edge_loop(selected_object)
    surface_length = calculate_total_edge_length(longest_edge_loop)   

def get_cross_section_perimeter(mesh, plane_transform):
    plane_position = cmds.xform(plane_transform, q=True, ws=True, rp=True)
    plane_rotation = cmds.xform(plane_transform, q=True, ws=True, ro=True)

    cut_edges = cmds.polyCut(mesh, ws=True, ro=plane_rotation, ch=True)

    if not cut_edges:
        raise ValueError("No intersection found between the mesh and the plane.")

    cut_curve = cmds.polyToCurve(ch=False)[0]

    curve_fn = om.MFnNurbsCurve(om.MGlobal.getSelectionListByName(cut_curve).getDagPath(0))
    perimeter = curve_fn.length()

    cmds.delete(cut_curve)

    return perimeter

def on_click_reset_color(*args):
    selected_objects = cmds.ls(selection=True)
    
    if not selected_objects:
        cmds.warning("No object selected.")
        return
    
    default_color = [0.3, 0.3, 0.3, 1.0]
    
    for obj in selected_objects:
        if cmds.nodeType(obj) != "mesh":
            shapes = cmds.listRelatives(obj, shapes=True)
            if not shapes or cmds.nodeType(shapes[0]) != "mesh":
                cmds.warning(f"{obj} is not a mesh.")
                continue
        
        start_time = time.time()

        shape_node = cmds.listRelatives(obj, shapes=True)[0]
        sel_list = om.MSelectionList()
        sel_list.add(shape_node)
        dag_path = sel_list.getDagPath(0)
        mesh = om.MFnMesh(dag_path)

        color_set = 'vertexColorSet'
        vertex_color_representation = om.MFnMesh.kRGB
        if color_set not in mesh.getColorSetNames():
            mesh.createColorSet(color_set, vertex_color_representation)
        mesh.setCurrentColorSetName(color_set)

        vertex_count = mesh.numVertices
        np_colors = np.array([default_color] * vertex_count, dtype=np.float32)
        color_array = om.MColorArray()
        for color in np_colors:
            color_array.append(om.MColor(color.tolist()))

        vertex_indices = list(range(vertex_count))
        mesh.setVertexColors(color_array, vertex_indices)
        cmds.polyOptions(obj, colorShadedDisplay=True)

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Setting colors for {obj} took: {execution_time:.5f} seconds")

if __name__ == '__main__':
    print("################### Similarity Visualizer Start ###################")
    window = cmds.window(title="My Widget", widthHeight=(300, 300))
    
    # 使用垂直布局作为主布局
    main_layout = cmds.columnLayout(adjustableColumn=True)
    
    def run_hausdorff_similarity_palette(*args):
        threshold = cmds.floatSliderGrp(similarity_threshold_slider, query=True, value=True)
        visualize_similarity(False, True, threshold)

    def run_hausdorff_similarity_binary(*args):
        threshold = cmds.floatSliderGrp(similarity_threshold_slider, query=True, value=True)
        visualize_similarity(True, True, threshold)

    def run_hausdorff_similarity_no_color(*args):
        threshold = cmds.floatSliderGrp(similarity_threshold_slider, query=True, value=True)
        visualize_similarity(False, False, threshold)
        
    def increment_threshold(*args):
        current_value = cmds.floatSliderGrp(similarity_threshold_slider, query=True, value=True)
        step = cmds.floatSliderGrp(similarity_threshold_slider, query=True, step=True)
        max_value = cmds.floatSliderGrp(similarity_threshold_slider, query=True, maxValue=True)
        new_value = min(current_value + step, max_value)
        cmds.floatSliderGrp(similarity_threshold_slider, edit=True, value=new_value)
        run_hausdorff_similarity_palette()
        
    def decrement_threshold(*args):
        current_value = cmds.floatSliderGrp(similarity_threshold_slider, query=True, value=True)
        step = cmds.floatSliderGrp(similarity_threshold_slider, query=True, step=True)
        min_value = cmds.floatSliderGrp(similarity_threshold_slider, query=True, minValue=True)
        new_value = max(current_value - step, min_value)
        cmds.floatSliderGrp(similarity_threshold_slider, edit=True, value=new_value)
        run_hausdorff_similarity_palette()

    # 创建一个水平布局来放置滑动条和按钮
    slider_row = cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=(280, 50), columnAttach=[(1, 'both', 0), (2, 'right', 0)])
    
    # 在水平布局的第一列创建滑动条
    similarity_threshold_slider = cmds.floatSliderGrp(
        parent=slider_row,
        label="Similarity Threshold",
        field=True,
        minValue=95.0,
        maxValue=100.0,
        value=100,
        step=0.01,
        columnWidth3=(110, 50, 120),
        adjustableColumn=3,
        dragCommand=run_hausdorff_similarity_palette,
        changeCommand=run_hausdorff_similarity_palette
    )
    
    # 在水平布局的第二列创建一个新的垂直布局来放置增减按钮
    button_col = cmds.columnLayout(parent=slider_row)
    minus_button = cmds.button(parent=button_col, label="-", width=25, command=decrement_threshold)
    plus_button = cmds.button(parent=button_col, label="+", width=25, command=increment_threshold)
    
    # 返回到主布局
    cmds.setParent(main_layout)
    
    # 添加一个小间隔
    cmds.separator(height=5, style='none')
    
    # 创建其他按钮
    cmds.button(label="Hausdorff Similarity Palette Color", command=run_hausdorff_similarity_palette)
    cmds.button(label="Hausdorff Similarity Binary Color", command=run_hausdorff_similarity_binary)
    cmds.button(label="Hausdorff Similarity No Color", command=run_hausdorff_similarity_no_color)
    cmds.button(label="Surface Length Similarity", command=calculate_surface_length_similarity)
    cmds.button(label="Measure Circumference", command=measure_circumference)
    cmds.button(label="Create plane", command=create_polyplane)
    cmds.button(label="Calculate selected edges length", command=on_click_calculate_selected_edge_length)
    cmds.button(label="Calculate mesh's max edge loop length", command=on_click_calculate_mesh_max_edge_loop_length)
    cmds.button(label="Reset Color", command=on_click_reset_color)

    cmds.showWindow(window)
    print("################### Similarity Visualizer End  ###################")