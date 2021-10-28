import pandas as pd
import warnings

import time
from datetime import datetime
from datetime import date

from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm

import plotly.graph_objects as go
import plotly.express as px

warnings.filterwarnings('ignore')


class forecastingGoogle():

    def __init__(self, df):

        self.df = df
        self.data_clean = None
        self.model = None
        self.train_dt = None
        self.test_dt = None
        self.graphs_show = True

    def pre_pro(self):

        df = self.df

        # Takinh the propriete column names

        # Rename the columns
        self.data_clean = df.reset_index().rename(columns={'index': 'week', 'Category: All categories': 'score'})

        # Remove the header row
        self.data_clean = self.data_clean.iloc[1:len(self.data_clean)]

        # Fixing formats
        self.data_clean.week = pd.to_datetime(self.data_clean.week, format='%Y-%m-%d')
        self.data_clean.score = self.data_clean.score.astype(int)

        self.data_clean['year'] = self.data_clean['week'].dt.year
        self.data_clean['month'] = self.data_clean['week'].dt.month
        self.data_clean['day'] = self.data_clean['week'].dt.day

        self.data_clean = self.data_clean[['week', 'year', 'month', 'day', 'score']]

        print('*** Preprocessing ***\n\nOur Clean Data are:\n')
        print(self.data_clean.head(5))

        return self.data_clean

    def graphs_gen(self):

        # Showing The avg allocation month
        m_dt = self.data_clean.groupby('month').score.mean()
        y = m_dt
        fig_avg_month = go.Figure(data=[go.Bar(
            y=y,
            x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Dec'],
            text=y,
            textposition='auto',
        )])
        fig_avg_month.update_layout(title_text='Avg Allocation per Month', title_x=0.5)
        if self.graphs_show:
            fig_avg_month.show()

        # Showing The avg allocation Year
        todays_date = date.today()
        year = int(todays_date.year)

        m_dt = self.data_clean.groupby('year').score.mean()
        y = m_dt
        fig_avg_year = go.Figure(data=[go.Bar(
            y=y,
            x=[year - 5, year - 4, year - 3, year - 2, year - 1, year],
            text=y,
            textposition='auto',
        )])
        fig_avg_year.update_layout(title_text='Avg Allocation per Year', title_x=0.5)
        if self.graphs_show:
            fig_avg_year.show()

        # Showing The timeseries
        fig_timeseries = px.line(self.data_clean, x='week', y="score")
        fig_timeseries.update_layout(title_text='Search Score Over Time', title_x=0.5)
        if self.graphs_show:
            fig_timeseries.show()

        return fig_timeseries, fig_avg_year, fig_avg_month

    def train_sarimax_model(self):

        # Adfuller metric to find best design
        def adfuler_mets(time_series):

            print('Results of Dickey-Fuller Test:')
            dftest = adfuller(time_series, autolag='AIC')
            dfoutput = pd.Series(dftest[0:4],
                                 index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])

            for key, value in dftest[4].items():
                dfoutput['Critical Value (%s)' % key] = value

            print('*** Adfuller:\n', dfoutput)

        adfuler_mets(self.data_clean['score'])  # .diff().dropna().diff().dropna()


        # Prepare test and train data
        all_len = len(self.data_clean)
        ts_tr = int(all_len * 0.7)
        ts_te = all_len - ts_tr

        train_data = self.data_clean[0:ts_tr]
        self.train_dt = train_data
        test_data = self.data_clean.tail(ts_te)
        self.test_dt = test_data

        # Prepare Arima Model
        my_order = (2, 1, 0)
        my_seasonal_order = (0, 1, 0, 54)
        model = SARIMAX(train_data.score, order=my_order, seasonal_order=my_seasonal_order)

        # fit the model
        model_fit = model.fit()
        # print(model_fit.summary())

        # get the predictions and residuals
        predictions = model_fit.forecast(len(test_data.score))
        predictions = pd.Series(predictions, index=test_data.index)
        residuals = test_data.score - predictions

        # # Vis Residuals
        fig_residual = go.Figure()
        fig_residual.add_trace(go.Scatter(y=residuals, name='residuals'))
        fig_residual.add_hline(y=0, line_width=3, line_dash="dash", line_color="green")
        fig_residual.update_layout(title_text='Residuals from SARIMA model', title_x=0.5)
        fig_residual.add_annotation(
            # x=2,
            y=max(residuals),
            xref="x",
            yref="y",
            text='Residual mean is:'+str(residuals.mean()),
            showarrow=False,
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="#ffffff"
            ),
            align="center",
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#636363",
            ax=20,
            ay=-30,
            bordercolor="#c7c7c7",
            borderwidth=2,
            borderpad=4,
            bgcolor="#ff7f0e",
            opacity=0.8
        )
        if self.graphs_show:
            fig_residual.show()

        fig_res = go.Figure()
        fig_res.add_trace(go.Scatter(x=self.data_clean['week'], y=self.data_clean['score'], name='Data Original'))
        fig_res.add_trace(go.Scatter(x=self.train_dt['week'], y=self.train_dt['score'], name='Train Data'))
        fig_res.add_trace(go.Scatter(x=self.test_dt['week'], y=self.test_dt['score'], name='Test Data'))
        fig_res.add_trace(go.Scatter(x=self.test_dt['week'], y=predictions, name='Predictions'))
        fig_res.update_layout(title_text='Original Data and Predictions', title_x=0.5)
        if self.graphs_show:
            fig_res.show()

        return fig_res, fig_residual


if __name__ == "__main__":
    df = pd.read_csv('data/sun.csv')

    a = forecastingGoogle(df)

    a.pre_pro()

    a.graphs_gen()

    a.train_sarimax_model()
