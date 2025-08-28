from gias3.musculoskeletal.bonemodels.modelcore import ACSCartesian
from gias3.common import geoprimitives
import numpy as np
from gias3.musculoskeletal import model_alignment


class PelvisModel:
    def __init__(self, ssm_handler, general_fit_settings, side):
        self.name = 'Pelvis'
        self.side = side
        self.ssm_handler = ssm_handler
        self.general_fit_settings = general_fit_settings
        self.acs = ACSCartesian((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))

        self.landmark_names = dict(left=['ASIS_VERTEX',
                                         'PSIS_VERTEX'
                                         ],
                                   right=['ASIS_VERTEX',
                                          'PSIS_VERTEX'
                                          ])

        self.bone_names = dict(left=['Pel_L', 'Pel_R'], right=['Pel_L', 'Pel_R'])

        self.landmark_node_nrs = ssm_handler.ssm_lm_node_nrs_pelvis

        self.node_coords = None
        self.node_coords_pel_l = None
        self.node_coords_pel_r = None
        # self.node_coords_sac = None
        # self.node_coords = None
        self.landmark_coords = dict(left={}, right={})
        self.region_coords = dict(left={}, right={})
        self.acetabulum_origin = dict(left={}, right={})

    def update_node_coords(self):
        node_coords_per_bone = self.ssm_handler.reconstructed_nodes_per_bone
        self.node_coords_pel_l = node_coords_per_bone[self.bone_names[self.side][0]]
        self.node_coords_pel_r = node_coords_per_bone[self.bone_names[self.side][1]]

        self.node_coords = np.vstack((self.node_coords_pel_l, self.node_coords_pel_r))

    def update_acs(self):
        self.acs.update(*model_alignment.createPelvisACSISB(self.landmark_coords['left']['ASIS_VERTEX'],
                                                            self.landmark_coords['right']['ASIS_VERTEX'],
                                                            self.landmark_coords['left']['PSIS_VERTEX'],
                                                            self.landmark_coords['right']['PSIS_VERTEX']))

    def update_landmarks_and_regions(self):
        for landmark_name in self.landmark_names['left']:
            self.landmark_coords['left'].update({
                landmark_name: self.node_coords_pel_l[self.landmark_node_nrs['left'][landmark_name]]})

        for landmark_name in self.landmark_names['right']:
            self.landmark_coords['right'].update({
                landmark_name: self.node_coords_pel_r[self.landmark_node_nrs['right'][landmark_name]]})

        self.obtain_acetabulum_sphere_centre()

    def obtain_acetabulum_sphere_centre(self):
        if self.side == 'left':
            pel = self.node_coords_pel_l
        elif self.side == 'right':
            pel = self.node_coords_pel_r

        acetabulum_coords = []
        for node_nr in self.ssm_handler.ssm_regions_node_nrs_pelvis[self.side]['acetabulum_nodes']:
            acetabulum_coords.append(pel[node_nr, :])
        hc, r = geoprimitives.fitSphereAnalytic(np.asarray(acetabulum_coords))
        self.acetabulum_origin[self.side] = hc
