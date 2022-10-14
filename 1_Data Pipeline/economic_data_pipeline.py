from fredapi import Fred

class EconomicDataGetter():

    def __init__(self):
        self.fred = fred = Fred(api_key='b2ecc78578eb71eb61fb776be2689182')

    def get_economic_data(self, code, name, period_aggregation = 'monthly'):
        df = self.fred.get_series(code).rename(name).to_frame()
        return df

    def form_economic_data_payload(self, dict_of_fred_codes):

        df_payload = []

        for name, code in dict_of_fred_codes.items():

            df_payload.append(self.get_economic_data(code, name))

        final_df = df_payload[0]

        for i in range(1, len(df_payload)):
            final_df = final_df.merge(df_payload[i], how = 'outer', left_index = True, right_index = True)

        return final_df

