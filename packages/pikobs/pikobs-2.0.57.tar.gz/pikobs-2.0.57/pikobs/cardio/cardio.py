"""
Generating Cardiograms for Radiance Assimilation Analysis
=========================================================

This script is designed to generate cardiograms that analyze the results of radiance assimilation. Below is a description of the generated graphs, their characteristics, and their importance in the context of data assimilation.

Cardiograms of Radiance Assimilation
-------------------------------------
The script generates four main types of cardiograms, each providing critical information to assess the performance of radiance assimilation.

.. image::  ../../../docs/source/_static/cardio.png
   :alt: code_quality

1. **Mean of Differences**
   This cardiogram shows the averages of the differences between observations and predictions (O-P) and, if available, the differences between observations and adjustments (O-A). It also includes bias corrections (Bcor) if present.
   **Importance:** Analyzing the averages of O-P and O-A helps identify and quantify any systematic bias in the assimilation process, which is crucial for improving the accuracy of prediction models.

2. **Standard Deviations of Differences**
   This cardiogram shows the standard deviations of the differences between observations and predictions (O-P) and, if available, the standard deviations of the differences between observations and adjustments (O-A).
   **Importance:** Standard deviations measure the dispersion of errors. Analyzing these deviations helps understand the variability and uncertainty in the predictions and adjustments made during radiance assimilation.

3. **Obsvalue of Data**
   This cardiogram shows the obsvalue in the assimilation process.
   **Importance:** Evaluating the obsvalue of accepted data is essential to understand the efficiency of the assimilation system and the quality of the data being used. A high number of accepted data points can indicate an efficient and reliable filtering process.

4. **Total Number of Processed Data (Data Processing Analysis)**
   This cardiogram shows the total number of processed data points (Ntot) during assimilation.
   **Importance:** The total number of processed data points provides an overview of the amount of information handled by the system. It is an indicator of the data volume and the system's capacity to process large datasets.


*******************************************************
Generate Cardiograms for Radiance Assimilation Analysis
*******************************************************

To start an interactive session for generating cardiograms, use the following qsub command:
::
    qsub -I -X -l select=4:ncpus=80:mpiprocs=80:ompthreads=1:mem=185gb -l place=scatter -l walltime=6:0:0

Generating Cardiograms
^^^^^^^^^^^^^^^^^^^^^^
To generate cardiograms using pikobs, use the following command format:
::

    python -c 'import pikobs; pikobs.cardio.arg_call()'\

         --path_experience  /home/sprj700/data_maestro/ppp6/maestro_archives/G2FC900V2E22/monitoring/banco/postalt/ \

         --experience_name     G2FC900V2E22               \

         --pathwork   to_amsua_qc          \

         --datestart  2022061400                \

         --dateend    2022062400                \

         --region     Monde                     \

         --family     ai            \

         --flags_criteria assimilee             \

         --id_stn     join     \

         --channel    all        \

         --plot_title Test                      \

         --n_cpu      40

Parameters Explanation
^^^^^^^^^^^^^^^^^^^^^^
- **path_experience:** Path to the directory where the experience data is stored.
- **experience_name:** Name of the specific experience.
- **pathwork:** Directory path indicating the working directory for the script.
- **datestart:** Start date and time of the assimilation process (format: YYYYMMDDHH).
- **dateend:** End date and time of the assimilation process (format: YYYYMMDDHH).
- **region:** Geographic region or area of interest for the assimilation analysis. (e.g., Monde, PoleNord, PoleSud, AmeriqueduNord, OuestAmeriqueduNord, AmeriqueDuNordPlus, ExtratropiquesNord, HemisphereNord, HemisphereSud, Asie, Europe, Mexique, Canada, BaieDhudson, Arctiquecanadien, EtatsUnis, Tropiques30, Tropiques, Australie, Pacifique and Atlantique)
- **family:** Family of observation (e.g., mwhs2, mwhs2_qc, to_amsua_qc, to_amsua, to_amsua_allsky, to_amsua_allsky_qc, to_amsub_qc, to_amsub, ssmis_qc, ssmis, iasi, iasi_qc, crisfsr1_qc, crisfsr2_qc, cris, atms_allsky, atms_qc and csr, csr_qc)
- **flags_criteria:** Specific flag criteria used during assimilation (e.g., all, assimilee, bgckalt, bgckalt_qc and postalt).
- **id_stn:** all or satellites IDs for which assimilation results are analyzed also join satellites (e.g., METOP-1, METOP-3). Modify as needed to specify particular satellites.
- **channel:** all or specific channels to analyze. Use 'all' to analyze all available channels. Modify as needed to specify particular channels of interest.
- **plot_title:** Title for the generated cardiogram.
- **n_cpu:** Number of CPU cores to be used for parallel processing. Adjust according to your system capabilities.

Additional Note
^^^^^^^^^^^^^^^
- Modify **--channel** and **--id_stn** parameters as needed to specify particular satellites and channels of interest.
- Ensure paths (**path_experience, pathwork**) are correctly set to point to your data directories.
- The script leverages parallel processing (**--n_cpu**) to optimize performance, adjust according to your system capabilities.
- The generated cardiograms provide comprehensive visual insights into the assimilation performance metrics across selected satellites, channels, and criteria.

""" 
#!/usr/bin/python3
import sqlite3
import pikobs
import re
import os
from  dask.distributed import Client
import numpy as np
import sqlite3
import os
import re
import sqlite3
from  datetime import datetime, timedelta


