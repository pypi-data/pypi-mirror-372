import glob
import sqlite3
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import json
import os
import random
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
def load_color_mapping( mapping_file):
        """Carga el mapeo de colores desde el archivo JSON."""
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as file:
                try:
                    mapping = json.load(file)
                    return mapping
                except json.JSONDecodeError:
                    print("Error decoding JSON from the file. Returning empty mapping.")
                    return {}
        return {}
    
def save_color_mapping(mapping,mapping_file):
        """Guarda el mapeo de colores en el archivo JSON."""
        with open(mapping_file, 'w') as file:
            json.dump(mapping, file, indent=4)
            print("Saved color mapping:", mapping)  # Verifica el contenido guardado
    
def get_color_for_flag(flag, color_mapping,mapping_file):
        """Obtiene el color para un flag. Si no existe, asigna uno nuevo y actualiza el archivo."""
        print ('----JANINA>',color_mapping)
        if flag not in color_mapping:
            print(f"Flag {flag} not found in color mapping. Assigning a new color.")  # Mensaje de advertencia
            new_color = generate_random_color()
            color_mapping[flag] = new_color
            save_color_mapping(color_mapping,mapping_file)  # Guarda solo el nuevo mapeo
        return color_mapping[flag]
    
def generate_random_color():
        """Genera un color hexadecimal aleatorio."""
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))
    

def parse_date(date_str):
    """Convierte un string en formato YYYYMMDDHH a un objeto datetime."""
    return datetime.strptime(date_str, '%Y%m%d%H')

def format_date(date):
    """Convierte un objeto datetime a un string en formato YYYYMMDDHH."""
    return date.strftime('%Y%m%d%H')

def generate_date_range(datestart_str, dateend_str):
    """Genera una lista de fechas desde datestart menos 6 horas hasta dateend en formato YYYYMMDDHH."""
    # Convierte las cadenas en objetos datetime
    datestart = parse_date(datestart_str)
    dateend = parse_date(dateend_str)

    # Resta 6 horas a datestart
   # datestart -= timedelta(hours=6)

    # Genera una lista de fechas desde datestart hasta dateend
    date_list = []
    current_date = datestart
    while current_date <= dateend:
        date_list.append(format_date(current_date))
        current_date += timedelta(hours=6)  # Cambia el intervalo según sea necesario

    return date_list# Directory and file pattern
def generate_random_color():
        """Genera un color hexadecimal aleatorio."""
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))
def format_avg_obs(avg_obs, num_files):
                avg_per_file = avg_obs / num_files
                if avg_per_file >= 1:
                    return f"{int(round(avg_per_file))}"
                else:
                    # Redondear a la primera cifra significativa
                    return f"{avg_per_file:.1g}"
def format_avg_percentage(avg_percentage):
                if avg_percentage >= 0.001:
                    return f"{avg_percentage:.3f}"  # 3 decimales
                else:
                    return f"{avg_percentage:.1g}"  # Primera cifra significativa
                        # Usar la función en el código

def bits_active(number):
        if number == 0:
            return [0]  # Si el número es 0, devolver [0] explícitamente
        return [bit for bit in range(24) if (number & (1 << bit)) != 0]
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import json
import os

def bits_to_decimal(*bit_positions):
    """
    Convierte una lista de posiciones de bits activados a su valor decimal.
    bit_positions: una lista de enteros que representan las posiciones de los bits encendidos.
    """
    decimal = 0
    for bit in bit_positions:
        decimal += 2**bit  # Sumar el valor de 2 elevado a la posición del bit
    return decimal

def parse_date(date_str):
    try:
        # Assuming date format is 'YYYYMMDDHH' or 'YYYY-MM-DD HH:MM:SS'
        return pd.to_datetime(date_str, format='%Y%m%d%H', errors='coerce')
    except ValueError:
        return pd.NaT
#def bits_active(flag):
#    """
#    Devuelve una lista de los bits activos para un flag (valor decimal).
##    """
#    return [i for i in range(24) if flag & (1 << i)]
       
