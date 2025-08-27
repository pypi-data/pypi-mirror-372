from brynq_sdk_brynq import BrynQ
import base64
import json
import time
import sys
import pandas as pd
from urllib import parse
import requests
from requests.adapters import HTTPAdapter

from typing import Union, List, Literal
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception

__all__ = ['GetConnector']

def is_request_exception(e: BaseException) -> bool:
    if isinstance(e, requests.RequestException) and (e.response.status_code >= 500 or e.response.status_code == 408):
        error = str(e)[:400].replace('\'', '').replace('\"', '')
        print(f"{error}, retrying")
        return True
    else:
        return False


class GetConnector(BrynQ):
    def __init__(self, label: Union[str, List], test_environment: bool = False, debug: bool = False):
        super().__init__()
        if test_environment:
            self.base_url = 'resttest.afas.online'
        else:
            self.base_url = 'rest.afas.online'
        credentials = self.get_system_credential(system='profit', label=label, test_environment=test_environment)
        self.environment = credentials['environment']
        base64token = base64.b64encode(credentials['token'].encode('utf-8')).decode()
        self.session = requests.Session()
        self.session.headers.update({'Authorization': 'AfasToken ' + base64token,
                                     'IntegrationId': '38092_135680'})
        self.debug = debug
        self.timeout = 3600

    def get_metadata(self, connector: str = None, type: Literal['get', 'update', None] = 'get') -> dict:
        url = f"https://{self.environment}.{self.base_url}/profitrestservices/metainfo"
        if type is not None and connector is not None:
            url += f'/{type}/{connector}'

        response = self.session.get(url=url, timeout=self.timeout)
        response = response.json()
        if connector is not None:
            return response.get('fields')
        else:
            if type == "get":
                return response.get("getConnectors")
            elif type == "update":
                return response.get("updateConnectors")
            else:
               return response

    def get_data(self, connector, fields=None, values=None, operators=None, orderbyfields=None):
        """
        Possible filter operators are:
        1: is gelijk aan
        2: is groter of gelijk aan
        3: is kleiner of gelijk aan
        4: is groter dan
        5: is kleiner dan
        6: tekst komt voor in veld	                                Plaats de filterwaarde tussen %..%, bijvoorbeeld %Microsoft%
        7: is niet gelijk aan / Tekst komt niet voor in veld	    Plaats de filterwaarde tussen %..%, bijvoorbeeld %Microsoft%
        8: veld is leeg	                                            Geef filterfieldid, filtervalue en operatortype op. De waarde bij filtervalue is altijd null
        9: veld is niet leeg	                                    Geef filterfieldid, filtervalue en operatortype op
        10 :veld begint met tekst	                                Plaats het teken % aan het einde van de filterwaarde, bijvoorbeeld Microsoft%
        12 :veld begint niet met tekst	                            Plaats het teken % aan het einde van de filterwaarde, bijvoorbeeld Microsoft%
        13 :veld eindigt met tekst	                                Plaats het teken % aan het begin van de filterwaarde, bijvoorbeeld %Microsoft
        14 :veld eindigt niet met tekst	                            Plaats het teken % aan het begin van de filterwaarde, bijvoorbeeld %MiMicrosoft

        If you use a skip and take, highly recommended to specify orderbyfields. This makes the requests much faster.
        You should use unique fields or combinations of most unique fields in the dataset

        Using ';' between filters is OR, ',' is AND
        """
        total_response = []
        loop_boolean = True
        no_of_loops = 0
        no_of_results = 0

        if fields is not None:
            parameters = {"filterfieldids": fields, "filtervalues": values, "operatortypes": operators}
        else:
            parameters = {}

        if orderbyfields is not None:
            parameters["orderbyfieldids"] = "-{}".format(orderbyfields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, connector)

        while loop_boolean:
            loop_parameters = {"skip": 40000 * no_of_loops, "take": 40000}
            parameters.update(loop_parameters)
            request = requests.Request('GET', url=url, params=parameters)
            prepared_request = self.session.prepare_request(request)
            response = self.do_request(prepared_request)
            response_json = response.json()['rows']
            no_of_loops += 1
            no_of_results += len(response_json)
            loop_boolean = True if len(response_json) == 40000 else False

            if self.debug:
                print(time.strftime('%H:%M:%S'), 'Got next connector from profit: ', connector, ' With nr of rows: ', no_of_results)
            total_response += response_json

        return total_response

    def get_complex_filtered_data(self, connector: str, fields: list, values: list, operators: list, orderbyfields: str = None):
        """
        This method is meant for complex combined filters like (a and b) or (a and c)

        Possible filter operators are:
        1: is gelijk aan
        2: is groter of gelijk aan
        3: is kleiner of gelijk aan
        4: is groter dan
        5: is kleiner dan
        6: tekst komt voor in veld	                                Plaats de filterwaarde tussen %..%, bijvoorbeeld %Microsoft%
        7: is niet gelijk aan / Tekst komt niet voor in veld	    Plaats de filterwaarde tussen %..%, bijvoorbeeld %Microsoft%
        8: veld is leeg	                                            Geef filterfieldid, filtervalue en operatortype op. De waarde bij filtervalue is altijd null
        9: veld is niet leeg	                                    Geef filterfieldid, filtervalue en operatortype op
        10 :veld begint met tekst	                                Plaats het teken % aan het einde van de filterwaarde, bijvoorbeeld Microsoft%
        12 :veld begint niet met tekst	                            Plaats het teken % aan het einde van de filterwaarde, bijvoorbeeld Microsoft%
        13 :veld eindigt met tekst	                                Plaats het teken % aan het begin van de filterwaarde, bijvoorbeeld %Microsoft
        14 :veld eindigt niet met tekst	                            Plaats het teken % aan het begin van de filterwaarde, bijvoorbeeld %MiMicrosoft

        If you use a skip and take, highly recommended to specify orderbyfields. This makes the requests much faster.
        You should use unique fields or combinations of most unique fields in the dataset

        Using ';' between filters is OR, ',' is AND
        :param connector: name of connector
        :param fields: list of filters. each listitem is one filterblock. example: ['naam, woonplaats', 'achternaam, einddatum']
        :param values: list of filters. each listitem corresponds to one filterblock. example: ['Jan, Gouda', 'Janssen, 2019-01-01T00:00']
        :param operators: list of filters. each listitem corresponds to one filterblock. example: ['1, 1', '1, 3']
        :param orderbyfields: string of fields to order result by
        :return: data in json format
        """

        total_response = []
        loop_boolean = True
        no_of_loops = 0
        no_of_results = 0

        parameters = {"Filters": {"Filter": []}}

        for filter_no in range(0, len(fields)):
            filter = {"@FilterId": 'Filter {}'.format(filter_no + 1), "Field": []}
            fields_values = fields[filter_no].split(',')
            operators_values = operators[filter_no].split(',')
            values_values = values[filter_no].split(',')
            for number in range(0, len(fields_values)):
                filter["Field"].append({"@FieldId": fields_values[number],
                                        "@OperatorType": operators_values[number],
                                        "#text": values_values[number]})
            parameters['Filters']['Filter'].append(filter)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, connector)
        # eliminate whitespaces and escape special characters
        querystring = parse.quote(json.dumps(parameters, separators=(',', ':')))
        if orderbyfields is not None:
            querystring = querystring + '&orderbyfieldids={}'.format(orderbyfields)

        while loop_boolean:
            loop_parameters = "&skip={}&take={}".format(40000 * no_of_loops, 40000)
            request = requests.Request('GET', url=url, params="filterjson={}{}".format(querystring, loop_parameters))
            prepared_request = self.session.prepare_request(request)
            response = self.do_request(prepared_request)
            response_json = response.json()['rows']
            no_of_loops += 1
            no_of_results += len(response_json)
            loop_boolean = True if len(response_json) == 40000 else False

            if self.debug:
                print(time.strftime('%H:%M:%S'), 'Got next connector from profit: ', connector, ' With nr of rows: ', no_of_results)
            total_response += response_json

        return total_response

    def get_dossier_attachments(self, dossieritem_id, dossieritem_guid) -> requests.Response:
        """
        This method returns base64encoded binary data in the filedata key of the json response. You can process this by decoding it and writing it to a file using:
        blob = base64.b64decode(response.json()['filedata'])
        with open('{}/{}'.format(self.file_directory, filename), 'wb') as f:
            f.write(blob)
        :param dossieritem_id: dossieritem_id
        :param dossieritem_guid: dossieritem_guid
        :return: response object
        """
        url = f"https://{self.environment}.{self.base_url}/profitrestservices/subjectconnector/{dossieritem_id}/{dossieritem_guid}"
        request = requests.Request('GET', url=url)
        prepared_request = self.session.prepare_request(request)
        response = self.do_request(prepared_request)

        return response

    def download_file(self, file_id: str, filename: str, output_folder: str):
        """
        This method is for downloading a file from AFAS.
        :param file_id: the file_id of the file you want to download
        :param filename: the filename of the file you want to download
        :param output_folder: The folder where the file should be saved
        """

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/fileconnector/{file_id}/{filename}"
        request = requests.Request('GET', url=url)
        prepared_request = self.session.prepare_request(request)
        response = self.do_request(prepared_request)

        with open(f"{output_folder}/{filename}", 'wb') as f:
            blob = base64.b64decode(response.json()['filedata'])
            f.write(blob)

    def download_report(self, report_id: str, output_filepath: str):
        """
        This method is for downloading a report from AFAS.
        :param report_id: the ID of the report you want to download
        :param output_filepath: The full path (folder and filename) to where you want to store the report
        """
        url = f"https://{self.environment}.{self.base_url}/profitrestservices/reportconnector/{report_id}"
        request = requests.Request('GET', url=url)
        prepared_request = self.session.prepare_request(request)
        response = self.do_request(prepared_request)

        with open(f"{output_filepath}", 'wb') as f:
            blob = base64.b64decode(response.json()['filedata'])
            f.write(blob)

    def convert_datatypes_to_afas_datatypes(self, data: list, connector: str) -> pd.DataFrame:
        """
        Takes in the response of get_data or get_complex data and converts the datatypes of the columns to the datatype
        specified in the metadata of the connector.
        :param data: response of get_data or get_complex_data method
        :param connector: name of connector
        :return: pd.DataFrame with datatypes as given in the metadata of the connector
        """

        # Converts the data to a pandas dataframe and gets the metadata
        data = pd.DataFrame(data)
        meta_data = self.get_metadata(connector=connector)

        # mapping to convert the datatypes in the metadata to the correct pandas datatypes
        mapping = {
            "int": "Int64",
            "decimal": "float",
            "string": "str",
            "date": "datetime64[ns]",
            "boolean": "bool",
            "blob": "object"
        }

        # Checks if the column is in the metadata and if so adds it to the list of columns to convert
        columns_to_convert = [column for column in meta_data if column["id"] in data.columns]

        # Loops through the columns to convert and converts them to the correct datatype
        for column in columns_to_convert:
            new_type = mapping[column['dataType']]
            col_data = data[column['id']]


            # Looks if the column is a datetime column and checks what the control type is to assign the correct type.
            # Control type are used in AFAS to determine the formatting 4 is a date, 7 is a time and 8 is a datetime.
            if new_type == "datetime64[ns]":
                # Separated the datetime conversion from the other types to handle date objects with differening timezones
                temp_datetime = pd.to_datetime(col_data, errors='coerce').dt.tz_localize(None)
                if column["controlType"] == 4:
                    data[column['id']] = temp_datetime.dt.date
                elif column["controlType"] == 7:
                    data[column['id']] = temp_datetime.dt.time
                else:
                    data[column['id']] = temp_datetime
            else:
                # Proceed with conversion for other types as normal
                data[column['id']] = col_data.astype(new_type)

        # returns the dataframe with the correct datatypes
        return data

    # this method should be used to execute all requests so retry and raising are handled in one place
    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_request_exception), reraise=True)
    def do_request(self, prepped_request: requests.PreparedRequest) -> requests.Response:
        response = self.session.send(prepped_request, timeout=3000)
        if response.status_code >= 400:
            raise requests.exceptions.ConnectionError(f"Error occured: {response.status_code, response.text} while retrieving data for URL: {prepped_request.url}",
                                                      response=response, request=prepped_request)

        return response
