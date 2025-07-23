import json
import os
import sys

import pytest

# Ensure the app module can be imported from the tests directory
current_path = os.path.dirname(__file__)
sys.path.append(os.path.join(current_path, "../.."))

from app import handler


@pytest.fixture
def event():
    event_file = os.path.join(current_path, "testcases/request.json")

    with open(event_file, encoding="utf-8") as f:
        event = json.load(f)

    return event


@pytest.fixture
def example_response_body():
    response_file = os.path.join(current_path, "testcases/response.json")

    with open(response_file, encoding="utf-8") as f:
        example_response = json.load(f)

    example_response_body = json.loads(example_response.get("body", r"{}"))

    return example_response_body


def test_successful_inference(event, example_response_body):
    r = handler(event, None)

    ### check if pass
    assert r["status_code"] == 200

    ### check if the keys are the same
    r_body = json.loads(r["body"])
    assert set(r_body.keys()) == set(example_response_body.keys())


def test_incomplete_request(event):
    # edit the request to contain only a few values
    event["body"] = '{"room_size": 30.0, "unit_type": "1 Bedroom", "rent_price": 13000}'

    r = handler(event, None)

    ### check if fail
    assert r["status_code"] == 400
    assert '"type": "missing"' in r["body"]  # some keys are missing


def test_invalid_values(event):
    # edit the request to invalid some values
    event[
        "body"
    ] = '{"room_size": 0.0, "unit_type": "0", "air_conditioner": 2, "digital_door_lock": 1, "furnished": 1, "hot_tub": 0, "phone": 0, "completed_on": 2005, "fingerprint_access_control": 0, "jacuzzi": 0, "kids_playground": 1, "library": 1, "near_BTSBangWa": 0, "near_BTSChitLom": 0, "near_BTSChongNonsi": 1, "near_BTSKrungThonBuri": 0, "near_BTSNationalStadium": 0, "near_BTSPhloenChit": 0, "near_BTSPhoNimit": 0, "near_BTSRatchadamri": 0, "near_BTSRatchathewi": 0, "near_BTSSaintLouis": 0, "near_BTSSalaDaeng": 1, "near_BTSSaphanTaksin": 0, "near_BTSSiam": 0, "near_BTSSurasak": 0, "near_BTSTalatPhlu": 0, "near_BTSVictoryMonument": 0, "near_BTSWongwianYai": 0, "near_BTSWutthakat": 0, "near_MRTBangPhai": 0, "near_MRTBangWa": 0, "near_MRTKhlongToei": 0, "near_MRTLumphini": 0, "near_MRTPhetKasem48": 0, "near_MRTSamYan": 0, "near_MRTSiLom": 1, "near_MRTThaPhra": 0, "rent_price": 13000}'

    r = handler(event, None)

    ### check if fail
    assert r["status_code"] == 400
    assert '"ctx":' in r["body"]  # some values don't correspond to BodyRequest
