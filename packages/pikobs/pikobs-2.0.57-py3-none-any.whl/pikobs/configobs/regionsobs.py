def regions(region):
    
    """

    Available regions and their boundaries:

       - **PoleNord**: Northern polar region
         - LAT1=60, LAT2=90 (Latitude range: 60°N to 90°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **PoleSud**: Southern polar region
         - LAT1=-90, LAT2=-60 (Latitude range: 90°S to 60°S)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **AmeriqueduNord**: North America
         - LAT1=25, LAT2=60 (Latitude range: 25°N to 60°N)
         - LON1=-145, LON2=-50 (Longitude range: 145°W to 50°W)

       - **OuestAmeriqueduNord**: Western North America
         - LAT1=25, LAT2=60 (Latitude range: 25°N to 60°N)
         - LON1=-145, LON2=-97.5 (Longitude range: 145°W to 97.5°W)

       - **AmeriqueDuNordPlus**: Extended North America
         - LAT1=25, LAT2=85 (Latitude range: 25°N to 85°N)
         - LON1=-170, LON2=-40 (Longitude range: 170°W to 40°W)

       - **Monde**: World
         - LAT1=-90, LAT2=90 (Latitude range: 90°S to 90°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **Global**: Global
         - LAT1=-90, LAT2=90 (Latitude range: 90°S to 90°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **ExtratropiquesNord**: Northern Extratropics
         - LAT1=20, LAT2=90 (Latitude range: 20°N to 90°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **ExtratropiquesSud**: Southern Extratropics
         - LAT1=-90, LAT2=-20 (Latitude range: 90°S to 20°S)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **HemisphereNord**: Northern Hemisphere
         - LAT1=0, LAT2=90 (Latitude range: 0°N to 90°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **HemisphereSud**: Southern Hemisphere
         - LAT1=-90, LAT2=0 (Latitude range: 90°S to 0°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **Asie**: Asia
         - LAT1=25, LAT2=60 (Latitude range: 25°N to 60°N)
         - LON1=65, LON2=145 (Longitude range: 65°E to 145°E)

       - **Europe**: Europe
         - LAT1=25, LAT2=70 (Latitude range: 25°N to 70°N)
         - LON1=-10, LON2=28 (Longitude range: 10°W to 28°E)

       - **Mexique**: Mexico
         - LAT1=15, LAT2=30 (Latitude range: 15°N to 30°N)
         - LON1=-130, LON2=-60 (Longitude range: 130°W to 60°W)

       - **Canada**: Canada
         - LAT1=45, LAT2=90 (Latitude range: 45°N to 90°N)
         - LON1=-151, LON2=-50 (Longitude range: 151°W to 50°W)

       - **BaieDhudson**: Hudson Bay
         - LAT1=55, LAT2=90 (Latitude range: 55°N to 90°N)
         - LON1=-90, LON2=-60 (Longitude range: 90°W to 60°W)

       - **Arctiquecanadien**: Canadian Arctic
         - LAT1=58, LAT2=90 (Latitude range: 58°N to 90°N)
         - LON1=-141, LON2=-50 (Longitude range: 141°W to 50°W)

       - **EtatsUnis**: United States
         - LAT1=25, LAT2=45 (Latitude range: 25°N to 45°N)
         - LON1=-130, LON2=-70 (Longitude range: 130°W to 70°W)

       - **SudestEtatsUnis**: Southeastern United States
         - LAT1=25, LAT2=40 (Latitude range: 25°N to 40°N)
         - LON1=-100, LON2=-70 (Longitude range: 100°W to 70°W)

       - **EstAmeriqueduNord**: Eastern North America
         - LAT1=25, LAT2=60 (Latitude range: 25°N to 60°N)
         - LON1=-97.5, LON2=-50 (Longitude range: 97.5°W to 50°W)

       - **EstAmeriqueduNordPlus**: Extended Eastern North America
         - LAT1=25, LAT2=85 (Latitude range: 25°N to 85°N)
         - LON1=-97.5, LON2=-50 (Longitude range: 97.5°W to 50°W)

       - **OuestAmeriqueduNordPlus**: Extended Western North America
         - LAT1=25, LAT2=85 (Latitude range: 25°N to 85°N)
         - LON1=-170, LON2=-97.5 (Longitude range: 170°W to 97.5°W)

       - **Tropiques30**: Tropics 30
         - LAT1=-30, LAT2=30 (Latitude range: 30°S to 30°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **Tropiques**: Tropics
         - LAT1=-20, LAT2=20 (Latitude range: 20°S to 20°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **Australie**: Australia
         - LAT1=-55, LAT2=-10 (Latitude range: 55°S to 10°S)
         - LON1=90, LON2=180 (Longitude range: 90°E to 180°E)

       - **Pacifique**: Pacific
         - LAT1=20, LAT2=65 (Latitude range: 20°N to 65°N)
         - LON1=130, LON2=-150 (Longitude range: 130°E to 150°W)

       - **Atlantique**: Atlantic
         - LAT1=20, LAT2=65 (Latitude range: 20°N to 65°N)
         - LON1=-80, LON2=-1 (Longitude range: 80°W to 1°W)

       - **Alaska**: Alaska
         - LAT1=50, LAT2=75 (Latitude range: 50°N to 75°N)
         - LON1=-180, LON2=-140 (Longitude range: 180°W to 140°W)

       - **HIMAPEst**: HIMAP East
         - LAT1=35, LAT2=65 (Latitude range: 35°N to 65°N)
         - LON1=-105, LON2=-50 (Longitude range: 105°W to 50°W)

       - **HIMAPOuest**: HIMAP West
         - LAT1=40, LAT2=65 (Latitude range: 40°N to 65°N)
         - LON1=-135, LON2=-90 (Longitude range: 135°W to 90°W)

       - **ExtremeSud**: Extreme South
         - LAT1=-90, LAT2=-87 (Latitude range: 90°S to 87°S)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **ExtremeNord**: Extreme North
         - LAT1=87, LAT2=90 (Latitude range: 87°N to 90°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **TropiquesOuest**: Western Tropics
         - LAT1=-20, LAT2=0 (Latitude range: 20°S to 0°N)
         - LON1=180, LON2=-90 (Longitude range: 180°E to 90°W)

       - **Bande60a90**: Band from 60°N to 90°N
         - LAT1=60, LAT2=90 (Latitude range: 60°N to 90°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **Bande30a60**: Band from 30°N to 60°N
         - LAT1=30, LAT2=60 (Latitude range: 30°N to 60°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **Bande00a30**: Band from 0°N to 30°N
         - LAT1=0, LAT2=30 (Latitude range: 0°N to 30°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **BandeM30a00**: Band from -30°S to 0°N
         - LAT1=-30, LAT2=0 (Latitude range: 30°S to 0°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **BandeM60aM30**: Band from -60°S to -30°S
         - LAT1=-60, LAT2=-30 (Latitude range: 60°S to 30°S)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **BandeM90aM60**: Band from -90°S to -60°S
         - LAT1=-90, LAT2=-60 (Latitude range: 90°S to 60°S)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **Rapidscat**: RapidScat coverage
         - LAT1=-55, LAT2=55 (Latitude range: 55°S to 55°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **npstere**: North Polar Stereographic
         - LAT1=0, LAT2=90 (Latitude range: 0°N to 90°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

       - **spstere**: South Polar Stereographic
         - LAT1=-90, LAT2=0 (Latitude range: 90°S to 0°N)
         - LON1=-180, LON2=180 (Longitude range: 180°W to 180°E)

    """

    
    if region == 'PoleNord':
        latlons = (60, 90, -180, 180)
    elif region == 'PoleSud':
        latlons = (-90, -60, -180, 180)
    elif region == 'AmeriqueduNord':
        latlons = (25, 60, -145, -50)
    elif region == 'OuestAmeriqueduNord':
        latlons = (25, 60, -145, -97.5)
    elif region == 'AmeriqueDuNordPlus':
        latlons = (25, 85, -170, -40)
    elif region == 'Monde':
        latlons = (-90, 90, -180, 180)
    elif region == 'Global':
        latlons = (-90, 90, -180, 180)
    elif region == 'ExtratropiquesNord':
        latlons = (20, 90, -180, 180)
    elif region == 'ExtratropiquesSud':
        latlons = (-90, -20, -180, 180)
    elif region == 'HemisphereNord':
        latlons = (0, 90, -180, 180)
    elif region == 'HemisphereSud':
        latlons = (-90, 0, -180, 180)
    elif region == 'Asie':
        latlons = (25, 60, 65, 145)
    elif region == 'Europe':
        latlons = (25, 70, -10, 28)
    elif region == 'Mexique':
        latlons = (15, 30, -130, -60)
    elif region == 'Canada':
        latlons = (45, 90, -151, -50)
    elif region == 'BaieDhudson':
        latlons = (55, 90, -90, -60)
    elif region == 'Arctiquecanadien':
        latlons = (58, 90, -141, -50)
    elif region == 'EtatsUnis':
        latlons = (25, 45, -130, -70)
    elif region == 'SudestEtatsUnis':
        latlons = (25, 40, -100, -70)
    elif region == 'EstAmeriqueduNord':
        latlons = (25, 60, -97.5, -50)
    elif region == 'EstAmeriqueduNordPlus':
        latlons = (25, 85, -97.5, -50)
    elif region == 'OuestAmeriqueduNordPlus':
        latlons = (25, 85, -170, -97.5)
    elif region == 'Tropiques30':
        latlons = (-30, 30, -180, 180)
    elif region == 'Tropiques':
        latlons = (-20, 20, -180, 180)
    elif region == 'Australie':
        latlons = (-55, -10, 90, 180)
    elif region == 'Pacifique':
        latlons = (20, 65, 130, -150)
    elif region == 'Atlantique':
        latlons = (20, 65, -80, -1)
    elif region == 'Alaska':
        latlons = (50, 75, -180, -140)
    elif region == 'HIMAPEst':
        latlons = (35, 65, -105, -50)
    elif region == 'HIMAPOuest':
        latlons = (40, 65, -145, -100)
    elif region == 'ExtremeSud':
        latlons = (-90, -87, -180, 180)
    elif region == 'ExtremeNord':
        latlons = (87, 90, -180, 180)
    elif region == 'TropiquesOuest':
        latlons = (-20, 0, 180, -90)
    elif region == 'Bande60a90':
        latlons = (60, 90, -180, 180)
    elif region == 'Bande30a60':
        latlons = (30, 60, -180, 180)
    elif region == 'Bande00a30':
        latlons = (0, 30, -180, 180)
    elif region == 'BandeM30a00':
        latlons = (-30, 0, -180, 180)
    elif region == 'BandeM60aM30':
        latlons = (-60, -30, -180, 180)
    elif region == 'BandeM90aM60':
        latlons = (-90, -60, -180, 180)
    elif region == 'Rapidscat':
        latlons = (-55, 55, -180, 180)
    elif region == 'npstere':
        latlons = (0, 90, -180, 180)
    elif region == 'spstere':
        latlons = (-90, 0, -180, 180)
    else:
        raise ValueError(f'Región desconocida: {region}')
    
    LAT1, LAT2, LON1, LON2 = latlons
    LATLONS = f"{LAT1}_{LAT2},{LON1}_{LON2}"
    
    return latlons

