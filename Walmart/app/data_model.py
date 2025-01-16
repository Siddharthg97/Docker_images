"""
Description - Defines the Schema for JSON input
"""

__author__ = 'Rahul Kumar'
__copyright__ = '2021, Markdown Optimization'
__credits__ = ['Rahul', 'Srikant', 'Suraj', 'Jaspreet', 'Suyash']
__maintainer__ = '{Suraj, Rahul}'
__email__ = ['suraj.bansal@walmart.com', 'rahul.kumar16@walmart.com']
__status__ = 'Development'

from pydantic import BaseModel
from typing import Optional


# Model Class - Input Json for V3 API Needs to be Defined in this Format only
class ItemClub(BaseModel):
    club_nbr: str
    customer_item_nbr: str
    oos_date: str
    md_start_date: Optional[str] = None
    sell_through_threshold: Optional[float] = None
    current_inventory: int
    current_retail_price: float
    liquidation_price: float
