# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from glob import glob
import gsw
import seawater as sw
import os
from collections import OrderedDict


#################################
########## Ler OC2 ##############
#################################

#################################
##### Numero de skip rows #######
##### para cada ficheiro  #######
#################################

# Vê para cada estação quantas linhas precisa dar skip
def skip_rows(stat):
    skip_r=np.array([])
    f = open(stat)
    cont=1
    while True:
        linha=f.readline()
        if linha.split()[0] == '*END*':
            skip_r=np.append(skip_r,cont)
            break
        else:
            cont+=1
    return skip_r

def bad_flag(stat):
    bf=np.array([])
    f = open(stat)
    while True:
        linha=f.readline()
        if 'bad_flag' in linha:
            flag=float(linha.split('=')[-1])
            bf=np.append(bf,flag)
        elif '*END*' in linha:
            break
    return bf
#lê as posições lon e lat da estação
def get_lonlat(stat,sep=','):
    lon,lat=np.array([]),np.array([])
    f=open(stat)
    while True:
        d=f.readline()
        if sep == '.':
            if d.split()[0]=='**':
                if d.split()[-1]=='S':
                    deg = float(d.split()[1])
                    seg=int(np.round((float(d.split()[2])/60)*10000))/10000. 
                    latv = (deg+seg)*(-1.)
                    lat=np.append(lat,latv)
                    d=f.readline()
                if d.split()[-1]=='W':
                    deg = float(d.split()[1])
                    seg=int(np.round((float(d.split()[2])/60)*10000))/10000.
                    lonv = (deg+seg)*(-1.)
                    lon=np.append(lon,lonv)
                    break
        if sep == ',':
            if d.split()[0]=='**':
                if d.split()[-1]=='S':
                    deg = float(d.split()[2])
                    prim=d.split()[3].split(',')[0]+'.'+d.split()[3].split(',')[1]
                    seg=int(np.round((float(prim)/60)*10000))/10000.
                    latv = (deg+seg)*(-1.)
                    lat=np.append(lat,latv)
                    d=f.readline()
                if d.split()[-1]=='W':
                    deg = float(d.split()[2])
                    prim=d.split()[3].split(',')[0]+'.'+d.split()[3].split(',')[1]
                    seg=int(np.round((float(prim)/60)*10000))/10000.
                    lonv = (deg+seg)*(-1.)
                    lon=np.append(lon,lonv)
                    break
    return lon,lat   

# lê a lista de todas as propriedades presentes no dado
def propertie(stat):
    prop = np.array([])
    unit = np.array([])
    f=open(stat)
    while True:
        d=f.readline()
        if '# name' in d:
            propv = d.split(':')[0].split('=')[-1]+' - '+d.split(':')[1].split()[0].split(',')[0]
            prop = np.append(prop,propv)
            unitv = d.split(':')[1].split('\r')[:-1]
            unit=np.append(unit,unitv)
        elif d.split()[0] == '*END*':
            break   
    return prop,unit

#regista quais propriedades de todas as disponíveis serão usadas
def get_props(stat):
    prop,unit=propertie(stat)
    print 'As propriedades registadas pelo sensor foram:'
    print ' ' 
    print prop
    print ' '
    print ' '
    print 'As unidades dessas propriedades foram:'
    print ' ' 
    print unit
    input = raw_input("Propriedades a tratar(0 a %i): "%(prop.size))
    input_list = input.split(',')
    cols = np.array([int(x.strip()) for x in input_list])
    prop2=prop[cols]
    props=[]
    for i in prop2:
        if 'flag' in i:
            props.append('flag')
        else:
            props.append(i.split(' ')[1])
    return props,cols
    
