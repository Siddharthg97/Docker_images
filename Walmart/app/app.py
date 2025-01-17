"""
Description - This is the entry point of markdown optimization script.
User request hits the URL with JSON request and output with markdown
recommendations is set back as JSON.
"""

__author__ = 'Suraj Bansal'
__copyright__ = '2021, Markdown Optimization'
__credits__ = ['Suyash, Preetham, Rahul, Srikant, Suraj']


import logging
import time
from datetime import timedelta


from fastapi import FastAPI, status
from typing import Dict

from src.jyotish.data_model import ItemClub as ItemClubV3_jyotish
from src.jyotish.prediction_pipeline import PredictionPipeline
from src.jyotish.requests_manager import RequestsManager
from src.v3.data_model import ItemClub as ItemClubV3
from src.v3.recommendation_pipeline import process_md_recommendation_pipeline

from src.dotcom_prediction.data_model import ItemClub as ItemClub_dotcom_prediction
from src.dotcom_prediction.prediction_pipeline import PredictionPipeline as PredictionPipeline_dotcom_prediction
from src.dotcom_prediction.requests_manager import RequestsManager as RequestsManager_dotcom_prediction
from src.dotcom_optimization.data_model import ItemClub as ItemClub_dotcom_optimization
from src.dotcom_optimization.recommendation_pipeline import process_md_recommendation_pipeline as process_md_recommendation_pipeline_dotcom_optimization
from src.config import Settings
from wmfs.feature_mart import FeatureMart
# Set Logging Configurations
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
format_ = logging.Formatter('%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')
handler.setFormatter(format_)
logger.addHandler(handler)

# Initial FastAPI app
app = FastAPI()
Settings.setup_feature_store_credentials()
feature_store= FeatureMart(fs_name='fs_bq_bt', namespace='sams')

# Root URL
@app.get("/")
def root_url():
    return {
        "status": "SUCCESS",
        "API": "Deployed Markdown Application Test 1"
    }


@app.get("/healthcheck", status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {
        "healthcheck": "SUCCESS"
    }


# V3 Jyotish API Endpoint
@app.post("/json/v3_jyotish")
def get_recommendations(data: Dict[str, ItemClubV3_jyotish]):
    logger.info("API Request received. Processing of request started")
    logger.info(f"Number of requests in the batch = {len(data)}")
    request_manager_handle = RequestsManager(data, PredictionPipeline.process_prediction_pipeline,feature_store)
    sale_prediction = request_manager_handle.process_requests()
    logger.info('Predictions Generated')

    return {
        "status": "SUCCESS",
        "data": sale_prediction
    }
# {
#   "additionalProp3": {
#     "club_nbr": "6279",
#     "product_id": "prod27341561",
#     "customer_item_nbr": "980407953",
#     "oos_date": "2024-07-30",
#     "md_start_date": "2024-07-01",
#     "current_inventory": 50,
#     "current_retail_price": 12.8,
#     "liquidation_price": 3
#   }}

# V3 API Endpoint
@app.post("/json/v3")
def get_recommendations(data: Dict[str, ItemClubV3]):
    starttime = time.perf_counter()
    #Profiling below piece of code

    logger.info("API Request received. Processing of request started")
    logger.info(f"Number of requests in the batch = {len(data)}")
    sale_prediction = process_md_recommendation_pipeline(data,feature_store)
    logger.info('Predictions Generated')

    #Profiling ends
    duration = timedelta(seconds=time.perf_counter()-starttime)
    logger.info(f"Time taken to run Markdown inclub optimization API: {duration} seconds!")

    return {
        "status": "SUCCESS",
        "data": sale_prediction
    }

@app.post("/json/dotcom_prediction")
def get_recommendations(data: Dict[str, ItemClub_dotcom_prediction]):
    logger.info("API Request received. Processing of request started")
    logger.info(f"Number of requests in the batch = {len(data)}")
    request_manager_handle = RequestsManager_dotcom_prediction(data, PredictionPipeline_dotcom_prediction.process_prediction_pipeline,feature_store)
    sale_prediction = request_manager_handle.process_requests()
    logger.info('Predictions Generated')

    return {
        "status": "SUCCESS",
        "data": sale_prediction
    }


# V3 API Endpoint
@app.post("/json/dotcom_optimization")
def get_recommendations(data: Dict[str, ItemClub_dotcom_optimization]):
    logger.info("API Request received. Processing of request started")
    logger.info(f"Number of requests in the batch = {len(data)}")
    sale_prediction = process_md_recommendation_pipeline_dotcom_optimization(data,feature_store)
    logger.info('Predictions Generated')

    return {
        "status": "SUCCESS",
        "data": sale_prediction
    }
