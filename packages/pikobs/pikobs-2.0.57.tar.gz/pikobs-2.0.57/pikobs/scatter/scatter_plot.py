#!/usr/bin/env python3

#Auteur : Pierre Koclas, May 2021
import os
import sys
import csv
from math import floor,ceil,sqrt
import matplotlib as mpl
mpl.use('Agg')
#import pylab as plt
import matplotlib.pylab as plt
import numpy as np
import matplotlib.colorbar as cbar
import matplotlib.cm as cm
import datetime
import cartopy.crs as ccrs
import cartopy.feature
#from cartopy.mpl.ticker    import LongitudeFormatter,  LatitudeFormatter
import matplotlib.colors as colors
#import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import sqlite3
from matplotlib.collections import PatchCollection
from statistics import median
import pikobs
import optparse
from mpl_toolkits.axes_grid1 import make_axes_locatable
def projectPpoly(PROJ,lat,lon,deltax,deltay,pc):
        X1,Y1  = PROJ.transform_point(lon - deltax,lat-deltay,pc )
        X2,Y2  = PROJ.transform_point(lon - deltax,lat+deltay,pc )
        X3,Y3  = PROJ.transform_point(lon + deltax,lat+deltay,pc )
        X4, Y4 = PROJ.transform_point(lon + deltax,lat-deltay,pc )
        Pt1=[ X1,Y1 ]
        Pt2=[ X2,Y2 ]
        Pt3=[ X3,Y3 ]
        Pt4=[ X4,Y4 ]
        Points4 = [ Pt1, Pt2,Pt3,Pt4 ]
           
        return Points4
def SURFLL(lat1,lat2,lon1,lon2):
#= (pi/180)R^2 |sin(lat1)-sin(lat2)| |lon1-lon2|
    R=6371.
    lat2=min(lat2,90.)
    surf=R*R*(np.pi/180.)*abs ( np.sin(lat2*np.pi/180.) - np.sin(lat1*np.pi/180.) ) *abs( lon2-lon1 )
   # if ( surf == 0.):
    # print (   ' surf=',lat1,lat2,lat2*np.pi/180.,lat1*np.pi/180.,np.sin(lat2*np.pi/180.) ,  np.sin(lat1*np.pi/180.) )
    return surf

def NPSURFLL(lat1, lat2, lon1, lon2):
    R = 6371.
    lat2 = np.minimum(lat2, 90.)
    surf = R**2 * (np.pi/180) * np.abs(np.sin(lat2*np.pi/180) - np.sin(lat1*np.pi/180)) * np.abs(lon2 - lon1)
  #  if np.any(surf == 0.):
    #    print('surf contiene valores cero')
    return surf
def SURFLL2(lat1, lat2, lon1, lon2):
    R = 6371.0
    lat2 = np.minimum(lat2, 90.0)
    surf = R * R * (np.pi / 180.0) * np.abs(np.sin(lat2 * np.pi / 180.0) - np.sin(lat1 * np.pi / 180.0)) * np.abs(lon2 - lon1)
    # Debugging print statements if surface is zero
    zero_surf_indices = (surf == 0.0)
 #   if np.any(zero_surf_indices):
 #       print('surf=', lat1[zero_surf_indices], lat2[zero_surf_indices], lat2[zero_surf_indices] * np.pi / 180.0,
 #             lat1[zero_surf_indices] * np.pi / 180.0,
 #             np.sin(lat2[zero_surf_indices] * np.pi / 180.0),
 #             np.sin(lat1[zero_surf_indices] * np.pi / 180.0))
    return surf
def days_between(d1, d2):
    d1 = datetime.datetime.strptime(d1, "%Y%m%d%H")
    d2 = datetime.datetime.strptime(d2, "%Y%m%d%H")
    delta = d2 - d1 

    return delta.total_seconds() / (24 * 3600)



import pikobs
import math

