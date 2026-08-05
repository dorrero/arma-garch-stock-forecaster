import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def saveBasicPlot(data, path, name):

	fig = plt.figure()
	plt.plot(data.index, data.Close)
	plt.xlabel("Date")
	plt.xticks(rotation=45, ha='right', fontsize=10)
	plt.ylabel("Stock Price")
	plt.title("Trend over Given Range")
	fig.subplots_adjust(bottom = 0.2)
	fig.savefig(path + '/' + name)
	plt.close(fig)
	return fig


def saveReturnsPlot(returns_data, path, name):

	fig = plt.figure()
	plt.plot(returns_data.index, returns_data)
	plt.xlabel("Date")
	plt.xticks(rotation=45, ha='right', fontsize=10)
	plt.ylabel("Returns")
	plt.title("Returns Trend over Given Range")
	fig.subplots_adjust(bottom = 0.2)
	fig.savefig(path + '/' + name)
	plt.close(fig)
	return fig