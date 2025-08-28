from gias3.musculoskeletal.bonemodels.modelcore import ACSCartesian
from gias3.musculoskeletal import model_alignment
import numpy as np


class TibiaFibulaModel:
    def __init__(self, ssm_handler, side):
        self.name = 'Tibia-Fibula'
        self.side = side
        self.ssm_handler = ssm_handler
        self.acs = ACSCartesian((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        self.landmark_names = dict(left=['condyle_lat', 'condyle_med', 'malleolus_lat', 'malleolus_med', 'tib_plateau_lat', 'tib_plateau_med'],
                                   right=['condyle_lat', 'condyle_med', 'malleolus_lat', 'malleolus_med', 'tib_plateau_lat', 'tib_plateau_med'])
        self.bone_names = dict(left=['Fib_L','Tib_L'], right=['Fib_R','Tib_R'])

        self.landmark_node_nrs = self.ssm_handler.ssm_lm_node_nrs_tibiafibula
        self.landmark_coords = dict(left={}, right={})
        self.region_coords = dict(left={}, right={})

        self.node_coords_tib = None
        self.node_coords_fib = None
        self.node_coords = None

    def update_node_coords(self):
        node_coords_per_bone = self.ssm_handler.reconstructed_nodes_per_bone
        self.node_coords_fib = node_coords_per_bone[self.bone_names[self.side][0]]
        self.node_coords_tib = node_coords_per_bone[self.bone_names[self.side][1]]
        self.node_coords = np.vstack((self.node_coords_fib, self.node_coords_tib))

    def update_landmarks_and_regions(self):
        for landmark_name in self.landmark_names[self.side]:
            self.landmark_coords[self.side].update({
                landmark_name: self.node_coords[self.landmark_node_nrs[self.side][landmark_name], :]})

        self.region_coords[self.side]['knee_nodes'] = []
        for node_nr in self.ssm_handler.ssm_regions_node_nrs_tibiafibula[self.side]['knee_nodes']:
            self.region_coords[self.side]['knee_nodes'].append(self.node_coords[node_nr, :])

    def update_acs(self):
        self.acs.update(*model_alignment.createTibiaFibulaACSISB_2(self.landmark_coords[self.side]['malleolus_med'],
                                                                   self.landmark_coords[self.side]['malleolus_lat'],
                                                                   self.landmark_coords[self.side]['condyle_med'],
                                                                   self.landmark_coords[self.side]['condyle_lat'],
                                                                   side=self.side))
