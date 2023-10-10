# function that drops duplicates

def identify_and_drop_duplicates(df):
    """Function that will identify and drop all duplicates aside from the first appearance"""

    if df.duplicated().sum() > 0:
        print("# of duplicated row:", df.duplicated().sum())
        df_cleaned = df.drop_duplicates(keep="first")
    else:
        print("No duplicated found")
        df_cleaned = df

    return df_cleaned
