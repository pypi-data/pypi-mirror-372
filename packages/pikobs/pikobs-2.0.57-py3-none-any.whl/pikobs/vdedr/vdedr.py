#!/usr/bin/python3
"""

Generating Verification of Radiance 
===========================================

This script is designed to generate detailed charts that analyze **residual bias** and **raw bias** for each radiance channel of a specific satellite. These charts provide essential insights into the performance of the radiance verification system, helping assess the accuracy and consistency of satellite observations. 

**Purpose**: To evaluate the effectiveness of bias corrections and highlight systematic differences in radiance data across experiments or datasets.

Bias and Error Plots
====================

This module produces three key plots to analyze biases and errors in radiance data across datasets. The **radiance channels** serve as the y-axis in all plots, facilitating channel-wise comparison.

1. Bias Plot
------------
Compares the **residual bias** and **raw bias** between two datasets.

**Details**:

- **Residual bias**: The difference between the average OMP values (`AvgOMP`) of the two datasets.

- **Raw bias**: The difference between the bias-corrected OMP values of the two datasets.

**Axes**:

- **X-axis**: Bias values (residual and raw).

- **Y-axis**: Radiance channels shared by both datasets.

**Purpose**: This plot highlights differences in bias measurements for the radiance channels between datasets, aiding in the detection of performance variations.

   .. image:: ../../../docs/source/_static/vdedr1.png
      :alt: Bias Plot

2. Delta Error Plot
-------------------
Shows the percentage difference in (`Standard Deviation  OMP`) and number of observations (`Nobs`) between the two datasets.

**Details**:

- **% sigma:** Percentage difference in Standard Deviation OMP of the two datasets.

- **% Nobs:** Percentage difference in Nobs of the two datasets.

**Axes**:

- **X-axis**: Percentage differences in (`Standard Deviation  OMP`)  and  (`Nobs`).

- **Y-axis**: Radiance channels shared by both datasets.

**Purpose**: This plot evaluates relative changes in measurement errors and observation counts, providing insight into experimental variability.

   .. image:: ../../../docs/source/_static/vdedr2.png
      :alt: Delta Error Plot

3. Delta Error (OMA) Plot
-------------------------
Similar to the Delta Error Plot but focuses on **OMA** (observations minus analysis) instead of OMP.

**Details**:

- **% sigma:** Percentage difference in Standard Deviation OMA of the two datasets.

- **% Nobs:** Percentage difference in Nobs of the two datasets.



**Axes**:

- **X-axis**: Percentage differences in (`Standard Deviation  OMA`)  and  (`Nobs`).

- **Y-axis**: Radiance channels shared by both datasets.

**Purpose**: This plot assesses relative changes in OMA errors and observation counts, helping identify patterns specific to analysis deviations.

   .. image:: ../../../docs/source/_static/vdedr3.png
      :alt: Delta Error (OMA) Plot
*******************************************************
Generate Verification of Radiance 
*******************************************************

To start an interactive session for generating cardiograms, use the following qsub command:
::
    qsub -I -X -l select=4:ncpus=80:mpiprocs=80:ompthreads=1:mem=185gb -l place=scatter -l walltime=6:0:0

Generating Verification of Radiance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To generate cardiograms using pikobs, use the following command format:
::

   python -c 'import pikobs; pikobs.vdedr.arg_call()' \

         --path_control_files  /home/sprj700/data_maestro/ppp6/maestro_archives/G2FC900V2E22/monitoring/banco/postalt/ \

         --control_name  G2FC900V2E22 \

         --path_experience_files  /home/sprj700/data_maestro/ppp6/maestro_archives/G2FC900V2E22/monitoring/banco/postalt/ \

         --experience_name  G2FC900V2E33 \

         --pathwork   work_to_amsua_allsky \

         --datestart  2022061500 \

         --dateend    2022061700 \

         --region     Monde \

         --family     cris to_amsua_allsky \

         --flags_criteria assimilee \

         --id_stn     all \

         --n_cpu      40

Parameter Explanation
^^^^^^^^^^^^^^^^^^^^^
- **path_control_files:** Path to the directory where the control data is stored.
- **control_name:**  Name of the specific control
- **path_experience_files:** Path to the directory where the experiment data is stored.
- **experience_name:**  Name of the specific experiment.
- **pathwork:**  Path to the working directory for the script.
- **datestart:**  Start date and time of the analysis (format: YYYYMMDDHH).
- **dateend:**  End date and time of the analysis (format: YYYYMMDDHH).
- **region:**  Geographic region of interest (e.g., Global, Northern Hemisphere, Southern Hemisphere).
- **family:**  Family of observation (e.g., mwhs2, mwhs2_qc, to_amsua_qc, to_amsua, to_amsua_allsky, to_amsua_allsky_qc, to_amsub_qc, to_amsub, ssmis_qc, ssmis, iasi, iasi_qc, crisfsr1_qc, crisfsr2_qc, cris, atms_allsky, atms_qc and csr, csr_qc)
- **id_stn:**  Name of the satellite for whichis analyzed (e.g., METOP-1, NOAA-20, all).
- **n_cpu:**   Number of CPU cores to use for parallel processing.


"""




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
import os
import sqlite3
import re

