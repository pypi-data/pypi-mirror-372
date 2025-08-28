from gias3.mesh import vtktools
import numpy as np
import os
import csv


def save_mesh_and_lms(ll_model, source_lms, target_lms, lms_to_fit, output_directory, side, xopt):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    lms_to_fit_source = np.asarray([np.append(np.copy(lms_to_fit), 'hjc')])
    lms_to_fit_source = np.asarray([np.append(lms_to_fit_source, 'condyle_lat')])
    lms_to_fit_source = np.asarray([np.append(lms_to_fit_source, 'condyle_med')])

    if side == 'left':
        model = ll_model.ll_l
        node_coords_pel = model.pelvis_model.node_coords_pel_l
    elif side == 'right':
        model = ll_model.ll_r
        node_coords_pel = model.pelvis_model.node_coords_pel_r

    if model.include_patella == 1:
        node_coords_pat = model.patella_model.node_coords

    node_coords_fem = model.femur_model.node_coords
    node_coords_tib = model.tibfib_model.node_coords_tib
    node_coords_fib = model.tibfib_model.node_coords_fib

    hjc = model.pelvis_model.acetabulum_origin[side]
    condyle_lat = model.tibfib_model.landmark_coords[side]['condyle_lat']
    condyle_med = model.tibfib_model.landmark_coords[side]['condyle_med']

    target_lms_save = np.copy(target_lms[:-2])
    source_lms_save = np.copy(source_lms[:-2])
    source_lms_save = np.concatenate((source_lms_save, np.asarray([hjc]), np.asarray([condyle_lat]), np.asarray([condyle_med])), axis=0)
    bone_mesh_pel, bone_mesh_fem, bone_mesh_tib, bone_mesh_fib = model.ssm_handler.create_mesh_each_bone(node_coords_pel, node_coords_fem, node_coords_tib, node_coords_fib)

    output_pel = os.path.join(output_directory, f'predicted_mesh_{side}_pelvis.stl')
    output_fem = os.path.join(output_directory, f'predicted_mesh_{side}_femur.stl')
    output_tib = os.path.join(output_directory, f'predicted_mesh_{side}_tibia.stl')
    output_fib = os.path.join(output_directory, f'predicted_mesh_{side}_fibula.stl')
    pred_lms = os.path.join(output_directory, f'predicted_lms_{side}.txt')
    orig_lms = os.path.join(output_directory, f'orignial_lms_{side}.txt')
    x_opt = os.path.join(output_directory, f'x_opt_{side}.txt')

    pred_lms_save = np.concatenate((np.transpose(lms_to_fit_source), source_lms_save), axis=1)
    with open(pred_lms, "w+") as file:
        csv.writer(file, delimiter=" ").writerows(pred_lms_save)

    lms_to_fit_targ = np.asarray([lms_to_fit])
    orig_lms_save = np.concatenate((np.transpose(lms_to_fit_targ), target_lms_save), axis=1)
    with open(orig_lms, "w+") as file:
        csv.writer(file, delimiter=" ").writerows(orig_lms_save)

    headers = ['pelvis_rigid', 'hip_rot', 'knee_rot', 'pc_weights']
    with open(x_opt, "w+") as file:
        for header, row in zip(headers, xopt):
            file.write(f"{header} " + " ".join(map(str, row)) + "\n")

    pred_mesh_pel = vtktools.Writer(filename=output_pel, v=bone_mesh_pel.v, f=bone_mesh_pel.f)
    pred_mesh_pel.write()
    pred_mesh_fem = vtktools.Writer(filename=output_fem, v=bone_mesh_fem.v, f=bone_mesh_fem.f)
    pred_mesh_fem.write()
    pred_mesh_tib = vtktools.Writer(filename=output_tib, v=bone_mesh_tib.v, f=bone_mesh_tib.f)
    pred_mesh_tib.write()
    pred_mesh_fib = vtktools.Writer(filename=output_fib, v=bone_mesh_fib.v, f=bone_mesh_fib.f)
    pred_mesh_fib.write()
