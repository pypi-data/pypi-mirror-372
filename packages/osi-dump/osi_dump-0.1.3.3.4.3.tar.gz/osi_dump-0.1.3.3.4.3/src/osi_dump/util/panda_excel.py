import pandas as pd

from pandas import DataFrame


def expand_list_column(df, column):
    # Find the maximum length of the list in the column
    max_len = df[column].apply(len).max()

    # Expand each dictionary in the list into columns
    expanded_df = pd.DataFrame(
        df[column]
        .apply(lambda x: [{**item} for item in x] + [{}] * (max_len - len(x)))
        .tolist(),
        index=df.index,
    )

    # Flatten the nested dictionaries into separate columns
    expanded_df = pd.json_normalize(expanded_df.to_dict(orient="records"))

    expanded_df = expanded_df.add_prefix(column)

    # Drop the original column and join the expanded columns
    df = df.drop(column, axis=1).join(expanded_df)

    return df
