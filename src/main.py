import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from Dataset import Dataset
from Cashflows import Cashflows

import warnings
warnings.filterwarnings('ignore')

def run():

    """
    Main function for ParPar/Proceeds yields calculation using the Dual curve approach
    """
    curves,FX,EUR_USD_XRate,Hist_XRate,p1,p2,p3,dt_=Dataset().prepare_dataset(path=r'../sample_mkt_data.pickle',date='2022-02-11')

    df=pd.DataFrame(columns=['Date','ISIN','Price','Coupon','Coupon Frequency','Next Coupon Date','Workout date'],index=[0])
    
    df['Date']=dt_
    df['ISIN']='US91282CDJ71'
    df['Price']=95.15625000
    df['Coupon']=1.375000
    df['Coupon Frequency']=2
    df['Next Coupon Date']='2022-01-15'
    df['Workout date']='2031-11-15'

    yields=Cashflows(p1,p2,p3,dt_,EUR_USD_XRate,Hist_XRate,curves).IRR(df.copy(),proceeds=False)
    print(yields)

if __name__ == "__main__":
    run()