def create_table_if_not_exists(cursor):
    """
    """
    query = """
        CREATE TABLE IF NOT EXISTS serie_vdedr(
            DATE INTEGER,
            vcoord FLOAT,
            Ntot FLOAT,
            AvgOMP FLOAT,
            AvgOMA FLOAT,
            StdOMP FLOAT,
            StdOMA FLOAT,
            varno INTEGER,
            AvgBCOR INTEGER,
            id_stn TEXT
        );
    """
    cursor.execute(query)

import sqlite3
import os
import re
import pikobs


def create_serie_cardio(family, 
                        new_db_filename, 
                        existing_db_filename,
                        region_selected,
                        selected_flags, 
                        id_stn,
                        varno):
    """
    Create and populate a new SQLite database with processed data from an existing database.

    Args:
        family (str): Data family name.
        new_db_filename (str): Output SQLite database file name.
        existing_db_filename (str): Input SQLite database file name.
        region_selected (str): Region selection criteria.
        selected_flags (str): Flag filtering criteria.
        id_stn (str): Station ID or 'all' for all stations.
        varno (int): Variable number for filtering.

    Returns:
        None
    """
    # Extract date from the input database filename
    date_pattern = r'(\d{10})'
    date_match = re.search(date_pattern, existing_db_filename)
    date = date_match.group(1) if date_match else None
    if not date:
        print(f"Error: No valid date found in filename {existing_db_filename}.")
        return

    # Load family and region metadata
    FAM, VCOORD, VCOCRIT, STATB, VCOORD, VCOTYP = pikobs.family(family)
    LAT1, LAT2, LON1, LON2 = pikobs.regions(region_selected)
    LATLONCRIT = pikobs.generate_latlon_criteria(LAT1, LAT2, LON1, LON2)
    flag_criteria = pikobs.flag_criteria(selected_flags)
    criteria_id_stn = f"AND id_stn='{id_stn}'" if id_stn != 'all' else ''
    import random

    # Generar un número entero de 16 bits sin signo
    num_16bit_unsigned = random.randint(0, 2**16 - 1)
    filename=f'{os.path.basename(existing_db_filename)}?mode=memory&cache=shared'
    filename=f"file::memory:?cache=shared"

  


    # Open connection to the new database
    with sqlite3.connect(filename, uri=True, check_same_thread=False) as new_db_conn: 
    #conn_pathfileout = sqlite3.connect(pathfileout, uri=True, isolation_level=None, timeout=9999)


        new_db_cursor = new_db_conn.cursor()

        # Apply performance optimizations
        new_db_cursor.execute("PRAGMA journal_mode = WAL;")
        new_db_cursor.execute("PRAGMA synchronous = OFF;")
        new_db_cursor.execute("PRAGMA cache_size = -100000;")  # 100 MB

        # Create table if it does not exist
        create_table_if_not_exists(new_db_cursor)

        # Load SQLite extension
        extension_dir = os.path.join(os.path.dirname(pikobs.__file__), "extension/libudfsqlite-shared.so")
        new_db_conn.enable_load_extension(True)
        new_db_conn.execute(f"SELECT load_extension('{extension_dir}')")

        # Attach the existing database
        try:
            new_db_cursor.execute(f"ATTACH DATABASE '{existing_db_filename}' AS db;")
        except sqlite3.Error as e:
            print(f"Error attaching database: {e}")
            return

        # Execute the SQL query within a transaction
        try:
            new_db_cursor.execute("BEGIN TRANSACTION;")
            query = f"""
                INSERT INTO serie_vdedr(
                    DATE, vcoord, Ntot, AvgOMP, AvgOMA, StdOMP, StdOMA, AvgBCOR, varno, id_stn
                )
                SELECT 
                    {date},
                    vcoord,
                    COUNT(*) AS Ntot,
                    SUM(omp * 1.0) / COUNT(*) AS AvgOMP,
                    SUM(oma * 1.0) / COUNT(*) AS AvgOMA,
                    STDDEV(omp) AS StdOMP,
                    STDDEV(oma) AS StdOMA,
                    AVG(BIAS_CORR) AS AvgBCOR,
                    varno,
                    id_stn
                FROM
                    db.header
                NATURAL JOIN 
                    db.data
                WHERE 
                    VARNO = {int(varno)}
                    AND obsvalue IS NOT NULL
                    {criteria_id_stn}
                    {flag_criteria}
                    {LATLONCRIT}
                    {VCOCRIT}
                GROUP BY 
                    vcoord, id_stn;
            """
            
            new_db_cursor.execute(query)
            new_db_conn.commit()  # Commit transaction
        except sqlite3.Error as e:
            new_db_conn.rollback()  # Rollback transaction on error
            print(f"Error executing SQL query: {e} {filename} ")
        try:
        
            combine(new_db_filename, filename)
        except sqlite3.Error as error:
            print(f"Error while creating a single sqlite file:  {os.path.basename(filename)}", error)

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
    order_sql = """ INSERT INTO serie_vdedr(
                    DATE, vcoord, Ntot, AvgOMP, AvgOMA, StdOMP, StdOMA, AvgBCOR, varno, id_stn
                )
                    SELECT
                    DATE, vcoord, Ntot, AvgOMP, AvgOMA, StdOMP, StdOMA, AvgBCOR, varno, id_stn
                    FROM  this_avg_db.serie_vdedr"""
    conn_pathfileout.execute(order_sql) 

    conn_pathfileout.commit()
    conn_pathfileout.execute(""" DETACH DATABASE this_avg_db """)

