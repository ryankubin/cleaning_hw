import pandas as pd
import numpy as np
import datetime
from pathlib import Path


def output_cleaned_csv(rootdir="/Users/ryankubin/projects/data_cleaner/data"):
    p = Path(rootdir)
    failed = []
    successful = []

    # create output file
    # this could also check for existence to see if a job has already run
    # to make this repeatable during the exercise,
    # the fcn will delete any existing file and create a new one on run
    try:
        output_file = construct_output_file(p.parent / "cleaned_data", p)
    except:
        return "Error creating output file"

    # Iterate over provided data folders
    for data_folder in p.iterdir():
        try:
            # ignore cruft or misplaced files
            if data_folder.is_dir():
                # different paths depending on starting state
                # this could have interim output files such that all files go through the same process
                # assumptions and thoughts are offered in the notes folder

                # multiple CSVs
                if len(list(data_folder.glob("**/*.csv"))) > 1:
                    process_multiple_files(data_folder, output_file)
                # single CSV
                else:
                    process_single_file(data_folder, output_file)
                successful.append(str(data_folder))
                # would typically want to mark or move these after processing to avoid duplication
        except:
            failed.append(str(data_folder))

    return {"output_file": str(output_file), "success": successful, "fail": failed}


def construct_output_file(output_directory, data_directory):
    file_name = "cleaned_geo_sample_data-" + str(datetime.date.today()) + ".csv"
    header_file = data_directory / "data_headers.csv"

    headers_df = load_data(header_file)
    headers_df.to_csv(output_directory / file_name, index=False)

    return output_directory / file_name


def process_multiple_files(d, output_destination):
    sample_data_file = d / "assay_samples.csv"
    composition_data_file = d / "chemical_compositions.csv"
    header_file = d.parent / "data_headers.csv"

    sample_df = load_data(sample_data_file)
    comp_df = load_data(composition_data_file)
    headers_df = load_data(header_file)

    # split lat_long
    sample_df[["lat", "lat_long"]] = sample_df["lat_long"].str.split(", ", expand=True)

    # rename lat_long to long for sanity's sake (could remove for performance)
    sample_df.rename(columns={"lat_long": "long"}, inplace=True)

    # group by id and transpose chemical composition values
    transposed_df = (
        comp_df.groupby(["sample_id"])["percentage"]
        .apply(lambda gf: gf.reset_index(drop=True))
        .unstack()
    )

    # remove incomplete rows
    transposed_df = transposed_df.dropna()

    # Fetch column names, and update columns with compound types and values
    column_names = list(headers_df.columns)
    compound_types = column_names[4:13]

    compound_count = 0
    for compound in compound_types:
        sample_df[compound] = transposed_df.iloc[:, compound_count].to_numpy()
        compound_count += 1

    # Clean provided compound columns
    for compound in sample_df.columns[-9:]:
        sample_df[compound] = np.where(
            (sample_df[compound] < 0) | (sample_df[compound] > 100),
            np.nan,
            sample_df[compound],
        )

    # calculated mineral composition
    sample_df["calculated_mineral_composition"] = sample_df.iloc[
        :, -len(compound_types) :
    ].sum(axis=1)

    # add company name
    sample_df.insert(0, "company_name", d.name)

    # Output results to destination file
    # Use column names to match correct output order
    sample_df.to_csv(
        output_destination, mode="a", header=False, index=False, columns=column_names
    )
    return f"Data added to file: {output_destination}"


def process_single_file(d, output_destination):
    data_file = list(d.iterdir())[0]

    df = load_data(data_file)

    # Clean provided compound columns
    for compound in df.columns[-4:]:
        df[compound] = np.where(
            (df[compound] < 0) | (df[compound] > 100), np.nan, df[compound]
        )

    # Add missing compound columns and default to None
    for i in range(1, 6):
        df["missing_compound_{}".format(i)] = None

    # Add None total calculated percentage values
    df["total_mineral_composition"] = None

    # raw calculated percentage values
    # Not making decisions on whether to include/exclude a sample based on this,
    # but likely should
    # sums could be rounded to longest decimal available, but reasonably handled elsewhere
    # hard coded columns are brittle but for sake of the exercise seem fine
    # not rounding as there is potential issues with changing levels of precision
    df["calculated_mineral_composition"] = df.iloc[:, 3:7].sum(axis=1)

    # add company name
    df.insert(0, "company_name", d.name)

    # Output results to destination file
    df.to_csv(output_destination, mode="a", header=False, index=False)
    return f"Data added to file: {output_destination}"


def load_data(data_file):
    # Load data csv columns in header, and only load those columns
    cols = pd.read_csv(data_file, nrows=1).columns
    # load data
    return pd.read_csv(data_file, usecols=cols)
