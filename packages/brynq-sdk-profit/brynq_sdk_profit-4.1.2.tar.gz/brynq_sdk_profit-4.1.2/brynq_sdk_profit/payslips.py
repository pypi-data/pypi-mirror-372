import asyncio
import pandas as pd
import requests
import logging
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception

from brynq_sdk_functions import Functions
from .schemas.payslip import PayslipGetSchema, PayslipMetaInfoSchema
from .schemas.document import DocumentSchema


def is_request_exception(e: BaseException) -> bool:
    if isinstance(e, requests.RequestException) and (
            e.response.status_code >= 500 or e.response.status_code == 408):
        error = str(e)[:400].replace('\'', '').replace('\"', '')
        print(f"{error}, retrying")
        return True
    else:
        return False


class Payslips:
    """Payslips management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize Payslips class with AFAS connector and required utilities

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_payslips"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get payslips information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing payslips information

        Raises:
            Exception: If get payslips operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(
                url=f"{self.afas.base_url}/brynq_sdk_payslips",
                schema=PayslipGetSchema,
                filter_fields=filter_fields
            ))
        except Exception as e:
            raise Exception(f"Get payslips failed: {str(e)}") from e

    def get_payslips_metainfo(self):
        """
        Get payslips meta information

        Returns:
            dict: Payslips meta information
        """
        try:
            return asyncio.run(self.afas.base_get(
                url=f"{self.afas.base_url}/brynq_sdk_payslips_metainfo",
                schema=PayslipMetaInfoSchema
            ))
        except Exception as e:
            raise Exception(f"Get payslips meta info failed: {str(e)}") from e
        
    def get_payslips_data(self):
        """
        Get payslips data

        Returns:
            dict: Payslips data
        """
        try:
            return asyncio.run(self.afas.base_get(
                url=f"{self.afas.base_url}/brynq_sdk_payslips",
                schema=PayslipGetSchema
            ))
        except Exception as e:
            raise Exception(f"Get payslips data failed: {str(e)}") from e

    def list_payslips(self): 
        try:
            # Get both metainfo and payslips data using the new functions
            meta_info_df = self.get_payslips_metainfo()
            payslips_df = self.get_payslips_data()

            # Merge the dataframes
            merged_payslips = pd.merge(
                left=meta_info_df,
                right=payslips_df,
                on="dossier_id",
                how="left"
            )

            valid_payslips, invalid_payslips = Functions.validate_data(df=merged_payslips, schema=DocumentSchema)
            return valid_payslips
        except Exception as e:
            raise Exception(f"Failed to list payslips. Error is {e}")

    def download(self, payslips: pd.DataFrame) -> pd.DataFrame:
        payslips['blob'] = payslips.apply(lambda x: self._download(dossieritem_id=x['dossier_id'], dossieritem_guid=x['attachment_code']), axis=1)
        return payslips

    def _download(self, dossieritem_id, dossieritem_guid) -> requests.Response:
        """
        This method returns base64encoded binary data in the filedata key of the json response. You can process this by decoding it and writing it to a file using:
        blob = base64.b64decode(response.json()['filedata'])
        with open('{}/{}'.format(self.file_directory, filename), 'wb') as f:
            f.write(blob)
        :param dossieritem_id: dossieritem_id
        :param dossieritem_guid: dossieritem_guid
        :return: response object
        """
        if self.afas.test_environment:
            url = f"https://{self.afas.environment}.resttest.afas.online/profitrestservices/subjectconnector/{dossieritem_id}/{dossieritem_guid}"
        else:
            url = f"https://{self.afas.environment}.rest.afas.online/profitrestservices/subjectconnector/{dossieritem_id}/{dossieritem_guid}"

        request = requests.Request('GET', url=url)
        prepared_request = self.afas.session.prepare_request(request)
        try:
            response = self.do_request(prepared_request)
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Failed to download payslips. Error is {e}")
            return None
        return response

    # this method should be used to execute all requests so retry and raising are handled in one place
    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_request_exception), reraise=True)
    def do_request(self, prepped_request: requests.PreparedRequest) -> requests.Response:
        response = self.afas.session.send(prepped_request, timeout=3000)
        if response.status_code >= 400:
            raise requests.exceptions.ConnectionError(f"Error occured: {response.status_code, response.text} while retrieving data for URL: {prepped_request.url}",
                                                      response=response, request=prepped_request)

        return response
