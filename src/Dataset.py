import pandas as pd
import numpy as np
import pickle
import datetime as dt
from Bootstrap import Bootstrap

import warnings
warnings.filterwarnings('ignore')

class Dataset(Bootstrap):

    def __init__(self) -> None:
        super().__init__()

    def prepare_dataset(self,path,date):
        
        with open(path, 'rb') as f:
            USD_SOFR,EUR_OIS_STR,EURIBOR_3m,USD_3m,Basis,_,Hist_XRate,FXF=pickle.load(f)
        
        if type(date)==str:date=dt.datetime.strptime(date,'%Y-%m-%d')

        USD_SOFR=USD_SOFR[USD_SOFR.DATE==date]
        EUR_OIS_STR=EUR_OIS_STR[EUR_OIS_STR.DATE==date]
        EURIBOR_3m=EURIBOR_3m[EURIBOR_3m.DATE==date]
        USD_3m=USD_3m[USD_3m.DATE==date]
        Basis=Basis[Basis.DATE==date]
        Hist_XRate=Hist_XRate[Hist_XRate.DATE==date]
        FXF=FXF[FXF.DATE==date]        
        
        EUR_USD_XRate=Hist_XRate['EURUSD BGN Curncy'].iloc[-1]

        #Modifications
        EUR_OIS_STR=EUR_OIS_STR[['ID','PX']].rename(columns={'ID':'Tenor'}).dropna().reset_index(drop=True)
        USD_SOFR=USD_SOFR[['ID','PX']].rename(columns={'ID':'Tenor'}).dropna().reset_index(drop=True)      
        
        #Bootstrapping
        dict_={'D':1,'W':7,'M':30,'Y':360}
        EUR_OIS_STR['Days1']=EUR_OIS_STR.Tenor.apply(lambda x: x[:-1]).astype('int')
        EUR_OIS_STR['Days2']=EUR_OIS_STR.Tenor.apply(lambda x: dict_.get(x[-1]))
        EUR_OIS_STR['DC']=EUR_OIS_STR['Days1']*EUR_OIS_STR['Days2']       
        EUR_OIS_STR['Year']=EUR_OIS_STR['DC']/360
        EUR_OIS_STR[['DF','ZR']]=self.bootstrap(EUR_OIS_STR.copy())
        
        USD_SOFR['Days1']=USD_SOFR.Tenor.apply(lambda x: x[:-1]).astype('int')
        USD_SOFR['Days2']=USD_SOFR.Tenor.apply(lambda x: dict_.get(x[-1]))
        USD_SOFR['DC']=USD_SOFR['Days1']*USD_SOFR['Days2']
        USD_SOFR['Year']=USD_SOFR['DC']/360
        USD_SOFR[['DF','ZR']]=self.bootstrap(USD_SOFR.copy())
        
        #Dual Curve Stripping
        EURIBOR_3m=EURIBOR_3m[['ID','PX']].rename(columns={'ID':'Tenor','PX':'PX_3m'}).dropna(subset=['PX_3m'])
        EURIBOR_3m['Days1']=EURIBOR_3m.Tenor.apply(lambda x: x[:-1]).astype('int')
        EURIBOR_3m['Days2']=EURIBOR_3m.Tenor.apply(lambda x: dict_.get(x[-1]))
        EURIBOR_3m['DC']=EURIBOR_3m['Days1']*EURIBOR_3m['Days2']
        EURIBOR_3m=pd.merge(EURIBOR_3m,EUR_OIS_STR[['Tenor','DF','PX']],on='Tenor',how='left').dropna(subset=['PX']).reset_index(drop=True).dropna(subset=['PX_3m']).reset_index(drop=True)
        
        temp1=pd.DataFrame()
        temp1[['Tenor','Forward']]=self.forward(EURIBOR_3m.copy())
        EUR_OIS_STR=pd.merge(EUR_OIS_STR,temp1,on='Tenor',how='left')
        
        USD_3m=USD_3m[['ID','PX']].rename(columns={'ID':'Tenor','PX':'PX_3m'}).dropna(subset=['PX_3m'])
        USD_3m['Days1']=USD_3m.Tenor.apply(lambda x: x[:-1]).astype('int')
        USD_3m['Days2']=USD_3m.Tenor.apply(lambda x: dict_.get(x[-1]))
        USD_3m['DC']=USD_3m['Days1']*USD_3m['Days2']
        USD_3m=pd.merge(USD_3m,USD_SOFR[['Tenor','DF','PX']],on='Tenor',how='left').dropna(subset=['PX']).reset_index(drop=True).dropna(subset=['PX_3m']).reset_index(drop=True)
        
        temp2=pd.DataFrame()
        temp2[['Tenor','Forward']]=self.forward(USD_3m.copy())
        USD_SOFR=pd.merge(USD_SOFR,temp2,on='Tenor',how='left')
        
        #Basis
        Basis=Basis.rename(columns={'ID':'Tenor','PX':'Basis'})
        EUR_OIS_STR=EUR_OIS_STR.dropna(subset=['Forward']).reset_index(drop=True)
        EUR_OIS_STR=pd.merge(EUR_OIS_STR,Basis,on='Tenor',how='left').dropna(subset=['Basis']).reset_index(drop=True)
        EUR_OIS_STR=pd.merge(EUR_OIS_STR,USD_3m[['Tenor','PX']].rename(columns={'PX':'PX_USD'}),on='Tenor',how='left').dropna(subset=['PX_USD']).reset_index(drop=True)
        EUR_OIS_STR=pd.merge(EUR_OIS_STR.rename(columns={'Forward':'Forward1'}),USD_SOFR[['Tenor','Forward']].rename(columns={'Forward':'Forward2'}),on='Tenor',how='left')
        
        EUR_OIS_STR[['Dollar_DF_DC','Dollar_ZR_DC']]=self.basis(EUR_OIS_STR.copy())
        EUR_OIS_STR=pd.merge(EUR_OIS_STR,USD_SOFR[['Tenor','ZR']].rename(columns={'ZR':'Dollar_ZR_SC'}),on='Tenor',how='left')
        
        curves=EUR_OIS_STR.copy()

        #FX Forwards
        Hist_XRate=Hist_XRate[['DATE','EURUSD BGN Curncy']]
        FX=FXF[['ID','PX']].rename(columns={'ID':'Tenor','PX':'FX_Points'})
        FX['FX_Forward']=FX['FX_Points']/10000+EUR_USD_XRate

        DF_201=self.bootstrap(EURIBOR_3m.iloc[:,:-2].rename(columns={'PX_3m':'PX'}))
        DF_23=self.bootstrap(USD_3m.iloc[:,:-2].rename(columns={'PX_3m':'PX'}))

        DF_201['Tenor']=EURIBOR_3m['Tenor']
        DF_23['Tenor']=USD_3m['Tenor']

        DF_201['Days1']=DF_201.Tenor.apply(lambda x: x[:-1]).astype('int')
        DF_201['Days2']=DF_201.Tenor.apply(lambda x: dict_.get(x[-1]))
        DF_201['DC']=DF_201['Days1']*DF_201['Days2']
        DF_201['Year']=DF_201['DC']/360

        DF_23['Days1']=DF_23.Tenor.apply(lambda x: x[:-1]).astype('int')
        DF_23['Days2']=DF_23.Tenor.apply(lambda x: dict_.get(x[-1]))
        DF_23['DC']=DF_23['Days1']*DF_23['Days2']
        DF_23['Year']=DF_23['DC']/360

        Basis['Days1']=Basis.Tenor.apply(lambda x: x[:-1]).astype('int')
        Basis['Days2']=Basis.Tenor.apply(lambda x: dict_.get(x[-1]))
        Basis['DC']=Basis['Days1']*Basis['Days2']
        Basis['Year']=Basis['DC']/360

        FX=FX.append(self.FX_forward(DF_201,DF_23,Basis,EUR_USD_XRate)).reset_index(drop=True)
        FX['Days1']=FX.Tenor.apply(lambda x: x[:-1]).astype('int')
        FX['Days2']=FX.Tenor.apply(lambda x: dict_.get(x[-1]))
        FX['DC']=FX['Days1']*FX['Days2']
        FX['Year']=FX['DC']/360
        FX=FX.dropna(subset=['FX_Forward']).reset_index(drop=True)
        
        p1=np.poly1d(np.polyfit(curves.Year, curves.Dollar_DF_DC, 6))#USD
        p2=np.poly1d(np.polyfit(curves.Year, curves.DF, 5))#EUR
        p3=np.poly1d(np.polyfit(FX.Year, FX.FX_Forward, 4))#FXF

        return curves, FX, EUR_USD_XRate, Hist_XRate, p1, p2, p3, date