def create_serie_cardio(family, 
                        new_db_filename, 
                        existing_db_filename,
                        region_seleccionada,
                        selected_flags, 
                        id_stn,
                        channel, 
                        varnos):
    """

    Create a new SQLite database with a 'moyenne' table and populate it with data from an existing database.

    Args:

      new_db_filename (str): Filename of the new database to be created.
  
      existing_db_filename (str): Filename of the existing database to be attached.
  
      region_seleccionada (str): Region selection criteria.
   
      selected_flags (str): Selected flags criteria.
   
      FONCTION (float): Value for sum_fonction column.

    
    Returns:
    
      None
    
    """
 
    pattern = r'(\d{10})'
    match = re.search(pattern, existing_db_filename)

    if match:
        date = match.group(1)
       
    else:
        print("No 10 digits found in the string.")
    
    # Connect to the new database
    if id_stn[0]=='all':
      criteria_id_stn = '    '
    else:
       elemnts = [f"'{element}'" for element in id_stn]

       resultado = f"({','.join(elemnts)})"
       criteria_id_stn = f'   '
    if channel[0]=='all':
      criteria_vcoord = '    '
    else:
       resultado = f"({','.join(channel)})"
       criteria_vcoord = f'    '

    
    filename=f"file::memory:?cache=shared"
    new_db_conn = sqlite3.connect(filename, uri=True, isolation_level=None, timeout=999999)
    new_db_cursor = new_db_conn.cursor()

    FAM, VCOORD, VCOCRIT, STATB, element, VCOTYP = pikobs.family(family)
    if id_stn[0]!='all' and id_stn[0]!='join':
       id_stn[0]='all' 
    if varnos:
        element=",".join(varnos)
    if channel=='join':
        VCOORD='  vcoord '
    if channel[0]=='join' and  id_stn[0]=='all':
      group_channel = ' "join" as Chan,    '
      group_id_stn  = ' id_stn as id_stn '
      group_id_stn_vcoord = ' group by id_stn,varno'
    if channel[0]=='all' and  id_stn[0]=='join':
      group_channel = f' {VCOORD} as  Chan, '
      group_id_stn  = ' "join" as id_stn '
      group_id_stn_vcoord = f' group by {VCOORD},varno'
    if channel[0]=='all' and  id_stn[0]=='all':
      group_channel = f'  {VCOORD} as Chan,'
      group_id_stn  = ' id_stn as id_stn '
      group_id_stn_vcoord = f' group by id_stn, {VCOORD},varno'

    if channel[0]=='join' and  id_stn[0]=='join':
      group_channel = ' "join" as Chan, '
      group_id_stn  =  ' "join" as id_stn  '
      group_id_stn_vcoord = 'group by varno  '

    LAT1, LAT2, LON1, LON2 = pikobs.regions(region_seleccionada)
    LATLONCRIT = pikobs.generate_latlon_criteria(LAT1, LAT2, LON1, LON2)
    flag_criteria = pikobs.flag_criteria(selected_flags)

    # Attach the existing database
    new_db_cursor.execute(f"ATTACH DATABASE '{existing_db_filename}' AS db;")
    # load extension CMC 
    new_db_conn.enable_load_extension(True)
    extension_dir = f'{os.path.dirname(pikobs.__file__)}/extension/libudfsqlite-shared.so'
    new_db_conn.execute(f"SELECT load_extension('{extension_dir}')")
    # Create the 'moyenne' table in the new database if it doesn't exist
    new_db_cursor.execute("""
           CREATE TABLE IF NOT EXISTS serie_cardio ( 
            DATE INTEGER,
            Chan INTEGER,
            Nrej INTEGER,
            Nacc INTIGER,
            AvgOMP FLOAT, 
            AvgOMA FLOAT,
            StdOMP FLOAT,
            StdOMA FLOAT,
            NDATA  INTEGER,
            Nprofile INTEGER,
            AvgBCOR FLOAT,
            AvgOBS FLOAT,
            Ntot INTEGER,
            varno INTEGER,
            id_stn  TEXT
        );
    """)
    query=f"""INSERT INTO serie_cardio (

            DATE,
            Chan,
            Nrej,
            Nacc,
            AvgOMP, 
            AvgOMA,
            StdOMP,
            StdOMA,
            NDATA,
            Nprofile,
            AvgBCOR,
            AvgOBS,
            Ntot,
            varno,
            id_stn
        )
    
    
             SELECT 
                 isodatetime({date}) AS DATE,  
                 {group_channel}
                 SUM(flag & 512=512) AS Nrej,
                 SUM(flag & 4096=4096) AS Nacc,
                 ROUND(AVG(OMP), 4) AS AvgOMP,
                 ROUND(AVG(OMA), 4) AS AvgOMA,
                 ROUND(STDDEV(OMP), 4) AS StdOMP,
                 ROUND(STDDEV(OMA), 4) AS StdOMA,
                 SUM(OMP IS NOT NULL) AS NDATA,
                 COUNT(DISTINCT id_obs) AS Nprofils,
                 ROUND(AVG(BIAS_CORR), 4) AS AvgBCOR,
                 ROUND(AVG(OBSVALUE), 4) AS AvgOBS,
                 (SELECT COUNT(*) FROM header h2 WHERE h2.ID_STN = header.ID_STN) AS Ntot,
                 varno AS varno,
                 {group_id_stn}
                 
            FROM 
                 header
             NATURAL JOIN 
                 data
             WHERE 
                 varno IN ({element}) 
                 {criteria_id_stn}
                 {criteria_vcoord}
                 {flag_criteria}
                 {LATLONCRIT}
                 {VCOCRIT}
                {group_id_stn_vcoord};"""
    new_db_cursor.execute(query)
    # Commit changes and detach the existing database
    new_db_conn.commit()

    # Commit changes and detach the existing database
    new_db_cursor.execute("DETACH DATABASE db;")
    try:
         combine(new_db_filename, filename)
    except sqlite3.Error as error:
         print(f"Error while creating a single sqlite file:  {os.path.basename(filename)}", error)

    
    # Close the connections
    #anew_db_conn.close()


