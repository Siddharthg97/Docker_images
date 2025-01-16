"""
Description - Module to Validate Input Request
"""

__author__ = 'Rahul Kumar'
__copyright__ = '2021, Markdown Optimization'
__credits__ = ['Rahul', 'Srikant', 'Suraj', 'Jaspreet', 'Suyash']
__maintainer__ = '{Suyash}'
__email__ = ['Suyash.Garg@walmart.com']
__status__ = 'Development'

import datetime
import json
import logging
import traceback
import time
from datetime import timedelta

import pandas as pd
from typing import Dict
from numba import jit

from src.config import Settings
from src.utils import is_equal
from src.v3.data_model import ItemClub

# Set Logging Configurations
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
format_ = logging.Formatter('%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')
handler.setFormatter(format_)
logger.addHandler(handler)


def validate_club_nbr(data: pd.core.series.Series) -> str:
    if isinstance(data['club_nbr'], str):
        return ''
    else:
        return "We've encountered a problem with club number format. Check for valid Input eg: '8299'"


def validate_customer_item_nbr(data: pd.core.series.Series) -> str:
    if isinstance(data['customer_item_nbr'], str):
        return ''
    else:
        return "We've encountered a problem with item number format. Check for valid input eg: '980254364'"


def validate_current_inventory(data: pd.core.series.Series) -> str:
    """
    Description - Function Validates the Current Inventory Information
    """
    # We are not validating the int data type of current_inventory since that check will be done by fastapi itself as
    # per the input datatype defined in the data_model.py. Similarly, we are not checking datatypes for other input
    # fields
    if data['current_inventory'] > 0:
        return ''
    else:
        return "Current on hands are less than or equal to zero. On hands must be positive to recommend a price."


def validate_current_price(data: pd.core.series.Series) -> str:
    """
    Description - Function Validates the Current Price Information
    """
    if data['current_retail_price'] > 0:
        return ''
    else:
        return "We've encountered a problem with retail price data. Please create a support incident through the Help menu for this issue"


def validate_liquidation_price(data: pd.core.series.Series) -> str:
    """
    Description - Function Validates the Liquidation Price
    """

    if data['liquidation_price'] >= 0:
        return ''
    else:
        return "We've encountered a problem with liquidation price data. Please create a support incident through the Help menu for this issue."


def validate_outofstock_date(data: pd.core.series.Series) -> str:
    """
    Description - Function Validates the OOS Date
    """
    try:
        # TODO: Pick the date format from config file
        oos_date = datetime.datetime.strptime(data['oos_date'], "%Y-%m-%d").date()
    except ValueError:
        return "We've encountered a problem with the Out-of-stock date format. Please create a support incident through the Help menu for this issue."
    today = datetime.date.today()
    date_difference = (oos_date - today).days

    # Check if Out of Stock Date is Within 8 Weeks from Today
    if date_difference >= Settings.max_forecast_weeks * 7:
        return f'Out-of-stock date cannot be more than {Settings.max_forecast_weeks} Weeks from today date'
    if (Settings.enable_historic_data_requests is False) and (date_difference < 0):
        return 'OOS Date is in Past'
    return ''


def validate_mdstart_date(data: pd.core.series.Series) -> str:
    """
    Description - Function Validates the Markdown Start Date
    """

    if not pd.isna(data['md_start_date']):
        try:
            md_start_date = datetime.datetime.strptime(data['md_start_date'], "%Y-%m-%d").date()
        except ValueError:
            return "We've encountered a problem with the Markdown start date format. Please create a support incident through the Help menu for this issue.t"
        today = datetime.date.today()
        date_difference = (md_start_date - today).days
        # Check if Start Date is not a Historic Date
        if (Settings.enable_historic_data_requests is False) and (date_difference < 0):
            return 'Markdown Start Date is in Past'
        # Check if Start Date is Within 8 Weeks from Today
        if date_difference >= Settings.max_forecast_weeks * 7:
            return f'Markdown start date cannot be more than {Settings.max_forecast_weeks} Weeks from today date'

    return ''


def validate_sell_through_threshold(data: pd.core.series.Series) -> str:
    if not pd.isna(data['sell_through_threshold']):
        stt = data['sell_through_threshold']
        if not (0 <= stt <= 1):
            return "DS model couldn't compute a valid recommendation. Please create a support incident through the Help menu for this issue."
    return ''