# lê o csv de estação uma a uma gravando nesta as propriedades 
#previamente escolhidas e a longitude e latitude de cada estação
def read_stat(stat,props,cols,sep=','):
    sk=skip_rows(stat)
    lon,lat=get_lonlat(stat,sep=sep)
    bf=bad_flag(stat)
    st = pd.read_csv(stat,usecols=cols,names=props,delim_whitespace=True,skiprows=int(sk))
    lon,lat,bf=np.zeros(st.shape[0])+lon[0],np.zeros(st.shape[0])+lat[0],np.zeros(st.shape[0])+bf[0]
    st['Lon']=pd.Series(lon)
    st['Lat']=pd.Series(lat)
    st['BadFlag']=pd.Series(bf)
    return st

#divide a estação em up e down e grava esses dados num arquivo 
def split(stat,path_save,props,cols,sep=','):
    if stat.split('/')[-2]=='OS3':
        name = 'OS3-'+stat.split('I')[-1].split('.')[0]
    else:
        name = stat.split('/')[-1].split('.')[0]
    st=read_stat(stat,props,cols,sep=sep)
    cut=np.argwhere(st[st.keys()[0]]==np.max(st[st.keys()[0]].values))[0]
    down_args=np.arange(0,cut+1)
    up_args=np.arange(cut+1,st.shape[0])
    down_dat = st.iloc[down_args,:]
    up_dat = st.iloc[up_args,:]
    up_dat.to_pickle(path_save+name+'_up')
    down_dat.to_pickle(path_save+name+'_down')


# divide todas as estações de uma comissão em up e down
def cut_stats(path_dados,path_save):
    lista=glob(path_dado_bruto+'*.cnv')
    lista.sort()
    os.system('mkdir %s'%path_save)
    props,cols = get_props(lista[0])
    sep2 = raw_input('O separador de lat e lon qual é (. ou ,)?  ')
    for stat in lista:
        split(stat,path_save,props,cols,sep=sep2)
        print stat.split('/')[-1].split('.')[0]+' cuted!'
    pd.to_pickle(props,path_save+'props')

        
################################################################        
########################## PROCESSAMENTO #######################        
################################################################

def rmv_flag(stat):
    bf = stat.BadFlag[0]
    stat = stat[stat.flag != stat.BadFlag[0]]
    return stat

def loop_ed(stat2,up=True):
    stat = stat2.copy()
    print 'LOOP EDIT'
    while True:
        difs=np.append(np.array([0]),np.diff(stat[stat.keys()[0]]))
        mask=difs>=0   
        if up:
            difs=np.append(np.array([0]),np.diff(stat[stat.keys()[0]]))
            mask=difs<=0
        if np.all(mask):
            break
        stat = stat.iloc[mask,:]
    return stat
                
def despike(self,propname,block):
    '''
    This function apply Hanning Window filter to some item
    named 'propname'
    '''

    def spike(x):
        return 3*np.std(x)
    stds = pd.rolling_apply(self[propname].values,block,spike,center=True)
    #Fill the head and tail of values that does not got the filter
    mask1=~(stds>self[propname])
    self = self[mask1]
    return self

def binaige(self,step):
    bins=np.arange(0.5,self.shape[0]+1,step)
    groups = np.digitize(self[self.keys()[0]].values,bins)
    self = self.groupby(by=groups,axis=0).mean()
    self=self.drop(self.keys()[0],axis=1) 
    return self

    bins=np.arange(0.5,d.shape[0]+1,step)
    groups = np.digitize(d[d.keys()[0]].values,bins)
    d = d.groupby(by=groups,axis=0).mean()
    d=d.drop(d.keys()[0],axis=1) 
    return self


def window(self,block,props):
    '''
    props must be a list of properties
    '''
    for i in props:
        vals = pd.rolling_window(self[i].values,window=block,win_type='boxcar',center=True)
        cond = np.argwhere(np.isnan(vals))
        vals[cond] = self[i].values[cond]
        self[i] = vals    
    return self



#####################################
########  FAZER CÁLCULOS!!!! ########
#####################################

def calcs(self,S,T,P):
    self['gpan']=sw.gpan(S,T,P)
    self['pt']=sw.ptmp(S,T,P) 
    self['psigma0']=sw.pden(S,T,P,0)-1000
    self['psigma1']=sw.pden(S,T,P,1000)-1000
    self['psigma2']=sw.pden(S,T,P,2000)-1000
    
    return self
    
    