def combine(pathfileout, filememory):

    """ Creating a single sqlite file from multiple sqlite files
 
    args:
    ----------------

     pathfileout   : output averaging  sqlite file 
     filememory    : name of the sqlite file in memory to copy
   
    output:
    ----------------

    Nothing
     A sqlite file is made with all averaged volume scans
   
   """

    # write in output averaging  sqlite file
    conn_pathfileout = sqlite3.connect(pathfileout, uri=True, isolation_level=None, timeout=9999)

    conn_pathfileout.execute("""PRAGMA journal_mode=OFF;""")

    # off the journal
    create_table_if_not_exists( conn_pathfileout)
    conn_pathfileout.execute("""PRAGMA journal_mode=OFF;""")
    # SQLite continues without syncing as soon as it has handed data off to the operating system
    conn_pathfileout.execute("""PRAGMA synchronous=OFF;""")
    # Wait to read and write until the next process finishes
    # attach the sqlite file in memory for one PPI
    create_table_if_not_exists(conn_pathfileout)

    conn_pathfileout.execute("ATTACH DATABASE ? AS this_avg_db;", (filememory,))
    order_sql = """ INSERT INTO serie_cardio( DATE, Chan, Nrej, Nacc, AvgOMP, AvgOMA, StdOMP, StdOMA, NDATA, Nprofile, AvgBCOR, AvgOBS, Ntot, varno, id_stn
 

                )
                    SELECT
                    DATE, Chan, Nrej, Nacc, AvgOMP, AvgOMA, StdOMP, StdOMA, NDATA, Nprofile, AvgBCOR, AvgOBS, Ntot, varno, id_stn
 
                    FROM  this_avg_db.serie_cardio"""
    conn_pathfileout.execute(order_sql) 

    conn_pathfileout.commit()
    conn_pathfileout.execute(""" DETACH DATABASE this_avg_db """)

