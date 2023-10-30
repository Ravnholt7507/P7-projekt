import pandas as pd
def cleanse():
    pd.set_option('display.max_columns', 20)

    n = 150000  # number of records in file

    df = pd.read_csv('data/AIS_2023_01_01.csv',nrows=n)
    # Sort by MMSI
    df = df.sort_values(by=['MMSI', 'BaseDateTime'])

    # Take ships where the SOG is greater than 5
    df = df[df.SOG > 5]

    # Take ships where lat is between 30 and 50 and lon is between -130 and -110
    df = df[(df.LAT > 23) & (df.LAT < 24) & (df.LON > -82) & (df.LON < -80)]

    # group = df.groupby("MMSI")

    #Take row where MMSI is
    # group1 = group.get_group(636093085)
    # group2 = group.get_group(310731000)

    #Combine the two groups
    # group = pd.concat([group1, group2])

    # Cleasing data so there is only on row per MMSI
    df = df.drop_duplicates(subset='MMSI', keep='first')

    # # Remove all rows
    # df = df.iloc[0:0]
    
    df.to_csv('data/1_boats.csv', index=False)
