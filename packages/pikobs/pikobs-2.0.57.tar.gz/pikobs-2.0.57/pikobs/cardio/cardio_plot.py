#!/usr/bin/python3
import numpy as np
import sys
import csv
import dateutil
import string
import math
import matplotlib as mpl
mpl.use('Agg')
import pylab as plt
import sqlite3
from matplotlib import ticker, font_manager, dates
import matplotlib
from datetime import date
import pikobs
# -----------------------------------------------------------------------------------------------------------------
# VERSION 2:  Added  ${qc_flags} argument.
#             Allow for plots with missing O-A (monitoring, bgckalt) and missing BCor
# -----------------------------------------------------------------------------------------------------------------

# USAGE:                        1         2          3         4         5
# > satellite_cardio_plot.py ${file}  ${channel}  ${TITLE}  ${type}  ${qc_flags}

# channel = "10"              plot channel 10 out of multiple channels in file
#         = "0"               single channel or channels combined  (channel numbers are NOT in file)
#                             (Channel info will be in TITLE)

# e.g. > satellite_cardio_plot_v2.py /data/cmda/afsd/abe/sortir_les_resultats/cardiogrammes/burp2rdb_plots_v2/G2_50BE14AB4/serie_ssmis_Monde_G2_50BE14AB4_DMSP16 '12' 'G2_50BE14AB4  Monde  DMSP16-ssmis Ch.12' wide assimilee


# Process arguments (into strings)
def cardio_plot(pathwork,datestart, dateend, flag_type, family, fig_title, plot_type, channel, id_stn, varno, region):
  
 # print ('PINTAR')
  LARG=[]
  matplotlib.pyplot.close()
  GREEN='#009900'
  BLUE='#0276FD'
  BLACK='#000000'
  RED='#D00000'
  
  MISSING=-99.9
  
 # print (' LARG=',LARG)
  

  #datfile   = LARG[1]
 # channel   = LARG[2]
  #ichannel = int(channel)
  #fig_title = LARG[3]
  #plot_type = LARG[4]  #  classic or wide
  #flag_type = LARG[5]  #  monitoring bgckalt postalt assimilee all
  

  if plot_type == 'classic':
    #            w    h  (inches)
    fig_size = (8.5,11.0)
  elif plot_type == 'wide':
    fig_size = (15.0,10.0)
  else:
    print ("Invalid plot type =",plot_type)
    sys.exit()
  
  if flag_type == 'monitoring' or flag_type == 'bgckalt' or flag_type == 'bgckalt_qc':
    is_oma = False
  else:
    is_oma = True
  
  
  #                 Input CSV file with stats results grouped by channel
  #
  #       0             1    2    3     4      5      6       7     8      9       10     11       12
  #   DATE            ,Chan,Nrej,Nacc,AvgOMP,AvgOMA,StdOMP,StdOMA,NDATA,Nprofils,AvgBCOR,AvgOBS,  Ntot
  #2011-01-24 00:00:00, 12,  0,  381, 0.5461, 0.298,2.1832,1.2944,381,  381,     0.1669, 133.186, 1621
  #2011-01-24 00:00:00 ,13,  0,  396, 0.208, 0.0207,1.3537,0.7966,396,  396,    -3.0804,195.3015, 1621
  #.....
  #         Input file with stats results NOT grouped by channel (channel combination)
  #
  #       0               1     2    3      4      5      6      7     8         9       10     12
  #   DATE            , Nrej,Nacc,AvgOMP,AvgOMA,StdOMP,StdOMA,NDATA,Nprofils, AvgBCOR,AvgOBS,  Ntot
  #2011-01-24 00:00:00,  0,  381, 0.5461, 0.298,2.1832,1.2944,381,   381,     0.1669, 133.186, 1621
  #2011-01-24 06:00:00,  0,4105,  0.5088,0.3161,2.2415,1.2529,4105, 4105,     0.2958,134.2117, 18279
  #.....
  
  # Ntot = number of data locations in HEADER of SQLite rdb file
  
  
  # Set timer on and pragma TEMP_STORE=memory
  path_output_work=f'{pathwork}/{family}/cardio_{region}_{datestart}_{dateend}_{flag_type}_{family}.db'
 # print (path_output_work) 
  conn = sqlite3.connect(path_output_work)
  # Create a cursor to execute SQL queries
  #FNAM, FNAMP, SUM, SUM2 = pikobs.type_boxes(fonction)
  cursor = conn.cursor()

  cursor.execute("PRAGMA TEMP_STORE=memory")
  critery_stn=f"AND id_stn='{id_stn}'"
  critery_chan=f"and Chan='{channel}'"

  if id_stn=='join':
       critery_stn=' '
  if channel=='join':
       critery_channel=' '
  query = f"""
           SELECT
                DATE,  
                Chan,
                Nrej,
                Nacc,
                AvgOMA,
                AvgOMP,
                StdOMA,
                StdOMP,
                AvgOBS,
                NDATA,
                Nprofile,
                Ntot,
                AvgBCOR
            FROM
               serie_cardio
            WHERE
                varno='{varno}'
                {critery_stn}
                {critery_chan}
                 
            GROUP BY
                DATE;"""
  cursor.execute(query)
  results = cursor.fetchall() 
  Dates  = np.array([row[0] for row in results])  #Dates
  Chans   = np.array([row[1] for row in results])  #Chans
  aoma    = np.array([row[4] for row in results])  #AvgOMA
  aomp    = np.array([row[5] for row in results])  #AvgOMP
  StdOMA  = np.array([row[6] for row in results])  #StdOMA
  StdOMP  = np.array([row[7] for row in results])  #StdOMP
  aobs    = np.array([row[8] for row in results])  #AvgOBS
  NDATA   = np.array([row[9] for row in results]) #NData
  Ntot    = np.array([row[11] for row in results]) #Ntot
  abcor   = np.array([row[12] for row in results]) #AvgBCOR
  #sys.exit()
  #print (Dates, Chans )
  #cursor.execute(". nullvalue -99.9")
