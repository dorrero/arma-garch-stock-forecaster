import json
import os
import re
import threading

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static

from .data_retriever import *
from .stock_models import *
from .plotting import *

IEX_API_TOKEN = os.environ.get('IEX_API_TOKEN', '')

# Historical data for a fixed (ticker, start_date, end_date) never changes,
# so a completed fit can be cached indefinitely; LocMemCache's own entry cap
# (default 300, LRU-evicted) keeps this from growing without bound.
CACHE_TIMEOUT = None
JOB_LOCK_TIMEOUT = 60 * 10


def _slug(ticker, start_date, end_date):
	raw = "{}_{}_{}".format(ticker.upper(), start_date, end_date)
	return re.sub(r'[^A-Za-z0-9_-]', '_', raw)


def _run_pipeline(ticker, start_date, end_date, cache_key):
	try:
		(data, returns_data) = retrieve(ticker, start_date, end_date)

		if data.empty:
			cache.set(cache_key, {
				'error': "No data found for '{}' in that date range. Check the ticker symbol and try again.".format(ticker)
			}, CACHE_TIMEOUT)
			return

		slug = _slug(ticker, start_date, end_date)
		hist_name = "historical_plot_{}.jpg".format(slug)
		returns_name = "returns_plot_{}.jpg".format(slug)
		forecast_name = "forecast_vs_actual_{}.jpg".format(slug)

		saveBasicPlot(data, "quotes/static/plots", hist_name)
		saveReturnsPlot(returns_data, "quotes/static/plots", returns_name)

		(arma, arma_res, model_summary) = ARMA_model(data, plot_name=forecast_name)
		(garch, garch_summary, pred_var) = GARCH_model(returns_data)
		VaR = Historical_VaR(returns_data)

		cache.set(cache_key, {
			'VaR': VaR,
			'model_summary': str(model_summary),
			'garch_summary': str(garch_summary),
			'pred_var': pred_var.to_dict(),
			'historical_plot_url': static('plots/' + hist_name),
			'returns_plot_url': static('plots/' + returns_name),
			'forecast_plot_url': static('plots/' + forecast_name),
		}, CACHE_TIMEOUT)
	except Exception as e:
		cache.set(cache_key, {'error': "Error modeling '{}': {}".format(ticker, e)}, CACHE_TIMEOUT)


# Create your views here.
def model(request):
	import requests

	if request.method == 'POST':

		ticker = request.POST['ticker']
		start_date = request.POST['start_date']
		end_date = request.POST['end_date']

		# get stock quote (best-effort: skip if no token, and never let a
		# flaky/unreachable quote API take down the whole page)
		api = "Quote unavailable (no IEX_API_TOKEN configured)."
		if IEX_API_TOKEN:
			try:
				api_request = requests.get(
					"https://cloud.iexapis.com/stable/stock/" + ticker + "/quote",
					params={'token': IEX_API_TOKEN},
					timeout=5,
				)
				api = json.loads(api_request.content)
			except Exception:
				api = "Error fetching quote."

		slug = _slug(ticker, start_date, end_date)
		cache_key = "model_result_{}".format(slug)
		cached = cache.get(cache_key)

		if cached is None:
			lock_key = "model_job_running_{}".format(slug)
			if cache.get(lock_key) is None:
				cache.set(lock_key, True, JOB_LOCK_TIMEOUT)
				threading.Thread(
					target=_run_pipeline,
					args=(ticker, start_date, end_date, cache_key),
					daemon=True,
				).start()
			return render(request, 'processing.html', {
				'ticker': ticker,
				'start_date': start_date,
				'end_date': end_date,
				'slug': slug,
			})

		if 'error' in cached:
			return render(request, 'model.html', {'ticker': cached['error']})

		return render(request, 'model.html', {
			'api': api,
			'file_content': cached['model_summary'],
			'file_content1': cached['garch_summary'],
			'Var': cached['VaR'],
			'predvar': cached['pred_var'],
			'historical_plot_url': cached['historical_plot_url'],
			'returns_plot_url': cached['returns_plot_url'],
			'forecast_plot_url': cached['forecast_plot_url'],
		})

	else:
		return render(request, 'model.html', {'ticker': "Enter a ticker symbol above."})


def model_status(request, slug):
	cache_key = "model_result_{}".format(slug)
	return JsonResponse({'done': cache.get(cache_key) is not None})


def home(request):
	return render(request, 'home.html', {})

def about(request):
	return render(request, 'about.html', {})
