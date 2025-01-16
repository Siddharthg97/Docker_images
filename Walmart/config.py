"""
Description - Configuration Setting
"""

__author__ = 'Suraj Bansal'
__copyright__ = '2021, Markdown Optimization'
__credits__ = ['Kishan, Preetham, Rahul, Srikant, Suraj']
__maintainer__ = '{Suyash}'
__email__ = ['suyash.garg@walmart.com']
__status__ = 'Development'

import json
import logging
import os
from google.cloud import secretmanager
from dotenv import load_dotenv
# load_dotenv(os.getcwd() + '/.env')
load_dotenv()
from google.oauth2 import service_account

# Set Logging Configurations
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
format_ = logging.Formatter('%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s')
handler.setFormatter(format_)
logger.addHandler(handler)

# Set Database Pointer
DATABASE_POINTER = 'databricks'  # ['databricks', 'azure_sql']`

# Set Debug Mode
# databricks - In this debug mode connection with Databricks is acquired
# local - In this debug mode connection with Azure sql from local machine is acquired
# wcnp - In this debug mode connection with Azure sql from wcnp server is acquired
DEBUG_MODE = 'local'

# Get Database Connection Type
if DEBUG_MODE == 'wcnp':
    CONNECTION_TYPE = 'pyodbc'
else:
    CONNECTION_TYPE = 'persistent'


