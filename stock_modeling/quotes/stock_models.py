from statsmodels.graphics.tsaplots import plot_predict
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime as dt

from itertools import product
from .plotting import *
import warnings
warnings.filterwarnings('ignore')

def Historical_VaR(returns):

	returns = returns.to_numpy()
	returns = np.sort(returns)
	ninenine_var_idx = round(0.01 * len(returns)) - 1
	ninefive_var_idx = round(0.05 * len(returns)) - 1
	ninenine_var = returns[ninenine_var_idx]
	ninefive_var = returns[ninefive_var_idx]

	ninenine_es = np.mean(returns[0:ninenine_var_idx])
	ninefive_es = np.mean(returns[0:ninefive_var_idx])

	return (ninenine_var, ninefive_var, ninenine_es, ninefive_es)

def GARCH_model(returns):

	returns = returns * 100
	garch = arch_model(returns, vol='garch', p=1, o=0, q=1)
	garch_fitted = garch.fit()
	model_summary = garch_fitted.summary()

	# write summary to file
	fileobj = open("quotes/static/model_results/ARCH_Summary.txt", 'w')
	fileobj.write(model_summary.as_text())
	fileobj.close()

	# one step out-of-sample forecast
	garch_forecast = garch_fitted.forecast(horizon=1, method='simulation')
	pred_var = garch_forecast.variance.dropna()

	return (garch_fitted,model_summary,pred_var)

def ARMA_model(data, ohlc='Close'):

	data = data[ohlc]

	# choose best p, q parameters for our model using AIC optimization
	params = bestParams(data)
	model = ARIMA(data, order=(params[0], 0, params[2]))
	res = model.fit()

	#model_summary = res.summary().as_text()
	model_summary = res.summary()
	# write summary to file
	#fileobj = open("quotes/static/model_results/ARMA_Summary.txt", 'w')
	#fileobj.write(model_summary.as_text())
	#fileobj.close()

	fig, ax = plt.subplots(figsize=(10,8))
	ax = data.plot(ax=ax)
	fig = plot_predict(res, start=data.index[0], end=data.index[-1], ax=ax, plot_insample=False)
	legend = ax.legend(["Actual price", "Forecast", "95% Confidence Interval"], loc='upper left')

	fig.savefig("quotes/static/plots/forecast_vs_actual.jpg")
	return (model, res, model_summary)

def bestParams(data):

	ps = range(0, 8, 1)
	d = 1
	qs = range(0, 8, 1)

	# Create a list with all possible combination of parameters
	parameters = product(ps, qs)
	parameters_list = list(parameters)
	order_list = []

	for each in parameters_list:
	    each = list(each)
	    each.insert(1, 1)
	    each = tuple(each)
	    order_list.append(each)

	result_df = AIC_optimization(order_list, exog=data)
	return result_df['(p, d, q)'].iloc[0]

def AIC_optimization(order_list, exog):
    """
        Return dataframe with parameters and corresponding AIC
        
        order_list - list with (p, d, q) tuples
        exog - the exogenous variable
    """
    
    results = []
    
    for order in order_list:
        try: 
            model = SARIMAX(exog, order=order).fit(disp=-1)
        except:
            continue
            
        aic = model.aic
        results.append([order, model.aic])
        
    result_df = pd.DataFrame(results)
    result_df.columns = ['(p, d, q)', 'AIC']

    #Sort in ascending order, lower AIC is better
    result_df = result_df.sort_values(by='AIC', ascending=True).reset_index(drop=True)
    return result_df