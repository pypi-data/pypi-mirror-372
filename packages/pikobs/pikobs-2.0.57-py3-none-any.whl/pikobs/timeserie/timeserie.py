"""
pikobs.timeserie Module
=======================

The ``timeserie`` module within the ``pikobs`` package is designed for advanced time-series analysis of meteorological observations. It enables users to visualize and analyze both the **quantity** and **quality** of observations across customizable time periods, making it suitable for robust scientific and operational studies.

Main Features
-------------

- **Comprehensive Visualization:** Generate time-series plots for observation counts, bias, and standard deviation.
- **Flexible Grouping Options:** Analyze data per station, aggregated across all stations, or compare different configurations and satellites.

Example Visualizations
----------------------

- **Aggregated statistics for all stations in a single experience (id_stn=join):**

  .. image:: ../../../docs/source/_static/timeserie1.png

  Visualizes time-series data for the ensemble station across the entire experience.

- **Disaggregated station statistics (id_stn=all):**

  .. image:: ../../../docs/source/_static/timeserie2.png

  Displays individual station statistics for more granular comparison.

- **Fully aggregated view across an experience (id_stn=all , all-station aggregation):**

  .. image:: ../../../docs/source/_static/timeserie3.png

  Shows global statistics summarizing all stations within the experience.

Generated Graphs
----------------

1. **Bias and Standard Deviation**
   - **Bias:** Indicates persistent differences between observations and reference data, highlighting systematic errors.
   - **Standard Deviation:** Represents the variability of observations over time.

2. **Observation Count Over Time**
   - Illustrates the density and availability of observations, helping detect temporal gaps or inconsistencies.

Usage & Integration
-------------------

This module can be executed from the command line, allowing seamless integration into batch workflows. Below is an example Bash script:

.. code-block:: bash

   #!/bin/bash

   # Locate Python executable
   PYTHON_EXEC=$(which python)

   # Run the timeserie analysis
   $PYTHON_EXEC -c 'import pikobs; pikobs.timeserie.arg_call()' \

     --path_experience_files "/path/to/experience_files/" \
   
     --experience_name "ops+NOAA21+GOES19" \
     
     --path_control_files "/path/to/control_files/" \
     
     --control_name "ops" \
     
     --pathwork "onthefly2" \
     
     --datestart "2025041200" \
     
     --dateend "2025041300" \
     
     --region "Monde" \
     
     --family "sw" \
     
     --flags_criteria "assimilee" \
     
     --fonction "omp" \
     
     --id_stn "join" \
     
     --channel "join" \
     
     --n_cpu 40

Parameter Descriptions
----------------------

- **path_experience_files:** Directory containing experience data files.
- **experience_name:** Identifier for the specific experiment.
- **path_control_files:** Directory containing control/reference data.
- **control_name:** Identifier for the control/reference configuration.
- **pathwork:** Working directory where outputs and intermediates are stored.
- **datestart:** Start timestamp for the analysis period (format: YYYYMMDDHH).
- **dateend:** End timestamp for the analysis period (format: YYYYMMDDHH).
- **region:** Geographic area of interest. Valid values include:
  - Monde, PoleNord, PoleSud, AmeriqueduNord, OuestAmeriqueduNord, AmeriqueDuNordPlus, ExtratropiquesNord, HemisphereNord, HemisphereSud, Asie, Europe, Mexique, Canada, BaieDhudson, Arctiquecanadien, EtatsUnis, Tropiques30, Tropiques, Australie, Pacifique, Atlantique.
- **family:** Observation family (e.g., mwhs2, to_amsua, iasi_qc, atms_qc, csr_qc, etc.).
- **flags_criteria:** Filtering criterion (e.g., "assimilee").
- **fonction:** Computational function used (e.g., "omp").
- **id_stn:** Specifies stations or satellites to include (e.g., "all", "join", or specific satellite IDs like METOP-1).
- **channel:** Specifies channels to analyze ("all", "join", or specific channel numbers).
- **n_cpu:** Number of CPU cores to use for parallel processing.

Tip: Adjust the command-line arguments to match your data, region, and analysis goals.
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
from datetime import datetime, timedelta

def create_table_if_not_exists(cursor):
    """
    Create the 'serie_cardio' table if it does not already exist.

    Args:
        cursor (sqlite3.Cursor): Database cursor for executing SQL queries.
    """
    query = """
        CREATE TABLE IF NOT EXISTS timeserie (
              DATE INTEGER,
                varno INTEGER,
                Nrej INTEGER,
                Nacc INTEGER,
                SUMx FLOAT,
                SUMx2 FLOAT,
                SUMy FLOAT,
                SUMy2 FLOAT,
                SUMz FLOAT,
                SUMz2 FLOAT,
                sumStat FLOAT,
                sumStat2 FLOAT,
                N INTEGER,
                id_stn TEXT,
                vcoord FLOAT,
                flag INTEGER
        ); """
    cursor.execute(query)



def combine(pathfileout: str, filememory: str) -> None:
    """
    Combine multiple SQLite files into a single output file.

    This function copies records from the 'timeserie' table of a source SQLite file 
    (filememory) and inserts them into the 'timeserie' table of a destination/output SQLite file (pathfileout).
    
    Args:

        pathfileout (str): Path to the output SQLite file where combined data will be stored.
        filememory  (str): Path to the source SQLite file (can be memory or disk).
        
    Returns:
        None. The result is saved directly in the specified output file.
    """
    insert_sql = """
        INSERT INTO timeserie(
             DATE, varno, Nrej, Nacc, SUMx, SUMx2, SUMy, SUMy2, SUMz,SUMz2, sumStat,sumStat2,  N,id_stn, vcoord,flag
        )
        SELECT 
             DATE, varno, Nrej, Nacc, SUMx, SUMx2, SUMy, SUMy2, SUMz,SUMz2, sumStat,sumStat2,  N,id_stn, vcoord,flag
        FROM this_avg_db.timeserie
    """
    # Use 'with' statement to ensure connection is properly closed
    with sqlite3.connect(pathfileout, uri=True, isolation_level=None, timeout=9999) as conn:
        try:
            # Set performance-optimized PRAGMAs, provided your application allows for non-durable writes
            conn.execute("PRAGMA journal_mode=OFF;")
            conn.execute("PRAGMA synchronous=OFF;")

            # Ensure the table exists
            create_table_if_not_exists(conn)

            # Attach the source SQLite database
            conn.execute(f"ATTACH DATABASE '{filememory}' AS this_avg_db;")

            # Copy data
            conn.execute(insert_sql)
            conn.commit()

            # Detach the attached database
            conn.execute("DETACH DATABASE this_avg_db;")
        except sqlite3.Error as e:
            print(f"Error combining SQLite files: {e}")
            raise

def create_timeserie_table(
    family, 
    new_db_filename,
    existing_db_filename, 
    region_seleccionada, 
    selected_flags,
    varnos,
    channel,
    id_stn
):
    """
    Function to create a timeserie table in a SQLite database.
    
    Parameters:
    - family: Family identifier.
    - new_db_filename: File path for the new database.
    - existing_db_filename: File path for the existing database.
    - region_seleccionada: Selected region identifier.
    - selected_flags: Flag criteria for selection.
    - varnos: Variable numbers to consider.
    - channel: Channel information.
    - id_stn: Station identifier.
    """

    # Extract date from existing_db_filename
    pattern = r'(\d{10})'
    match = re.search(pattern, existing_db_filename)
    if not match:
        print("No 10 digits found in the filename.")
        return
    date = match.group(1)

    # Create a new temporary database for inspection
    in_memory_db = f"file::memory:?cache=shared"


    with sqlite3.connect(in_memory_db, uri=True, isolation_level=None, timeout=9999999) as new_db_conn:
        new_db_cursor = new_db_conn.cursor()

        # Attach existing database
        new_db_cursor.execute(f"ATTACH DATABASE '{existing_db_filename}' AS db;")
        # Check for required tables and columns
        tables_needed = ['header', 'DATA']
        for table in tables_needed:
            new_db_cursor.execute(f"PRAGMA table_info({table});")
            table_info = new_db_cursor.fetchall()
            if not table_info:
                raise sqlite3.Error(f"Table '{table}' is missing in the database.")

        new_db_conn.enable_load_extension(True)
        extension_dir = f"{os.path.dirname(pikobs.__file__)}/extension/libudfsqlite-shared.so"
        new_db_cursor.execute(f"SELECT load_extension('{extension_dir}')")

        # Configure performance settings
        pragmas = [
            "PRAGMA journal_mode = OFF",
            "PRAGMA synchronous = OFF",
            "PRAGMA foreign_keys = OFF"
        ]
        for pragma in pragmas:
            new_db_cursor.execute(pragma)

        # Collect criteria
        FAM, VCOORD, VCOCRIT, STATB, element, VCOTYP = pikobs.family(family)
        LAT1, LAT2, LON1, LON2 = pikobs.regions(region_seleccionada)
        LATLONCRIT = pikobs.generate_latlon_criteria(LAT1, LAT2, LON1, LON2)
        flag_criteria = pikobs.flag_criteria(selected_flags)

        if varnos:
            element = ",".join(varnos)

        group_conditions = {
            ('join', 'all'): ('"join" as Chan,', 'id_stn as id_stn,', 'group by date,id_stn,varno'),
            ('all', 'join'): (f'{VCOORD} as Chan,', '"join" as id_stn,', f'group by date,{VCOORD},varno'),
            ('all', 'all'): (f'{VCOORD} as Chan,', 'id_stn as id_stn,', f'group by date,id_stn,{VCOORD},varno'),
            ('join', 'join'): ('"join" as Chan,', '"join" as id_stn,', 'group by date,varno')}
        group_channel, group_id_stn, group_id_stn_vcoord = group_conditions.get(
            (channel, id_stn),
            ('', '', '')
        )

        # Check if 'bias_corr' exists
        new_db_cursor.execute("PRAGMA table_info('DATA')")
        columns = new_db_cursor.fetchall()
        bias_corr_exists = any(col[1] == 'bias_corr' for col in columns)

        bias_corr_sum = "sum(bias_corr)" if bias_corr_exists else "NULL"
        bias_corr_sq_sum = "sum(bias_corr * bias_corr)" if bias_corr_exists else "NULL"

        # Create the timeserie table
        new_db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeserie (
                DATE INTEGER,
                varno INTEGER,
                Nrej INTEGER,
                Nacc INTEGER,
                SUMx FLOAT,
                SUMx2 FLOAT,
                SUMy FLOAT,
                SUMy2 FLOAT,
                SUMz FLOAT,
                SUMz2 FLOAT,
                sumStat FLOAT,
                sumStat2 FLOAT,
                N INTEGER,
                id_stn TEXT,
                vcoord FLOAT,
                flag INTEGER
            );
        """)
        new_db_conn.commit()

        # Insert data into timeserie table
        query = f"""
        INSERT INTO timeserie (
            DATE, varno, Nrej, Nacc, SUMx, SUMx2, SUMy, SUMy2, SUMz, SUMz2,
            sumStat, sumStat2, N, id_stn, VCOORD, flag
        )
        SELECT
            isodatetime({date}) AS DATE,
            varno AS VARNO,
            count(*) - SUM(flag & 4096 = 4096) AS Nrej,
            SUM(flag & 4096 = 4096) AS Nacc,
            SUM(OMP) AS SUMx,
            SUM(OMP * OMP) AS SUMx2,
            SUM(OMA) AS SUMy,
            SUM(OMA * OMA) AS SUMy2,
            SUM(obsvalue) AS SUMz,
            {bias_corr_sum} AS sumStat,
            SUM(obsvalue * obsvalue) AS SUMz2,
            {bias_corr_sq_sum} AS sumStat2,
            count(*) AS N,
            {group_id_stn}
            {group_channel}
            flag AS flag
        FROM
            db.header
        NATURAL JOIN
            db.DATA
        WHERE 
            varno IN ({element}) AND
            obsvalue IS NOT NULL
            {flag_criteria}
            {LATLONCRIT}
        {group_id_stn_vcoord}
        """
        new_db_cursor.execute(query)
        new_db_conn.commit()

        # Finalize and inspect
        try:
            combine(new_db_filename, in_memory_db)
        except sqlite3.Error as error:
            print(f"Error when combining SQLite files: {error}")


