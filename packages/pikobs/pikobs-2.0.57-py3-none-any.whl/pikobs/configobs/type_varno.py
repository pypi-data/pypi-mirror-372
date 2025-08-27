def type_varno(varno):
    GRAPHE_NOMVAR = {
        '11215': ('11215:U COMPONENT OF WIND (10M)', '[m/s]', 'review type_varno.py'),
        '11216': ('11216:V COMPONENT OF WIND (10M)', '[m/s]', 'review type_varno.py'),
        '12004': ('12004:DRY BULB TEMPERATURE AT 2M', '', 'review type_varno.py'),
        '10051': ('10051:PRESSURE REDUCED TO MEAN SEA LEVEL', '', 'review type_varno.py'),
        '10004': ('10004:PRESSURE', '', 'review type_varno.py'),
        '12203': ('12203:DEW POINT DEPRESSION (2M)', '', 'review type_varno.py'),
        '12001': ('12001:TEMPERATURE/DRY BULB', '', 'review type_varno.py'),
        '11003': ('11003:U COMPONENT OF WIND', '[m/s]', 'review type_varno.py'),
        '11004': ('11004:V COMPONENT OF WIND', '[m/s]', 'review type_varno.py'),
        '12192': ('12192:DEW POINT DEPRESSION', '', 'review type_varno.py'),
        '12163': ('12163:BRIGHTNESS TEMPERATURE', '[K]', 'Channel'),
        '21014': ('21014:Doppler velocity', '[m/s]', 'Height'),
        '15036': ('15036:ATMOSPHERIC REFRACTIVITY', '', 'review type_varno.py'),
        '11001': ('11001:WIND DIRECTION', '', 'review type_varno.py'),
        '11002': ('11002:WIND SPEED', '', 'review type_varno.py'),
        '11011': ('11011:WIND DIRECTION AT 10M', '', 'review type_varno.py'),
        '11012': ('11012:WIND SPEED AT 10M', '[m/s]', 'review type_varno.py'),
        '11214': ('11214:VECTOR DIFFERENCE OF WIND', '', 'review type_varno.py'),
        '15198': ('15198:TOTAL OR PARTIAL COLUMN (DOBSON)', '', 'review type_varno.py'),
        '15008': ('15008:VOLUMETRIC MIXING RATIO(PROPORTIONED)', '', 'review type_varno.py')
    }

    # Ensure varno is a string for dictionary lookup
    varno_str = str(varno)

    # Check if the variable number is in the dictionary
    if varno_str in GRAPHE_NOMVAR:
        # If it is, retrieve the variable name and units
        variable_name, units, vcoord_type = GRAPHE_NOMVAR[varno_str]
        # Return the variable name along with its units and vcoord_type
        return variable_name, units, vcoord_type
    else:
        # If the variable number is not found, raise an exception
        raise ValueError(f"Varno '{varno}' not found in the dictionary")

