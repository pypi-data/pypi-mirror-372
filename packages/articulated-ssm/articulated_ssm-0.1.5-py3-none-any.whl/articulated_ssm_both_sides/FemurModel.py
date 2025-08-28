from gias3.musculoskeletal.bonemodels.modelcore import ACSCartesian
from gias3.musculoskeletal import model_alignment
from gias3.common import geoprimitives
import numpy as np


class FemurModel:
    def __init__(self, ssm_handler, side):
        self.name = 'Femur'
        self.side = side
        self.ssm_handler = ssm_handler
        self.acs = ACSCartesian((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        self.landmark_names = dict(left=['MEC_VERTEX', 'LEC_VERTEX', 'med_bot_con', 'lat_bot_con'],
                                   right=['MEC_VERTEX', 'LEC_VERTEX', 'med_bot_con', 'lat_bot_con'])
        self.bone_names = dict(left='Fem_L', right='Fem_R')

        self.landmark_node_nrs = ssm_handler.ssm_lm_node_nrs_femur
        self.node_coords = None
        # self.node_coords_fem_l = None
        # self.node_coords_fem_r = None
        self.landmark_coords = dict(left={}, right={})
        self.region_coords = dict(left={}, right={})
        self.femoral_head_centre = ()

    def update_node_coords(self):
        node_coords_per_bone = self.ssm_handler.reconstructed_nodes_per_bone
        self.node_coords = node_coords_per_bone[self.bone_names[self.side]]

    def update_landmarks_and_regions(self):

        for landmark_name in self.landmark_names[self.side]:
            self.landmark_coords[self.side].update({
                landmark_name: self.node_coords[self.landmark_node_nrs[self.side][landmark_name], :]})
        self.region_coords[self.side]['knee_nodes'] = []
        for node_nr in self.ssm_handler.ssm_regions_node_nrs_femur[self.side]['knee_nodes']:
            self.region_coords[self.side]['knee_nodes'].append(self.node_coords[node_nr, :])
        self.femoral_head_centre = self.obtain_femoral_head_centre()

    def obtain_femoral_head_centre(self):
        femoral_head_coords = []
        for node_nr in self.ssm_handler.ssm_regions_node_nrs_femur[self.side]['femur_head_nodes']:
            femoral_head_coords.append(self.node_coords[node_nr, :])
        hc, r = geoprimitives.fitSphereAnalytic(np.asarray(femoral_head_coords))
        return hc

    def update_acs(self):
        self.acs.update(*model_alignment.createFemurACSISB(self.femoral_head_centre,
                                                           self.landmark_coords[self.side]['MEC_VERTEX'],
                                                           self.landmark_coords[self.side]['LEC_VERTEX'],
                                                           side=self.side))
