"""
This will load models and test them on the test set, it will print nice things.
"""

# -------------------------------------------------------------------------------------

from keras.models import model_from_json
from sklearn.metrics import (
    f1_score,
    accuracy_score,
    mean_squared_error,
    precision_recall_fscore_support,
)
from sklearn.preprocessing import MultiLabelBinarizer
from branch2treelabels import branch2treelabelsStance
import numpy as np
import os
import pickle as pkl
import json

# -------------------------------------------------------------------------------------
def labell2strA(label):

    if label == 0:
        return "support"
    elif label == 1:
        return "comment"
    elif label == 2:
        return "deny"
    elif label == 3:
        return "query"
    else:
        print(label)


def labell2strB(label):

    if label == 0:
        return "true"
    elif label == 1:
        return "false"
    elif label == 2:
        return "unverified"
    else:
        print(label)


def convertsave_competitionformat(
    idsA, predictionsA, idsB, predictionsB, confidenceB, temp_save=False
):

    subtaskaenglish = {}
    subtaskbenglish = {}

    for i, id in enumerate(idsA):
        # print(id[-1])
        subtaskaenglish[id[-1]] = labell2strA(predictionsA[i])

    for i, id in enumerate(idsB):
        subtaskbenglish[id] = [labell2strB(predictionsB[i]), 0]

    answer = {}
    answer["subtaskaenglish"] = subtaskaenglish
    answer["subtaskbenglish"] = subtaskbenglish

    answer["subtaskadanish"] = {}
    answer["subtaskbdanish"] = {}

    answer["subtaskarussian"] = {}
    answer["subtaskbrussian"] = {}

    if temp_save:
        with open("tempAnswers.json", "w") as f:
            json.dump(answer, f)
    else:
        with open("output/answer.json", "w") as f:
            json.dump(answer, f)

    return answer


def prediction_to_label(pred):
    if len(pred.shape) == 2:
        return np.argmax(pred, axis=1)
    if len(pred.shape) == 3:
        return np.argmax(pred, axis=2)
    print("ERROR! ERROR!1!!!!")
    exit(0)


# -------------------------------------------------------------------------------------

with open("data/test/final-eval-key.json", "r") as f:
    TEST_DATA_LABELS = json.load(f)

with open("data/train/dev-key.json", "r") as f:
    VAL_DATA_LABELS = json.load(f)

with open("data/train/train-key.json", "r") as f:
    TRAIN_DATA_LABELS = json.load(f)

# load stance model
json_file = open("output/model_architecture_stance.json", "r")
loaded_stance_model_json = json_file.read()
json_file.close()
stance_model = model_from_json(loaded_stance_model_json)
# load weights into new model
stance_model.load_weights("output/my_model_stance_weights.h5")
print("Loaded stance model")

# load veracity model
json_file = open("output/model_architecture_veracity.json", "r")
loaded_veracity_model_json = json_file.read()
json_file.close()
veracity_model = model_from_json(loaded_veracity_model_json)
# load weights into new model
veracity_model.load_weights("output/my_model_veracity_weights.h5")
print("Loaded veracity model")

path = "preprocessing/saved_dataRumEval2019"
x_train = np.load(os.path.join(path, "train/train_array.npy"), allow_pickle=True)
y_train_stance = np.load(
    os.path.join(path, "train/fold_stance_labels.npy"), allow_pickle=True
)
y_train_veracity = np.load(os.path.join(path, "train/labels.npy"), allow_pickle=True)
x_val = np.load(os.path.join(path, "dev/train_array.npy"), allow_pickle=True)
y_val_stance = np.load(
    os.path.join(path, "dev/fold_stance_labels.npy"), allow_pickle=True
)
y_val_veracity = np.load(os.path.join(path, "dev/labels.npy"), allow_pickle=True)
x_test = np.load(os.path.join(path, "test/train_array.npy"), allow_pickle=True)
y_test_stance = np.load(
    os.path.join(path, "test/fold_stance_labels.npy"), allow_pickle=True
)
y_test_veracity = np.load(os.path.join(path, "test/labels.npy"), allow_pickle=True)


# For STANCE
twt_ids_train = np.load(os.path.join(path, "train/tweet_ids.npy"), allow_pickle=True)
twt_ids_dev = np.load(os.path.join(path, "dev/tweet_ids.npy"), allow_pickle=True)
twt_ids_test = np.load(os.path.join(path, "test/tweet_ids.npy"), allow_pickle=True)

# For VERACITY
ids_train = np.load(os.path.join(path, "train/ids.npy"), allow_pickle=True)
ids_dev = np.load(os.path.join(path, "dev/ids.npy"), allow_pickle=True)
ids_test = np.load(os.path.join(path, "test/ids.npy"), allow_pickle=True)