def has_predefined_pair(bits,  predefined_bit_pairs):
    """
    Verifies if the active bits satisfy the conditions specified in predefined_bit_pairs.
    Handles conditions before and after multiple 'or', and supports excluded bits (e.g., 'n23').
    
    :param bits: A list of active bits (e.g., [6, 12, 15]).
    :param predefined_bit_pairs: A list of tuples representing predefined bit pairs.
                                 Example: [(12, 6, 'n23', 'or', 6, 'or', 9)].
                                 'n' prefix indicates the bit must be inactive.
    :return: A list of valid bit pairs that satisfy the conditions.
    """
    valid_pairs = []  # List to store all valid pairs

    for bit_pair in predefined_bit_pairs:
        active_conditions = []  # List of conditions to check
        excluded_bits = []  # Bits that must be inactive (prefixed with 'n')
        
        condition_sets = []  # Multiple sets of conditions, split by 'or'
        current_set = []  # The current set of conditions before the next 'or'
        
        for bit in bit_pair:
            if isinstance(bit, str) and bit.startswith('n'):
                excluded_bits.append(int(bit[1:]))  # 'n23' -> bit 23 must be inactive
            elif bit == 'or':
                # When encountering 'or', save the current set and start a new one
                condition_sets.append(current_set)
                current_set = []  # Reset for the next condition set
            else:
                current_set.append(bit)  # Add bits to the current set of conditions
        
        # Append the final set of conditions if there were no more 'or' separators
        if current_set:
            condition_sets.append(current_set)
        
        # Now check each condition set (separated by 'or')
        found_valid_set = False
        for condition_set in condition_sets:
      #      # Check if all bits in the set are active and all excluded bits are inactive
            if all(bit in bits for bit in condition_set) and all(bit not in bits for bit in excluded_bits):
                found_valid_set = True
                break  # If one set is valid, no need to check further

        if found_valid_set:
            valid_pairs.append(bit_pair)

    return valid_pairs  # Return the list of valid pairs


    return valid_pairs  # Return the list of valid pairs    
