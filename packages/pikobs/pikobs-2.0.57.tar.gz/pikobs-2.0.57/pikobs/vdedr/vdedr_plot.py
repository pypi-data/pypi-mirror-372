#!/usr/bin/python3
###############################################################################
#
#                              plots_profils.py 
#
# Purpose: Graphs of radiance statistics 
#
# Author: Sylvain Heilliette, Pierre Koclas and David Lobon  2020
#
# Modifications:
#     -2020  David Lobon 
#        - various updates
# Syntax:
#
#    plots_profils.py 
#  
#         
###############################################################################
import sys
import csv
import math
import matplotlib as mpl
mpl.use('Agg')
import pylab
import sqlite3
import numpy as np
ROUGE = '#FF9999'
ROUGEPUR = '#FF0000'
VERT = '#009900'
BLEU = '#1569C7'
NOIR = '#000000'
COULEURS = [BLEU, ROUGEPUR, ROUGE, VERT, NOIR]


def read_sqlite(file, id_stn):
    """
    Función para leer los datos desde una base de datos SQLite y obtener los resultados de las consultas.
    """
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    query = f"""
    SELECT 
        vcoord AS vcoord,
        SUM(Ntot * AvgOMP) / SUM(Ntot) AS AvgOMP_combined,
        SUM(Ntot * AvgOMA) / SUM(Ntot) AS AvgOMA_combined,
        SQRT(SUM(Ntot * (StdOMP * StdOMP + AvgOMP * AvgOMP)) / SUM(Ntot) - POW(SUM(Ntot * AvgOMP) / SUM(Ntot), 2)) AS CombinedStdOMP,
        SQRT(SUM(Ntot * (StdOMA * StdOMA + AvgOMA * AvgOMA)) / SUM(Ntot) - POW(SUM(Ntot * AvgOMA) / SUM(Ntot), 2)) AS CombinedStdOMA,
        SUM(Ntot) AS TotalNtot,
        SUM(Ntot * AvgBCOR) / SUM(Ntot) AS AvgBCOR_combined
    FROM 
        serie_vdedr
    WHERE 
        id_stn = '{id_stn}'
    GROUP BY 
        vcoord;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    vcoord = [result[0] for result in results]
    AvgOMP = [result[1] for result in results]
    AvgOMA = [result[2] for result in results]
    StdOMP = [result[3] for result in results]
    StdOMA = [result[4] for result in results]
    Ntot   = [result[5] for result in results]
    BiasCor= [result[6] for result in results]
    return vcoord, AvgOMP, AvgOMA, StdOMP, StdOMA, Ntot, BiasCor

def get_graphe_nomvar():
    """
    Función que devuelve el diccionario de las variables con su descripción.
    """
    return {
        '11215': 'U COMPONENT OF WIND (10M)',
        '11216': 'V COMPONENT OF WIND (10M)',
        '12004': 'DRY BULB TEMPERATURE AT 2M',
        '10051': 'PRESSURE REDUCED TO MEAN SEA LEVEL',
        '10004': 'PRESSURE', 
        '12203': 'DEW POINT DEPRESSION (2M)',
        '12001': 'TEMPERATURE/DRY BULB', 
        '11003': 'U COMPONENT OF WIND',
        '11004': 'V COMPONENT OF WIND',
        '12192': 'DEW POINT DEPRESSION',
        '12163': 'BRIGHTNESS TEMPERATURE',
        '15036': 'ATMOSPHERIC REFRACTIVITY',
        '11001': 'WIND DIRECTION',
        '11002': 'WIND SPEED',
        '11011': 'WIND DIRECTION AT 10M', 
        '11012': 'WIND SPEED AT 10M'
    }
import matplotlib.pyplot as plt

def vdedr_plot(pathwork,datestart, dateend, flag_type, family,region, files_in,names_in ,id_stn, varno,mode):
    
    vcoord_type =  'CANAL'# LARG[1]
    files = files_in
    famille = family
    region  = region
    varno = varno
    platf = id_stn
    label = names_in[0]
    debut = datestart
    fin = dateend
    mode = mode
    #print (" varno= ", varno) 
    GRAPHE_NOMVAR = get_graphe_nomvar()
    if varno  in GRAPHE_NOMVAR :
        Nom = GRAPHE_NOMVAR[varno]
    else:
        Nom = varno
    #files.append(LARG[11])
    label2 = names_in[1]
    
    PERIODE = 'From  ' + debut + '   to  ' + fin
    
    #
    #==============================================================================
    order = True
    if ( vcoord_type == 'PRESSION'):
        SIGN = -1
        vcoord_type_e = 'Pressure'
    elif ( vcoord_type == 'HAUTEUR'):
        SIGN = -1
        vcoord_type_e = 'Height'
    elif ( vcoord_type == 'CANAL'):
        SIGN = -1
        vcoord_type_e = 'Channel'
    else:
        SIGN= -1
        vcoord_type_e = vcoord_type
    
    
    #=================================
    #fig = pylab.figure(figsize=(8, 10))
    #=================================
    #ax = fig.add_subplot(1, 1, 1)
    #ax.grid(True)
    
    filenumb = 0
    TITRE = 'VERIFS'
   # lvl = []
   # numb = []
    
    lvl1, AvgOMP1, AvgOMA1, StdOMP1, StdOMA1, Ntot1, BiasCor1 = read_sqlite(files[0], id_stn)
    lvl2, AvgOMP2, AvgOMA2, StdOMP2, StdOMA2, Ntot2, BiasCor2 = read_sqlite(files[1], id_stn)
    for mode in ['bias',"delta_err","delta_err_oma"]: 
        fig = pylab.figure(figsize=(8, 10))
          #=================================
        ax = fig.add_subplot(1, 1, 1)
        ax.grid(True)
    

        lvl = []
        numb = []
          #lvl1, Bomp1, Somp1, Nomb1 = read_delta_err_oma_csv(files[0])
         # lvl2, Bomp2, Somp2, Nomb2 = read_delta_err_oma_csv(files[1])
        lset1 = set( lvl1 )
        lset2 = set( lvl2 )
        
        common_levels = lset1 & lset2
        
        lvlm = sorted(list(common_levels), reverse = order)
        if (mode=="bias"):
          delta_residual = [] 
          delta_raw = []
        if (mode=="delta_err"):
          delta_sigma = [] 
          delta_N = []
        if (mode=="delta_err_oma"):
          delta_sigma = [] 
          delta_N = []
        
        n1 = []
        n2 = []
        idlev = range(0,len(lvlm))
        
        for lev in lvlm:
            pos1 = lvl1.index(lev)
            pos2 = lvl2.index(lev)
            if (mode=="bias"):
              delta_residual.append( AvgOMP2[pos2] - AvgOMP1[pos1]  )
              delta_raw.append(  AvgOMP2[pos2] -  BiasCor2[pos2] - AvgOMP1[pos1] + BiasCor1[pos1])
            if (mode=="delta_err"):
              delta_sigma.append( 100.0 * ( StdOMP2[pos2] -  StdOMP1[pos1]) / StdOMP1[pos1] )
              delta_N.append( 100.0 * (Ntot2[pos2] - Ntot1[pos1]) / Ntot1[pos1] )
            if (mode=="delta_err_oma"):  
              delta_sigma.append( 100.0 * (StdOMA2[pos2] -  StdOMA1[pos1]) / StdOMA1[pos1] )
              delta_N.append( 100.0 * (Ntot2[pos2] - Ntot1[pos1]) / Ntot1[pos1] )
          
            n1.append(Ntot1[pos1])
            n2.append(Ntot2[pos2])
        #========================GRAPHIQUE==============================================
        if (mode=="bias"):
          ax.plot(delta_residual, idlev, linestyle = '-', marker = 'o', \
                    color = COULEURS[2], markersize = 4 )
          ax.plot(delta_raw, idlev, linestyle = '-', marker = 'p', \
                    color = COULEURS[3], markersize = 4 ) 
        if (mode=="delta_err"):
          ax.plot(delta_sigma, idlev, linestyle = '-', marker = 'o', \
                    color = COULEURS[2], markersize = 4 )
          ax.plot(delta_N, idlev, linestyle = '-', marker = 'p', \
                    color = COULEURS[3], markersize = 4 ) 
        if (mode=="delta_err_oma"):
          ax.plot(delta_sigma, idlev, linestyle = '-', marker = 'o', \
                    color = COULEURS[2], markersize = 4 )
          ax.plot(delta_N, idlev, linestyle = '-', marker = 'p', \
                    color = COULEURS[3], markersize = 4 ) 
        
        #===============================================================================
        
        #======TICK MARKS=ET LABEL===============================
        xlim = pylab.get(pylab.gca(), 'xlim')
        if varno  in GRAPHE_NOMVAR :
            Nom2 = GRAPHE_NOMVAR[varno]
        else:
            Nom2 = varno
        ylim = (min(idlev), max(idlev) )
            
        yticks = map(str, idlev)
        ax.set_yticks(idlev)
        
        yticks = map(str, lvlm)
        ax.set_yticklabels(yticks, fontsize = 6)
        
         
        pylab.setp(pylab.gca(), ylim = ylim[::SIGN])
                
        ax.set_ylabel(vcoord_type_e, color = NOIR, bbox = dict(facecolor=ROUGE), \
                          fontsize = 16)
        #========================================================
        
        #=NOMBRE DE NONNEES ==================================================
        datapt = []
        for y in  range(0, len(lvlm) ):
            datapt.append(( xlim[1], idlev[y] ) )
        display_to_ax = ax.transAxes.inverted().transform
        data_to_display = ax.transData.transform
        
        if ( len(datapt) > 0):
            ax_pts = display_to_ax(data_to_display(datapt))
            for y in  range(0, len(lvlm) ):
                ix, iy = ax_pts[y]
                pylab.text(ix + .01 , iy, int(n1[y]), fontsize = 6, \
                               color = COULEURS[0], transform = ax.transAxes )
                pylab.text(ix + .07 , iy,int(n2[y]), fontsize = 6, \
                               color = COULEURS[1], transform = ax.transAxes )
        #====================================================================
        #----------------------------------------------------------------------

        famille1 = famille + " " + platf
        REGION1 = region
        LABEL1 = label
        LABEL2 = label2
        if (mode=="bias"):
          legendlist = [' residual bias ', ' raw bias ']
          name = "omp_bias"
          typer='OMP'
        if (mode=="delta_err"):
          legendlist = ['% sigma ', '% Nobs ']
          name = "omp_rel"
          typer='OMP'

        if (mode=="delta_err_oma"):
          legendlist = ['% sigma ', '% Nobs ']
          name = "oma_rel"
          typer='OMA'

        l1 = pylab.legend(legendlist, columnspacing=1, fancybox=False, ncol=2, \
                              shadow = False, loc = (0.50, +1.00), prop = {'size':8}, frameon=False)
        ltext = pylab.gca().get_legend().get_texts()
     #   print(ltext)
        pylab.setp(ltext[0], fontsize = 10, color = 'k')
        #----------------------------------------------------------------------
        bbox_props = dict(facecolor = BLEU, boxstyle = 'round')
        pylab.text(-.03, -0.05, f"{famille1}  {Nom} {typer} ", \
                         fontsize = 10, bbox = bbox_props, transform = ax.transAxes)
        pylab.text(.00, 1.05, REGION1, fontsize = 10, \
                        bbox = dict(facecolor = BLEU, boxstyle = 'round'), \
                        transform = ax.transAxes)
        pylab.text(.25, 1.05, PERIODE, fontsize = 10, \
                        bbox = dict(facecolor = BLEU, boxstyle = 'round'), \
                        transform = ax.transAxes)
        pylab.text(.70, 1.05, LABEL2 + ' - ' + LABEL1, fontsize = 10, \
                        bbox = dict(facecolor = BLEU, boxstyle = 'round'), \
                        transform = ax.transAxes)
        
        #==========================================================
        #pylab.show()
        pylab.savefig(f'{pathwork}/{family}/{name}_{family}_{id_stn}_{names_in[0]}-{names_in[1]}_{region}.png', format = 'png', dpi = 100)
        pylab.close()
