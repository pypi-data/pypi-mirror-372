import polars as pl


def summarize_n(df):
    """print cohort N and recorded days"""
    if isinstance(df, pl.LazyFrame):
        print("Skipping summarize N since inputs are Lazy.")
    elif isinstance(df, pl.DataFrame):
        print(f"N: {df.n_unique(subset='person_id')}")
        print(f"Days: {df.shape[0]}")
    else:
        print("Unknown DataFrame type...Skipping summarizing...")
