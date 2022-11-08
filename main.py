import pandas as pd
import datetime
from FeatureEngineering.stable_state_feature_engineer import Model

def main():

    df = pd.read_csv('BT4222 Data Payload.csv').drop(columns = ['Unnamed: 0', 
                                                            'CBOE Emerging Markets ETF Volatility Index', 
                                                            'Total Nonfarm Private Payroll Employment',
                                                           'CBOE EuroCurrency ETF Volatility Index',
                                                           'ICE BofA US Emerging Markets Liquid Corporate Plus Index Total Return Index Value'])
    #these are dropped because they limit the number of samples we have too much
    df.index = pd.to_datetime(df['index']).rename('Date')
    df = df.drop(columns = ['index'])
    
    start = datetime.datetime(1950,1,1)

    for i in df.columns:
        if df[i].to_frame().dropna().first_valid_index() > start:
            start = df[i].to_frame().dropna().first_valid_index()
            print(i, start)

    df = df.fillna(method = 'bfill').resample('M').last().loc[start:]

    us10y = pd.read_csv('US10Y.csv')
    us10y.index = pd.to_datetime(us10y.Date)
    us10y = us10y['adjusted_close'].rename('US10Y').to_frame().resample('M').last()
    us10y

    df = us10y.merge(df, how = 'outer', left_index = True, right_index = True)
    
    m = Model(df.dropna(), 'US10Y')
    models = m.search_for_optimal_model().sort_values('Testing RMSE', ascending = True)

    return models

if __name__ == '__main__':
    main()