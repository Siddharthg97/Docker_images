import json
import logging
import time
from datetime import timedelta

import pandas as pd
from typing import Dict, Union

from src.v3.business_policy_utils import get_min_max_price, modify_reco_as_per_business_policy, \
    apply_business_policy_for_min_md_price
from src.v3.data_model import ItemClub
from src.v3.data_validation import validate_input, validate_output, format_output_as_dict
from src.v3.optimization import get_optimal_point
from src.v3.sale_prediction import get_expected_sale

# Set Logging Configurations
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
format_ = logging.Formatter('%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')
handler.setFormatter(format_)
logger.addHandler(handler)


def outlier_manager(function):
    """
    Defines a decorator on top of the given function and returns that decorated function
    :param function:
    :return:
    """

    def decorated_function(data: Union[pd.core.series.Series, pd.core.frame.DataFrame], *args, **kwargs) -> Union[
        pd.core.series.Series, pd.core.frame.DataFrame]:
        """
        In the situation of given data being a pandas series, if the given data has no_reco_reason_code as
        recommendation_successful then the given `function` is called and the output of the function is returned,
        otherwise input data is returned as it is.

        In case the given data is a dataframe, given `function` is applied only on those rows which have
        no_reco_reason_code as recommendation_successful. Output of this function is concatenated with the rows of the
        data that didn't have no_reco_reason_code as recommendation_successful, and then finally returned as output.
        :param data:
        :return:
        """
        if isinstance(data, pd.core.series.Series):
            if data['no_reco_reason_code'] == 'recommendation_successful':
                return function(data, *args, **kwargs)
            else:
                return data
        elif isinstance(data, pd.core.frame.DataFrame):
            valid_data = data[data['no_reco_reason_code'] == 'recommendation_successful']
            invalid_data = data[data['no_reco_reason_code'] != 'recommendation_successful']
            if valid_data.empty:
                return invalid_data
            else:
                return pd.concat([function(valid_data, *args, **kwargs), invalid_data])

    return decorated_function


def process_md_recommendation_pipeline(input_data: Dict[str, ItemClub],feature_store) -> Dict[str, dict]:
    """
    Given the relevant details of the club items, this function identifies the optimal markdown price for the club item.
    If start date is not provided, function identifies the optimal start date as well.

    Input data is passed through a series of steps i.e. Expected sale calculation, business policy application, revenue
    optimisation etc. After all these steps we get the recommended markdown price and the recommended start date

    :param input_data:
    :return:
    """
    starttime = time.perf_counter()
    #Profiling below piece of code

    data_list = [dict(value.dict(), request_id=key) for key, value in input_data.items()]
    logger.info("Sample input data:")
    logger.info(json.dumps(data_list[:3], sort_keys=True, indent=4))

    input_pd_df = pd.DataFrame(data_list)
    logger.info("Input Dataframe info:")
    logger.info(input_pd_df.info())

    #Profiling ends
    duration = timedelta(seconds=time.perf_counter()-starttime)
    logger.info(f"Time taken to create the input dataset: {duration} seconds!")

    starttime = time.perf_counter()
    #Profiling below piece of code

    output_dict = (input_pd_df
                   .assign(no_reco_reason_code='recommendation_successful',
                           remark='')
                   .convert_dtypes()
                   # Input and output are pandas dataframe with same set of columns
                   .apply(validate_input, axis=1)
                   # Input and output are pandas dataframe and output has following additional columns:
                   # 1. max_md_price, 2. min_md_price
                   .apply(outlier_manager(get_min_max_price), axis=1)
                   # Input and output are pandas dataframe and output has following additional columns:
                   # 1. elasticity_data, 2. model_features
                   .pipe(outlier_manager(get_expected_sale), feature_store=feature_store)
                   # Input and output are pandas dataframe with same set of columns
                   .apply(outlier_manager(apply_business_policy_for_min_md_price), axis=1)
                   # Input and output are pandas dataframe and output has following additional columns:
                   # 1. markdown_recommendation, 2. expected_sale_units, 3. expected_revenue,
                   # 4. week_level_expected_sale_units
                   .apply(outlier_manager(get_optimal_point), axis=1)
                   # Input and output are pandas dataframe with same set of columns
                   .apply(outlier_manager(modify_reco_as_per_business_policy), axis=1)
                   # Input is a pandas dataframe and output is a dictionary
                   .pipe(format_output_as_dict)
                   )
    
    #Profiling ends
    duration = timedelta(seconds=time.perf_counter()-starttime)
    logger.info(f"Time taken to create the output dataset as a dictionary: {duration} seconds!")

    starttime = time.perf_counter()
    #Profiling below piece of code

    # TODO: Do exception handling for the complete code
    output_dict = validate_output(input_data, output_dict)

    #Profiling ends
    duration = timedelta(seconds=time.perf_counter()-starttime)
    logger.info(f"Time taken to validate the output dataset as a dictionary: {duration} seconds!")

    logger.info("Sample output data")
    logger.info(json.dumps(dict(list(output_dict.items())[0:3]), sort_keys=True, indent=4))
    return output_dict
