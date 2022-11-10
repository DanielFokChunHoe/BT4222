import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn import linear_model
import datetime
from sklearn.metrics import mean_squared_error
from statsmodels.regression.linear_model import OLS

#apply all timeshifts to all features

#run random forest classifier on time shifted feature dataframe to select the best features

#run selected features + sentiment premium to then predict US10Y

class Model():
    
    def __init__(self, dataframe, target_variable_name, unique_timeshifts_accepted = 3, min_lead = 6, max_lead = 24):
        self.dataframe = dataframe
        
        self.features = list(dataframe.columns)
        self.features.remove(target_variable_name)
        self.feature_dataframe = self.dataframe[self.features]
        
        self.target_variable_name = target_variable_name
        self.target_variable_dataframe = self.dataframe[[self.target_variable_name]]
        
        self.random_state = 42
        self.unique_timeshifts_accepted = unique_timeshifts_accepted
        self.min_lead = min_lead
        self.max_lead = max_lead
        
        self.time_shifted_feature_dataframe = self.generate_time_shifted_feature_dataframe()
    
    #generate feature dataframe with all possible time shifts applied
    def generate_time_shifted_feature_dataframe(self):
        
        feature_payload = []
        
        for feature in self.features:
            
            temp_feature = self.feature_dataframe[[feature]]
            
            for i in range(self.min_lead, self.max_lead + 1):
                temp_shifted_feature = temp_feature.copy()
                temp_shifted_feature.index = temp_shifted_feature.index.shift(i, freq = 'MS')
                temp_shifted_feature.columns = [feature + ' (Leading by ' + str(i) + ' Months)']
                feature_payload.append(temp_shifted_feature)
            
        final = feature_payload[0]
        for i in range(1, len(feature_payload)):
            final = final.merge(feature_payload[i], how = 'outer', left_index = True, right_index = True)
            
        start = datetime.datetime(1950,1,1)

        for i in final.columns:
            if final[i].to_frame().dropna().first_valid_index() > start:
                start = final[i].to_frame().dropna().first_valid_index()
        
        final = final.loc[start:].fillna(method = 'bfill').resample('M').last()

        return final
    
    def get_top_performing_individual_features(self, X_train, n = None):
        
        if n == None:
            n = self.unique_timeshifts_accepted
        
        feature_payload = []
        #cycle through each individual feature, run a standard OLS on each run and pick
        #use the statsmodel ols to filter the 3 time shifts that produce the lowest p-values
        #save these features onto a payload
        for feature in self.features:
            temp_X_train = X_train.copy().filter(like = feature)
            
            temp = self.target_variable_dataframe.merge(temp_X_train, how = 'inner', left_index = True, right_index = True).dropna()

            temp_SM_OLS_Model = OLS(endog = temp[self.target_variable_name], exog = temp.drop(columns = [self.target_variable_name]))
            fitted_model = temp_SM_OLS_Model.fit()
            result_summary = fitted_model.summary2()
            best_features = list(result_summary.tables[1].sort_values('P>|t|').index[:n])
            feature_payload.extend(best_features)
            
        return feature_payload
    
    def run_modified_stepwise_regression(self, X_train, X_test, y_train, y_test):
        