def proc(path1,path_save,sent):
    '''
    path1 -> ler os arquivos a processar
    path_save -> salvar arquivos processados
    sent -> indicar se lê arquivos de subida ou descida
    '''
    total = OrderedDict()
    props = pd.read_pickle(path1+'props')
    lista=glob(path1+'*_'+sent)
    lista.sort()
    block = float(raw_input('Qual o número de blocos para despike?  '))
    print props
    print ' '
    propname=raw_input('Que propriedades são analisadas no despike?  ')
    propname = propname.split(',')
    prop_wind = propname
    print ' '
    step = float(raw_input('Qual o step (m) da binagem?  '))
    #print ' '
    #prop_wind = raw_input('Que propriedades são analisadas na janela móvel? (Props ou none)')
    #prop_wind = prop_wind.split(',')
    if prop_wind[0] != 'none':
        print ' '
        block2 = int(raw_input('Qual o número de blocos para janela móvel?  '))
    print props
    print ' ' 
    print ' '
    ts = raw_input('Quais as prop T-S ?  ')
    T,S=ts.split(',')[0],ts.split(',')[1]
    os.system('mkdir %s'%path_save_proc)
    for stat in lista:     
        d = pd.read_pickle(stat)
        d = rmv_flag(d)
        if sent == 'up':
            d = loop_ed(d,up=True)
        elif sent == 'down':
            d=loop_ed(d,up=False)
        else:
            raise ValueError('Sentido de mov do ctd errado')
        for prop in propname:
            d = despike(d,prop,block)
        d=binaige(d,step)
        if d.index.values[0] != 0:
            tst = d.copy().T
            for i in np.arange(0,d.index.values[0]):
                tst.insert(i,i,np.ones(d.shape[1])*np.NaN)
            d = tst.T
            d=d.fillna(method='backfill')    
        Temp = d[T].values
        P = d.index.values
        if 'c' in S:
            if d[S].values[0]/10<1:
                sal=d[S].values*10
                d['sp'] = gsw.SP_from_C(sal,Temp,P)
            Sal = d['sp'].values  
        else:
            Sal = d[S].values
        if prop_wind[0]=='none':
            
            d_final = calcs(d,Sal,Temp,P)
            d_final.to_pickle(path_save+stat.split('/')[-1].split('.')[0].split('_')[0]+'_'+sent[0].upper()+'_proc')
            total['Stat '+stat.split('-')[-1].split('_')[0]] = d_final
            print 'Stations %s processed'%(stat.split('/')[-1].split('.')[0])

        else:
            for prop in prop_wind:
                d=window(d,block2,prop_wind)
            d_final = calcs(d,Sal,Temp,P)
            d_final.to_pickle(path_save+stat.split('/')[-1].split('.')[0].split('_')[0]+'_'+sent[0].upper()+'_proc')
            total['Stat '+stat.split('-')[-1].split('_')[0]] = d_final
            print 'Stations %s processed'%(stat.split('/')[-1].split('.')[0])
    tudo = pd.Panel.fromDict(total)
    tudo.to_pickle(path_save+stat.split('/')[-3]+'_alldata')

    

####################################################

for i in ['OS4/']:
    print 'PROCESSANDO %s'%(i.split('/')[0])
    print ' '
    print ' '
    print ' '
    
    path_dado_bruto= '/home/helio/Projeto/Dados/OC/Oceano_Sul_4/Dados_CTD/CTD_bruto/data_cnv/'
    path_save_cut = '/'.join(path_dado_bruto.split('/')[:-3])+'cut/'
    path_save_proc = '/'.join(path_dado_bruto.split('/')[:-3])+'proc/'
    
    #CORTA em up-down
    cut_stats(path_dado_bruto,path_save_cut)
    #processa down
    proc(path_save_cut,path_save_proc,'down')
    
    print ' '
    print ' '
    print 'FINALLY!!!!'
    print ' '
    print ' '
    print ' '