def round_first_digit_3(x):
    # Si es cero, lo devolvemos tal cual
    if x == 0:
        return "0"

    abs_x = abs(x)

    # Regla 1: >= 1 → 1 decimal  
    if abs_x >= 10:
        return f"{int(x)}"

    # Regla 2: >= 0.1 → 2 decimales
    elif abs_x >= 0.1:
        return f"{round(x, 2)}"

    # Regla 3: >= 0.01 → 3 decimales

    # Regla 4: >= 0.001 → 4 decimales
  #  elif abs_x >= 0.001:
   #     return f"{round(x, 3)}"

    # Regla 5: < 0.001 → formato científico
    else:
        mantissa, exp = f"{x:.1e}".split("e")
        mantissa = mantissa.split(".")[0]  # solo parte entera
        return f"{mantissa}.e{int(exp)}"

import numpy as np
def scatter_plot(
                   mode,
                   region,
                   family, 
                   id_stn, 
                   datestart,
                   dateend, 
                   Points,
                   boxsizex,
                   boxsizey, 
                   proj, 
                   pathwork, 
                   flag_criteria, 
                   fonction,
                   vcoord,
                   filesin,
                   namesin,
                   varno,
                   intervales):

       selected_flags = pikobs.flag_criteria(flag_criteria)


   
       pointsize=0.5
       delta=float(boxsizex)/2.
       deltay=float(boxsizey)/2.
       deltax=float(boxsizex)/2.
   
   #=============================================================
   #============      LECTURE   ================================
  # if isinstance(varnos, int):
  #  varnos = [varnos]
  # for fonction  in  fonctions:
  #  for Proj in proj:
       interval_a = intervales[0]
       interval_b = intervales[1]
       if  interval_a==None and  interval_b==None:
          criteria_interval = ''
          layers='layer_all'
       else:
          criteria_interval = f' and  {interval_a*100} <= vcoord <= {interval_b*100}'
          layers=f'Layer: {interval_a} hPa - {interval_b} hPa'


       conn = sqlite3.connect(":memory:")
       cursor = conn.cursor()
       cursor.execute("PRAGMA TEMP_STORE=memory")
       query = f"ATTACH DATABASE '{filesin[0]}' AS db1"  
       cursor.execute(query)

       FNAM, FNAMP, SUM, SUM2 = pikobs.type_boxes(fonction)
       if id_stn =='join' and vcoord=='join' :
          crite ="  "
       if id_stn =='join' and vcoord!='join' :
          crite = f" and  vcoord = {vcoord} "

       if id_stn !='join' and vcoord=='join' :
          crite = f"and  id_stn= '{id_stn}'    "
       
       if id_stn !='join' and vcoord!='join':
          crite = f"  and  vcoord = {vcoord} and id_stn= '{id_stn}'  "



       if len(filesin)>1:
             create_table='boites1'
             info_name = f"{namesin[0]} VS {namesin[1]}"
       else:
             create_table='AVG'
             info_name = f"namesin[0]"
        
       query = f"""CREATE TEMPORARY TABLE {create_table} AS
                   SELECT boite, 
                          lat,
                          lon, 
                          varno, 
                          vcoord,
                          SUM({SUM})/SUM(CAST(N AS FLOAT)) AVG,
                          SQRT(SUM({SUM2})/SUM(CAST(N AS FLOAT)) - SUM({SUM})/SUM(CAST(N AS FLOAT))*SUM({SUM})/SUM(CAST(N AS FLOAT))) STD,
                          SUM(sumstat)/SUM(CAST(N AS FLOAT)) BCORR,
                          SUM(n) N
                   FROM db1.moyenne
                   where varno={varno}

                   {crite} 

                   GROUP BY boite, lat, lon, varno having sum(n)>3;"""
       cursor.execute(query)

       if len(filesin)>1:
           query = f"ATTACH DATABASE '{filesin[1]}' AS db2"
           cursor.execute(query)
           query = f"""CREATE TEMPORARY TABLE boites2 AS
                       SELECT boite, lat, lon, varno, vcoord,
                              SUM({SUM})/SUM(CAST(N AS FLOAT)) AVG,

                              SQRT(SUM({SUM2})/SUM(CAST(N AS FLOAT)) - SUM({SUM})/SUM(CAST(N AS FLOAT))*SUM({SUM})/SUM(CAST(N AS FLOAT))) STD,
                              SUM(sumstat)/SUM(CAST(N AS FLOAT)) BCORR,
                              SUM(n) N
                       FROM db2.moyenne
                       where  varno={varno}

                       {crite} 
                     
                       GROUP BY boite, lat, lon, varno having sum(n)>3;"""  

           cursor.execute(query)

           query = f"""Create temporary table AVG as 
                       SELECT BOITES1.boite BOITE,
                              BOITES1.lat LAT,
                              BOITES1.lon LON,
                              BOITES1.vcoord VCOORD,
                              BOITES1.varno VARNO,
                              ABS(BOITES1.avg) - ABS(BOITES2.avg) AVG, --BOITES1.avg - BOITES2.avg AVG,
                              COALESCE(ABS(BOITES1.avg),8888) AVG1,
                              COALESCE(ABS(BOITES2.avg),8888) AVG2,
                              ABS(BOITES1.std) - ABS(BOITES2.std) STD, --  BOITES1.std - BOITES2.std STD, 
                              COALESCE(ABS(BOITES1.std),8888) as  std1,
                              COALESCE(ABS(BOITES2.std),8888) as std2,
                              ABS(BOITES1.bcorr) - ABS(BOITES2.bcorr) BCORR ,  --BOITES1.bcorr - BOITES2.bcorr BCORR , 
                              COALESCE(ABS(BOITES1.bcorr),8888) AS bcorr1,
                              COALESCE(ABS(BOITES2.bcorr),8888) AS bcorr2,
                              BOITES1.N - BOITES2.N  N , --BOITES1.N - BOITES2.N  N, 
                              COALESCE(BOITES1.N, 8888) AS N1,
                              COALESCE(BOITES2.N, 8888) AS N2
                      FROM BOITES1,BOITES2 
                      WHERE  BOITES1.boite=BOITES2.boite and BOITES1.VCOORD=BOITES2.VCOORD; 
                      """ 

           cursor.execute(query)
       
       query = f"""
        SELECT lat, lon, avg, std, N
        FROM AVG;
       """
       if len(filesin) > 1:
          query = f"""
        SELECT lat, lon, avg, std, N, N1, N2, avg1, avg2, std1, std2, bcorr, bcorr1, bcorr2
        FROM AVG;
       """

       cursor.execute(query)
      
       cursor.execute(query)
       results = cursor.fetchall()    
       # Convertir a arrays numpy
       import numpy as np
       lat = np.array([row[0] for row in results])
       lon = np.array([row[1] for row in results])
       Bomp = np.array([row[2] for row in results])
       Somp = np.array([row[3] for row in results])
       nombre = np.array([row[4] for row in results])
       
       if len(filesin) > 1:

          N1 = np.array([row[5] for row in results])
          N2 = np.array([row[6] for row in results])
          avg1 = np.array([row[7] for row in results])
          avg2 = np.array([row[8] for row in results])
          std1 = np.array([row[9] for row in results])
          std2 = np.array([row[10] for row in results])
          bcorr = np.array([row[11] for row in results])
          bcorr1 = np.array([row[12] for row in results])
          bcorr2 =  np.array([row[13] for row in results])
          con = sqlite3.connect('tu_base_de_datos.db')
          
        
          sql = """
        SELECT b1.boite, b1.lat, b1.lon
        FROM boites1 b1
        LEFT JOIN boites2 b2 ON b1.boite = b2.boite
        WHERE b2.boite IS NULL
        
        UNION
        
        SELECT b2.boite, b2.lat, b2.lon
        FROM boites2 b2
        LEFT JOIN boites1 b1 ON b2.boite = b1.boite
        WHERE b1.boite IS NULL
        """
          cursor.execute(sql)
          resultados = cursor.fetchall()
        
       dens = nombre/NPSURFLL(lat-deltay,lat+deltay,lon-deltax,lon + deltax)


       index_none=np.where(Somp ==None)
       lat = np.delete(lat, index_none) 
       lon = np.delete(lon, index_none)
       Bomp = np.delete(Bomp, index_none)
       Somp = np.delete(Somp, index_none)

       nombre = np.delete(nombre, index_none)

       query = f"""select  
         
         '{datestart}',
                  '{dateend}',
                  '{family}',
                  '{varno}' , 
                   avg(avg)  , 
                   avg(std) ,
                   sum(N) 
                   From  
                   AVG    ;"""
       
       cursor.execute(query)
       results = cursor.fetchall()   
       debut  = np.array([row[0] for row in results])
       fin    = np.array([row[1] for row in results])
       familys = np.array([row[2] for row in results])
       Mu     = np.array([row[4] for row in results])
       Sigma  = np.array([row[5] for row in results])
       Nobs   = np.array([row[6] for row in results])

       conn.close()
       typer=''
       
       import numpy as np
       import matplotlib.pyplot as plt
       from matplotlib import cm, colors
       from matplotlib.ticker import FuncFormatter
       from mpl_toolkits.axes_grid1 import make_axes_locatable
       import cartopy
       
       if Sigma is not None:
           Sigma = np.round(Sigma, 3)
       
           vartyp = fonction
           PERIODE = f'From {datestart} To {dateend}'
           NDAYS = max(1/4, days_between(datestart, dateend))
           variable_name, units, vcoord_type = pikobs.type_varno(varno)
       
           if vcoord == 'join':
               Nomvar = f"{variable_name} {units} \n id_stn:{id_stn} vcoord/channel:{(vcoord)} {layers}"
           else:
               Nomvar = f"{variable_name} {units} \n id_stn:{id_stn} vcoord/channel:{int(vcoord)} {layers} "
       
           mode = 'MOYENNE'
           OMP = Somp if mode == 'SIGMA' else Bomp
           OMP = np.nan_to_num(OMP, nan=np.nan)
       
           plt.close('all')
           fig = plt.figure(figsize=(10, 10))
           plt.rcParams['axes.linewidth'] = 1
           fontsize = 17
       
           OMPm = [value for value in OMP if isinstance(value, float)]
           vmin = np.nanmin(OMPm)
           vmax = np.nanmax(OMPm)
           Ninterv = 10
       
           if vartyp == 'dens' or vartyp == 'dens%' :
               OMP = dens / NDAYS 
               if len(filesin) > 1:
                  den1 = N1/NPSURFLL(lat-deltay,lat+deltay,lon-deltax,lon + deltax) 
                  den2 = N2/NPSURFLL(lat-deltay,lat+deltay,lon-deltax,lon + deltax) 
                  OMP = (den2-den1)*100/den1  

                  vmin = -100
                  vmax =  100
               else:
                  
             
                     vmin = np.min(OMP)
                     vmax = np.max(OMP)
               cmap_base = cm.get_cmap('PuRd', lut=Ninterv)
               if vmin < 0:
                   max_abs = max(abs(vmin), abs(vmax))
                   vmin, vmax = -max_abs, max_abs
           elif vartyp in ['nobs', 'NOBSHDR']:
               Ninterv = 10
               OMP = nombre / NDAYS
               if len(filesin) > 1:
                   N1=N1 / NDAYS