def validate_cross_features(data: pd.core.series.Series) -> str:
    """
    Do validations which require interaction of multiple features
    :param data:
    :return:
    """
    if not pd.isna(data['md_start_date']):
        md_start_date = datetime.datetime.strptime(data['md_start_date'], "%Y-%m-%d").date()
        oos_date = datetime.datetime.strptime(data['oos_date'], "%Y-%m-%d").date()
        if (oos_date - md_start_date).days < 6:
            return "Out-of-stock date must be at least 6 days after markdown start date."

    if data['liquidation_price'] > data['current_retail_price']:
        return 'Liquidation price is greater than current retail price.'

    return ''


@jit(parallel=True)
def validate_input(item_club_data: pd.core.series.Series) -> pd.core.series.Series:
    """
    Validates each of the input field passed in the input of the V3 API and sets the value of no_reco_reason_code and
    remark accordingly
    """
    starttime = time.perf_counter()
    #Profiling below piece of code

    failure_remarks = []

    # Pipeline of all the Validation Functions

    failure_remarks.append(validate_club_nbr(item_club_data))
    failure_remarks.append(validate_customer_item_nbr(item_club_data))
    failure_remarks.append(validate_outofstock_date(item_club_data))
    failure_remarks.append(validate_mdstart_date(item_club_data))
    failure_remarks.append(validate_sell_through_threshold(item_club_data))
    failure_remarks.append(validate_current_inventory(item_club_data))
    failure_remarks.append(validate_current_price(item_club_data))
    failure_remarks.append(validate_liquidation_price(item_club_data))
    failure_remarks.append(validate_cross_features(item_club_data))

    # Check if there is validation failure remark from any of the Validation Functions
    failure_remarks = [remark for remark in failure_remarks if remark]
    final_remark = '; '.join(failure_remarks)
    item_club_data['no_reco_reason_code'] = 'invalid_input' if final_remark else 'recommendation_successful'
    item_club_data['remark'] = final_remark

    #Profiling ends
    duration = timedelta(seconds=time.perf_counter()-starttime)
    logger.info(f"Time taken in validate_input(): {duration} seconds!")

    return item_club_data

def get_dummy_output(input_data: ItemClub, no_reco_reason_code: str, remark: str) -> dict:
    input_dict = input_data.dict()
    # Setting fields in input to same value and rest of the fields to None
    output_dict = {col: input_dict.get(col) for col in Settings.output_cols}
    output_dict['no_reco_reason_code'] = no_reco_reason_code
    output_dict['remark'] = remark
    return output_dict


def validate_same_request_ids_in_input_and_output(input_data: Dict[str, ItemClub], output_data: Dict[str, dict]) -> \
        Dict[str, dict]:
    """
    Validate that request IDs in input and output are same. Also ensure that common fields in input and output contain
    the same value. If validation fails, replace output for that request with dummy output containing the
    unexpected_error message.
    :param input_data:
    :param output_data:
    :return:
    """
    if len(input_data) != len(output_data):
        logger.error("We've encountered a problem with the output values in this plan ID. Please create a support incident through the Help menu for this issue.")
    output_data = {key: value for key, value in output_data.items() if key in input_data}
    requests_only_in_input = input_data.keys() - output_data.keys()
    for request_id in requests_only_in_input:
        remark = 'We have encountered a problem with the output values in this plan ID. Please create a support incident through the Help menu for this issue.'
        output_data[request_id] = get_dummy_output(input_data[request_id], 'unexpected_error', remark)

    # Ensure that common fields in input and output contain the same value
    for request_id, input_obj in input_data.items():
        input_dict = input_obj.dict()
        common_keys = set(input_dict.keys()).intersection(Settings.output_cols)
        output_dict = output_data[request_id]
        # If the value is float, we don't want to compare till maximum decimal precision since this precision tends to
        # change because of different float number storage approaches
        if not all([is_equal(input_dict[key], output_dict.get(key), 0.001) if isinstance(input_dict[key], float) else
                    input_dict[key] == output_dict.get(key) for key in common_keys]):
            remark = 'We have encountered a problem with the output values in this plan ID. Please create a support incident through the Help menu for this issue.'
            output_data[request_id] = get_dummy_output(input_obj, 'unexpected_error', remark)

    return output_data


