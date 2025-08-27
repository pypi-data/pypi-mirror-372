def family(famille):
    if famille in ('ua', 'ua_qc'):
        FAM = "Radiosondes"
        VCOORD = " round(vcoord/025000.)*02500 "
        VCOORD = " round(vcoord/20000.)*20000 "
    #    VCOORD = " round(vcoord/05000.)*05000 "
        STATB = "OBS_ERROR"
        STATB = " 0."
        VCOCRIT = " and  id_stn like '%' "
        VCOCRIT = "    "
        elem = "11004,11003,12001,12192"
        VCOTYP = 'PRESSION'
    elif famille in ('gp', 'gp_qc', 'gpssfc_b'):
        FAM = "GBGPS"
        VCOTYP = 'SURFACE'
        VCOCRIT = "  "
        VCOORD = " 9999    "
        VCOORD = " round(lat/10)*10    "
        STATB = "OBS_ERROR"
        STATB = "0. "
        elem = "15031 "
    elif famille == 'synop_b':
        FAM = "SHIPS"
        VCOTYP = 'SURFACE'
        VCOORD = "'SURF'   "
        STATB = "OBS_ERROR"
        VCOCRIT = "    "
    elif famille in ('sc', 'sc_qc'):
        FAM = "SCATS"
        VCOTYP = 'SURFACE'
        VCOORD = " 9999    "
        VCOORD = " round(lat/10)*10    "
        VCOCRIT = "      "
        STATB = "OBS_ERROR"
        STATB = "0. "
        elem = "11215,11216"
    elif famille in ('ro', 'ro_qc', 'gpsocc'):
        FAM = "GPSRO"
        VCOTYP = 'HAUTEUR(metres)'
        VCOORD = " round(vcoord/10000.)*10000 "
        VCOORD = " round(vcoord/1000.)*1000 "
        STATB = " 0. "
        VCOCRIT = "      "
        elem = "15036"
    elif famille in ('mwhs2', 'mwhs2_qc'):
        FAM = "MWHS2"
        VCOORD = "  vcoord "
        VCOTYP = 'CANAL'
        STATB = "BIAS_CORR"
        VCOCRIT = "      "
        elem = "12163"
    elif famille in ('to_amsua_qc', 'to_amsua', 'to_amsua_allsky', 'to_amsua_allsky_qc'):
        FAM = "AMSUA"
        VCOORD = "  vcoord "
        VCOTYP = 'CANAL'
        STATB = "BIAS_CORR" 
        VCOCRIT = "      "
        elem = "12163"
    elif famille in ('to_amsub_qc', 'to_amsub_allsky'):
        FAM = "AMSUB"
        VCOTYP = 'CANAL'
        STATB = "BIAS_CORR"
        VCOORD = "  vcoord "
        VCOCRIT = "  "
        elem = "12163"
    elif famille in ('ssmis_qc', 'ssmis'):
        FAM = "SSMIS"
        VCOTYP = 'CANAL'
        STATB = "BIAS_CORR"
        VCOORD = "  vcoord "
        elem = "12163"
        VCOCRIT = "  "
    elif famille in ('iasi', 'iasi_qc'):
        FAM = "IASI"
        VCOTYP = 'CANAL'
        STATB = "BIAS_CORR"
        VCOORD = "  vcoord "
       # VCOORDLIST = "32,38,44,50,57,63,76,79,82,87,104,109,116,122,128,135,141,154,160,167,173,180,185,199,205,212,213,214,217,219,224,226,230,232,236,239,243,246,249,252,262,265,269,275,282,299,300,323,327,329,335,347,350,354,356,360,366,371,373,375,377,379,381,389,404,407,410,414,416,426,428,432,434,445,457,515,546,552,566,571,573,646,662,668,756,867,921,1027,1046,1121,1133,1191,1194,1271,2019,2094,2119,2213,2321,2398,2907,2944,2951,2977,2990,2993,3008,3027,3030,3049,3058,3087,3107,3110,3127,3151,3160,3228,3263,3303,3432,3467,3497,3499,3518,3610,3646,3673,3710,3763,4920,4991,5371,6135,6149,6158,6161,6174,6205,6209,6213,6317"
        VCOCRIT = " "
        elem = "12163"
    elif famille in ('ch','ch_db'):
        FAM = "OZONE"
        VCOTYP = 'LEVEL'
        VCOORD = "  vcoord    "
        elem = "15198,15008"
        FONCTION = "(100.*omp/obsvalue)"
        FONCTION2 = "(omp*0.)"
        STATB = '    '
        STN_IDS = " id_stn in ('AURA-MLS') and vcoord = 100"
        VCOCRIT = '    '
    elif famille in ('crisfsr1_qc', 'crisfsr2_qc', 'cris'):
        FAM = "CRISFSR"
        VCOORD = "  vcoord "
        VCOTYP = 'CANAL'
        STATB = "BIAS_CORR"
        elem = "12163"
        VCOCRIT = "    "
    elif famille in ('atms_allsky', 'atms_qc', 'atms'):
        
        FAM = "ATMS"
        VCOTYP = 'CANAL'
        STATB = "BIAS_CORR"
        VCOORD = "  vcoord " 
        VCOCRIT = "    "
        elem = "12163"
    elif famille in ('csr', 'csr_qc'):
        FAM = "CSR"
        VCOTYP = 'CANAL'
        STATB = "BIAS_CORR"
        VCOCRIT = "  "
        VCOORD = "  vcoord "
        elem = "12163"
    elif famille in ('ai', 'ai_qc','012_ai.sqlite' ):
        FAM = "AIRCRAFTS"
        VCOTYP = 'PRESSION'
        VCOORD = " round(vcoord/20000.)*20000 "
       # VCOORD = " round(vcoord/05000.)*05000 "
        STATB = "BIAS_CORR"
        VCOCRIT = " and vcoord > 00000 "
        elem = "11004,11003,12001,12192"
    elif famille in ('radar'):
        FAM = "RADAR"
        VCOTYP = 'Height'
        VCOORD = "  "
        VCOORD = "  "
        STATB = " "
        VCOCRIT = "  "
        elem = "21014"

    elif famille in ('sw', 'sw_qc', 'sw_polar', 'sw_polaireDB'):
        FAM = "AMVS"
        VCOTYP = 'PRESSION'
        VCOORD = " round(vcoord/2000.)*2000 "
        STATB = "OBS_ERROR"
        STATB = " 0."
        VCOCRIT = "  "
        elem = "11002,11004,11003"
    elif famille in ('sf', 'swobnchwos'):
        FAM = "Surface"
        VCOTYP = 'SURFACE'
        VCOORD = " 9999    "
        # VCOORD = " round(lat/30)*30    "
        # VCOORD = "cast(round( (julianday(( (julianday(isodatetime(date,time)) ) )) - julianday(isodatetime(${DATE})))*24.*60./15.,5) as int) +13 "
        VCOCRIT = "  "
        STATB = "OBS_ERROR"
        STATB = "0. "
        elem = "11215,11216,10051,10004,12004,12203,11011,11012 "
    else:
        print("FAMILLE:", famille)
        print("famille no existente. Salida.")
        return None
    return FAM, VCOORD, VCOCRIT, STATB, elem, VCOTYP
