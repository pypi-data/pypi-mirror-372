# Main articulated SSM model fitting script
# 25/01/2023

import os
import numpy as np

from articulated_ssm_both_sides.FitASM_2 import FitASM
from articulated_ssm_both_sides.LandmarkHandler import LandmarkHandler
from articulated_ssm_both_sides.SegmentationHandler import SegmentationHandler
from articulated_ssm_both_sides.LowerLimb import LowerLimb
from articulated_ssm_both_sides.PLSR import pls_predict_PC

general_fit_settings = {
    'segm_fit': False,  # Fit using segmentation data
    'lm_fit': True,  # Fit using landmark coordinates
    'include_patella': False,  # Include patella
    'patella_shift': np.array([50, 50, -10]),
    'pc_modes': [[0], [0, 1, 2, 3]],  # , [[0,1],[0, 1, 2, 3, 4]],    # PC modes to fit (multi fit: [[],[]])
    'mweight': [1, 0.0001],  # [1, 0.01],                    # Mahalanobis weight (multi fit: [float, float])
    'min_args': {'method': 'Powell', 'options': {'xtol': 1e-3, 'ftol': 1e-4, 'maxiter': 50, 'disp': False}},
    # {'method': 'BFGS','jac': False,'bounds': None, 'tol': 1e-6,'options': {'eps': 1e-5}},
    'knee_gap': 5,  # Minimal gap between femur and tibia knee nodes
    'knee_fixed': False,  # Fix the knee in initial position (0)
    'allow_knee_adduction_dof': True,  # Allow rotation in VV when placing tibia-fibula
    'allow_knee_adduction_correction': True,  # Allow VV rotation to obtain minimal knee gap
    'x0': None,  # Initial parameters for the 1st fit
    'init_pc_weights': None,  # Initial weights for each mode in the first fit.
    'correct_markers': True,  # if motion capture markers are used for prediction: True
    'PLSR': False,  # if a partial least squares regression is used to provide an initial guess to shape model
}


def run_asm(marker_data, output_directory, demo_factors, marker_radius):
    """
    Main entry point for ASM fitting process. Takes a dictionary containing the landmark positions
    defining a single TRC frame.

    :param marker_data: A dictionary containing the landmark positions defining a single TRC frame.
    :param output_directory: The path to the directory where the mesh files should be saved.
    """

    # Generate and load lower limb model.
    lower_limb_model = LowerLimb(general_fit_settings)
    lower_limb_model.ll_l.load_bones_and_model()
    lower_limb_model.ll_r.load_bones_and_model()

    # Load landmark coordinates data to fit to.
    fit_data = landmark_fit(lower_limb_model, marker_data, marker_radius, demo_factors)

    # Produce an initial guess for the pc weights to bound the model
    # need to add verification here that all demo factors are present
    pc_pred_l = pls_predict_PC(demo_factors.iloc[:, [1, 4]],
                           r'{}/rf_files/pls_model_PC_left_side.pkl'.format(os.path.dirname(__file__)),
                           lower_limb_model.ll_l.ssm_handler.coupled_pcs.weights)
    pc_pred_r = pls_predict_PC(demo_factors.iloc[:, [1, 4]],
                           r'{}/rf_files/pls_model_PC_right_side.pkl'.format(os.path.dirname(__file__)),
                           lower_limb_model.ll_r.ssm_handler.coupled_pcs.weights)

    asm_fitter_l = FitASM(lower_limb_model, general_fit_settings, fit_data, output_directory, 'left', pc_pred_l)
    asm_fitter_r = FitASM(lower_limb_model, general_fit_settings, fit_data, output_directory, 'right', pc_pred_r)

    write_fit_metrics(asm_fitter_l, asm_fitter_r, output_directory)


def landmark_fit(lower_limb_model, marker_data, marker_radius, demo_factors = None):
    landmark_names_to_fit = ['ASIS', 'PSIS', 'SAC', 'LEC', 'MEC', 'malleolus_med', 'malleolus_lat']

    fit_data = {}
    for side in ['left', 'right']:
        fit_data[f'landmark_handler_{side[0]}'] = LandmarkHandler(
            marker_data, landmark_names_to_fit, lower_limb_model, general_fit_settings['correct_markers'], side, marker_radius, demo_factors
        )

    return fit_data


def segmentation_fit(segmentations_directory):
    segmentation_handler = SegmentationHandler(segmentations_directory, general_fit_settings)
    fit_data = {'segmentation_handler': segmentation_handler}

    return fit_data


def plsr_fit(anthro_data_path, case_data):
    """
    `case_data` should be a numpy array containing the values: 'height', ASIS width, femur length, tibia length.
    """
    pred_weights, pred_sd = plsr(case_data, anthro_data_path, general_fit_settings)
    if isinstance(general_fit_settings['pc_modes'][0], (list, tuple, np.ndarray)):
        general_fit_settings['init_pc_weights'] = pred_sd[:(len(general_fit_settings['pc_modes'][-1]))]
    else:
        general_fit_settings['init_pc_weights'] = pred_sd[:(len(general_fit_settings['pc_modes']))]
        print(general_fit_settings['init_pc_weights'])


def write_fit_metrics(asm_fitter_l, asm_fitter_r, output_directory):
    metrics_path = os.path.join(output_directory, "asm_fit_metrics.txt")
    with open(metrics_path, "w") as metrics_file:
        metrics_file.write("MAE, RMSE, m_weight\n")
        metrics_file.write(f"{asm_fitter_l.mae_lm}, {asm_fitter_l.rmse_lm}, {asm_fitter_l.opt_mweight}\n")
        metrics_file.write(f"{asm_fitter_r.mae_lm}, {asm_fitter_r.rmse_lm}, {asm_fitter_r.opt_mweight}\n")
