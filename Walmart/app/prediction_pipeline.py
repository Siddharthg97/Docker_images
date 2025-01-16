import traceback
import logging

import pandas as pd

from src.jyotish.data_model import ItemClub, ItemClubElasticity
from src.jyotish.data_validation import DataValidationManager, ElasticityDataValidationManager
from src.jyotish.sale_predictor import SalePredictor, ElasticityPredictor

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
format_ = logging.Formatter('%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')
handler.setFormatter(format_)
logger.addHandler(handler)


class PredictionPipeline():
    def __init__(self):
        pass

    def validate_pre_computed_features(club_item_data: dict) -> tuple:
        if not club_item_data:
            return False, "Item-Club combination does not have enough sales data"

        logger.info("validating pre computed features")

        validation_failure_messages = []
        if not (isinstance(club_item_data.get('club_nbr'), int)):
            validation_failure_messages.append("We've encountered a problem with club number feature. Check for valid Input")

        if not isinstance(club_item_data.get('item_nbr'), int):
            validation_failure_messages.append("We've encountered a problem with item number feature. Check for valid input")
        # FIXME: Ensure that region_name, category_nbr & subcategory_nbr belong to the set on which model is trained

        if not isinstance(club_item_data.get('subclass_nbr'), int):
            validation_failure_messages.append("We've encountered a problem with subcategory feature. Please create a support incident through the Help menu for this issue")

        if not isinstance(club_item_data.get('department_nbr'), int):
            validation_failure_messages.append("We've encountered a problem with category feature. Please create a support incident through the Help menu for this issue")

        #Tech Debt: Need to handle multiple cases
        #if not isinstance(club_item_data.get('day_on_shelf_cnt'), float):
        #    validation_failure_messages.append("We've encountered a problem with on-shelf feature. Please create a support incident through the Help menu for this issue")

        if not isinstance(club_item_data.get('median_price_6_month_last_amt'), float):
            validation_failure_messages.append("We've encountered a problem with price feature. Please create a support incident through the Help menu for this issue")
        if not isinstance(club_item_data.get('price_1_week_back_median_price_6_month_last_nbr'), float):
            validation_failure_messages.append("We've encountered a problem with price features. Please create a support incident through the Help menu for this issue")

        if not isinstance(club_item_data.get('price_2_week_back_median_price_6_month_last_nbr'), float):
            validation_failure_messages.append("We've encountered a problem with price features. Please create a support incident through the Help menu for this issue")
        if not isinstance(club_item_data.get('price_3_week_back_median_price_6_month_last_nbr'), float):
            validation_failure_messages.append("We've encountered a problem with price features. Please create a support incident through the Help menu for this issue")
        if not isinstance(club_item_data.get('price_4_week_back_median_price_6_month_last_nbr'), float):
            validation_failure_messages.append("We've encountered a problem with price features. Please create a support incident through the Help menu for this issue")

        if not (isinstance(club_item_data.get('unit_sold_1_week_back_cnt'), float) and club_item_data[
            'unit_sold_1_week_back_cnt'] >= 0):
            validation_failure_messages.append("We've encountered a problem with week sale units. Please create a support incident through the Help menu for this issue")

        if not (isinstance(club_item_data.get('unit_sold_2_week_back_cnt'), float) and club_item_data[
            'unit_sold_2_week_back_cnt'] >= 0):
            validation_failure_messages.append("We've encountered a problem with week sale units. Please create a support incident through the Help menu for this issue")

        if not (isinstance(club_item_data.get('unit_sold_3_week_back_cnt'), float) and club_item_data[
            'unit_sold_3_week_back_cnt'] >= 0):
            validation_failure_messages.append("We've encountered a problem with week sale units. Please create a support incident through the Help menu for this issue")

        if not (isinstance(club_item_data.get('unit_sold_4_week_back_cnt'), float) and club_item_data[
            'unit_sold_4_week_back_cnt'] >= 0):
            validation_failure_messages.append("We've encountered a problem with week sale units. Please create a support incident through the Help menu for this issue")

        if validation_failure_messages:
            return False, "; ".join(validation_failure_messages)

        return True, ""

    def format_output(input_data: ItemClub, outlier: str, expected_sale_units: int = None, model_features: dict = None,
                      remark: str = "") -> dict:
        """
        Format the output in the format as defined in the IO doc.
        :param outlier:
        :param expected_sale_units:
        :param model_features:
        :param remark:
        :return: formatted output
        """
        op_cols_from_ip = ['club_nbr', 'customer_item_nbr', 'md_start_date', 'md_session_details', 'current_inventory',
                           'current_retail_price']
        ip_dict = input_data.dict()
        formatted_output = {key: ip_dict[key] for key in op_cols_from_ip}
        if model_features is None:
            model_features = {}
        op_generated = dict(outlier=outlier, expected_sale_units=expected_sale_units, model_features=model_features,
                            remark=remark)
        logger.info(f"Output data formatted")
        formatted_output.update(op_generated)
        return formatted_output

    def format_elasticity_output(no_reco_reason_code: str, elasticity_data: pd.core.frame.DataFrame = None,
                                 model_features: dict = None, remark: str = "") -> dict:
        """
        Format the output in the format defined for the Elasticman API

        :param elasticity_data:
        :param model_features:
        :param remark:
        :return:
        """
        if model_features is None:
            model_features = {}
        formatted_output = dict(no_reco_reason_code=no_reco_reason_code, elasticity_data=elasticity_data,
                                model_features=model_features, remark=remark)
        return formatted_output

    # FIXME: Define input and output data types for all the functions. Write documentation of all functions
    def process_prediction_pipeline(input_data: ItemClub, club_item_data: dict, model_data: dict) -> dict:
        """
        Perform all the steps to get the expected sales for the given club item
        :param club_item_data:
        :param model_data:
        :return:
        """
        try:
            validation_handle = DataValidationManager(input_data)
            validation_status, validation_message = validation_handle.validate_input_data()
            logger.info(f"Input data validation Status: {validation_status}")

            output = None
            if validation_status:
                validation_status, validation_message = PredictionPipeline.validate_pre_computed_features(
                    club_item_data)
                logger.info(f"Pre computed data validation Status: {validation_status}")

                if validation_status:
                    sale_predictor_handle = SalePredictor(input_data, club_item_data, model_data)
                    expected_sale, outlier, model_features, remark = sale_predictor_handle.get_sale_prediction()
                    output = PredictionPipeline.format_output(input_data, 
                                                              outlier, 
                                                              expected_sale_units=expected_sale,
                                                              model_features=model_features, 
                                                              remark=remark)
                else:
                    output = PredictionPipeline.format_output(input_data, 'incomplete_info', remark=validation_message)
            else:
                output = PredictionPipeline.format_output(input_data, "invalid_input", remark=validation_message)

            op_validation_status, op_validation_message = validation_handle.validate_output_data(output)
            logger.info(op_validation_message)

            if op_validation_status:
                return output
            else:
                # If output we got so far is not in a valid format, then return a dummy output.
                return PredictionPipeline.format_output(input_data, "unexpected_error", remark=op_validation_message)
        except Exception as e:
            return PredictionPipeline.format_output(input_data, "unexpected_error", remark=traceback.format_exc())

    def process_elasticity_prediction_pipeline(input_data: ItemClubElasticity, club_item_data: dict,
                                               model_data: dict) -> dict:
        """
        Run the complete pipeline to get elasticity data.

        First validate the input data. If validation succeeds, validate the pre-computed features fetched from the DB.
        If validation succeeds, get the elasticity curve from the Elasticity prediction module. After this format the
        output obtained from Elasticity prediction module. If validation fails at any stage, or the code throws some
        error, create an output with no_reco_reason_code accordingly. Output validation is called on the output
        generated.
        :param club_item_data:
        :param model_data:
        :return:
        """
        try:

            validation_handle = ElasticityDataValidationManager(input_data)
            validation_status, validation_message = validation_handle.validate_input_data()
            if validation_status:
                validation_status, validation_message = PredictionPipeline.validate_pre_computed_features(
                    club_item_data)
                if validation_status:
                    elasticity_predictor_handle = ElasticityPredictor(input_data, club_item_data, model_data)
                    elasticity_data, model_features, no_reco_reason_code, remark = \
                        elasticity_predictor_handle.get_elasticity_prediction()

                    output = PredictionPipeline.format_elasticity_output(no_reco_reason_code,
                                                                         elasticity_data=elasticity_data,
                                                                         model_features=model_features, 
                                                                         remark=remark)

                else:
                    output = PredictionPipeline.format_elasticity_output('incomplete_info', remark=validation_message)
            else:
                output = PredictionPipeline.format_elasticity_output('invalid_input', remark=validation_message)
            op_validation_status, op_validation_message = validation_handle.validate_output_data(output)
            if op_validation_status:
                return output
            else:
                # If output we got so far is not in a valid format, then return a dummy output.
                return PredictionPipeline.format_elasticity_output("unexpected_error", remark=op_validation_message)
        except Exception as e:
            return PredictionPipeline.format_elasticity_output("unexpected_error", remark=traceback.format_exc())
