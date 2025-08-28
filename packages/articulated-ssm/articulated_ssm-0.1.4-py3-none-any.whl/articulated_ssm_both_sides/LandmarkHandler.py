import numpy as np
import articulated_ssm_both_sides.correct_markers as cm

landmark_map = {
    'ASI': 'ASIS',
    'PSI': 'PSIS',
    'KNE': 'LEC',
    'KNEM': 'MEC',
    'ANK': 'malleolus_lat',
    'MED': 'malleolus_med'
}


class LandmarkHandler:
    def __init__(self, landmarks, landmark_names_to_fit, ll_model, correct_markers, side, marker_radius, demo_factors):
        self.landmark_names_to_fit = landmark_names_to_fit
        self.side = side
        self.ll_model = ll_model
        self.target_landmarks_original = {}
        self.target_landmarks = dict(left={}, right={}, sacrum={})
        self.source_landmarks = dict(left={}, right={}, sacrum={})
        self.update_source_landmarks_dict()
        self.convert_landmark_names(landmarks)
        self.create_target_landmarks_dict()
        if correct_markers:
            cm.correct_target_markers(self.target_landmarks, side, demo_factors, marker_radius)

    def convert_landmark_names(self, landmarks):
        complete_map = {}
        for side in ['left', 'right']:
            for key, value in landmark_map.items():
                complete_map[f"{side[0].upper()}{key}"] = f"{side}-{value}"
        self.target_landmarks_original = {complete_map.get(k, k): v for k, v in landmarks.items()}

    def create_target_landmarks_dict(self):
        for landmark_name in self.landmark_names_to_fit:
            for key in self.target_landmarks_original.keys():
                if landmark_name in key:
                    if self.side in key:
                        self.target_landmarks[self.side].update({landmark_name: self.target_landmarks_original[key]})
        if self.side == 'right':
            self.target_landmarks['left']['ASIS'] = self.target_landmarks_original['left-ASIS']
            self.target_landmarks['left']['PSIS'] = self.target_landmarks_original['left-PSIS']
        if self.side == 'left':
            self.target_landmarks['right']['ASIS'] = self.target_landmarks_original['right-ASIS']
            self.target_landmarks['right']['PSIS'] = self.target_landmarks_original['right-PSIS']

        psis_left = self.target_landmarks['left']['PSIS']
        psis_right = self.target_landmarks['right']['PSIS']
        self.target_landmarks['sacrum']['SAC'] = [((psis_left[0] + psis_right[0]) / 2),
                                                  ((psis_left[1] + psis_right[1]) / 2),
                                                  ((psis_left[2] + psis_right[2]) / 2)]

    def update_source_landmarks_dict(self):
        # SSM fitted landmark coordinates
        if self.side == 'left':
            model = self.ll_model.ll_l
            sides = ['left']
        elif self.side == 'right':
            model = self.ll_model.ll_r
            sides = ['right']
        else:
            model = self.ll_model.ll
            sides = ['left', 'right']

        for side in sides:
            if self.side == 'both':
                if side == 'left':
                    pel = model.pelvis_model_l
                    fem = model.femur_model_l
                    tib = model.tibfib_model_l
                    if model.include_patella:
                        pat = model.patella_model_l
                else:
                    pel = model.pelvis_model_r
                    fem = model.femur_model_r
                    tib = model.tibfib_model_r
                    if model.include_patella:
                        pat = model.patella_model_r
            else:
                pel = model.pelvis_model
                fem = model.femur_model
                tib = model.tibfib_model
                if model.include_patella:
                    pat = model.patella_model
            for landmark_name in self.landmark_names_to_fit:
                for key in pel.landmark_coords['left'].keys():
                    if landmark_name in key:
                        self.source_landmarks['left'].update(
                            {landmark_name: pel.landmark_coords['left'][key]})
                for key in pel.landmark_coords['right'].keys():
                    if landmark_name in key:
                        self.source_landmarks['right'].update(
                            {landmark_name: pel.landmark_coords['right'][key]})
                for key in fem.landmark_coords[side].keys():
                    if landmark_name in key:
                        self.source_landmarks[side].update(
                            {landmark_name: fem.landmark_coords[side][key]})
                for key in tib.landmark_coords[side].keys():
                    if landmark_name in key:
                        self.source_landmarks[side].update(
                            {landmark_name: tib.landmark_coords[side][key]})
                if model.include_patella:
                    for key in pat.landmark_coords[side].keys():
                        if landmark_name in key:
                            self.source_landmarks[side].update(
                                {landmark_name: pat.landmark_coords[side][key]})

        psis_left = self.source_landmarks['left']['PSIS']
        psis_right = self.source_landmarks['right']['PSIS']
        self.source_landmarks['sacrum']['SAC'] = [((psis_left[0] + psis_right[0]) / 2),
                                                  ((psis_left[1] + psis_right[1]) / 2),
                                                  ((psis_left[2] + psis_right[2]) / 2)]

    def update_source_landmarks_dict_old(self):
        # SSM fitted landmark coordinates
        if self.side == 'left':
            model_list = [self.ll_model.ll_l]
        elif self.side == 'right':
            model_list = [self.ll_model.ll_r]
        else:
            model_list = [self.ll_model.ll_l, self.ll_model.ll_r]
        for model in model_list:
            side = model.side
            for landmark_name in self.landmark_names_to_fit:
                for key in model.pelvis_model.landmark_coords[side].keys():
                    if landmark_name in key:
                        self.source_landmarks[side].update(
                            {landmark_name: model.pelvis_model.landmark_coords[side][key]})
                for key in model.femur_model.landmark_coords[side].keys():
                    if landmark_name in key:
                        self.source_landmarks[side].update(
                            {landmark_name: model.femur_model.landmark_coords[side][key]})
                for key in model.tibfib_model.landmark_coords[side].keys():
                    if landmark_name in key:
                        self.source_landmarks[side].update(
                            {landmark_name: model.tibfib_model.landmark_coords[side][key]})
                if model.include_patella:
                    for key in model.patella_model.landmark_coords[side].keys():
                        if landmark_name in key:
                            self.source_landmarks[side].update(
                                {landmark_name: model.patella_model.landmark_coords[side][key]})
        psis_left = self.source_landmarks['left']['PSIS']
        psis_right = self.source_landmarks['right']['PSIS']
        self.source_landmarks['sacrum']['SAC'] = [((psis_left[0] + psis_right[0]) / 2),
                                                  ((psis_left[1] + psis_right[1]) / 2),
                                                  ((psis_left[2] + psis_right[2]) / 2)]

    def obtain_landmark_lists_from_dict(self):
        target_lms_list = []
        source_lms_list = []
        if self.side == 'both':
            for side in ['left', 'right']:
                for landmark_name in self.landmark_names_to_fit:
                    target_lms_list.append(self.target_landmarks[side][landmark_name])
                    source_lms_list.append(self.source_landmarks[side][landmark_name])
        else:
            for landmark_name in self.landmark_names_to_fit:
                if landmark_name == 'SAC':
                    target_lms_list.append(self.target_landmarks['sacrum'][landmark_name])
                    source_lms_list.append(self.source_landmarks['sacrum'][landmark_name])
                    continue
                target_lms_list.append(self.target_landmarks[self.side][landmark_name])
                source_lms_list.append(self.source_landmarks[self.side][landmark_name])
            if self.side == 'left':
                target_lms_list.append(self.target_landmarks['right']['ASIS'])
                target_lms_list.append(self.target_landmarks['right']['PSIS'])
                source_lms_list.append(self.source_landmarks['right']['ASIS'])
                source_lms_list.append(self.source_landmarks['right']['PSIS'])
            elif self.side == 'right':
                target_lms_list.append(self.target_landmarks['left']['ASIS'])
                target_lms_list.append(self.target_landmarks['left']['PSIS'])
                source_lms_list.append(self.source_landmarks['left']['ASIS'])
                source_lms_list.append(self.source_landmarks['left']['PSIS'])
        return target_lms_list, source_lms_list
