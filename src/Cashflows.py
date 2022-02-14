import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import *

import warnings
warnings.filterwarnings('ignore')

class Cashflows:

    def __init__(self,p1,p2,p3,dt_,EUR_USD_XRate,Hist_XRate,curves):

        self.curves=curves

        self.p1=p1
        self.p2=p2
        self.p3=p3
        self.EUR_USD_XRate=EUR_USD_XRate
        self.Hist_XRate=Hist_XRate

        self.Dollar_Notional=1e6 # 1 million D Notional
        self.Euro_Notional={}
        self.Initial_Swap_value={}

        self.CF_USD={}
        self.CF_EUR={}

        self.DF_USD={}
        self.DF_EUR={}
        self.DF_USD_={}#Used for FX

        self.Disc_CF_USD={}
        self.Disc_CF_EUR={}

        self.USD_coupon_dates={}
        self.EUR_coupon_dates={}
        self.common_dates={}

        self.Numerator={}
        self.Denominator_={}
        self.Denominator={}

        self.Numerator2={}
        self.Denominator2={}

        self.CF_USD={}
        self.CF_EUR={}

        self.FX_={}

        self.common_dates={}
        self.dt_=dt_

    def y_pred(self,x,p):
        y=p[6]*x**6+p[5]*x**5+p[4]*x**4+p[3]*x**3+p[2]*x**2+p[1]*x+p[0]
        return y

    def CF_Modeling_USD(self,df,proceeds):
        
        for id, row in df[df['Next Coupon Date']!=''].iterrows():
            coupon=float(row['Coupon'])
            coupon_freq=float(row['Coupon Frequency'])
            isin=row['ISIN']
            
            if coupon_freq==1:
                cf=12
            elif coupon_freq==2:
                cf=6
            elif coupon_freq==4:
                cf=3
                
            next_cpn_date=pd.to_datetime(row['Next Coupon Date'])
            today=self.dt_
            start_date=next_cpn_date+relativedelta(months=-cf)
            
            while(start_date>today):
                start_date=start_date+relativedelta(months=-cf)
            
            workout_date=pd.to_datetime(row['Workout date'])
            
            self.USD_coupon_dates[isin]=[]
            self.USD_coupon_dates[isin].append(workout_date)
            date=workout_date
            i=1
            
            while(date>start_date):
                new_date=workout_date+relativedelta(months=-cf*i)
                if new_date>start_date:
                    self.USD_coupon_dates[isin].append(new_date)
                i=i+1

                date=workout_date+relativedelta(months=-cf*i)
                
            self.USD_coupon_dates[isin].append(start_date)
            self.USD_coupon_dates[isin]=self.USD_coupon_dates[isin][::-1]
            self.USD_coupon_dates[isin]=list(np.unique(self.USD_coupon_dates[isin]))

            price=df[df.ISIN==isin].Price.values[0]
            
            if proceeds:
                self.Euro_Notional[isin]=(self.Dollar_Notional/self.EUR_USD_XRate)*(price/100)
                self.Initial_Swap_value[isin]=0
                self.CF_USD[isin]=[]
                
                for i in range(0,len(self.USD_coupon_dates[isin])-1):
                    try:
                        if i==0 and abs((self.USD_coupon_dates[isin][1]-self.USD_coupon_dates[isin][0])-(self.USD_coupon_dates[isin][2]-self.USD_coupon_dates[isin][1])).days>5:
                            day_frac=(self.USD_coupon_dates[isin][i+1]-self.USD_coupon_dates[isin][i]).days/360
                        else:
                            day_frac=cf/12#180/360
                    except:
                        pass
                    self.CF_USD[isin].append(self.Dollar_Notional*day_frac*(coupon/100))
                
                self.CF_USD[isin][-1]=self.CF_USD[isin][-1]+self.Dollar_Notional
                    
            else:#ParPar Swap
                self.Euro_Notional[isin]=(self.Dollar_Notional/self.EUR_USD_XRate)
                self.Initial_Swap_value[isin]=((100-price)/100)*(self.Dollar_Notional/self.EUR_USD_XRate)
                self.CF_USD[isin]=[]
                
                for i in range(0,len(self.USD_coupon_dates[isin])-1):
                    try:
                        if i==0 and abs((self.USD_coupon_dates[isin][1]-self.USD_coupon_dates[isin][0])-(self.USD_coupon_dates[isin][2]-self.USD_coupon_dates[isin][1])).days>5:
                            day_frac=(self.USD_coupon_dates[isin][i+1]-self.USD_coupon_dates[isin][i]).days/360
                        else:
                            day_frac=cf/12#180/360
                    except:
                        day_frac=12/12
                        
                    self.CF_USD[isin].append(self.Dollar_Notional*day_frac*(coupon/100))
                
                self.CF_USD[isin][-1]=self.CF_USD[isin][-1]+self.Dollar_Notional
            
            self.DF_USD[isin]=[]
            
            for i in range(0,len(self.USD_coupon_dates[isin])-1):
                self.DF_USD[isin].append(self.y_pred((self.USD_coupon_dates[isin][i+1]-self.USD_coupon_dates[isin][0]).days/360,self.p1))

            self.Disc_CF_USD[isin]=list(np.array(self.CF_USD[isin]) * np.array(self.DF_USD[isin]))

        return self.Disc_CF_USD


    def CF_Modeling_EUR(self,df,proceeds,alternative):
        
        for id, row in df[df['Next Coupon Date']!=''].iterrows():
            coupon=100
            coupon_freq=float(row['Coupon Frequency'])
            isin=row['ISIN']
            
            if coupon_freq==1:
                cf=12
            elif coupon_freq==2:
                cf=6
            elif coupon_freq==4:
                cf=3
                
            next_cpn_date=pd.to_datetime(row['Next Coupon Date'])
            today=self.dt_
            start_date=next_cpn_date+relativedelta(months=-cf)
            
            while(start_date>today):
                start_date=start_date+relativedelta(months=-cf)
            
            workout_date=pd.to_datetime(row['Workout date'])
            
            self.EUR_coupon_dates[isin]=[]
            self.EUR_coupon_dates[isin].append(workout_date)
            date=workout_date
            i=1
            
            while(date>start_date):
                new_date=workout_date+relativedelta(months=-12*i)
                if new_date>start_date:
                    self.EUR_coupon_dates[isin].append(new_date)
                i=i+1
                date=workout_date+relativedelta(months=-12*i)
                
            self.EUR_coupon_dates[isin].append(start_date)
            self.EUR_coupon_dates[isin]=self.EUR_coupon_dates[isin][::-1]
            self.EUR_coupon_dates[isin]=list(np.unique(self.EUR_coupon_dates[isin]))
            
            price=df[df.ISIN==isin].Price.values[0]
            missing=[]
            
            if proceeds:
                self.Euro_Notional[isin]=(self.Dollar_Notional/self.EUR_USD_XRate)*(price/100)
                self.Initial_Swap_value[isin]=0
                self.CF_EUR[isin]=[]
                
                for i in range(0,len(self.EUR_coupon_dates[isin])-1):
                    try:
                        if i==0 and abs((self.EUR_coupon_dates[isin][1]-self.EUR_coupon_dates[isin][0])-(self.EUR_coupon_dates[isin][2]-self.EUR_coupon_dates[isin][1])).days>5:
                            day_frac=(self.EUR_coupon_dates[isin][i+1]-self.EUR_coupon_dates[isin][i]).days/360
                        else:
                            day_frac=360/360
                        
                    except:
                        missing.append(isin)
                        
                    self.CF_EUR[isin].append(self.Euro_Notional[isin]*(day_frac)*(coupon/100))
                    
                missing=np.unique(missing)
                self.Denominator_[isin]=self.CF_EUR[isin].copy()
                self.CF_EUR[isin][-1]=self.CF_EUR[isin][-1]+(self.Euro_Notional[isin])
                
            else:#ParPar Swap
                self.Euro_Notional[isin]=(self.Dollar_Notional/self.EUR_USD_XRate)
                self.Initial_Swap_value[isin]=((100-price)/100)*(self.Dollar_Notional/self.EUR_USD_XRate)
                self.CF_EUR[isin]=[]
                           
                for i in range(0,len(self.EUR_coupon_dates[isin])-1):
                    try:
                        if i==0 and abs((self.EUR_coupon_dates[isin][1]-self.EUR_coupon_dates[isin][0])-(self.EUR_coupon_dates[isin][2]-self.EUR_coupon_dates[isin][1])).days>5:
                            day_frac=(self.EUR_coupon_dates[isin][i+1]-self.EUR_coupon_dates[isin][i]).days/360
                        else:
                            day_frac=360/360
                    except:
                        missing.append(isin)
                        day_frac=1
                    self.CF_EUR[isin].append(self.Euro_Notional[isin]*day_frac*(coupon/100))
                    
                missing=np.unique(missing)
                self.Denominator_[isin]=self.CF_EUR[isin].copy()
                self.CF_EUR[isin][-1]=self.CF_EUR[isin][-1]+self.Euro_Notional[isin]
                
            self.DF_EUR[isin]=[]
            self.FX_[isin]=[]

            try:
                self.FX_[isin].append(self.Hist_XRate[self.Hist_XRate.DATE==self.EUR_coupon_dates[isin][0]]['EURUSD BGN Curncy'].values[0])
            except:
                self.FX_[isin].append(self.Hist_XRate['EURUSD BGN Curncy'].iloc[-1])
            
            for i in range(0,len(self.EUR_coupon_dates[isin])-1):
                self.DF_EUR[isin].append(self.y_pred((self.EUR_coupon_dates[isin][i+1]-self.EUR_coupon_dates[isin][0]).days/360,self.p2))
                self.FX_[isin].append(self.y_pred(np.round((self.EUR_coupon_dates[isin][i+1]-dt.datetime.today()).days/360,2),self.p3))
                
            self.Disc_CF_EUR[isin]=list(np.array(self.CF_EUR[isin]) * np.array(self.DF_EUR[isin]))
            
            self.Numerator[isin]=[]
            self.Numerator[isin].append(-self.Euro_Notional[isin]*self.DF_EUR[isin][-1]*1)
            self.Denominator[isin]=list(np.array(self.Denominator_[isin]) * np.array(self.DF_EUR[isin])*1)
            
            #For alternatives
            if alternative:
    
                self.DF_USD_[isin]=[]
                self.common_dates[isin]=[]
                self.common_dates[isin]=[date for date in self.USD_coupon_dates[isin] if date in self.EUR_coupon_dates[isin]]
                
                for i in range(0,len(self.common_dates[isin])-1):
                    self.DF_USD_[isin].append(self.y_pred((self.common_dates[isin][i+1]-self.common_dates[isin][0]).days/360,self.p1))
                    
                self.Numerator2[isin]=[]
                self.Numerator2[isin].append(-self.Euro_Notional[isin]*self.DF_USD[isin][-1]*1)
                self.Denominator2[isin]=list(np.array(self.Denominator_[isin]) * np.array(self.DF_USD_[isin])*1)

        return self.Disc_CF_EUR, self.FX_, self.Numerator2, self.Denominator2


    def IRR(self,df,proceeds=False):
        X_yield=[]

        Disc_CF_USD=self.CF_Modeling_USD(df,proceeds)
        Disc_CF_EUR,FX_,Numerator2,Denominator2=self.CF_Modeling_EUR(df,proceeds,alternative=True)

        for id, row in df.iterrows():
            isin=row['ISIN']
            X_yield.append(((-(np.array(Disc_CF_USD[isin])*-1).sum()+self.Initial_Swap_value[isin]*self.EUR_USD_XRate+(np.array(Numerator2[isin])*np.array(FX_[isin][-1])).sum())/((np.array(Denominator2[isin])*np.array(FX_[isin][1:])).sum()))*100)    
        
        df['X_Yield']=X_yield

        return df[['ISIN','X_Yield']]
