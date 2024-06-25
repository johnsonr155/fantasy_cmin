# project
import logging
import json
import boto3
import os
from datetime import datetime as dt
from app import conf
from ten_ds_utils.filesystem.s3 import S3Path, CLEAN_BUCKET


def import_data(filename, **kwargs):
    """
        Reads file from local/s3 depending on environment.

    Parameters
    ----------
    filename: str
        Filename of the object to read in (.csv, .xlsx, .json, .geojson)
    **kwargs:
        Additional keyword arguments to pass onto underlying read_file method.
    """

    fs = conf.filesystem()
    df_path = conf.generate_path(filename)

    return fs.read_file(df_path, **kwargs)


def save_graph_to_pickle_jar(object_to_be_pickled, filename):
    """
        Uploads and stores an object from a 10ds-dash app to s3 in
        the corresponding env as a pickle. Only used when deployed.

    Parameters
    ----------
    object_to_be_pickled: Any
        Object to be pickled and stored in s3. Usually a dcc.Graph
    filename: str
        Filename of the pickle object store - should end in '.pkl'
    """

    if not conf.is_local():
        if not filename.endswith(".pkl"):
            filename += ".pkl"

        fs = conf.filesystem()
        s3_path = S3Path(conf.data_bucket(), f"pickle-jar/{conf.app_name()}/{filename}")
        fs.upload_pickle(s3_path, object_to_be_pickled)


def write_file(df, file_name: str):
    fs = conf.filesystem()
    path = conf.generate_path(file_name)
    fs.upload_df(path, df)


def json_to_s3(package, file_name="data"):
    if conf.is_local():
        logging.info("--- Saving local data... ---")
        with open(f"{conf.data_bucket()}/{file_name}", "w") as fp:
            json.dump(package, fp)

    else:
        logging.info("--- Sending data to s3... ---")
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(conf.data_bucket())
        json_obj = bucket.Object(f"{conf.data_path()}/{file_name}")
        json_obj.put(Body=(bytes(json.dumps(package).encode("UTF-8"))))


def json_from_s3(file_name="data.json"):
    if conf.is_local():
        with open(f"{conf.data_bucket()}/{file_name}", "rb") as f:
            data = json.load(f)
    else:
        df_path = conf.generate_path(file_name)
        fs = conf.filesystem()
        data = fs.read_file(df_path)

    return data


def get_saved_scorecards_metadata():
    saved_scorecards = []
    # loop over all files
    if conf.is_local():
        logging.info("--- Loading scorecards saved locally ---")

        if conf.is_local():
            os.makedirs(
                f"{conf.data_bucket()}/saved_scorecards/metadata/", exist_ok=True
            )  # make sure path exists

        for file in os.listdir(f"{conf.data_bucket()}/saved_scorecards/metadata/"):
            metadata = json_from_s3(f"saved_scorecards/metadata/{file}")
            saved_scorecards += [metadata]

    else:
        logging.info("--- Loading scorecards saved in s3 ---")
        # get bucket in s3
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(conf.data_bucket())
        # loop over objects prefixed with 'misc/shuffle/saved_scorecards/metadata/'
        for object in bucket.objects.filter(
            Prefix=f"{conf.data_path()}/saved_scorecards/metadata/"
        ):
            if "/archived/" in object.key:
                continue

            pkl_data = object.get()["Body"].read()
            metadata = json.loads(pkl_data)
            saved_scorecards += [metadata]

    # return metadata sorted by government date (or save date if not available)
    for data_dict in saved_scorecards:
        data_dict["datetime"] = dt.strptime(data_dict["date"], "%Y-%m-%d %H:%M:%S")

    saved_scorecards = sorted(
        saved_scorecards,
        key=lambda d: d["datetime"],
        reverse=True,
    )

    return saved_scorecards


def calculate_percentage_costs(df, polic_lens="lens_1"):
    total_cost = df["cost"].sum()
    percentage_costs = {}
    for category in df[polic_lens].unique():
        cost_category = df[df[polic_lens] == category]["cost"].sum()
        percentage_costs[category] = {
            "%": round(cost_category / total_cost * 100),
            "€": round(cost_category, 1),
        }

    return percentage_costs


def move_metadata_to_archive(file_path, target_path):
    if conf.is_local():
        os.makedirs(
            f"{conf.data_bucket()}/saved_scorecards/archived_metadata/", exist_ok=True
        )
        os.rename(
            f"{conf.data_bucket()}/{file_path}", f"{conf.data_bucket()}/{target_path}"
        )

    else:
        bucket = conf.data_bucket()
        client = boto3.client("s3")
        copy_source = {"Bucket": bucket, "Key": f"{conf.data_path()}/{file_path}"}
        client.copy_object(
            Bucket=conf.data_bucket(),
            CopySource=copy_source,
            Key=f"{conf.data_path()}/{target_path}",
        )
        client.delete_object(
            Bucket=conf.data_bucket(), Key=f"{conf.data_path()}/{file_path}"
        )
