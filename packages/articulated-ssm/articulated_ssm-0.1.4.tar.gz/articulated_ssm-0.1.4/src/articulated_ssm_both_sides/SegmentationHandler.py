import os
from gias3.mesh import vtktools
import numpy as np
from scipy.spatial import cKDTree


class SegmentationHandler:
    def __init__(self, segmentations_dir, general_fit_settings):
        self.segmentations_dir = segmentations_dir
        self.side = general_fit_settings['side']
        self.segmentations = {}
        self.load_segmentations()

    def load_segmentations(self):
        files = os.listdir(self.segmentations_dir)
        if self.side == 'left' or self.side == 'both':
            for file in files:
                if 'left' in file:
                    if 'femur' in file:
                        self.segmentations.update({'Fem_L': vtktools.loadpoly(
                            r'{}\{}'.format(self.segmentations_dir, file))})
                    if 'hemi' in file:
                        self.segmentations.update({'Pel_L': vtktools.loadpoly(
                            r'{}\{}'.format(self.segmentations_dir, file))})
                    if 'tibia' in file:
                        self.segmentations.update({'Tib_L': vtktools.loadpoly(
                            r'{}\{}'.format(self.segmentations_dir, file))})
                    if 'fibula' in file:
                        self.segmentations.update({'Fib_L': vtktools.loadpoly(
                            r'{}\{}'.format(self.segmentations_dir, file))})
                    if 'patella' in file:
                        self.segmentations.update({'Pat_L': vtktools.loadpoly(
                            r'{}\{}'.format(self.segmentations_dir, file))})
        if self.side == 'right' or self.side == 'both':
            for file in files:
                if 'right' in file:
                    if 'femur' in file:
                        self.segmentations.update({'Fem_R': vtktools.loadpoly(
                            r'{}\{}'.format(self.segmentations_dir, file))})
                    if 'hemi' in file:
                        self.segmentations.update({'Pel_R': vtktools.loadpoly(
                            r'{}\{}'.format(self.segmentations_dir, file))})
                    if 'tibia' in file:
                        self.segmentations.update({'Tib_R': vtktools.loadpoly(
                            r'{}\{}'.format(self.segmentations_dir, file))})
                    if 'fibula' in file:
                        self.segmentations.update({'Fib_R': vtktools.loadpoly(
                            r'{}\{}'.format(self.segmentations_dir, file))})
                    if 'patella' in file:
                        self.segmentations.update({'Pat_R': vtktools.loadpoly(
                            r'{}\{}'.format(self.segmentations_dir, file))})

    def average_rmse_segmentations(self, ll_model):
        rmse_list = []
        for key in self.segmentations.keys():
            _key_in_left = False
            if ll_model.side == 'left' or ll_model.side == 'both':
                _key_in_left = True
                if key in ll_model.ll_l.pelvis_model.bone_names['left']:
                    fitted_vertices = ll_model.ll_l.pelvis_model.node_coords
                elif key in ll_model.ll_l.femur_model.bone_names['left']:
                    fitted_vertices = ll_model.ll_l.femur_model.node_coords
                elif key in ll_model.ll_l.tibfib_model.bone_names['left']:
                    fitted_vertices = ll_model.ll_l.tibfib_model.node_coords
                elif key in ll_model.ll_l.patella_model.bone_names['left']:
                    fitted_vertices = ll_model.ll_l.patella_model.node_coords
                else:
                    _key_in_left = False
                if _key_in_left:
                    rmse_list.append(calculate_rmse_segmentation_to_fitted_per_bone(fitted_vertices,
                                                                                    self.segmentations[key].v))
            if not _key_in_left:
                if ll_model.side == 'right' or ll_model.side == 'both':
                    _key_in_right = True
                    if key in ll_model.ll_r.pelvis_model.bone_names['right']:
                        fitted_vertices = ll_model.ll_r.pelvis_model.node_coords
                    elif key in ll_model.ll_r.femur_model.bone_names['right']:
                        fitted_vertices = ll_model.ll_r.femur_model.node_coords
                    elif key in ll_model.ll_r.tibfib_model.bone_names['right']:
                        fitted_vertices = ll_model.ll_r.tibfib_model.node_coords
                    elif key in ll_model.ll_r.patella_model.bone_names['right']:
                        fitted_vertices = ll_model.ll_r.patella_model.node_coords
                    else:
                        _key_in_right = False
                    if _key_in_right:
                        rmse_list.append(calculate_rmse_segmentation_to_fitted_per_bone(fitted_vertices,
                                                                                        self.segmentations[key].v))

        rmse = np.average(rmse_list)
        return rmse


def calculate_rmse_segmentation_to_fitted_per_bone(fitted_vertices, segmentation_vertices):
    b = fitted_vertices             # Point cloud (x,y,z)
    c = segmentation_vertices       # Point of interest

    xtree = cKDTree(b)
    cd, ci = xtree.query(c, k=1)        # k = number of the closest points to select, cd = distance, ci = index
    distances = []
    [distances.append(distance/1000) for distance in cd]
    rmse = np.sqrt(((np.array(distances) ** 2.0).sum())/len(distances))
    return rmse