def create_data_list_cardio(datestart1, 
                            dateend1,
                            families,
                            pathin, 
                            names,
                            pathwork,
                            flag_criteria,
                            regions,
                            id_stn):
    """
    Generate a list of dictionaries containing metadata for processing files 
    within a specified date range and conditions.

    Args:
        datestart1 (str): Start date in the format 'YYYYMMDDHH'.
        dateend1 (str): End date in the format 'YYYYMMDDHH'.
        families (list): List of family names.
        pathin (list): List of input directory paths corresponding to family names.
        names (list): List of names associated with each family.
        pathwork (str): Path for output files.
        flag_criteria (str): Criteria for filtering flags.
        regions (list): List of regions to process.
        id_stn (list): List of station IDs to include, or 'all' for all stations.

    Returns:
        list: A list of dictionaries containing metadata for processing.
    """
    data_list_cardio = []
    # Iterate over input paths and corresponding family names
    for path, name in zip(pathin, names):
        for region in regions:
            for family in families:
                # Convert start and end dates to datetime objects
                datestart = datetime.strptime(datestart1, '%Y%m%d%H')
                dateend = datetime.strptime(dateend1, '%Y%m%d%H')
                current_date = datestart
                delta = timedelta(hours=6)

                # Retrieve family metadata
                FAM, VCOORD, VCOCRIT, STATB, element, VCOTYP = pikobs.family(family)
                element_array = np.array([float(x) for x in element.split(',')])

                # Loop over variables in the family
                for varno in element_array:
                    # Loop through the date range in 6-hour intervals
                    while current_date <= dateend:
                        formatted_date = current_date.strftime('%Y%m%d%H')
                        filename = f'{formatted_date}_{family}'
                        file_path_name = f'{path}/{filename}'

                        # Connect to the database (ensures file existence)
                        try:
                            conn = sqlite3.connect(file_path_name)
                            conn.close()
                        except sqlite3.Error:
                            print(f"Warning: Unable to open file {file_path_name}. Skipping.")
                            current_date += delta
                            continue

                        # Generate data dictionaries
                        channel = 'all'
                        for station in id_stn:
                            data_dict = {
                                'family': family,
                                'filein': file_path_name,
                                'db_new': f'{pathwork}/{family}/vdedr_{region}_{name}_{datestart1}_{dateend1}_{flag_criteria}_{family}.db',
                                'region': region,
                                'flag_criteria': flag_criteria,
                                'varno': varno,
                                'vcoord': channel,
                                'id_stn': station
                            }
                            data_list_cardio.append(data_dict)

                        # Increment the date by 6 hours
                        current_date += delta

    return data_list_cardio

