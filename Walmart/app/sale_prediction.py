import json
import logging

import pandas as pd

from src.jyotish.data_model import ItemClubElasticity
from src.jyotish.prediction_pipeline import PredictionPipeline
from src.jyotish.requests_manager import RequestsManager

# Set Logging Configurations
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
format_ = logging.Formatter('%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')
handler.setFormatter(format_)
logger.addHandler(handler)

def get_expected_sale(df: pd.core.frame.DataFrame,feature_store) -> pd.core.frame.DataFrame:
    """
    This function calls the elasticman API (API for getting the elasticity curve) for the rows in the given input
    dataframe.

    Input data is transformed in a format to pass to the elasticman API, then we call the elasticman API. The output of
    the elasticman API is merged to the input dataframe which adds elasticity_data & model_features columns to the input
    dataframe and sets the appropriate values to the no_reco_reason_code and remark column.

    :param df:
    :return:
    """
    relevant_columns = ['request_id', 'club_nbr', 'customer_item_nbr', 'md_start_date', 'oos_date', 'current_inventory',
                        'current_retail_price', 'min_md_price', 'max_md_price']
    data_json = (df
                 .filter(relevant_columns)
                 .set_index('request_id')
                 .convert_dtypes()
                 .to_json(orient='index')
                 )
     
    data_dict = json.loads(data_json)

    logger.info("Fetching the elasticity curve for the club items in the given input")
    logger.info("Sample data before fetching the elasticity curve:")
    # logger.info('\n' + df.head().transpose().to_markdown())
    data_pydantic = {key: ItemClubElasticity.parse_obj(val) for key, val in data_dict.items()}
    elasticity_generator = RequestsManager(data_pydantic, PredictionPipeline.process_elasticity_prediction_pipeline,feature_store)

    elasticity_prediction = elasticity_generator.process_requests()

    output_data = (pd.DataFrame(elasticity_prediction)
                   .transpose()
                   .rename_axis('request_id')
                   .reset_index()
                   .merge(df.drop(columns=['no_reco_reason_code', 'remark']), on='request_id', how='right')
                   .fillna(dict(no_reco_reason_code='unexpected_error', remark='no_result_from_elasticman_API'))
                   .convert_dtypes()
                   )

    return output_data
