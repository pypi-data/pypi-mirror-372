# Main articulated SSM model fitting script when using a train/test set
# 25/01/2023

import os
import time
import numpy as np

from articulated_ssm_both_sides.FitASM import FitASM
from articulated_ssm_both_sides.SSMHandler import SSMHandler
from articulated_ssm_both_sides.LandmarkHandler import LandmarkHandler
from articulated_ssm_both_sides.SegmentationHandler import SegmentationHandler
from articulated_ssm_both_sides.LowerLimb import LowerLimb
from articulated_ssm_both_sides.PLSR import plsr


general_fit_settings = {
    'segm_fit': False,                          # Fit using segmentation data
    'lm_fit': True,                             # Fit using landmark coordinates
    'side': 'left',                             # Either 'left', 'right' or 'both'
    'include_patella': False,                   # Include patella
    'patella_shift': np.array([50, 50, -10]),
    'pc_modes': [0, 1, 2, 3, 4, 5, 6],          # , [[0,1],[0, 1, 2, 3, 4]],        # PC modes to fit (multi fit: [[],[]])
    'mweight':  None,                           # [0.01,0.001], #[1, 0.01],         # Mahalanobis weight (multi fit: [float, float])
    'min_args': {'method': 'Powell'},           # {'method': 'BFGS','jac': False,'bounds': None, 'tol': 1e-6,'options': {'eps': 1e-5}},
    'name': 'test_fit',
    'knee_gap': 5,                              # Minimal gap between femur and tibia knee nodes
    'knee_fixed': False,                        # Fix the knee in initial position (0)
    'allow_knee_adduction_dof': True,           # Allow rotation in VV when placing tibia-fibula
    'allow_knee_adduction_correction': True,    # Allow VV rotation to obtain minimal knee gap
    'x0': None,                                 # Initial parameters for the 1st fit
    'init_pc_weights': None,                    # Initial weights for each mode in the first fit.
    'correct_markers': False,                   # True if motion capture marker used for prediction, False if bone surface landmarks used
    'ssm_name': 'ASM_left_side_train_90',       # name of the statistical shape model to use
    'pred_path': 'train_90',                    # name of the folder in 'pred_meshes' where to save predicted meshes and errors
    'PLSR': False                               # runs a partial least squares regression before articulated shape model prediction
}

# load test list and error files
test_list = sorted((open(r'{}/target_landmarks/test_list_90.txt'.format(os.getcwd()))).read().splitlines())
train_list = sorted((open(r'{}/target_landmarks/train_list_90.txt'.format(os.getcwd()))).read().splitlines())

anthro_data_path = r'{}/target_landmarks/Left_side_all_predictive_factors.csv'.format(os.getcwd())
n = len(test_list)
print("number of test cases:", n)
errors_path = '{}/pred_meshes/{}/{}_lm_errors.txt'.format(os.getcwd(), general_fit_settings['pred_path'], general_fit_settings['ssm_name'])
if os.path.exists(errors_path):
    os.remove(errors_path)
errors = open(errors_path, 'w+')
errors.write('mae_lm,rmse_lm,mweight\n')

if general_fit_settings['PLSR'] is True:
    pred_weights, pred_sd = PLSR.plsr(test_list, train_list, anthro_data_path, general_fit_settings)

for i in range(len(test_list)):
    startTime = time.time()
    case = test_list[i]
    print('starting case:', case)
    if general_fit_settings['PLSR'] is True:
        if isinstance(general_fit_settings['pc_modes'][0], (list, tuple, np.ndarray)):
            general_fit_settings['init_pc_weights'] = pred_sd[:(len(general_fit_settings['pc_modes'][-1])), i]
        else:
            general_fit_settings['init_pc_weights'] = pred_sd[:(len(general_fit_settings['pc_modes'])), i]
            print(general_fit_settings['init_pc_weights'])
    # load the coupled SSM
    ssm_handler = SSMHandler(general_fit_settings)

    # Generate lower limb model
    test_model = LowerLimb(ssm_handler, general_fit_settings)

    if general_fit_settings['side'] == 'both':
        test_model.ll_l.load_bones_and_model()
        test_model.ll_r.load_bones_and_model()
    if general_fit_settings['side'] == 'left':
        test_model.ll_l.load_bones_and_model()
    if general_fit_settings['side'] == 'right':
        test_model.ll_r.load_bones_and_model()

    # Initialize data for minimisation
    fit_data = {}  # Dictionary with data to fit the ASM to

    # load segmentation data to fit to
    if general_fit_settings['segm_fit']:
        segmentations_dir = r'{}/segmentations'.format(os.getcwd())
        segmentation_handler = SegmentationHandler(segmentations_dir, general_fit_settings)
        fit_data['segmentation_handler'] = segmentation_handler

    # load landmark coordinates data to fit to
    if general_fit_settings['lm_fit']:
        target_lms_file = r'{}/target_landmarks/aligned_lms/{}_landmarks_mocap.txt'.format(os.getcwd(), case)
        landmark_names_to_fit = ['ASIS', 'PSIS', 'MEC', 'LEC', 'malleolus_med', 'malleolus_lat']
        landmark_handler = LandmarkHandler(target_lms_file, landmark_names_to_fit, test_model)
        fit_data['landmark_handler'] = landmark_handler

    # Fit articulated SSM
    asm_fitter = FitASM(test_model, general_fit_settings, fit_data, case)
    errors.write(str(asm_fitter.mae_lm)+','+str(asm_fitter.rmse_lm)+','+str(asm_fitter.opt_mweight)+'\n')

    exectutionTime = (time.time() - startTime)
    print('Execution time in seconds: ' + str(exectutionTime))
errors.close()