#         feature_payload = self.get_top_performing_individual_features(3)
        
        mswr_payload = []
        
        #with the 3 time shifts from each features saved, re-run sm.OLS on these selected features
        new_X_train = X_train.copy()#[feature_payload]
        new_X_test = X_test.copy()#[feature_payload]
        
        while len(new_X_train) > 0:
            temp_SM_OLS_Model = OLS(endog = y_train.copy(), exog = new_X_train.copy())
            fitted_model = temp_SM_OLS_Model.fit()

            train_predict = fitted_model.predict(new_X_train.copy())
            test_predict = fitted_model.predict(new_X_test)

            train_rmse = mean_squared_error(y_train.copy(), train_predict, squared=False)
            test_rmse = mean_squared_error(y_test.copy(), test_predict, squared=False)
            
            mswr_payload.append({'Model': fitted_model, 'Features': list(new_X_train.copy().columns),
                                'Training RMSE': train_rmse, 'Testing RMSE': test_rmse})
        
            #continually filter out the highest p-values until you are left with no features
            result_summary = fitted_model.summary2()
            new_features_after_elimination = best_features = list(result_summary.tables[1].sort_values('P>|t|').index[:-1])
            if len(new_features_after_elimination) == 0:
                break
            new_X_train = X_train.copy()[new_features_after_elimination]
            new_X_test = X_test.copy()[new_features_after_elimination]    
        
        #pick the combination with the best RMSE
        final_results = pd.DataFrame(mswr_payload).sort_values('Training RMSE', ascending = True).iloc[:10].sort_values('Testing RMSE').iloc[0]
        fitted_sm_ols_model = final_results['Model'] 
        feature_payload = final_results['Features']
        train_rmse = final_results['Training RMSE']
        test_rmse = final_results['Testing RMSE']
        
        return fitted_sm_ols_model, feature_payload, train_rmse, test_rmse
    
    def search_for_optimal_model(self):
        
        payload = []
        
        #prepare data
        time_shifted_feature_dataframe = self.time_shifted_feature_dataframe.copy()
        
        X = time_shifted_feature_dataframe
        y = self.target_variable_dataframe.copy()
        model_data = y.merge(X, how = 'inner', left_index = True, right_index = True).dropna()
        X_train, X_test, y_train, y_test = train_test_split(model_data, model_data[self.target_variable_name], test_size=0.3, random_state=self.random_state)
        if self.target_variable_name in X_train.columns:
            X_train = X_train.drop(columns = [self.target_variable_name])
            X_test = X_test.drop(columns = [self.target_variable_name])
            
        #get top 3 performing individual features to minimize collinearity 
        feature_payload = self.get_top_performing_individual_features(X_train)
        X_train = X_train[feature_payload]
        X_test = X_test[feature_payload]
        
        
        #base model: LR of all variables against target
        base_model = linear_model.LinearRegression().fit(X = X_train.copy(), y = y_train.copy())
        
        base_model_train_predict = base_model.predict(X_train.copy())
        base_model_test_predict = base_model.predict(X_test.copy())
        
        base_model_train_rmse = mean_squared_error(y_train.copy(), base_model_train_predict, squared=False)
        base_model_test_rmse = mean_squared_error(y_test.copy(), base_model_test_predict, squared=False)
        
        payload.append({'Model Name':'Base Model - Linear Regression', 'Model': base_model, 
                        'Features': list(X.columns), '# of Features': len(X.columns),
                       'Training RMSE': base_model_train_rmse, 'Testing RMSE': base_model_test_rmse})
                
