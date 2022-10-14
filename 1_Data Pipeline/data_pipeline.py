from economic_data_pipeline import EconomicDataGetter
from text_data_pipeline import TweetDataGetter

class DataPipeline():

    def __init__(self):
        pass

    def get_bt4222_economic_data_payload(self):
        dict_of_fred_codes = {'GDP': 'GDP', 'M2V': 'M2V'}
        return EconomicDataGetter().form_economic_data_payload(dict_of_fred_codes)

    def get_bt4222_text_payload(self):
        return TweetDataGetter.get_text_payload(["@DeltaOne", "@Bloomberg"])
