import pandas as pd


def round_large_numbers_to_string(number):
    """
    Rounds large numbers to billions/millions/thousands.
    Keeps one decimal place if the number is between 1 and 10 (after removing billions/m/k), otherwise 0 decimals.
    """
    if number >= 10**9:
        dps = 1 if number < 10**10 else 0
        output = f"{round(number/10**9, dps)}bn"

    elif number >= 10**6:
        dps = 1 if number < 10**7 else 0
        output = f"{round(number/10**6, dps)}m"

    elif number >= 10**3:
        dps = 1 if number < 10**4 else 0
        output = f"{round(number/10**3, dps)}k"

    else:
        dps = 1 if number < 10 else 0
        output = f"{round(number, dps)}"

    return output.replace(".0", "")


def convert_metric_to_text(number, metric):
    if pd.isna(metric):  # deals with missing values
        metric = ""

    # define metric text
    metric_prefix = "£" if "£" in metric else ""
    metric_suffix = (
        metric.replace(" ", "") if metric in ["", "%", "GW", "ha"] else " " + metric
    )
    metric_suffix = "" if metric in ["£"] else metric_suffix

    # put it together
    return metric_prefix + round_large_numbers_to_string(number) + metric_suffix
