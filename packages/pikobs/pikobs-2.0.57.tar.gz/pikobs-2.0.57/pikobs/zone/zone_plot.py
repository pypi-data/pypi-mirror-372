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

def zone_plot(
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
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    from matplotlib import cm, colors, colorbar
    import numpy as np
    import sqlalchemy
    import os
    from matplotlib.colors import ListedColormap, BoundaryNorm

    method = 1
    vcoord_type = 'Channel'
    if family == 'sw':
        vcoord_type = 'Pressure(Hpa)'

    debut = datestart
    final = dateend
    sqlite_files = filesin
    os.makedirs(pathwork, exist_ok=True)
    os.makedirs(os.path.join(pathwork, family), exist_ok=True)

    def load_data(sqlite_file):
        engine = sqlalchemy.create_engine(f"sqlite:///{sqlite_file}")
        query = f"""
        SELECT
            id_stn, varno,
            vcoord AS vcoord_bin,
            round(lat/1.0)*1.0 AS lat_bin,
            SUM(sumy)*1.0/SUM(N) AS omp,
            SQRT(SUM(sumy2)*1.0/SUM(N) - POWER(SUM(sumy)*1.0/SUM(N), 2)) AS sigma,
            SUM(N) AS n_obs
        FROM moyenne
        WHERE
            varno = {varno}
            AND id_stn = '{id_stn}'
            AND sumy IS NOT NULL
            AND date BETWEEN '{debut}' AND '{final}'
        GROUP BY id_stn, varno, vcoord_bin, lat_bin
        HAVING COUNT(*) > 1
        ORDER BY vcoord_bin DESC, lat_bin
        """
        return pd.read_sql_query(query, engine)

    # Datos del primer archivo
    df1 = load_data(sqlite_files[0])

    # Colormap personalizado (modo 'tints' sin blanco central, muy claro cerca de 0)
    def custom_div_cbar(bounds,
                        mode='tints',
                        blanco=(1,1,1,1),
                        over_color='#e600c7',
                        under_color='#0235ad'):
        M = len(bounds) - 1
        if M <= 0:
            raise ValueError("bounds debe tener al menos 2 valores")

        if mode == 'white2':
            if M % 2 != 0:
                raise ValueError("Para 'white2' usa número PAR de bins (p.ej., -100..100 paso 10).")
            N_neg = M // 2 - 1
            N_pos = M // 2 - 1
            center_slots = 2
            neg_samples = np.linspace(0.08, 0.40, max(N_neg, 0))
            pos_samples = np.linspace(0.60, 0.92, max(N_pos, 0))
            neg_colors = [cm.RdYlBu_r(x) for x in neg_samples] if N_neg > 0 else []
            pos_colors = [cm.RdYlBu_r(x) for x in pos_samples] if N_pos > 0 else []
            colors_list = neg_colors + [blanco]*center_slots + pos_colors
        elif mode == 'tints':
            if M % 2 != 0:
                raise ValueError("Para 'tints' usa número PAR de bins (p.ej., -100..100 paso 10).")
            N_neg = M // 2
            N_pos = M // 2
            neg_samples = np.linspace(0.10, 0.49, N_neg)
            pos_samples = np.linspace(0.51, 0.90, N_pos)
            neg_colors = [cm.RdYlBu_r(x) for x in neg_samples]
            pos_colors = [cm.RdYlBu_r(x) for x in pos_samples]
            colors_list = neg_colors + pos_colors
        else:
            raise ValueError("mode debe ser 'tints' o 'white2'.")

        cmap = ListedColormap(colors_list)
        cmap.set_over(over_color)
        cmap.set_under(under_color)
        cmap.set_bad((0.85, 0.85, 0.85, 1.0))
        norm = BoundaryNorm(bounds, ncolors=cmap.N, clip=False)
        return cmap, norm

    # Preparar datos, colormaps y bounds
    if len(sqlite_files) == 2:
        # Merge y porcentajes
        df2 = load_data(sqlite_files[1])
        df = pd.merge(
            df2, df1,
            on=['id_stn', 'varno', 'vcoord_bin', 'lat_bin'],
            suffixes=('_exp', '_ctl')
        )

        # Diferencias absolutas (por si quieres guardar)
        df['omp'] = (df['omp_ctl'] - df['omp_exp'])*(100/df['omp_ctl'])
        df['sigma'] =( df['sigma_ctl'] - df['sigma_exp'])*(100/df['sigma_ctl'])
        df['n_obs'] =( df['n_obs_ctl'] - df['n_obs_exp'])*(100/df['n_obs_ctl'])
        # Porcentajes respecto al control (sin recortar para ver triángulos)
        for var in ['omp', 'sigma', 'n_obs']:
            den = df[f'{var}_ctl'].replace(0, np.nan)
            df[f'{var}_pct'] = 100 * (df[f'{var}_ctl'] - df[f'{var}_exp']) / den
        df.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Límites y colormaps [-100..100] paso 10
        bounds_pct = np.arange(-100, 101, 10, dtype=float)
        cmap_omp,   norm_omp   = custom_div_cbar(bounds_pct, mode='tints')
        cmap_sigma, norm_sigma = custom_div_cbar(bounds_pct, mode='tints')
        cmap_nobs,  norm_nobs  = custom_div_cbar(bounds_pct, mode='tints')
        bounds_omp = bounds_sigma = bounds_nobs = bounds_pct

        use_percent = True
    else:
        # Un solo archivo: original (no porcentajes)
        df = df1.copy()
        bounds_omp_pos = np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 5])
        bounds_omp = np.concatenate((-bounds_omp_pos[::-1], bounds_omp_pos))
        bounds_sigma = np.array([0., 0.1, 0.2, 0.5, 1, 2, 4, 5, 6])
        bounds_nobs = [1, 50, 100, 500, 1000, 2000, 4000, 10000, 24000, 100000]

        # Reutilizamos el mismo constructor de cmap
        cmap_omp,   norm_omp   = custom_div_cbar(bounds_omp, mode='tints')
        cmap_sigma, norm_sigma = custom_div_cbar(bounds_sigma, mode='tints')
        # Para n_obs no simétrico, usa jet o un cmap secuencial si prefieres
        cmap_nobs = cm.get_cmap('jet', len(bounds_nobs) - 1)
        norm_nobs = BoundaryNorm(bounds_nobs, cmap_nobs.N)
        use_percent = False

    if df.empty:
        print("[WARNING] No data retrieved from database.")
        return

    variable_name, units, vcoord_type = pikobs.type_varno(varno)
    print(variable_name, units, vcoord_type)

    lat = df['lat_bin'].values
    vcrd = df['vcoord_bin'].values / 100. if family == 'sw' else df['vcoord_bin'].values

    # Datos a graficar (porcentaje si hay 2 archivos)
    if use_percent:
        omp = df['omp_pct'].values
        sigma = df['sigma_pct'].values
        n_obs = df['n_obs_pct'].values
        label_sigma = 'Standard Deviation (%)'
        label_omp = 'O - P (Bias) (%)'
        label_nobs = 'Number Of Observations (%)'
    else:
        omp = df['omp'].values
        sigma = df['sigma'].values
        n_obs = df['n_obs'].values
        label_sigma = 'Standard Deviation'
        label_omp = 'O - P (Bias)'
        label_nobs = 'Number Of Observations'

    Delt_LAT, DeltP = (2, 20) if family == 'sw' else (2, 0.5)

    variables = [
        ('sigma', sigma, label_sigma, cmap_sigma, norm_sigma, bounds_sigma),
        ('nobs',  n_obs,  label_nobs,  cmap_nobs,  norm_nobs,  bounds_nobs),
        ('omp',     omp,   label_omp,   cmap_omp,   norm_omp,   bounds_omp)
    ]

    # Arrays 1D
    lat = np.asarray(lat).ravel()
    vcrd = np.asarray(vcrd).ravel()

    # X-lims (latitud)
    lat_min = np.min(lat) - Delt_LAT / 2.0
    lat_max = np.max(lat) + Delt_LAT / 2.0

    # Canales únicos e índice para modo 'indices'
    unique_vcrd = np.sort(np.unique(vcrd))
    vcrd_to_idx = {val: idx for idx, val in enumerate(unique_vcrd)}
    vcrd_idx = np.array([vcrd_to_idx[val] for val in vcrd])

    # Alturas variables (modo 'values')
    def compute_variable_heights(unique_vals):
        if len(unique_vals) == 1:
            edges = np.array([unique_vals[0] - 0.5, unique_vals[0] + 0.5])
        else:
            centers = unique_vals
            mids = (centers[:-1] + centers[1:]) / 2.0
            first_edge = centers[0] - (centers[1] - centers[0]) / 2.0
            last_edge = centers[-1] + (centers[-1] - centers[-2]) / 2.0
            edges = np.concatenate(([first_edge], mids, [last_edge]))
        heights = edges[1:] - edges[:-1]
        heights_by_val = {val: heights[i] for i, val in enumerate(unique_vals)}
        return edges, heights_by_val

    if family == 'sw':
        tipo = 'values'
        y_limits = (0, 1000)
        invertir_y = True
        DeltP_val = None
        y_major_step = 100
        y_minor_step = 10
        edges_vals, heights_by_val = compute_variable_heights(unique_vcrd)
    else:
        tipo = 'indices'
        invertir_y = True
        y_limits = None
        DeltP_val = 1.0
        y_major_step = None
        y_minor_step = None
        edges_vals, heights_by_val = None, None

    outdir = os.path.join(pathwork, family)
    os.makedirs(outdir, exist_ok=True)

    for name, var, label, cmap, norm, bounds in variables:
        var = np.asarray(var).ravel()
        if var.shape[0] != lat.shape[0]:
            raise ValueError(f"var '{name}' tiene longitud {var.shape[0]} y no coincide con lat ({lat.shape[0]}).")

        fig, ax = plt.subplots(figsize=(18, 18))
        ax.set_xlim(lat_min, lat_max)

        # Mapeo de colores consistente (incluye under/over y NaN)
        mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array([])  # para colorbar
        colors_vec = mappable.to_rgba(var)

        # Crear rectángulos
        rects = []
        for i in range(len(var)):
            vi = var[i]
            if not np.isnan(vi):
                FC = colors_vec[i]
                if tipo == 'indices':
                    y_center = int(vcrd_idx[i])
                    y_height = 1.0
                else:
                    y_center = vcrd[i]
                    if DeltP_val is None and heights_by_val is not None:
                        key = y_center
                        if key not in heights_by_val:
                            idx_near = int(np.argmin(np.abs(unique_vcrd - y_center)))
                            key = unique_vcrd[idx_near]
                        y_height = float(heights_by_val[key])
                    else:
                        y_height = float(DeltP_val)

                rects.append(Rectangle(
                    (lat[i] - Delt_LAT / 2.0, y_center - y_height / 2.0),
                    Delt_LAT, y_height,
                    facecolor=FC, edgecolor=FC
                ))

        ax.add_collection(PatchCollection(rects, match_original=True))

        # Eje Y y rejilla
        if tipo == 'indices':
            N = len(unique_vcrd)
            pad = 0.5
            ymin, ymax = -0.5 - pad, N - 0.5 + pad
            ax.set_ylim((ymax, ymin) if invertir_y else (ymin, ymax))
            ax.set_yticks(np.arange(N))
            ax.set_yticklabels([f"{v:.0f}" for v in unique_vcrd], fontsize=6)
            ax.set_yticks(np.arange(-0.5, N + 0.5, 1.0), minor=True)
            ax.grid(False)
            ax.grid(True, axis='y', which='minor', color='k', linewidth=0.8)
            ax.grid(True, axis='x', which='major', color='k', alpha=0.3)
            ax.set_ylabel(vcoord_type)
        else:
            if y_limits is not None:
                ymin, ymax = y_limits
            else:
                if edges_vals is not None:
                    ymin, ymax = float(edges_vals[0]), float(edges_vals[-1])
                else:
                    ymin = float(np.nanmin(vcrd) - 0.5 * (1.0 if DeltP_val is None else DeltP_val))
                    ymax = float(np.nanmax(vcrd) + 0.5 * (1.0 if DeltP_val is None else DeltP_val))
            ax.set_ylim((ymax, ymin) if invertir_y else (ymin, ymax))

            import matplotlib.ticker as mticker
            if y_major_step is None or y_minor_step is None:
                span = abs(ymax - ymin)
                if y_major_step is None:
                    y_major_step = 100 if span >= 800 else 50 if span >= 300 else 10
                if y_minor_step is None:
                    y_minor_step = max(y_major_step / 5.0, 1)
            ax.yaxis.set_major_locator(mticker.MultipleLocator(y_major_step))
            ax.yaxis.set_minor_locator(mticker.MultipleLocator(y_minor_step))
            ax.grid(True, axis='y', which='major', color='k', alpha=0.4)
            ax.grid(True, axis='x', which='major', color='k', alpha=0.3)
            ax.set_ylabel(vcoord_type)

        ax.set_xlabel('Latitud')
        ax.set_title(f'{label} vs Latitude and Channel from {datestart} to {dateend},\nvarno={varno}, id_stn={id_stn}')

        # Barra de color (con triángulos si hay 2 archivos/porcentaje)
        cax = fig.add_axes([0.91, 0.15, 0.02, 0.7])
        cb = fig.colorbar(
            mappable, cax=cax,
            boundaries=bounds,
            orientation='vertical',
            extend='both' if use_percent else 'neither'
        )
        cb.set_label(label)
        if use_percent:
            cb.set_ticks(np.arange(-100, 101, 20))

        # Guardado
        output_file = os.path.join(outdir, f'1scatterplot_{"_".join(namesin)}_{name}_var{varno}_{id_stn}.png')
        plt.savefig(output_file, dpi=600, format='png', bbox_inches='tight', pad_inches=0.05)
        plt.close(fig)

