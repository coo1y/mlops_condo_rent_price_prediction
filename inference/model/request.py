from typing import Literal

from pydantic import BaseModel, Field


class RequestBody(BaseModel):
    room_size: float = Field(..., gt=20.0)
    unit_type: Literal["Studio", "1 Bedroom", "2 Bedroom", "3 Bedroom"]
    air_conditioner: Literal[0, 1]
    digital_door_lock: Literal[0, 1]
    furnished: Literal[0, 1]
    hot_tub: Literal[0, 1]
    phone: Literal[0, 1]
    completed_on: int = Field(..., ge=1995, le=2023)
    fingerprint_access_control: Literal[0, 1]
    jacuzzi: Literal[0, 1]
    kids_playground: Literal[0, 1]
    library: Literal[0, 1]
    near_BTSBangWa: Literal[0, 1]
    near_BTSChitLom: Literal[0, 1]
    near_BTSChongNonsi: Literal[0, 1]
    near_BTSKrungThonBuri: Literal[0, 1]
    near_BTSNationalStadium: Literal[0, 1]
    near_BTSPhloenChit: Literal[0, 1]
    near_BTSPhoNimit: Literal[0, 1]
    near_BTSRatchadamri: Literal[0, 1]
    near_BTSRatchathewi: Literal[0, 1]
    near_BTSSaintLouis: Literal[0, 1]
    near_BTSSalaDaeng: Literal[0, 1]
    near_BTSSaphanTaksin: Literal[0, 1]
    near_BTSSiam: Literal[0, 1]
    near_BTSSurasak: Literal[0, 1]
    near_BTSTalatPhlu: Literal[0, 1]
    near_BTSVictoryMonument: Literal[0, 1]
    near_BTSWongwianYai: Literal[0, 1]
    near_BTSWutthakat: Literal[0, 1]
    near_MRTBangPhai: Literal[0, 1]
    near_MRTBangWa: Literal[0, 1]
    near_MRTKhlongToei: Literal[0, 1]
    near_MRTLumphini: Literal[0, 1]
    near_MRTPhetKasem48: Literal[0, 1]
    near_MRTSamYan: Literal[0, 1]
    near_MRTSiLom: Literal[0, 1]
    near_MRTThaPhra: Literal[0, 1]
    rent_price: int = Field(..., gt=5000)