def create_data_list(datestart1, dateend1, families, input_paths,names, pathwork, flag_criteria, regions, varnos):
    data_list = []

    
    # Convert datestart and dateend to datetime objects
    datestart = datetime.strptime(datestart1, '%Y%m%d%H')
    dateend = datetime.strptime(dateend1, '%Y%m%d%H')

    # Initialize the current_date to datestart
    current_date = datestart

    # Define a timedelta of 6 hours
    delta = timedelta(hours=6)
   # FAM, VCOORD, VCOCRIT, STATB, element, VCOTYP = pikobs.family(family)
    
    #flag_criteria = generate_flag_criteria(flag_criteria)

    #element_array = np.array([float(x) for x in element.split(',')])  
    # Iterate through the date range in 6-hour intervals
    while current_date <= dateend: 
      # for varno in element_array:
     for family in families:
      for region in regions:
       for name, input_path in zip(names, input_paths):
        FAM, VCOORD, VCOCRIT, STATB, element, VCOTYP = pikobs.family(family)
        element_array = np.array([float(x) for x in element.split(',')])  
   

        # Format the current date as a string
        formatted_date = current_date.strftime('%Y%m%d%H')

        # Build the file name using the date and family
        filename = f'{formatted_date}_{family}'
        # Create a new dictionary and append it to the list
        data_dict = {
            'family': family,
            'filein': f'{input_path}/{filename}',
            'db_new': f'{pathwork}/{family}/timeserie_{name}_{datestart1}_{dateend1}_{flag_criteria}_{family}_{region}.db',
            'region': region,
            'flag_criteria': flag_criteria,
            'varnos': varnos,
          #  'varno'   : varno
        }
        data_list.append(data_dict)

        # Update the current_date in the loop by adding 6 hours
     current_date += delta

    return data_list

