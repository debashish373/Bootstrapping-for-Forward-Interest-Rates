import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

class Bootstrap:
    
    def __init__(self):
        pass
    
    def day_count(self):
        pass
    
    def bootstrap(self,df):
        disc=[]
        disc.append(1/(1+((1/360)*df.PX[0]/100)))
        df['tou']=(df['DC']-df['DC'].shift(1))/360
        df['tou'].iloc[0]=df['DC'].iloc[0]/360
        
        for i in range(0,len(df)-1):
            tou=df.loc[i+1,'tou']
            s=df.loc[i+1,'PX']/100
            disc.append((1-s*np.dot(df.tou[0:i+1],disc))/(1+s*tou))
            
        df['DF']=disc
        df['ZR']=-np.log(df['DF'])/(df['DC']/360)
        df['ZR']=df['ZR']*100
        
        return df[['DF','ZR']]

    def forward(self,df):
        forward=[]
        forward.append(df.PX_3m[0]/100)
        df['tou']=(df['DC']-df['DC'].shift(1))/360
        df['tou'].iloc[0]=df['DC'].iloc[0]/360
        
        for i in range(0,len(df)-1):
            X=(df.PX_3m[i+1]/100)*np.dot(df.tou[0:i+2],df.DF[0:i+2])
            Y=np.dot(df.DF[0:i+1],forward*df.tou[0:i+1])
            forward.append((X-Y)/(df.DF[i+1]*df.tou[i+1]))
        
        df['Forward']=forward
        df['Forward']=df['Forward']*100
        return df[['Tenor','Forward']]

    def FX_forward(self,eur,usd,basis,EUR_USD_XRate):
        #pass
        #upto 10 year
        #For tenors greater than 10y using CCS
        df1=usd[usd.Year>10][['Tenor','DF','ZR','Year']].rename(columns={'DF':'DF_USD','ZR':'ZR_USD'})
        df2=eur[eur.Year>10][['DF','ZR','Year']].rename(columns={'DF':'DF_EUR','ZR':'ZR_EUR'})
        df3=basis[basis.Year>10][['Basis','Year']]
        df=pd.merge(df1,df2,on='Year',how='left')
        df=pd.merge(df,df3,on='Year',how='left')
        df['FX_Forward']=EUR_USD_XRate*np.power(((1+df['ZR_USD']/100-df['Basis']/10000)/(1+df['ZR_EUR']/100)),df['Year'])
        df['FX_Points']=(df['FX_Forward']-EUR_USD_XRate)*10000
        return df[['Tenor','FX_Points','FX_Forward']]

    def basis(self,df):
        df['tou']=(df['DC']-df['DC'].shift(1))/360
        df['tou'].iloc[0]=df['DC'].iloc[0]/360
        dollar_disc=[]
        X0=(df.DF[0]+(df.DF[0]*(df.Forward1[0]/100+df.Basis[0]/10000)*df.tou[0]))/(1+(df.Forward2[0]/100)*df.tou[0])
        dollar_disc.append(X0)
        
        for i in range(0,len(df)-1):
            X=df.DF[i+1]+np.dot(df.DF[0:i+2],(df.Forward1[0:i+2]/100+df.Basis[0:i+2]/10000)*df.tou[0:i+2])
            Y=np.dot(dollar_disc[0:i+1],(df.Forward2[0:i+1]/100)*df.tou[0:i+1])
            dollar_disc.append((X-Y)/(1+df.Forward2[i+1]/100*df.tou[i+1]))
    
        df['Dollar_DF_DC']=dollar_disc
        df['Dollar_ZR_DC']=-np.log(df['Dollar_DF_DC'])/(df['DC']/360)
        df['Dollar_ZR_DC']=df['Dollar_ZR_DC']*100
        return df[['Dollar_DF_DC','Dollar_ZR_DC']]

    def plot_dcs(self,df):
        fig1 = plt.figure(figsize=(15,5))

        x=df.Year
        y1=df.Dollar_ZR_DC
        y3=df.ZR

        ax1 = fig1.add_subplot(111)
        line1, = ax1.plot(x,y1,color='black')
        line1.set_label('USD')

        line2, = ax1.plot(x,y3,color='green')
        line2.set_label('EUR')

        ax1.legend()
        plt.title('Bootstrapped curves DC Stripping')
        plt.show()
