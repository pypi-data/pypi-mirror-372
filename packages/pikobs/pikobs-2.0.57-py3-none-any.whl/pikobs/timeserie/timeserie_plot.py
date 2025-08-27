#!/usr/bin/env python3
import numpy as np
import sys
import csv
import dateutil
from datetime import datetime
#import matplotlib.dates as dates2
from matplotlib.dates import date2num
import pikobs
import math
from matplotlib.dates import MONDAY,MO, TU, WE, TH, FR, SA, SU
from matplotlib.dates import  DateFormatter, WeekdayLocator,DayLocator
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as pyplot
import sqlite3
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator, date2num
import dateutil.parser
from matplotlib.lines import Line2D

def custom_round(value):

    
     return round(value, 3)


def plot_time_series(curso, table_name):
              """
              Plot time series data for all distinct `id_stn` in the specified database table.
              
              :param database_path: Path to the SQLite database file.
              :param table_name: Name of the table containing the time series data.
              """
              
              try:
                  # Query to retrieve distinct id_stn values
                  distinct_stations_query = f"SELECT DISTINCT id_stn FROM {table_name};"
                  cursor.execute(distinct_stations_query)
                  distinct_stations = cursor.fetchall()
                  # Extract the station IDs
                  id_stn_values = [row[0] for row in distinct_stations]
          
                  # Define the SQL query to fetch date and Nobs for each station
                  query_template = f"""
                      SELECT
                          DATE,
                          Nacc  -- Make sure this is the correct field for your case
                      FROM
                          {table_name}
                      WHERE
                          id_stn = ?
                      GROUP BY
                          DATE;
                  """
          
                  # Initialize a plot
                  import matplotlib.pyplot as plt
                  plt.figure(figsize=(10, 6))
          
                  # Loop over each id_splot_time_series(curso, table_name)tn value to fetch data and plot
                  for id_stn in id_stn_values:
                      print (id_stn)
                      # Execute the query with the current id_stn
                      cursor.execute(query_template, (id_stn,))
                      results = cursor.fetchall()
          
                      # Extract Dates and Nobs and convert them to arrays
                      Dates = np.array([row[0] for row in results])
                      Nobs = np.array([row[1] for row in results])
                      # Plot the data, label each line with the id_stn
                      plt.plot(Dates, Nobs, label=f'Station {id_stn}')
          
                  # Customize the plot
                  plt.xlabel('Date')
                  plt.ylabel('Nobs')
                  plt.title('Time Series of Nobs for Multiple Stations')
                  plt.legend()
                  plt.xticks(rotation=45)
                  plt.tight_layout()
          
                  # Show the plot
                  pyplot.savefig('po.png')
              finally:

                  print (1)