#  exit()
#  sys.exit()
#  Dates=[]
#  Chans=[]
#  AvgOMP=[]
#  AvgOMA=[]
#  StdOMP=[]
#  StdOMA=[]
#  NData=[]
#  AvgBCOR=[]
#  AvgOBS=[]
  
  L1=[]  # List containing all rows (lists) of data read from csv file
  rownum1 = 0
  
  #----------------------------------------------------------------------
  # Read data from input CSV file
  #   row = list containing column data (as strings) for a row
  #----------------------------------------------------------------------
  
  #hdl1 = open (datfile,'r')                  # Open file for reading only
  #reader1 = csv.reader(hdl1,delimiter=",")   # Read file, skipping first (header) line
  #for row in reader1:
  #   if rownum1 != 0:
  #      if ichannel != 0:                    # Only select rows for specified channel!
  #         ichan = int(row[header.index("Chan")])
  #         if ichan == ichannel:
  #            L1.append( row )
  #      else:
  #         L1.append( row )
  #   else:
  #      header = row
  #      print ("Header from file =",header)
  #   rownum1 += 1
  
  #L1.sort(key=lambda tup: tup[0])
  
  # Extract the time series (columns) for plotting from data rows read
  # Convert the string values to appropriate data type
  
  #if "DATE" in header:
  #  Dates   = [da[header.index("DATE")] for da in L1]
  #  pdates  = [dateutil.parser.parse(s) for s in Dates]
  #else:
  #  print ("DATE not found in header!")
  #  sys.exit()
  #
  #if "AvgOMP" in header:
  #  AvgOMP  = [x[header.index("AvgOMP")]  for x in L1]

  #  AvgOMP  = [float(x) for x in AvgOMP]
  #  aomp    = np.array(AvgOMP)
  #else:/
  #  print ("AvgOMP not found in header!")
  #  sys.exit()
  # 
  #if "AvgOMA" in header:
  #  AvgOMA  = [x[header.index("AvgOMA")]  for x in L1]
  #  AvgOMA  = [float(x) for x in AvgOMA]
  #  aoma    = np.array(AvgOMA)
  #else:
  #  print ("AvgOMA not found in header!")
  #  sys.exit()
 # 
  #if "StdOMP" in header:
   # StdOMP  = [x[header.index("StdOMP")]  for x in L1]
  #  StdOMP  = [float(x) for x in StdOMP]
  #else:
  #  print ("StdOMP not found in header!")
 #   sys.exit()
  
 # if "StdOMA" in header:
 #   StdOMA  = [x[header.index("StdOMA")]  for x in L1]
 ##   StdOMA  = [float(x) for x in StdOMA]
 # else:
  #  print ("StdOMA not found in header!")
  #  sys.exit()
  
  #if "NDATA" in header:
  #  NData   = [x[header.index("NDATA")]   for x in L1]
  #  NData   = [int(x) for x in NData]
 # else:
 #   print ("NDATA not found in header!")
 #   sys.exit()
  
 # if "AvgBCOR" in header:
 #   AvgBCOR = [x[header.index("AvgBCOR")] for x in L1]
 #   AvgBCOR = [float(x) for x in AvgBCOR]
  #  abcor   = np.array(AvgBCOR)
 # else:
 #   print ("AvgBCOR not found in header!")
 #   sys.exit()
  
 # if "AvgOBS" in header:
  #  AvgOBS  = [x[header.index("AvgOBS")] for x in L1]
  #  AvgOBS  = [float(x) for x in AvgOBS]
  #  aobs    = np.array(AvgOBS)
  #else:
  #  print ("AvgOBS not found in header!")
  #  sys.exit()
  
  #if "Ntot" in header:
  #  Ntot   = [x[header.index("Ntot")]   for x in L1]
  #  Ntot   = [int(x) for x in Ntot]
  #else:
  #  print ("Ntot not found in header!")
  #  sys.exit()
  
 # if ichannel != 0:
  #  Chans  = [x[header.index("Chan")] for x in L1]  # list should contain selected channel number only
  #  Chans  = [int(x) for x in Chans]
  
  # Check if AvgOMA, StdOMA are missing (=MISSING)
  
  oma = list(set(aoma))
  if len(oma) == 1 and oma[0] == MISSING:
    if is_oma:
      print ("OMA data are missing! Aborting....")
      sys.exit()
    else:
      is_oma = False
  else:
    is_oma = True
  
  # Check if AvgBCOR are missing; if yes then set values to 0
  
  bc = list(set(abcor))
  is_bcor = True
  if len(bc) == 1 and bc[0] == MISSING:
    if flag_type != 'monitoring':
      print ("WARNING: AvgBCOR data are missing.")
    AvgBCOR[:] = 0.0
    abcor = np.array(AvgBCOR)
    is_bcor = False
  try:
     raw_omp = aomp - abcor
  except:
     raw_omp = aomp  
  try:
     raw_obs = aobs - abcor
  except:
     raw_obs = aobs 
  p = aobs - aomp
  if is_oma:
    a = aobs - aoma
  N  = NDATA
  NT = Ntot
  
  Bias1  = aomp
  Sigma1 = StdOMP
  Mu  = sum(Bias1*N)/sum(N)
  Sx2 = (Sigma1*Sigma1 +Bias1*Bias1)*N
  Sig = math.sqrt(sum(Sx2)/sum(N)  -Mu*Mu)
  Mean_OMP = Mu
  Mean_raw_OMP = sum(raw_omp*N)/sum(N)
  Std_OMP  = Sig
  STRING_OMP = 'O-P Mean: '+str(round(Mu,3)) + ' Sigma: '+str(round(Sig,3)) + ' Ndata: '+ str( int(sum(N)))
  
  if is_oma:
    Bias2  = aoma
    Sigma2 = StdOMA
    Mu  = sum(Bias2*N)/sum(N)
    Mean_OMA = Mu
    Sx2 = (Sigma2*Sigma2 +Bias2*Bias2)*N
    Sig = math.sqrt(sum(Sx2)/sum(N)  -Mu*Mu)
    Std_OMA  = Sig
    STRING_OMA = 'O-A Mean: '+str(round(Mu,3)) + ' Sigma: '+str(round(Sig,3)) + ' Ndata: '+ str( int(sum(N)))
  
  try:
    Avg_BCOR = sum(abcor*N)/sum(N)
  except:
    Avg_BCOR = 0
  Avg_N = float(sum(N))/len(N)
  Avg_NT = float(sum(NT))/len(NT)
  
  debut=Dates[0]
  fin  =Dates[-1]
  PERIODE='From ' + debut +'   to ' + fin
  TITLE=fig_title
  
  MEAN_TITLE1 = str('Mean(O-P) = '+str(round(Mean_OMP,3))) + '  Raw Mean(O-P) = '+str(round(Mean_raw_OMP,3)) # red
  if is_oma:
    MEAN_TITLE2 = str('Mean(O-A) = '+str(round(Mean_OMA,3)))  # blue
  else:
    MEAN_TITLE2 = ''
  if is_bcor:
    MEAN_TITLE3 = str('Mean(Bcor) = '+str(round(Avg_BCOR,3))) # green
  else:
    MEAN_TITLE3 = ''
  
  STD_TITLE1  = str('Std(O-P) = '+str(round(Std_OMP,3)))    # red
  if is_oma:
    STD_TITLE2  = str('Std(O-A) = '+str(round(Std_OMA,3)))    # blue
  else:
    STD_TITLE2  = ''
  
  #----------------------------------------------------------------------
  #  Plot Section:      4 plots on 1 page (fig) using plt.axes()
  #----------------------------------------------------------------------
  
  left = 0.1   # left margin
  width = 0.8  # width of the plots
  
  fp=font_manager.FontProperties(size='small')  # set font props for legends
  
  fig = plt.figure(figsize=fig_size,facecolor='white')
  
  p1_bottom = 0.73
  p2_bottom = 0.51
  p3_bottom = 0.29
  p4_bottom = 0.07
  height  = 0.18
  
  # Position the 4 plots on the page (figure)
  ax1 = plt.axes([left, p1_bottom, width, height])
  ax2 = plt.axes([left, p2_bottom, width, height])
  ax3 = plt.axes([left, p3_bottom, width, height])
  ax4 = plt.axes([left, p4_bottom, width, height])
  
  # hide grid lines
  ax1.grid(False)
  ax2.grid(False)
  ax3.grid(False)
  ax4.grid(False)
  
  # ticks
  #ax1.xaxis.tick_bottom()
  #ax2.xaxis.tick_bottom()
  #ax3.xaxis.tick_bottom()
  #ax4.xaxis.tick_bottom()
  
  # X-axis values (dates) for plots
  variable_name, unit, vcoord_type = pikobs.type_varno(f"{varno}")
  def format_date(x, pos=None):
      return plt.num2date(x).strftime('%b %d:%HZ')
  
  ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
  ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
  ax3.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
  ax4.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
  
  x = plt.date2num(Dates)
  xmi=x[0]
  xma=x[-1]
  #ax1.set_xlim([xmi, xma])
  #ax2.set_xlim([xmi, xma])
  #ax3.set_xlim([xmi, xma])
  #ax4.set_xlim([xmi, xma])
  ax1.plot(x, aomp, linestyle='-',  color=RED,lw=2,   label='O-P')
  ncols = 1
  if is_oma:
    ax1.plot(x, aoma, linestyle='-',  color=BLUE,lw=2,  label='O-A')
    ncols += 1
  if is_bcor:
    ax1.plot(x, abcor, linestyle='-', color=GREEN,lw=2, label='bcor')
    ax1.plot(x, raw_omp, linestyle=':',color=RED,lw=2,   label='(O-P)raw')
    ncols += 2
  ax1.set_xlim([xmi, xma])
  ax1.axhline(color='purple',lw=2)
  ax1.set_ylabel(f'Mean {unit}')
  #ax1.legend(loc=
  #  best          0
  #  upper right   1
  #  upper left    2
  #  lower left    3
  #  lower right   4
  ax1.legend(loc=2,ncol=ncols,prop=fp)
  ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator())
  ax1.xaxis.set_minor_locator(dates.DayLocator())
  ax1.yaxis.grid(True, which='major', linestyle='-', color='grey')
  ax1.yaxis.grid(True, which='minor', linestyle=':', color='grey')
  ax1.xaxis.grid(True, which='major', linestyle=':', color='grey')
  ax1.xaxis.grid(True, which='minor', linestyle=':', color='grey')
  ax1.text(0.0,  1.0, MEAN_TITLE1, horizontalalignment='left', verticalalignment='bottom', transform=ax1.transAxes, color=RED,fontsize=11)
  ax1.text(0.52, 1.0, MEAN_TITLE2, horizontalalignment='left', verticalalignment='bottom', transform=ax1.transAxes, color=BLUE, fontsize=11)
  ax1.text(0.77, 1.0, MEAN_TITLE3, horizontalalignment='left', verticalalignment='bottom', transform=ax1.transAxes, color=GREEN,fontsize=11)
  for label in ax1.get_xticklabels():
        label.set_fontsize(8)
   # extend y-axis range by 1 major tick interval so legend does not cover data plot
  yt=ax1.yaxis.get_majorticklocs() # numpy array with locations of y-ticks in y-axis units (with extra ticks at each end)
  ylims=ax1.get_ylim()
  if yt[-1] == ylims[1]:
    delt = yt[-1] - yt[-2]
    ylim2 = yt[-1] + delt
    ax1.set_ylim([ylims[0],ylim2])
  else:
    ax1.set_ylim([ylims[0],yt[-1]])
  
  ax2.plot(x, StdOMP, linestyle='-', color=RED,lw=2, label='O-P')
  ncols = 1
  if is_oma:
    ax2.plot(x, StdOMA, linestyle='-', color=BLUE,lw=2, label='O-A')
    ncols += 1
  ax2.set_xlim([xmi, xma])
  ylims = ax2.get_ylim()
  if is_oma:
    ax2.set_ylim([0,ylims[1]])
  ax2.set_ylabel(f'StdDev {unit}')
