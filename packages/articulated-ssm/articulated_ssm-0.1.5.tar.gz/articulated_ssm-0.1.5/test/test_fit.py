import os
import pandas as pd

from articulated_ssm_both_sides.MainASM import run_asm


def test(file_name, demo_factors, marker_radius):
    test_directory = os.path.dirname(__file__)
    data_directory = os.path.join(test_directory, "data")
    marker_data_path = os.path.join(data_directory, file_name)
    marker_data = {}
    with open(marker_data_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 4:
                label = parts[0]
                coords = list(map(float, parts[1:]))
                marker_data[label] = coords

    case_name = os.path.splitext(file_name)[0]
    output_directory = os.path.join(test_directory, "_output", case_name)

    run_asm(marker_data, output_directory, demo_factors, marker_radius)


def to_subject_df(values):
    feature_columns = [
        'Age', 'Height', 'Mass', 'Sex', 'ASIS_width',
        'left_epicon_width', 'left_malleolar_width',
        'right_epicon_width', 'right_malleolar_width'
    ]

    return pd.DataFrame([values], columns=feature_columns)


if __name__ == "__main__":
    test("06_1064.txt", to_subject_df([11, 145, 41, 2, 179.5, 71.2, 60.6, 71.5, 58.5]), 0)
    test("10_1347_skin_surface_lms.txt", to_subject_df(
        [9, 135, 38.0, 2, 175.31953869525000, 66.98745752495950,
         58.05935101397360, 67.026293783983, 55.90857549855320]), 0)
    test("13_1096_skin_surface_lms.txt", to_subject_df(
        [5, 104, 16.0, 2, 141.3784538287770, 51.93160518831500,
         38.530202970864400, 52.4974766248662, 44.0693476556198]), 0)
    test("14_3111_skin_surface_lms.txt", to_subject_df(
        [4, 96, 15.0, 1, 136.36277193273000, 41.32046580601270,
         34.91756954728280, 41.42523298567590, 35.55637577818560]), 0)
    test("2201_skin_surface_lms.txt", to_subject_df(
        [18, 163, 55.0, 1, 160.569752648607, 71.61904098434910,
         56.37639984398010, 73.71260266374000, 57.69812092475080]), 0)
    test("2228_skin_surface_lms.txt", to_subject_df(
        [17, 160, 73.0, 1, 218.0423302748580, 70.16413878202430, 60.45875598313340,
         70.41634690533600, 57.19884630697000]), 0)

'''
Demo factors as DataFrame:
0: Age, 
1: Height, 
2: Mass, 
3: Sex (1=F, 2=M), 
4: ASIS_width, 
5: epicon_width_left, 
6: malleolar_width_left, 
7: epicon_width_right, 
8: malleolar_width_right

Left model uses: Age, Height, Sex, ASIS_width, PSIS_width, left_epicon_width, left_malleolar_width
Right model uses: Age, Height, Sex, ASIS_width, PSIS_width, right_epicon_width
'''
