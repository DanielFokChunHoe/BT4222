from fredapi import Fred
from pathlib import Path

class EconomicDataGetter():

    def __init__(self):
        self.fred = fred = Fred(api_key='b2ecc78578eb71eb61fb776be2689182')

    def get_economic_data(self, code, name, period_aggregation = 'monthly'):
        df = self.fred.get_series(code).rename(name).to_frame()
        return df

    def form_economic_data_payload(self, dict_of_fred_codes, save_name = None):

        df_payload = []

        for name, code in dict_of_fred_codes.items():

            df_payload.append(self.get_economic_data(code, name))

        final_df = df_payload[0]

        for i in range(1, len(df_payload)):
            final_df = final_df.merge(df_payload[i], how = 'outer', left_index = True, right_index = True)

        if save_name != None:
            filepath = Path(__file__).parents[1]/'DataCache'/save_name
            final_df.reset_index().to_csv(filepath)
        else:
            return final_df

    def get_bt4222_economic_data_payload(self):
        # USALOLITONOSTSAM is used a proxy for GDPC1
        dict_of_fred_codes = {'US OECD CLI': 'USALOLITONOSTSAM', 
        # Consumer Market
            # Labour, Weekly
            'Total Nonfarm Private Payroll Employment': 'ADPWNUSNERSA', 
            'Initial Claims': 'ICSA', 
            'Continued Claims (Insured Unemployment)':'CCSA',
            'KC Fed Labor Market Conditions Index, Level of Activity Indicator': 'FRBKCLMCILA',
            'University of Michigan: Consumer Sentiment': 'UMCSENT',

        # Financial Market
            # Bond Market Indices, Daily
            'ICE BofA AAA US Corporate Index Total Return Index Value':'BAMLCC0A1AAATRIV', 
            'ICE BofA CCC & Lower US High Yield Index Total Return Index Value':'BAMLHYH0A3CMTRIV',
            'ICE BofA US Emerging Markets Liquid Corporate Plus Index Total Return Index Value':'BAMLEMCLLCRPIUSTRIV',

            #Volatility, Daily
            'CBOE Emerging Markets ETF Volatility Index':'VXEEMCLS',
            'CBOE EuroCurrency ETF Volatility Index':'EVZCLS',
            'CBOE Volatility Index: VIX':'VIXCLS',

            #Banking
            'Assets: Securities Held Outright: U.S. Treasury Securities: All: Wednesday Level': 'TREAST',
            'Assets: Central Bank Liquidity Swaps: Central Bank Liquidity Swaps: Wednesday Level':'SWPT',
            'Total Borrowings of Depository Institutions from the Federal Reserve':'TOTBORR',
            'Borrowings, All Commercial Banks': 'H8B3094NCBA',

        # Business
            'Total Business: Inventories to Sales Ratio': 'ISRATIO',
            'Retail Sales': 'RSXFS',
            'Industrial Production':'INDPRO'

        }
        return self.form_economic_data_payload(dict_of_fred_codes, save_name = 'BT4222 Data Payload.csv')