#  ax2.set_ylim(0, 5)
  ax2.legend(loc=3,ncol=ncols,prop=fp)
  ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator())
  ax2.xaxis.set_minor_locator(dates.DayLocator())
  ax2.yaxis.grid(True, which='major', linestyle='-', color='grey')
  ax2.yaxis.grid(True, which='minor', linestyle=':', color='grey')
  ax2.xaxis.grid(True, which='major', linestyle=':', color='grey')
  ax2.xaxis.grid(True, which='minor', linestyle=':', color='grey')
  ax2.text(0.0,   1.0, STD_TITLE1, horizontalalignment='left', verticalalignment='bottom', transform=ax2.transAxes, color=RED,fontsize=11)
  ax2.text(0.25,  1.0, STD_TITLE2, horizontalalignment='left', verticalalignment='bottom', transform=ax2.transAxes, color=BLUE, fontsize=11)
  for label in ax2.get_xticklabels():
        label.set_fontsize(8)
  
  ax3.plot(x, aobs, linestyle='-', color=BLACK, label='Obs')
  ncols = 1
  if is_bcor:
    ax3.plot(x, raw_obs, linestyle=':', color=BLACK, label='RawObs')
    ncols += 1
  ax3.plot(x, p, color=RED, label='Trial')
  ncols += 1
  if is_oma:
    ax3.plot(x, a, color=BLUE, label='Anal')
    ncols += 1
  ax3.set_xlim([xmi, xma])
  ax3.set_ylabel(f'{variable_name} {unit}')
  ax3.legend(loc=0,ncol=ncols,prop=fp)
  ax3.yaxis.set_minor_locator(ticker.AutoMinorLocator())
  ax3.xaxis.set_minor_locator(dates.DayLocator())
  ax3.xaxis.grid(True, which='major', linestyle=':', color='grey')
  ax3.xaxis.grid(True, which='minor', linestyle=':', color='grey')
  for label in ax3.get_xticklabels():
        label.set_fontsize(8)
  
  ax4.plot(x, NDATA, linestyle='-', color=BLACK, label='Ndata' )
  ax4.plot(x, Ntot,  linestyle=':', color=BLACK, label='Nlocs')
  ax4.set_xlim([xmi, xma])
  ylims = ax4.get_ylim()
  ax4.set_ylim([0,ylims[1]])
  ax4.set_ylabel('Number of Observations')
  ax4.legend(loc=0,ncol=2,prop=fp)
  ax4.yaxis.set_minor_locator(ticker.AutoMinorLocator())
  ax4.xaxis.set_minor_locator(dates.DayLocator())
  ax4.xaxis.grid(True, which='major', linestyle=':', color='grey')
  ax4.xaxis.grid(True, which='minor', linestyle=':', color='grey')
  for label in ax4.get_xticklabels():
        label.set_fontsize(8)
  title4="Average number of data = "+str(int(round(Avg_N)))+"  Avg Nlocs = "+str(int(round(Avg_NT)))
  ax4.set_title(title4)
  
  
  fig.autofmt_xdate()
  fig.suptitle(f'Experience:{TITLE} Satellite:{id_stn} channel:{channel} ({region})', fontsize=15, fontweight='bold')
  
  #plt.show()

  plt.savefig(f'{pathwork}/{family}/serie_{TITLE}_{family}_{id_stn}_id_stn_{region}_ch{channel}_varno{varno}.png',format='png',dpi=100)
  plt.close()
