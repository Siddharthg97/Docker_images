# optimization
import datetime

import numpy as np
import pandas as pd

from src.config import Settings



def calculate_revenue(df: pd.core.frame.DataFrame, liquidation_price: float) -> pd.core.series.Series:


    revenue = df.apply(lambda x: np.dot(x['session_level_units_sold'], x['session_prices']) + x[
        'expected_liquidation_sale'] * liquidation_price, axis=1)
    return revenue


def get_optimal_point(club_item_data: pd.core.series.Series) -> pd.core.series.Series:
    """
    Function identifies the price point which optimises the objective metric subject to business constrains

    We refer to a combination corresponding to some markdown start date and some markdown price as a price point. If the
    sell_through_threshold is not given, we set the sell_through_threshold to default one. First we filter those price
    points which have expected sell through more than the sell_through_threshold. If all price points have expected sell
    through less than sell_through_threshold, we keep the price point corresponding to maximum expected sell through.
    Among the filtered price points, we pick the price point with maximum expected revenue. In case of tie for revenue
    metric, we pick the price point having lesser markdown price and earlier markdown start date.

    Following fields are added to the given pandas series:
    1. markdown_recommendation
    2. expected_sale_units
    3. expected_revenue

    :param club_item_data:
    :return:
    """
    elasticity_data = club_item_data['elasticity_data']
    current_inventory = club_item_data['current_inventory']
    liquidation_price = club_item_data['liquidation_price']
    input_stt = club_item_data['sell_through_threshold']
    sell_through_threshold = Settings.default_sell_through_threshold if pd.isna(input_stt) else input_stt
    max_revenue_data = (
        elasticity_data
        .assign(expected_sale_units=lambda x: x['session_level_units_sold'].apply(sum))
        .assign(expected_sell_through=lambda x: x['expected_sale_units'] / current_inventory)
        .assign(sell_through_threshold=lambda x: min(max(x['expected_sell_through']), sell_through_threshold))
        .query("expected_sell_through >= sell_through_threshold")
        .assign(expected_liquidation_sale=lambda x: current_inventory - x['expected_sale_units'])
        .assign(expected_revenue=lambda x: calculate_revenue(x, liquidation_price))
        .loc[lambda x: x['expected_revenue'] == x['expected_revenue'].max()]
        # In case of tie for revenue metric, we pick the price point having higher markdown_price and
        # earlier markdown start date
        .loc[lambda x: x['session_prices'].map(tuple) == tuple(x['session_prices'].max())]
        .loc[lambda x: x['session_dividing_dates'].map(tuple) == tuple(x['session_dividing_dates'].min())]
    )
    session_dividing_dates = max_revenue_data.iloc[0]['session_dividing_dates']
    today = datetime.date.today().strftime("%Y-%m-%d")
    recommended_md_start_date = session_dividing_dates[0] if session_dividing_dates else today
    recommended_markdown_price = max_revenue_data.iloc[0]['session_prices'][-1]
    club_item_data['markdown_recommendation'] = [dict(markdown_session_start_date=recommended_md_start_date,
                                                      recommended_markdown_price=recommended_markdown_price)]
    club_item_data['expected_sale_units'] = max_revenue_data.iloc[0]['expected_sale_units']
    club_item_data['expected_revenue'] = max_revenue_data.iloc[0]['expected_revenue']
    club_item_data['week_level_expected_sale_units'] = max_revenue_data.iloc[0]['week_level_units_sold']
    return club_item_data
