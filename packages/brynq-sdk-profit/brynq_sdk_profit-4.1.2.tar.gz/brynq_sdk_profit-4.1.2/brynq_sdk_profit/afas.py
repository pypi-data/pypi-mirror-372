import base64
import requests
import pandas as pd
import warnings
from brynq_sdk_brynq import BrynQ
from brynq_sdk_functions import Functions

from .employees import Employees
from .person import Person
from .organisation import Organisation
from .organisational_unit import OrganisationalUnit
from .costcenter import CostCenter
from .costcarrier import CostCarrier
from .bankaccount import BankAccount
from .debtor_creditor import Debtor, Creditor
from .journalentry import JournalEntry
from .postcalculation import PostCalculation
from .functions import EmployeeFunction
from .custom_connector import CustomGetConnector
import pandera as pa
from typing import Dict, Any, Type, Optional, List, Literal, Union
import datetime
import aiohttp
import asyncio
import base64

class AFAS(BrynQ):
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, test_environment: bool = False, debug: bool = False):
        """
        Initialize AFAS connection handler

        Args:
            system_type: Connection system_type for credentials
            test_environment: Whether to use test environment
            debug: Whether to enable debug mode
        """
        super().__init__()
        self.debug = debug
        self.timeout = 3600
        self.test_environment = test_environment
        credentials = self.interfaces.credentials.get(system="profit", system_type=system_type, test_environment=test_environment)
        self.environment = credentials["data"]['environment']
        base64token = base64.b64encode(credentials['data']['token'].encode('utf-8')).decode()
        if test_environment:
            self.base_url = f'https://{self.environment}.resttest.afas.online/ProfitRestServices/connectors'
        else:
            self.base_url = f'https://{self.environment}.rest.afas.online/profitrestservices/connectors'

        # Initialize session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': 'AfasToken ' + base64token,
            'IntegrationId': '38092_135680',
            'Content-Type': 'application/json',
            "accept-language": "en-us",# To see errors in English :)

        })

        # Initialize all service classes
        self.employees = Employees(self)
        self.person = Person(self)
        self.organisation = Organisation(self)
        self.organisational_unit = OrganisationalUnit(self)
        self.cost_center = CostCenter(self)
        self.cost_carrier = CostCarrier(self)
        self.bank_account = BankAccount(self)
        self.debtor = Debtor(self)
        self.creditor = Creditor(self)
        self.journal_entry = JournalEntry(self)
        self.post_calculation = PostCalculation(self)
        self.function = EmployeeFunction(self)
        self.post_calculation = PostCalculation(self)
        self.custom_connector = CustomGetConnector(self)

        self.iso2_mapping = {
            "Afghanistan": "AF",
            "Åland Islands": "AX",
            "Albania": "AL",
            "Algeria": "DZ",
            "American Samoa": "AS",
            "Andorra": "AD",
            "Angola": "AO",
            "Anguilla": "AI",
            "Antarctica": "AQ",
            "Antigua and Barbuda": "AG",
            "Argentina": "AR",
            "Armenia": "AM",
            "Aruba": "AW",
            "Australia": "AU",
            "Austria": "AT",
            "Azerbaijan": "AZ",
            "Bahamas": "BS",
            "Bahrain": "BH",
            "Bangladesh": "BD",
            "Barbados": "BB",
            "Belarus": "BY",
            "Belgium": "BE",
            "Belize": "BZ",
            "Benin": "BJ",
            "Bermuda": "BM",
            "Bhutan": "BT",
            "Bolivia, Plurinational State of": "BO",
            "Bonaire, Sint Eustatius and Saba": "BQ",
            "Bosnia and Herzegovina": "BA",
            "Botswana": "BW",
            "Bouvet Island": "BV",
            "Brazil": "BR",
            "British Indian Ocean Territory": "IO",
            "Brunei Darussalam": "BN",
            "Bulgaria": "BG",
            "Burkina Faso": "BF",
            "Burundi": "BI",
            "Cambodia": "KH",
            "Cameroon": "CM",
            "Canada": "CA",
            "Cape Verde": "CV",
            "Cayman Islands": "KY",
            "Central African Republic": "CF",
            "Chad": "TD",
            "Chile": "CL",
            "China": "CN",
            "Christmas Island": "CX",
            "Cocos (Keeling) Islands": "CC",
            "Colombia": "CO",
            "Comoros": "KM",
            "Congo": "CG",
            "Congo, the Democratic Republic of the": "CD",
            "Cook Islands": "CK",
            "Costa Rica": "CR",
            "Côte d'Ivoire": "CI",
            "Croatia": "HR",
            "Cuba": "CU",
            "Curaçao": "CW",
            "Cyprus": "CY",
            "Czech Republic": "CZ",
            "Denmark": "DK",
            "Djibouti": "DJ",
            "Dominica": "DM",
            "Dominican Republic": "DO",
            "Ecuador": "EC",
            "Egypt": "EG",
            "El Salvador": "SV",
            "Equatorial Guinea": "GQ",
            "Eritrea": "ER",
            "Estonia": "EE",
            "Ethiopia": "ET",
            "Falkland Islands (Malvinas)": "FK",
            "Faroe Islands": "FO",
            "Fiji": "FJ",
            "Finland": "FI",
            "France": "FR",
            "French Guiana": "GF",
            "French Polynesia": "PF",
            "French Southern Territories": "TF",
            "Gabon": "GA",
            "Gambia": "GM",
            "Georgia": "GE",
            "Germany": "DE",
            "Ghana": "GH",
            "Gibraltar": "GI",
            "Greece": "GR",
            "Greenland": "GL",
            "Grenada": "GD",
            "Guadeloupe": "GP",
            "Guam": "GU",
            "Guatemala": "GT",
            "Guernsey": "GG",
            "Guinea": "GN",
            "Guinea-Bissau": "GW",
            "Guyana": "GY",
            "Haiti": "HT",
            "Heard Island and McDonald Islands": "HM",
            "Holy See (Vatican City State)": "VA",
            "Honduras": "HN",
            "Hong Kong": "HK",
            "Hungary": "HU",
            "Iceland": "IS",
            "India": "IN",
            "Indonesia": "ID",
            "Iran, Islamic Republic of": "IR",
            "Iraq": "IQ",
            "Ireland": "IE",
            "Isle of Man": "IM",
            "Israel": "IL",
            "Italy": "IT",
            "Jamaica": "JM",
            "Japan": "JP",
            "Jersey": "JE",
            "Jordan": "JO",
            "Kazakhstan": "KZ",
            "Kenya": "KE",
            "Kiribati": "KI",
            "Korea, Democratic People's Republic of": "KP",
            "Korea, Republic of": "KR",
            "Kosovo, Republic of": "XK",
            "Kuwait": "KW",
            "Kyrgyzstan": "KG",
            "Lao People's Democratic Republic": "LA",
            "Latvia": "LV",
            "Lebanon": "LB",
            "Lesotho": "LS",
            "Liberia": "LR",
            "Libya": "LY",
            "Liechtenstein": "LI",
            "Lithuania": "LT",
            "Luxembourg": "LU",
            "Macao": "MO",
            "Macedonia, the former Yugoslav Republic of": "MK",
            "Madagascar": "MG",
            "Malawi": "MW",
            "Malaysia": "MY",
            "Maldives": "MV",
            "Mali": "ML",
            "Malta": "MT",
            "Marshall Islands": "MH",
            "Martinique": "MQ",
            "Mauritania": "MR",
            "Mauritius": "MU",
            "Mayotte": "YT",
            "Mexico": "MX",
            "Micronesia, Federated States of": "FM",
            "Moldova, Republic of": "MD",
            "Monaco": "MC",
            "Mongolia": "MN",
            "Montenegro": "ME",
            "Montserrat": "MS",
            "Morocco": "MA",
            "Mozambique": "MZ",
            "Myanmar": "MM",
            "Namibia": "NA",
            "Nauru": "NR",
            "Nepal": "NP",
            "Netherlands": "NL",
            "New Caledonia": "NC",
            "New Zealand": "NZ",
            "Nicaragua": "NI",
            "Niger": "NE",
            "Nigeria": "NG",
            "Niue": "NU",
            "Norfolk Island": "NF",
            "Northern Mariana Islands": "MP",
            "Norway": "NO",
            "Oman": "OM",
            "Pakistan": "PK",
            "Palau": "PW",
            "Palestine, State of": "PS",
            "Panama": "PA",
            "Papua New Guinea": "PG",
            "Paraguay": "PY",
            "Peru": "PE",
            "Philippines": "PH",
            "Pitcairn": "PN",
            "Poland": "PL",
            "Portugal": "PT",
            "Puerto Rico": "PR",
            "Qatar": "QA",
            "Réunion": "RE",
            "Romania": "RO",
            "Russian Federation": "RU",
            "Rwanda": "RW",
            "Saint Barthélemy": "BL",
            "Saint Helena, Ascension and Tristan da Cunha": "SH",
            "Saint Kitts and Nevis": "KN",
            "Saint Lucia": "LC",
            "Saint Martin (French part)": "MF",
            "Saint Pierre and Miquelon": "PM",
            "Saint Vincent and the Grenadines": "VC",
            "Samoa": "WS",
            "San Marino": "SM",
            "Sao Tome and Principe": "ST",
            "Saudi Arabia": "SA",
            "Senegal": "SN",
            "Serbia": "RS",
            "Seychelles": "SC",
            "Sierra Leone": "SL",
            "Singapore": "SG",
            "Sint Maarten (Dutch part)": "SX",
            "Slovakia": "SK",
            "Slovenia": "SI",
            "Solomon Islands": "SB",
            "Somalia": "SO",
            "South Africa": "ZA",
            "South Georgia and the South Sandwich Islands": "GS",
            "South Sudan": "SS",
            "Spain": "ES",
            "Sri Lanka": "LK",
            "Sudan": "SD",
            "Suriname": "SR",
            "Svalbard and Jan Mayen": "SJ",
            "Swaziland": "SZ",
            "Sweden": "SE",
            "Switzerland": "CH",
            "Syrian Arab Republic": "SY",
            "Taiwan, Province of China": "TW",
            "Tajikistan": "TJ",
            "Tanzania, United Republic of": "TZ",
            "Thailand": "TH",
            "Timor-Leste": "TL",
            "Togo": "TG",
            "Tokelau": "TK",
            "Tonga": "TO",
            "Trinidad and Tobago": "TT",
            "Tunisia": "TN",
            "Turkey": "TR",
            "Turkmenistan": "TM",
            "Turks and Caicos Islands": "TC",
            "Tuvalu": "TV",
            "Uganda": "UG",
            "Ukraine": "UA",
            "United Arab Emirates": "AE",
            "United Kingdom": "GB",
            "United States": "USA",
            "United States Minor Outlying Islands": "UM",
            "Uruguay": "UY",
            "Uzbekistan": "UZ",
            "Vanuatu": "VU",
            "Venezuela, Bolivarian Republic of": "VE",
            "Viet Nam": "VN",
            "Virgin Islands, British": "VG",
            "Virgin Islands, U.S.": "VI",
            "Wallis and Futuna": "WF",
            "Western Sahara": "EH",
            "Yemen": "YE",
            "Zambia": "ZM",
            "Zimbabwe": "ZW"
        }
        self.nationality_mapping = {
            "Afghan": "AF",
            "Albanian": "AL",
            "Algerian": "DZ",
            "American": "US",
            "Andorran": "AD",
            "Angolan": "AO",
            "Antiguans": "AG",
            "Argentinean": "AR",
            "Armenian": "AM",
            "Australian": "AU",
            "Austrian": "AT",
            "Azerbaijani": "AZ",
            "Bahamian": "BS",
            "Bahraini": "BH",
            "Bangladeshi": "BD",
            "Barbadian": "BB",
            "Barbudans": "AG",  # Antigua and Barbuda shares the same code
            "Batswana": "BW",
            "Belarusian": "BY",
            "Belgian": "BE",
            "Belizean": "BZ",
            "Beninese": "BJ",
            "Bhutanese": "BT",
            "Bolivian": "BO",
            "Bosnian": "BA",
            "Brazilian": "BR",
            "British": "GB",
            "Bruneian": "BN",
            "Bulgarian": "BG",
            "Burkinabe": "BF",
            "Burmese": "MM",
            "Burundian": "BI",
            "Cambodian": "KH",
            "Cameroonian": "CM",
            "Canadian": "CA",
            "Cape Verdean": "CV",
            "Central African": "CF",
            "Chadian": "TD",
            "Chilean": "CL",
            "Chinese": "CN",
            "Colombian": "CO",
            "Comoran": "KM",
            "Congolese": "CG",  # Republic of the Congo
            "Costa Rican": "CR",
            "Croatian": "HR",
            "Cuban": "CU",
            "Cypriot": "CY",
            "Czech": "CZ",
            "Danish": "DK",
            "Djibouti": "DJ",
            "Dominican": "DO",
            "Dutch": "NL",
            "East Timorese": "TL",
            "Ecuadorean": "EC",
            "Egyptian": "EG",
            "Emirian": "AE",
            "Equatorial Guinean": "GQ",
            "Eritrean": "ER",
            "Estonian": "EE",
            "Ethiopian": "ET",
            "Fijian": "FJ",
            "Filipino": "PH",
            "Finnish": "FI",
            "French": "FR",
            "Gabonese": "GA",
            "Gambian": "GM",
            "Georgian": "GE",
            "German": "DE",
            "Ghanaian": "GH",
            "Greek": "GR",
            "Grenadian": "GD",
            "Guatemalan": "GT",
            "Guinea-Bissauan": "GW",
            "Guinean": "GN",
            "Guyanese": "GY",
            "Haitian": "HT",
            "Herzegovinian": "BA",  # Bosnia and Herzegovina
            "Honduran": "HN",
            "Hongkonger": "HK",
            "Hungarian": "HU",
            "Icelander": "IS",
            "Indian": "IN",
            "Indonesian": "ID",
            "Iranian": "IR",
            "Iraqi": "IQ",
            "Irish": "IE",
            "Israeli": "IL",
            "Italian": "IT",
            "Ivorian": "CI",
            "Jamaican": "JM",
            "Japanese": "JP",
            "Jordanian": "JO",
            "Kazakhstani": "KZ",
            "Kenyan": "KE",
            "Kittian and Nevisian": "KN",
            "Kuwaiti": "KW",
            "Kyrgyz": "KG",
            "Laotian": "LA",
            "Latvian": "LV",
            "Lebanese": "LB",
            "Liberian": "LR",
            "Libyan": "LY",
            "Liechtensteiner": "LI",
            "Lithuanian": "LT",
            "Luxembourgish": "LU",
            "Macedonian": "MK",
            "Malagasy": "MG",
            "Malawian": "MW",
            "Malaysian": "MY",
            "Maldivan": "MV",
            "Malian": "ML",
            "Maltese": "MT",
            "Marshallese": "MH",
            "Mauritanian": "MR",
            "Mauritian": "MU",
            "Mexican": "MX",
            "Micronesian": "FM",
            "Moldovan": "MD",
            "Monacan": "MC",
            "Mongolian": "MN",
            "Montenegrin": "ME",
            "Moroccan": "MA",
            "Mosotho": "LS",
            "Motswana": "BW",  # Same as Botswana
            "Mozambican": "MZ",
            "Namibian": "NA",
            "Nauruan": "NR",
            "Nepalese": "NP",
            "Netherlander": "NL",
            "New Zealander": "NZ",
            "Ni-Vanuatu": "VU",
            "Nicaraguan": "NI",
            "Nigerian": "NG",
            "Nigerien": "NE",
            "North Korean": "KP",
            "Northern Irish": "GB",  # Part of UK
            "Norwegian": "NO",
            "Omani": "OM",
            "Pakistani": "PK",
            "Palauan": "PW",
            "Palestinian": "PS",
            "Panamanian": "PA",
            "Papua New Guinean": "PG",
            "Paraguayan": "PY",
            "Peruvian": "PE",
            "Polish": "PL",
            "Portuguese": "PT",
            "Qatari": "QA",
            "Romanian": "RO",
            "Russian": "RU",
            "Rwandan": "RW",
            "Saint Lucian": "LC",
            "Salvadoran": "SV",
            "Samoan": "WS",
            "San Marinese": "SM",
            "Sao Tomean": "ST",
            "Saudi": "SA",
            "Scottish": "GB",  # Part of UK
            "Senegalese": "SN",
            "Serbian": "RS",
            "Seychellois": "SC",
            "Sierra Leonean": "SL",
            "Singaporean": "SG",
            "Slovakian": "SK",
            "Slovenian": "SI",
            "Solomon Islander": "SB",
            "Somali": "SO",
            "South African": "ZA",
            "South Korean": "KR",
            "Spanish": "ES",
            "Sri Lankan": "LK",
            "Sudanese": "SD",
            "Surinamer": "SR",
            "Swazi": "SZ",
            "Swedish": "SE",
            "Swiss": "CH",
            "Syrian": "SY",
            "Taiwanese": "TW",
            "Tajik": "TJ",
            "Tanzanian": "TZ",
            "Thai": "TH",
            "Togolese": "TG",
            "Tongan": "TO",
            "Trinidadian or Tobagonian": "TT",
            "Tunisian": "TN",
            "Turkish": "TR",
            "Tuvaluan": "TV",
            "Ugandan": "UG",
            "Ukrainian": "UA",
            "Uruguayan": "UY",
            "Uzbekistani": "UZ",
            "Venezuelan": "VE",
            "Vietnamese": "VN",
            "Welsh": "GB",  # Part of UK
            "Yemenite": "YE",
            "Zambian": "ZM",
            "Zimbabwean": "ZW"
        }

    @staticmethod
    def create_typed_empty_df(schema: Type[pa.DataFrameModel]) -> pd.DataFrame:
        """
        Create an empty DataFrame with columns matching the schema's data types.

        Args:
            schema (pa.DataFrameModel): The Pandera schema to use for generating the DataFrame.

        Returns:
            pd.DataFrame: An empty DataFrame with schema-matching column types.
        """
        # Extract schema columns and their definitions
        schema_columns = schema.to_schema().columns

        # Prepare a dictionary for columns and their corresponding dtypes
        column_dtypes: Dict[str, Any] = {}

        for column_name, column_properties in schema_columns.items():
            # Extract the column's dtype
            dtype = column_properties.dtype.type

            # Assign the dtype to the column name
            column_dtypes[column_name] = dtype

        # Create an empty DataFrame with the defined dtypes
        empty_df = pd.DataFrame({col: pd.Series(dtype=dtype) for col, dtype in column_dtypes.items()})

        return empty_df

    @staticmethod
    def clean_nans(df):
        """
        Clean NaN values from DataFrame

        Args:
            df: DataFrame to clean

        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        # String columns: NaN -> ""
        string_cols = df.select_dtypes(include=['object']).columns
        df[string_cols] = df[string_cols].fillna("")

        # Numeric columns: NaN -> 0
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        df[numeric_cols] = df[numeric_cols].fillna('').replace({'': 0})

        # Boolean columns: NaN -> False
        bool_cols = df.select_dtypes(include=['bool']).columns
        df[bool_cols] = df[bool_cols].fillna(False)

        return df

    def fill_empty_df(self,empty_df:pd.DataFrame,data:dict)->pd.DataFrame:
        for column in empty_df.columns:
            if column in data:
                value = data[column]
                empty_df.at[0, column] = None if pd.isna(value) else value
            else:
                empty_df.at[0, column] = None
        empty_df = self.clean_nans(empty_df)
        return empty_df

    async def base_get(self, url: str, schema: Type[pa.DataFrameModel] = None, schema_required: bool = True,
                       filter_fields: Optional[dict] = None, batch_size: int = 8, take: int = 40000) -> Union[pd.DataFrame, str]:
        """
        Base GET method for AFAS API calls (async version, batched like legacy)

        Args:
            url: Base URL for the endpoint
            schema: Pandera schema for validation. Is required for all endpoints, except for custom connectors.
            schema_required: For safety: Whether the schema is required for the endpoint. Should only be set to False for custom connectors.
            filter_fields: Optional filters to apply
            batch_size: Number of pages to fetch concurrently per batch
            take: Page size (defaults to legacy value of 40000)

        Returns:
            pd.DataFrame: Validated response data
        """
        if schema_required and schema is None:
            raise ValueError("Schema is required for this endpoint")

        if filter_fields:
            filter_params = {
                'filterfieldids': ','.join(filter_fields.keys()),
                'filtervalues': ','.join(str(value) for value in filter_fields.values()),
                'operatortypes': ','.join(['1'] * len(filter_fields))
            }
            url = f"{url}?{'&'.join(f'{k}={v}' for k, v in filter_params.items())}"

        # Batched concurrent pagination (like legacy async implementation)
        rows: List[dict] = []

        conn = aiohttp.TCPConnector(
            force_close=True,
            enable_cleanup_closed=True
        )

        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async def fetch_page(session: aiohttp.ClientSession, page_skip: int) -> List[dict]:
            try:
                async with session.get(url, params={'skip': page_skip, 'take': take}) as resp:
                    resp.raise_for_status()
                    payload = await resp.json()
                    if not payload:
                        return []
                    return payload.get("rows", [])
            except aiohttp.ClientResponseError as http_error:
                error_message = f" HTTP STATUS CODE == '{http_error.status}'. HTTP ERROR MESSAGE == '{getattr(http_error, 'message', str(http_error))}'."
                if http_error.headers and 'X-Profit-Error' in http_error.headers:
                    error_header = http_error.headers['X-Profit-Error']
                    try:
                        decoded_error = base64.b64decode(error_header).decode('utf-8')
                        error_message += f" DECODED ERROR MESSAGE == '{decoded_error}'."
                    except Exception:
                        error_message += f" (Failed to decode 'X-Profit-Error' header: {error_header})"

                request_url = http_error.request_info.url if hasattr(http_error, 'request_info') and http_error.request_info else 'unknown URL'
                raise type(http_error)(
                    request_info=http_error.request_info,
                    history=http_error.history,
                    status=http_error.status,
                    message=f"{error_message}, URL='{request_url}'",
                    headers=http_error.headers
                ) from http_error
            except aiohttp.ClientError as client_error:
                request_url = getattr(client_error, 'url', 'unknown URL')
                raise type(client_error)(f"Client Error in pagination: {client_error}, URL='{request_url}'") from client_error
            except asyncio.TimeoutError as timeout_error:
                raise asyncio.TimeoutError(f"Timeout Error in pagination: The request took too long to complete. Original error: {timeout_error}") from timeout_error
            except Exception as general_error:
                raise Exception(f"An unexpected error occurred during pagination: {general_error}") from general_error

        async with aiohttp.ClientSession(
                headers=self.session.headers,
                connector=conn,
                timeout=timeout
        ) as session:
            got_all_results = False
            batch_number = 0
            while not got_all_results:
                tasks = []
                for i in range(batch_size):
                    page_skip = take * (i + batch_number * batch_size)
                    tasks.append(fetch_page(session, page_skip))

                batch_results: List[List[dict]] = await asyncio.gather(*tasks)

                # Flatten and detect end
                for page_rows in batch_results:
                    if not page_rows:
                        got_all_results = True
                    rows.extend(page_rows)
                    if len(page_rows) < take:
                        got_all_results = True

                batch_number += 1
                # Be polite between batches
                await asyncio.sleep(0.05)

        df = pd.DataFrame(rows)

        if 'Btw-nummer' in df.columns:
            df = df.rename(columns={'Btw-nummer': 'Btw_nummer'})

        #if schema is provided, validate the data, otherwise return the raw data if response_data is not empty
        if not df.empty:
            if schema_required and schema:
                valid_data, invalid_data = Functions.validate_data(
                    df=df,
                    schema=schema,
                    debug=True
                )
                return valid_data
            else:
                return df
        else:
            warnings.warn(f"No record found! Returning empty response DataFrame for {url}")
            return pd.DataFrame(rows)

    async def get_paginated_result(self, request: requests.Request) -> List:
        """
        Handle paginated requests to AFAS (async version)

        Args:
            request: Request object to send

        Returns:
            List of results from all pages
        """
        skip = 0
        take = 5000
        result_data = []

        conn = aiohttp.TCPConnector(
            force_close=True,
            enable_cleanup_closed=True
        )

        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
                headers=self.session.headers,
                connector=conn,
                timeout=timeout
        ) as session:
            while True:
                try:
                    if request.params is None:
                        request.params = {}
                    request.params.update({
                        'skip': skip,
                        'take': take
                    })

                    async with session.get(request.url, params=request.params) as resp:
                        resp.raise_for_status()
                        response_data = await resp.json()

                        if not response_data:
                            break

                        result_data.extend(response_data["rows"])

                        if len(response_data["rows"]) < take:
                            break

                        skip += take

                    await asyncio.sleep(0.1)

                #-- error handling
                except aiohttp.ClientResponseError as http_error:
                    error_message = f" HTTP STATUS CODE == '{http_error.status}'. HTTP ERROR MESSAGE == '{getattr(http_error, 'message', str(http_error))}'."
                    #detailed error message is b64 encoded inside the X-Profit-Error header (if present)
                    if http_error.headers and 'X-Profit-Error' in http_error.headers:
                        error_header = http_error.headers['X-Profit-Error']
                        try:
                            decoded_error = base64.b64decode(error_header).decode('utf-8')
                            error_message += f" DECODED ERROR MESSAGE == '{decoded_error}'."
                        except Exception:
                            error_message += f" (Failed to decode 'X-Profit-Error' header: {error_header})"

                    # Include the URL that caused the error if available
                    request_url = http_error.request_info.url if hasattr(http_error, 'request_info') and http_error.request_info else 'unknown URL'
                    raise type(http_error)(
                        request_info=http_error.request_info,
                        history=http_error.history,
                        status=http_error.status,
                        message=f"{error_message}, URL='{request_url}'",
                        headers=http_error.headers
                    ) from http_error

                except aiohttp.ClientError as client_error:
                    request_url = getattr(client_error, 'url', 'unknown URL')
                    raise type(client_error)(f"Client Error in pagination: {client_error}, URL='{request_url}'") from client_error

                except asyncio.TimeoutError as timeout_error:
                    raise asyncio.TimeoutError(f"Timeout Error in pagination: The request took too long to complete. Original error: {timeout_error}") from timeout_error

                except Exception as general_error:
                    raise Exception(f"An unexpected error occurred during pagination: {general_error}") from general_error

        return result_data

    def validate(self, schema: Type[pa.DataFrameModel], data: dict) -> dict:
        try:
            empty_df = self.create_typed_empty_df(schema)
            df = self.fill_empty_df(empty_df=empty_df, data=data)
            valid_data, invalid_data = Functions.validate_data(schema=schema, df=df)
            if valid_data.empty:
                raise ValueError(f"Data validation failed. Invalid data: {invalid_data}")

            return valid_data.to_dict('records')[0]
        except Exception as e:
            raise Exception(f"Validation error: {str(e)}")

    def convert_timestamp_columns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        converted = {}
        for key, value in data.items():
            if isinstance(value, (datetime.datetime, pd.Timestamp)):
                if pd.isnull(value):  # True for both NaN, NaT, etc.
                    converted[key] = None  # or '' or 'N/A'
                else:
                    converted[key] = value.strftime('%Y-%m-%d')
            else:
                converted[key] = value
        return converted

    def list_connectors(self, type: Literal['get', 'update'] = 'get') -> List[str]:
        """
        Get list of available connectors

        Args:
            type: Type of connectors to list ('get' or 'update')

        Returns:
            List[str]: List of connector names

        Raises:
            Exception: If listing connectors fails
        """
        try:
            metadata = self.get_metadata(type=type)
            if isinstance(metadata, dict):
                return list(metadata.keys())
            elif isinstance(metadata, list):
                return [conn.get('name', '') for conn in metadata if 'name' in conn]
            else:
                return []
        except Exception as e:
            raise Exception(f"List connectors failed: {str(e)}") from e
