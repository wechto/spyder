# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 21:17:37 2018

@author: administered
"""


import pymysql
import numpy as np, pandas as pd
import os, time, sys

import initialization, mPlot

class mSQL:
    
    def __init__(self):
        mSQL.connect = pymysql.connect(host=initialization.host,port=initialization.port,
                          user=initialization.user,passwd=initialization.passwd,
                          db=initialization.database,charset=initialization.charset)
        mSQL.cursor = mSQL.connect.cursor();

    def close(self):        
        mSQL.cursor.close()
        mSQL.connect.close()

    # 查看分类数据
    def mClassificate(temp,*var):
        #print(var)
        for v in var:
            sql = 'SELECT '+v+', COUNT( '+v + ') as size' +' FROM '+ initialization.table+' GROUP BY ' +v;
            #sql= 'SELECT user_identity_type,COUNT(user_identity_type) as size FROM ods_wei_order_info GROUP BY user_identity_type'
            mSQL.cursor.execute(sql);
            res = []
            for row in mSQL.cursor.fetchall():
                #print(type(row))
                res.append(list(row))
                #print('{} : {}'.format(v,row));
            print('')
            resNp = np.array(res)
            resNp_ = np.true_divide(resNp[:,1],np.linspace(sum(resNp[:,1]),sum(resNp[:,1]),resNp.shape[0]))
            resNp=np.column_stack((resNp,resNp_))
            for i in range(resNp.shape[0]):
                print('{} : {} \t{} \t{:.4}'.format(v,resNp[i,0],resNp[i,1],resNp[i,2]))


#SELECT mst.stid , mst.stname, mst.real_province ,mst.real_city ,mst.real_district ,mst.real_address , 
# mst.longitude , mst.latitude , minfo.user_id , minfo.platform , mit.create_time  
#FROM ods_wei_stations as mst, ods_wei_order_info  as minfo ,ods_wei_order_items as mit 
#WHERE  mst.stid = 10312  AND minfo.merchant_id = mst.stid AND mit.id = minfo.id 
#AND mit.create_time >= 1497888000 AND mit.create_time <= 1537200000 
#ORDER BY mit.create_time;

    #油站 时间 商品
    def mStTiPro(self,minit):
        mStiProReturn = 0
        if isinstance(minit['st'],int):
            sql_st=' mst.stid = '+ str(minit['st'])+' '
        elif isinstance(minit['st'],str):
            sql_st=' mst.stname = \''+ minit['st']+'\' '
        else:
            print(type(minit['st']))
            sys.exit()
        #print(sql_st)
        file_pp = sql_st+'_'+minit['s']+' '+minit['e']
        if not ( os.path.exists('csv_temp/mStTiPro_df_'+file_pp+'.csv') and \
                os.path.exists('csv_temp/mStTiPro_info_'+file_pp+'.csv') ) :
            
            temp_time_struct = time.strptime(minit['s'],'%Y-%m-%d %H-%M-%S')
            time_s = str(int(time.mktime(temp_time_struct)))
            temp_time_struct = time.strptime(minit['e'],'%Y-%m-%d %H-%M-%S')
            time_e = str(int(time.mktime(temp_time_struct)))
            msql = 'SELECT mst.stid , mst.stname, mst.real_province ,mst.real_city ,mst.real_district ,mst.real_address , \
                mst.longitude , mst.latitude , minfo.user_id , minfo.platform , minfo.create_time \
                FROM ods_wei_stations as mst, ods_wei_order_info  as minfo ,ods_wei_order_items as mit  \
                WHERE '+ sql_st +' AND minfo.merchant_id = mst.stid AND mit.id = minfo.id \
                AND minfo.create_time >= '+time_s+' AND minfo.create_time <= '+time_e+' \
                AND mit.goods_type = 10\
                ORDER BY mit.create_time;'
    #        print(msql)
            mSQL.cursor.execute(msql)
            res = mSQL.cursor.fetchall()
            print('共检索到 {} 条数据'.format(len(res)))
    #        print(res[1:5])
            alldf = pd.DataFrame(np.array(res),columns = ['stid','stname','province',
                              'city','district','address','longitude','latitude',
                              'user_id','platform','time'])
    #        print(alldf.head())
            msql_info = 'SELECT stid,stname,real_province as province,real_city as city , \
                    real_district as district,longitude,latitude FROM ods_wei_stations as mst WHERE ' + sql_st 
            mSQL.cursor.execute(msql_info)
            dealinfo =pd.DataFrame( np.array(mSQL.cursor.fetchall()),columns = ['stid',\
                                   'stname','province','city','district','longitude','latitude'])
            print(dealinfo)
            dealdf = alldf.loc[:,['time']]
            #print('{}条'.format(len(dealdf)))
            #print(dealdf.head())
            
            def fun_df_time(x):
                temp = time.localtime(int(x))
                Y = time.strftime('%Y',temp)
                m = time.strftime('%m',temp)
                d = time.strftime('%d',temp) 
                H = time.strftime('%H',temp)
                M = time.strftime('%M',temp) 
                S = time.strftime('%S',temp)
                
                w = time.strftime('%w',temp) #周几
                yweek = time.strftime('%U',temp)#一年中的第几周
                yday =  time.strftime('%j',temp)#一年中的第几天
                
    #            return [Y,m,d,H,M,S]
    #            return S
                return {'Y':Y,'m':m,'d':d,'H':H,'M':M,'S':S,'w':w,'yweek':yweek,'yday':yday}
            
            dealdf['Y'] = None
            dealdf['m'] = None
            dealdf['d'] = None
            dealdf['H'] = None
            dealdf['M'] = None
            dealdf['S'] = None
            
            dealdf['w'] = None
            dealdf['yweek'] = None
            dealdf['yday'] = None
            
    #        for index,row in dealdf.iterrows():
    #            dealdf.loc[[index],['Y','m','d','H','M','S']] = fun_df_time(row['time'])  
            for i in ['Y','m','d','H','M','S','w','yweek','yday']:
                dealdf[i] = dealdf.apply(lambda row:fun_df_time(row['time'])[i],axis = 1)
            #print(dealdf.head())
            
            def fun_file():
                if not os.path.exists('csv_temp'):
                    os.makedirs('csv_temp')
        
                if os.path.exists('csv_temp/mStTiPro_df_'+file_pp+'.csv'):
                    os.remove('csv_temp/mStTiPro_df_'+file_pp+'.csv')
                file1 = open('csv_temp/mStTiPro_df_'+file_pp+'.csv','w')
                file1.close()
                if os.path.exists('csv_temp/mStTiPro_info_'+file_pp+'.csv'):
                    os.remove('csv_temp/mStTiPro_info_'+file_pp+'.csv')
                file2 = open('csv_temp/mStTiPro_df_'+file_pp+'.csv','w')
                file2.close()
                
            fun_file()
            dealinfo.to_csv('csv_temp/mStTiPro_info_'+file_pp+'.csv',index = False , header = True)
            dealdf.to_csv('csv_temp/mStTiPro_df_'+file_pp+'.csv',index = False , header = True)
            mStiProReturn = mPlot.mStTiPro(dealinfo,dealdf)
        else:
            mStiProReturn = mPlot.mStTiPro(pd.read_csv('csv_temp/mStTiPro_info_'+file_pp+'.csv'),\
                           pd.read_csv('csv_temp/mStTiPro_df_'+file_pp+'.csv'))
        return mStiProReturn

    def mTi(self,minit):
        mTiReturn = 0
        file_pp = 'time- '+minit['s']+' '+minit['e']
        if not ( os.path.exists('csv_temp/mTi_df_'+file_pp+'.csv') ) :
            
            temp_time_struct = time.strptime(minit['s'],'%Y-%m-%d %H-%M-%S')
            time_s = str(int(time.mktime(temp_time_struct)))
            temp_time_struct = time.strptime(minit['e'],'%Y-%m-%d %H-%M-%S')
            time_e = str(int(time.mktime(temp_time_struct)))
            msql = 'SELECT minfo.merchant_id , \
                    ( SELECT mst.stid  FROM ods_wei_stations as mst WHERE minfo.merchant_id =  mst.stid ) as stid, \
                    ( SELECT mst.stname  FROM ods_wei_stations as mst WHERE minfo.merchant_id =  mst.stid ) as stname, \
                    ( SELECT mst.real_province  FROM ods_wei_stations as mst WHERE minfo.merchant_id =  mst.stid ) as province, \
                    ( SELECT mst.real_city  FROM ods_wei_stations as mst WHERE minfo.merchant_id =  mst.stid ) as city, \
                    ( SELECT mst.real_district  FROM ods_wei_stations as mst WHERE minfo.merchant_id =  mst.stid ) as district, \
                    ( SELECT mst.real_address  FROM ods_wei_stations as mst WHERE minfo.merchant_id =  mst.stid ) as address, \
                    ( SELECT mst.longitude  FROM ods_wei_stations as mst WHERE minfo.merchant_id =  mst.stid ) as longitude, \
                    ( SELECT mst.latitude  FROM ods_wei_stations as mst WHERE minfo.merchant_id =  mst.stid ) as latitude, \
                    COUNT(minfo.merchant_id) as count \
                    FROM ods_wei_order_info as minfo \
                    WHERE minfo.create_time >= '+time_s+' AND minfo.create_time <= '+time_e+'  \
                    AND merchant_id > 0 \
                    GROUP BY minfo.merchant_id ;'
            print(msql)
            mSQL.cursor.execute(msql)
            res = mSQL.cursor.fetchall()
            print('共检索到 {} 条数据'.format(len(res)))
    #        print(res[1:5])
            alldf = pd.DataFrame(np.array(res),columns = ['merchant_id','stid','stname','province',
                              'city','district','address','longitude','latitude','count'])
            print(alldf.head())
            def fun_file():
                if not os.path.exists('csv_temp'):
                    os.makedirs('csv_temp')
        
                if os.path.exists('csv_temp/mTi_df_'+file_pp+'.csv'):
                    os.remove('csv_temp/mTi_df_'+file_pp+'.csv')
                file1 = open('csv_temp/mTi_df_'+file_pp+'.csv','w')
                file1.close()
                
            fun_file()
#            alldf.drop(['del'],axis = 1)
            alldf.to_csv('csv_temp/mTi_df_'+file_pp+'.csv',index = False , header = True)
            mTiReturn = mPlot.mTi(alldf)
        else:
            mTiReturn = mPlot.mTi(pd.read_csv('csv_temp/mTi_df_'+file_pp+'.csv'))
        return mTiReturn
    
    def mAll(self,minit):
        mAllReturn = 0
        if isinstance(minit['st'],int):
            sql_st=' mst.stid = '+ str(minit['st'])+' '
        elif isinstance(minit['st'],str):
            sql_st=' mst.stname = \''+ minit['st']+'\' '
        else:
            print(type(minit['st']))
            sys.exit()
        #print(sql_st)
        file_pp =' '+sql_st+' '+minit['s']+' '+minit['e']
        if not ( os.path.exists('csv_temp/mAll'+file_pp+'.csv') and \
                os.path.exists('csv_temp/mAll'+file_pp+'.csv') ) :
            
            temp_time_struct = time.strptime(minit['s'],'%Y-%m-%d %H-%M-%S')
            time_s = str(int(time.mktime(temp_time_struct)))
            temp_time_struct = time.strptime(minit['e'],'%Y-%m-%d %H-%M-%S')
            time_e = str(int(time.mktime(temp_time_struct)))
            msql = 'SELECT mst.stid , mst.stname, mst.real_province as province, mst.real_city as city , \
                    mst.real_district as district ,mst.real_address as address , mst.longitude , mst.latitude , \
                    minfo.user_id , minfo.platform , minfo.create_time , \
                    mit.goods_name, mit.goods_number,mit.market_price,mit.actual_price , mit.subtotal \
                    FROM ods_wei_stations as mst, ods_wei_order_info  as minfo ,ods_wei_order_items as mit  \
                    WHERE '+ sql_st +' AND minfo.merchant_id = mst.stid AND mit.id = minfo.id \
                    AND minfo.create_time >= '+time_s+' AND minfo.create_time <= '+time_e+'  \
                    AND mit.goods_type = 10 AND minfo.user_id > 0 AND minfo.platform > 0 ;'
#            print(msql)
            mSQL.cursor.execute(msql)
            res = mSQL.cursor.fetchall()
            print('共检索到 {} 条数据'.format(len(res)))
    #        print(res[1:5])
            alldf = pd.DataFrame(np.array(res),columns = ['stid','stname','province',
                              'city','district','address','longitude','latitude',
                              'user_id','platform','create_time','goods_name',
                              'goods_number','market_price','actual_price','subtotal'])
    #        print(alldf.head())
            
            alldf['date'] = None ; alldf['num'] = None
            alldf['date'] = alldf.apply(lambda row:time.strftime(r'%Y/%m/%d', \
                 time.localtime(row['create_time'])),axis = 1)
            alldf['num'] = alldf.apply(lambda row:1 ,axis = 1)
#            alldf['date'] = pd.to_datetime(alldf['date'])
#            alldf = alldf.set_index('date')
            
            def fun_file():
                if not os.path.exists('csv_temp'):
                    os.makedirs('csv_temp')
        
                if os.path.exists('csv_temp/mAll'+file_pp+'.csv'):
                    os.remove('csv_temp/mAll'+file_pp+'.csv')
                file1 = open('csv_temp/mAll'+file_pp+'.csv','w')
                file1.close()
                
            fun_file()
            alldf.to_csv('csv_temp/mAll'+file_pp+'.csv',index = False , header = True)
#            mAllReturn = mPlot.mAll(alldf)
            mAllReturn = alldf
        else:
#            mAllReturn = mPlot.mAll(pd.read_csv('csv_temp/mAll'+file_pp+'.csv'))
            mAllReturn = pd.read_csv('csv_temp/mAll'+file_pp+'.csv')
        mAllReturn['date'] = pd.to_datetime(mAllReturn['date'])
        mAllReturn = mAllReturn.set_index('date')
        return mAllReturn
        
        
        
        
    

if __name__ == '__main__':
    m = mSQL();
#    m.mClassificate("goods_type");
    m.close();