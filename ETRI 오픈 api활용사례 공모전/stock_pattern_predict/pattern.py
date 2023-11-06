import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import warnings
import FinanceDataReader as fdr
warnings.filterwarnings('ignore')


class PatternFinder():
    def __init__(self, period=5):
        self.period = period
        self.kospi = pd.read_csv('코스피.csv')
        self.kosdaq = pd.read_csv('코스닥.csv') 
        self.code_kospi = fdr.StockListing('KOSPI').Code.values
        self.code_kosdaq = fdr.StockListing('KOSDAQ').Code.values

    def set_stock(self, code: str):
        self.code = code
        self.data = fdr.DataReader(code)
        self.close = self.data['Close']
        self.change = self.data['Change']
        return self.data

    def search(self, start_date, end_date, threshold=0.98):
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)

        # Condition to use KOSPI or KOSDAQ data based on the stock code
        if self.code in self.code_kospi:
            base_df = self.kospi
        elif self.code in self.code_kosdaq:
            base_df = self.kosdaq
        else:
            raise ValueError("Stock code not found in KOSPI or KOSDAQ listings")
    
        # Convert the 'Date' column of the chosen dataframe to datetime objects
        base_df['Date'] = pd.to_datetime(base_df['Date'])
    
        # Filter the chosen dataframe by date range and select the 'Close' column
        base = base_df[(base_df['Date'] >= self.start_date) & (base_df['Date'] <= self.end_date)]['Close']
    
        # Normalize the data
        self.base_norm = (base - base.min()) / (base.max() - base.min())
        self.base = base
    
        window_size = len(base)
        moving_cnt = len(self.data) - window_size - self.period - 1
        cos_sims = self.__cosine_sims(moving_cnt, window_size)
    
        self.window_size = window_size
        cos_sims = cos_sims[cos_sims > threshold]
        return cos_sims
        
    
    def __cosine_sims(self, moving_cnt, window_size):
        def cosine_similarity(x, y):
            return np.dot(x, y) / (np.sqrt(np.dot(x, x)) * np.sqrt(np.dot(y, y)))
        
        # 유사도 저장 딕셔너리
        sim_list = []

        for i in range(moving_cnt):
            target = self.close[i:i+window_size]

            # Normalize
            target_norm = (target - target.min()) / (target.max() - target.min())

            # 코사인 유사도 저장
            cos_similarity = cosine_similarity(self.base_norm, target_norm)

            # 코사인 유사도 <- i(인덱스), 시계열데이터 함께 저장
            sim_list.append(cos_similarity)
        return pd.Series(sim_list).sort_values(ascending=False)

    
    def plot_pattern(self, idx, period=5):
        if period != self.period:
            self.period = period
            
        top = self.close[idx:idx+self.window_size+period]
        top_norm = (top - top.min()) / (top.max() - top.min())
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.plot(self.base_norm.values, label='base', color='black',  alpha=0.7)
        axis.plot(top_norm.values, label='prediction', color='red', linestyle='dashed')
        axis.plot(top_norm.values[:len(self.base_norm.values)], label='pattern', color='red', linestyle='solid')
        axis.axvline(x=len(self.base_norm)-1, c='tomato', linestyle='dotted')
        axis.axvspan(len(self.base_norm.values)-1, len(top_norm.values)-1, facecolor='yellow', alpha=0.3)
        axis.legend()
        axis.get_yaxis().set_visible(False)
        axis.get_xaxis().set_visible(False)
        
        preds = self.change[idx+self.window_size: idx+self.window_size+period]
        
        print(f'pred: {round(preds.mean(),5)*100} % ')
        return fig

    
    def stat_prediction(self, result, period=5):
        idx_list = list(result.keys())
        mean_list = []
        for idx in idx_list:
            pred = self.change[idx+self.window_size: idx+self.window_size+period]
            mean_list.append(pred.mean())
        return np.array(mean_list)
    


class RealProfit:
    def __init__(self, pattern_finder):
        self.pattern_finder = pattern_finder  # PatternFinder 객체를 전달
        self.start_date = self.pattern_finder.start_date
        self.end_date = self.pattern_finder.end_date
        self.code = self.pattern_finder.code

    def calculate_profit(self):
        # start_date, end_date, code 정보를 활용하여 실제 수익률을 계산
        # 주식 데이터와 KOSPI 지수 데이터를 가져오고 수익률을 계산하는 등의 작업 수행
        start_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)
        
        stock_data = fdr.DataReader(self.code, start_date, end_date)
        stock_returns = stock_data['Close'].iloc[-1]/stock_data['Close'].iloc[0]  # Daily stock returns
        
        return f'{round(stock_returns, 5)} %'
    


