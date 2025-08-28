import numpy as np
from copy import deepcopy
from gias3.common import math
from articulated_ssm_both_sides.PLSR import rf_predict
import os


### moved this into function instead ##
#average skin padding for each landmark in our dataset
#SKIN_PADDING_ASIS = 10
#SKIN_PADDING_PSIS = 26
#SKIN_PADDING_LEC = 14
#SKIN_PADDING_MEC = 16
#SKIN_PADDING_LMAL = 3
#SKIN_PADDING_MMAL = 5

#MARKER_RADIUS = 0   # 7mm marker radius + 2mm marker plate

def normaliseVector(v):
    return v / np.linalg.norm(v)


def correct_target_markers(target_markers_per_bone, side, demographic_factors, marker_radius=9):
    """Correct the target marker location using the marker radius and skin padding
    target_markers_per_bone [dict]: Dictionary with the bones, marker_names and coordinates of each target marker per
                                    side:
                                    target_markers_per_bone = {bone: {'left': {markername1: xyz,
                                                                               markername2: xyz},
                                                                      'right': {markername1: xyz,
                                                                                markername2: xyz}}}
    plot [boolean]: True = plot results, False = do not plot results
    """

    MARKER_RADIUS = marker_radius
    if demographic_factors is None:
        SKIN_PADDING_ASIS = 10
        SKIN_PADDING_PSIS = 26
        SKIN_PADDING_LEC = 14
        SKIN_PADDING_MEC = 16
        SKIN_PADDING_LMAL = 3
        SKIN_PADDING_MMAL = 5
    else:
        if side == 'left':
            predictors = rf_predict(demographic_factors.iloc[:, [0, 1, 2, 4, 5]],
                                    r'{}/rf_files/rf_model_lm_left_side.pkl'.format(os.path.dirname(__file__)))
        else:
            predictors = rf_predict(demographic_factors.iloc[:, [0, 1, 2, 4, 7, 8]],
                                    r'{}/rf_files/rf_model_lm_right_side.pkl'.format(os.path.dirname(__file__)))
        SKIN_PADDING_ASIS = predictors[0]
        SKIN_PADDING_PSIS = predictors[1]
        SKIN_PADDING_LEC = predictors[2]
        SKIN_PADDING_MEC = predictors[3]
        SKIN_PADDING_LMAL = predictors[4]
        SKIN_PADDING_MMAL = predictors[5]

    original_target_markers_per_bone = deepcopy(target_markers_per_bone)

    oa = (np.asarray(target_markers_per_bone['left']['ASIS']) +
          np.asarray(target_markers_per_bone['right']['ASIS'])) / 2
    op = (np.asarray(target_markers_per_bone['left']['PSIS']) +
          np.asarray(target_markers_per_bone['right']['PSIS'])) / 2

    # determine forward direction (x) for pelvis
    z = normaliseVector(
        np.asarray(target_markers_per_bone['right']['ASIS']) - np.asarray(target_markers_per_bone['left']['ASIS']))
    n1 = normaliseVector(np.cross(np.asarray(target_markers_per_bone['right']['ASIS']) - op,
                                  np.asarray(target_markers_per_bone['left']['ASIS']) - op))
    ap_axis = normaliseVector(np.cross(n1, z))

    if side == 'left':
        ml_axis_fem = math.norm(np.asarray(target_markers_per_bone['left']['MEC']) -
                                np.asarray(target_markers_per_bone['left']['LEC']))
        ml_axis_tib = math.norm(np.asarray(target_markers_per_bone['left']['malleolus_med']) -
                                np.asarray(target_markers_per_bone['left']['malleolus_lat']))
        for side in target_markers_per_bone.keys():
            for lm_name in target_markers_per_bone[side].keys():
                if 'ASIS' in lm_name:  # Move marker location posteriorly
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ap_axis * (MARKER_RADIUS + SKIN_PADDING_ASIS)
                elif 'PSIS' in lm_name or lm_name == 'SAC':  # Move marker location anteriorly
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ap_axis * (MARKER_RADIUS + SKIN_PADDING_PSIS)
                elif lm_name == 'MEC':  # Move marker location laterally
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ml_axis_fem * (MARKER_RADIUS + SKIN_PADDING_MEC)
                elif lm_name == 'LEC':  # Move marker location medially
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ml_axis_fem * (MARKER_RADIUS + SKIN_PADDING_LEC)
                elif lm_name == 'malleolus_med':  # Move marker location laterally
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ml_axis_tib * (MARKER_RADIUS + SKIN_PADDING_MMAL)
                elif lm_name == 'malleolus_lat':  # Move marker location medially
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ml_axis_tib * (MARKER_RADIUS + SKIN_PADDING_LMAL)
                else:
                    print(lm_name)
                    print('Error in skin padding and marker radius correction')
                    input()

    elif side == 'right':
        ml_axis_fem = math.norm(np.asarray(target_markers_per_bone['right']['LEC']) -
                                np.asarray(target_markers_per_bone['right']['MEC']))
        ml_axis_tib = math.norm(np.asarray(target_markers_per_bone['right']['malleolus_lat']) -
                                np.asarray(target_markers_per_bone['right']['malleolus_med']))
        for side in target_markers_per_bone.keys():
            for lm_name in target_markers_per_bone[side]:
                if 'ASIS' in lm_name:  # Move marker location posteriorly
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ap_axis * (MARKER_RADIUS + SKIN_PADDING_ASIS)
                elif 'PSIS' in lm_name or lm_name == 'SAC':  # Move marker location anteriorly
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ap_axis * (MARKER_RADIUS + SKIN_PADDING_PSIS)
                elif lm_name == 'MEC':  # Move marker location laterally
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ml_axis_fem * (MARKER_RADIUS + SKIN_PADDING_MEC)
                elif lm_name == 'LEC':  # Move marker location medially
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ml_axis_fem * (MARKER_RADIUS + SKIN_PADDING_LEC)
                elif lm_name == 'malleolus_med':  # Move marker location laterally
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] + \
                        ml_axis_tib * (MARKER_RADIUS + SKIN_PADDING_MMAL)
                elif lm_name == 'malleolus_lat':  # Move marker location medially
                    target_markers_per_bone[side][lm_name] = \
                        target_markers_per_bone[side][lm_name] - \
                        ml_axis_tib * (MARKER_RADIUS + SKIN_PADDING_LMAL)
                else:
                    print('Error in skin padding and marker radius correction')
