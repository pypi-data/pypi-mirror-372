import numpy as np
from gias3.registration import alignment_fitting
from gias3.common import transform3D
from numpy.linalg import inv
from scipy import optimize

from articulated_ssm_both_sides import SaveMesh


class FitASM:
    def __init__(self, ll_model, general_fit_settings, fit_data, case, side):
        self.case = case
        self.pred_path = general_fit_settings['pred_path']
        self.segm_fit = general_fit_settings['segm_fit']
        self.lm_fit = general_fit_settings['lm_fit']
        self.side = side
        self.pc_modes = general_fit_settings['pc_modes']
        self.mweight = general_fit_settings['mweight']
        self.min_args = general_fit_settings['min_args']
        self.x0 = general_fit_settings['x0']
        self.init_pc_weights = general_fit_settings['init_pc_weights']
        self.fit_data = fit_data
        if self.segm_fit:
            self.segmentations = fit_data['segmentation_handler'].segmentations
        if self.lm_fit:
            if self.side == 'left':
                self.target_landmarks = self.fit_data['landmark_handler_l'].target_landmarks
                self.source_landmarks = self.fit_data['landmark_handler_l'].source_landmarks
            elif self.side == 'right':
                self.target_landmarks = self.fit_data['landmark_handler_r'].target_landmarks
                self.source_landmarks = self.fit_data['landmark_handler_r'].source_landmarks
        self.ll_model = ll_model

        self.multi_fit = None
        self.n_iterations = None
        self.N_PARAMS_PELVIS = self.ll_model.lower_limb_settings['dof']['N_PARAMS_PELVIS']
        self.N_PARAMS_HIP = self.ll_model.lower_limb_settings['dof']['N_PARAMS_HIP']
        self.N_PARAMS_KNEE = self.ll_model.lower_limb_settings['dof']['N_PARAMS_KNEE']
        self.N_PARAMS_RIGID = self.N_PARAMS_PELVIS + self.N_PARAMS_HIP + self.N_PARAMS_KNEE

        self.x_history = []

        self.initiate_fitting()

    def lower_limb_fit(self, x0, minimise_args, pc_modes_it, mweight_it):

        x_hist_it = []

        def _x_splitter(x):
            if self.side == 'both':
                pc_weights_index_L = len(pc_modes_it)
                pc_weights_index_R = pc_weights_index_L + len(pc_modes_it)
                pel_rigid_index_L = pc_weights_index_R + self.N_PARAMS_PELVIS
                pel_rigid_index_R = pel_rigid_index_L + self.N_PARAMS_PELVIS
                hip_rot_x_index_L = pel_rigid_index_R + self.N_PARAMS_HIP
                knee_rot_x_index_L = hip_rot_x_index_L + self.N_PARAMS_KNEE
                hip_rot_x_index_R = knee_rot_x_index_L + self.N_PARAMS_HIP
                knee_rot_x_index_R = hip_rot_x_index_R + self.N_PARAMS_KNEE

                x_split = [x[:pc_weights_index_L],                      # pc weights left side
                           x[pc_weights_index_L:pc_weights_index_R],    # pc weights right side
                           x[pc_weights_index_R:pel_rigid_index_L],     # init rigid pelvis L
                           x[pel_rigid_index_L:pel_rigid_index_R],      # init rigid pelvis L
                           x[pel_rigid_index_R:hip_rot_x_index_L],      # hip left
                           x[hip_rot_x_index_L:knee_rot_x_index_L],     # knee left
                           x[knee_rot_x_index_L:hip_rot_x_index_R],     # hip right
                           x[hip_rot_x_index_R:]]                       # knee right

            else:
                hip_rigid_x_index = len(pc_modes_it)
                hip_rot_x_index = hip_rigid_x_index + self.N_PARAMS_PELVIS
                knee_rot_x_index = hip_rot_x_index + self.N_PARAMS_HIP

                x_split = [x[:hip_rigid_x_index],                   # pc weights
                           x[hip_rigid_x_index:hip_rot_x_index],    # init rigid pelvis
                           x[hip_rot_x_index:knee_rot_x_index],     # hip left
                           x[knee_rot_x_index:]]                    # knee left
            return x_split

        def objective_function(x):
            x_split = _x_splitter(x)

            if self.side == 'left':
                self.ll_model.ll_l.update_all_models(x_split[0], pc_modes_it, x_split[1], x_split[2], x_split[3])
            elif self.side == 'right':
                self.ll_model.ll_r.update_all_models(x_split[0], pc_modes_it, x_split[1], x_split[2], x_split[3])
            elif self.side == 'both':
                self.ll_model.ll.update_all_models(x_split[0], x_split[1], pc_modes_it, x_split[2], x_split[3],
                                                   x_split[4], x_split[5], x_split[6], x_split[7])
                # self.ll_model.ll_l.update_all_models(x_split[0], pc_modes_it, x_split[2], x_split[3], x_split[4])
                # self.ll_model.ll_r.update_all_models(x_split[1], pc_modes_it, x_split[2], x_split[5], x_split[6])

            # Calculate total fitting error
            # calc squared mahalanobis distance
            m2 = 0.0
            if self.mweight is not None:
                m2 = mweight_it * ((x_split[0] ** 2).sum())
                if self.side == 'both':
                    m2 = ((mweight_it * ((x_split[0] ** 2).sum())) + (mweight_it * ((x_split[1] ** 2).sum()))) / 2
                    print(m2)
                maha_errors.append(m2)

            # Calculate distance to segmentations
            if self.segm_fit:
                rmse = self.fit_data['segmentation_handler'].average_rmse_segmentations(self.ll_model)
                print(rmse)
                total_error = rmse + m2
                dist_errors.append(rmse)

            if self.lm_fit:
                if self.side == 'left':
                    self.fit_data['landmark_handler_l'].update_source_landmarks_dict()
                    target_lms_list, source_lms_list = self.fit_data['landmark_handler_l'].obtain_landmark_lists_from_dict()
                elif self.side == 'right':
                    self.fit_data['landmark_handler_r'].update_source_landmarks_dict()
                    target_lms_list, source_lms_list = self.fit_data[
                        'landmark_handler_r'].obtain_landmark_lists_from_dict()
                # calc sum of squared distance between target and source landmarks
                ssdist = ((np.asarray(target_lms_list) - np.asarray(source_lms_list)) ** 2.0).sum()  # in mm
                # print('ssdist = {}mm'.format(ssdist))
                landmark_dist = \
                    np.linalg.norm((np.asarray(target_lms_list) - np.asarray(source_lms_list)), axis=1)
                mae = np.mean(landmark_dist)
                rmse = np.sqrt(np.mean(landmark_dist ** 2.0))  # in mm
                print('rmse = {}mm'.format(rmse))
                # total_error = ssdist + m2
                total_error = rmse + m2
                # print('m2:', m2)
                # dist_errors.append(ssdist)
                dist_errors.append(rmse)

            total_errors.append(total_error)
            x_input.append(x)
            return total_error

        # start optimisation
        if x0 is None:
            x0 = self._make_x0(len(pc_modes_it))
        else:
            x0 = np.array(x0)

        dist_errors = []
        maha_errors = []
        total_errors = []
        x_input = []

        opt_results_1 = optimize.minimize(objective_function, x0, **minimise_args)
        xopt1_split = _x_splitter(opt_results_1['x'])
        x_hist_it.append(xopt1_split)

        if self.side == 'left':
            self.ll_model.ll_l.update_all_models(xopt1_split[0],
                                                 pc_modes_it,
                                                 xopt1_split[1],
                                                 xopt1_split[2],
                                                 xopt1_split[3])

        elif self.side == 'right':
            self.ll_model.ll_r.update_all_models(xopt1_split[0],
                                                 pc_modes_it,
                                                 xopt1_split[1],
                                                 xopt1_split[2],
                                                 xopt1_split[3])
        elif self.side == 'both':
            self.ll_model.ll.update_all_models(xopt1_split[0],
                                               xopt1_split[1],
                                               pc_modes_it,
                                               xopt1_split[2],
                                               xopt1_split[3],
                                               xopt1_split[4],
                                               xopt1_split[5],
                                               xopt1_split[6],
                                               xopt1_split[7])

        if self.lm_fit:
            if self.side == 'left':
                self.fit_data['landmark_handler_l'].update_source_landmarks_dict()
                opt_target_lms_list, opt_source_lms_list = \
                    self.fit_data['landmark_handler_l'].obtain_landmark_lists_from_dict()
            elif self.side == 'right':
                self.fit_data['landmark_handler_r'].update_source_landmarks_dict()
                opt_target_lms_list, opt_source_lms_list = \
                    self.fit_data['landmark_handler_r'].obtain_landmark_lists_from_dict()
            SaveMesh.save_mesh_and_lms(self.ll_model, opt_source_lms_list, opt_target_lms_list, self.case,
                                       self.pred_path, self.side)
            opt_landmark_dist = \
                np.linalg.norm((np.asarray(opt_target_lms_list) - np.asarray(opt_source_lms_list)), axis=1)
            opt_ssdist = (opt_landmark_dist ** 2).sum()
            mae = np.mean(opt_landmark_dist)
            opt_landmark_rmse = np.sqrt(np.mean(opt_landmark_dist ** 2.0))
            opt_mahalanobis_dist = np.sqrt((xopt1_split[0] ** 2.0).sum())
            print('mae = {}mm rmse = {}mm ssdist = {} mdist = {}'.format(mae, opt_landmark_rmse, opt_ssdist,
                                                                         opt_mahalanobis_dist))
            self.mae_lm = mae
            self.rmse_lm = opt_landmark_rmse
            self.ssdist = opt_ssdist
            self.opt_mweight = opt_mahalanobis_dist

        if self.segm_fit:
            for index in range(0, len(x_input)):
                if np.array_equal(np.array(x_input[index]), np.array(opt_results_1.x)):
                    opt_index = index

            print('opt_dist_error = {}'.format(dist_errors[opt_index]))
            print('opt_maha_error = {}'.format(maha_errors[opt_index]))
            print('opt_total_error = {}'.format(total_errors[opt_index]))

        return x_hist_it

    def initiate_fitting(self):
        if isinstance(self.pc_modes[0], (list, tuple, np.ndarray)):
            self.multi_fit = True
            self.n_iterations = len(self.pc_modes)
            self.min_args = [self.min_args, ] * self.n_iterations
        else:
            self.multi_fit = False

        total_rigid_params = self.N_PARAMS_RIGID

        if not self.multi_fit:
            print('Running single lower limb fit')
            if self.mweight is not None:
                return self.lower_limb_fit(self.x0, self.min_args, self.pc_modes, self.mweight[0])
            else:
                return self.lower_limb_fit(self.x0, self.min_args, self.pc_modes, self.mweight)
        else:
            print('Running {}-stage lower limb fit'.format(self.n_iterations))
            if self.x0 is not None:
                self.x_history.append(self.x0)

            for it in range(self.n_iterations):
                if it > 0:
                    n_modes_diff = len(self.pc_modes[it]) - len(self.pc_modes[it - 1])
                    if self.init_pc_weights:
                        self.init_pc_weights = self.init_pc_weights[:(len(self.pc_modes[it]))]
                        init_pc_weights_extra = self.init_pc_weights[len(self.pc_modes[it - 1]):]
                    else:
                        init_pc_weights_extra = np.zeros(len(self.pc_modes[it]))
                    if n_modes_diff > 0:
                        x0 = np.hstack([np.hstack([self.x0[:-total_rigid_params],
                                                   init_pc_weights_extra]),
                                        self.x0[-total_rigid_params:]])
                    elif n_modes_diff < 0:
                        x0 = np.hstack([self.x0[:len(self.pc_modes)], self.x0[-total_rigid_params:]])
                else:
                    x0 = self.x0

                if self.mweight is not None:
                    x_hist_it = self.lower_limb_fit(x0=x0,
                                                    minimise_args=self.min_args[it],
                                                    pc_modes_it=self.pc_modes[it],
                                                    mweight_it=self.mweight[it])
                else:
                    x_hist_it = self.lower_limb_fit(x0=x0,
                                                    minimise_args=self.min_args[it],
                                                    pc_modes_it=self.pc_modes[it],
                                                    mweight_it=self.mweight)

                self.x0 = np.hstack(x_hist_it[-1])
                self.x_history.append(x_hist_it[-1])

    def _make_x0(self, npcs):
        """ Generate initial parameters for articulated SSM fitting. The pelvis landmarks or segmentations are rigidly
        registered to get initial rigid transformation parameters.
        """
        if self.segm_fit:
            segmentation_vertices = []
            ssm_mean_vertices = []
            ssm_mean = self.ll_model.ssm_handler.ssm_mean_split_per_bone
            [segmentation_vertices.append(self.segmentations[key].v) for key in self.segmentations.keys()]
            [ssm_mean_vertices.append(ssm_mean[key]) for key in self.segmentations.keys()]
            _source = np.vstack(segmentation_vertices)
            _target = np.vstack(ssm_mean_vertices)

            rx, ry, rz = [0, 0, 0]
            t0 = np.hstack([_target.mean(0) - _source.mean(0), [rx, ry, rz], ])
            t_opt, data_fitted = alignment_fitting.fitDataRigidEPDP(data=_source, target=_target, t0=t0)

            # apply inverse transformation (to stick to segmentation position)
            point_of_rotation = _source.mean(0)  # Euclidean mean of all points in data
            affine_matrix = transform3D.calcRigidAffineMatrix(t=t_opt, com=point_of_rotation)
            inv_affine_matrix = inv(affine_matrix)
            target_transformed = transform3D.transformAffine(x=_target, t=inv_affine_matrix)

            if self.side == 'left':
                ll_model_side = self.ll_model.ll_l
            else:
                ll_model_side = self.ll_model.ll_r

            init_rigid, data_fitted1 = alignment_fitting.fitRigid(data=_target,
                                                                  target=target_transformed,
                                                                  rotcentre=ll_model_side.pelvis_model.acs.o)

        elif self.lm_fit:
            _target = np.array([self.target_landmarks['left']['ASIS'],
                                self.target_landmarks['left']['PSIS'],
                                self.target_landmarks['right']['ASIS'],
                                self.target_landmarks['right']['PSIS'],
                                self.target_landmarks['sacrum']['SAC']])
            _source = np.array([self.source_landmarks['left']['ASIS'],
                                self.source_landmarks['left']['PSIS'],
                                self.source_landmarks['right']['ASIS'],
                                self.source_landmarks['right']['PSIS'],
                                self.source_landmarks['sacrum']['SAC']])

            rx, ry, rz = [0, 0, 0]
            t0 = np.hstack([_target.mean(0) - _source.mean(0), [rx, ry, rz], ])
            rot_centre = 0.5 * (_source[0] + _source[2])
            init_rigid, fitted_landmarks, fit_errors = alignment_fitting.fitRigid(_source,
                                                                                  _target,
                                                                                  t0=t0,
                                                                                  rotcentre=rot_centre,
                                                                                  xtol=1e-9,
                                                                                  maxfev=1e6,
                                                                                  maxfun=1e6,
                                                                                  epsfcn=1e-6,
                                                                                  output_errors=1)

        if self.init_pc_weights is None:
            init_pc_weights = [0] * npcs
            # init_pc_weights = np.array(float(self.ll_model.ssm_handler.coupled_pcs.weights[:npcs]))
        else:
            init_pc_weights = self.init_pc_weights
        if self.side == 'left':
            model = self.ll_model.ll_l
        elif self.side == 'right':
            model = self.ll_model.ll_r

        if self.side == 'both':
            init_x = np.hstack([init_pc_weights,
                                init_pc_weights,
                                init_rigid,
                                init_rigid,
                                [0, ] * self.ll_model.ll.N_PARAMS_HIP,
                                [0, ] * self.ll_model.ll.N_PARAMS_KNEE,
                                [0, ] * self.ll_model.ll.N_PARAMS_HIP,
                                [0, ] * self.ll_model.ll.N_PARAMS_KNEE])
        else:
            init_x = np.hstack([init_pc_weights,
                                init_rigid,
                                [0, ] * model.N_PARAMS_HIP,
                                [0, ] * model.N_PARAMS_KNEE])

        return init_x
