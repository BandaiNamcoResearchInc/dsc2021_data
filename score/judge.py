import math
import os
import sys
import zipfile

import numpy as np
import pandas as pd


if len(sys.argv) != 3:
    print("引数の数が無効です。ZIPファイル名とスコアの種類の2つの引数を指定してください。")
    sys.exit(1)

zipname = sys.argv[1]

if sys.argv[2] == 'public':
    public_flag = True
elif sys.argv[2] == 'private':
    public_flag = False
else:
    print("引数2の指定が無効です。'public'か'private'を指定してください")
    sys.exit(1)


mse = 0.0
mse_count = 0
correct_path = "correct_answer"
levels = ["easy", "normal", "hard"]
file_names = ["test_easy.csv", "test_normal.csv", "test_hard.csv"]
public_names = ["test_public_easy.csv",
                "test_public_normal.csv", "test_public_hard.csv"]
private_names = ["test_private_easy.csv",
                 "test_private_normal.csv", "test_private_hard.csv"]
data_names = {'public': {'easy': ['020', '052', '066', '117', '128'], 'normal': ['005', '036', '079', '122', '130'], 'hard': ['013', '032', '078', '101', '134']}, 'private': {
    'easy': ['011', '040', '073', '104', '148'], 'normal': ['028', '067', '085', '144', '155'], 'hard': ['022', '049', '059', '098', '113']}}


class WrongFileCountError(Exception):
    def __str__(self):
        return "ZIPアーカイブ中のファイル数が違います。3ファイルで提出してください。"


class WrongFileNameError(Exception):
    def __str__(self):
        return "ZIPアーカイブ中のcsvファイル名が違います。"


class WrongMotionCountError(Exception):
    def __init__(self, file_id, motion_count):
        self.file_id = file_id
        self.motion_count = motion_count

    def __str__(self):
        return "csvファイル内のモーションの数が間違っています。\nファイル名：" + str(self.file_id) \
            + "\n提出されたモーション数：" + str(self.motion_count) \
            + "\n提出すべきモーション数：10"


class NoMotionError(Exception):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return "提出すべきモーションがありません。\n提出されていないモーション：" + str(self.id)


class WrongRowCountError(Exception):
    def __init__(self, file_id, motion_id, wrong_row, correct_row):
        self.file_id = file_id
        self.motion_id = motion_id
        self.wrong_row = wrong_row
        self.correct_row = correct_row

    def __str__(self):
        return "CSV内の行数が違います。\nファイル名：" + str(self.file_id) \
            + "\nモーション名：" + str(self.motion_id) \
            + "\n提出された行数:" + str(self.wrong_row) + "行" \
            + "\n提出すべき行数:" + str(self.correct_row) + "行"


class WrongColumnCountError(Exception):
    def __init__(self, file_id, motion_id, wrong_col, correct_col):
        self.file_id = file_id
        self.motion_id = motion_id
        self.wrong_col = wrong_col
        self.correct_col = correct_col

    def __str__(self):
        return "CSV内の列数が違います。\nファイル名：" + str(self.file_id) \
            + "\nモーション名：" + str(self.motion_id) \
            + "\n提出された列数:" + str(self.wrong_col) + "列" \
            + "\n提出すべき列数:" + str(self.correct_col) + "列"


class WrongFrameIdError(Exception):
    def __init__(self, file_id, motion_id, wrong_id, correct_id):
        self.file_id = file_id
        self.motion_id = motion_id
        self.wrong_id = wrong_id
        self.correct_id = correct_id

    def __str__(self):
        return "CSV内のフレーム番号(frame_id)が違います。\nファイル名：" + str(self.file_id) \
            + "\nモーション名：" + str(self.motion_id) \
            + "\n提出されたフレーム番号:" + str(self.wrong_id)  \
            + "\n提出すべきフレーム番号:" + str(self.correct_id)


try:
    with zipfile.ZipFile(zipname, 'r') as zf:
        data_corr = []
        data_pred = []
        if len(zf.namelist()) != 3:
            raise WrongFileCountError

        for i, level in enumerate(levels):
            for fname in zf.namelist():
                if file_names[i] in fname:
                    with zf.open(fname) as f:
                        data_pred.append(pd.read_csv(f))

        if len(data_pred) != 3:
            raise WrongFileNameError

        data_corr = {"public": [], "private": []}
        for data_idx in ["public", "private"]:
            for i, level in enumerate(levels):
                if data_idx == "public":
                    corr_name = os.path.join(correct_path, public_names[i])
                else:
                    corr_name = os.path.join(correct_path, private_names[i])

                with open(corr_name) as f:
                    data_corr[data_idx].append(pd.read_csv(f))

        mse = 0.0
        for i, level in enumerate(levels):
            df_pred = data_pred[i]
            if df_pred.motion.nunique() != 10:
                raise WrongMotionCountError(
                    file_names[i], df_pred.motion.nunique())

            for data_idx in ["public", "private"]:
                df_corr = data_corr[data_idx][i]
                for motion_id in data_names[data_idx][level]:
                    y_pred = df_pred[df_pred.motion == int(motion_id)]
                    y_corr = df_corr[df_corr.motion == int(motion_id)]

                    if len(y_pred.values) == 0:
                        raise NoMotionError(motion_id)

                    if y_pred.values.shape[0] != y_corr.values.shape[0]:
                        raise WrongRowCountError(
                            file_names[i], motion_id, y_pred.values.shape[0], y_corr.values.shape[0])

                    if y_pred.values.shape[1] != y_corr.values.shape[1]:
                        raise WrongColumnCountError(
                            file_names[i], motion_id, y_pred.values.shape[1], y_corr.values.shape[1])

                    if list(y_pred.frame_id) != list(y_corr.frame_id):
                        for j, corr_id in enumerate(list(y_corr.frame_id)):
                            if list(y_pred.frame_id)[j] != corr_id:
                                wrong_id = list(y_pred.frame_id)[j]
                                raise WrongFrameIdError(
                                    file_names[i], motion_id, wrong_id, corr_id)

                    if not(data_idx == "public") ^ public_flag:
                        mse += np.mean((y_corr.values[:, 2:] -
                                       y_pred.values[:, 2:]) ** 2)

    mse /= 15.0

    if mse == 0:
        result = 100
    else:
        mse = 1.0 / mse
        mse = 30 * np.log(mse + 1)
        if public_flag:
            mse = round(mse, 2 - math.ceil(math.log10(abs(mse))))
            if mse == int(mse) and mse >= 10:
                result = int(mse)
        result = min(mse, 100)


except ValueError:
    sys.stderr.write("無効なデータです")
    sys.exit(1)

except zipfile.BadZipFile:
    sys.stderr.write("ZIPアーカイブファイルではありません。")
    sys.exit(1)

except (WrongFileCountError,
        WrongFileNameError,
        WrongMotionCountError,
        NoMotionError,
        WrongRowCountError,
        WrongColumnCountError,
        WrongFrameIdError) as e:

    sys.stderr.write(str(e))
    sys.exit(1)

except:
    sys.stderr.write("\n不明な書式エラー")
    sys.exit(1)


print("Score: " + str(result))