#
                   N2=N2/ NDAYS

                   OMP =(N2-N1)*100/N1
                   vmin = -100
                   vma = 100
               else:
                  vmin = np.min(OMP)
                  vmax = np.max(OMP)

               max_abs = max(abs(vmin), abs(vmax))
               if vmin > 0.0:
                   Ninterv = 11
                   cmap_base = cm.get_cmap('PuRd', lut=Ninterv)
                   vmin, vmax = vmin + 1, vmax
               else:
                   cmap_base = cm.get_cmap('RdYlBu_r', lut=Ninterv)
                   vmin, vmax = -max_abs, max_abs
           elif vartyp == 'obs':
               if len(filesin) > 1:
                   OMP =(abs(avg2)-abs(avg1))*100/abs(avg1)
                   vmin = -100
                   vmax= 100

               else:
                  vmin = np.min(OMP)
                  vmax = np.max(OMP)
                  cmap_base = cm.get_cmap('RdYlBu_r', lut=Ninterv)  
           elif vartyp == 'bcorr':
               if len(filesin) > 1:
                   OMP =(abs(bcorr2)-abs(bcorr1))*100/abs(bcorr1)
                   vmin = -100
                   vmax= 100

               else:
                  vmin = np.min(OMP)
                  vmax = np.max(OMP)
                  cmap_base = cm.get_cmap('RdYlBu_r', lut=Ninterv)

           elif vartyp in ['omp', 'oma', 'bcorr', 'stdomp', 'stdoma']:
               
               vmin = np.min(OMP)
               vmax = np.max(OMP)
               #b30000
               vmax = np.max(np.abs(OMP))
               vmin = - vmax

               if len(filesin) > 1:
                   
                   OMP =(abs(avg2)-abs(avg1))*100/abs(avg1)
                   vmin = -100
                   vmax = 100


               N = 10
               if vartyp == 'stdomp':
                   mode = 'SIGMA'
                   typer = 'STD'
               cmap_base = cm.get_cmap('seismic', lut=N)
               if mode == 'MOYENNE':
                   typer = 'AVG'
               if mode == 'SIGMA':
                   cmap_base = cm.get_cmap('RdYlBu_r', lut=Ninterv)
           else:
               cmap_base = cm.get_cmap('RdYlBu_r', lut=Ninterv)
       
           if len(filesin) > 1:
            #    N = 21  
            #    boundaries = np.linspace(vmin, vmax, N)
            #    y = (boundaries[:-1] + boundaries[1:]) / 2
            #    neg_colors = [cm.RdYlBu_r(x) for x in np.linspace(0.08, 0.40, N//2)]
            #    blanco = (1, 1, 1, 1) 
            #    blanco = (1.0, 1.0, 0.6, 1.0) 
            #    pos_colors = [cm.RdYlBu_r(x) for x in np.linspace(0.60, 0.92, N//2)]
            #    over_color = '#e600c7'   
            #    under_color = '#0235ad' 
            #    colores =  neg_colors + [blanco] + pos_colors  

            #    cmap = colors.ListedColormap(colores)
            #    cmap.set_under('#0235ad')
            #    cmap.set_over('#e600c7')
            #    norm = colors.BoundaryNorm(boundaries, N)
             #   extend_color = 'both'
         #       ticks = boundaries
         #     boundaries = [-30, -20, -10, -2, 2, 10, 20, 30]
              
              # Colores
             extend_color = 'both'

             boundaries = np.array(
                 list(range(vmin, -5, 20)) +   # valores negativos hasta -2
                 [-5, 5] +                      # rango blanco [-2,2]
                 list(range(20, vmax+10, 20))   # valores positivos desde 10
             )
             y = boundaries


             # Colores negativos
             neg_colors = [cm.RdYlBu_r(x) for x in np.linspace(0.08, 0.40, len(boundaries[boundaries < -2]))]
             
             # Color blanco para [-2,2]
             blanco = (1.0, 1.0, 1.0, 1.0)
             
             # Colores positivos
             pos_colors = [cm.RdYlBu_r(x) for x in np.linspace(0.60, 0.92, len(boundaries[boundaries > 2]))]
             
             # Concatenar colores
             colores = neg_colors + [blanco] + pos_colors
             
             # Crear cmap y norm
             cmap = colors.ListedColormap(colores)
             cmap.set_under('#0235ad')
             cmap.set_over('#b30000')
             norm = colors.BoundaryNorm(boundaries, cmap.N)
             
             # Ticks para el colorbar
             ticks = list(boundaries[boundaries < -5]) + [-5, 5] + list(boundaries[boundaries > 5])