def zone_plot2(
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
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    from matplotlib import cm, colors, colorbar
    import numpy as np
    import sqlalchemy
    import os
    from matplotlib.colors import ListedColormap, BoundaryNorm
    method = 1
    vcoord_type = 'Channel'
    if family == 'sw':
        vcoord_type = 'Pressure(Hpa)'

    debut = datestart
    final = dateend
    sqlite_files = filesin
    os.makedirs(pathwork, exist_ok=True)
    os.makedirs(os.path.join(pathwork, family), exist_ok=True)

    def load_data(sqlite_file):
        engine = sqlalchemy.create_engine(f"sqlite:///{sqlite_file}")
        query = f"""
        SELECT
            id_stn, varno,
            vcoord AS vcoord_bin,
            round(lat/1.0)*1.0 AS lat_bin,
            SUM(sumy)*1.0/SUM(N) AS omp,
            SQRT(SUM(sumy2)*1.0/SUM(N) - POWER(SUM(sumy)*1.0/SUM(N), 2)) AS sigma,
            SUM(N) AS n_obs
        FROM moyenne
        WHERE
            varno = {varno}
            AND id_stn = '{id_stn}'
            AND sumy IS NOT NULL
            AND date BETWEEN '{debut}' AND '{final}'
        GROUP BY id_stn, varno, vcoord_bin, lat_bin
        HAVING COUNT(*) > 1
        ORDER BY vcoord_bin DESC, lat_bin
        """
        return pd.read_sql_query(query, engine)

    def custom_div_cbar(bounds, cmap_name='seismic', center_color=[0.7, 0.7, 0.7, 1]):
        n_bins = len(bounds) - 1
        ncolors = 2 * n_bins + 1
        base = cm.get_cmap(cmap_name, ncolors)
        color_arr = base(np.linspace(0, 1, ncolors)).copy()
        zero_bin = np.searchsorted(bounds, 0) - 1
        cmap_out = ListedColormap(color_arr[n_bins - (n_bins // 2): n_bins + (n_bins // 2) + 1])
        norm = BoundaryNorm(bounds, cmap_out.N)
        return cmap_out, norm

    df1 = load_data(sqlite_files[0])

    if len(sqlite_files) == 2:
      def custom_div_cbar(bounds,
                          mode='tints',               # 'tints' => sin blanco central, tonos muy claros cerca de 0
                          blanco=(1,1,1,1),
                          over_color='#e600c7',
                          under_color='#0235ad'):
          """
          Crea cmap/norm:
            - mode='tints': sin blanco central; el bin [-10,0] es azul muy claro, [0,10] amarillo muy claro.
            - mode='white2': dos bins blancos en el centro ([-10,0] y [0,10]).
          """
          M = len(bounds) - 1
          if M <= 0:
              raise ValueError("bounds debe tener al menos 2 valores")
      
          if mode == 'white2':
              # 2 bins blancos centrales
              if M % 2 != 0:
                  raise ValueError("Para 'white2' usa número PAR de bins (p.ej., -100..100 paso 10).")
              N_neg = M // 2 - 1
              N_pos = M // 2 - 1
              center_slots = 2
              neg_samples = np.linspace(0.08, 0.40, max(N_neg, 0))  # azul oscuro -> azul claro
              pos_samples = np.linspace(0.60, 0.92, max(N_pos, 0))  # amarillo claro -> rojo
              neg_colors = [cm.RdYlBu_r(x) for x in neg_samples] if N_neg > 0 else []
              pos_colors = [cm.RdYlBu_r(x) for x in pos_samples] if N_pos > 0 else []
              colors = neg_colors + [blanco]*center_slots + pos_colors
      
          elif mode == 'tints':
              # Sin blanco central, 10 neg + 10 pos con tonos muy claros cerca de 0
              if M % 2 != 0:
                  raise ValueError("Para 'tints' usa número PAR de bins (p.ej., -100..100 paso 10).")
              N_neg = M // 2
              N_pos = M // 2
              # Muy cerca de blanco (0.5 en RdYlBu_r es blanco): usamos 0.49 y 0.51 como bordes internos
              neg_samples = np.linspace(0.10, 0.49, N_neg)  # azul -> azul muy claro (casi blanco)
              pos_samples = np.linspace(0.51, 0.90, N_pos)  # amarillo muy claro -> rojo
              neg_colors = [cm.RdYlBu_r(x) for x in neg_samples]
              pos_colors = [cm.RdYlBu_r(x) for x in pos_samples]
              colors = neg_colors + pos_colors
      
          else:
              raise ValueError("mode debe ser 'tints' o 'white2'.")
      
          cmap = ListedColormap(colors)
          cmap.set_over(over_color)
          cmap.set_under(under_color)
          cmap.set_bad((0.85, 0.85, 0.85, 1.0))
      
          norm = BoundaryNorm(bounds, ncolors=cmap.N, clip=False)
          return cmap, norm
      # 2) Ejemplo: preparar porcentajes y límites [-100, 100]
      # Cargar y unir (ajusta a tu entorno)
      df2 = load_data(sqlite_files[1])
      df = pd.merge(
          df2, df1,
          on=['id_stn', 'varno', 'vcoord_bin', 'lat_bin'],
          suffixes=('_exp', '_ctl')
      )
      
      # Diferencias absolutas (por si las usas)
      df['omp'] = df['omp_ctl'] - df['omp_exp']
      df['sigma'] = df['sigma_ctl'] - df['sigma_exp']
      df['n_obs'] = df['n_obs_ctl'] - df['n_obs_exp']
      
      # Porcentajes respecto al control (evita división por cero)
      for var in ['omp', 'sigma', 'n_obs']:
          den = df[f'{var}_ctl'].replace(0, np.nan)
          df[f'{var}_pct'] = 100 * (df[f'{var}_ctl'] - df[f'{var}_exp']) / den
      
      # Opcional: recortar para mapas
      pct_cols = ['omp_pct', 'sigma_pct', 'n_obs_pct']
      df[pct_cols] = df[pct_cols].clip(-100, 100).replace([np.inf, -np.inf], np.nan)
      
      # Límites discretos de -100 a 100 cada 10
      bounds_pct = np.arange(-100, 101, 10, dtype=float)
      
      # 3) Crear cmap/norm con tus colores
      cmap_omp,   norm_omp   = custom_div_cbar(bounds_pct, blanco=(1.0, 1.0, 0.6, 1.0))
      cmap_sigma, norm_sigma = custom_div_cbar(bounds_pct, blanco=(1.0, 1.0, 0.6, 1.0))
      cmap_nobs,  norm_nobs  = custom_div_cbar(bounds_pct, blanco=(1.0, 1.0, 0.6, 1.0))
      
      # Aliases si tu código espera estos nombres
      bounds_omp = bounds_sigma = bounds_nobs = bounds_pct
      im = ax.pcolormesh(X, Y, data, cmap=cmap_sigma, norm=norm_sigma)
      cbar = plt.colorbar(im, ax=ax, extend='both')  # esto dibuja los triángulos under/over
#        bounds_omp_pos = np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 5])
#        bounds_omp = np.concatenate((-bounds_omp_pos[::-1], bounds_omp_pos))
#        bounds_sigma_pos = np.array([0.05, 0.1, 0.2, 0.5, 1])
#        bounds_sigma = np.concatenate((-bounds_sigma_pos[::-1], bounds_sigma_pos))
#        bounds_nobs_pos = np.array([1, 50, 100, 500 ])
#        bounds_nobs = np.concatenate((-bounds_nobs_pos[::-1], bounds_nobs_pos)) 
#        cmap_sigma, norm_sigma = custom_div_cbar(bounds_sigma, 'PuOr')
#        cmap_omp, norm_omp = custom_div_cbar(bounds_omp, 'seismic')
#        cmap_nobs = cm.get_cmap('jet', len(bounds_nobs) - 1)
#        norm_nobs = BoundaryNorm(bounds_nobs, cmap_nobs.N)

    else:
        df = df1.copy()
        bounds_omp_pos = np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 5])
        bounds_omp = np.concatenate((-bounds_omp_pos[::-1], bounds_omp_pos))
        bounds_sigma = np.array([0., 0.1, 0.2, 0.5, 1, 2, 4, 5, 6])
        bounds_nobs = [1, 50, 100, 500, 1000, 2000, 4000, 10000, 24000, 100000]

        cmap_omp, norm_omp = custom_div_cbar(bounds_omp, 'seismic')
        cmap_sigma, norm_sigma = custom_div_cbar(bounds_sigma, 'PuOr')
        cmap_nobs = cm.get_cmap('jet', len(bounds_nobs) - 1)
        norm_nobs = BoundaryNorm(bounds_nobs, cmap_nobs.N)

    if df.empty:
        print("[WARNING] No data retrieved from database.")
        return
    variable_name, units, vcoord_type = pikobs.type_varno(varno)
    print (variable_name, units, vcoord_type)
    lat = df['lat_bin'].values
    vcrd = df['vcoord_bin'].values / 100. if family == 'sw' else df['vcoord_bin'].values
    omp = df['omp'].values
    sigma = df['sigma'].values
    n_obs = df['n_obs'].values

    Delt_LAT, DeltP = (2, 20) if family == 'sw' else (2, 0.5)
    vcoord_min_plot, vcoord_max_plot = vcrd.min(), vcrd.max()
    lat_min, lat_max = -91, 91

    variables = [
        ('sigma', sigma, 'Standard Deviation', cmap_sigma, norm_sigma, bounds_sigma),
        ('nobs', n_obs, 'Number Of Observations', cmap_nobs, norm_nobs, bounds_nobs),
        ('omp', omp, 'O - P (Bias)', cmap_omp, norm_omp, bounds_omp)
    ]


    # Arrays 1D
    lat = np.asarray(lat).ravel()
    vcrd = np.asarray(vcrd).ravel()
    
    # X-lims (latitud) con margen medio Delt_LAT
    lat_min = np.min(lat) - Delt_LAT / 2.0
    lat_max = np.max(lat) + Delt_LAT / 2.0
    
    # Canales únicos y mapeo a índice (para modo 'indices')
    unique_vcrd = np.sort(np.unique(vcrd))
    vcrd_to_idx = {val: idx for idx, val in enumerate(unique_vcrd)}
    vcrd_idx = np.array([vcrd_to_idx[val] for val in vcrd])
    
    # Precalcular celdas (bordes y alturas) en modo 'values' para DeltP_val auto (variable)
    def compute_variable_heights(unique_vals):
        # Si solo hay un valor, asume altura 1.0
        if len(unique_vals) == 1:
            edges = np.array([unique_vals[0] - 0.5, unique_vals[0] + 0.5])
        else:
            centers = unique_vals
            mids = (centers[:-1] + centers[1:]) / 2.0
            # bordes extremos por extrapolación
            first_edge = centers[0] - (centers[1] - centers[0]) / 2.0
            last_edge = centers[-1] + (centers[-1] - centers[-2]) / 2.0
            edges = np.concatenate(([first_edge], mids, [last_edge]))
        heights = edges[1:] - edges[:-1]
        heights_by_val = {val: heights[i] for i, val in enumerate(unique_vals)}
        return edges, heights_by_val
    
    # Elegir modo según 'family'
    if family == 'sw':
        # Modo valores reales, eje 0..1000 e invertido (0 arriba).
        tipo = 'values'
        y_limits = (0, 1000)
        invertir_y = True           # pon False si prefieres 0 abajo, 1000 arriba
        DeltP_val = None            # AUTO: altura variable según discretización real
        y_major_step = 100
        y_minor_step = 10
        # Prepara alturas variables
        edges_vals, heights_by_val = compute_variable_heights(unique_vcrd)
    else:
        # Modo compacto por canales (categorías)
        tipo = 'indices'
        invertir_y = True           # canal menor arriba; pon False si lo quieres abajo
        y_limits = None
        DeltP_val = 1.0             # no se usa en 'indices'
        y_major_step = None
        y_minor_step = None
        edges_vals, heights_by_val = None, None
    
    # Directorio de salida
    outdir = os.path.join(pathwork, family)
    os.makedirs(outdir, exist_ok=True)
    
    # Bucle por variables
    for name, var, label, cmap, norm, bounds in variables:
        var = np.asarray(var).ravel()
        if var.shape[0] != lat.shape[0]:
            raise ValueError(f"var '{name}' tiene longitud {var.shape[0]} y no coincide con lat ({lat.shape[0]}).")
    
        fig, ax = plt.subplots(figsize=(14, 14))
        ax.set_xlim(lat_min, lat_max)
    
        # Mapeo de colores
        mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
        colors_list = [mappable.to_rgba(x) for x in bounds]
        inds = np.digitize(var, bounds)
    
        # Crear rectángulos
        rects = []
        for i in range(len(var)):
            vi = var[i]
            if not np.isnan(vi):
                if vi < bounds[0] or vi > bounds[-1]:
                    FC = '#FF00FF'  # fuera de rango
                else:
                    idx_color = max(0, min(inds[i] - 1, len(colors_list) - 1))
                    FC = colors_list[idx_color]
    
                if tipo == 'indices':
                    y_center = int(vcrd_idx[i])
                    y_height = 1.0
                else:
                    y_center = vcrd[i]
                    # Si DeltP_val es None -> usar altura variable por discretización
                    if DeltP_val is None and heights_by_val is not None:
                        # Puede fallar si vcrd[i] no está exactamente en unique_vcrd por flotantes;
                        # en ese caso buscamos el índice del valor más cercano.
                        key = y_center
                        if key not in heights_by_val:
                            idx_near = int(np.argmin(np.abs(unique_vcrd - y_center)))
                            key = unique_vcrd[idx_near]
                        y_height = float(heights_by_val[key])
                    else:
                        y_height = float(DeltP_val)
    
                rects.append(Rectangle(
                    (lat[i] - Delt_LAT / 2.0, y_center - y_height / 2.0),
                    Delt_LAT, y_height,
                    facecolor=FC, edgecolor=FC
                ))
    
        ax.add_collection(PatchCollection(rects, match_original=True))
    
        # Configuración del eje Y y rejilla
        if tipo == 'indices':
            N = len(unique_vcrd)
            pad = 0.5  # margen para que no se “coman” las celdas extremas
            ymin, ymax = -0.5 - pad, N - 0.5 + pad
            ax.set_ylim((ymax, ymin) if invertir_y else (ymin, ymax))
    
            # Ticks mayores en centros (etiquetas reales), menores en bordes (rejilla)
            ax.set_yticks(np.arange(N))
            #ax.set_yticklabels(int(unique_vcrd), fontsize=6)
            ax.set_yticklabels([f"{v:.0f}" for v in unique_vcrd], fontsize=6)
            ax.set_yticks(np.arange(-0.5, N + 0.5, 1.0), minor=True)
    
            ax.grid(False)
            ax.grid(True, axis='y', which='minor', color='k', linewidth=0.8)
            ax.grid(True, axis='x', which='major', color='k', alpha=0.3)
            ax.set_ylabel(vcoord_type)
        else:
            # Modo valores reales (0..1000 si family == 'ee')
            if y_limits is not None:
                ymin, ymax = y_limits
            else:
                # Si tenemos bordes calculados, usarlos para no cortar
                if edges_vals is not None:
                    ymin, ymax = float(edges_vals[0]), float(edges_vals[-1])
                else:
                    ymin = float(np.nanmin(vcrd) - 0.5 * (1.0 if DeltP_val is None else DeltP_val))
                    ymax = float(np.nanmax(vcrd) + 0.5 * (1.0 if DeltP_val is None else DeltP_val))
    
            ax.set_ylim((ymax, ymin) if invertir_y else (ymin, ymax))
    
            # Ticks y rejileta
            if y_major_step is None or y_minor_step is None:
                span = abs(ymax - ymin)
                if y_major_step is None:
                    y_major_step = 100 if span >= 800 else 50 if span >= 300 else 10
                if y_minor_step is None:
                    y_minor_step = max(y_major_step / 5.0, 1)
            import matplotlib.ticker as mticker   
           # ax.yaxis.set_major_locator(MultipleLocator(y_major_step))
           # ax.yaxis.set_minor_locator(MultipleLocator(y_minor_step))
            ax.yaxis.set_major_locator(mticker.MultipleLocator(y_major_step))
            ax.yaxis.set_minor_locator(mticker.MultipleLocator(y_minor_step))
            ax.grid(True, axis='y', which='major', color='k', alpha=0.4)
            ax.grid(True, axis='x', which='major', color='k', alpha=0.3)
            ax.set_ylabel(vcoord_type)
    
        ax.set_xlabel('Latitud')
        ax.set_title(f'{label} vs Latitude and Channel from {datestart} to {dateend},\nvarno={varno}, id_stn={id_stn}')
    
        # Barra de color
        cax = fig.add_axes([0.91, 0.15, 0.02, 0.7])
        cb = colorbar.ColorbarBase(
            cax, cmap=cmap, norm=norm, boundaries=bounds,
            orientation='vertical', ticks=bounds
        )
        cb.set_label(label)
    
        # Guardado alta resolución
        output_file = os.path.join(outdir, f'1scatterplot_{"_".join(namesin)}_{name}_var{varno}_{id_stn}.png')
        plt.savefig(output_file, dpi=600, format='png', bbox_inches='tight', pad_inches=0.05)
        plt.close(fig)
#    for name, var, label, cmap, norm, bounds in variables:
#        fig, ax = plt.subplots(figsize=(14, 7))
#        ax.set_xlim(lat_min, lat_max)
#        if vcoord_type.lower() == 'channel':
#            ax.set_ylim(vcoord_max_plot, vcoord_min_plot)
#        else:
#            ax.set_ylim(1000, 0) if family == 'sw' else ax.set_ylim(vcoord_min_plot, vcoord_max_plot)
#
#        mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
#        colors_list = [mappable.to_rgba(x) for x in bounds]
#        inds = np.digitize(var, bounds)
#
#        rects = []
#        for i in range(len(var)):
#            if not np.isnan(var[i]):
#                val = var[i]
#                if val < bounds[0] or val > bounds[-1]:
#                    FC = '#FF00FF'
#                else:
#                    idx = max(0, min(inds[i] - 1, len(colors_list) - 1))
#                    FC = colors_list[idx]
#                rect = Rectangle(
#                    (lat[i] - Delt_LAT / 2.0, vcrd[i] - DeltP / 2.0),
#                    Delt_LAT, DeltP,
#                    facecolor=FC, edgecolor=FC
#                )
#                rects.append(rect)
#
#        ax.add_collection(PatchCollection(rects, match_original=True))
#        ax.set_xlabel('Latitude')
#        ax.set_ylabel(vcoord_type)
#        ax.set_title(f'{label} vs Latitude and {vcoord_type} from {datestart} to {dateend},\nvarno={varno}, id_stn={id_stn}')
#        ax.grid(True, color='k')
#
#        cax = fig.add_axes([0.91, 0.15, 0.02, 0.7])
#        cb = colorbar.ColorbarBase(cax, cmap=cmap, norm=norm, boundaries=bounds,
#                                   orientation='vertical', ticks=bounds)
#        cb.set_label(label)
#
#        output_file = os.path.join(pathwork, family, f'scatterplot_{"_".join(namesin)}_{name}_var{varno}_{id_stn}.png')
#        plt.savefig(output_file, format='png')
#        plt.close(fig)
#