### TESTING STANCE MODEL (PART A)
train_preds = stance_model.predict_classes(x_train)
val_preds = stance_model.predict_classes(x_val)
test_preds = stance_model.predict_classes(x_test)

for name, ids, json_file, true, pred in zip(
    ["Training set", "val set", "Test set"],
    [twt_ids_train, twt_ids_dev, twt_ids_test],
    [TRAIN_DATA_LABELS, VAL_DATA_LABELS, TEST_DATA_LABELS],
    [y_train_stance, y_val_stance, y_test_stance],
    [train_preds, val_preds, test_preds],
):
    trees, tree_pred, tree_label = branch2treelabelsStance(ids, true, pred, json_file)

    mse = mean_squared_error(tree_label, tree_pred, squared=False)

    f1 = f1_score(tree_label, tree_pred, labels=np.unique(pred), average="macro")

    if name == "Test set":
        predictionsA = tree_pred

    # m = MultiLabelBinarizer().fit(true)
    #
    # if name == "Test set":
    #     print(m.transform(true))
    #
    # if name == "Test set":
    #     print(m.transform(pred))
    #
    # f1 = f1_score(
    #     m.transform(true), m.transform(pred), labels=np.unique(pred), average="macro"
    # )

    # acc = accuracy_score(true, pred)
    print(
        "#-----------------------------------------------------------------------------"
    )
    print(f"A - STANCE: CALCULATING FOR {name.upper()}")
    if name == "Test set":
        print(f"A - STANCE: F1 score is {f1}: EXPECTED BASELINE ON TEST: 0.4929")
    else:
        print(f"A - STANCE: F1 score is {f1}")
    # print("A - STANCE: RMSE is " + str(mse))
    # print("A - STANCE: Accuracy is " + str(acc))

print(
    "#-----------------------------------------------------------------------------\n"
)

### TESTING VERACITY MODEL (PART B)

train_preds = veracity_model.predict_classes(x_train)
val_preds = veracity_model.predict_classes(x_val)
test_preds = veracity_model.predict_classes(x_test)

for name, true, pred in zip(
    ["Training set", "val set", "Test set"],
    [y_train_veracity, y_val_veracity, y_test_veracity],
    [train_preds, val_preds, test_preds],
):

    mse = mean_squared_error(true, pred, squared=False)
    f1 = f1_score(true, pred, labels=np.unique(pred), average="macro")
    acc = accuracy_score(true, pred)

    if name == "Test set":
        predictionsB = pred
    print(
        "#-----------------------------------------------------------------------------"
    )
    print(f"B - VERACITY: CALCULATING FOR {name.upper()}")
    if name == "Test set":
        print(f"B - VERACITY: F1 score is {f1}: EXPECTED BASELINE ON TEST: 0.3364")
        print(f"B - VERACITY: RMSE score is {mse}: EXPECTED BASELINE ON TEST: 0.7806")
    else:
        print(f"B - VERACITY: F1 score is {f1}")
        print(f"B - VERACITY: RMSE score is {mse}")
    # print("B - VERACITY: Accuracy is " + str(acc))


# score = stance_model.evaluate(x_test, y_test, verbose=0)
# print("%s: %.2f%%" % (stance_model.metrics_names[1], score[1]*100))

# score = stance_model.evaluate(x_test, y_test, verbose=0)
# print("%s: %.2f%%" % (stance_model.metrics_names[1], score[1]*100))
confidenceB = []
answer = convertsave_competitionformat(
    twt_ids_test, predictionsA, ids_test, predictionsB, confidenceB, temp_save=True
)

with open("tempAnswers.json", "r") as f:
    predicted = json.load(f)

shouldhaveA = len(list(TEST_DATA_LABELS["subtaskaenglish"].keys()))
actuallyhaveA = len(list(predicted["subtaskaenglish"].keys()))
Adiff = shouldhaveA - actuallyhaveA
shouldhaveB = len(list(TEST_DATA_LABELS["subtaskbenglish"].keys()))
actuallyhaveB = len(list(predicted["subtaskbenglish"].keys()))
Bdiff = shouldhaveB - actuallyhaveB

if "443938194715713536" not in predicted["subtaskaenglish"].keys():
    print(f"\n443938194715713536 still missing from A")

if Adiff != 0:
    if Adiff > 0:
        print(
            f"\nYou're missing {Adiff} ids in Task A (Stance)... write smarter printing to know which ones."
        )
    if Adiff < 0:
        print(f"\nYou have {Adiff} extra values in Task A (Stance)...")

if Bdiff != 0:
    if Bdiff > 0:
        print(
            f"\nYou're missing {Adiff} ids in Task B (Veracity)... write smarter printing to know which ones."
        )
    if Bdiff < 0:
        print(f"\nYou have {Adiff} extra values in Task B (Veracity)...")

print()

exit(0)