def create_data_list_plot(datestart1,
                          dateend1, 
                          families, 
                          pathwork, 
                          flag_criteria, 
                          regions, 
                          id_s,  
                          channels, 
                          files_in,
                          names_in): 
    """
    Generate a list of dictionaries containing metadata for plotting based on input parameters.

    Args:
        datestart1 (str): Start date in the format 'YYYYMMDDHH'.
        dateend1 (str): End date in the format 'YYYYMMDDHH'.
        families (list): List of family names.
        pathwork (str): Path to the working directory.
        flag_criteria (str): Criteria for filtering flags.
        regions (list): List of selected regions for filtering data.
        id_stns (list): List of station IDs or 'all' to include all stations.
        channels (list): List of channels for processing.
        files_in (list): List of input file names.
        names_in (list): List of names associated with databases (e.g., control, experimental).

    Returns:
        list: A list of dictionaries containing metadata for plotting.
    """
    data_list_plot = []

    # Loop over regions
    for region in regions:
        # Loop over families
        for family in families:
            # Define database paths for control and experimental groups
            filedb_control = f'{pathwork}/{family}/vdedr_{region}_{names_in[0]}_{datestart1}_{dateend1}_{flag_criteria}_{family}.db'
            filedb_experience = f'{pathwork}/{family}/vdedr_{region}_{names_in[1]}_{datestart1}_{dateend1}_{flag_criteria}_{family}.db'
            # Connect to the control database
            conn = sqlite3.connect(filedb_control)
            cursor = conn.cursor()
            # Determine station IDs and variables based on input criteria
            if id_s[0] == 'all':

                # Fetch all distinct station IDs and variables
                query = "SELECT DISTINCT id_stn, varno FROM serie_vdedr;"
                cursor.execute(query)
                id_stns = cursor.fetchall()
            else:
                # Fetch specific station IDs and variables
                stn_str = f"({', '.join(repr(stn) for stn in id_stns)})"
                query = f"SELECT DISTINCT id_stn, varno FROM serie_vdedr WHERE id_stn IN {stn_str};"
                cursor.execute(query)
                id_stns = cursor.fetchall()

            # Generate data dictionaries for each station ID and variable
            for id_stn, varno in id_stns:
                data_dict_plot = {
                    'files_in': [filedb_control, filedb_experience],
                    'names_in': names_in,
                    'id_stn': id_stn,
                    'family': family,
                    'region': region,
                    'varno': varno
                }
                data_list_plot.append(data_dict_plot)

            # Close the database connection
            conn.close()

    return data_list_plot

