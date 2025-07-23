import json
import os
import pickle
from pprint import pprint
from typing import Any, Dict

import mlflow
from dotenv import load_dotenv
from model.request import RequestBody
from model.response import ResponseBody
from predictor import CondoRentPredictor
from pydantic import ValidationError
from utils.log import logger


def get_request_payload(event: Dict[str, Any]) -> RequestBody:
    body = {}
    if "body" in event and event["body"] is not None:
        event_body = event["body"]
        try:
            body = json.loads(event_body)
            logger.info("Received the request")
        except json.JSONDecodeError:
            logger.warning(f"Cannot decode this request: {event_body}")

    return RequestBody(**body)


def return_model_artifact():
    current_path = os.path.dirname(__file__)
    model_file = os.path.join(current_path, "condo4rent.pkl")

    if os.path.exists(model_file):
        ## if the model already exist/loaded, get it from local
        with open(model_file, "rb") as file:
            model = pickle.load(file)
    else:
        ## otherwise, load the registered model from MLFlow server
        load_dotenv()
        mlflow_endpoint = os.environ.get("MLFLOW_TRACKING_DNS", "127.0.0.1")
        mlflow.set_tracking_uri(f"http://{mlflow_endpoint}:5000")

        stage = "prod"
        model_alias = "champion"

        model_uri = f"models:/{stage}@{model_alias}"
        model = mlflow.sklearn.load_model(model_uri)

        ## save the model for next time
        with open(model_file, "wb") as file:
            pickle.dump(model, file)

    return model


def execute_predictor(request: RequestBody, model) -> ResponseBody:
    crp = CondoRentPredictor(request, model, logger)
    crp.preprocess_data()
    crp.predict()
    resp = crp.get_prediction_result()

    return ResponseBody(**resp)


def handler(event: Dict[str, Any], context):
    try:

        request = get_request_payload(event=event)
        model = return_model_artifact()
        response = execute_predictor(request=request, model=model)

        return {"status_code": 200, "body": json.dumps(response.model_dump())}

    except ValidationError as e:
        return {"status_code": 400, "body": json.dumps({"error": e.errors()})}

    except Exception as e:
        return {"status_code": 400, "body": json.dumps({"error": str(e)})}


if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    files = [
        "examples/request.json",
    ]
    files = [os.path.join(current_path, i) for i in files]

    for i in files:
        print("===============")
        with open(i, encoding="utf-8") as f:
            event = json.load(f)

        r = handler(event, None)
        pprint(r)
