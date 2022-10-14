from economic_data_pipeline import EconomicDataGetter

class DataPipeline():

    def __init__(self):
        self.EconomicDataGetter = EconomicDataGetter()

    def get_bt4222_economic_data_payload(self):
        dict_of_fred_codes = {'GDP': 'GDP', 'M2V': 'M2V'}
        return self.EconomicDataGetter.form_economic_data_payload(dict_of_fred_codes)
        

