import logging
from zenml import step
import pandas as pd 
from src.data_cleaning import DataPreProcessing, DataStrategy
from typing_extensions import Annotated
from typing import Tuple


@step 
def clean_df(df: pd.DataFrame) -> Tuple:
    Annotated(pd.DataFrame)
    try:
        process_strategy = DataPreProcessing()
        processed_data = process_strategy.handle_data()

        logging.info("Data cleaning Completed")
    except Exception as e:
        logging.error("Error in cleaning data: {}".format(e))
        raise e