def validate_markdown_recommendation(output: dict) -> list:
    validation_failure_remarks = []
    if isinstance(output['no_reco_reason_code'], str) and output['no_reco_reason_code'] == 'recommendation_successful':
        if isinstance(output['markdown_recommendation'], list) and (len(output['markdown_recommendation']) > 0):
            oos_date = datetime.datetime.strptime(output['oos_date'], "%Y-%m-%d").date()
            for recommendation in output['markdown_recommendation']:
                today = datetime.date.today()
                session_date = datetime.datetime.strptime(recommendation['markdown_session_start_date'],
                                                          "%Y-%m-%d").date()
                if not (today <= session_date <= oos_date):
                    validation_failure_remarks.append("We've encountered a problem providing a valid recommended price or markdown start date. Please create a support incident through the Help menu for this issue")
                if not (0 < recommendation['recommended_markdown_price'] <= output['current_retail_price']):
                    validation_failure_remarks.append("We've encountered a problem providing a valid recommended price or markdown start date. Please create a support incident through the Help menu for this issue")
        else:
            validation_failure_remarks.append("We've encountered a problem providing a valid recommended price or markdown start date. Please create a support incident through the Help menu for this issue")
    else:
        if output['markdown_recommendation'] is not None:
            validation_failure_remarks.append("We've encountered a problem providing a valid recommended price or markdown start date. Please create a support incident through the Help menu for this issue")
    return validation_failure_remarks


def validate_expected_sale_units(output: dict) -> list:
    validation_failure_remarks = []
    if isinstance(output['no_reco_reason_code'], str) and output['no_reco_reason_code'] == 'recommendation_successful':
        expected_sale = output['expected_sale_units']
        if not (isinstance(expected_sale, int) and 0 <= expected_sale <= output['current_inventory']):
            validation_failure_remarks.append("Recommendation exceeds current inventory. Please create support incident through the Help menu for this issue")
    else:
        if output['expected_sale_units'] is not None:
            validation_failure_remarks.append("Recommendation exceeds current inventory. Please create support incident through the Help menu for this issue")
    return validation_failure_remarks


def validate_week_level_expected_sale_units(output: dict) -> list:
    validation_failure_remarks = []
    if isinstance(output['no_reco_reason_code'], str) and output['no_reco_reason_code'] == 'recommendation_successful':
        weekly_sale = [data['expected_sale_units'] for data in output['week_level_expected_sale_units']]
        if not all([(sale >= 0) for sale in weekly_sale if sale!= None]):
            validation_failure_remarks.append("We've encountered a problem with data quality checks. Please create a support incident through the Help menu for this issue")
        elif round(sum(filter(None, weekly_sale))) > output['current_inventory']:
            validation_failure_remarks.append("We've encountered a problem with data quality checks. Please create a support incident through the Help menu for this issue")
        # elif round(sum(weekly_sale)) != output['expected_sale_units']:
        #     validation_failure_remarks.append("week_level_expected_sale_units sum is not equal to expected_sale_units")
        try:
            today = datetime.date.today()
            if any([(datetime.datetime.strptime(data['start_date'], "%Y-%m-%d").date() - today).days != week_index * 7
                    for week_index, data in enumerate(output['week_level_expected_sale_units'])]):
                validation_failure_remarks.append("We've encountered a problem with data quality checks. Please create a support incident through the Help menu for this issue")
            if any([(datetime.datetime.strptime(data['end_date'], "%Y-%m-%d").date() - today).days != week_index * 7 + 6
                    for week_index, data in enumerate(output['week_level_expected_sale_units'][:-1])]):
                validation_failure_remarks.append("We've encountered a problem with data quality checks. Please create a support incident through the Help menu for this issue")
            if output['week_level_expected_sale_units'][-1]['end_date'] != output['oos_date']:
                validation_failure_remarks.append("We've encountered a problem with data quality checks. Please create a support incident through the Help menu for this issue")
        except Exception as e:
            validation_failure_remarks.append("We've encountered a problem with data quality checks. Please create a support incident through the Help menu for this issue")
    else:
        if output['week_level_expected_sale_units'] is not None:
            validation_failure_remarks.append("We've encountered a problem with data quality checks. Please create a support incident through the Help menu for this issue")
    return validation_failure_remarks


