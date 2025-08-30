import pandas as pd


def recalculate_redex_data(
    energis_csv=None,
    redex_html=None,
    colname=None
):

    if energis_csv:
        df = pd.read_csv(
            energis_csv,
            sep=";",
            parse_dates=["DAY"],
            date_format="%d/%m/%Y %H:%M"
        )
    else:
        df = pd.DataFrame(columns=["DAY", colname])

    df.dropna(inplace=True)
    df.set_index("DAY", inplace=True)
    col = df.columns[0]

    html_dfs = pd.read_html(
        redex_html,
        # parse_dates=["Read date"],
        # date_format="%d/%m/%Y",
    )

    for i, html_df in enumerate(html_dfs):
        print(f"Table {i + 1}:")
        html_df.loc[:, "Read date"] = pd.to_datetime(
            html_df["Read date"],
            format="%d/%m/%Y"
        )
        html_df.set_index("Read date", inplace=True)
        html_df.loc[:, "Reading"] = html_df["Reading"].apply(
            lambda x: x.replace(",", ".").replace(" ", "")
        ).astype(float)
        print(html_df)  # Print the first few rows of each table

    for i, row in html_df.iterrows():
        if i not in df.index:
            df.loc[i, col] = row["Reading"]

    df[col] = df[col].astype(float)

    new_df = df.resample("D").interpolate(method="linear")

    return new_df