def flags_plotv2(pathwork,
               datestart,
               dateend,
               family,
               plot_title,
               vcoord,
               id_stn, 
               varno,
               region):
    db_path = f'{pathwork}/{family}/output_file{region}.db'
    
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    dates = generate_date_range(datestart, dateend)
    dates.sort()  # Ensure dates are in order
    
    # Initialize data structures for storing results
    results_by_file = defaultdict(lambda: defaultdict(int))
    total_observations_by_file = {}
    
    # Bit descriptions for flags
    bit_descriptions = {
        0: "Modified or generated by ADE", 1: "Exceeds climate extreme", 2: "Erroneous", 3: "Possibly erroneous",
        4: "Doubtful", 5: "Interpolated", 6: "Bias corrected", 7: "Rejected by satellite QC",
        8: "Unselected (blacklisted)", 9: "Rejected for background check", 10: "Generated by analysis",
        11: "Unselected channel", 12: "Assimilated", 13: "O-P rogue check failure level 1",
        14: "O-P rogue check failure level 2", 15: "O-P rogue check failure level 3",
        16: "Rejection for O-P magnitude", 17: "Rejected by QC-Var 3DVAR", 18: "Rejected over land due to higher topography",
        19: "Rejected due to land/sea mask", 20: "Aircraft TrackQC rejection",
        21: "Rejected due to transmittance above model top", 22: "QC Obs rejection", 23: "Cloud affected radiance"
    }
    
    # Fetch total observations and flag values in one go
    for date in dates:
        query_id_stn = ''
        query_vcoord = ''
        if id_stn != 'join':
            query_id_stn = f" and id_stn='{id_stn}'"
        if vcoord != 'join':
            query_vcoord = f" and vcoord='{vcoord}'"

        cursor.execute(f"""
            SELECT flag, sum(num_data_entries)
            FROM flag_observations
            WHERE varno={varno} AND date={date} {query_id_stn} {query_vcoord}
            GROUP BY flag
        """)

        flag_data = cursor.fetchall()
        


        total_observations = sum(num for _, num in flag_data)
        total_observations_by_file[date] = total_observations
        
        for flag, num_observations in flag_data:
            results_by_file[date][flag] = num_observations

    # Normalize data and calculate cumulative percentages
    normalized_data = defaultdict(lambda: defaultdict(lambda: (0, 0)))
    numberobs_data = defaultdict(lambda: defaultdict(float))
    
    for date, counts in results_by_file.items():
        total_observations = total_observations_by_file[date]
        print ('22', total_observations )
        accumulated = 0
        for flag, num_observations in sorted(counts.items(), key=lambda item: item[1], reverse=True):
            
            percentage = (num_observations / total_observations) * 100
            normalized_data[date][flag] = (accumulated, accumulated + percentage)
            numberobs_data[date][flag] = num_observations
            accumulated += percentage

    # Calculate average percentage and observations for each flag
    average_percentage_by_flag = {}
    average_obs_by_flag = {}
    total_observations_all_files = sum(total_observations_by_file.values())
    
    all_flags = set(flag for counts in results_by_file.values() for flag in counts)
    
    for flag in all_flags:
       # print (flag, sum(results_by_file[date].get(flag, 0) for date in dates))

        total_flag_observations = sum(results_by_file[date].get(flag, 0) for date in dates)
        average_percentage_by_flag[flag] = (total_flag_observations / total_observations_all_files) * 100
        average_obs_by_flag[flag] = total_flag_observations
    
    # Prepare for plotting
    fig = plt.figure(figsize=(20, 30))
    gs = fig.add_gridspec(14, 5, height_ratios=[3000] + [1000] * 13, hspace=1)
    ax1 = fig.add_subplot(gs[0, :])
    
    file_names = list(total_observations_by_file.keys())
    x = np.arange(len(file_names))
    bar_width = 1 / len(file_names)

    # Load color mapping
    with open('color_mapping.json') as f:
        color_mapping = json.load(f)
    
    x_positions = []
    
    for file_idx, date in enumerate(dates):
        sorted_flags = sorted(average_percentage_by_flag.items(), key=lambda item: item[1], reverse=True)
        sorted_flags_keys = [flag for flag, _ in sorted_flags]
        for flag_idx, flag in enumerate(sorted_flags_keys):
            try:
                start, end = normalized_data[date][flag]
            except KeyError:
                start = 99.999
                end = 100
            label = (f'Flag {flag} (Active bits: {bits_active(flag)}, '
                     rf'Average percentage $^1$ : {format_avg_percentage(average_percentage_by_flag[flag])}%, '
                     rf'Average number of observations $^2$: {format_avg_obs(average_obs_by_flag[flag], len(dates))})') \
                    if file_idx == 0 else ""
            x_position = file_idx + bar_width * np.arange(len(dates)) - 0.5
            x_positions.extend(x_position)
            print (str(flag))
            ax1.bar(x_position, end - start, bottom=start, width=bar_width,
                    label=label, color=get_color_for_flag(str(flag), color_mapping,'color_mapping.json'))
    
    ax1.set_xlim(min(x_positions), max(x_positions) + bar_width)
    ax1.set_ylim(0, 100)
    ax1.set_yticks(np.arange(0, 101, 20))
    ax1.set_xlabel('Date', fontsize=15)
    ax1.set_ylabel('Percentage of N. Obs.', fontsize=15)
    ax1.set_title(f'Normalized Distribution of Bits Presented per File of 6h\n {datestart}-{dateend} # Family:{family} # Channel:{vcoord} # Sat:{id_stn}', fontsize=15)
    ax1.set_xticks(x[::max(1, len(file_names) // 6)])
    ax1.set_xticklabels([os.path.basename(file)[0:10] for file in file_names][::max(1, len(file_names) // 6)])
    ax1.legend(loc='upper center', bbox_to_anchor=(0.15, -0.4), ncol=1, frameon=False, fontsize=8)
    ax1.tick_params(axis='x', labelsize=18)
    ax1.tick_params(axis='y', labelsize=18)
    
    explanation_text = (
        r"$^1$ Average percentage is calculated based on the total number of observations."
        r"$^2$ Average number of observations per 6-hour intervals."
    )
    fig.text(0.5, 0.5, explanation_text, ha='center', va='top', fontsize=7, linespacing=1.5)
    # Predefined pairs of bits you want to plot
    
    # Definir pares de bits predefinidos
    print (family)
    
    if family in ('cris','iasi'):
        predefined_bit_pairs = [(0,'or',2,'or',9,'n16'),(8,),(9,16),(11,7),(11,19),(11,21),(11,23),(9,'or',11),(12,)]  # Ejemplo con exclusión de bit 23
       #a predefined_bit_pairs2 = [(0,'or',2,'or',9,'n16'),(8,),(9,16,'n8'),(11,7,'n8'),(11,19,'n8'),(11,21,'n8'),(11,23,'n8'),(12,)]  # Ejemplo con exclusión de bit 23
        predefined_bit_pairs2 = [(0,'or',2,'or',9,'n16'),(8,),(9,16,'n8'),(11,7,'n8'),(11,19,'n8'),(11,21,'n8'),(11,23,'n8'), (9,'n8','or',11,'n8'),(12,)]  # Ejemplo con exclusión de bit 23
       
    if family in ('amsua_allsky', 'amsub_allsky','atms_allsky.db' ,'atms_allsky', 'mwhs2', 'mwhs2.db','ssmis' ,'ssmis.db'): 
        predefined_bit_pairs =  [(0,'or',7),(8,),(9,16,),(9,18,),(9,23,),(9,),(12,),(23,12,),(23,),(19,)]  # Ejemplo con exclusión de bit 23
        predefined_bit_pairs_assi = [(0,'or',7),(8,),(9,16),(9,18,),(9,23,),(9),(12,),(23,12,),(23,),(19,)]  # Ejemplo con exclusión de bit 23
      
    if family in ('radar'):
       predefined_bit_pairs = [(12,),(11,),(9,'n11')]  # Ejemplo con exclusión de bit 23
       #a predefined_bit_pairs2 = [(0,'or',2,'or',9,'n16'),(8,),(9,16,'n8'),(11,7,'n8'),(11,19,'n8'),(11,21,'n8'),(11,23,'n8'),(12,)]  # Ejemplo con exclusión de bit 23
       predefined_bit_pairs2 = [(12,),(11,),(9,'n11')]  # Ejemplo con exclusión de bit 23
    if family in ('csr'):
        predefined_bit_pairs = [(0,'or',2,'or',9,'n16'),(8,),(9,16),(11,7),(11,19),(11,21),(11,23),(9,'or',11),(12,)]  # Ejemplo con exclusión de bit 23
       #a predefined_bit_pairs2 = [(0,'or',2,'or',9,'n16'),(8,),(9,16,'n8'),(11,7,'n8'),(11,19,'n8'),(11,21,'n8'),(11,23,'n8'),(12,)]  # Ejemplo con exclusión de bit 23
        predefined_bit_pairs2 = [(0,'or',2,'or',9,'n16'),(8,),(9,16,'n8'),(11,7,'n8'),(11,19,'n8'),(11,21,'n8'),(11,23,'n8'), (9,'n8','or',11,'n8'),(12,)]  # Ejemplo con exclusión de bit 23
       
        
  

    # Total de observaciones en todas las banderas (flags)
    total_observations_all_files = 0
    bit_pair_observations = defaultdict(int) 
    bit_pair_observations_assi= defaultdict(int)
    total_observations_n8 = 0
    total_observations_n8v2 = 0
    total_observations_n8v3 = 0
    total_n23= 0
    total_31_n23= 0
    total_32_n23= 0

    total_31=0
    total_32=0
    TOTAL = 0  
    TOTAL_ASSI = 0 
    for date in dates:
        cursor.execute(f"""
            SELECT flag, sum(num_data_entries), vcoord
            FROM flag_observations
            WHERE varno={varno} AND date={date}  {query_id_stn} {query_vcoord}
            GROUP BY flag, vcoord
        """)

        flag_data = cursor.fetchall()
        cursor.execute(f"""
            SELECT distinct(vcoord) FROM flag_observations  where  (flag & 4096) = 4096;
  

            
        """)
        vcoord_data = cursor.fetchall()

        def bits_activos(decimal):
                # Devuelve una lista con los números de los bits activos
                return [i for i in range(decimal.bit_length()) if decimal & (1 << i) != 0]

        vcoord_data = [vcoord_data[0] for vcoord_data in  vcoord_data ] 
        for flag, num_observations, vcoord_ in flag_data: 
            bits = bits_activos(flag)

            if vcoord_ in (vcoord_data):
               TOTAL_ASSI+= num_observations
               valid_bit_pairs  = has_predefined_pair(bits,predefined_bit_pairs)
               for bit_pair in valid_bit_pairs:

                   bit_pair_observations_assi[bit_pair] += num_observations

            TOTAL+= num_observations
          #  print (flag)
           
            valid_bit_pairs  = has_predefined_pair(bits,predefined_bit_pairs)
            
            for bit_pair in valid_bit_pairs:

               bit_pair_observations[bit_pair] += num_observations

            #valid_bit_pairs2 = has_predefined_pair(bits, predefined_bit_pairs2)
            
          #  for bit_pair in valid_bit_pairs2:
          #      bit_pair_observations2[bit_pair] += num_observations
            # Procesar todos los pares de bits válidos (puede ser más de uno)
           # for bit_pair in valid_bit_pairs:
            #    bit_pair_observations[bit_pair] += num_observations  # Solo suma los pares de bits válidosa
    for pair in bit_pair_observations:
        print ( '======>' ,pair, bit_pair_observations[pair],TOTAL)
    bit_pair_percentages = {pair: (bit_pair_observations[pair] / TOTAL) * 100 for pair in bit_pair_observations}
   # print (bit_pair_percentages2 )

    bit_pair_percentages_assi = {pair: (bit_pair_observations_assi[pair], (bit_pair_observations_assi[pair] /  TOTAL_ASSI) * 100) for pair in bit_pair_observations_assi}
  #  exit()
    # Gráfico de pie para los pares de bits
    num_cols = 5
    num_rows = (len(bit_pair_percentages) + (num_cols - 3)) // (num_cols - 2) + 1
#    bit_pair_titles = {(0,'or',2,'or', 9,'n16'): "DONNÉES ERRONÉES",
#                       (8,): "CANAUX SUR LA LISTE NOIRE",
#                       (9,16,'n8') : "BACKGROUND CHECK (O-P INNOVATION ROGUE CHECK)",
#                       (9,16) : "BACKGROUND CHECK (O-P INNOVATION ROGUE CHECK)",
#                       (11,7,'n8') : "PAS ASSIMILÉS LE JOUR"                                               ,
#                       (11,7) : "PAS ASSIMILÉS LE JOUR"                                               ,
#                       (11,19,'n8'): "SENSIBILITÉ LAND / SEA-ICE"                                               , 
#                       (11,19): "SENSIBILITÉ LAND / SEA-ICE"                                               , 
#                       (11,21,'n8'): "SENSIBILITÉ OVER MODEL TOP"                                                ,
#                       (11,21): "SENSIBILITÉ OVER MODEL TOP"                                                ,
#
#
#                       (11,23,'n8'): "AFFECTÉS PAR LES NUAGES"                                             ,
#                       (11,23     ): "AFFECTÉS PAR LES NUAGES"                                             ,
#                       (9,'n8','or',11,'n8'):"REJETÉS PAR LE CONTRÔLE DE QUALITÉ DANS SON ENSEMBLE"                                   ,
#                       (9,'or',11):"REJETÉS PAR LE CONTRÔLE DE QUALITÉ DANS SON ENSEMBLE"                                   ,
#                        (12,): "ASSIMILÉS" ,
#                       (0,'n8','or',7,'n8'): "DONNÉES ERRONÉES" , 
#                       (0,'or',7): "DONNÉES ERRONÉES" ,
#
#                       (0,'or',7,'n8'): "DONNÉES ERRONÉES" ,
#                         (8,): "CANAUX SUR LA LISTE NOIRE",
#                       (9,16,'n8'): "BACKGROUND CHECK (O-P INNOVATION ROGUE CHECK)",
#                       (9,16): "BACKGROUND CHECK (O-P INNOVATION ROGUE CHECK)",
#                       (9,18,'n8'): "SENSIBILITÉ À LA TOPOGRAPHIE",
#                       (9,18): "SENSIBILITÉ À LA TOPOGRAPHIE",
#                       (9,23,'n8'): "AFFECTÉS PAR LES NUAGES PAS ASSIMILÉS ",
#                       (9,23): "AFFECTÉS PAR LES NUAGES",
#                       (23,12): "AFFECTÉS PAR LES NUAGES MAIS ASSIMILÉS",
#                       (23,): "AFFECTÉS PAR LES NUAGES",
#
#                       (9,'n8'): "REJETÉS PAR LE CONTRÔLE DE QUALITÉ DANS SON ENSEMBLE" ,
#                       (9,): "REJETÉS PAR LE CONTRÔLE DE QUALITÉ DANS SON ENSEMBLE" ,
#
#
#
#
#
#                        }    
     
    bit_pair_titles ={(0, 'or', 2, 'or', 9, 'n16'): "ERRONEOUS DATA",
                       (8,): "CHANNELS ON THE BLACKLIST",
                       (9, 16, 'n8'): "BACKGROUND CHECK (O-P INNOVATION ROGUE CHECK)",
                       (9, 16): "BACKGROUND CHECK (O-P INNOVATION ROGUE CHECK)",
                       (11, 7, 'n8'): "NOT ASSIMILATED DURING THE DAY",
                       (11, 7): "NOT ASSIMILATED DURING THE DAY",
                       (11, 19, 'n8'): "LAND / SEA-ICE SENSITIVITY",
                       (11, 19): "LAND / SEA-ICE SENSITIVITY",
                       (11, 21, 'n8'): "SENSITIVITY OVER MODEL TOP",
                       (11, 21): "SENSITIVITY OVER MODEL TOP",
                       (11, 23, 'n8'): "AFFECTED BY CLOUDS",
                       (11, 23): "AFFECTED BY CLOUDS AND BIT 11",
                       (9, 'n8', 'or', 11, 'n8'): "REJECTED BY OVERALL QUALITY CONTROL",
                       (9, 'or', 11): "REJECTED BY OVERALL QUALITY CONTROL",
                       (12,): "ASSIMILATED",
                       (0, 'n8', 'or', 7, 'n8'): "ERRONEOUS DATA",
                       (0, 'or', 7): "ERRONEOUS DATA",
                       (0, 'or', 7, 'n8'): "ERRONEOUS DATA",
                       (8,): "CHANNELS ON THE BLACKLIST",
                       (9, 16, 'n8'): "BACKGROUND CHECK (O-P INNOVATION ROGUE CHECK)",
                       (9, 16): "BACKGROUND CHECK (O-P INNOVATION ROGUE CHECK)",
                       (9, 18, 'n8'): "TOPOGRAPHY SENSITIVITY",
                       (9, 18): "TOPOGRAPHY SENSITIVITY",
                       (9, 23, 'n8'): "AFFECTED BY CLOUDS NOT ASSIMILATED",
                       (9, 23): "AFFECTED BY CLOUDS AND BIT 9",
                       (23, 12): "AFFECTED BY CLOUDS BUT ASSIMILATED",
                       (23,): "AFFECTED BY CLOUDS",
                       (9, 'n8'): "REJECTED BY OVERALL QUALITY CONTROL",
                       (9,): "REJECTED BY OVERALL QUALITY CONTROL",
                       (11,): "REJECTED BY THINNING",
                       (9,'n11'): "REJECTED BY BACKGROUND CHECK",
                       (19,): "LAND / SEA-ICE SENSITIVITY",

                       }

                       #(9,11,'n7') : "PAS ASSIMILÉS LE JOUR",
                      # PAS ASSIMILÉS LE JOUR}
  #  print (bit_pair_percentages)
    bit_pair_percentages_sorted = dict(sorted(bit_pair_percentages.items(), key=lambda x: x[1], reverse=True))
    bit_pair_percentages_sorted_assi = dict(sorted(bit_pair_percentages_assi.items(), key=lambda x: x[1][1], reverse=True))
                 
    #import matplotlib.pyplot as plt
    for i, (bit_pair, percentage) in enumerate(bit_pair_percentages_sorted.items()):
        row = i // (num_cols - 2) + 2
        col = (i % (num_cols - 2)) + 2
        ax2 = fig.add_subplot(gs[row, col])
        
        sizes = [percentage, 100 - percentage]
        significant_threshold = 1  # Adjust this value if needed
        colors = ['tab:blue', 'white']
       # print (bit_pair, percentage)
        if percentage < significant_threshold:
             # If percentage is very small, show a more meaningful label
             labels = [f'Bits {bit_pair}\n{percentage:.3g}%', f'Rest (Bits)\n{round(100 - percentage, 3)}%']
        else:
             # Standard labels when percentage is not small
             labels = [f'Bits {bit_pair}\n{round(percentage, 3)}%', f'Rest (Bits)\n{round(100 - percentage, 3)}%']

             
        textprops = {'color': 'black', 'fontweight': 'bold'}
        print ('ssss',sizes)

        ax2.pie(sizes, labels=labels, colors=colors, autopct=None, startangle=190,
                wedgeprops={'edgecolor': 'black'}, textprops=textprops, labeldistance=1.2)  
        # Dynamically create the description for all valid bits in the bit_pair
        additional_title = bit_pair_titles.get(tuple(bit_pair), r"\textbf{Default Title}")
        bit_descriptions_str = "\n ".join([bit_descriptions.get(bit, f"Unknown ({bit})") 
                                  for bit in bit_pair 
                                  if isinstance(bit, int) or (isinstance(bit, str) and not bit.startswith('n') and bit != 'or')])
       # aax2.set_title(f'\\textbf{{{additional_title}}}\n Bits {bit_pair}: \n{bit_descriptions_str}', pad=10, fontsize=10)
        #ax2.text(0.5, 1.01, f'Bits {bit_pair}:', ha='center', va='center', fontsize=10, transform=ax2.transAxes)
        #ax2.text(0.5, 0.95, bit_descriptions_str, ha='center', va='center', fontsize=10, transform=ax2.transAxes)
        ax2.set_title(f'{additional_title}\n Bits {bit_pair}: \n{bit_descriptions_str}', pad=10, fontsize=10)
        ax2.axis('equal')
    # Prepare the percentages to be written
    percentages_text = "Pourcentages tenant compte uniquement des canaux souhaités.\n"
    percentages_text = "Percentages considering only the desired channels.\n"
    if family !='radar':
        for bit_pair, (observations, percentage)  in bit_pair_percentages_sorted_assi.items():
           # Get the title or description
           if bit_pair!= (8,) and bit_pair!=(0,'or',2,'or',9,'n16') and bit_pair!=(11,23     ):
             additional_title = bit_pair_titles.get(tuple(bit_pair), "Bits " + str(bit_pair))
           #  print (total_observations_n8v2, total_observations_all_files)
            # percentages_text += f"*{additional_title}: {(percentage/(total_observations_n8 *100/ total_observations_all_files))*100:.4g}%\n" 
        #     percentages_text += f"*{additional_title}: {percentage/((total_observations_n8-total_observations_n8v3) *100/ total_observations_all_files)   }\n"
             try:
               percentages_text += f"*{additional_title}:  {(observations*100/TOTAL_ASSI):.4g}%\n"
             except:
               print ("")
    
           if bit_pair==(0,'or',2,'or',9,'n16'):
             additional_title = bit_pair_titles.get(tuple(bit_pair), "Bits " + str(bit_pair))
             try:
               percentages_text += f"*{additional_title}: {total_observations_n8v3*100/TOTAL_ASSI:.4g}%\n"
             except:
               print ("")
            #  percentages_text += f"*{additional_title}: {(percentage/(total_observations_n8v2 *100/ total_observations_all_files))*100:.4g}%\n"
           #  print (f"Q*{additional_title}: {100- total_observations_n8*100/total_observations_n8v2:.4g}%")
        # Add the text to the figure
        fig.text(0.65, 0.5,percentages_text, ha='left', va='bottom', fontsize=12)

    print (f'{pathwork}/{family}/combined_{pathwork[0:7]}_channel_{vcoord}_id_stn_{id_stn}_{varno}_plot.png')
    plt.savefig(f'{pathwork}/{family}/combined_{pathwork[0:7]}_channel_{vcoord}_id_stn_{id_stn}_{varno}_plot.png', bbox_inches='tight')
