import asyncio
import pandas as pd

from .schemas.family import FamilyGetSchema


class Family:
    def __init__(self, afas_connector):
        """
        Initialize Family class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_family"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get family information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing family information

        Raises:
            Exception: If get family operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=FamilyGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get family failed: {str(e)}") from e
