import pandas as pd


class CondoRentPredictor:
    def __init__(self, request, model, logger):
        self.request = request.model_dump()
        self.model = model
        self.logger = logger

        self.logger.info("Executing Predictor ...")

    def preprocess_data(self):
        self.logger.info("Preprocessing data ...")

        unit_type_map = {
            "Studio": 0,
            "1 Bedroom": 1,
            "2 Bedroom": 2,
            "3 Bedroom": 3,
        }
        landmark_names_map = {
            "near_BTSBangWa": "near_BTS Bang Wa",
            "near_BTSChitLom": "near_BTS Chit Lom",
            "near_BTSChongNonsi": "near_BTS Chong Nonsi",
            "near_BTSKrungThonBuri": "near_BTS Krung Thon Buri",
            "near_BTSNationalStadium": "near_BTS National Stadium",
            "near_BTSPhloenChit": "near_BTS Phloen Chit",
            "near_BTSPhoNimit": "near_BTS Pho Nimit",
            "near_BTSRatchadamri": "near_BTS Ratchadamri",
            "near_BTSRatchathewi": "near_BTS Ratchathewi",
            "near_BTSSaintLouis": "near_BTS Saint Louis",
            "near_BTSSalaDaeng": "near_BTS Sala Daeng",
            "near_BTSSaphanTaksin": "near_BTS Saphan Taksin",
            "near_BTSSiam": "near_BTS Siam",
            "near_BTSSurasak": "near_BTS Surasak",
            "near_BTSTalatPhlu": "near_BTS Talat Phlu",
            "near_BTSVictoryMonument": "near_BTS Victory Monument",
            "near_BTSWongwianYai": "near_BTS Wongwian Yai",
            "near_BTSWutthakat": "near_BTS Wutthakat",
            "near_MRTBangPhai": "near_MRT Bang Phai",
            "near_MRTBangWa": "near_MRT Bang Wa",
            "near_MRTKhlongToei": "near_MRT Khlong Toei",
            "near_MRTLumphini": "near_MRT Lumphini",
            "near_MRTPhetKasem48": "near_MRT Phet Kasem 48",
            "near_MRTSamYan": "near_MRT Sam Yan",
            "near_MRTSiLom": "near_MRT Si Lom",
            "near_MRTThaPhra": "near_MRT Tha Phra",
        }

        data = pd.DataFrame([self.request])
        data.drop(columns=["rent_price"], inplace=True)

        # map column names corresponding to the columns used in model training
        data.rename(columns=landmark_names_map, inplace=True)

        unit_type_num = unit_type_map.get(self.request["unit_type"], -1)
        # in case of the unit type isn't matched
        if unit_type_num == -1:
            self.logger.warning(
                f"Unit type: {self.request['unit_type']} isn't available."
            )

        # convert `unit_type` to be numeric
        data["unit_type"] = data["unit_type"].map(unit_type_map)

        self.data = data

    def predict(self):
        self.logger.info("Predicting rental price ...")

        prediction = self.model.predict(self.data)[0]

        self.prediction = int(prediction)

    def get_prediction_result(self):
        rent_price = self.request.get("rent_price", 1)
        prediction = self.prediction
        pct_diff = round((rent_price - prediction) / rent_price * 100.0, 2)

        self.logger.info("====== [Done] ======")

        return {
            "rent_price": rent_price,
            "predicted_rent_price": prediction,
            "pct_diff": pct_diff,
        }