def create_data_list_plot(datestart1,
                          dateend1, 
                          families,
                          namein, 
                          pathwork, 
                          flag_criteria, 
                          regions, 
                          id_stn, 
                          channel,
                          fonctions):
 data_list_plot = []
 for fonction in fonctions:
  for family in families:
   for region in regions:
    
    filea = f'{pathwork}/{family}/timeserie_{namein[0]}_{datestart1}_{dateend1}_{flag_criteria}_{family}_{region}.db'
    namea = namein[0]
    fileset = [filea]
    nameset = [namein[0]]
   
    if len(namein)>1:
          fileb = f'{pathwork}/{family}/timeserie_{namein[1]}_{datestart1}_{dateend1}_{flag_criteria}_{family}_{region}.db'
          fileset = [filea,fileb]
          nameset = [namein[0], namein[1]] 
          conn = sqlite3.connect(fileb)
          cursor = conn.cursor()

    else:
    
      conn = sqlite3.connect(filea)
      cursor = conn.cursor()
    if id_stn=='all':
           query = "SELECT DISTINCT id_stn FROM timeserie;"
           cursor.execute(query)
           id_stns = np.array([item[0] for item in cursor.fetchall()])
           query = "SELECT DISTINCT varno FROM timeserie;"
           cursor.execute(query)
           varnos = np.array([item[0] for item in cursor.fetchall()])
           for varno in varnos:
              data_dict_plot = {
               'id_stn': 'all_t',
               'vcoord': 'join',
               'files_in':fileset,
               'varno':varno,
               'name_in':nameset,
               'region':region,
               'family':family,
               'fonction':fonction}
              data_list_plot.append(data_dict_plot)
    else:
           id_stns = ['join']
    
    for idstn in id_stns:
        if id_stn=='join':
            criter = '   '
        else:
            criter =f'where id_stn = "{idstn}"'
        if channel =='all': 
            query = f"SELECT DISTINCT vcoord, varno FROM timeserie {criter} ORDER BY vcoord ASC;"
            cursor.execute(query)
            vcoords = cursor.fetchall()
            for vcoord, varno in vcoords:
              data_dict_plot = {
               'id_stn': idstn,
               'vcoord': vcoord,
               'files_in':fileset,
               'varno':varno,
               'name_in':nameset,
               'region':region,
               'family':family,
               'fonction':fonction}
              data_list_plot.append(data_dict_plot)
        else:
            query = f"SELECT DISTINCT  varno FROM timeserie ;"
            cursor.execute(query)
            channels_varno = []
            result = cursor.fetchall()
            if result:
                   channels_varno.append(result)
   
            for  varno in channels_varno[0]:
              data_dict_plot = {
               'id_stn': idstn,
               'vcoord': 'join',
               'files_in':fileset,
               'varno':varno,
               'name_in':nameset,
               'region':region,
               'family':family,
               'fonction':fonction}
              data_list_plot.append(data_dict_plot)
    

  return data_list_plot


