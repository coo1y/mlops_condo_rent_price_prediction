from prefect import flow
from utils import (
    clean_data,
    drop_null_data,
    filter_data,
    get_data,
    merge_data,
    preprocess_data,
    split_data,
    train_models,
)


@flow(log_prints=True)
def execute_pipeline(train_ratio, val_ratio):
    room_listing, project, property_nearby = get_data()

    room_listing, project, property_nearby = clean_data(
        room_listing=room_listing,
        project=project,
        property_nearby=property_nearby,
    )

    room_listing, project, property_nearby = filter_data(
        room_listing=room_listing,
        project=project,
        property_nearby=property_nearby,
    )

    data = merge_data(
        room_listing=room_listing,
        project=project,
        property_nearby=property_nearby,
    )

    data = drop_null_data(data=data)

    data = preprocess_data(data=data)

    X_train, y_train, X_val, y_val, X_test, y_test = split_data(
        data=data, train_ratio=train_ratio, val_ratio=val_ratio
    )

    # print(X_train.shape, X_val.shape, X_test.shape)
    print(X_train.columns)

    train_models(
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        X_test=X_test,
        y_test=y_test,
    )


if __name__ == "__main__":
    train_ratio = 0.8
    val_ratio = 0.1
    execute_pipeline(train_ratio=train_ratio, val_ratio=val_ratio)