def make_cardio( files_in,
                 names_in,
                 pathwork, 
                 datestart,
                 dateend,
                 regions, 
                 families, 
                 flag_criteria, 
                 id_stns,
                 channels,
                 n_cpu):

   for family in families:
       pikobs.delete_create_folder(pathwork, family) 
   
   data_list_cardio = create_data_list_cardio(datestart,
                                           dateend, 
                                           families, 
                                           files_in,
                                           names_in,
                                           pathwork,
                                           flag_criteria, 
                                           regions,
                                           id_stns)
   import time 
   import dask
   t0 = time.time()
 #  n_cpu=1
   if n_cpu==1:
       print (f"in Serie: {filein} files for serie calculation")
       for  data_ in data_list_cardio:  
           create_serie_cardio(data_['family'], 
                                data_['db_new'], 
                                data_['filein'],
                                data_['region'],
                                data_['flag_criteria'],
                                data_['id_stn'],
                                data_['varno'])
    
    
    
   else:
        print (f"in Paralle: {len(data_list_cardio)} files for serie calculation")
        with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                           n_workers=n_cpu, 
                                           silence_logs=40) as client:
            delayed_funcs = [dask.delayed(create_serie_cardio)(data_['family'], 
                                              data_['db_new'], 
                                              data_['filein'],
                                              data_['region'],
                                              data_['flag_criteria'],
                                              data_['id_stn'],
                                              data_['varno'])for data_ in data_list_cardio]
            results = dask.compute(*delayed_funcs)
        
   tn= time.time()
   print (f'Total time for serie calculation:', round(tn-t0,2) ) 
   data_list_plot = create_data_list_plot(datestart,
                                dateend, 
                                families, 
                                pathwork,
                                flag_criteria, 
                                regions,
                                id_stns,
                                channels,
                                files_in,
                                names_in)


   
   t0= time.time()
   mode='bias'
   if n_cpu==1: 
      print (f'in Serie plots = {len(data_list_plot)*3} ')
      for  data_ in data_list_plot:  
          pikobs.vdedr_plot(pathwork,
                            datestart,
                            dateend,
                            flag_criteria,
                            data_['family'],
                            data_['region'],
                            data_['files_in'],
                            data_['names_in'],
                            data_['id_stn'], 
                            data_['varno'],
                            mode)
   else:
      print (f'in Paralle = {len(data_list_plot)*3} plots')
      with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                       n_workers=n_cpu, 
                                       silence_logs=40) as client:
        delayed_funcs = [dask.delayed(pikobs.vdedr_plot)(
                           pathwork,
                            datestart,
                            dateend,
                            flag_criteria,
                            data_['family'],
                            data_['region'],
                            data_['files_in'],
                            data_['names_in'],
                            data_['id_stn'], 
                            data_['varno'],
                            mode) for data_ in data_list_plot]

        results = dask.compute(*delayed_funcs)
   tn = time.time()
   print ('Total time for plotting =',round(tn-t0,2) ) 

 



def arg_call():
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_control_files', default='undefined', type=str, help="Directory where input sqlite files are located")
    parser.add_argument('--control_name', default='undefined', type=str, help="Directory where input sqlite files are located")
    parser.add_argument('--path_experience_files', default='undefined', type=str, help="Directory where input sqlite files are located")
    parser.add_argument('--experience_name', default='undefined', type=str, help="Directory where input sqlite files are located")
    parser.add_argument('--pathwork', default='undefined', type=str, help="Working directory")
    parser.add_argument('--datestart', default='undefined', type=str, help="Start date")
    parser.add_argument('--dateend', default='undefined', type=str, help="End date")
    parser.add_argument('--region', nargs="+", default='undefined', type=str, help="Region")
    parser.add_argument('--family', nargs="+",default='undefined', type=str, help="Family")
    parser.add_argument('--flags_criteria', default='undefined', type=str, help="Flags criteria")
    parser.add_argument('--id_stn', nargs="+",  default='all', type=str, help="id_stn") 
    parser.add_argument('--channel', nargs="+", default='all', type=str, help="channel") 
    parser.add_argument('--n_cpus', default=1, type=int, help="Number of CPUs")

    args = parser.parse_args()
    for arg in vars(args):
       print (f'--{arg} {getattr(args, arg)}')
    # Check if each argument is 'undefined'
    if args.path_control_files == 'undefined':
        raise ValueError('You must specify --path_control_files')
    elif args.control_name == 'undefined':
        raise ValueError('You must specify --control_name')
    else:    
      
      if args.path_experience_files == 'undefined':
          raise ValueError('You must specify --path_experience_files')
      if args.experience_name == 'undefined':
          raise ValueError('You must specify --experience_name')
      else:

          files_in = [args.path_control_files, args.path_experience_files]
          names_in = [args.control_name, args.experience_name]

    if args.pathwork == 'undefined':
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


    # Comment
    # Proj='cyl' // Proj=='OrthoN'// Proj=='OrthoS'// Proj=='robinson' // Proj=='Europe' // Proj=='Canada' // Proj=='AmeriqueNord' // Proj=='Npolar' //  Proj=='Spolar' // Proj == 'reg'
  

    #print("in")
    # Call your function with the arguments
    sys.exit(make_cardio (files_in,
                          names_in,
                          args.pathwork,
                          args.datestart,
                          args.dateend,
                          args.region,
                          args.family,
                          args.flags_criteria,
                          args.id_stn,
                          args.channel,
                          args.n_cpus))

if __name__ == '__main__':
    args = arg_call()




