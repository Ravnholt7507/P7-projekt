import pandas as pd
import pandas as pd
def load_data():
    df = pd.read_csv("data/AIS_2023_01_01.csv")
    return df

def find_360(df):
    heading = df[(df['Heading'] == 511.0) & (df['SOG'] > 0)]
    course = df[(df['COG'] == 360.0) & (df['SOG'] > 0)]
    heading_and_course = df[(df['Heading'] == 511.0) & (df['COG'] == 360.0) & (df['SOG'] > 0)]
    return len(heading)+len(course), len(heading), len(course), len(heading_and_course)

def main():
    df = load_data()
    print("length of AIS data: ", len(df))
    init = len(df)
    filtered_df, heading, course, heading_and_course = find_360(df)
    print("length of AIS data after filtering: ", filtered_df)
    print("number of records with heading 511: ", heading)
    print("number of records with course 360: ", course)
    print("number of records with heading 511 and course 360: ", heading_and_course)
    print(heading / init * 100, "% of removed is heading 511")
    print(course / init * 100, "% of removed is course 360")
    print(heading_and_course / init * 100, "% of removed is heading 511 and course 360")
    print((filtered_df/init)*100, "% of data removed")
    print(((heading-heading_and_course)/init)*100, "removed only because of heading 511")
    print(((course-heading_and_course)/init)*100, "removed only because of course 360")

main()