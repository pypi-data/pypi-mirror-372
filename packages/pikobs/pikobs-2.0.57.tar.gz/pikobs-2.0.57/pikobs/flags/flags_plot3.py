import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import json
import random
import os

def flags_plot(pathwork, datestart, dateend, family, plot_title, vcoord, id_stn, varno, region):
    db_file = f'{pathwork}/output_file{region}.db'

    def bits_active(number):
        if number == 0:
            return [0]
        return [bit for bit in range(24) if (number & (1 << bit)) != 0]

    results_by_date = defaultdict(lambda: defaultdict(int))
    total_observations_by_date = defaultdict(int)

    # Conexión con la base de datos
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Obtener todas las fechas y observaciones
    cursor.execute(f"""
        SELECT DISTINCT date, flag
        FROM flag_observations
        WHERE varno={varno}
    """)
    rows = cursor.fetchall()
    for date, flag in rows:
        cursor.execute(f"""
            SELECT count(*)
            FROM flag_observations
            WHERE date=? AND flag=? AND varno={varno}
        """, (date, flag))
        num_observations = cursor.fetchone()[0]
        results_by_date[date][flag] += num_observations

    cursor.execute(f"""
        SELECT date, count(*)
        FROM flag_observations
        WHERE varno={varno}
        GROUP BY date
    """)
    total_observations = cursor.fetchall()
    for date, count in total_observations:
        total_observations_by_date[date] = count
    
    connection.close()

    if not results_by_date:
        print("No data found.")
        return
    
    normalized_data = defaultdict(lambda: defaultdict(float))
    numberobs_data = defaultdict(lambda: defaultdict(float))
    
    for date, counts in results_by_date.items():
        total_observations = total_observations_by_date[date]
        accumulated = 0
        for flag, num_observations in sorted(counts.items(), key=lambda item: item[1], reverse=True):
            percentage = (num_observations / total_observations) * 100
            normalized_data[date][flag] = (accumulated, accumulated + percentage)
            numberobs_data[date][flag] = num_observations
            accumulated += percentage
    
    average_percentage_by_flag = {}
    average_obs_by_flag = {}
    
    all_flags = set()
    for date in results_by_date:
        all_flags.update(normalized_data[date].keys())
    
    total_observations_all_dates = sum(total_observations_by_date.values())
    for flag in all_flags:
        total_flag_observations = sum(results_by_date[date][flag] for date in results_by_date)
        average_percentage_by_flag[flag] = (total_flag_observations / total_observations_all_dates) * 100
        average_obs_by_flag[flag] = total_flag_observations

    # Color mapping
    mapping_file = 'color_mapping.json'
    
    def load_color_mapping():
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as file:
                try:
                    mapping = json.load(file)
                    return mapping
                except json.JSONDecodeError:
                    return {}
        return {}
    
    def save_color_mapping(mapping):
        with open(mapping_file, 'w') as file:
            json.dump(mapping, file, indent=4)
    
    def get_color_for_flag(flag, color_mapping):
        if flag not in color_mapping:
            new_color = generate_random_color()
            color_mapping[flag] = new_color
            save_color_mapping(color_mapping)
        return color_mapping[flag]
    
    def generate_random_color():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))
    
    color_mapping = load_color_mapping()
    
    all_flags = {8390912, 0, 4, 2240, 8390720}
    for flag in all_flags:
        get_color_for_flag(str(flag), color_mapping)
    
    fig = plt.figure(figsize=(20, 20))
    gs = fig.add_gridspec(14, 5, height_ratios=[3000] + [1000]*13, hspace=1)
    ax1 = fig.add_subplot(gs[0, :])
    fig.subplots_adjust(top=0.9, bottom=0.1, left=0.1, right=0.9, hspace=1, wspace=0.9)
    
    dates = list(total_observations_by_date.keys())
    if len(dates) == 0:
        print("No dates found in the data.")
        return

    bar_width = 1 / len(dates) if len(dates) > 0 else 0.2
    x_positions = []
    for date_idx, date in enumerate(dates):
        sorted_flags = sorted(average_percentage_by_flag.items(), key=lambda item: item[1], reverse=True)
        sorted_flags_keys = [flag for flag, _ in sorted_flags]
        normalized_data[date] = {flag: normalized_data[date][flag] for flag in sorted_flags_keys}
        for flag_idx, flag in enumerate(sorted_flags_keys):
            try:
                start, end = normalized_data[date][flag]
            except KeyError:
                start = 99.999
                end = 100
            
            bits = bits_active(flag)
            avg_percentage = average_percentage_by_flag[flag]
            avg_obs = average_obs_by_flag[flag]
            
            def format_avg_obs(avg_obs, num_dates):
                avg_per_date = avg_obs / num_dates
                if avg_per_date >= 1:
                    return f"{int(round(avg_per_date))}"
                else:
                    return f"{avg_per_date:.1g}"
            
            def format_avg_percentage(avg_percentage):
                if avg_percentage >= 0.001:
                    return f"{avg_percentage:.3f}"
                else:
                    return f"{avg_percentage:.1g}"
            
            formatted_avg_obs = format_avg_obs(avg_obs, len(dates))
            formatted_avg_percentage = format_avg_percentage(avg_percentage)
            label = (f'Flag {flag} (Active bits: {bits}, '
                     f'Avg %: {formatted_avg_percentage}, '
                     f'Avg N. Obs.: {formatted_avg_obs})') if date_idx == 0 else ""
            x_position = date_idx + bar_width * np.arange(len(dates)) - 0.4
            x_positions.extend(x_position)
            ax1.bar(x_position, end - start, bottom=start, width=bar_width, label=label, color=get_color_for_flag(str(flag), color_mapping))
    
    x_min = min(x_positions) if x_positions else 0
    x_max = max(x_positions) + bar_width if x_positions else bar_width
    ax1.set_xlim(x_min, x_max)
    ax1.set_ylim(0, 100)
    ax1.set_yticks(np.arange(0, 101, 20))
    gs.update(wspace=0.3)
    ax1.set_xlabel('Date', fontsize=15)
    ax1.set_ylabel('Percentage of N. Obs.', fontsize=15)
    ax1.set_title(f'Normalized Distribution of Flags and Active Bits per File\n {datestart} to {dateend} {family}', fontsize=15)
    tick_interval = max(1, len(dates) // 6)
    ax1.set_xticks(x_positions[::tick_interval])
    ax1.set_xticklabels(dates[::tick_interval])
    ax1.legend(loc='upper center', bbox_to_anchor=(0.15, -0.4), ncol=1, frameon=False, fontsize=8)
    ax1.tick_params(axis='x', labelsize=18)
    ax1.tick_params(axis='y', labelsize=18)
    
    bit_observations = defaultdict(int)
    total_observations_all_dates = 0
    explanation_text = (
        r"$^1$ Average percentage is calculated based on the total number of observations.\n"
        r"$^2$ Average number of observations per 6-hour intervals."
    )
    fig.text(0.5, 0.5, explanation_text, ha='center', va='top', fontsize=7, linespacing=1.5)
    
    # Segundo gráfico: Observaciones por bit
    fig2 = plt.figure(figsize=(20, 20))
    ax2 = fig2.add_subplot(111)
    
    total_bits = len(bit_observations)
    bit_colors = [get_color_for_flag(str(bit), color_mapping) for bit in bit_observations.keys()]
    sorted_bits = sorted(bit_observations.items())
    bit_labels = [f"Bit {bit}: {count}" for bit, count in sorted_bits]
    
    bar_width = 0.35
    x = np.arange(total_bits)
    
    ax2.bar(x, [count for bit, count in sorted_bits], color=bit_colors, width=bar_width)
    ax2.set_xticks(x)
    ax2.set_xticklabels(bit_labels, rotation=90)
    ax2.set_xlabel('Bits')
    ax2.set_ylabel('Total Observations')
    ax2.set_title('Total Number of Observations per Bit')
    
    plt.show()