def create_table_if_not_exists(cursor):
    """
    Create the 'serie_cardio' table if it does not already exist.

    Args:
        cursor (sqlite3.Cursor): Database cursor for executing SQL queries.
    """
    query = """
           CREATE TABLE IF NOT EXISTS serie_cardio ( 
            DATE INTEGER,
            Chan INTEGER,
            Nrej INTEGER,
            Nacc INTIGER,
            AvgOMP FLOAT, 
            AvgOMA FLOAT,
            StdOMP FLOAT,
            StdOMA FLOAT,
            NDATA  INTEGER,
            Nprofile INTEGER,
            AvgBCOR FLOAT,
            AvgOBS FLOAT,
            Ntot INTEGER,
            varno INTEGER,
            id_stn  TEXT );
    """
    cursor.execute(query)


def create_data_list_cardio(datestart1, 
                            dateend1,
                            families,
                            pathin, 
                            pathwork,
                            flag_criteria,
                            id_stn,
                            channel,
                            regions,
                            varnos):
    
    data_list_cardio = []
    for family in families:
        for region in regions:
             # Convert datestart and dateend to datetime objects
             datestart = datetime.strptime(datestart1, '%Y%m%d%H')
             dateend = datetime.strptime(dateend1, '%Y%m%d%H')

             # Initialize the current_date to datestart
             current_date = datestart

             # Define a timedelta of 6 hours
             delta = timedelta(hours=6)
             FAM, VCOORD, VCOCRIT, STATB, element, VCOTYP = pikobs.family(family)

            #  print ("VCOORD", vcoord, element, type(element))
              # Iterate through the date range in 6-hour intervals
             while current_date <= dateend:
                 # Format the current date as a string
                 formatted_date = current_date.strftime('%Y%m%d%H')

                 # Build the file name using the date and family
                 filename = f'{formatted_date}_{family}'

                 file_path_name = f'{pathin}/{filename}'
                 conn = sqlite3.connect(file_path_name)
                 # Create a cursor to execute SQL queries
                 cursor = conn.cursor()

                 #  Create a new dictionary and append it to the list
                 data_dict = {'family': family,
                                   'filein': f'{pathin}/{filename}',
                                   'db_new': f'{pathwork}/{family}/cardio_{region}_{datestart1}_{dateend1}_{flag_criteria}_{family}.db',
                                   'region': region,
                                   'flag_criteria': flag_criteria,
                                   'varno':  varnos,
                                   'vcoord': channel,
                                   'id_stn': id_stn}
                 data_list_cardio.append(data_dict)
                 conn.close()

                 # Update the current_date in the loop by adding 6 hours
                 current_date += delta

    return data_list_cardio


