from gias3.musculoskeletal.bonemodels.modelcore import ACSCartesian
from gias3.common import transform3D, math, geoprimitives
import numpy as np
from gias3.musculoskeletal import model_alignment


class PatellaModel:
    def __init__(self, ssm_handler, general_fit_settings, side):
        self.name = 'Patella'
        self.side = side
        self.ssm_handler = ssm_handler
        self.acs = ACSCartesian((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        self.bone_names = dict(left='Pat_L', right='Pat_R')
        self.landmark_names = ['superior', 'inferior', 'lateral']
        self.patella_shift = general_fit_settings['patella_shift']

        self.landmark_node_nrs = ssm_handler.ssm_lm_node_nrs_patella
        self.node_coords = None
        self.region_coords = dict(left={}, right={})
        self.landmark_coords = dict(left={}, right={})

    def update_node_coords(self):
        node_coords_per_bone = self.ssm_handler.reconstructed_nodes_per_bone
        self.node_coords = node_coords_per_bone[self.bone_names[self.side]]

    def update_landmarks_and_regions(self):
        for landmark_name in self.landmark_names:
            self.landmark_coords[self.side].update({
                landmark_name: self.node_coords[self.landmark_node_nrs[self.side][landmark_name], :]})

    def update_acs(self):

        def normalisevector(v):
            return v / np.linalg.norm(v)

        def create_patella_acs(sup, inf, lat):
            """Axes: x-anterior, y-superior, z-right
            """
            if self.side == 'left':
                o = (sup + inf) / 2.0
                x = normalisevector(np.cross(lat - inf, sup - inf))
                y = normalisevector(sup - inf)
                z = normalisevector(np.cross(x, y))
            else:
                o = (sup + inf) / 2.0
                x = normalisevector(np.cross(sup - inf, lat - inf))
                y = normalisevector(sup - inf)
                z = normalisevector(np.cross(x, y))

            return o, x, y, z

        self.acs.update(*create_patella_acs(self.landmark_coords[self.side]['superior'],
                                            self.landmark_coords[self.side]['inferior'],
                                            self.landmark_coords[self.side]['lateral']))
