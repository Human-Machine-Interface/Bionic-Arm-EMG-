import argparse
import numpy as np
import pandas as pd
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument('--folder_window_size', help='The path where the source data is stored', type=str)
FLAGS = parser.parse_args()

MOTOR_TASKS = ["Task1", "Task2", "Task3", "Task4", "Task5"]
MOTOR_TASKS_DIC = {label.split('.')[0]:num+1 for num, label in enumerate(MOTOR_TASKS)}

TIME_RAW_PATH      = 'paradigmaV1kHz/RAW_DATA/TXT/TimeDomain/Raw/' + FLAGS.folder_window_size
TIME_RMS_PATH      = 'paradigmaV1kHz/RAW_DATA/TXT/TimeDomain/Rms/' + FLAGS.folder_window_size
TIME_RMS_NORM_PATH = 'paradigmaV1kHz/RAW_DATA/TXT/TimeDomain/RmsNorm_Reg/' + FLAGS.folder_window_size
FEATURES_PATH      = 'paradigmaV1kHz/RAW_DATA/Features'

emg_columns = ["MW1", "MW2", "MW3", "Ax", "Ay", "Az", "Gx", "Gy", "Gz"]
used_sensors = ['MW1', 'MW2', 'MW3']


WINDOW_SIZE   = 50      #ms
SAMPLING_RATE = 1000    #Hz
TASK_DURATION = 5       #seconds

WINDOW_20Hz   = 100     #ms
WINDOW_RMS    = 10      #values

def txt_2_csv(src_path='paradigmaV1kHz/RAW_DATA/TXT/TimeDomain/Raw/five_sec'):
    for folder in os.listdir(src_path):
        path_folder = os.path.join(src_path, folder)
        for file_ in os.listdir(path_folder):
            if file_.endswith(".txt"):
                df = pd.read_csv(os.path.join(path_folder, file_), names=emg_columns)
                df.to_csv(os.path.join(path_folder, file_.replace('.txt', '.csv')))

def get_window_full(df, window_size_ms):
    peaks_centroid = int(np.mean([df['MW1'].idxmax(),df['MW2'].idxmax(),df['MW3'].idxmax()]))

    if (peaks_centroid-(window_size_ms/2)) <  0:
        min_index = 0
        max_index = window_size_ms
    else:
        min_index = int(peaks_centroid - (window_size_ms/2))
        max_index = int(peaks_centroid + (window_size_ms/2))
    return df.iloc[min_index:max_index]

def five_2_two_sec(window_size_ms, src_path, dest_folder):
    for folder in os.listdir(src_path):
            path_folder = os.path.join(src_path, folder)
            for file_ in os.listdir(path_folder):
                if file_.endswith(".csv"):
                    df = pd.read_csv(os.path.join(path_folder, file_), index_col=0)
                    get_window_full(df, window_size_ms).to_csv(os.path.join(path_folder, file_).replace('five_sec', dest_folder))

def get_rms(df):
    df_rms = pd.DataFrame(np.nan, index = list(range(0,int((TASK_DURATION*SAMPLING_RATE)/WINDOW_SIZE))), columns=emg_columns)
    index_list = list(range(0,int((TASK_DURATION*SAMPLING_RATE)/WINDOW_SIZE)))
    for index in index_list:
        index_min = index*50
        index_max = index_min + WINDOW_SIZE
        df_window = df.iloc[index_min:index_max]
        for column in emg_columns:
            df_rms.iloc[index][column] = np.sqrt(np.mean(df_window[column]**2))
    return df_rms

def get_rms_all(source_path):
    for folder in os.listdir(source_path):
        path_folder = os.path.join(source_path, folder)
        for file_ in os.listdir(path_folder):
            if file_.endswith(".csv"):
                data_raw = pd.read_csv(os.path.join(path_folder, file_), index_col = 0)
                data_rms = get_rms(data_raw)
                data_rms.to_csv(os.path.join(path_folder, file_).replace("Raw", "Rms"))
    print("DONE RMS")

def reg_normalization(df):
    df_norm = (df - df.min())/(df.max()-df.min())
    return df_norm

def normalize_files(src_path, dest_path):
    """Normalizes all input files

    Parameters
    ----------
    main_path : str
        The path were all the input files are stored
    raw_bool : bool
        A flag used to select the type of data raw or rms
            Raw: set it as 1
            Rms: set it as 0

    Returns
    -------
    None
    """
    columns_to_normalize = ['MW1', 'MW2', 'MW3'] 
    for folder in os.listdir(src_path):
            path_folder = os.path.join(src_path, folder)
            for file_ in os.listdir(path_folder):
                if file_.endswith(".csv"):
                    data = pd.read_csv(os.path.join(path_folder, file_), index_col = 0)
                    subject = int(re.search('S(.*)',file_.split('.')[0]).group(1))
                    for column in columns_to_normalize:
                        data[column] =  reg_normalization(data[column])#, subject, column)
                        data.to_csv(os.path.join(dest_path, folder, file_))
    print("DONE NORMALIZATION")

def get_features_column():
    features_column = ['Label']#, 'Subject']
    for sensor in used_sensors:
        for x in range(WINDOW_RMS,WINDOW_20Hz+WINDOW_RMS, WINDOW_RMS):
            features_column.append('RMS' + str(x) + '_' + sensor)
    return features_column

def define_feature_df(path):
    num_files = 0
    for folder in os.listdir(path):
        path_folder = os.path.join(path, folder)
        csv_files = [f for f in os.listdir(path_folder) if re.search(r'.*\.(csv)$', f)]
        num_files += len(csv_files)
    return pd.DataFrame(np.nan, index = list(range(0,num_files)), columns= get_features_column())

def get_rms_features(main_path, file_name):
    num_row = 0
    df_rms_features = define_feature_df(main_path)
    #df_rms_features['Subject'] = df_rms_features['Subject'].astype('str')
    for folder in os.listdir(main_path):
            path_folder = os.path.join(main_path, folder)
            for file_ in os.listdir(path_folder):
                if file_.endswith(".csv"):
                    data = pd.read_csv(os.path.join(path_folder, file_), index_col = 0)                   
                    for idx in list(range(0,int(data.shape[0]/WINDOW_RMS))):
                        idx = idx*WINDOW_RMS
                        for column in used_sensors:
                            column_tag = 'RMS' + str(idx+WINDOW_RMS) + '_' + column
                            df_rms_features.at[num_row,column_tag] = np.sqrt(np.mean(data[idx:idx+WINDOW_RMS][column]**2))
                    #df_rms_features.at[num_row,'Subject'] = file_
                    df_rms_features.at[num_row, 'Label'] = MOTOR_TASKS_DIC[folder]
                    num_row += 1
    df_rms_features.dropna(how='all', axis=1, inplace=True)
    df_rms_features.dropna(axis=0, inplace=True)
    df_rms_features.to_csv(os.path.join(FEATURES_PATH, file_name))
    print("DONE FEATURES")

#txt_2_csv()
#five_2_two_sec(2000, 'paradigmaV1kHz/RAW_DATA/TXT/TimeDomain/Raw/five_sec', 'two_sec')
#get_rms_all(TIME_RAW_PATH)
normalize_files(TIME_RMS_PATH , TIME_RMS_NORM_PATH)
get_rms_features(TIME_RMS_NORM_PATH, "Features_2sec.csv")