def make_timeserie(files_in,
                   names_in,  
                   pathwork, 
                   datestart,
                   dateend,
                   regions, 
                   familys, 
                   flag_criteria, 
                   fonction,
                   varnos,
                   id_stn,
                   channel,
                   n_cpu):


    for family in familys:
       pikobs.delete_create_folder(pathwork, family)

          
    data_list = create_data_list(datestart,
                                 dateend, 
                                 familys, 
                                 files_in,
                                 names_in,
                                 pathwork,
                                 flag_criteria, 
                                 regions,
                                 varnos)
          

    import time
    import dask
    t0 = time.time()
    if n_cpu==1:
           for  data_ in data_list:  
               print (f"Serie = {len(data_list)}")
               #print (data_['family'], 
               create_timeserie_table(data_['family'], 
                                      data_['db_new'], 
                                      data_['filein'],
                                      data_['region'],
                                      data_['flag_criteria'],
                                      data_['varnos'],
                                      channel,
                                      id_stn)
               
       
       
       
       
    else:
           print (f'in Parallel  = {len(data_list)}')
           with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                              n_workers=n_cpu, 
                                              silence_logs=40) as client:
               delayed_funcs = [dask.delayed(create_timeserie_table)(data_['family'], 
                                                 data_['db_new'], 
                                                 data_['filein'],
                                                 data_['region'],
                                                 data_['flag_criteria'],
                                                 data_['varnos'],
                                                 channel,
                                                 id_stn)for data_ in data_list]
               results = dask.compute(*delayed_funcs)
    
    tn= time.time()
    print ('Total time:', round(tn-t0,2) )  
    data_list_plot = create_data_list_plot(datestart,
                                       dateend, 
                                       familys, 
                                       names_in, 
                                       pathwork,
                                       flag_criteria, 
                                       regions,
                                       id_stn,
                                       channel,
                                       fonction)

    #$ os.makedirs(f'{pathwork}/timeserie')
    fig_title = ''
    t0 = time.time()
    #n_cpu=1
    if n_cpu==1:
           for  data_ in data_list_plot[0:1]:  
               print ("Plotting in serie")

               pikobs.timeserie_plot(
                                  pathwork,
                     datestart,
                     dateend,
                     data_['fonction'],
                     flag_criteria,
                     data_['family'],
                     data_['region'],
                     fig_title,
                     data_['vcoord'], 
                     data_['id_stn'], 
                     data_['varno'],
                     data_['files_in'],
                     data_['name_in'])  
    else:
             print (f'Plotting in Parallel = {len(data_list_plot)}')
             with dask.distributed.Client(processes=True, threads_per_worker=1, 
                                              n_workers=n_cpu, 
                                              silence_logs=40) as client:
               delayed_funcs = [dask.delayed(pikobs.timeserie_plot)(
                                  pathwork,
                     datestart,
                     dateend,
                     data_['fonction'],
                     flag_criteria,
                     data_['family'],
                     data_['region'],
                     fig_title,
                     data_['vcoord'], 
                     data_['id_stn'], 
                     data_['varno'],
                     data_['files_in'],
                     data_['name_in'])for data_ in data_list_plot]

               results = dask.compute(*delayed_funcs)
    tn= time.time()
    print ('Total time:', round(tn-t0,2) )  
 



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
    parser.add_argument('--family', nargs="+", default='undefined', type=str, help="Family")
    parser.add_argument('--flags_criteria', default='undefined', type=str, help="Flags criteria")
    parser.add_argument('--fonction', nargs="+", default='undefined', type=str, help="Function")
    parser.add_argument('--varnos', nargs="+", default='undefined', type=str, help="Function")
    parser.add_argument('--id_stn', default='all', type=str, help="id_stn") 
    parser.add_argument('--channel', default='all', type=str, help="channel")
    parser.add_argument('--n_cpus', default=1, type=int, help="Number of CPUs")

    args = parser.parse_args()
    for arg in vars(args):
       print (f'--{arg} {getattr(args, arg)}')
    # Check if each argument is 'undefined'
    if args.path_control_files == 'undefined':
        files_in = [args.path_experience_files]
        names_in = [args.experience_name]
    else:    
        if args.path_experience_files == 'undefined':
            raise ValueError('You must specify --path_experience_files')
        if args.experience_name == 'undefined':
            raise ValueError('You must specify --experience_name')
        else:

            files_in = [args.path_control_files, args.path_experience_files]
            names_in = [args.control_name, args.experience_name]
    if args.varnos == 'undefined':
        args.varnos = []
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
    if args.fonction == 'undefined':
        raise ValueError('You must specify --fonction')


    # Comment
    # Proj='cyl' // Proj=='OrthoN'// Proj=='OrthoS'// Proj=='robinson' // Proj=='Europe' // Proj=='Canada' // Proj=='AmeriqueNord' // Proj=='Npolar' //  Proj=='Spolar' // Proj == 'reg'
  
    # Call your function with the arguments
    sys.exit(make_timeserie(files_in,
                            names_in, 
                            args.pathwork,
                            args.datestart,
                            args.dateend,
                            args.region,
                            args.family,
                            args.flags_criteria,
                            args.fonction, 
                            args.varnos,
                            args.id_stn,
                            args.channel,
                            args.n_cpus))

if __name__ == '__main__':
    args = arg_call()    