#              Colors = [
#                  "#053061",
#                  "#4393c3",  # -30 a -20
#                  "#92c5de",  # -20 a -10
#                  "#d1e5f0",  # -10 a -2
#                  "#f7f7f7",  # -2 a  2
#                  "#fddbc7",  #  2 a 10
#                  "#f4a582",  # 10 a 20
#                  "#d6604d",  # 20 a 30
#                  '#67001f',
#              ]
#
#              boundaries =  [-20, -15, -10, -2, 2, 10, 15, 20]            
#
#              # Colores (8 intervalos + 2 extremos)
#              Colors = [
#    "#4393c3",  # -30 a -20
#    "#92c5de",  # -20 a -10
#    "#d1e5f0",  # -10 a -2
#    "#f7f7f7",  # -2 a  2
#    "#fddbc7",  #  2 a 10
#    "#f4a582",  # 10 a 20
#    "#d6604d",  # 20 a 30
#] 
#              cmap = colors.ListedColormap( Colors)
#              #cmap.set_under("#67001f")  # < -30
#              #cmap.set_over("#053061")
#              norm = colors.BoundaryNorm(boundaries, cmap.N)  
#              cmap.set_over("#b2182b")  # < -30
#              cmap.set_under("#2166ac")
##b2182b#b2182b
#           #   norm = colors.BoundaryNorm([-1e9] + boundaries + [1e9], cmap.N)
#              # Definimos los ticks en los cortes internos
#              ticks = [-20, -15, -10, -2, 2, 10, 15, 20]              
           else:
               boundaries = np.linspace(vmin, vmax, Ninterv + 1)
               y = boundaries[:-1] + (boundaries[1] - boundaries[0]) / 2
               cmap = cmap_base
               norm = cm.colors.Normalize(vmin=vmin, vmax=vmax)
               extend_color = None
               ticks = boundaries
               #Colors = [m.to_rgba(x) for x in y]

           m = cm.ScalarMappable(norm=norm, cmap=cmap)
           Colors = [m.to_rgba(x) for x in y]
           inds = np.digitize(OMP, boundaries) - 1
           inds = np.clip(inds, 0, len(Colors) - 1)
       
           nombres = 0
           left, bottom = 0.90, 0.15
           ax, fig, LATPOS, PROJ, pc = pikobs.type_projection(proj)
           ONMAP = 0 
           ONMAP2 = 0
           POINTS = 'OFF'
           patch_list = []

           for i in range(len(nombre)):
               x1, y1 = PROJ.transform_point(lon[i], lat[i], pc)
               point = PROJ.transform_point(lon[i], lat[i], src_crs=pc)
               fig_coords = ax.transData.transform(point)
               ax_coords = ax.transAxes.inverted().transform(fig_coords)
               xx, yy = ax_coords
               mask = (xx >= -0.01) & (xx <= 1.01) & (yy >= -0.01) & (yy <= 1.01)
               if mask:
                   ONMAP += nombre[i]
                   if len(filesin) > 1:
 
                       ONMAP2 +=N1[i]
                   if POINTS == 'ON':
                       plt.text(point[0], point[1], int(np.floor(nombre[i])), color="k", fontsize=17, zorder=5, ha='center', va='center', weight='bold')
                   else: 
                       if boxsizex >=10:
                          plt.text(point[0], point[1], round_first_digit_3(OMP[i]), color="b", fontsize=5, zorder=5, ha='center', va='center', weight='bold')
                     
                       points4 = projectPpoly(PROJ, lat[i], lon[i], deltax, deltay, pc)
                       
                       valor = OMP[i]

                       if valor < -100:
                           col =  '#0235ad' #67001f' #0235ad'   #67001f #053061     
                       elif valor > 100:
                           col = '#b30000' #e600c7' #b2182b' #e600c7'         
                       else:
                           ind = np.digitize(valor, boundaries) - 1
                           col = Colors[inds[i]]     
                       if len(filesin) == 1:

                           col = Colors[inds[i]]

                       
                       poly = plt.Polygon(points4, fc=col, zorder=4, ec='k', lw=0.2, alpha=1.0)
                       ax.add_patch(poly)
           if len(filesin) > 1:
            
            for boite, latn, lonn in resultados:
             points4 = projectPpoly(PROJ, latn, lonn, deltax, deltay, pc)

             poly = plt.Polygon(points4, fc=(0,0,0,1), zorder=4, ec='k', lw=0.8, alpha=1.0)
             ax.add_patch(poly)


       
           ax.coastlines()
           ax.add_feature(cartopy.feature.LAND, zorder=1, edgecolor='#C0C0C0', facecolor='#C0C0C0')
           ax.add_feature(cartopy.feature.OCEAN, zorder=0, edgecolor='#7f7f7f', facecolor='#00bce3')
           ax.add_feature(cartopy.feature.BORDERS, zorder=10)
           ax.add_feature(cartopy.feature.COASTLINE, zorder=10)
           gl = ax.gridlines(color='b', linestyle=(0, (1, 1)), xlocs=range(-180, 190, 10), ylocs=LATPOS, draw_labels=False, zorder=0)
       
           divider = make_axes_locatable(ax)
           ax3 = divider.append_axes("right", size="5%", pad=0.05, axes_class=plt.Axes)
       
           cb2 = cbar.ColorbarBase(
               ax3, cmap=cmap,
               norm=norm,
               orientation='vertical',
               drawedges=True,
               extend= extend_color,
               ticks=ticks,
               boundaries=boundaries,
               alpha=1.0
           )
           def scientific(x, pos):
               return f'{x:.1e}'
       
           if vartyp == 'dens' :
               if len(filesin) < 1:
                    cb2.ax.yaxis.set_major_formatter(FuncFormatter(scientific))
       
           dif = ''
           if len(filesin) > 1:
               dif = 'Differences'
           if len(filesin) > 1 and   vartyp == 'dens':
                cb2.ax.set_ylabel(f'Percentage of increase in sum(dens [nobs/km²])/days \n relative to {namesin[0]} [%]', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) > 1 and  vartyp == 'nobs':
                cb2.ax.set_ylabel(f'Percentage of increase in sum(nobs)/days \n relative to {namesin[0]} [%]', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) > 1 and   vartyp == 'omp': 
                cb2.ax.set_ylabel(f'Percentage of improvement in OMP \n relative to {namesin[0]} [%]', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) > 1 and  vartyp == 'oma' :
                cb2.ax.set_ylabel(f'Percentage of improvement in OMA \n relative to {namesin[0]} [%]', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) > 1 and   vartyp == 'obs' :
                cb2.ax.set_ylabel(f'Percentage of improvement in {variable_name}  \n relative to {namesin[0]} [%]', fontsize=15, rotation=90, labelpad=20)
           if len(filesin) > 1 and   vartyp == 'bcorr' :
                cb2.ax.set_ylabel(f'Percentage increase in bcorr \n relative to {namesin[0]} [%]', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) > 1 and   vartyp == 'stdomp' :
                cb2.ax.set_ylabel(f'Percentage increase in stdomp \n relative to {namesin[0]} [%]', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) > 1 and   vartyp == 'stdoma' :
                cb2.ax.set_ylabel(f'Percentage increase in stdoma \n relative to {namesin[0]} [%]', fontsize=18, rotation=90, labelpad=20)
           


           if len(filesin) == 1 and   vartyp == 'dens':
                cb2.ax.set_ylabel(f'sum(dens [nobs/km²])/days', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) == 1 and  vartyp == 'nobs':
                cb2.ax.set_ylabel(f'sum(nobs)/days', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) == 1 and   vartyp == 'omp': 
                cb2.ax.set_ylabel(f'OMP {units}', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) == 1 and  vartyp == 'oma' :
                cb2.ax.set_ylabel(f'OMA {units}', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) == 1 and   vartyp == 'obs' :
                cb2.ax.set_ylabel(f'{variable_name}  {units}', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) == 1 and   vartyp == 'bcorr' :
                cb2.ax.set_ylabel(f' BIAS Correction {units} ', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) == 1 and   vartyp == 'stdomp' :
                cb2.ax.set_ylabel(f' STDOMP Correction {units} ', fontsize=18, rotation=90, labelpad=20)
           if len(filesin) == 1 and   vartyp == 'stdoma' :
                cb2.ax.set_ylabel(f' STDOMA Correction {units} ', fontsize=18, rotation=90, labelpad=20)

           if len(filesin) < 1:
               fontsize = 12
               ax.text(0.00, 1.05, namesin[0], fontsize=fontsize, color='b', transform=ax.transAxes) 
          
           else: 
               fontsize = 12
               start_x = 0.00
               y_coord = 1.05
               text1_len = len(namesin[0]) * 1.5
               text1_x = start_x
       
               if len(filesin) > 1:
                   text2_len = len(namesin[1])
                   text2_x = text1_x + text1_len
                   text3_x = text1_x + 0.2

                   ax.text(text1_x, y_coord, 'Diff ' + namesin[0] , fontsize=fontsize, color='blue', transform=ax.transAxes)
                   ax.text(text3_x, y_coord, "-" + namesin[1] , fontsize=fontsize, color='red', transform=ax.transAxes)
               else:
                   ax.text(text1_x, y_coord,  namesin[0] , fontsize=fontsize, color='blue', transform=ax.transAxes)
       
           ax.text(0.00 + 20, 1.05, vartyp, fontsize=fontsize, color='k', transform=ax.transAxes)
           ax.text(0.00, 1.02, PERIODE, fontsize=fontsize, color='#3366FF', transform=ax.transAxes)
           ax.text(0.45, 1.05, Nomvar, fontsize=fontsize, color='k', transform=ax.transAxes, fontweight='bold')
       
           ax.text(0.5, -0.08, 'Longitude', transform=ax.transAxes, ha='center', va='top', fontsize=14)
           ax.text(-0.06, 0.5, 'Latitude', transform=ax.transAxes, ha='center', va='bottom', rotation='vertical', fontsize=14)
       
           props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
           if vartyp in [f'dens', 'nobs']:
               textstr = f'Nobs=%.2i (for %.2f days)' % (ONMAP, NDAYS)
           else:
               textstr = '$\\bar{\\mu}=%.3f$ $\\bar{\\sigma}=%.3f$ \nNobs=%.2i (for %.2f days)' % (Mu, Sigma, ONMAP, NDAYS)
       
           if len(filesin) < 2:
               ax.text(0.82, 1.15, textstr, transform=ax.transAxes, fontsize=fontsize, verticalalignment='top', bbox=props)
           else:
               textstr = f'Diff Nobs={ONMAP:02d} \nDiff%={((ONMAP/(ONMAP2*NDAYS))*100):.2f}% for {NDAYS:.2f} days'
 #              textstr = f'Diff Nobs=%.2i ( Diff%= %.2i in %.2f days)' % (ONMAP, (ONMAP/ONMAP2)* NDAYS*100, NDAYS)
               ax.text(0.88, 1.15, textstr, transform=ax.transAxes, fontsize=fontsize, verticalalignment='top', bbox=props)
        
           plt.grid(True)
           plt.rcParams['axes.linewidth'] = 2
       
           if vcoord == 'join':
               plt.savefig(f'{pathwork}/{family}/{fonction}_{proj}_{layers}_id_stn_{id_stn}_{region}_vcoord_{vcoord}_varno{varno}.png', dpi=600, format='png')
           else:
               plt.savefig(f'{pathwork}/{family}/{fonction}_{proj}_{layers}_id_stn_{id_stn}_{region}_vcoord_{int(vcoord)}_varno{varno}.png', dpi=600, format='png')
           plt.close(fig) 
       
