import json
import logging
import math

import pandas as pd
import numpy as np
from typing import Dict, Union
# from multiprocessing import Pool

from src.azure_connection import get_connection
from src.jyotish.data_model import ItemClub, ItemClubElasticity
from src.jyotish.model_loader import model_loader_handle
from src.config import Settings
import os

# Set Logging Configurations
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
format_ = logging.Formatter('%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')
handler.setFormatter(format_)
logger.addHandler(handler)


class RequestsManager():
    def __init__(self, data: Union[Dict[str, ItemClubElasticity], Dict[str, ItemClub]], pipeline_processor,feature_store):
        self.requests_data = data
        self.pipeline_processor = pipeline_processor
        self.feature_store = feature_store

    def get_distinct_club_items(self) -> set:
        club_items = set((input_data.club_nbr, input_data.customer_item_nbr)
                         for input_data in self.requests_data.values())
        return club_items

    def get_club_item_data(self) -> Dict[str, dict]:
        """Fetches Databricks data for all the club items in the input request.
        :return: Key of the output dict is request_id and value is club item info
        """

        logger.info("Pulling from Feature Store")
        Settings.setup_feature_store_credentials()

        fv = "sams_club_item_daily_v4"


        feature_names = []
        for feature in Settings.static_feature_names:
            feature_names.append(f'{fv}:{feature}')

        feature_names.remove(f'{fv}:week')
        feature_names.remove(f'{fv}:month')
        feature_names.remove(f'{fv}:club_nbr')
        feature_names.append(f'{fv}:date')

        entity_rows = [{'item_nbr': input_data.customer_item_nbr,
                        'club_nbr': input_data.club_nbr}
                       for input_data in self.requests_data.values()]
        logger.info("Store Entity created. Get Online Features func being called.")
        club_item_data_df = self.feature_store.get_online_features(
            entity_rows=entity_rows,
            features=feature_names
        ).to_df()
        club_item_data_df = club_item_data_df[club_item_data_df['department_nbr'].notna()]
        logger.info(club_item_data_df.columns)

        club_item_data_df['date'] = pd.to_datetime(club_item_data_df['date'])
        club_item_data_df['month'] = club_item_data_df['date'].dt.month
        club_item_data_df['week'] = club_item_data_df['date'].dt.isocalendar().week
        club_item_data_df = club_item_data_df.drop('date', axis=1)

        club_item_data_df = club_item_data_df.fillna(value=np.nan)
        datatype_dict = club_item_data_df.dtypes.to_dict()
        club_item_data_df = club_item_data_df.fillna(0)
        club_item_data_df = club_item_data_df.astype(datatype_dict)
        
        logger.info(club_item_data_df.head().to_string())
        
        integer_columns, _ = model_loader_handle.get_features()
        integer_columns = list(set(integer_columns) & set(club_item_data_df.columns))
        club_item_data_df[integer_columns] = club_item_data_df[integer_columns].apply(pd.to_numeric, errors='coerce')
        club_item_data_df['department_nbr'] = club_item_data_df['department_nbr'].astype('Int64')
        club_item_data_df['subclass_nbr'] = club_item_data_df['subclass_nbr'].astype('Int64')
        club_item_data_df['unit_sold_1_week_back_cnt'] = club_item_data_df['unit_sold_1_week_back_cnt'].astype('float')
        club_item_data_df['unit_sold_2_week_back_cnt'] = club_item_data_df['unit_sold_2_week_back_cnt'].astype('float')
        club_item_data_df['unit_sold_3_week_back_cnt'] = club_item_data_df['unit_sold_3_week_back_cnt'].astype('float')
        club_item_data_df['unit_sold_4_week_back_cnt'] = club_item_data_df['unit_sold_4_week_back_cnt'].astype('float')

        logger.info("Sample data fetched from Featurestore:\n" + club_item_data_df.head().to_string())
        # Assumption: club_nbr or customer_item_nbr doesn't contain '__' in its value
        club_item_data_dict = {str(x['club_nbr']) + '__' + str(x['item_nbr']): x for x in
                               club_item_data_df.to_dict(orient='records')}
        club_item_data = {}
        for request_id, input_data in self.requests_data.items():
            key = input_data.club_nbr + '__' + input_data.customer_item_nbr
            club_item_data[request_id] = club_item_data_dict.get(key, {})
        return club_item_data

    def process_requests(self) -> Dict[str, dict]:
        """Fetch club item info for all the club items in one go and then call the prediction pipeline for each request
        one by one.
        :return: Expected sale results for all the requests.
        """
        if not len(self.requests_data):
            return {}
        logger.info("Sample input Data")
        logger.info(json.dumps([val.dict() for val in self.requests_data.values()][:2], sort_keys=True, indent=4))
        logger.info("Fetching Club Item data from Feature Store")

        club_item_data = self.get_club_item_data()
        key_vals = list(zip(*self.requests_data.items()))
        # key_vals is a list of size 2. 1st element of key_vals is the tuple of request_ids and 2nd element is tuple of
        # requests
        request_ids = key_vals[0]
        requests = key_vals[1]
        club_item_data_vals = [club_item_data[request_id] for request_id in request_ids]

        # Fetching model and features data
        all_features, categorical_features = model_loader_handle.get_features()
        model = model_loader_handle.get_model()
        model_data = dict(all_features=all_features, categorical_features=categorical_features, model=model)

        logger.info("Running prediction pipeline on all the requests")
        results = list(map(self.pipeline_processor, requests, club_item_data_vals, [model_data] * len(requests)))
        # # results = list(map(self.pipeline_processor, requests, club_item_data_vals, [model_data] * len(requests)))
        # pipeline_processor_args = list(zip(requests, club_item_data_vals, [model_data] * len(requests)))
        # # num_processes = min(max(1, math.ceil(os.cpu_count() - 2)), len(requests))
        # num_processes = min(2, len(requests))
        # logger.info(f"Doing multiprocessing with {num_processes} processes")
        # chunksize = math.ceil(len(requests) / num_processes)
        # with Pool(processes=num_processes, maxtasksperchild=chunksize) as pool:
        #     results = pool.starmap(self.pipeline_processor, pipeline_processor_args, chunksize)
        logger.info('Prediction pipeline completed')
        return dict(zip(request_ids, results))

