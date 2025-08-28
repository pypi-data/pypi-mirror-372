import numpy as np
from scipy.spatial import cKDTree
from gias3.common import transform3D, math

from articulated_ssm_both_sides.FemurModel import FemurModel
from articulated_ssm_both_sides.PelvisModel import PelvisModel
from articulated_ssm_both_sides.PatellaModel import PatellaModel
from articulated_ssm_both_sides.TibiaFibulaModel import TibiaFibulaModel


class LowerLimbSide:
    def __init__(self, side, ssm_handler, general_fit_settings, ll_settings, loo=False):
        self.side = side
        self.ssm_handler = ssm_handler
        self.include_patella = general_fit_settings['include_patella']
        self.N_PARAMS_PELVIS = ll_settings['dof']['N_PARAMS_PELVIS']
        self.N_PARAMS_HIP = ll_settings['dof']['N_PARAMS_HIP']
        self.N_PARAMS_KNEE = ll_settings['dof']['N_PARAMS_KNEE']
        self.N_PARAMS_RIGID = self.N_PARAMS_PELVIS + self.N_PARAMS_HIP + self.N_PARAMS_KNEE
        self._neutral_params = [[0, ],  # pc_weights
                                [0, ],  # pc_modes
                                [0] * self.N_PARAMS_PELVIS,     # pelvis_rigid dof
                                [0] * self.N_PARAMS_HIP,        # hip_rot dof
                                [0] * self.N_PARAMS_KNEE]       # knee_rot

        self.pelvis_model = PelvisModel(ssm_handler, general_fit_settings, side)
        self.femur_model = FemurModel(ssm_handler, side)
        self.tibfib_model = TibiaFibulaModel(ssm_handler, side)
        if self.include_patella:
            self.patella_model = PatellaModel(ssm_handler, general_fit_settings, side)

        self.direction_parameters = ll_settings['directions']
        self.knee_gap = general_fit_settings['knee_gap']
        self.knee_fixed = general_fit_settings['knee_fixed']
        self.allow_knee_adduction_dof = general_fit_settings['allow_knee_adduction_dof']
        self.allow_knee_adduction_correction = general_fit_settings['allow_knee_adduction_correction']
        self.loo = loo

    def import_opposite_side(self, ll):
        """
        function to associate two lower limb models with each other in the case of using both sides
        used to keep consistent coordinate systems mainly in the pelvis
        """
        if self.side == 'left':
            self.ll_r = ll
        else:
            self.ll_l = ll

    def load_bones_and_model(self):
        # Load bone models and set to neutral positions
        # zero shape model

        self.ssm_handler.load_coupled_ssm()
        self.ssm_handler.reconstruct_ssm([0, ], [0, ])
        self.ssm_handler.split_ssm_geometry_per_bone(self.ssm_handler.reconstructed)

        self.femur_model.update_node_coords()
        self.femur_model.update_landmarks_and_regions()
        self.femur_model.update_acs()

        self.tibfib_model.update_node_coords()
        self.tibfib_model.update_landmarks_and_regions()
        self.tibfib_model.update_acs()

        self.pelvis_model.update_node_coords()
        self.pelvis_model.update_landmarks_and_regions()
        self.pelvis_model.update_acs()

        if self.include_patella:
            self.patella_model.update_node_coords()
            self.patella_model.update_landmarks_and_regions()
            self.patella_model.update_acs()

        # zero model again, this time with angles and hip and knee set
        self.update_all_models(*self._neutral_params)

    def update_all_models(self, pc_weights, pc_modes, pelvis_rigid, hip_rot, knee_rot):
        """Update the lower limb geometry by pc weights and rigid transformations
        Inputs:
        pc_weights [list of floats]: list of pc weights
        pc_modes [list of ints]: list of the pcs that the weights are for
        pelvis_rigid [1-d array]: an array of six elements defining the rigid body
            translation and rotation for the pelvis.
        hip_rot [1-d array]: an array of 3 radian angles for femur rotation about the
            hip joint (flexion, rotation, adduction)
        knee_rot [1-d array]: an array of radian angles for tibia-fibula rotation
            about the knee joint (flexion)
        """
        # evaluate shape model
        self.update_models_by_pcweights_sd(pc_weights, pc_modes)

        # rigid transform pelvis
        self.update_pelvis(pelvis_rigid)

        # place femur by hip rotation
        self.update_femur(hip_rot)

        # place tibia and fibula by knee_rot and default_knee_offset
        self.update_tibiafibula(knee_rot)

        # place patella relative to tibia
        if self.include_patella == 1:
            self.update_patella()

        # self.put_all_landmark_coords_in_one_dict()

    def update_models_by_pcweights_sd(self, pc_weights, pc_modes):
        self.ssm_handler.reconstruct_ssm(pc_weights, pc_modes)
        self.ssm_handler.split_ssm_geometry_per_bone(self.ssm_handler.reconstructed)

        self.femur_model.update_node_coords()
        self.femur_model.update_landmarks_and_regions()
        self.femur_model.update_acs()

        self.pelvis_model.update_node_coords()
        self.pelvis_model.update_landmarks_and_regions()
        self.pelvis_model.update_acs()

        self.tibfib_model.update_node_coords()
        self.tibfib_model.update_landmarks_and_regions()
        self.tibfib_model.update_acs()

        if self.include_patella:
            self.patella_model.update_node_coords()
            self.patella_model.update_landmarks_and_regions()
            self.patella_model.update_acs()

    def update_pelvis(self, pelvis_rigid):
        """Update position and orientation of the pelvis.
        Inputs:
        pelvis_rigid [list]: list of 6 floats describing a rigid transformation in the global coordinate system of the
            pelvis - [tx, ty, tz, rx, ry, rz]. Rotation is about the origin of the pelvis anatomic coordinate system.
        """

        pel = self.pelvis_model
        _pel_origin = self.pelvis_model.acs.o

        pel.node_coords_pel_l = transform3D.transformRigid3DAboutP(pel.node_coords_pel_l, pelvis_rigid, _pel_origin)
        pel.node_coords_pel_r = transform3D.transformRigid3DAboutP(pel.node_coords_pel_r, pelvis_rigid, _pel_origin)
        pel.node_coords = np.vstack((pel.node_coords_pel_l, pel.node_coords_pel_r))

        pel.update_landmarks_and_regions()

        pel.update_acs()

    def update_femur(self, hip_rot):
        """Update position and orientation of the femur segment.
        inputs:
        hip_rot [list]: list of 3 floats describing hip flexion, rotation, and adduction in radians.
        """

        # align femur to neutral hip CS
        self.reset_femur_hip()

        # get joint cs
        o, flex, rot, abd = self.get_hip_acs()

        # apply hip rotations:
        # flexion (pelvis-z)
        self.femur_model.node_coords = transform3D.transformRotateAboutAxis(self.femur_model.node_coords,
                                                                            self.direction_parameters[self.side]
                                                                            ['hip_flex_coeff'] * hip_rot[0],
                                                                            o,
                                                                            o + flex)

        self.femur_model.update_landmarks_and_regions()
        self.femur_model.update_acs()

        # abduction (floating)
        self.femur_model.node_coords = transform3D.transformRotateAboutAxis(self.femur_model.node_coords,
                                                                            self.direction_parameters[self.side]
                                                                            ['hip_add_coeff'] * hip_rot[2],
                                                                            o,
                                                                            o + abd)

        self.femur_model.update_landmarks_and_regions()
        self.femur_model.update_acs()

        # rotations (femur-z)

        self.femur_model.node_coords = transform3D.transformRotateAboutAxis(self.femur_model.node_coords,
                                                                            self.direction_parameters[self.side]
                                                                            ['hip_rot_coeff'] * hip_rot[1],
                                                                            o,
                                                                            o + rot)

        self.femur_model.update_landmarks_and_regions()
        self.femur_model.update_acs()

    def reset_femur_hip(self):
        """Reset femur position to have 0 rotations at the hip.
        i.e. align femur ACS with pelvis ACS at the HJC
        """
        # translate axes to femur system
        op = self.pelvis_model.acetabulum_origin[self.side]
        cs_targ = np.array([op,
                            op + self.pelvis_model.acs.x,
                            op + self.pelvis_model.acs.y,
                            op + self.pelvis_model.acs.z])

        of = self.femur_model.femoral_head_centre
        cs_source = np.array([of,
                              of + self.femur_model.acs.x,
                              of + self.femur_model.acs.y,
                              of + self.femur_model.acs.z])
        t = transform3D.directAffine(cs_source, cs_targ)

        self.femur_model.node_coords = transform3D.transformAffine(self.femur_model.node_coords, t)
        self.femur_model.update_landmarks_and_regions()
        self.femur_model.update_acs()

    def get_hip_acs(self):
        o = self.pelvis_model.acetabulum_origin[self.side]
        abd = math.norm(np.cross(self.femur_model.acs.y, self.pelvis_model.acs.z))  # floating axis
        rot = self.femur_model.acs.y  # rotation
        flex = self.pelvis_model.acs.z  # flexion
        return np.array([o, flex, rot, abd])

    def update_tibiafibula(self, knee_rot):
        """Update position and orientation of the tibiafibula segment.
        inputs:
        knee_rot [list of floats]: knee flexion and adduction angle in radians.
        """
        # align tibia to neutral knee CS
        self.reset_tibia_knee()

        if not self.knee_fixed:
            # get joint cs
            o, flex, rot, abd = self.get_knee_acs()

            # apply knee rotations: flexion(femur-z)
            self.tibfib_model.node_coords_tib = transform3D.transformRotateAboutAxis(self.tibfib_model.node_coords_tib,
                                                                                 self.direction_parameters[self.side]
                                                                                 ['knee_flex_coeff'] * knee_rot[0],
                                                                                 o,
                                                                                 o + flex)
            self.tibfib_model.node_coords_fib = transform3D.transformRotateAboutAxis(self.tibfib_model.node_coords_fib,
                                                                                     self.direction_parameters[
                                                                                         self.side]
                                                                                     ['knee_flex_coeff'] * knee_rot[0],
                                                                                     o,
                                                                                     o + flex)
            self.tibfib_model.node_coords = np.vstack((self.tibfib_model.node_coords_fib,self.tibfib_model.node_coords_tib))
            self.tibfib_model.update_landmarks_and_regions()
            self.tibfib_model.update_acs()

            # apply knee rotation: adduction(floating x)
            if self.allow_knee_adduction_dof:
                self.tibfib_model.node_coords_tib = transform3D.transformRotateAboutAxis(self.tibfib_model.node_coords_tib,
                                                                                     self.direction_parameters
                                                                                     [self.side]['knee_add_coeff']
                                                                                     * knee_rot[1],
                                                                                     o,
                                                                                     o + abd)
                self.tibfib_model.node_coords_fib = transform3D.transformRotateAboutAxis(
                    self.tibfib_model.node_coords_fib,
                    self.direction_parameters
                    [self.side]['knee_add_coeff']
                    * knee_rot[1],
                    o,
                    o + abd)
                self.tibfib_model.node_coords = np.vstack((self.tibfib_model.node_coords_fib, self.tibfib_model.node_coords_tib))
                self.tibfib_model.update_landmarks_and_regions()
                self.tibfib_model.update_acs()

            # reset knee gap
            if self.allow_knee_adduction_correction:
                self.reset_tibia_kneegap_2()
            else:
                self.reset_tibia_kneegap_1()

    def reset_tibia_knee(self):
        """Reset tibia position to have 0 rotations at the knee.
        i.e. align tibia ACS with femur ACS at the femur origin
        """
        # translate axes to femur system
        of = self.femur_model.acs.o
        cs_targ = np.array([of,
                            of + self.femur_model.acs.x,
                            of + self.femur_model.acs.y,
                            of + self.femur_model.acs.z,
                            ])

        ot = 0.5 * (self.tibfib_model.landmark_coords[self.side]['condyle_med'] +
                    self.tibfib_model.landmark_coords[self.side]['condyle_lat'])

        cs_source = np.array([ot,
                              ot + self.tibfib_model.acs.x,
                              ot + self.tibfib_model.acs.y,
                              ot + self.tibfib_model.acs.z,
                              ])

        t = transform3D.directAffine(cs_source, cs_targ)

        self.tibfib_model.node_coords_tib = transform3D.transformAffine(self.tibfib_model.node_coords_tib, t)
        self.tibfib_model.node_coords_fib = transform3D.transformAffine(self.tibfib_model.node_coords_fib, t)
        self.tibfib_model.node_coords = np.vstack((self.tibfib_model.node_coords_fib, self.tibfib_model.node_coords_tib))
        self.tibfib_model.update_landmarks_and_regions()
        self.tibfib_model.update_acs()

        self.reset_tibia_kneegap_1()

    def reset_tibia_kneegap_1(self):
        """shift tibia along tibia y to maintain knee joint gap
        """
        # self.femur_model.get_knee_surface_pts(self)
        # self.tibfib_model.get_knee_surface_pts(self)
        current_knee_gap = self.calc_knee_gap()
        knee_shift = current_knee_gap - self.knee_gap
        shift_t = knee_shift * self.tibfib_model.acs.y
        self.tibfib_model.node_coords_tib = self.tibfib_model.node_coords_tib + shift_t
        self.tibfib_model.node_coords_fib = self.tibfib_model.node_coords_fib + shift_t
        self.tibfib_model.node_coords = np.vstack((self.tibfib_model.node_coords_fib, self.tibfib_model.node_coords_tib))
        self.tibfib_model.update_landmarks_and_regions()
        self.tibfib_model.update_acs()

    def reset_tibia_kneegap_2(self):
        """shift and reorient tibia to fit to femoral condyles. Allow rotation
        in its x-axis
        """
        # place tibia as per normal
        self.reset_tibia_kneegap_1()

        # build ckdtree of femoral condyle points
        femur_tree = cKDTree(np.asarray(self.femur_model.region_coords[self.side]['knee_nodes']))

        # calculate and apply varus-valgus angle (about floating-x)
        varus_angle = self.calc_varus_angle(femur_tree)[0]

        floating_x = math.norm(np.cross(self.tibfib_model.acs.y, self.femur_model.acs.z))
        self.tibfib_model.node_coords_tib = transform3D.transformRotateAboutAxis(self.tibfib_model.node_coords_tib,
                                                                             -varus_angle,
                                                                             self.femur_model.acs.o,
                                                                             self.femur_model.acs.o + floating_x)
        self.tibfib_model.node_coords_fib = transform3D.transformRotateAboutAxis(self.tibfib_model.node_coords_fib,
                                                                                 -varus_angle,
                                                                                 self.femur_model.acs.o,
                                                                                 self.femur_model.acs.o + floating_x)
        self.tibfib_model.node_coords = np.vstack(
            (self.tibfib_model.node_coords_fib, self.tibfib_model.node_coords_tib))

        self.tibfib_model.update_landmarks_and_regions()
        self.tibfib_model.update_acs()

    def calc_knee_gap(self):
        """Calculate the closest distance between points on the femoral
        knee articular surface and the tibial knee articular surface.
        """
        # evaluate points
        femur_points = np.asarray(self.femur_model.region_coords[self.side]['knee_nodes'])
        tibia_points = np.asarray(self.tibfib_model.region_coords[self.side]['knee_nodes'])

        # find closest neighbours
        femur_tree = cKDTree(femur_points)
        dist, femur_points_i = femur_tree.query(tibia_points)

        # calc distance in the tibial Y for each pair
        tibia_y_dist = np.dot(femur_points[femur_points_i] - tibia_points, self.tibfib_model.acs.y)

        return tibia_y_dist.min()

    def get_knee_acs(self):
        """Returns knee joint coordinate system:
        [origin, flexion axis, rotation axis, abduction axis]
        """
        o = self.femur_model.acs.o  # origin
        abd = math.norm(np.cross(self.tibfib_model.acs.y, self.femur_model.acs.z))  # abduction, floating axis
        rot = self.tibfib_model.acs.y  # rotation
        flex = self.femur_model.acs.z  # flexion
        return np.array([o, flex, rot, abd])

    def calc_varus_angle(self, femur_points_tree):
        # evaluate tibial plateau points
        tp_lat = self.tibfib_model.landmark_coords[self.side]['tib_plateau_lat']
        tp_med = self.tibfib_model.landmark_coords[self.side]['tib_plateau_med']

        # tibial plateau vector
        if self.side == 'left':
            tp_v = tp_med - tp_lat
        elif self.side == 'right':
            tp_v = tp_lat - tp_med
        # find the closest femur condyle points to tp_lat and tp_med
        (med_d, lat_d), (fc_med_i, fc_lat_i) = femur_points_tree.query([tp_med, tp_lat])

        # if fc_med_i == fc_lat_i:  # To make sure fc_v is not NaN
        #     fc_med_i -= 1

        # femoral condyle vector
        # if self.side == 'left':
        #    fc_v = femur_points_tree.data[fc_med_i] - femur_points_tree.data[fc_lat_i]
        # elif self.side == 'right':
        #    fc_v = femur_points_tree.data[fc_lat_i] - femur_points_tree.data[fc_med_i]

        fc_med_i = self.femur_model.landmark_coords[self.side]['med_bot_con']
        fc_lat_i = self.femur_model.landmark_coords[self.side]['lat_bot_con']

        if self.side == 'left':
            fc_v = fc_med_i - fc_lat_i
        elif self.side == 'right':
            fc_v = fc_lat_i - fc_med_i

        # project vectors to Z-Y plane
        z = self.femur_model.acs.z
        y = self.tibfib_model.acs.y
        tp_v_zy = np.array([np.dot(tp_v, z), np.dot(tp_v, y)])
        fc_v_zy = np.array([np.dot(fc_v, z), np.dot(fc_v, y)])

        # calc angle in Z-Y plane
        tp_fc_angle = abs(math.angle(tp_v_zy, fc_v_zy))

        # if lat condyle is higher than med condyle, negative rotation is needed
        lat_d = np.sqrt(np.sum((tp_lat-fc_lat_i)**2, axis=0))
        med_d = np.sqrt(np.sum((tp_med - fc_med_i) ** 2, axis=0))

        if self.side == 'left':
            if lat_d > med_d:
                tp_fc_angle *= -1.0
        else:
            if lat_d < med_d:
                tp_fc_angle *= -1.0

        return tp_fc_angle, (lat_d, med_d)

    def update_patella(self):
        """Update patella position and orientation. Patella is placed a fixed distance
        from the tibia in the tibial Y direction"""

        # align patella acs to tibial acs, centred at midpoint of tibial epicondyles
        ot = 0.5 * (self.tibfib_model.landmark_coords[self.side]['condyle_lat'] +
                    self.tibfib_model.landmark_coords[self.side]['condyle_med'])

        cs_targ = np.array([ot,
                            ot + self.tibfib_model.acs.x,
                            ot + self.tibfib_model.acs.y,
                            ot + self.tibfib_model.acs.z,
                            ])

        cs_source = self.patella_model.acs.unit_array

        t1 = transform3D.directAffine(cs_source, cs_targ)
        self.patella_model.node_coords = transform3D.transformAffine(x=self.patella_model.node_coords, t=t1)
        self.patella_model.update_landmarks_and_regions()
        self.patella_model.update_acs()

        # apply patella shift
        t2 = self.tibfib_model.acs.x * self.patella_model.patella_shift[0] + \
            self.tibfib_model.acs.y * self.patella_model.patella_shift[1] + \
            self.tibfib_model.acs.z * self.patella_model.patella_shift[2]

        self.patella_model.node_coords = self.patella_model.node_coords + t2
        self.patella_model.update_landmarks_and_regions()
        self.patella_model.update_acs()