def get_station_ids(cursor, id_stn):
    if id_stn[0] == 'all':
        cursor.execute("SELECT DISTINCT id_stn FROM serie_cardio;")
        return [item[0] for item in cursor.fetchall()]
    return np.array(id_stn)

def fetch_channels_and_varno(cursor, idstn, channel):
    criter = f'WHERE id_stn = "{idstn}"'
    if channel[0] == 'all':
        if idstn=='join':
           query = f"SELECT DISTINCT chan, varno FROM serie_cardio  ;"
        else:
           query = f"SELECT DISTINCT chan, varno FROM serie_cardio {criter} ;"       
        cursor.execute(query)
        return cursor.fetchall()
    else:
        channels_varno = []
        for chan in np.array(channel):
            if idstn=='join':
               query = f"SELECT DISTINCT 'join', varno FROM serie_cardio;"
            else:
               query = f"SELECT DISTINCT 'join', varno FROM serie_cardio;"        
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                channels_varno.append(result)
        return channels_varno

def create_data_list_plot(datestart1, dateend1, families, pathin, pathwork, flag_criteria, regions, id_stn, channel):
    data_list_plot = []
    for family in families:
        for region in regions: 
           filedb = f'{pathwork}/{family}/cardio_{region}_{datestart1}_{dateend1}_{flag_criteria}_{family}.db'
           try:
               with sqlite3.connect(filedb) as conn:
                   cursor = conn.cursor()
                   if id_stn[0]=='all':
                       id_stns = get_station_ids(cursor, id_stn)
                   elif id_stn[0]=='join':  
                       id_stns = ['join']
                   else:
                       id_stns=id_stn
                   for idstn in id_stns:
                       channels_varno = fetch_channels_and_varno(cursor, idstn, channel)
                       for chan, varno in channels_varno:
                           data_dict_plot = {
                               'id_stn': idstn,
                               'vcoord': chan,
                               'varno': varno,
                               'region':region,
                               'family':family,
                           }
                           data_list_plot.append(data_dict_plot)
           except sqlite3.Error as e:
               print(f"Database error: {e}")
           except Exception as e:
               print(f"Error: {e}")
    return data_list_plot

def make_cardio(path_experience_files,
                experience_names,      
                pathwork, 
                datestart,
                dateend,
                regions, 
                families, 
                flag_criteria, 
                id_stn,
                channel,
                plot_type,
                plot_title,
                n_cpu,
                varnos):
       
       for family in families:
           pikobs.delete_create_folder(pathwork, family) 

       data_list_cardio = create_data_list_cardio(datestart,
                                           dateend, 
                                           families, 
                                           path_experience_files, 
                                           pathwork,
                                           flag_criteria, 
                                           id_stn,
                                           channel,
                                           regions,
                                           varnos)

       import time
       import dask
       t0 = time.time()
       if n_cpu==1:
        print (f'in Serie: {len(data_list_cardio)} files for serie calculation')
        for  data_ in data_list_cardio:  
            create_serie_cardio(data_['family'], 
                                data_['db_new'], 
                                data_['filein'],
                                data_['region'],
                                data_['flag_criteria'],
                                data_['id_stn'],
                                data_['vcoord'],
                                data_['varno'])




       else:
        print (f'in Paralle: {len(data_list_cardio)} files for serie calculation')
        with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                           n_workers=n_cpu, 
                                           silence_logs=40) as client:
            delayed_funcs = [dask.delayed(create_serie_cardio)(data_['family'], 
                                              data_['db_new'], 
                                              data_['filein'],
                                              data_['region'],
                                              data_['flag_criteria'],
                                              data_['id_stn'],
                                              data_['vcoord'],
                                              data_['varno'])for data_ in data_list_cardio]
            results = dask.compute(*delayed_funcs)
        
       tn= time.time()
       print ('Total time serie calculation:', round(tn-t0,2) )  
       data_list_plot = create_data_list_plot(datestart,
                                    dateend, 
                                    families, 
                                    path_experience_files, 
                                    pathwork,
                                    flag_criteria, 
                                    regions,
                                    id_stn,
                                    channel)



       t0 = time.time()
       if len(data_list_plot)==0:
          raise ValueError('You must specify best selectoion od id_stn and channel plot==0')

       if n_cpu==1: 
          print (f'in Serie plots = {len(data_list_plot)}')
          for  data_ in data_list_plot:  
              pikobs.cardio_plot(pathwork,
                                 datestart,
                                 dateend,
                                 flag_criteria,
                                 data_['family'],
                                 plot_title,
                                 plot_type, 
                                 data_['vcoord'],
                                 data_['id_stn'], 
                                 data_['varno'],
                                 data_['region'])
       else:
          print (f'in Paralle = {len(data_list_plot)} plots')
          with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                           n_workers=n_cpu, 
                                           silence_logs=40) as client:
            delayed_funcs = [dask.delayed(pikobs.cardio_plot)(
                               pathwork,
                                 datestart,
                                 dateend,
                                 flag_criteria,
                                 data_['family'],
                                 plot_title,
                                 plot_type, 
                                 data_['vcoord'],
                                 data_['id_stn'], 
                                 data_['varno'],
                                 data_['region'])for data_ in data_list_plot]

            results = dask.compute(*delayed_funcs)
       tn= time.time()
       print ('Total time for plotting:',tn-t0 )  

 



