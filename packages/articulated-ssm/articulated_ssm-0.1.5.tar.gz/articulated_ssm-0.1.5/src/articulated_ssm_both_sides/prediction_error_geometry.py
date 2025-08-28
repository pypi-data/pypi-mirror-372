"""
Calculates the difference between two meshes
to change:
- pred path
- aligned path
- data path
- might need to change row 35: case_name = case[:-18] depending on how your files are named
author: Laura Carman
"""
import os
import numpy as np
from gias3.mesh import simplemesh, vtktools

root_dir = os.getcwd()

# set predicted path
pred_path = '{}/pred_meshes/train_80'.format(root_dir)
# set the ground truth path
aligned_path = '/Volumes/Laura2TB/ASM/fitted_CT_scan_CS_meshes/merged'
# set where you want the errors to go
data_path = '{}/pred_meshes/train_80/data'.format(root_dir)
if not os.path.exists(data_path):
    os.makedirs(data_path)

bone_names = sorted([f for f in os.listdir(pred_path) if f.endswith('.ply')])
n = len(bone_names)
print("number of bones:", n)
rms_path = os.path.join(data_path, "train_80_errors_mesh_pred.txt")
if os.path.exists(rms_path):
    os.remove(rms_path)
rms_file = open(rms_path, 'a')
rms_file.write("Data           \tRMSE            \tMAE            \tSD            \tMin            \tMax\n")

# for each predicted geometry run the for loop to calculate rms distances
for case in bone_names[:]:
    case_name = case[:-18]
    # Step through meshes
    aligned_mesh = vtktools.loadpoly(os.path.join(aligned_path, case_name+'Left_side.ply'))
    pred_mesh = vtktools.loadpoly(os.path.join(pred_path, case))

    diff = aligned_mesh.v - pred_mesh.v
    data = np.linalg.norm(diff, axis=1)
    dists_rms = np.sqrt(np.mean(data ** 2))
    dists_mae = np.mean(abs(data))
    dists_std = np.std(data)
    dists_min = np.min(data)
    dists_max = np.max(data)

    rms_file = open(rms_path, 'a')
    # Write data
    rms_file.write("%s\t%5.15f\t%5.15f\t%5.15f\t%5.15f\t%5.15f\n" % (case_name, dists_rms, dists_mae, dists_std, dists_min, dists_max))
    rms_file.close()
print("--completed RMSE")