def generate_latlon_criteria(LAT1, LAT2, LON1, LON2):
    """
    This function generates a filtering criteria expression based on latitude and longitude coordinates.

    Arguments:
    LAT1 (float): The starting latitude.
    LAT2 (float): The ending latitude.
    LON1 (float): The starting longitude.
    LON2 (float): The ending longitude.

    Returns:
    str: A filtering criteria expression.
    """
    relatopLAT = '<=' if LAT2 == 90 else '<'
    relatopLON = '<=' if LON2 == 180 else '<'

    if LON1 >= LON2:
        LATLONCRIT = (
            f" and lat >= {LAT1} and lat {relatopLAT} {LAT2} "
            f" and ((lon >= 0. and lon < {LON2}) or (lon >= {LON1} and {LON1} < 179.99))"
        )
    else:
        LATLONCRIT = (
            f" and lat >= {LAT1} and lat {relatopLAT} {LAT2} "
            f" and lon >= {LON1} and lon {relatopLON} {LON2}"
        )

    return LATLONCRIT


def flag_criteria(flags):

    """     
     Flag Criteria
     =============
     
     This function generates a filtering criteria expression based on flag selection.
     
     Flag Criteria for Filtering Elements
     ------------------------------------
     
     In data processing and analysis, flag criteria are essential for selecting and managing elements based on specific conditions or quality assessments. These criteria allow users to filter data effectively, focusing on elements that meet predefined standards or have undergone particular processing stages.
     
     Possible Flag Criteria
     ----------------------
     
      - **--flag_criteria all (all elements):**
       Selects all available elements without applying restrictions based on specific bits.
     
      - **--flag_criteria assimilee (assimilated elements):**
       Selects elements that have the BIT12 (4096) active, indicating that the element has influenced the analysis.
     
      - **--flag_criteria bgckalt (approved by Background Check):**
       Excludes elements that have the BIT9 (512) and BIT11 (2048) active, indicating rejections due to AO quality control and the selection process (thinning or canal), respectively.
      
      - **--flag_criteria bgckalt_qc (approved by Background Check and QC-Var):**
       Similar to "bgckalt", but also excludes elements with BIT9 (512) and BIT11 (2048) active.
     
      - **--flag_criteria monitoring (monitoring):**
       This filter excludes elements with BIT9 (512) and BIT7 (128) active, indicating rejection by AO quality control (Background Check or QC-Var) and being in reserve, respectively.
     
      - **--flag_criteria postalt (postal):**
       This filter excludes elements with BIT17 (131072), BIT9 (512), BIT11 (2048), and BIT8 (256) active, indicating rejection by QC-Var, AO quality control, the selection process (thinning or canal), and being in the blacklist, respectively.
     
     Description of Active Bits
     --------------------------
     
     - **BIT0 (1) - ADE:** Modified or generated by ADE.
     - **BIT1 (2) - ADE:** Element that exceeds a climatological extreme or fails consistency test.
     - **BIT2 (4) - ADE:** Erroneous element.
     - **BIT3 (8) - ADE:** Potentially erroneous element.
     - **BIT4 (16) - DERIV:** Dubious element.
     - **BIT5 (32) - DERIV:** Interpolated element, generated by DERIVATE.
     - **BIT6 (64) - DERIV:** Corrected by DERIVATE sequence or bias correction.
     - **BIT7 (128) - DERIV:** Reserved.
     - **BIT8 (256) - AO:** Element rejected because it is on a blacklist.
     - **BIT9 (512) - AO:** Element rejected by AO quality control (Background Check or QC-Var).
     - **BIT10 (1024) - AO:** Generated by AO.
     - **BIT11 (2048) - AO:** Rejected by a selection process (thinning or canal).
     - **BIT12 (4096) - AO:** Element that exceeds a climatological extreme or fails consistency test.
     - **BIT13 (8192) - AO:** Comparison against test field, level 1.
     - **BIT14 (16384) - AO:** Comparison against test field, level 2.
     - **BIT15 (32768) - AO:** Comparison against test field, level 3.
     - **BIT16 (65536) - AO:** Rejected by comparison against test field (Background Check).
     - **BIT17 (131072) - AO:** Rejected by QC-Var.
     - **BIT18 (262144) - DERIV:** Not used due to orography.
     - **BIT19 (524288) - DERIV:** Not used due to land-sea mask.
     - **BIT20 (1048576) - DERIV:** Aircraft position error detected by TrackQc.
     - **BIT21 (2097152) - QC:** Inconsistency detected by a CQ process.
     
     Args: 
     
       flags (str):  The selected flag option ('all', 'rejets_qc', 'rejets_bgck', 'assimilee', 'qc', 'bias_corr', 'bgckalt', 'bgckalt_qc', 'monitoring', 'postalt').
     
     Returns:
     
     
        str: A filtering criteria expression.
 
    """

    # Define bit masks for flag criteria
    BIT6_BIASCORR = 64  
    BIT7_REJ = 128  
    BIT8_BLACKLIST = 256
    BIT9_REJ = 512
    BIT11_SELCOR = 2048  
    BIT12_VUE = 4096 
    BIT16_REJBGCK = 65536
    BIT17_QCVAR = 131072

    # Generate filtering criteria based on the selected flag
    if flags == "all":
        FLAG = "flag >= 0"
    elif flags == "assimilee":
        FLAG = f"and (flag & {BIT12_VUE}) = {BIT12_VUE}"
    elif flags == "bgckalt":
        FLAG = f"and (flag & {BIT9_REJ}) = 0 and (flag & {BIT11_SELCOR}) = 0 and (flag & {BIT8_BLACKLIST}) = 0"
    elif flags == "bgckalt_qc":
        FLAG = f"and (flag & {BIT9_REJ}) = 0 and (flag & {BIT11_SELCOR}) = 0"
    elif flags == "monitoring":
        FLAG = f"and (flag & {BIT9_REJ}) = 0 and (flag & {BIT7_REJ}) = 0"
    elif flags == "postalt":
        FLAG = f"and (flag & {BIT17_QCVAR}) = 0 and (flag & {BIT9_REJ}) = 0 and (flag & {BIT11_SELCOR}) = 0 and (flag & {BIT8_BLACKLIST}) = 0"
    elif flags == "rejets_qc":
        FLAG = f"and (flag & {BIT9_REJ}) = {BIT9_REJ}"
    elif flags == "rejets_bgck":
        FLAG = f"and (flag & {BIT16_REJBGCK}) = {BIT16_REJBGCK}"
    elif flags == "bias_corr":
        FLAG = f"and (flag & {BIT6_BIASCORR}) = {BIT6_BIASCORR}"
    elif flags == "qc":
        FLAG = f"and (flag & {BIT9_REJ}) = 0"
    else:
        raise ValueError(f'Invalid flag option: {flags}')

    return FLAG
#doctest.testmod()
#import doctest

#if __name__ == '__main__': 
#    import doctest
#    doctest.testmod()
#    args = arg_call()    