def arg_call():
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--path_experience_files', default='undefined', type=str, help="Directory where input sqlite files are located")
    parser.add_argument('--experience_name', default='undefined', type=str, help="experience's name")
    parser.add_argument('--pathwork', default='undefined', type=str, help="Working directory")
    parser.add_argument('--datestart', default='undefined', type=str, help="Start date")
    parser.add_argument('--dateend', default='undefined', type=str, help="End date")
    parser.add_argument('--region', nargs="+", default='undefined', type=str, help="Region")
    parser.add_argument('--family', nargs="+", default='undefined', type=str, help="Family")
    parser.add_argument('--flags_criteria', default='undefined', type=str, help="Flags criteria")
    parser.add_argument('--id_stn',nargs="+", default='all', type=str, help="id_stn") 
    parser.add_argument('--channel',nargs="+",  default='all', type=str, help="channel") 
    parser.add_argument('--plot_type', default='wide', type=str, help="channel")
    parser.add_argument('--plot_title', default='plot', type=str, help="channel")
    parser.add_argument('--n_cpus', default=1, type=int, help="Number of cpus")
    parser.add_argument('--varnos', nargs="+", default='undefined', type=str, help="Function")
   
    args = parser.parse_args()
    print ( "Inputs in cardiogram calculation")
    print ("----------------------------------------")

    for arg in vars(args):
      
       print (f'--{arg} {getattr(args, arg)}')
    print ("----------------------------------------")
    # check if each argument is 'undefined'
    if args.path_experience_files == 'undefined':
        raise ValueError('You must specify --path_experience_files')
    if args.experience_name == 'undefined':      
        raise ValueError('You must specify -experience_name') 
    if args.varnos == 'undefined':
        args.varnos = []
    if args.pathwork  == 'undefined':
        raise ValueError('You must specify --pathwork')
    if args.datestart == 'undefined':
        raise ValueError('You must specify --datestart')
    if args.dateend == 'undefined':
        raise ValueError('You must specify --dateend')
    if args.region == 'undefined':
        raise ValueError('You must specify --region')
    if args.family == 'undefined':
        raise ValueError('You must specify --family')
    if args.flags_criteria == 'undefined':
        raise ValueError('You must specify --flags_criteria')
   # if args.fonction == 'undefined':
   #     raise ValueError('You must specify --fonction')

    #Call your function with the arguments
    sys.exit(make_cardio (args.path_experience_files,
                          args.experience_name,
                          args.pathwork,
                          args.datestart,
                          args.dateend,
                          args.region,
                          args.family,
                          args.flags_criteria,
                          args.id_stn,
                          args.channel,
                          args.plot_type,
                          args.plot_title,
                          args.n_cpus,
                          args.varnos))

