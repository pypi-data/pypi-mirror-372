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
    if np.any(zero_surf_indices):
        print('surf=', lat1[zero_surf_indices], lat2[zero_surf_indices], lat2[zero_surf_indices] * np.pi / 180.0,
              lat1[zero_surf_indices] * np.pi / 180.0,
              np.sin(lat2[zero_surf_indices] * np.pi / 180.0),
              np.sin(lat1[zero_surf_indices] * np.pi / 180.0))
    return surf
##           plt.close(fig)
def days_between(d1, d2):
    d1 = datetime.datetime.strptime(d1, "%Y%m%d%H")
    d2 = datetime.datetime.strptime(d2, "%Y%m%d%H")
    return abs((d2 - d1).days)
import pikobs

def profile_plot(
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
    intervales
):
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    import sqlalchemy
    import os

    selected_flags = pikobs.flag_criteria(flag_criteria)

    element = varno
    sat = id_stn

    def load_data(dbfile):
        engine = sqlalchemy.create_engine(f"sqlite:///{dbfile}")
        query = f"""
        SELECT 
          varno,
          round(vcoord) AS vcoord,
          SUM(sumy) * 1.0 / SUM(N) AS bias,
          SQRT(
            SUM(sumy2)*1.0/SUM(N) - POWER(SUM(sumy), 2)*1.0/(SUM(N)*SUM(N))
          ) AS scartype,
          MIN(sumy) AS min_sumy,
          MAX(sumy) AS max_sumy,
          SUM(N) AS total_n
        FROM moyenne
        WHERE 
          varno = {element}
          AND id_stn IN ('{sat}')
          AND sumy IS NOT NULL
        GROUP BY varno, round(vcoord)
        HAVING COUNT(*) > 1
        ORDER BY round(vcoord)
        """
        return pd.read_sql_query(query, engine)

    # --- Cargar datos ---
    df0 = load_data(filesin[0])
    has_exp = len(filesin) > 1 and os.path.exists(filesin[1])
    df1 = load_data(filesin[1]) if has_exp else None
     
    # --- Crear figura y ejes ---
    fig, ax = plt.subplots(figsize=(14, 10))
 #   fig, ax = plt.subplots(constrained_layout=True)
    def plot_curve(df, label, color, alpha):
        ax.fill_betweenx(df['vcoord'], df['min_sumy'], df['max_sumy'],
                         color=color, alpha=alpha, label=f'{label} min-max')
        ax.plot(df['bias'], df['vcoord'], label=f'{label} bias', color=color, linewidth=2)
        ax.plot(df['scartype'], df['vcoord'], label=f'{label} scartype', color=color, linestyle='--')

    # Dibujar control (azul)
    plot_curve(df0, namesin[0], 'blue', alpha=0.07)

    # Dibujar experiencia (verde), si existe
    if has_exp:
        plot_curve(df1, namesin[1], 'red', alpha=0.07)

    # Ejes y título
    ax.set_xlabel('Value') 
    ax.set_ylabel('Channel')

    if family=='sw':
       ax.set_ylabel('Pressure (Hpa)')
    ax.invert_yaxis()
    ax.grid(True)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
    ax.set_title(f'From {datestart} to {dateend} \nvarno={element}, id_stn={sat}')

    # Segundo eje Y (solo para alinear en altura)
    ax2 = ax.twinx()
    ax2.set_ylim(ax.get_ylim())
    ax2.set_yticks([])
    ax2.set_ylabel("")

    # Aumentar margen derecho para mostrar dos columnas de texto
    xmin, xmax = ax.get_xlim()
    ax.set_xlim(xmin, xmax )  # más espacio

    # Coordenadas relativas al eje
    transform = ax.get_yaxis_transform()

    # Posiciones horizontales relativas para las columnas de texto
    col1_x = 1.0
    col2_x = 1.07

    # Mostrar columna 1 (control)
    for _, row in df0.iterrows():
        ax.text(col1_x, row['vcoord'], f"{int(row['total_n'])}",
                transform=transform, va='center', ha='left', fontsize=9, color='blue')

    # Mostrar columna 2 (experiencia), si existe
    if has_exp:
        for _, row in df1.iterrows():
            ax.text(col2_x, row['vcoord'], f"{int(row['total_n'])}",
                    transform=transform, va='center', ha='left', fontsize=9, color='red')

    # Encabezados
    min_y = min(df0['vcoord'].min(), df1['vcoord'].min() if has_exp else df0['vcoord'].min())
    ax.text(col1_x, min_y - 3000, f'{namesin[0]} Obs',
            transform=transform, va='center', ha='left', fontsize=10, color='blue')
    if has_exp:
        ax.text(col2_x, min_y - 3000, f'{namesin[1]} Obs',
                transform=transform, va='center', ha='left', fontsize=10, color='red')

    # Guardar gráfico
    plt.tight_layout()
    output = f"{pathwork}/{family}/{fonction}_id_stn_{id_stn}_{region}_varno{varno}.png"
    os.makedirs(os.path.dirname(output), exist_ok=True)
    plt.savefig(output)
    plt.close()

