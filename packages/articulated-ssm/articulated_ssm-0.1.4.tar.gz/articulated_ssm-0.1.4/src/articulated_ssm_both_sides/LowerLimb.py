from articulated_ssm_both_sides.SSMHandler import SSMHandler
from articulated_ssm_both_sides.LowerLimbSide import LowerLimbSide


class LowerLimb:
    def __init__(self, general_fit_settings):
        self.include_patella = general_fit_settings['include_patella']
        # self.ssm_handler = ssm_handler

        self.lower_limb_settings = {'dof': {'N_PARAMS_PELVIS': 6,
                                            'N_PARAMS_HIP': 3,
                                            'N_PARAMS_KNEE': 2}, 'directions': {'left': {'hip_flex_coeff': 1.0,
                                                                                         'hip_add_coeff': -1.0,
                                                                                         'hip_rot_coeff': -1.0,
                                                                                         'knee_flex_coeff': -1.0,
                                                                                         'knee_add_coeff': -1.0},
                                                                                'right': {'hip_flex_coeff': 1.0,
                                                                                          'hip_add_coeff': 1.0,
                                                                                          'hip_rot_coeff': 1.0,
                                                                                          'knee_flex_coeff': -1.0,
                                                                                          'knee_add_coeff': 1.0}}}

        ssm_handler_l = SSMHandler(general_fit_settings, 0, side='left')
        ssm_handler_r = SSMHandler(general_fit_settings, 0, side='right')
        self.ll_l = LowerLimbSide('left', ssm_handler_l, general_fit_settings, self.lower_limb_settings)
        self.ll_r = LowerLimbSide('right', ssm_handler_r, general_fit_settings, self.lower_limb_settings)
