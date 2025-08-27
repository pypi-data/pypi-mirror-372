import asyncio
import pandas as pd
from typing import Optional, Dict, Any, Literal, List
import json
from urllib import parse

class CustomGetConnector:
    """Custom connector class for AFAS integration that handles non-standard connectors"""

    def __init__(self, afas_connector: Any) -> None:
        """
        Initialize custom connector class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector

    def get_metadata(self, connector: str = None, type: Literal['get', 'update', None] = 'get') -> dict:
        """
        Get metadata information for connectors

        Args:
            connector: Name of the connector to get metadata for
            type: Type of metadata ('get', 'update', or None)

        Returns:
            dict: Metadata information

        Raises:
            Exception: If metadata retrieval fails
        """
        try:
            url = f"https://{self.afas.environment}.rest.afas.online/profitrestservices/metainfo"
            if self.afas.test_environment:
                url = f"https://{self.afas.environment}.resttest.afas.online/profitrestservices/metainfo"

            if type is not None and connector is not None:
                url += f'/{type}/{connector}'

            response = self.afas.session.get(url=url, timeout=self.afas.timeout)
            response_json = response.json()

            if connector is not None:
                return response_json.get('fields')
            else:
                if type == "get":
                    return response_json.get("getConnectors")
                elif type == "update":
                    return response_json.get("updateConnectors")
                else:
                    return response_json
        except Exception as e:
            raise Exception(f"Get metadata failed: {str(e)}") from e

    def get(self, connector: str,
            filter_fields: Optional[dict] = None) -> pd.DataFrame:
        """
        Get data from a custom connector using AFAS base_get method
        """
        try:
            # Build the URL for the custom connector
            url = f"{self.afas.base_url}/{connector}"
            #url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, connector)


            # Use base_get method with schema_required=False for custom connectors
            return asyncio.run(self.afas.base_get(
                url=url,
                schema=None,
                schema_required=False,
                filter_fields=filter_fields
            ))

        except Exception as e:
            raise Exception(f"Get data from connector '{connector}' failed: {str(e)}") from e
