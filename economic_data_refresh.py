from DataPipeline.economic_data_pipeline import EconomicDataGetter


def refresh_economic_data():

    EconomicDataGetter().get_bt4222_economic_data_payload()

if __name__ == '__main__':
    refresh_economic_data()

refresh_economic_data()

