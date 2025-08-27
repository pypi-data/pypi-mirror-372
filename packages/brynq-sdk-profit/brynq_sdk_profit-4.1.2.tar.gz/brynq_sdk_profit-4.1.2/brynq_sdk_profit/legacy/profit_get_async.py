from brynq_sdk_brynq import BrynQ
from .profit_get import GetConnector
import base64
import asyncio
import time
import aiohttp
import json
from typing import List, Union, Literal
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception

__all__ = ['GetConnectorAsync']

# This method makes sure that the request is retried if the request fails with a 5xx error or a 408 error
def is_request_exception(e: BaseException) -> bool:
    if isinstance(e, aiohttp.ClientResponseError) and (e.status >= 500 or e.status == 408):
        error = str(e)[:400].replace('\'', '').replace('\"', '')
        print(f"{error}, retrying")
        return True
    else:
        return False


class GetConnectorAsync:
    def __init__(self, label: Union[str, List], test_environment: bool = False, debug: bool = False):
        self.profit = GetConnector(label=label, test_environment=test_environment)
        self.profit_async = ProfitExtractAsync(label=label, test_environment=test_environment, debug=debug)

    def get_data(self, connector_information: Union[dict, list, str], batch_size: int = 8, take: int = 40000) -> dict:
        """
        A synchronous method is needed to be able to run multiple asynchronous functions. Within this function, a call
        is made to an asynchronous wrapper, which calls a single request function multiple times asynchronously untill
        the complete connector has been extracted. In this, filters can be used to specify which data needs to be extracted
        from profit.
        Note that Python version 3.7 or higher is necessary to be able to use this method.

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

        :param connector_information: Dict of connectors with corresponding filters like so: {"connector_a": {"fields": "a,b", "operators": "1,2", "values": "100,200", "orderbyfields": "a"}, "connector_b": {}}
        :param batch_size: amount of requests to be sent per connector simultaneously
        :param take: amount of results to request per call
        :return data in json format
        """
        if isinstance(connector_information, dict):
            # Rebuild dict because async get_data method only expects the filters in parameters, connectors are a separate parameter.
            connectors = list(connector_information.keys())
            parameters = {}

            # rename readable field keys to the keys that AFAS expects (eg: fields -> filterfieldids)
            for connector in connector_information.keys():
                if 'fields' in connector_information[connector].keys():
                    parameters[connector].update({'filterfieldids': connector_information[connector]['fields']}) if connector in parameters.keys() else parameters.update({connector: {'filterfieldids': connector_information[connector]['fields']}})
                if 'values' in connector_information[connector].keys():
                    parameters[connector].update({'filtervalues': connector_information[connector]['values']}) if connector in parameters.keys() else parameters.update({connector: {'filtervalues': connector_information[connector]['values']}})
                if 'operators' in connector_information[connector].keys():
                    parameters[connector].update({'operatortypes': connector_information[connector]['operators']}) if connector in parameters.keys() else parameters.update({connector: {'operatortypes': connector_information[connector]['operators']}})
                if 'orderbyfields' in connector_information[connector].keys():
                    parameters[connector].update({'orderbyfieldids': connector_information[connector]['orderbyfields']}) if connector in parameters.keys() else parameters.update({connector: {'orderbyfieldids': connector_information[connector]['orderbyfields']}})

        # if connectorinformation is list, no filters are present
        elif isinstance(connector_information, list):
            connectors = connector_information
            parameters = {}
        # if connectorinformation is string, no filters are present, string should be converted to list
        else:
            connectors = [connector_information]
            parameters = {}

        total_response = asyncio.run(
            self.profit_async.get_data(connectors=connectors,
                                       parameters=parameters,
                                       batch_size=batch_size,
                                       take=take))

        return total_response

    def get_complex_filtered_data(self, connector: str, fields: list, values: list, operators: list, orderbyfields: str = None, batch_size: int = 8, take: int = 40000) -> json:
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
        :param batch_size: amount of requests to be sent per connector simultaneously
        :param take: amount of results to request per call
        :return: data in json format
        """
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

        # eliminate whitespaces and escape special characters
        querystring = json.dumps(parameters, separators=(',', ':'))
        if orderbyfields is not None:
            querystring = {connector: {"filterjson": querystring, "orderbyfieldids": f"{orderbyfields}"}}
        else:
            querystring = {connector: {"filterjson": querystring}}

        total_response_raw = asyncio.run(
            self.profit_async.get_data(connectors=[connector],
                                       parameters=querystring,
                                       batch_size=batch_size,
                                       take=take))
        total_response = [item for sublist in total_response_raw for item in sublist]

        return total_response

    def get_meta_data(self, connector: str = None, type: Literal['get', 'update', None] = 'get'):
        """
        This function makes sure that you can create a list of connector names without having to call another class.
        :return: returns a list of all connectors in the environment.
        """
        return self.profit.get_metadata(connector=connector, type=type)

    def convert_datatypes_to_afas_datatypes(self, data: dict) -> dict:
        """
        Takes in the response of get_data or get_complex data and converts the datatypes of the columns to the datatype
        specified in the metadata of the connector.
        :param data: response of get_data or get_complex_data method
        :return: pd.DataFrame with datatypes as given in the metadata of the connector
        """
        # Initializes the list of dataframes
        new_data = {}

        # Loops through the connectors and the data
        for connector, data_test in data.items():
            new_data.update({connector: self.profit.convert_datatypes_to_afas_datatypes(data=data_test, connector=connector)})

        # returns the dataframe with the correct datatypes
        return new_data


class ProfitExtractAsync(BrynQ):
    def __init__(self, label: Union[str, List], test_environment: bool = False, debug=False):
        super().__init__()
        if test_environment:
            self.base_url = 'resttest.afas.online'
        else:
            self.base_url = 'rest.afas.online'
        credentials = self.get_system_credential(system='profit', label=label, test_environment=test_environment)
        self.environment = credentials['environment']
        base64token = base64.b64encode(credentials['token'].encode('utf-8')).decode()
        self.headers = {'Authorization': 'AfasToken ' + base64token,
                        'IntegrationId': '38092_135680'}
        self.got_all_results = False
        self.debug = debug

    async def get_data(self, connectors: List = None, parameters: dict = {}, batch_size: int = 8, take: int = 40000) -> dict:
        """
        This (asynchronous) function functions as a wrapper that can carry out multiple single get requests to be able
        to get all data from profit in an asynchronous and efficient way. Only use this function in async code, otherwise use the profit class to call this from a sync function.
        :param connectors: Names of the connectors to be extracted. If not provided, keys of parameters dict will be used
        :param parameters: multilevel dict of filters per connector. Key must always be the connector, then dict like {connector: {"filterfieldids": fields, "filtervalues": values, "operatortypes": operators}
        :return: data in json format
        """
        url = f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/'
        batch_number = 0

        total_response = {}
        self.got_all_results = False
        while not self.got_all_results:
            async with aiohttp.ClientSession(headers=self.headers, timeout=aiohttp.ClientTimeout()) as session:
                requests = [self.get_request(url=url,
                                             connector=connector,
                                             params={**(parameters[connector] if connector in parameters.keys() else {}), **{
                                                 "skip": take * (i + batch_number * batch_size),
                                                 "take": take}},
                                             session=session,
                                             take=take) for i in range(batch_size) for connector in connectors]
                response = await asyncio.gather(*requests, return_exceptions=False)

                # Flatten response (multiple dicts with the same key (connectorname) and different values are returned)
                for item in response:
                    for key, value in item.items():
                        if key in total_response.keys():
                            total_response[key].extend(value)
                        else:
                            total_response[key] = value

                batch_number += 1

        return total_response

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_request_exception), reraise=True)
    async def get_request(self, url: str, connector: str, params: dict, session: aiohttp.ClientSession, take: int):
        """
        This function carries out a single get request given the inputs. It is used as input for the abovementioned wrapper,
        get_data_content. Note that this function cannot be called it itself, but has to be started via get_data_content.

        :param url: profit url to retrieve the data.
        :param params: body of the request.
        :param session: type of the request.
        :return: data in json format
        """
        if self.debug:
            print(f"started request for {connector} at: {time.time()}")
        async with session.get(url=f"{url}{connector}", params=params) as resp:
            if resp.status >= 400:
                raise aiohttp.ClientResponseError(message=f"Error occured: {resp.status, await resp.text()} while retrieving data for URL: {url}",
                                                  request_info=resp.request_info,
                                                  history=resp.history,
                                                  status=resp.status,
                                                  headers=resp.headers)
            response = await resp.json()
            response = response['rows']
            if len(response) < take:
                if self.debug:
                    print(f"request with params: {params} was the last request with {len(response)} rows")
                self.got_all_results = True
            else:
                if self.debug:
                    print(f"request with params: {params} has {len(response)} rows")

            return {connector: response}

    @retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(initial=60, max=900), retry=retry_if_exception(is_request_exception), reraise=True)
    async def get_meta_data(self, connector: str = None):
        """
        This function makes sure that you can create a list of connector names without having to call another class.
        :return: returns a list of all connectors in the environment.
        """

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/metainfo{f'/get/{connector}' if connector is not None else ''}"

        async with aiohttp.ClientSession(headers=self.headers, timeout=aiohttp.ClientTimeout()) as session:
            async with session.get(url=f"{url}") as resp:
                if resp.status >= 400:
                    raise aiohttp.ClientResponseError(message=f"Error occured: {resp.status, await resp.text()} while retrieving data for URL: {resp.url}",
                                                      request_info=resp.request_info,
                                                      history=resp.history,
                                                      status=resp.status,
                                                      headers=resp.headers)
                response = await resp.json()
                response = response[f"{'getConnectors' if connector is None else 'fields'}"]

                return response
