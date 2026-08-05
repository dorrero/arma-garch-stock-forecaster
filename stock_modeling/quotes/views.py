import os

from django.shortcuts import render
from .data_retriever import *
from .stock_models import *
from .plotting import *

IEX_API_TOKEN = os.environ.get('IEX_API_TOKEN', '')

# Create your views here.
def model(request):
	import requests
	import json

	# NJFJY7DW1WXTJ4U4 -- alphavantage
	if request.method == 'POST':

		ticker = request.POST['ticker']
		start_date = request.POST['start_date']
		end_date = request.POST['end_date']

		# get stock quote
		api_request = requests.get(
			"https://cloud.iexapis.com/stable/stock/" + ticker + "/quote",
			params={'token': IEX_API_TOKEN},
		)

		# Retrieve historical stock data
		(data, returns_data) = retrieve(ticker, start_date, end_date)

		if data.empty:
			return render(request, 'model.html', {
				'ticker': "No data found for '{}' in that date range. Check the ticker symbol and try again.".format(ticker)
			})

		# make plot of historical stock price data and returns
		historical_price_plot = saveBasicPlot(data, "quotes/static/plots", "historical_plot.jpg")
		historical_returns_plot = saveReturnsPlot(returns_data, "quotes/static/plots", "returns_plot.jpg")

		# models
		(arma, arma_res, model_summary) = ARMA_model(data)
		(garch,garch_summary,pred_var) = GARCH_model(returns_data)
		VaR = Historical_VaR(returns_data)
		print("VaR at 99% confidence interval is:", VaR[0])
		print("VaR at 95% confidence interval is:", VaR[1])
		print("Expected shortfall at 99% confidence interval is:", VaR[2])
		print("Expected shortfall at 95% confidence interval is:", VaR[3])

		try:
			api = json.loads(api_request.content)
		except Exception as e:
			api = "Error..."
		return render(request, 'model.html', {'api': api,'file_content':model_summary,'file_content1':garch_summary,'Var':VaR,'predvar':pred_var})

	else:
		return render(request, 'model.html', {'ticker': "Enter a ticker symbol above."})

def home(request):
	return render(request, 'home.html', {})

def about(request):
	return render(request, 'about.html', {})

