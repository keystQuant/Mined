'''
Mined.

 ʕ•ﻌ•ʔ     ʕ•ﻌ•ʔ
( >  <) ♡ (>  < )
 u   u     u   u

feat. peepee
with love...
'''
import math, datetime, time
from datetime import datetime
import pandas as pd

from algorithms.data import Data


class PortfolioProcessor(object):
    '''

    **설명: 포트폴리오에 사용할 자보금과 포트폴리오에 추가하고 싶은 주식 종목들 인풋으로 받아,
           동일 비중 포트폴리오를 형성해 주는 클래스다.

           동일 비중 포트폴리오를 생성하는데 사용가능한 다양한 알고리즘이 있지만,
           마인드의 알고리즘은 이런 단계를 거친다: (예를 들어 자본금 1000원으로 가격이 각각
           100, 200, 300인 주식을 사서 동일 비중 포트폴리오를 만든다고 생각해보자)

               - 1000을 3으로 나눈다.
               - 위에서 계산한 값보다 가격이 높은 종목은 고려하지 않는다.
               - 포트폴리오에 모든 종목을 한 주씩 추가한다.
               - 남은 자본금을 계산한다 --> 1000 - 100 - 200 - 300 = 400
               - 400을 3으로 나눈다.
               - 위에서 계산한 값보다 가격이 높은 종목은 고려하지 않는다.
               - 가격이 100, 200인 종목으로만 포트폴리오를 만든다.
               - 400으로 2를 나눈다. (200)
               - 가격이 200 미만인 종목은 제외 한다 (없다)
               - 각 종목을 하나씩 포트폴리오에 추가한다.
               - 남은 자본금 금액을 계산한다 --> 400 - 100 - 200 = 100
               - 위와 같은 절차를 반복한다...

          결과: 100: 3개, 200: 2개, 300: 1개로 포트폴리오를 구성하게 된다.

    **태스크:
    1.

    '''

    #*** UPDATE: 20180730 ***#
    def __init__(self, portfolio_type, stocks, capital):
        ## ** 인자 설명 ** ##
        ### portfolio_type (str) --> 포트폴리오 타입은 S 혹은 CS이다. (S: Stock, CS: Cash + Stock)
        ### stocks (list) --> ['000020', '000030'] --> 리스트 형식]
        ### capital (int) --> 총 투자 자본금

        # Data 인스턴스 생성/부여
        self.data = Data('portfolio', stocks)

        # 포트폴리오의 메타데이터를 만든다
        port = {
            'portfolio': portfolio_type,
            'stocks': stocks,
            'stock_count': len(stocks),
            'capital': capital,
            'capital_per_stock': capital//len(stocks) # 각 주식에 기본적으로 얼마를 투자해야 하는지 계산
        } # 입력받은 인자로 포트폴리오 기본 정보 설정하기

        # 클래스 속성 설정
        self.port_params = port # 위에서 만든 port 딕셔너리를 속성으로 만든다
        self.ratio_dict = {'cash': 0} # 시작 현금 금액은 0원이다.
        # 만약, port['portfolio'] == 'S' 이면 현금 금액은 계속 0이다.
        # 만약, port['portfolio'] == 'CS' 이면 현금 금액은 알고리즘에 따라 변해야 한다.
        # 앞으로, self.ratio_dict에 다른 종목들 비중도 계산하여 업데이트해줄 것이다

        # Data 인스턴스를 생성하여 stocks에서 입력받은 주가 정보를 받아온다.
        ohlcv_data_list = self.data.make_ohlcv_data() # OHLCV 정보를 받아온다
        self.ohlcv_inst_list = ohlcv_data_list

    def get_recent_stock_close_price(self, ticker):
        # 종목의 코드를 인자로 받아서 그 종목의 최근 종가를 리턴하는 메소드
        pass

    def initial_distribution(self):
        # 초기에 자본을 분배할 때는 모든 종목에 동일한 비중의 자본금을 나누는 형식으로 진행한다
        port = self.port_params

        for stock in port['stocks']:
            code = stock.code.code
            ohlcv = self.get_recent_stock_close_price(code) # 제일 최근 종가 가져오기
            if ohlcv.exists():
                ohlcv_inst = ohlcv.first() # get the most recent ohlcv instance
                ticker_inst = Ticker.objects.filter(code=ohlcv_inst.code).order_by('-date').first()

                self.ohlcv_inst_list.append(ohlcv_inst)

                name = ticker_inst.name
                date = ohlcv_inst.date
                close_price = int(ohlcv_inst.close_price)
                stock_data = {
                    'name': name,
                    'date': date,
                    'price': close_price
                }
                self.ratio_dict[code] = stock_data
                capital_per_stock = port['capital_per_stock']
                if close_price < capital_per_stock:
                    stock_num = capital_per_stock//close_price
                    invested = int(stock_num * close_price)
                    self.ratio_dict[code]['invested'] = invested
                    self.ratio_dict[code]['buy_num'] = stock_num
                    self.ratio_dict['cash'] += (capital_per_stock - invested)
                else:
                    self.ratio_dict[code]['invested'] = 0
                    self.ratio_dict[code]['buy_num'] = 0
            else:
                continue

    def redistribute(self):
        left_over_capital = self.ratio_dict['cash']
        ohlcv_inst_list = self.ohlcv_inst_list
        redistribute = left_over_capital > 0
        while redistribute:
            extra_buy = list(filter(lambda x: x.close_price < left_over_capital, ohlcv_inst_list))
            if len(extra_buy) == 0:
                redistribute = False
                continue
            extra_capital_per_stock = left_over_capital//len(extra_buy)
            extra_buy_num = list(map(lambda x: extra_capital_per_stock//x.close_price, extra_buy))
            if sum(extra_buy_num) == 0:
                redistribute = False
                continue
            close_price_list = [ohlcv.close_price for ohlcv in extra_buy]
            reset_left_over = int(left_over_capital - sum(map(lambda x, y: x*y, extra_buy_num, close_price_list)))
            extra_stocks = [ohlcv.code for ohlcv in extra_buy]
            for i in range(len(extra_stocks)):
                extra_invested = extra_buy_num[i]*close_price_list[i]
                self.ratio_dict[extra_stocks[i]]['invested'] += int(extra_invested)
                self.ratio_dict[extra_stocks[i]]['buy_num'] += int(extra_buy_num[i])
            self.ratio_dict['cash'] = reset_left_over
            ohlcv_inst_list = extra_buy
            left_over_capital = reset_left_over
        for key, val in self.ratio_dict.items():
            if key != 'cash':
                stock_ratio = val['invested']/self.port_params['capital']
                self.ratio_dict[key]['ratio'] = float(format(round(stock_ratio, 4), '.4f'))
        pd_inst = PortfolioDiagnosis(portfolio=self.port_params['portfolio'], ratio=self.ratio_dict)
        pd_inst.save()