def timeserie_plot_all_t(pathwork, datestart, dateend, fonction, flag_type, family,
                   region, fig_title, vcoord, id_stn, varnos, files, names):

    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.dates import date2num, DayLocator, HourLocator, DateFormatter
    from matplotlib.ticker import NullFormatter
    from datetime import datetime
    import numpy as np
    import sqlite3
    import dateutil.parser
    import math

    # Ajustes globales de estilo
    mpl.style.use('classic')
    mpl.rcParams.update({
        'lines.linewidth': 1.0,
        'lines.dashed_pattern': [6, 6],
        'lines.dashdot_pattern': [3, 5, 1, 5],
        'lines.dotted_pattern': [1, 3],
        'lines.scale_dashes': False
    })

    if isinstance(varnos, int):
        varnos = [varnos]

    def build_criteria(id_stn, vcoord):
        if id_stn == 'join' and vcoord == 'join':
            return ""
        elif id_stn == 'join':
            return f" and vcoord = {vcoord} "
        elif vcoord == 'join':
            return f" and id_stn = '{id_stn}' "
        else:
            return f" and vcoord = {vcoord} and id_stn = '{id_stn}' "
    from itertools import cycle
    colors_base = plt.get_cmap('tab20').colors
    if varnos!=None:
        varno = varnos
        FNAM, FNAMP, SUM, SUM2 = pikobs.type_boxes(fonction)
        Misgv, MisgvN = -999., 0
        variable_name, units, vcoord_type = pikobs.type_varno(varno)

        try:
            vcoord = int(vcoord)
        except ValueError:
            pass
        for filenumb, file in enumerate(files):
            conn = sqlite3.connect(file)
            cursor = conn.cursor()
            cursor.execute("PRAGMA TEMP_STORE=memory")

            cursor.execute(f"SELECT DISTINCT id_stn FROM timeserie WHERE varno = {varno};")
            id_stns = [row[0] for row in cursor.fetchall()]
            if not id_stns:
                continue

            fig = plt.figure(figsize=(14, 5))
            axes = [
                plt.axes([0.1, 0.58, 0.9, 0.35]),
                plt.axes([0.1, 0.21, 0.9, 0.25]),
                plt.axes([0.1, 0.01, 0.9, 0.15])
            ]
            for i, ax in enumerate(axes):
                ax.grid(True)
                if i == 0:
                    ax.xaxis.tick_bottom()
                else:
                    ax.xaxis.set_visible(i == 1)
                    ax.yaxis.set_visible(i == 1)
            axes[2].xaxis.set_visible(False)
            axes[2].yaxis.set_visible(False)

            xmi, xma = None, None
            TITRE = ""
            legend_items = []

            for idx, id_stn in enumerate(id_stns):
                id_stns_sorted = sorted(set(id_stns))  # todos los id_stn únicos ordenados
                id_stn_color_map = {
                id_stn: colors_base[i % len(colors_base)]
                  for i, id_stn in enumerate(id_stns_sorted)
                    }
                crite = build_criteria(id_stn, vcoord)
                query = f"""
                    SELECT DATE, varno, Nrej, Nacc,
                      SUM({SUM})/SUM(CAST(N AS FLOAT)) AVG,
                      SQRT(SUM({SUM2})/SUM(CAST(N AS FLOAT)) - SUM({SUM})/SUM(CAST(N AS FLOAT))*SUM({SUM})/SUM(CAST(N AS FLOAT))) STD,
                      SUM(sumstat)/SUM(CAST(N AS FLOAT)) BCORR
                    FROM timeserie
                    WHERE varno='{varno}' {crite}
                    GROUP BY DATE;
                """
                cursor.execute(query)
                results = cursor.fetchall()
                if not results:
                    continue

                Dates2 = np.array([row[0] for row in results])
                Nrejets = np.array([row[2] for row in results], dtype=float)
                Bomp2   = np.array([row[4] for row in results], dtype=float)
                Somp2   = np.array([row[5] for row in results], dtype=float)
                Nomb2   = np.array([row[3] for row in results], dtype=float)
                bcorr   = np.array([row[6] for row in results], dtype=float)
                dates = [dateutil.parser.parse(s) for s in Dates2]
                debut, fin = dates[0], dates[-1]
                if not TITRE:
                    TITRE = f'From {debut:%Y%m%d%H} to {fin:%Y%m%d%H}'
                x = date2num(dates)

                Bomp2_masked = np.ma.masked_where(Bomp2 <= Misgv, Bomp2)
                Somp2_masked = np.ma.masked_where(Somp2 <= Misgv, Somp2)
                NB_masked = np.ma.masked_where(Nomb2 <= MisgvN, Nomb2)
                SNrej_masked = np.ma.masked_where(Nrejets <= Misgv, Nrejets)
                Bcorr_masked = np.ma.masked_where(bcorr <= Misgv, bcorr)

                ax1 = axes[0]
                ax2 = axes[1]

               # color = couleurs[idx % len(couleurs)]
               # color = next(couleurs)
                color = id_stn_color_map[id_stn]
                ax1.plot(x, Bomp2_masked, '--o', ms=3, color=color, lw=2)
                ax1.plot(x, Somp2_masked, '-*', ms=4, color=color, lw=2)
                if fonction in ('BIAS_CORR', 'OBS_ERROR'):
                    ax1.plot(x, Bcorr_masked, '-p', ms=4, color='g', lw=2)
                if fonction in ('NOBS', 'DENS'):
                    ax1.plot(x, NB_masked, drawstyle='steps', color='g')

                ax2.plot(x, NB_masked, '-o', drawstyle='steps', ms=3, color=color, lw=2)
                ax2.plot(x, SNrej_masked, '--p', drawstyle='steps', ms=4, color=color, lw=2)

                legend_items.append((id_stn, color))

                if xmi is None:
                    xmi, xma = x[0], x[-1]
                else:
                    xmi = min(xmi, x[0])
                    xma = max(xma, x[-1])

            # Format eje X
            diff_days = (datetime.strptime(dateend, "%Y%m%d%H") - datetime.strptime(datestart, "%Y%m%d%H")).days
            interval = 1 if diff_days <= 30 else 3
            major_locator = DayLocator(interval=interval)
            minor_locator = HourLocator(interval=10)
            major_formatter = DateFormatter('%m%d')

            for ax in [axes[0], axes[1]]:
                ax.set_xlim([xmi, xma])
                ax.xaxis.set_major_locator(major_locator)
                ax.xaxis.set_major_formatter(major_formatter)
                ax.xaxis.set_minor_locator(minor_locator)
                ax.xaxis.set_minor_formatter(NullFormatter())
                ax.tick_params(axis='x', which='minor', bottom=True)
                ax.tick_params(axis='x', which='major', bottom=True, labelsize=10)
                ax.grid(True, which='minor', axis='x')

            axes[0].text(0.00, 1.04, names[filenumb], fontsize=11, color='black', transform=axes[0].transAxes)
            axes[0].text(0.25, 1.04, TITRE, fontsize=11, color='black', transform=axes[0].transAxes)

            axes[2].text(0.01, 0.7, f'Family:{family}', fontsize=12)
            axes[2].text(0.42, 0.7, f'{variable_name} {units}', fontsize=12)
            axes[2].text(0.85, 0.7, f'Region:{region}', fontsize=12)
            
            legendlist = ['μ', 'σ']
            l2 = ax1.legend(legendlist, columnspacing=1, fancybox=True, ncol=2, shadow=False, loc=(0.80, +1.030))
           # [h.set_color('black') for h in l2.legendHandles]

            legendlist2 = ['Nobs', 'Nrej']
            l3 = ax2.legend(legendlist2, columnspacing=1, fancybox=True, ncol=2, shadow=False, loc=(0.80, +1.030))
         #   [h.set_color('black') for h in l3.legendHandles]

            for i, (station, color) in enumerate(legend_items):
                axes[2].text(0.01 + (i % 4) * 0.24, 0.02 + (i // 4) * 0.2,
                             f'{station}', fontsize=11, color=color)
            
            fig.savefig(f'{pathwork}/{family}/timeserie_{region}_{datestart}_{dateend}_{fonction}_allid_stn_varno_{varno}_{names[filenumb]}.png',
                        format='png', dpi=100, bbox_inches='tight')
            plt.close(fig)

def timeserie_plot(
    pathwork, datestart, dateend, fonction, flag_type, family,
    region, fig_title, vcoord, id_stn, varnos, files, names
    ):
    # Ajustes globales mpl
    mpl.style.use('classic')
    mpl.rcParams.update({
    'lines.linewidth': 1.0,
    'lines.dashed_pattern': [6, 6],
    'lines.dashdot_pattern': [3, 5, 1, 5],
    'lines.dotted_pattern': [1, 3],
    'lines.scale_dashes': False
    })
    
    if id_stn=='all_t':
      timeserie_plot_all_t(
    pathwork, datestart, dateend, fonction, flag_type, family,
    region, fig_title, vcoord, id_stn, varnos, files, names
     )
    else:   
       if isinstance(varnos, int):
           varnos = [varnos]
       
       def build_criteria(id_stn, vcoord):
           if id_stn == 'join' and vcoord == 'join':
               return ""
           elif id_stn == 'join':
               return f" and vcoord = {vcoord} "
           elif vcoord == 'join':
               return f" and id_stn = '{id_stn}' "
           else:
               return f" and vcoord = {vcoord} and id_stn = '{id_stn}' "
       
       for varno in varnos:
           FNAM, FNAMP, SUM, SUM2 = pikobs.type_boxes(fonction)
           couleurs = [plt.cm.Set1(i) for i in np.linspace(0, 1, 9)]
           couleurs[0]='blue'
           couleurs[1]='red'
           Misgv, MisgvN = -999., 0
           variable_name, units, vcoord_type = pikobs.type_varno(varno)
           try:
               vcoord = int(vcoord)
           except ValueError:
               pass
       
           famille = f'Family:{family} id_stn:{id_stn} Channel:{vcoord}'
           label = f'Region:{region}'
           vcoord_type_e = f'{variable_name} {units}'
           plt.close('all')
           fig = plt.figure(figsize=(14, 5))
           axes = [
               plt.axes([0.1, 0.58, 0.9, 0.35]),
               plt.axes([0.1, 0.21, 0.9, 0.25]),
               plt.axes([0.1, 0.01, 0.9, 0.15])
           ]
           for i, ax in enumerate(axes):
               ax.grid(True)
               if i == 0:
                   ax.xaxis.tick_bottom()
               else:
                   ax.xaxis.set_visible(i == 1)
                   ax.yaxis.set_visible(i == 1)
           axes[2].xaxis.set_visible(False)
           axes[2].yaxis.set_visible(False)
       
           TITRE = []
           for filenumb, file in enumerate(files):
               conn = sqlite3.connect(file)
               cursor = conn.cursor()
               cursor.execute("PRAGMA TEMP_STORE=memory")
               crite = build_criteria(id_stn, vcoord)
               query = f"""
                   SELECT DATE, varno, Nrej, Nacc,
                     SUM({SUM})/SUM(CAST(N AS FLOAT)) AVG,
                     SQRT(SUM({SUM2})/SUM(CAST(N AS FLOAT)) - SUM({SUM})/SUM(CAST(N AS FLOAT))*SUM({SUM})/SUM(CAST(N AS FLOAT))) STD,
                     SUM(sumstat)/SUM(CAST(N AS FLOAT)) BCORR,
                     count(flag)
                   FROM timeserie
                   WHERE varno='{varno}' {crite}
                   GROUP BY DATE;
               """
               cursor.execute(query)
               results = cursor.fetchall()
               if not results:
                   continue
       
               # Arrays numpy directos
               Dates2 = np.array([row[0] for row in results])
               Nrejets = np.array([row[2] for row in results], dtype=float)
               Bomp2   = np.array([row[4] for row in results], dtype=float)
               Somp2   = np.array([row[5] for row in results], dtype=float)
               Nomb2   = np.array([row[3] for row in results], dtype=float)
               bcorr   = np.array([row[6] for row in results], dtype=float)
               dates = [dateutil.parser.parse(s) for s in Dates2]
               debut, fin = dates[0], dates[-1]
               PERIODE = f' From {debut:%Y%m%d%H} to {fin:%Y%m%d%H}'
               TITRE.append(PERIODE)
               x = date2num(dates)
               # Máscaras compactas
               Bomp2_masked = np.ma.masked_where(Bomp2 <= Misgv, Bomp2)
               Somp2_masked = np.ma.masked_where(Somp2 <= Misgv, Somp2)
               NB_masked = np.ma.masked_where(Nomb2 <= MisgvN, Nomb2)
               SNrej_masked = np.ma.masked_where(Nrejets <= Misgv, Nrejets)
               Bcorr_masked = np.ma.masked_where(bcorr <= Misgv, bcorr)
               Bias, Sigma, Nomb = map(np.ma.compressed, [Bomp2_masked, Somp2_masked, NB_masked])
               xmi, xma = x[0], x[-1]
       
               # Primer plot
               ax1 = axes[0]
               ax1.set_xlim([xmi, xma])
               ax1.plot(x, Bomp2_masked, '--o', ms=3, color=couleurs[filenumb], lw=2)
               ax1.plot(x, Somp2_masked, '-*', ms=4, color=couleurs[filenumb], lw=2)
               if fonction in ('BIAS_CORR', 'OBS_ERROR'):
                   ax1.plot(x, Bcorr_masked, '-p', ms=4, color='g', lw=2)
               if fonction in ('NOBS', 'DENS'):
                   ax1.plot(x, NB_masked, drawstyle='steps', color='g')
               # X-Axis formatos solo una vez
               
               
               from matplotlib.dates import HourLocator
               from matplotlib.ticker import NullFormatter
               from matplotlib.dates import DayLocator, HourLocator, DateFormatter
               from matplotlib.ticker import NullFormatter
               
               # Locatorsdatestart, dateend,
   
               diff_days = (datetime.strptime(datestart, "%Y%m%d%H")-datetime.strptime(dateend, "%Y%m%d%H")).days
   
               interval = 2 if diff_days <= 30 else 4
               major_locator = DayLocator(interval=interval)                
               minor_locator = HourLocator(interval=6)      
               major_formatter = DateFormatter('%m%d')    
               
               for ax in [axes[0], axes[1]]:
                   ax.xaxis.set_major_locator(major_locator)
                   ax.xaxis.set_major_formatter(major_formatter)
               
                   ax.xaxis.set_minor_locator(minor_locator)
                   ax.xaxis.set_minor_formatter(NullFormatter())  
               
                   ax.grid(True, which='minor', axis='x')
               
                   ax.tick_params(axis='x', which='minor', bottom=True)
                   ax.tick_params(axis='x', which='major', bottom=True, labelsize=10)
                
   
               ax2 = axes[1]
               ax2.set_xlim([xmi, xma])
               ax2.plot(x, NB_masked, '-o', drawstyle='steps', ms=3, color=couleurs[filenumb], lw=2)
               ax2.plot(x, SNrej_masked, '--p', drawstyle='steps', ms=4, color=couleurs[filenumb], lw=2)
       
               # Estadísticas y anotaciones
               legendlist = ['μ', 'σ']
               if Nomb.size > 0:
                   Mu = np.sum(Bias * Nomb) / np.sum(Nomb)
                   Sx2 = (Sigma ** 2 + Bias ** 2) * Nomb
                   Sig = math.sqrt(np.sum(Sx2) / np.sum(Nomb) - Mu ** 2)
                   ax1.text(0.45, 1.12 + filenumb / 9., f'{fonction} μ:{custom_round(Mu)} σ:{custom_round(Sig)} Nobs:{int(np.sum(Nomb))}',
                            transform=ax1.transAxes, fontsize=11, va='top', color=couleurs[filenumb])
               # Leyendas y textos, manteniendo resultado
               ax1.text(.00, 1.040, names[0], fontsize=11, color=couleurs[0], transform=ax1.transAxes)
               ax1.text(.14, 1.040, TITRE[0], fontsize=11, color=couleurs[0], transform=ax1.transAxes)
               axes[2].text(.01, 0.24, famille, fontsize=12, color='black', transform=axes[2].transAxes)
               axes[2].text(.42, 0.24, vcoord_type_e, fontsize=12, color='black', transform=axes[2].transAxes)
               axes[2].text(.85, 0.24, label, fontsize=12, color='black', transform=axes[2].transAxes)
               l2 = ax1.legend(legendlist, columnspacing=1, fancybox=True, ncol=2, shadow=False, loc=(0.80, +1.030))
              # [h.set_color('black') for h in l2.legendHandles]
               legendlist2 = ['Nobs', 'Nrej']
               l3 = ax2.legend(legendlist2, columnspacing=1, fancybox=True, ncol=2, shadow=False, loc=(0.80, +1.030))
             #  [h.set_color('black') for h in l3.legendHandles]
               if filenumb == 1 and len(names) > 1:
                   ax1.text(.00, 1.030 + .056 * (filenumb + 1), names[1], fontsize=11, color=couleurs[filenumb], transform=ax1.transAxes)
                   try:
                      ax1.text(.14, 1.030 + .056 * (filenumb + 1), TITRE[1], fontsize=11, color=couleurs[filenumb], transform=ax1.transAxes)
                   except:  
                      ax1.text(.14, 1.030 + .056 * (filenumb + 1), TITRE[0], fontsize=11, color=couleurs[filenumb], transform=ax1.transAxes)
                
                      continue
                #   axes[2].text(.01, 0.016 + .30 * (filenumb + 1), famille, fontsize=12, color=couleurs[filenumb], transform=axes[2].transAxes)
                #   axes[2].text(.32, 0.016 + .30 * (filenumb + 1), vcoord_type_e, fontsize=12, color=couleurs[filenumb], transform=axes[2].transAxes)
                #   axes[2].text(.75, 0.016 + .30 * (filenumb + 1), label, fontsize=12, color=couleurs[filenumb], transform=axes[2].transAxes)
       fig.savefig(f'{pathwork}/{family}/timeserie_{region}_{datestart}_{dateend}_{fonction}_id_stn_{id_stn}_vcoord_{vcoord}_varno_{varno}.png',
                   format='png', dpi=100, bbox_inches='tight')
   