#         modified stepwise regression via backward elimination
        model, mswr_features, mswr_training_rmse, mswr_testing_rmse = self.run_modified_stepwise_regression(X_train, X_test, y_train, y_test)
        payload.append({'Model Name':'Modified Stepwise Regression', 'Model': model, 
                        'Features': mswr_features, '# of Features': len(mswr_features),
                       'Training RMSE': mswr_training_rmse, 'Testing RMSE': mswr_testing_rmse})
        
        #Elastic net, lasso, and ridge regression
        regularization_alphas = [0.1,0.2,0.5,0.75,1.0]
        
        for alpha in regularization_alphas:
            #Elastic Net
            elastic_net_model = linear_model.ElasticNet(alpha=alpha)
            elastic_net_model.fit(X = X_train.copy(), y = y_train.copy())

            elastic_net_features_df = pd.DataFrame({'Features': list(X_train.copy().columns), 'Weights': elastic_net_model.coef_})
            elastic_net_features = list(elastic_net_features_df['Features'])#[elastic_net_features_df['Weights'] != 0]['Features'])

            elastic_net_model_train_predict = elastic_net_model.predict(X_train.copy())
            elastic_net_model_test_predict = elastic_net_model.predict(X_test.copy())

            elastic_net_model_train_rmse = mean_squared_error(y_train.copy(), elastic_net_model_train_predict, squared=False)
            elastic_net_model_test_rmse = mean_squared_error(y_test.copy(), elastic_net_model_test_predict, squared=False)

            payload.append({'Model Name':'Elastic Net Model (alpha =' + str(alpha) + ')', 'Model': elastic_net_model, 
                            'Features': elastic_net_features, '# of Features': len(elastic_net_features),
                           'Training RMSE': elastic_net_model_train_rmse, 'Testing RMSE': elastic_net_model_test_rmse})

            #Lasso
            lasso_model = linear_model.Lasso(alpha=alpha)
            lasso_model.fit(X = X_train.copy(), y = y_train.copy())

            lasso_features_df = pd.DataFrame({'Features': list(X_train.copy().columns), 'Weights': lasso_model.coef_})
            lasso_features = list(lasso_features_df['Features'])#[lasso_features_df['Weights'] != 0]['Features'])

            lasso_model_train_predict = lasso_model.predict(X_train.copy())
            lasso_model_test_predict = lasso_model.predict(X_test.copy())

            lasso_model_train_rmse = mean_squared_error(y_train.copy(), lasso_model_train_predict, squared=False)
            lasso_model_test_rmse = mean_squared_error(y_test.copy(), lasso_model_test_predict, squared=False)

            payload.append({'Model Name':'Lasso Model (alpha =' + str(alpha) + ')', 'Model': lasso_model, 
                            'Features': lasso_features, '# of Features': len(lasso_features),
                           'Training RMSE': lasso_model_train_rmse, 'Testing RMSE': lasso_model_test_rmse})

            #Ridge
            ridge_model = linear_model.Ridge(alpha=alpha)
            ridge_model.fit(X = X_train.copy(), y = y_train.copy())

            ridge_features_df = pd.DataFrame({'Features': list(X_train.copy().columns), 'Weights': ridge_model.coef_})
            ridge_features = list(ridge_features_df['Features'])#[ridge_features_df['Weights'] != 0]['Features'])

            ridge_model_train_predict = ridge_model.predict(X_train.copy())
            ridge_model_test_predict = ridge_model.predict(X_test.copy())

            ridge_model_train_rmse = mean_squared_error(y_train.copy(), ridge_model_train_predict, squared=False)
            ridge_model_test_rmse = mean_squared_error(y_test.copy(), ridge_model_test_predict, squared=False)

            payload.append({'Model Name':'Ridge Model (alpha =' + str(alpha) + ')', 'Model': ridge_model, 
                            'Features': ridge_features, '# of Features': len(ridge_features),
                           'Training RMSE': ridge_model_train_rmse, 'Testing RMSE': ridge_model_test_rmse})

        #random forest regression
        for max_depth in [3,4,5]:
            for ccp_alpha in [0, 0.1, 0.2, 0.5, 1.0]:
                random_forest_regressor_model = RandomForestRegressor(max_depth=max_depth, random_state= self.random_state, ccp_alpha = ccp_alpha)
                random_forest_regressor_model.fit(X_train, y_train)

                random_forest_regressor_model_train_predict = random_forest_regressor_model.predict(X_train.copy())
                random_forest_regressor_model_test_predict = random_forest_regressor_model.predict(X_test.copy())

                random_forest_regressor_model_train_rmse = mean_squared_error(y_train.copy(), random_forest_regressor_model_train_predict, squared=False)
                random_forest_regressor_model_test_rmse = mean_squared_error(y_test.copy(), random_forest_regressor_model_test_predict, squared=False)

                payload.append({'Model Name':'Random Forest Regressor Model (ccp_alpha = ' + str(ccp_alpha) + ')', 'Model': random_forest_regressor_model, 
                                'Features': list(X_train.copy().columns), '# of Features': len(list(X_train.copy().columns)),
                               'Training RMSE': random_forest_regressor_model_train_rmse, 'Testing RMSE': random_forest_regressor_model_test_rmse})

        return pd.DataFrame(payload)