def validate_expected_revenue(output: dict) -> list:
    validation_failure_remarks = []
    if isinstance(output['no_reco_reason_code'], str) and output['no_reco_reason_code'] == 'recommendation_successful':
        max_possible_revenue = output['current_retail_price'] * output['current_inventory']
        expected_revenue = output['expected_revenue']
        if not (isinstance(expected_revenue, (int, float)) and (0 <= expected_revenue <= max_possible_revenue + 0.01)):
            validation_failure_remarks.append("We've encountered a problem with data quality checks. Please create a support incident through the Help menu for this issue")
    else:
        if output['expected_revenue'] is not None:
            validation_failure_remarks.append("We've encountered a problem with data quality checks. Please create a support incident through the Help menu for this issue")
    return validation_failure_remarks


def validate_model_features(output: dict) -> list:
    validation_failure_remarks = []
    if isinstance(output['no_reco_reason_code'], str) and output['no_reco_reason_code'] == 'recommendation_successful':
        if not (isinstance(output['model_features'], dict) and (len(output['model_features']) > 0)):
            validation_failure_remarks.append("We've encountered a problem with the output features in this plan ID. Please create a support incident through the Help menu for this issue")
    return validation_failure_remarks

def validate_no_reco_reason_code(output: dict) -> list:
    validation_failure_remarks = []
    if output['no_reco_reason_code'] not in Settings.valid_no_reco_reason_code:
        validation_failure_remarks.append("We've encountered a problem with the output error reason in this plan ID . Please create a support incident through the Help menu for this issue")
    return validation_failure_remarks


def validate_remark(output: dict) -> list:
    validation_failure_remarks = []
    if not (isinstance(output['remark'], str) or output['remark'] is None):
        validation_failure_remarks.append("We've encountered a problem with data quality checks. Please create a support incident through the Help menu for this issue")
    return validation_failure_remarks


def validate_output_field_values(input_data: Dict[str, ItemClub], output_data: Dict[str, dict]) -> Dict[str, dict]:
    """
    Validate output fields (apart from the ones which are directly inherited from the input). If validation fails,
    replace output for that request with dummy output containing the unexpected_error message

    :param input_data:
    :param output_data:
    :return:
    """
    erroneous_output = {}
    for request_id, output in output_data.items():
        try:
            validation_failure_remarks = []
            validation_failure_remarks.extend(validate_markdown_recommendation(output))
            validation_failure_remarks.extend(validate_expected_sale_units(output))
            validation_failure_remarks.extend(validate_week_level_expected_sale_units(output))
            validation_failure_remarks.extend(validate_expected_revenue(output))
            validation_failure_remarks.extend(validate_model_features(output))
            validation_failure_remarks.extend(validate_no_reco_reason_code(output))
            validation_failure_remarks.extend(validate_remark(output))
            if validation_failure_remarks:
                remark = '; '.join(validation_failure_remarks)
                erroneous_output[request_id] = get_dummy_output(input_data[request_id], 'unexpected_error', remark)
        except Exception as e:
            erroneous_output[request_id] = get_dummy_output(input_data[request_id], 'unexpected_error',
                                                            traceback.format_exc())
    output_data.update(erroneous_output)
    return output_data


def validate_max_price_policy(output: dict) -> list:
    for recommendation in output['markdown_recommendation']:
        price_reco = recommendation['recommended_markdown_price']
        current_retail_price = output['current_retail_price']
        if (price_reco > current_retail_price * (100 - Settings.min_percent_discount) / 100 + 0.01) or (
                price_reco > current_retail_price - Settings.min_dollar_discount + 0.01):
            return ["No price recommendation within allowable range."]
    return []


def validate_min_price_policy(output: dict) -> list:
    for recommendation in output['markdown_recommendation']:
        price_reco = recommendation['recommended_markdown_price']
        if price_reco < output['liquidation_price'] * (1 + Settings.buffer_percent_over_liquidation / 100) - 0.01:
            return ['No price recommendation within allowable range']
        if price_reco < Settings.min_markdown_price.get(str(output['model_features']['department_nbr']), 0) - 0.01:
            return ['No price recommendation within allowable range']
    return []


def validate_ninety_nine_cent_policy(output: dict) -> list:
    for recommendation in output['markdown_recommendation']:
        price_reco = recommendation['recommended_markdown_price']
        if is_equal(int(price_reco) + 0.99, price_reco):
            return ["We've encountered a problem with price point ending validation. Please create a support incident through the Help menu for this issue"]
    return []