class Settings:

    static_feature_names = ['club_nbr',
                            'department_nbr',
                            'subclass_nbr',
                            'median_price_6_month_last_amt',
                            'price_1_week_back_median_price_6_month_last_nbr',
                            'price_2_week_back_median_price_6_month_last_nbr',
                            'price_3_week_back_median_price_6_month_last_nbr',
                            'price_4_week_back_median_price_6_month_last_nbr',
                            'avg_weekly_unit_sold_1_month_back_cnt',
                            'day_on_shelf_cnt',
                            'month',
                            'week',
                            'avg_unit_sold_subcategory_52_week_back_cnt',
                            'change_unit_sold_subcategory_same_week_1_year_back_cnt',
                            'avg_unit_sold_dept_52_week_back_cnt',
                            'avg_unit_sold_52_week_back_cnt',
                            'unit_sold_1_week_back_cnt',
                            'unit_sold_2_week_back_cnt',
                            'unit_sold_3_week_back_cnt',
                            'unit_sold_4_week_back_cnt',
                            'change_unit_sold_1_2_week_back_cnt',
                            'change_unit_sold_2_3_week_back_cnt',
                            'change_unit_sold_3_4_week_back_cnt',
                            'subclass_unit_sold_same_week_1_year_back_nbr']

    # These features are used in dynamic calculations
    discount_feature_format = 'discount_{}_week_next_nbr'
    num_weeks_feature = 'num_weeks'
    pre_sell_ratio_feature = 'week_inventory_expected_to_last_cnt'
    past_one_month_weekly_sale_feature = 'avg_weekly_unit_sold_1_month_back_cnt'
    dotcom_pre_sell_ratio_feature = 'inventory_1_month_last_weekly_sale_nbr'
    dotcom_num_weeks_feature = 'num_weeks'
    dotcom_discount_feature_format = 'discount_{}_week_next_nbr'
    dotcom_past_one_month_weekly_sale_feature = 'avg_weekly_unit_sold_1_month_back_cnt'

    dotcom_static_feature_names = ['category_nbr',
                                   'sub_category_nbr',
                                   'avg_weekly_unit_sold_1_month_back_cnt',
                                   'units_sold_1_week_back_cnt',
                                   'units_sold_2_week_back_cnt',
                                   'units_sold_3_week_back_cnt',
                                   'units_sold_4_week_back_cnt',
                                   'app_delivery_add2cart_click_1_week_back_cnt',
                                   'app_delivery_add2cart_click_3_week_back_cnt',
                                   'app_delivery_add2cart_click_4_week_back_cnt',
                                   'app_pickup_add2cart_click_2_week_back_cnt',
                                   'app_delivery_add2cart_member_1_week_back_cnt',
                                   'web_delivery_add2cart_member_1_week_back_cnt',
                                   'web_delivery_add2cart_member_4_week_back_cnt',
                                   'web_pickup_add2cart_member_1_week_back_cnt',
                                   'web_shipping_add2cart_member_2_week_back_cnt',
                                   'web_delivery_add2cart_click_1_week_back_cnt',
                                   'web_delivery_add2cart_click_2_week_back_cnt',
                                   'web_delivery_add2cart_click_3_week_back_cnt',
                                   'web_shipping_add2cart_click_2_week_back_cnt',
                                   'web_shipping_add2cart_click_3_week_back_cnt',
                                   'web_shipping_add2cart_click_4_week_back_cnt']

    # Forecast Duration
    forcast_duration = range(1, 9)
    n_prediction_weeks = len(forcast_duration)

    # Discount Spacing
    discount_spacing = 0.05

    # Fields in the output of V3 API
    output_cols = ['club_nbr', 'customer_item_nbr', 'oos_date', 'md_start_date', 'sell_through_threshold',
                   'current_inventory', 'current_retail_price', 'liquidation_price', 'markdown_recommendation',
                   'expected_sale_units', 'week_level_expected_sale_units', 'no_reco_reason_code', 'model_features',
                   'remark', 'expected_revenue', 'misc']
    dotcom_output_cols = ['club_nbr', 'product_id','customer_item_nbr', 'oos_date', 'md_start_date', 'sell_through_threshold',
                   'current_inventory', 'current_retail_price', 'liquidation_price', 'markdown_recommendation',
                   'expected_sale_units', 'week_level_expected_sale_units', 'no_reco_reason_code', 'model_features',
                   'remark', 'expected_revenue', 'misc']

    valid_no_reco_reason_code = ['liquidation', 'invalid_input', 'incomplete_info', 'price_outlier', 'curve_outlier',
                                 'recommendation_successful', 'unexpected_error']

    # Category List with Critical Price Point Policy
    dict_critical_pp_cat_list = {"apparel": ['22', '23', '33', '34', '68', '95'],
                                 "teo": ['3', '5', '6', '20', '29', '31', '32', '61', '64', '69', '70', '71', '74',
                                         '80', '81', '83', '85', '86']}
    dict_critical_pp_list = {"apparel": [0.81], "teo": [0.91]}

    # Dictionary containing the minimum markdown price defined by business team for each category. The default value is
    # assumed to be 0 for rest of the categories.
    min_markdown_price = {'1': 1, '40': 1, '41': 1, '42': 1, '43': 1, '44': 1, '46': 1, '48': 1, '49': 1, '52': 1,
                          '57': 1, '58': 1, '78': 1}

    dict_cat_list = {"apparel": [22, 23, 33, 34, 95, 68],
                     "home_seasonal": [7, 9, 10, 11, 12, 14, 15, 16, 17, 18, 21, 32, 36, 50, 51, 60, 89, 92, 97],
                     "cat_3": [3]}
    dict_cat_min_percent_discount = {"apparel": 20, "home_seasonal": 15, "cat_3": 15}

    enable_historic_data_requests = False
    model_ttl = 24 * 60 * 60
    max_forecast_weeks = 8
    default_sell_through_threshold = 0
    min_percent_discount = 10
    min_dollar_discount = 1
    buffer_percent_over_liquidation = 20
    model_database_table = 'markdown.model_info_v3'

    def __init__(self):
        pass

    def __str__(self):
        pass

    @staticmethod
    def azure_sql_credentials():

        if DEBUG_MODE == 'local':
            sql_server = os.getenv('SQL_SERVER')
            sql_username = os.getenv('SQL_USER')
            sql_pass = os.getenv('SQL_PASS')
            sql_database = os.getenv('SQL_DB')
        else:
            # Read Azure Server Name
            path = r"/etc/secrets/sql_server.txt"
            try:
                assert os.path.isfile(path)
                sql_server = eval(f"open('{path}').read()")
            except:
                sql_server = os.getenv('SQL_SERVER')

            # Read Azure UserName
            path = r"/etc/secrets/sql_username.txt"
            try:
                assert os.path.isfile(path)
                sql_username = eval(f"open('{path}').read()")
            except:
                sql_username = os.getenv('SQL_USER')

            # Read Azure Database Name
            path = r"/etc/secrets/sql_database.txt"
            try:
                assert os.path.isfile(path)
                sql_database = eval(f"open('{path}').read()")
            except:
                sql_database = os.getenv('SQL_DB')

            # Read Azure Server Name
            path = r"/etc/secrets/sql_password.txt"
            try:
                assert os.path.isfile(path)
                sql_pass = eval(f"open('{path}').read()")
            except:
                sql_pass = os.getenv('SQL_PASS')

        sql_cred = {
            'sql_server': sql_server,
            'sql_database': sql_database,
            'sql_username': sql_username,
            'sql_pass': sql_pass
        }

        return sql_cred

    @staticmethod
    def databricks_credentials():

        if DEBUG_MODE == 'local':
            databricks_host_name = os.getenv('DATABRICKS_SERVER_HOSTNAME')
            databricks_token = os.getenv('DATABRICKS_TOKEN')
            databricks_http_path = os.getenv('DATABRICKS_HTTP_PATH')
        else:
            # Read Databricks Server Name
            databricks_host_name = ''
            path = r"/etc/secrets/databricks_server_hostname.txt"
            try:
                assert os.path.isfile(path)
                databricks_host_name = eval(f"open('{path}').read()")
            except:
                databricks_host_name = os.getenv('DATABRICKS_SERVER_HOSTNAME')

            # Read databricks Token
            databricks_token = ''
            path = r"/etc/secrets/databricks_token.txt"
            try:
                assert os.path.isfile(path)
                databricks_token = eval(f"open('{path}').read()")
            except:
                databricks_token = os.getenv('DATABRICKS_TOKEN')

            # Read Databricks HTTP Path
            databricks_http_path = ''
            path = r"/etc/secrets/databricks_http_path.txt"
            try:
                assert os.path.isfile(path)
                databricks_http_path = eval(f"open('{path}').read()")
            except:
                databricks_http_path = os.getenv('DATABRICKS_HTTP_PATH')

        databricks_cred = {
            'databricks_http_path': databricks_http_path,
            'databricks_token': databricks_token,
            'databricks_host_name': databricks_host_name,
        }

        return databricks_cred

    @staticmethod
    def get_azure_blob_credentials():

        if DEBUG_MODE == 'local':
            account_url = os.getenv('ACCOUNT_URL')
            account_key = os.getenv('ACCOUNT_KEY')
            container_name = os.getenv('CONTAINER_NAME')
        else:
            # Reading Account URL
            account_url = ''
            path = r"/etc/secrets/account_url.txt"
            try:
                assert os.path.isfile(path)
                account_url = eval(f"open('{path}').read()")
            except:
                account_url = os.getenv('ACCOUNT_URL')

            # Reading Account Key
            path = r"/etc/secrets/account_key.txt"
            try:
                assert os.path.isfile(path)
                account_key = eval(f"open('{path}').read()")
            except:
                account_key = os.getenv('ACCOUNT_KEY')

            # Reading Container Name
            path = r"/etc/secrets/container_name.txt"
            try:
                assert os.path.isfile(path)
                container_name = eval(f"open('{path}').read()")
            except:
                container_name = os.getenv('CONTAINER_NAME')

        blob_cred = {
            'account_url': account_url,
            'account_key': account_key,
            'container_name': container_name,
        }

        return blob_cred

    @staticmethod
    def access_secret(project_id, secret_id, version):
        client = secretmanager.SecretManagerServiceClient()
        name = client.secret_version_path(project_id, secret_id, version)
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode('UTF-8')
        return payload

    @staticmethod
    def setup_feature_store_credentials():

        if DEBUG_MODE == 'local':
            # FEATURE_STORE_CRED_STAGE = os.getenv('FEATURE_STORE_CRED_STAGE')
            with open('prod_onlinefeaturestore_key.json', 'r') as file:
            # with open(FEATURE_STORE_CRED_STAGE, 'r') as file:
                creds = json.load(file)
        else:
            try:
                path = r"/etc/secrets/prod-feature-store-api.json"
                assert os.path.isfile(path)
                with open(path) as file:
                    creds = json.load(file)
            except:
                featurestore_env = os.getenv('FEATURESTORE_API_ENV')
                featurestore_key = os.getenv('FEATURESTORE_API_KEY')
                featurestore_secret = os.getenv('FEATURESTORE_API_SECRET')
                creds = {"FEATURESTORE_API_ENV": featurestore_env,
                         "FEATURESTORE_API_KEY": featurestore_key,
                         "FEATURESTORE_API_SECRET": featurestore_secret
                         }
        for key in creds:
            os.environ[key] = creds[key]

    @staticmethod
    def get_gcp_credentials():
        if DEBUG_MODE == 'local':
            gcp_credentials_path = 'markdown_non_prod_key.json'
        else:
            gcp_credentials_path = r"/etc/secrets/gcp_prod_key.json"
        credentials = service_account.Credentials.from_service_account_file(
            gcp_credentials_path)
        return credentials

    @staticmethod
    def set_MLflow_env():
        # if local, the env variables are in .env file
        if DEBUG_MODE != 'local':
            path = r"/etc/secrets/mlflow_key.txt"
            assert os.path.isfile(path)
            try:
                mlflow_key = json.load(open(f"{path}"))
                os.environ['ELEMENT_TOKEN'] = mlflow_key['ELEMENT_TOKEN']  # ELEMENT_TOKEN_DECRYPTED
                os.environ['PROJECT_ID'] = mlflow_key['PROJECT_ID']
                os.environ['DATASET_SERVICE_HOST'] = mlflow_key['DATASET_SERVICE_HOST']
                os.environ['MLFLOW_TRACKING_URI'] = mlflow_key['MLFLOW_TRACKING_URI']
                os.environ['DATASET_SERVICE_PORT'] = mlflow_key['DATASET_SERVICE_PORT']
            except:
                raise Exception('mlflow key not Found')
        else:
            try:
                os.environ['ELEMENT_TOKEN'] = os.getenv['ELEMENT_TOKEN']  # ELEMENT_TOKEN_DECRYPTED
                os.environ['PROJECT_ID'] = os.getenv['PROJECT_ID']
                os.environ['DATASET_SERVICE_HOST'] = os.getenv['DATASET_SERVICE_HOST']
                os.environ['MLFLOW_TRACKING_URI'] = os.getenv['MLFLOW_TRACKING_URI']
                os.environ['DATASET_SERVICE_PORT'] = os.getenv['DATASET_SERVICE_PORT']
            except:
                raise Exception('mlflow key not Found')