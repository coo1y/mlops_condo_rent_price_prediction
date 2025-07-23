import math
import os

import mlflow
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from hyperopt.pyll import scope
from prefect import task
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_percentage_error

load_dotenv()
mlflow_endpoint = os.getenv("EC2_PUBLIC_DNS", "127.0.0.1")
mlflow.set_tracking_uri(f"http://{mlflow_endpoint}:5000")
mlflow.set_experiment("condo4rent-prediction")
mlflow.sklearn.autolog()


@task
def get_data():

    current_path = os.path.dirname(__file__)
    data_file = os.path.join(current_path, "dataset", "202306.xlsx")

    df_dict = pd.read_excel(data_file, sheet_name=None)

    room_listing = df_dict.get("Room", pd.DataFrame())
    project = df_dict.get("Project", pd.DataFrame())
    property_nearby = df_dict.get("Property Nearby", pd.DataFrame())

    return room_listing, project, property_nearby


@task
def clean_data(room_listing, project, property_nearby):
    ## preprocess `room_listing`
    # Let's strip 'sq.m.'
    room_size_temp = [rs.replace(" sq.m.", "") for rs in room_listing["room_size"]]
    room_listing["room_size"] = pd.to_numeric(room_size_temp)

    # size above 500 sq.m. seem to be a little extreme.
    # So, I'll assume the user typed wrong, and use the tenth digit rounded value
    size_temp = []
    for s in room_listing["room_size"]:
        if math.isnan(s):
            size_temp.append(s)
        elif s <= 500:
            size_temp.append(s)
        elif 1000 < s <= 10000:
            size_temp.append(round(s / 100 - 0.45))
        else:
            size_temp.append(round(s / 1000 - 0.45))

    room_listing["room_size"] = size_temp

    ## preprocess `project`
    # Let's look at `completed_on`
    complete_temp = []
    for c in project["completed_on"]:
        if c == "-":
            complete_temp.append(np.nan)
        else:
            complete_temp.append(c)

    project["completed_on"] = pd.to_numeric(complete_temp)

    return room_listing, project, property_nearby


@task
def filter_data(room_listing, project, property_nearby):
    # focus on rental price between 6000 and 100000 THB/month
    room_listing = room_listing[room_listing["rental"].between(6000, 100000)]

    # focus on condo types: Studio, 1 Bedroom, 2 Bedroom, 3 Bedroom
    room_listing = room_listing[
        room_listing["unit_type"].isin(
            ["Studio", "1 Bedroom", "2 Bedroom", "3 Bedroom"]
        )
    ]

    # print("room_listing:", room_listing.columns)
    # print("project     :", project.columns)

    # pick only these columns for `room_listing`
    chosen_columns = [
        "project_id",
        "rental",
        "room_size",
        "unit_type",
        "air_conditioner",
        "digital_door_lock",
        "furnished",
        "hot_tub",
        "phone",
        "last_update",
    ]
    room_listing = room_listing[chosen_columns]

    # pick only these columns for `project`
    chosen_columns = [
        "project_id",
        "completed_on",
        "fingerprint_access_control",
        "jacuzzi",
        "kids_playground",
        "library",
    ]
    project = project[chosen_columns]

    # focus on condos near mass transit train stations
    property_nearby = property_nearby[
        (property_nearby["property_type"] == "BTS Silom Line")
        | (property_nearby["property_type"] == "BTS Sukhumvit Line")
        | (property_nearby["property_type"] == "MRT Blue line")
    ]
    # then do one hot encoder
    property_nearby = (
        pd.get_dummies(
            property_nearby[["project_id", "property_name"]],
            prefix="near",
            columns=["property_name"],
            dtype=int,
        )
        .groupby("project_id", as_index=False)
        .sum()
    )

    return room_listing, project, property_nearby


@task
def merge_data(room_listing, project, property_nearby):
    data = room_listing.join(project, on="project_id", lsuffix="", rsuffix="_proj")
    data = data.join(property_nearby, on="project_id", lsuffix="", rsuffix="_pp")

    return data


@task
def drop_null_data(data):

    return data.dropna()


@task
def preprocess_data(data):
    # drop column `project_id`
    data = data.drop(columns=["project_id", "project_id_proj", "project_id_pp"])

    # convert `unit_type` to be numeric
    unit_type_map = {
        "Studio": 0,
        "1 Bedroom": 1,
        "2 Bedroom": 2,
        "3 Bedroom": 3,
    }
    data["unit_type"] = data["unit_type"].replace(unit_type_map)

    return data


@task
def split_data(data, train_ratio, val_ratio):
    n_rows = len(data)
    train_cutoff = int(n_rows * train_ratio)
    val_cutoff = int(n_rows * (train_ratio + val_ratio))

    data = data.sort_values(by=["last_update"])
    train_data = data.iloc[:train_cutoff]
    val_data = data.iloc[train_cutoff:val_cutoff]
    test_data = data.iloc[val_cutoff:]

    columns_to_drop = ["rental", "last_update"]
    X_train = train_data.drop(columns=columns_to_drop)
    y_train = train_data["rental"]
    X_val = val_data.drop(columns=columns_to_drop)
    y_val = val_data["rental"]
    X_test = test_data.drop(columns=columns_to_drop)
    y_test = test_data["rental"]

    return X_train, y_train, X_val, y_val, X_test, y_test


@task
def train_models(X_train, y_train, X_val, y_val, X_test, y_test, num_trials=10):
    def objective(params):

        with mlflow.start_run():
            # log the list of hyperparameters that are passed to
            # the objective function during the optimization
            mlflow.log_params(params)

            rf = RandomForestRegressor(**params)
            rf.fit(X_train, y_train)

            # log the metric obtained on the validation set
            y_val_pred = rf.predict(X_val)
            val_mape = mean_absolute_percentage_error(y_val, y_val_pred)
            mlflow.log_metric("val MAPE", val_mape)

            # log the metric obtained on the test set
            y_test_pred = rf.predict(X_test)
            test_mape = mean_absolute_percentage_error(y_test, y_test_pred)
            mlflow.log_metric("test MAPE", test_mape)

        return {"loss": val_mape, "status": STATUS_OK}

    search_space = {
        "max_depth": scope.int(hp.quniform("max_depth", 1, 15, 1)),
        "n_estimators": scope.int(hp.quniform("n_estimators", 10, 100, 1)),
        "min_samples_split": scope.int(hp.quniform("min_samples_split", 2, 15, 1)),
        "min_samples_leaf": scope.int(hp.quniform("min_samples_leaf", 1, 4, 1)),
        "random_state": 42,
    }

    rstate = np.random.default_rng(42)  # for reproducible results
    fmin(
        fn=objective,
        space=search_space,
        algo=tpe.suggest,
        max_evals=num_trials,
        trials=Trials(),
        rstate=rstate,
    )