def validate_critical_price_point_policy(output: dict) -> list:
    """
    Validate the apparel/teo policy which says that markdown recommendation for the items in apparel/teo categories should end
    by specific cents value only.

    :param output:
    :return:
    """
    for i in Settings.dict_critical_pp_cat_list:
        if output['model_features']['department_nbr'] in Settings.dict_critical_pp_cat_list[i]:
            for recommendation in output['markdown_recommendation']:
                price_reco = recommendation['recommended_markdown_price']
                price_reco_fraction = price_reco - int(price_reco)
                if not any([is_equal(price_reco_fraction, price_fraction) for price_fraction in Settings.dict_critical_pp_list[i]  ]):
                    return ["We've encountered a problem with price point ending validation. Please create a support incident through the Help menu for this issue"]
    return []


def validate_business_policy(input_data: Dict[str, ItemClub], output_data: Dict[str, dict]) -> Dict[str, dict]:
    """
    Validate all the business policies on the output we have got. If validation fails, replace output for that request
    with dummy output containing the unexpected_error message.

    :param input_data:
    :param output_data:
    :return:
    """
    erroneous_output = {}
    for request_id, output in output_data.items():
        if output['no_reco_reason_code'] == 'recommendation_successful':
            validation_failure_remarks = []
            validation_failure_remarks.extend(validate_max_price_policy(output))
            validation_failure_remarks.extend(validate_min_price_policy(output))
            validation_failure_remarks.extend(validate_ninety_nine_cent_policy(output))
            validation_failure_remarks.extend(validate_critical_price_point_policy(output))
            if validation_failure_remarks:
                remark = '; '.join(validation_failure_remarks)
                erroneous_output[request_id] = get_dummy_output(input_data[request_id], 'unexpected_error', remark)
    output_data.update(erroneous_output)
    return output_data


def validate_output(input_data: Dict[str, ItemClub], output_data: Dict[str, dict]) -> Dict[str, dict]:
    """"Following Points are validated:
        1. Number of club_items in input and output are same
        2. recommended_markdown_price should be float if no_reco_reason_code is 'recommendation_successful'
        3. expected_sale_units should be int if no_reco_reason_code is 'recommendation_successful', otherwise
                it should be null
        4. verify data type and eligible values of all the output fields
        5. Validate business policy for min and max limit on the recommended markdown price.
        6. Validate business policy for 99 cent rule
        7. Validate the business policy for apparel items i.e. the markdown selling price should end with 71,81 or 91
                cents.

        We set no_reco_reason_code to unexpected_error if validation fails
        """
    logger.info("Validation the output generated")
    output_data = validate_same_request_ids_in_input_and_output(input_data, output_data)
    output_data = validate_output_field_values(input_data, output_data)
    output_data = validate_business_policy(input_data, output_data)
    return output_data


def format_output_as_dict(data: pd.core.frame.DataFrame) -> dict:
    """
    Format the output in a form defined in the V3 API I/O doc

    :param data:
    :return:
    """
    output_json = (data
                   .assign(misc=pd.NA)
                   .set_index('request_id')
                   # Keep only the columns same as the one in Settings.output_cols.
                   # If any column in Settings.output_cols is not present in the given Dataframe, then create it.
                   # Reindex function does both the jobs.
                   .reindex(columns=Settings.output_cols)
                   .convert_dtypes()
                   .to_json(orient='index')
                   )
    output_dict = json.loads(output_json)
    today = datetime.date.today()
    # Formulate week_level_expected_sale_units in the required output format
    for request_id, output in output_dict.items():
        if output['week_level_expected_sale_units']:
            output['week_level_expected_sale_units'] = [
                dict(start_date=(today + datetime.timedelta(days=week_index * 7)).strftime("%Y-%m-%d"),
                     end_date=(today + datetime.timedelta(days=week_index * 7 + 6)).strftime("%Y-%m-%d"),
                     expected_sale_units=sale) for week_index, sale in
                enumerate(output['week_level_expected_sale_units'])]
            output['week_level_expected_sale_units'][-1]['end_date'] = output['oos_date']
        if  output['expected_sale_units']:
            output['expected_sale_units'] = int(output['expected_sale_units'])            

    return output_dict
