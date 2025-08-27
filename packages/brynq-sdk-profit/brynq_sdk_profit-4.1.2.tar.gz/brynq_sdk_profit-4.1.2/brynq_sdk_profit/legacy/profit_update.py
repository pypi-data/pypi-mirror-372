from brynq_sdk_brynq import BrynQ
import base64
import json
import warnings
from datetime import datetime
import pandas as pd
import requests
from typing import Union, List


class UpdateConnector(BrynQ):
    def __init__(self, label: str, test_environment: bool = False, debug: bool = False):
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
        self.debug = debug

    def update(self, updateconnector, data) -> requests.Response:
        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, updateconnector)

        update = requests.request("PUT", url, data=data, headers=self.headers)

        return update


    def create_person(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        Creates a new Person (KnPerson) in AFAS, using MatchPer=7 (always create new).

        Required fields:
          - person_id

        Allowed fields (mapped to KnPerson Fields):
          - birthname_partner           -> NmPa
          - prefix_birthname_partner    -> IsPa
          - birthname                   -> NmBi
          - last_name                   -> LaNm
          - prefix_birthname            -> IsBi
          - usual_name                  -> CaNm
          - firstname                   -> FiNm
          - marital_status              -> ViCs
          - date_of_marriage            -> DaMa
          - date_of_divorce            -> DaDi
          - date_of_death              -> DaDe
          - nationality                 -> PsNa
          - salutation                  -> TtId
          - email_work                  -> EmAd
          - email_private               -> EmA2
          - phone_work                  -> TeNr
          - phone_private               -> TeN2
          - mobile_work                 -> MbNr
          - mobile_private              -> MbN2
          - gender                      -> ViGe
          - date_of_birth               -> DaBi
          - country_of_birth            -> CoBi
          - place_of_birth              -> RsBi
          - social_security_number      -> SoSe
          - initials                    -> In
        """
        required_fields = ['person_id']
        allowed_fields = [
            'birthname_partner', 'prefix_birthname_partner', 'birthname', 'last_name',
            'prefix_birthname', 'usual_name', 'firstname', 'marital_status', 'date_of_marriage',
            'date_of_divorce', 'date_of_death', 'nationality', 'salutation', 'email_work', 'email_private',
            'phone_work', 'phone_private', 'mobile_work', 'mobile_private', 'gender', 'date_of_birth',
            'country_of_birth', 'place_of_birth', 'social_security_number', 'initials', 'name_usage'
        ]

        # Check fields
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnPerson"

        # Base body (some fields are set to fixed values: MatchPer=7 => always new, SpNm=True => 'birthname separately')
        base_body = {
            "KnPerson": {
                "Element": {
                    "Fields": {
                        "MatchPer": "7",  # Always create new
                        "BcCo": data['person_id'],
                    }
                }
            }
        }

        # Collect fields to update
        fields_to_update = {}

        # If the data has both 'last_name' and 'birthname', you can choose which to use for LaNm:
        if 'last_name' in data:
            fields_to_update.update({"LaNm": data['last_name']})
        elif 'birthname' in data:
            fields_to_update.update({"LaNm": data['birthname']})

        fields_to_update.update({"NmPa": data['birthname_partner']}) if 'birthname_partner' in data else None
        fields_to_update.update(
            {"IsPa": data['prefix_birthname_partner']}) if 'prefix_birthname_partner' in data else None
        fields_to_update.update({"NmBi": data['birthname']}) if 'birthname' in data else None
        fields_to_update.update({"IsBi": data['prefix_birthname']}) if 'prefix_birthname' in data else None
        fields_to_update.update({"CaNm": data['usual_name']}) if 'usual_name' in data else None
        fields_to_update.update({"FiNm": data['firstname']}) if 'firstname' in data else None
        fields_to_update.update({"ViCs": data['marital_status']}) if 'marital_status' in data else None
        fields_to_update.update({"DaMa": data['date_of_marriage']}) if 'date_of_marriage' in data else None
        fields_to_update.update({"DaDi": data['date_of_divorce']}) if 'date_of_divorce' in data else None
        fields_to_update.update({"DaDe": data['date_of_death']}) if 'date_of_death' in data else None
        fields_to_update.update({"PsNa": data['nationality']}) if 'nationality' in data else None
        fields_to_update.update({"TtId": data['salutation']}) if 'salutation' in data else None
        fields_to_update.update({"EmAd": data['email_work']}) if 'email_work' in data else None
        fields_to_update.update({"EmA2": data['email_private']}) if 'email_private' in data else None
        fields_to_update.update({"TeNr": data['phone_work']}) if 'phone_work' in data else None
        fields_to_update.update({"TeN2": data['phone_private']}) if 'phone_private' in data else None
        fields_to_update.update({"MbNr": data['mobile_work']}) if 'mobile_work' in data else None
        fields_to_update.update({"MbN2": data['mobile_private']}) if 'mobile_private' in data else None
        fields_to_update.update({"ViGe": data['gender']}) if 'gender' in data else None
        fields_to_update.update({"DaBi": data['date_of_birth']}) if 'date_of_birth' in data else None
        fields_to_update.update({"CoBi": data['country_of_birth']}) if 'country_of_birth' in data else None
        fields_to_update.update({"RsBi": data['place_of_birth']}) if 'place_of_birth' in data else None
        fields_to_update.update({"SoSe": data['social_security_number']}) if 'social_security_number' in data else None
        fields_to_update.update({"In": data['initials']}) if 'initials' in data else None
        fields_to_update.update({"SpNm": data['birth_name_separate']}) if 'birth_name_separate' in data else fields_to_update
        fields_to_update.update({"ViUs": data['name_use']}) if 'name_use' in data else fields_to_update

        # Optionally merge any overload fields (custom fields)
        fields_to_update.update(overload_fields) if overload_fields else None

        # Merge into the base body
        base_body["KnPerson"]["Element"]["Fields"].update(fields_to_update)

        # POST request
        response = requests.request("POST", url, data=json.dumps(base_body), headers=self.headers)
        return response

    def update_crm_person(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        Updates an existing Person (KnPerson) in AFAS.

        This method is used when a record exists in KnPerson, but there is no requirement
        for the person to also have an associated employee record (KnEmployee).

        Key details:
          - MatchPer=0 (match by person_id).

        Required fields:
          - person_id

        Allowed fields:
          - birthname_partner           -> NmPa
          - prefix_birthname_partner    -> IsPa
          - birthname                   -> NmBi
          - last_name                   -> LaNm
          - prefix_birthname            -> IsBi
          - usual_name                  -> CaNm
          - firstname                   -> FiNm
          - marital_status              -> ViCs
          - date_of_marriage            -> DaMa
          - date_of_divorce             -> DaDi
          - date_of_death               -> DaDe
          - nationality                 -> PsNa
          - salutation                  -> TtId
          - email_work                  -> EmAd
          - email_private               -> EmA2
          - phone_work                  -> TeNr
          - phone_private               -> TeN2
          - mobile_work                 -> MbNr
          - mobile_private              -> MbN2
          - gender                      -> ViGe
          - date_of_birth               -> DaBi
          - country_of_birth            -> CoBi
          - place_of_birth              -> RsBi
          - social_security_number      -> SoSe
          - initials                    -> In

        This method should be used for updating personal details of a person who is
        not necessarily an employee.
        """

        # Define the fields we will check
        required_fields = ['person_id']
        allowed_fields = [
            'birthname_partner', 'prefix_birthname_partner', 'birthname', 'last_name',
            'prefix_birthname', 'usual_name', 'firstname', 'marital_status', 'date_of_marriage',
            'date_of_divorce', 'date_of_death', 'nationality', 'salutation', 'email_work', 'email_private',
            'phone_work', 'phone_private', 'mobile_work', 'mobile_private', 'gender', 'date_of_birth',
            'country_of_birth', 'place_of_birth', 'social_security_number', 'initials', 'name_usage'
        ]

        # Check fields
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnPerson"

        # Base body (some fields are set to fixed values)
        base_body = {
            "KnPerson": {
                "Element": {
                    "Fields": {
                        "MatchPer": "0",  # Match existing person
                        "BcCo": data['person_id'],
                    }
                }
            }
        }

        # Collect fields to update
        fields_to_update = {}

        # Use 'last_name' if available; otherwise fall back to 'birthname'
        if 'last_name' in data:
            fields_to_update.update({"LaNm": data['last_name']})
        elif 'birthname' in data:
            fields_to_update.update({"LaNm": data['birthname']})

        fields_to_update.update({"NmPa": data['birthname_partner']}) if 'birthname_partner' in data else None
        fields_to_update.update(
            {"IsPa": data['prefix_birthname_partner']}) if 'prefix_birthname_partner' in data else None
        fields_to_update.update({"NmBi": data['birthname']}) if 'birthname' in data else None
        fields_to_update.update({"IsBi": data['prefix_birthname']}) if 'prefix_birthname' in data else None
        fields_to_update.update({"CaNm": data['usual_name']}) if 'usual_name' in data else None
        fields_to_update.update({"FiNm": data['firstname']}) if 'firstname' in data else None
        fields_to_update.update({"ViCs": data['marital_status']}) if 'marital_status' in data else None
        fields_to_update.update({"DaMa": data['date_of_marriage']}) if 'date_of_marriage' in data else None
        fields_to_update.update({"DaDi": data['date_of_divorce']}) if 'date_of_divorce' in data else None
        fields_to_update.update({"DaDe": data['date_of_death']}) if 'date_of_death' in data else None
        fields_to_update.update({"PsNa": data['nationality']}) if 'nationality' in data else None
        fields_to_update.update({"TtId": data['salutation']}) if 'salutation' in data else None
        fields_to_update.update({"EmAd": data['email_work']}) if 'email_work' in data else None
        fields_to_update.update({"EmA2": data['email_private']}) if 'email_private' in data else None
        fields_to_update.update({"TeNr": data['phone_work']}) if 'phone_work' in data else None
        fields_to_update.update({"TeN2": data['phone_private']}) if 'phone_private' in data else None
        fields_to_update.update({"MbNr": data['mobile_work']}) if 'mobile_work' in data else None
        fields_to_update.update({"MbN2": data['mobile_private']}) if 'mobile_private' in data else None
        fields_to_update.update({"ViGe": data['gender']}) if 'gender' in data else None
        fields_to_update.update({"DaBi": data['date_of_birth']}) if 'date_of_birth' in data else None
        fields_to_update.update({"CoBi": data['country_of_birth']}) if 'country_of_birth' in data else None
        fields_to_update.update({"RsBi": data['place_of_birth']}) if 'place_of_birth' in data else None
        fields_to_update.update({"SoSe": data['social_security_number']}) if 'social_security_number' in data else None
        fields_to_update.update({"In": data['initials']}) if 'initials' in data else None
        fields_to_update.update({"SpNm": data['birth_name_separate']}) if 'birth_name_separate' in data else None
        fields_to_update.update({"ViUs": data['name_use']}) if 'name_use' in data else None

        # Optionally merge any overload fields (custom fields)
        fields_to_update.update(overload_fields) if overload_fields else None

        # Merge into the base body
        base_body["KnPerson"]["Element"]["Fields"].update(fields_to_update)

        # PUT request
        response = requests.request("PUT", url, data=json.dumps(base_body), headers=self.headers)
        return response

    def update_person(self, data: dict, overload_fields: dict = None, method='PUT') -> requests.Response:
        """
        Updates an existing Person (KnPerson) and their associated Employee (KnEmployee) in AFAS.

        This method is used when a person has both a KnPerson record and an associated
        employee record (KnEmployee). The updates are applied to both the KnPerson and
        KnEmployee records as applicable.

        Required fields:
          - employee_id
          - person_id

        Allowed fields:
          - mail_work                  -> EmAd
          - mail_private               -> EmA2
          - mobile_work                -> MbNr
          - mobile_private             -> MbN2
          - nickname                   -> CaNm
          - first_name                 -> FiNm
          - initials                   -> In
          - prefix                     -> Is
          - last_name                  -> LaNm
          - prefix_birth_name          -> IsBi
          - birth_name                 -> NmBi
          - gender                     -> ViGe
          - nationality                -> PsNa
          - birth_date                 -> DaBi
          - country_of_birth           -> CoBi
          - ssn                        -> SoSe
          - marital_status             -> ViCs
          - date_of_marriage           -> DaMa
          - date_of_divorce            -> DaDi
          - phone_work                 -> TeNr
          - phone_private              -> TeN2
          - city_of_birth              -> RsBi
          - birth_name_separate        -> SpNm
          - name_use                   -> ViUs
          - match_person_on            -> MatchPer
          - birthname_partner          -> NmPa
          - prefix_birthname_partner   -> IsPa

        This method is more specific than `update_crm_person`, as it also requires
        the employee_id field and assumes the person is also an employee.
        """

        allowed_fields = ['employee_id', 'mail_work', 'mail_private', 'mobile_work', 'mobile_private', 'nickname', 'first_name', 'initials', 'prefix', 'last_name', 'prefix_birth_name',
                          'birth_name', 'gender', 'nationality', 'birth_date', 'country_of_birth', 'ssn', 'marital_status', 'date_of_marriage', 'date_of_divorce', 'phone_work', 'phone_private', 'city_of_birth',
                          'birth_name_separate', 'name_use', 'match_person_on', 'birthname_partner', 'prefix_birthname_partner']
        required_fields = ['employee_id', 'person_id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/KnPerson')

        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": "0" if "match_person_on" not in data else data['match_person_on'],
                                    "BcCo": data['person_id']
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"EmAd": data['mail_work']}) if 'mail_work' in data else fields_to_update
        fields_to_update.update({"EmA2": data['mail_private']}) if 'mail_private' in data else fields_to_update
        fields_to_update.update({"MbNr": data['mobile_work']}) if 'mobile_work' in data else fields_to_update
        fields_to_update.update({"MbN2": data['mobile_private']}) if 'mobile_private' in data else fields_to_update
        fields_to_update.update({"CaNm": data['nickname']}) if 'nickname' in data else fields_to_update
        fields_to_update.update({"FiNm": data['first_name']}) if 'first_name' in data else fields_to_update
        fields_to_update.update({"In": data['initials']}) if 'initials' in data else fields_to_update
        fields_to_update.update({"Is": data['prefix']}) if 'prefix' in data else fields_to_update
        fields_to_update.update({"LaNm": data['last_name']}) if 'last_name' in data else fields_to_update
        fields_to_update.update({"IsBi": data['prefix_birth_name']}) if 'prefix_birth_name' in data else fields_to_update
        fields_to_update.update({"NmBi": data['birth_name']}) if 'birth_name' in data else fields_to_update
        fields_to_update.update({"ViGe": data['gender']}) if 'gender' in data else fields_to_update
        fields_to_update.update({"PsNa": data['nationality']}) if 'nationality' in data else fields_to_update
        fields_to_update.update({"DaBi": data['birth_date']}) if 'birth_date' in data else fields_to_update
        fields_to_update.update({"CoBi": data['country_of_birth']}) if 'country_of_birth' in data else fields_to_update
        fields_to_update.update({"SoSe": data['ssn']}) if 'ssn' in data else fields_to_update
        fields_to_update.update({"ViCs": data['marital_status']}) if 'marital_status' in data else fields_to_update
        fields_to_update.update({"DaMa": data['date_of_marriage']}) if 'date_of_marriage' in data else fields_to_update
        fields_to_update.update({"DaMa": data['date_of_divorce']}) if 'date_of_divorce' in data else fields_to_update
        fields_to_update.update({"TeNr": data['phone_work']}) if 'phone_work' in data else fields_to_update
        fields_to_update.update({"TeN2": data['phone_private']}) if 'phone_private' in data else fields_to_update
        fields_to_update.update({"RsBi": data['city_of_birth']}) if 'city_of_birth' in data else fields_to_update
        fields_to_update.update({"SpNm": data['birth_name_separate']}) if 'birth_name_separate' in data else fields_to_update
        fields_to_update.update({"ViUs": data['name_use']}) if 'name_use' in data else fields_to_update
        fields_to_update.update({"NmPa": data['birthname_partner']}) if 'birthname_partner' in data else fields_to_update
        fields_to_update.update({"IsPa": data['prefix_birthname_partner']}) if 'prefix_birthname_partner' in data else fields_to_update

        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_user(self, data: dict, method='POST') -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param method: request type (must be post or put)
        :return: status code for request and optional error message
        """
        allowed_fields = ['profit_user_code', 'person_id', 'userPrincipalName', 'mail', 'outsite_access']
        required_fields = ['profit_user_code', 'person_id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnUser'

        base_body = {
            "KnUser": {
                "Element": {
                    "@UsId": data['profit_user_code'],
                    "Fields": {
                        "MtCd": 1,
                        "BcCo": data['person_id'],
                        "Nm": "BRYNQ",
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"Upn": data['userPrincipalName']}) if 'userPrincipalName' in data else fields_to_update
        fields_to_update.update({"EmAd": data['mail']}) if 'mail' in data else fields_to_update
        fields_to_update.update({"Site": data['outsite_access']}) if 'outsite_access' in data else fields_to_update

        # Update the request body with update fields
        base_body['KnUser']['Element']['Fields'].update(fields_to_update)

        if self.debug:
            print(json.dumps(base_body))

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def upload_photo(self, filepath: str, person_id: str, filename: str = None) -> requests.Response:
        """
        This code opens a file located at filename in binary mode, reads its contents, encodes the contents in base64, and assigns the result to filestream.
        Then, it creates a JSON object representing an image upload request to an API endpoint.
        This JSON object is converted to a string using json.dumps and assigned to body_image_upload.
        :param filepath: The filepath (complete path including filename) of the image to be uploaded
        :param filename: The filename of the image to be uploaded
        :param person_id: The personal id number of the user in AFAS
        """
        open_file = open(filepath, 'rb').read()
        filestream = base64.b64encode(open_file).decode('utf-8')
        body_image_upload = {"KnPerson": {
            "Element": {
                "Fields": {
                    "MatchPer": "0",
                    "BcCo": person_id,
                    "FileName": "filename" if filename is None else filename,
                    "FileStream": filestream,

                }
            }
        }
        }
        body_image_upload = json.dumps(body_image_upload)
        url = f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnPerson'
        update = requests.put(url=url, data=body_image_upload, headers=self.headers)
        return update

    def update_organisation(self, data: dict, method: str, custom_fields: dict = None) -> requests.Response:
        """
        This function updates organisations in CRM with the AFAS updateconnect 'KnOrganisation'.
        :param data: Deliver all the data which should be updated in list format. The data should at least contain the required_fields and can contain also the allowed fields
        :param method: Is a PUT for an update of an existing cost carrier. is a POST for an insert of a new cost carrier
        :param custom_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: The status code from AFAS Profit
        """
        required_fields = ['organisation_id', 'name', 'blocked']
        allowed_fields = ['collective_ledger_account', 'search_name', 'kvk_number', 'phone_number_work', 'email_work', 'vat_number', 'status',
                          'mailbox_address', 'country', 'street', 'housenumber', 'housenumber_add', 'zipcode', 'residence', 'search_living_place_by_zipcode']

        # Check if the fields in data exists in the required or allowed fields
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        if method != 'PUT' and method != 'POST' and method != 'DELETE':
            raise ValueError('Parameter method should be PUT, POST or DELETE (in uppercase)')

        if method == 'DELETE':
            url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnOrganisation/KnOrganisation/MatchOga,BdIdBcCo,Nm,Bl/0,1,{data['organisation_id']},{data['name']},{data['blocked']}"
            base_body = {}
        else:
            url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnOrganisation')

            base_body = {
                "KnOrganisation": {
                    "Element": {
                        "Fields": {
                            "MatchOga": "0",
                            "BcId": 1,
                            "BcCo": data['organisation_id'],
                            "Nm": data['name'],
                            "Bl": data['blocked']
                        },
                        "Objects": {

                        }
                    }
                }
            }

            address_body = {
                "KnBasicAddressAdr": {
                    "Element": {
                        "Fields": {
                        }
                    }
                }
            }

            # If one of the optional fields of a subelement is included, we need to merge the whole JSON object to the basebody
            if any(field in data.keys() for field in allowed_fields):
                fields_to_update = {}
                fields_to_update.update({"PbAd": data['mailbox_address']}) if 'mailbox_address' in data else fields_to_update
                fields_to_update.update({"CoId": data['country']}) if 'country' in data else fields_to_update
                fields_to_update.update({"Ad": data['street']}) if 'street' in data else fields_to_update
                fields_to_update.update({"HmNr": data['housenumber']}) if 'housenumber' in data else fields_to_update
                fields_to_update.update({"HmAd": data['housenumber_add']}) if 'housenumber_add' in data else fields_to_update
                fields_to_update.update({"ZpCd": data['zipcode']}) if 'zipcode' in data else fields_to_update
                fields_to_update.update({"Rs": data['residence']}) if 'residence' in data else fields_to_update
                fields_to_update.update({"ResZip": data['search_living_place_by_zipcode']}) if 'search_living_place_by_zipcode' in data else fields_to_update

                # merge subelement with basebody if there are address fields added. If not, don't add the address part to the base_body
                if len(fields_to_update) > 0:
                    address_body['KnBasicAddressAdr']['Element']['Fields'].update(fields_to_update)
                    base_body['KnOrganisation']['Element']['Objects'].update(address_body)

            # Add allowed fields to the basebody if they are available in the data. Fields that are not exists in the basebody, should not be added tot this basebody to prevent errrors.
            fields_to_update = {}
            fields_to_update.update({"SeNm": data['search_name']}) if 'search_name' in data else fields_to_update
            fields_to_update.update({"CcNr": data['kvk_number']}) if 'kvk_number' in data else fields_to_update
            fields_to_update.update({"TeNr": data['phone_number_work']}) if 'phone_number_work' in data else fields_to_update
            fields_to_update.update({"EmAd": data['email_work']}) if 'email_work' in data else fields_to_update
            fields_to_update.update({"FiNr": data['vat_number']}) if 'vat_number' in data else fields_to_update
            fields_to_update.update({"StId": data['status']}) if 'status' in data else fields_to_update

            base_body['KnOrganisation']['Element']['Fields'].update(fields_to_update)

            # Now create a dict for all the custom fields. This fields are not by default added to the base_body because they're not always present in the dataset
            fields_to_update = {}
            fields_to_update.update(custom_fields) if custom_fields is not None else ''

            # Update the request body with update fields
            base_body['KnOrganisation']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def connect_person_to_organisation(self, data: dict) -> requests.Response:
        required_fields = ['organisation_id', 'organisation_number', 'person_id', 'person_number', 'kind_of_relation', 'match_organisation_on', 'match_person_on']
        allowed_fields = ['postal_address_applied', 'organisation_name', 'last_name', 'role', 'country', 'street', 'house_number', 'house_number_add', 'house_number_add',
                          'postal_code', 'city', 'search_address_by_postal_code', 'address_is_postal_address']
        # Check if the fields in data exists in the required or allowed fields
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnOrganisation'

        base_body = {
            "KnOrganisation": {
                "Element": {
                    "Fields": {
                        "MatchOga": data['match_organisation_on'],
                        "BcId": data['organisation_id'],
                        "BcCo": data['organisation_number'],
                        "Nm": data['name']
                    },
                    "Objects": {
                        "KnContact": {
                            "Element": {
                                "Fields": {
                                    "ViKc": data['kind_of_relation']
                                },
                                "Objects": [
                                    {
                                        "KnPerson": {
                                            "Element": {
                                                "Fields": {
                                                    "MatchPer": data['match_person_on'],
                                                    "BcId": data['person_id'],
                                                    "BcCo": data['person_number']
                                                },
                                                'Objects': [
                                                ]
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
        role_body = {
            "KnContactAutRole": {
                "Element": {
                    "Fields": {
                    }
                }
            }
        }
        address_body = {
            "KnBasicAddressAdr": {
                "Element": {
                    "Fields": {
                    }
                }
            }
        }

        # Update the base structure of the organisation if needed
        fields_to_update = {}
        fields_to_update.update({"PadAdr": data['postal_address_applied']}) if 'postal_address_applied' in data else fields_to_update
        fields_to_update.update({"Nm": data['organisation_name']}) if 'organisation_name' in data else fields_to_update
        base_body['KnOrganisation']['Element']['Fields'].update(fields_to_update)

        # Update the person if there is data for the person
        fields_to_update = {}
        fields_to_update.update({"PadAdr": data['postal_address_applied']}) if 'postal_address_applied' in data else fields_to_update
        fields_to_update.update({"LaNm": data['last_name']}) if 'last_name' in data else fields_to_update
        base_body['KnOrganisation']['Element']['Objects']['KnContact']['Element']['Objects'][0]['KnPerson']['Element']['Fields'].update(fields_to_update)

        # Add a role to the body if the field role is in the data
        fields_to_update = {}
        fields_to_update.update({"AutRoleDs": data['role']}) if 'role' in data else fields_to_update
        if len(fields_to_update) > 0:
            role_body['KnContactAutRole']['Element']['Fields'].update(fields_to_update)
            base_body['KnOrganisation']['Element']['Objects']['KnContact']['Element']['Objects'][0]['KnPerson']['Element']['Objects'].append(role_body)

        # Add address data if there is any
        fields_to_update = {}
        fields_to_update.update({"CoId": data['country']}) if 'country' in data else fields_to_update
        fields_to_update.update({"PbAd": data['address_is_postal_address']}) if 'address_is_postal_address' in data else fields_to_update
        fields_to_update.update({"Ad": data['street']}) if 'street' in data else fields_to_update
        fields_to_update.update({"HmNr": data['house_number']}) if 'house_number' in data else fields_to_update
        fields_to_update.update({"HmAd": data['house_number_add']}) if 'house_number_add' in data else fields_to_update
        fields_to_update.update({"ZpCd": data['postal_code']}) if 'postal_code' in data else fields_to_update
        fields_to_update.update({"Rs": data['city']}) if 'city' in data else fields_to_update
        fields_to_update.update({"ResZip": data['search_address_by_postal_code']}) if 'search_address_by_postal_code' in data else fields_to_update
        if len(fields_to_update) > 0:
            address_body['KnBasicAddressAdr']['Element']['Fields'].update(fields_to_update)
            base_body['KnOrganisation']['Element']['Objects']['KnContact']['Element']['Objects'][0]['KnPerson']['Element']['Objects'].append(address_body)

        response = requests.request('POST', url, data=json.dumps(base_body), headers=self.headers)
        return response

    def update_debtor(self, data: dict, overload_fields: dict = None, method='PUT') -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :param method: request type
        :return: status code for request and optional error message
        """
        allowed_fields = ['match_person_on', 'enter_birthname_seperate', 'person_id', 'country', 'street', 'house_number', 'house_number_add', 'postal_code',
                          'mailbox_address', 'city', 'person_id', 'mail_private', 'nickname', 'first_name', 'initials', 'prefix', 'last_name',
                          'prefix_birth_name', 'birth_name', 'prefix_partner_name', 'partner_name', 'gender', 'phone_private', 'name_use',
                          'autonumber_person', 'search_address_by_postal_code', 'send_reminder']
        required_fields = ['debtor_id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnSalesRelationPer'

        base_body = {
            "KnSalesRelationPer": {
                "Element": {
                    "@DbId": data['debtor_id'],
                    "Fields": {
                        "CuId": "EUR",
                        "IsDb": True
                    },
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": "0" if "match_person_on" not in data else data['match_person_on'],
                                    "BcId": 1
                                },
                                "Objects": {
                                }
                            }
                        }
                    }
                }
            }
        }

        address_body = {
            "KnBasicAddressAdr": {
                "Element": {
                    "Fields": {
                    }
                }
            },
            "KnBasicAddressPad": {
                "Element": {
                    "Fields": {
                    }
                }
            }
        }

        # If one of the optional fields of a subelement is included, we need to merge the whole JSON object to the basebody
        if any(field in data.keys() for field in allowed_fields):
            fields_to_update = {}
            fields_to_update.update({"PbAd": data['mailbox_address']}) if 'mailbox_address' in data else fields_to_update
            fields_to_update.update({"CoId": data['country']}) if 'country' in data else fields_to_update
            fields_to_update.update({"Ad": data['street']}) if 'street' in data else fields_to_update
            fields_to_update.update({"HmNr": data['house_number']}) if 'house_number' in data else fields_to_update
            fields_to_update.update({"HmAd": data['house_number_add']}) if 'house_number_add' in data else fields_to_update
            fields_to_update.update({"ZpCd": data['postal_code']}) if 'postal_code' in data else fields_to_update
            fields_to_update.update({"Rs": data['city']}) if 'city' in data else fields_to_update
            fields_to_update.update({"ResZip": data['search_address_by_postal_code']}) if 'search_address_by_postal_code' in data else fields_to_update

            # merge subelement with basebody if there are address fields added. If not, don't add the address part to the base_body
            if len(fields_to_update) > 0:
                address_body['KnBasicAddressAdr']['Element']['Fields'].update(fields_to_update)
                address_body['KnBasicAddressPad']['Element']['Fields'].update(fields_to_update)
                base_body['KnSalesRelationPer']['Element']['Objects']['KnPerson']['Element']['Objects'].update(address_body)

        # Add fields to the basebody of the debtor itself (not the person)
        fields_to_update = {}
        fields_to_update.update({"ColA": data['collective_ledger_account']}) if 'collective_ledger_account' in data else fields_to_update
        fields_to_update.update({"PaCd": data['payment_condition']}) if 'payment_condition' in data else fields_to_update
        fields_to_update.update({"DuYN": data['send_reminder']}) if 'send_reminder' in data else fields_to_update
        # Update the request body with update fields
        base_body['KnSalesRelationPer']['Element']['Fields'].update(fields_to_update)

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update({"AutoNum": data['autonumber_person']}) if 'autonumber_person' in data else fields_to_update
        fields_to_update.update({"SpNm": data['enter_birthname_seperate']}) if 'enter_birthname_seperate' in data else fields_to_update
        fields_to_update.update({"BcCo": data['person_id']}) if 'person_id' in data else fields_to_update
        fields_to_update.update({"PbAd": data['mailbox_address']}) if 'mailbox_address' in data else fields_to_update
        fields_to_update.update({"EmA2": data['mail_private']}) if 'mail_private' in data else fields_to_update
        fields_to_update.update({"CaNm": data['nickname']}) if 'nickname' in data else fields_to_update
        fields_to_update.update({"FiNm": data['first_name']}) if 'first_name' in data else fields_to_update
        fields_to_update.update({"In": data['initials']}) if 'initials' in data else fields_to_update
        fields_to_update.update({"Is": data['prefix']}) if 'prefix' in data else fields_to_update
        fields_to_update.update({"LaNm": data['last_name']}) if 'last_name' in data else fields_to_update
        fields_to_update.update({"IsBi": data['prefix_birth_name']}) if 'prefix_birth_name' in data else fields_to_update
        fields_to_update.update({"NmBi": data['birth_name']}) if 'birth_name' in data else fields_to_update
        fields_to_update.update({"IsPa": data['prefix_partner_name']}) if 'prefix_partner_name' in data else fields_to_update
        fields_to_update.update({"NmPa": data['partner_name']}) if 'partner_name' in data else fields_to_update
        fields_to_update.update({"ViGe": data['gender']}) if 'gender' in data else fields_to_update
        fields_to_update.update({"TeN2": data['phone_private']}) if 'phone_private' in data else fields_to_update
        fields_to_update.update({"ViUs": data['name_use']}) if 'name_use' in data else fields_to_update

        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body['KnSalesRelationPer']['Element']['Objects']['KnPerson']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_creditor(self, method: str, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :param method: request type
        :return: status code for request and optional error message
        """
        allowed_fields_base = ['creditor_id', 'is_creditor', 'payment_to_external,' 'collective_account', 'preferred_delivery_method', 'automatic_payment', 'compact', 'payment_specification', 'remark', 'preferred_provisioning',
                                'preferred_iban']
        allowed_fields_person = ['person_id', 'internal_id', 'match_person_on', 'log_birthname_seperately', 'gender', 'salutation', 'correspondence', 'email', 'email_private' , 'mobile_phone',
                                 'outsite_access', 'outsite_email', 'auto_number', 'postal_address_applied', 'first_name', 'middle_name', 'last_name', 'social_security_number', 'date_of_birth', 'mobile_phone_private']
        allowed_fields_address = ['country', 'address_is_postal_address', 'street', 'house_number', 'house_number_addition', 'postal_code', 'city', 'match_city_on_postal_code']
        allowed_fields_bank = ['country_of_bank', 'iban', 'iban_check']

        required_fields = []
        allowed_fields = allowed_fields_base + allowed_fields_person + allowed_fields_address + allowed_fields_bank

        if method != 'PUT' and method != 'POST' and method != 'DELETE':
            raise ValueError('Parameter method should be PUT, POST or DELETE (in uppercase)')

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnPurchaseRelationPer'

        base_body = {
            "KnPurchaseRelationPer": {
                "Element": {
                    "Fields": {
                        "CuId": "EUR"
                    },
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": "0" if "match_person_on" not in data else data['match_person_on'],
                                },
                                "Objects": [
                                ]
                            }
                        }
                    }
                }
            }
        }

        if overload_fields is not None:
            #update the  knPurchaseRelationPer element, fields with the overload fields
            base_body['KnPurchaseRelationPer']['Element']['Fields'].update(overload_fields)

        fields_to_update = {}
        fields_to_update.update({"@CrId": data['creditor_id']}) if 'creditor_id' in data else fields_to_update
        base_body['KnPurchaseRelationPer']['Element'].update(fields_to_update)


        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update({"IsCr": data['is_creditor']}) if 'is_creditor' in data else fields_to_update
        fields_to_update.update({"IB47": data['payment_to_external']}) if 'payment_to_external' in data else fields_to_update
        fields_to_update.update({"Iban": data['preferred_iban']}) if 'preferred_iban' in data else fields_to_update
        fields_to_update.update({"Rm": data['remark']}) if 'remark' in data else fields_to_update
        fields_to_update.update({"PaCd": data['payment_condition']}) if 'payment_condition' in data else fields_to_update
        fields_to_update.update({"ColA": data['collective_account']}) if 'collective_account' in data else fields_to_update
        fields_to_update.update({"InPv": data['preferred_delivery_method']}) if 'preferred_delivery_method' in data else fields_to_update
        fields_to_update.update({"AuPa": data['automatic_payment']}) if 'automatic_payment' in data else fields_to_update
        fields_to_update.update({"PaCo": data['compact']}) if 'compact' in data else fields_to_update
        fields_to_update.update({"PaSp": data['payment_specification']}) if 'payment_specification' in data else fields_to_update
        fields_to_update.update({"InPv": data['preferred_provisioning']}) if 'preferred_provisioning' in data else fields_to_update

        fields_to_update.update(overload_fields) if overload_fields is not None else ''
        base_body['KnPurchaseRelationPer']['Element']['Fields'].update(fields_to_update)

        # Update the request body with update fields from the person fields
        fields_to_update = {}
        fields_to_update.update({"BcId": data['internal_id']}) if 'internal_id' in data else fields_to_update
        fields_to_update.update({"BcCo": data['person_id']}) if 'person_id' in data else fields_to_update
        fields_to_update.update({"SpNm": data['log_birthname_seperately']}) if 'log_birthname_seperately' in data else fields_to_update
        fields_to_update.update({"PadAdr": data['postal_address_applied']}) if 'postal_address_applied' in data else fields_to_update
        fields_to_update.update({"AutoNum": data['auto_number']}) if 'auto_number' in data else fields_to_update
        fields_to_update.update({"LaNm": data['last_name']}) if 'last_name' in data else fields_to_update
        fields_to_update.update({"FiNm": data['first_name']}) if 'first_name' in data else fields_to_update
        fields_to_update.update({"Is": data['middle_name']}) if 'middle_name' in data else fields_to_update
        fields_to_update.update({"ViGe": data['gender']}) if 'gender' in data else fields_to_update
        fields_to_update.update({"TtId": data['salutation']}) if 'salutation' in data else fields_to_update
        fields_to_update.update({"Corr": data['correspondence']}) if 'correspondence' in data else fields_to_update
        fields_to_update.update({"EmAd": data['email']}) if 'email' in data else fields_to_update
        fields_to_update.update({"EmA2": data['email_private']}) if 'email_private' in data else fields_to_update
        fields_to_update.update({"MbNr": data['mobile_phone']}) if 'mobile_phone' in data else fields_to_update
        fields_to_update.update({"MbN2": data['mobile_phone_private']}) if 'mobile_phone_private' in data else fields_to_update
        fields_to_update.update({"SoSe": data['social_security_number']}) if 'social_security_number' in data else fields_to_update
        fields_to_update.update({"DaBi": data['date_of_birth']}) if 'date_of_birth' in data else fields_to_update
        fields_to_update.update({"AddToPortal": data['outsite_access']}) if 'outsite_access' in data else fields_to_update
        fields_to_update.update({"EmailPortal": data['outsite_email']}) if 'outsite_email' in data else fields_to_update
        fields_to_update.update(overload_fields) if overload_fields is not None else ''
        base_body['KnPurchaseRelationPer']['Element']['Objects']['KnPerson']['Element']['Fields'].update(fields_to_update)

        # Update Address fields if they are in the data
        fields_to_update = {}
        fields_to_update.update({"CoId": data['country']}) if 'country' in data else fields_to_update
        fields_to_update.update({"PbAd": data['address_is_postal_address']}) if 'address_is_postal_address' in data else fields_to_update
        fields_to_update.update({"Ad": data['street']}) if 'street' in data else fields_to_update
        fields_to_update.update({"HmNr": data['house_number']}) if 'house_number' in data else fields_to_update
        fields_to_update.update({"HmAd": data['house_number_addition']}) if 'house_number_addition' in data else fields_to_update
        fields_to_update.update({"ZpCd": data['postal_code']}) if 'postal_code' in data else fields_to_update
        fields_to_update.update({"Rs": data['city']}) if 'city' in data else fields_to_update
        fields_to_update.update({"ResZip": data['match_city_on_postal_code']}) if 'match_city_on_postal_code' in data else fields_to_update
        if len(fields_to_update) > 0:
            new_address = {"KnBasicAddressAdr": {"Element": {"Fields": fields_to_update}}}
            base_body['KnPurchaseRelationPer']['Element']['Objects']['KnPerson']['Element']['Objects'].append(new_address)

        # Update Address fields if they are in the data
        fields_to_update = {}
        fields_to_update.update({"CoId": data['country_of_bank']}) if 'country_of_bank' in data else fields_to_update
        fields_to_update.update({"IbCk": data['iban_check']}) if 'iban_check' in data else fields_to_update
        fields_to_update.update({"Iban": data['iban']}) if 'iban' in data else fields_to_update
        if len(fields_to_update) > 0:
            new_bank = {"KnBankAccount": {"Element": {"Fields": fields_to_update}}}
            base_body['KnPurchaseRelationPer']['Element']['Objects']['KnPerson']['Element']['Objects'].append(new_bank)

        if self.debug:
            print(json.dumps(base_body))

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_project(self, data: dict, method: str, overload_fields: dict = None) -> requests.Response:
        """
        This method creates a new project in AFAS.
        method should be POST or PUT
        """
        required_fields = ['project_id', 'project_group', 'description', 'employee_id', 'creation_date', 'project_start_date', 'debtor_id']
        allowed_fields = []
        self.__check_fields(data, required_fields, allowed_fields)

        if method not in ['POST', 'PUT']:
            raise ValueError('Method should be POST or PUT')

        # Define the basic structure of the payload
        payload = {
            "PtProject": {
                "Element": {
                    "Fields": {
                        "PrId": data['project_id'],
                        "PrGp": data['project_group'],
                        "Ds": data['description'],
                        "EmId": data['employee_id'],
                        "DtAn": data['creation_date'],
                        "DaSt": data['project_start_date'],
                        "DbId": data['debtor_id']
                    },
                    "Objects": [
                        {
                            "KnBasicAddressAdr": {
                                "Element": data.get('KnBasicAddressAdr', [])
                            }
                        }
                    ]
                }
            }
        }

        # Update with any additional fields provided via overload_fields
        if overload_fields:
            payload['PtProject']['Element']['Fields'].update(overload_fields)

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/PtProject"

        response = requests.request(method, url, data=json.dumps(payload), headers=self.headers)

        return response

    def update_employee(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: status code for request and optional error message
        """
        allowed_fields = ['employee_id', 'city_of_birth']
        required_fields = ['employee_id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee')

        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Fields": {
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"LwRs": data['city_of_birth']}) if 'city_of_birth' in data else fields_to_update

        # This is to include custom fields
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_address(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: status code for request and optional error message
        """
        allowed_fields = ['street_number_add', 'city', 'match_employees_on', 'ssn', 'find_address_based_on_postal_code']
        required_fields = ['employee_id', 'person_id', 'country', 'street', 'street_number', 'postal_code', 'startdate']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/KnPerson')

        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": "1" if "match_employees_on" not in data else data['match_employees_on'],
                                    "BcCo": data['person_id']
                                },
                                "Objects": {
                                    "KnBasicAddressAdr": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],
                                                "PbAd": False,
                                                "Ad": data['street'],
                                                "HmNr": data['street_number'],
                                                "BcCo": data['employee_id'],
                                                "ZpCd": data['postal_code'],
                                                "ResZip": data['search_address_by_postal_code'] if 'search_address_by_postal_code' in data.keys() else True,
                                                "BeginDate": data['startdate']
                                            }
                                        }
                                    },
                                    "KnBasicAddressPad": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],
                                                "PbAd": False,
                                                "Ad": data['street'],
                                                "HmNr": data['street_number'],
                                                "BcCo": data['employee_id'],
                                                "ZpCd": data['postal_code'],
                                                "ResZip": data['search_address_by_postal_code'] if 'search_address_by_postal_code' in data.keys() else True,
                                                "BeginDate": data['startdate']
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"HmAd": data['street_number_add']}) if 'street_number_add' in data else fields_to_update
        fields_to_update.update({"Rs": data['city']}) if 'city' in data else fields_to_update

        # This is to include custom fields
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Objects']['KnBasicAddressAdr']['Element']['Fields'].update(fields_to_update)
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Objects']['KnBasicAddressPad']['Element']['Fields'].update(fields_to_update)
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Fields'].update({"SoSe": data['ssn']}) if 'ssn' in data else None

        if self.debug:
            print(json.dumps(base_body))

        update = requests.request("POST", url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_person_address(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        Updates a person's address in AFAS via the KnPerson connector.
        This method can be used when you only have a Person (KnPerson) record
        and there is no Employee (KnEmployee) relationship.

        Required fields:
          - person_id
          - country        (CoId)
          - street         (Ad)
          - housenumber    (HmNr)
          - postalcode     (ZpCd)
          - city           (Rs)

        Allowed fields (mapped to KnBasicAddressAdr/Pad if present):
          - housenumber_addition -> HmAd
          - startdate            -> BeginDate (defaults to today's date if omitted)
          - reszip               -> ResZip (defaults to False if omitted)
          - pb_address           -> PbAd (defaults to False if omitted)
          - match_person_on      -> MatchPer (defaults to "0" for matching by person_id)

        :param data: Dictionary of fields to update.
        :param overload_fields: Optional dict of custom fields for the address objects.
                               For example, {'DFEDS8-DSF9uD-DDSA': 'Vrij veld'}.
        :return: requests.Response object with status code / text from AFAS.
        """
        # You can adjust / expand these fields as you like
        required_fields = ["person_id", "country", "street", "housenumber", "postalcode", "city"]
        allowed_fields = [
            "housenumber_addition",
            "startdate",
            "reszip",
            "pb_address",
            "match_person_on"
        ]

        # Validate fields
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        # Determine MatchPer (defaults to '0' => match person by person_id)
        match_person_value = data.get("match_person_on", "0")

        # Determine BeginDate (defaults to today's date if none supplied)
        from datetime import datetime
        begin_date = data.get("startdate", datetime.now().strftime('%Y-%m-%d'))

        # Construct the base request body
        base_body = {
            "KnPerson": {
                "Element": {
                    "Fields": {
                        "MatchPer": match_person_value,  # Match existing person
                        "BcCo": data["person_id"]  # Person ID
                    },
                    "Objects": [
                        {
                            "KnBasicAddressAdr": {
                                "Element": {
                                    "Fields": {
                                        "CoId": data["country"],  # Country
                                        "Ad": data["street"],  # Street
                                        "HmNr": data["housenumber"],  # House number
                                        "ZpCd": data["postalcode"],  # Postal code
                                        "Rs": data["city"],  # City
                                        "PbAd": data.get("pb_address", False),
                                        "ResZip": data.get("reszip", False),
                                        "BeginDate": begin_date
                                    }
                                }
                            },
                            "KnBasicAddressPad": {
                                "Element": {
                                    "Fields": {
                                        "CoId": data["country"],
                                        "Ad": data["street"],
                                        "HmNr": data["housenumber"],
                                        "ZpCd": data["postalcode"],
                                        "Rs": data["city"],
                                        "PbAd": data.get("pb_address", False),
                                        "ResZip": data.get("reszip", False),
                                        "BeginDate": begin_date
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }

        # If there's a house number addition, set that in both address blocks
        if "housenumber_addition" in data:
            base_body["KnPerson"]["Element"]["Objects"][0]["KnBasicAddressAdr"]["Element"]["Fields"]["HmAd"] = data[
                "housenumber_addition"]
            base_body["KnPerson"]["Element"]["Objects"][0]["KnBasicAddressPad"]["Element"]["Fields"]["HmAd"] = data[
                "housenumber_addition"]

        # Merge any custom overload fields (applied to the address blocks)
        if overload_fields:
            # Example: If you want to apply them to BOTH KnBasicAddressAdr + KnBasicAddressPad:
            base_body["KnPerson"]["Element"]["Objects"][0]["KnBasicAddressAdr"]["Element"]["Fields"].update(
                overload_fields)
            base_body["KnPerson"]["Element"]["Objects"][0]["KnBasicAddressPad"]["Element"]["Fields"].update(
                overload_fields)

        # Send the request to AFAS
        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnPerson"
        response = requests.request("POST", url, data=json.dumps(base_body), headers=self.headers)

        return response

    def update_contract(self, data: dict, overload_fields: dict = None, method: str = 'POST') -> requests.Response:
        """
        :param data: Dictionary of fields that you want to update in AFAS. Only fields listed in allowed arrays are accepted. Fields listed in required fields array, are mandatory
        :param overload_fields: Dictionary of dictionaries. Specify sub dictionaries for each section you want to update.
        Specify as key which element you want to update, available options are: schedule, salary, contract, function.
        Example: overload_fields = {"employee": {"field": value}}
        :param method: request type
        :return: status code for request and optional error message
        """

        # Contract fields
        required_fields_contract = ['employee_id', 'startdate_contract']
        allowed_fields_contract = ['employee_id', 'type_of_employment', 'enddate_contract', 'termination_reason', 'termination_initiative', 'probation_period',
                                   'probation_enddate', 'cao', 'terms_of_employment', 'type_of_contract', 'employer_number', 'type_of_employee', 'employment',
                                   'seniority_date', 'contract_chain_code', 'start_date_contract_chain', 'date_in_service_original', 'number_income_ratio',
                                   'written_contract', 'employment_number']

        # Function fields
        required_fields_function = ['organizational_unit', 'function_id', 'costcenter_id']
        allowed_fields_function = ['costcarrier_id']

        # Timetable fields
        if 'standard_schedule' in data:
            required_fields_timetable = ['standard_schedule']
            allowed_fields_timetable  = []
        else:
            required_fields_timetable = ['weekly_hours', 'parttime_percentage']
            allowed_fields_timetable = ['changing_work_pattern', 'days_per_week', 'fte', 'on-call_contract', 'on_call_agreement', 'type_of_schedule']

        # Workschedule fields (Optional: if one field is given, all fields are required)
        fields_workschedule = ['startdate_workcycle', 'workcycle', 'start_week', 'index_number']

        # Salary fields
        required_fields_salary = ['type_of_salary', 'period_table']
        allowed_fields_salary = ['step', 'function_scale_type', 'salary_scale_type', 'function_scale', 'salary_scale', 'salary_year', 'net_salary', 'apply_timetable', 'salary_amount']

        # Tax Agency fields
        fields_tax_authority = ['tax_authority_code', 'income_relationship_type', 'nature_of_employment', 'table_colour', 'table_code', 'payroll_tax_credit',
                                'zvw', 'zvw_code', 'vw', 'ww', 'wia', 'risk_group_sector', 'risk_group_sector_diff', 'cbs_cla', 'cbs_cla_diff', 'on_call_with', 'apply_day_table']

        if method == 'POST':
            allowed_fields = allowed_fields_contract + allowed_fields_salary + allowed_fields_timetable + allowed_fields_function
            required_fields = required_fields_contract + required_fields_function + required_fields_timetable + required_fields_salary
        elif method == 'PUT':
            allowed_fields = allowed_fields_contract + required_fields_function + required_fields_timetable + required_fields_salary + allowed_fields_salary + allowed_fields_timetable + allowed_fields_function
            required_fields = required_fields_contract
        else:
            raise ValueError(f'Method {method} not supported, only POST and PUT are supported')

        # Check if there are fields that are not allowed or fields missing that are required
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasContract')

        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasContract": {
                            "Element": {
                                "@DaBe": data['startdate_contract'],
                                "Fields": {
                                }
                            }
                        }
                    }
                }
            }
        }

        # Extra JSON objects which are optional at contract creation
        function_dict = {
            "AfasOrgunitFunction": {
                "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                    }
                }
            }
        }

        timetable = {
            "AfasTimeTable": {
                "Element": {
                    "@DaBg": data['startdate_contract'],
                    "Fields": {
                        "StPa": True
                    }
                }
            }
        }

        salary = {
            "AfasSalary": {
                "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                    }
                }
            }
        }

        # If one of the optional fields of a subelement is included, we need to merge the whole JSON object to the basebody
        if any(field in data.keys() for field in allowed_fields_function + required_fields_function):
            for field in required_fields_function:
                if field not in data.keys():
                    raise KeyError('Field {field} is required. Required fields for function are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

            fields_to_update = {}
            fields_to_update.update({"DpId": data['organizational_unit']}) if 'organizational_unit' in data else fields_to_update
            fields_to_update.update({"FuId": data['function_id']}) if 'function_id' in data else fields_to_update
            fields_to_update.update({"CrId": data['costcenter_id']}) if 'costcenter_id' in data else fields_to_update
            fields_to_update.update({"CcId": data['costcarrier_id']}) if 'costcarrier_id' in data else fields_to_update
            # add overload function fields to the body
            if overload_fields is not None and 'function' in overload_fields.keys():
                fields_to_update.update(overload_fields['function'])

            # merge subelement with basebody
            function_dict['AfasOrgunitFunction']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(function_dict)

        if any(field in data.keys() for field in allowed_fields_timetable + required_fields_timetable):
            for field in required_fields_timetable:
                if field not in data.keys():
                    raise KeyError('Field {field} is required. Required fields for timetable are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

            fields_to_update = {}
            fields_to_update.update({"StPa": data['changing_work_pattern']}) if 'changing_work_pattern' in data else fields_to_update
            fields_to_update.update({"HrWk": data['weekly_hours']}) if 'weekly_hours' in data else fields_to_update
            fields_to_update.update({"PcPt": data['parttime_percentage']}) if 'parttime_percentage' in data else fields_to_update
            fields_to_update.update({"DyWk": data['days_per_week']}) if 'days_per_week' in data else fields_to_update
            fields_to_update.update({"Ft": data['fte']}) if 'fte' in data else fields_to_update
            fields_to_update.update({"ClAg": data['on-call_contract']}) if 'on-call_contract' in data else fields_to_update
            fields_to_update.update({"ClAg": data['on_call_agreement']}) if 'on_call_agreement' in data else fields_to_update
            fields_to_update.update({"EtTy": data['type_of_schedule']}) if 'type_of_schedule' in data else fields_to_update
            fields_to_update.update({"SeNo": data['standard_schedule']}) if 'standard_schedule' in data else fields_to_update
            # add overload schedule fields to the body
            if overload_fields is not None and 'schedule' in overload_fields.keys():
                fields_to_update.update(overload_fields['schedule'])

            timetable['AfasTimeTable']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(timetable)

        if any(field in data.keys() for field in fields_workschedule):
            for field in fields_workschedule:
                if field not in data.keys():
                    raise KeyError('Field {field} is required. Required fields for workschedules are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

            workschedule = {
                "Objects": [
                    {
                        "AfasWorkTime": {
                            "Element": {
                                "@DaBe": data['startdate_workcycle'],
                                "Fields": {
                                    "Twcy": data['workcycle'],
                                    "Twcp": data['start_week'],
                                    "Twcc": data['index_number']
                                }
                            }
                        }
                    }
                ]
            }
            base_body['AfasEmployee']['Element']['Objects']['AfasTimeTable']['Element'].update(workschedule)

        if any(field in data.keys() for field in allowed_fields_salary + required_fields_salary):
            for field in required_fields_salary:
                if field not in data.keys():
                    raise KeyError('Field {field} is required. Required fields for salaries are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

            fields_to_update = {}
            fields_to_update.update({"SaSt": data['step']}) if 'step' in data else fields_to_update
            fields_to_update.update({"SaPe": data['type_of_salary']}) if 'type_of_salary' in data else fields_to_update
            fields_to_update.update({"EmSa": data['salary_amount']}) if 'salary_amount' in data else fields_to_update
            fields_to_update.update({"PtId": data['period_table']}) if 'period_table' in data else fields_to_update
            fields_to_update.update({"VaSc": data['salary_scale']}) if 'salary_scale' in data else fields_to_update
            fields_to_update.update({"TaId": data['salary_scale_type']}) if 'salary_scale_type' in data else fields_to_update
            fields_to_update.update({"FuSc": data['function_scale']}) if 'function_scale' in data else fields_to_update
            fields_to_update.update({"FuTa": data['function_scale_type']}) if 'function_scale_type' in data else fields_to_update
            fields_to_update.update({"SaYe": data['salary_year']}) if 'salary_year' in data else fields_to_update
            fields_to_update.update({"NtSa": data['net_salary']}) if 'net_salary' in data else fields_to_update
            fields_to_update.update({"TtPy": data['apply_timetable']}) if 'apply_timetable' in data else fields_to_update
            # add overload salary fields to the body
            if overload_fields is not None and 'salary' in overload_fields.keys():
                fields_to_update.update(overload_fields['salary'])

            salary['AfasSalary']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(salary)

        # Update the tax agency
        fields_to_update = {}
        fields_to_update.update({"DaEn": data['enddate_contract']}) if 'enddate_contract' in data else fields_to_update
        fields_to_update.update({"PEmTy": data['type_of_employment']}) if 'type_of_employment' in data else fields_to_update
        fields_to_update.update({"ViIe": data['termination_initiative']}) if 'termination_initiative' in data else fields_to_update
        fields_to_update.update({"ViRe": data['termination_reason']}) if 'termination_reason' in data else fields_to_update
        fields_to_update.update({"ViTo": data['probation_period']}) if 'probation_period' in data else fields_to_update
        fields_to_update.update({"DaEt": data['probation_enddate']}) if 'probation_enddate' in data else fields_to_update
        fields_to_update.update({"WrCt": data['written_contract']}) if 'written_contract' in data else fields_to_update
        fields_to_update.update({"ClId": data['cao']}) if 'cao' in data else fields_to_update
        fields_to_update.update({"WcId": data['terms_of_employment']}) if 'terms_of_employment' in data else fields_to_update
        fields_to_update.update({"ApCo": data['type_of_contract']}) if 'type_of_contract' in data else fields_to_update
        fields_to_update.update({"CmId": data['employer_number']}) if 'employer_number' in data else fields_to_update
        fields_to_update.update({"EmMt": data['type_of_employee']}) if 'type_of_employee' in data else fields_to_update
        fields_to_update.update({"DvSn": data['employment_number']}) if 'employment_number' in data else fields_to_update
        fields_to_update.update({"ViEt": data['employment']}) if 'employment' in data else fields_to_update
        fields_to_update.update({"StAc": data['seniority_date']}) if 'seniority_date' in data else fields_to_update
        fields_to_update.update({"DaSc": data['start_date_contract_chain']}) if 'start_date_contract_chain' in data else fields_to_update
        fields_to_update.update({"ViKe": data['contract_chain_code']}) if 'contract_chain_code' in data else fields_to_update
        fields_to_update.update({"DbYs": data['date_in_service_original']}) if 'date_in_service_original' in data else fields_to_update
        fields_to_update.update({"EnS2": data['number_income_ratio']}) if 'number_income_ratio' in data else fields_to_update
        # add overload contract fields to the body
        if overload_fields is not None and 'contract' in overload_fields.keys():
            fields_to_update.update(overload_fields['contract'])

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasContract']['Element']['Fields'].update(fields_to_update)

        if self.debug:
            print(json.dumps(base_body))

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_contract_only(self, data: dict, overload_fields: dict = None, method: str = 'POST'):
        """
        :param data: Dictionary of fields that you want to update in AFAS. Only fields listed in allowed arrays are accepted. Fields listed in required fields array, are mandatory
        :param overload_fields: Dictionary of dictionaries. Specify sub dictionaries for each section you want to update.
        Specify as key which element you want to update, available options are: schedule, salary, contract, function.
        Example: overload_fields = {"employee": {"field": value}}
        :param method: request type
        """
        # Contract fields
        required_fields = ['employee_id', 'startdate_contract']
        allowed_fields = ['employee_id', 'type_of_employment', 'enddate_contract', 'termination_reason', 'termination_initiative', 'probation_period',
                          'probation_enddate', 'cao', 'terms_of_employment', 'type_of_contract', 'employer_number', 'type_of_employee', 'employment', 'employment_number',
                          'seniority_date', 'contract_chain_code', 'start_date_contract_chain', 'date_in_service_original', 'number_income_ratio']

        if method != 'POST' and method != 'PUT':
            raise ValueError(f'Method {method} not supported, only POST and PUT are supported')

        # Check if there are fields that are not allowed or fields missing that are required
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasContract')

        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasContract": {
                            "Element": {
                                "@DaBe": data['startdate_contract'],
                                "Fields": {
                                }
                            }
                        }
                    }
                }
            }
        }

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update({"DaEn": data['enddate_contract']}) if 'enddate_contract' in data else fields_to_update
        fields_to_update.update({"PEmTy": data['type_of_employment']}) if 'type_of_employment' in data else fields_to_update
        fields_to_update.update({"ViIe": data['termination_initiative']}) if 'termination_initiative' in data else fields_to_update
        fields_to_update.update({"ViRe": data['termination_reason']}) if 'termination_reason' in data else fields_to_update
        fields_to_update.update({"ViTo": data['probation_period']}) if 'probation_period' in data else fields_to_update
        fields_to_update.update({"DaEt": data['probation_enddate']}) if 'probation_enddate' in data else fields_to_update
        fields_to_update.update({"ClId": data['cao']}) if 'cao' in data else fields_to_update
        fields_to_update.update({"WcId": data['terms_of_employment']}) if 'terms_of_employment' in data else fields_to_update
        fields_to_update.update({"ApCo": data['type_of_contract']}) if 'type_of_contract' in data else fields_to_update
        fields_to_update.update({"CmId": data['employer_number']}) if 'employer_number' in data else fields_to_update
        fields_to_update.update({"EmMt": data['type_of_employee']}) if 'type_of_employee' in data else fields_to_update
        fields_to_update.update({"ViEt": data['employment']}) if 'employment' in data else fields_to_update
        fields_to_update.update({"DvSn": data['employment_number']}) if 'employment_number' in data else fields_to_update
        fields_to_update.update({"StAc": data['seniority_date']}) if 'seniority_date' in data else fields_to_update
        fields_to_update.update({"DaSc": data['start_date_contract_chain']}) if 'start_date_contract_chain' in data else fields_to_update
        fields_to_update.update({"ViKe": data['contract_chain_code']}) if 'contract_chain_code' in data else fields_to_update
        fields_to_update.update({"DbYs": data['date_in_service_original']}) if 'date_in_service_original' in data else fields_to_update
        fields_to_update.update({"EnS2": data['number_income_ratio']}) if 'number_income_ratio' in data else fields_to_update
        # add overload contract fields to the body
        if overload_fields is not None and 'contract' in overload_fields.keys():
            fields_to_update.update(overload_fields['contract'])

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasContract']['Element']['Fields'].update(fields_to_update)

        # Add tax authority data
        fields_to_update_tax_authority_base = {}
        fields_to_update_tax_authority_base.update({"@DaBe": data['date_effective']}) if 'tax_authority_code' in data else fields_to_update_tax_authority_base
        fields_to_update_tax_authority_base.update({"@AyId": data['tax_authority_code']}) if 'tax_authority_code' in data else fields_to_update_tax_authority_base

        fields_to_update_tax_authority = {}
        fields_to_update_tax_authority.update({"ViIn": data['income_relationship_type']}) if 'income_relationship_type' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViEm": data['nature_of_employment']}) if 'nature_of_employment' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViTs": data['table_colour']}) if 'table_colour' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViCd": data['table_code']}) if 'table_code' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViLk": data['payroll_tax_credit']}) if 'payroll_tax_credit' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"YnZW": data['zw']}) if 'zw' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"YnWW": data['ww']}) if 'ww' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"YWAO": data['wia']}) if 'wia' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViRi": data['risk_group_sector_diff']}) if 'risk_group_sector_diff' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViFc": data['cbs_cla_diff']}) if 'cbs_cla_diff' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"TxGn": data['on_call_with']}) if 'on_call_with' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"TyDt": data['apply_day_table']}) if 'apply_day_table' in data else fields_to_update_tax_authority

        if len(fields_to_update_tax_authority) > 0:
            # see https://help.afas.nl/meldingen/NL/SE/124356.htm for this ridiculous logic and when you find this, curse AFAS that they did not map this automatically like they do in the UI
            fiscal_year = datetime.strptime(data["date_effective"], '%Y-%m-%d').year
            if 'zvw_code' in data:
                zvw_code = data['zvw_code']
            else:
                if fiscal_year < 2006:
                    zvw_code = "C"
                elif fiscal_year < 2013:
                    zvw_code = "CEF"
                else:
                    zvw_code = "K"
            body['AfasEmployee']['Element']['Objects']['AfasAgencyFiscus']['Element'].update(fields_to_update_tax_authority_base)
            body['AfasEmployee']['Element']['Objects']['AfasAgencyFiscus']['Element']['Fields'].update(fields_to_update_tax_authority)
            body['AfasEmployee']['Element']['Objects']['AfasAgencyFiscus']['Element']['Fields'].update({"ViZv": zvw_code})


        if self.debug:
            print(json.dumps(base_body))

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_contract_with_rehire(self, data: dict, overload_fields: dict = None, method='POST') -> requests.Response:
        """
        :param data: Dictionary of fields that you want to update in AFAS. Only fields listed in allowed arrays are accepted. Fields listed in required fields array, are mandatory
        :param overload_fields: Dictionary of dictionaries. Specify sub dictionaries for each section you want to update.
        Specify as key which element you want to update, available options are: schedule, salary, contract, function.
        Example: overload_fields = {"employee": {"field": value}}
        :param method: request type
        :return: status code for request and optional error message
        """

        # Contract fields
        required_fields_contract = ['employee_id', 'startdate_contract']
        allowed_fields_contract = ['employee_id', 'type_of_employment', 'enddate_contract', 'termination_reason', 'termination_initiative', 'probation_period',
                                   'probation_enddate', 'cao', 'terms_of_employment', 'type_of_contract', 'employer_number', 'type_of_employee', 'employment'
                                                                                                                                                 'seniority_date', 'contract_chain_code', 'start_date_contract_chain', 'number_income_ratio']

        # Function fields
        required_fields_function = ['organizational_unit', 'function_id', 'costcenter_id']
        allowed_fields_function = ['costcarrier_id']

        # Timetable fields
        required_fields_timetable = ['weekly_hours', 'parttime_percentage']
        allowed_fields_timetable = ['changing_work_pattern', 'days_per_week', 'fte', 'on-call_contract', 'type_of_schedule']

        # Workschedule fields (Optional: If one field is given, all 4 are required)
        fields_workschedule = ['startdate_workcycle', 'workcycle', 'start_week', 'index_number']

        # Salary fields
        required_fields_salary = ['type_of_salary', 'period_table']
        allowed_fields_salary = ['step', 'function_scale', 'salary_scale', 'salary_year', 'net_salary', 'apply_timetable', 'salary_amount', 'function_scale_type', 'salary_scale_type']

        allowed_fields = allowed_fields_contract + allowed_fields_salary + allowed_fields_timetable + allowed_fields_function
        required_fields = required_fields_contract + required_fields_function + required_fields_timetable + required_fields_salary

        # Check if there are fields that are not allowed or fields missing that are required
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasContract')

        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Fields": {
                        "Bl": False if 'employee_blocked' not in data else data['employee_blocked']
                    },
                    "Objects": {
                        "AfasContract": {
                            "Element": {
                                "@DaBe": data['startdate_contract'],
                                "Fields": {
                                }
                            }
                        }
                    }
                }
            }
        }

        # Extra JSON objects which are optional at contract creation
        function_dict = {
            "AfasOrgunitFunction": {
                "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                    }
                }
            }
        }

        timetable = {
            "AfasTimeTable": {
                "Element": {
                    "@DaBg": data['startdate_contract'],
                    "Fields": {
                        "StPa": True
                    }
                }
            }
        }

        salary = {
            "AfasSalary": {
                "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                    }
                }
            }
        }

        # If one of the optional fields of a subelement is included, we need to merge the whole JSON object to the basebody
        if any(field in data.keys() for field in allowed_fields_function):
            for field in required_fields_function:
                if field not in data.keys():
                    raise KeyError('Field {field} is required. Required fields for function are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

            fields_to_update = {}
            fields_to_update.update({"DpId": data['organizational_unit']}) if 'organizational_unit' in data else fields_to_update
            fields_to_update.update({"FuId": data['function_id']}) if 'function_id' in data else fields_to_update
            fields_to_update.update({"CrId": data['costcenter_id']}) if 'costcenter_id' in data else fields_to_update
            fields_to_update.update({"CcId": data['costcarrier_id']}) if 'costcarrier_id' in data else fields_to_update
            # add overload function fields to the body
            if overload_fields is not None and 'function' in overload_fields.keys():
                fields_to_update.update(overload_fields['function'])

            # merge subelement with basebody
            function_dict['AfasOrgunitFunction']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(function_dict)

        if any(field in data.keys() for field in allowed_fields_timetable):
            for field in required_fields_timetable:
                if field not in data.keys():
                    raise KeyError('Field {field} is required. Required fields for timetable are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

            fields_to_update = {}
            fields_to_update.update({"StPa": data['changing_work_pattern']}) if 'changing_work_pattern' in data else fields_to_update
            fields_to_update.update({"HrWk": data['weekly_hours']}) if 'weekly_hours' in data else fields_to_update
            fields_to_update.update({"PcPt": data['parttime_percentage']}) if 'parttime_percentage' in data else fields_to_update
            fields_to_update.update({"DyWk": data['days_per_week']}) if 'days_per_week' in data else fields_to_update
            fields_to_update.update({"Ft": data['fte']}) if 'fte' in data else fields_to_update
            fields_to_update.update({"ClAg": data['on-call_contract']}) if 'on-call_contract' in data else fields_to_update
            fields_to_update.update({"EtTy": data['type_of_schedule']}) if 'type_of_schedule' in data else fields_to_update
            # add overload schedule fields to the body
            if overload_fields is not None and 'schedule' in overload_fields.keys():
                fields_to_update.update(overload_fields['schedule'])

            timetable['AfasTimeTable']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(timetable)

        if any(field in data.keys() for field in fields_workschedule):
            for field in fields_workschedule:
                if field not in data.keys():
                    raise KeyError('Field {field} is required. Required fields for workschedule are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

            workschedule = {
                "Objects": [
                    {
                        "AfasWorkTime": {
                            "Element": {
                                "@DaBe": data['startdate_workcycle'],
                                "Fields": {
                                    "Twcy": data['workcycle'],
                                    "Twcp": data['start_week'],
                                    "Twcc": data['index_number']
                                }
                            }
                        }
                    }
                ]
            }
            base_body['AfasEmployee']['Element']['Objects']['AfasTimeTable']['Element'].update(workschedule)

        if any(field in data.keys() for field in allowed_fields_salary):
            for field in required_fields_salary:
                if field not in data.keys():
                    raise KeyError('Field {field} is required. Required fields for salaries are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

            fields_to_update = {}
            fields_to_update.update({"SaSt": data['step']}) if 'step' in data else fields_to_update
            fields_to_update.update({"SaPe": data['type_of_salary']}) if 'type_of_salary' in data else fields_to_update
            fields_to_update.update({"EmSa": data['salary_amount']}) if 'salary_amount' in data else fields_to_update
            fields_to_update.update({"PtId": data['period_table']}) if 'period_table' in data else fields_to_update
            fields_to_update.update({"VaSc": data['salary_scale']}) if 'salary_scale' in data else fields_to_update
            fields_to_update.update({"TaId": data['salary_scale_type']}) if 'salary_scale_type' in data else fields_to_update
            fields_to_update.update({"FuSc": data['function_scale']}) if 'function_scale' in data else fields_to_update
            fields_to_update.update({"FuTa": data['function_scale_type']}) if 'function_scale_type' in data else fields_to_update
            fields_to_update.update({"SaYe": data['salary_year']}) if 'salary_year' in data else fields_to_update
            fields_to_update.update({"NtSa": data['net_salary']}) if 'net_salary' in data else fields_to_update
            fields_to_update.update({"TtPy": data['apply_timetable']}) if 'apply_timetable' in data else fields_to_update
            # add overload salary fields to the body
            if overload_fields is not None and 'salary' in overload_fields.keys():
                fields_to_update.update(overload_fields['salary'])

            salary['AfasSalary']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(salary)

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update({"DaEn": data['enddate_contract']}) if 'enddate_contract' in data else fields_to_update
        fields_to_update.update({"PEmTy": data['type_of_employment']}) if 'type_of_employment' in data else fields_to_update
        fields_to_update.update({"ViIe": data['termination_initiative']}) if 'termination_initiative' in data else fields_to_update
        fields_to_update.update({"ViRe": data['termination_reason']}) if 'termination_reason' in data else fields_to_update
        fields_to_update.update({"ViTo": data['probation_period']}) if 'probation_period' in data else fields_to_update
        fields_to_update.update({"DaEt": data['probation_enddate']}) if 'probation_enddate' in data else fields_to_update
        fields_to_update.update({"ClId": data['cao']}) if 'cao' in data else fields_to_update
        fields_to_update.update({"WcId": data['terms_of_employment']}) if 'terms_of_employment' in data else fields_to_update
        fields_to_update.update({"ApCo": data['type_of_contract']}) if 'type_of_contract' in data else fields_to_update
        fields_to_update.update({"CmId": data['employer_number']}) if 'employer_number' in data else fields_to_update
        fields_to_update.update({"EmMt": data['type_of_employee']}) if 'type_of_employee' in data else fields_to_update
        fields_to_update.update({"ViEt": data['employment']}) if 'employment' in data else fields_to_update
        fields_to_update.update({"StAc": data['seniority_date']}) if 'seniority_date' in data else fields_to_update
        fields_to_update.update({"DaSc": data['start_date_contract_chain']}) if 'start_date_contract_chain' in data else fields_to_update
        fields_to_update.update({"ViKe": data['contract_chain_code']}) if 'contract_chain_code' in data else fields_to_update
        fields_to_update.update({"EnS2": data['number_income_ratio']}) if 'number_income_ratio' in data else fields_to_update
        # add overload contract fields to the body
        if overload_fields is not None and 'contract' in overload_fields.keys():
            fields_to_update.update(overload_fields['contract'])

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasContract']['Element']['Fields'].update(fields_to_update)

        if self.debug:
            print(base_body)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_function(self, data: dict, overload_fields: dict = None, method="PUT") -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :param method: PUT or POST, depending on the case
        :return: status code for request and optional error message
        """
        required_fields = ['startdate', 'employee_id', 'organizational_unit', 'function', 'costcentre']
        allowed_fields = ['formation', 'costcarrier', 'employment_number']
        formation_fields = ['formation_number', 'formation_function', 'formation_org_unit', 'formation_cost_carrier', 'formation_cost_center', 'formation_percentage']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasOrgunitFunction')

        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasOrgunitFunction": {
                            "Element": {
                                "@DaBe": data['startdate'],
                                "Fields": {
                                    "DpId": data['organizational_unit'],
                                    "FuId": data['function'],
                                    "CrId": data['costcentre']
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        if any(field in data.keys() for field in formation_fields):
            for field in formation_fields:
                if field not in data.keys():
                    raise KeyError('Field {field} is required. Required fields for workschedules are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

            formation_division = {
                "Objects": [
                    {
                        "AfasSalaryCost": {
                            "Element": {
                                "@TdSn": data['formation_number'],
                                "Fields": {
                                    "DpId": data['formation_org_unit'],
                                    "FuId": data['formation_function'],
                                    "CcId": data['formation_cost_carrier'],
                                    "CrId": data['formation_cost_center'],
                                    "Perc": data['formation_percentage']
                                }
                            }
                        }
                    }
                ]
            }

            base_body['AfasEmployee']['Element']['Objects']['AfasOrgunitFunction']['Element'].update(formation_division)

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"FpId": data['formation']}) if 'formation' in data else fields_to_update
        fields_to_update.update({"CcId": data['costcarrier']}) if 'costcarrier' in data else fields_to_update
        fields_to_update.update({"DvSn": data['employment_number']}) if 'employment_number' in data else fields_to_update

        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasOrgunitFunction']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_salary(self, data: dict, overload_fields: dict = None, method='PUT') -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :param method: PUT or POST, depending on the case
        :return: status code for request and optional error message
        """
        allowed_fields = ['step', 'final_step', 'period_table', 'salary_year', 'function_scale', 'function_scale_type', 'salary_scale',
                          'salary_scale_type', 'salary_amount', 'net_salary', 'apply_timetable', 'employment_number', 'allowance', 'rsp']
        required_fields = ['startdate', 'employee_id', 'salary_type']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasSalary')

        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasSalary": {
                            "Element": {
                                "@DaBe": data['startdate'],
                                "Fields": {
                                    "SaPe": data['salary_type']
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"EmSa": data['salary_amount']}) if 'salary_amount' in data else fields_to_update
        fields_to_update.update({"SaSt": data['step']}) if 'step' in data else fields_to_update
        fields_to_update.update({"SaS2": data['final_step']}) if 'final_step' in data else fields_to_update
        fields_to_update.update({"SaYe": data['salary_year']}) if 'salary_year' in data else fields_to_update
        fields_to_update.update({"PtId": data['period_table']}) if 'period_table' in data else fields_to_update.update({"PtId": 5})
        fields_to_update.update({"VaSc": data['salary_scale']}) if 'salary_scale' in data else fields_to_update
        fields_to_update.update({"TaId": data['salary_scale_type']}) if 'salary_scale_type' in data else fields_to_update
        fields_to_update.update({"FuSc": data['function_scale']}) if 'function_scale' in data else fields_to_update
        fields_to_update.update({"FuTa": data['function_scale_type']}) if 'function_scale_type' in data else fields_to_update
        fields_to_update.update({"NtSa": data['net_salary']}) if 'net_salary' in data else fields_to_update
        fields_to_update.update({"TtPy": data['apply_timetable']}) if 'apply_timetable' in data else fields_to_update
        fields_to_update.update({"DvSn": data['employment_number']}) if 'employment_number' in data else fields_to_update
        fields_to_update.update({"EmSc": data['allowance']}) if 'allowance' in data else fields_to_update
        fields_to_update.update({"Rsp": data['rsp']}) if 'rsp' in data else fields_to_update

        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasSalary']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_subscription(self, data: dict, method: str, custom_fields: dict = None, custom_fields_lines: dict = None) -> requests.Response:
        """
        Update the subscriptions in AFAS Profit
        :param data: data to update. This is a dictionary with the subscription_id as key and the data to update as value
        :param method: method to use (POST or PUT). POST is used to create a new subscription, PUT is used to update an existing subscription
        :param custom_fields: custom fields to update. Give the key and the value of the field. For example: {'DFEDS8-DSF9uD-DDSA': 'value'}
        :param custom_fields_lines: custom fields to update for the subscription lines. Give the key and the value of the field. For example: {'DFEDS8-DSF9uD-DDSA': 'value'}
        :return: the response from AFAS Profit
        """
        required_fields = ['subscription_id']
        allowed_fields = ['start_date_subscription', 'end_date_subscription', 'item_type_id', 'item_code', 'amount', 'subscription_line_id', 'invoice_cycle',
                          'price', 'start_date_subscription_line', 'end_date_subscription_line', 'reason_of_termination']

        # Check if the fields in data exists in the required or allowed fields
        self.__check_fields(data, required_fields, allowed_fields)

        if method != 'POST' and method != 'PUT' and method != 'DELETE':
            raise ValueError('The method should be POST, PUT or DELETE')

        if method == 'DELETE':
            url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/FbSubscription/SuNr/{data['subscription_id']}"
            base_body = {}
        else:
            if 'subscription_line_id' in data.keys() or 'start_date_subscription_line' in data.keys():
                url = f'https://{self.environment}.{self.base_url}/ProfitRestServices/connectors/FbSubscription/FbSubscriptionLines/'
            else:
                url = f'https://{self.environment}.{self.base_url}/ProfitRestServices/connectors/FbSubscription/'

            base_body = {
                "FbSubscription": {
                    "Element": {
                        "Fields": {
                            "SuNr": data['subscription_id']
                        },
                        "Objects": {

                        }
                    }
                }
            }

            lines_body = {
                "FbSubscriptionLines": {
                    "Element": {
                        "Fields": {
                        }
                    }
                }
            }

            # If one of the optional fields of a subelement is included, we need to merge the whole JSON object to the basebody
            if any(field in data.keys() for field in allowed_fields):
                fields_to_update = {}
                fields_to_update.update({"VaIt": data['item_type_id']}) if 'item_type_id' in data else fields_to_update
                fields_to_update.update({"ItCd": data['item_code']}) if 'item_code' in data else fields_to_update
                fields_to_update.update({"Id": data['subscription_line_id']}) if 'subscription_line_id' in data else fields_to_update
                fields_to_update.update({"DaSt": data['start_date_subscription_line']}) if 'start_date_subscription_line' in data else fields_to_update
                fields_to_update.update({"DaEn": data['end_date_subscription_line']}) if 'end_date_subscription_line' in data else fields_to_update
                fields_to_update.update({"Qu": data['amount']}) if 'amount' in data else fields_to_update
                fields_to_update.update({"VaRs": data['reason_of_termination']}) if 'reason_of_termination' in data else fields_to_update
                fields_to_update.update({"Pric": data['price']}) if 'price' in data else fields_to_update
                # merge subelement with basebody if there are address fields added. If not, don't add the address part to the base_body
                fields_to_update.update(custom_fields_lines) if custom_fields_lines is not None else ''

                if len(fields_to_update) > 0:
                    lines_body['FbSubscriptionLines']['Element']['Fields'].update(fields_to_update)
                    base_body['FbSubscription']['Element']['Objects'].update(lines_body)

            # Add allowed fields to the basebody if they are available in the data. Fields that are not exists in the basebody, should not be added tot this basebody to prevent errrors.
            fields_to_update = {}
            fields_to_update.update({"VaIn": data['invoice_cycle']}) if 'invoice_cycle' in data else fields_to_update
            fields_to_update.update({"SuSt": data['start_date_subscription']}) if 'start_date_subscription' in data else fields_to_update
            fields_to_update.update({"SuEn": data['end_date_subscription']}) if 'end_date_subscription' in data else fields_to_update
            fields_to_update.update({"VaRs": data['reason_of_termination_subscription']}) if 'reason_of_termination_subscription' in data else fields_to_update
            base_body['FbSubscription']['Element']['Fields'].update(fields_to_update)

            # Now create a dict for all the custom fields. This fields are not by default added to the base_body because they're not always present in the dataset
            fields_to_update = {}
            fields_to_update.update(custom_fields) if custom_fields is not None else ''

            # Update the request body with update fields
            base_body['FbSubscription']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)
        return update

    def update_timetable(self, data: dict, overload_fields: dict = None, method="PUT") -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Give the guid and value from a free field if wanted
        :param method: PUT or POST, depending on the case
        :return: status code for request and optional error message
        """
        required_fields = ['startdate', 'employee_id']
        either_or_fields = ['weekly_hours', 'standard_schedule']
        allowed_fields = {
            "start_date_schedule": "DaBg",
            "employment_number": "DvSn",
            "standard_schedule": "SeNo",
            "type_of_schedule": "EtTy",
            "suspension_hours_type": "StIn",
            "deviation_hours_per_week_report": "DfHo",
            "variable_work_pattern": "StPa",
            "variable_work_pattern_with_schedule": "Spec",
            "flexible_working_hours": "PtDu",
            "days_per_week": "DyWk",
            "leave_build_up_per_week": "AhWk",
            "start_time_sunday": "TbSu",
            "end_time_sunday": "TeSu",
            "break_duration_sunday": "PsSu",
            "start_time_monday": "TbMo",
            "end_time_monday": "TeMo",
            "break_duration_monday": "PsMo",
            "start_time_tuesday": "TbTu",
            "end_time_tuesday": "TeTu",
            "break_duration_tuesday": "PsTu",
            "start_time_wednesday": "TbWe",
            "end_time_wednesday": "TeWe",
            "break_duration_wednesday": "PsWe",
            "start_time_thursday": "TbTh",
            "end_time_thursday": "TeTh",
            "break_duration_thursday": "PsTh",
            "start_time_friday": "TbFr",
            "end_time_friday": "TeFr",
            "break_duration_friday": "PsFr",
            "start_time_saturday": "TbSa",
            "end_time_saturday": "TeSa",
            "break_duration_saturday": "PsSa",
            "parttime_percentage": "PcPt",
            "sunday_working_day": "WdSu",
            "monday_working_day": "WdMo",
            "tuesday_working_day": "WdTu",
            "wednesday_working_day": "WdWe",
            "thursday_working_day": "WdTh",
            "friday_working_day": "WdFr",
            "saturday_working_day": "WdSa",
            "five_sv_days": "FtSv",
            "on_call_contract": ["ClAg", "CIAg"],
            "apply_min_max_contract_in_payroll": "Immc",
            "minimum_hours_per_week": "HrMn",
            "maximum_hours_per_week": "HrMx",
            "annual_hours_standard": "YrHr",
            "minimum_hours_per_period": "HrPm",
            "hours_commitment": "HrPr",
            "fte": "Ft",
            "fte_sunday": "FtSu",
            "fte_monday": "FtMo",
            "fte_tuesday": "FtTu",
            "fte_wednesday": "FtWe",
            "fte_thursday": "FtTh",
            "fte_friday": "FtFr",
            "fte_saturday": "FtSa",
            "hours_sunday": "HrSu",
            "hours_monday": "HrMo",
            "hours_tuesday": "HrTu",
            "hours_wednesday": "HrWe",
            "hours_thursday": "HrTh",
            "hours_friday": "HrFr",
            "hours_saturday": "HrSa",
            "bapo_fte": "FtBp",
            "save_bapo_fte": "FtSb",
            "remuneration_percentage": "ReRa",
            "reorganization_working_hours": "ReWt",
            "irregular_employment": "IrEm",
            "involuntary_part_time": "InPt",
            "work_schedule_code": "CoWo",
            "c_documents": "CDoc",
            "cao_42": "Cl42",
            "shift_night_reduction": "ShRe",
            "work_recovery_counter": "WrNu",
            "work_recovery_denominator": "WrDe",
            "work_recovery_scheme": "WrRe",
            "regularity_code": "ReCo",
            "child": "PlaFaSn",
            "parental_leave_hours_per_week": "PlaPhWk",
            "parental_leave_form_be": "PlaViTy",
            "number_of_blocks_be": "PlaAmBl",
            "parental_leave_distribution_type": "PlaVaDl",
            "paid_parental_leave_percentage": "PlaPerc",
            "planned_end_date_parental_leave": "PlaPlDe",
            "parental_leave_hours_monday": "PhMo",
            "parental_leave_hours_tuesday": "PhTu",
            "parental_leave_hours_wednesday": "PhWe",
            "parental_leave_hours_thursday": "PhTh",
            "parental_leave_hours_friday": "PhFr",
            "parental_leave_hours_saturday": "PhSa",
            "parental_leave_hours_sunday": "PhSu",
            "parental_leave_fte_monday": "PfMo",
            "parental_leave_fte_tuesday": "PfTu",
            "parental_leave_fte_wednesday": "PfWe",
            "parental_leave_fte_thursday": "PfTh",
            "parental_leave_fte_friday": "PfFr",
            "parental_leave_fte_saturday": "PfSa",
            "parental_leave_fte_sunday": "PfSu"
        }

        # Fields workschedule (Optional: If one field is given, all fields are required)
        fields_workschedule = ['startdate_workcycle', 'workcycle', 'start_week', 'index_number']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=list(allowed_fields.keys()), either_or_fields=either_or_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasTimeTable')

        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasTimeTable": {
                            "Element": {
                                "@DaBg": data['startdate'],
                                "Fields": {
                                    "StPa": True,
                                    #the following should only be added if the field is given in the data then the holw line should not be addded
                                    "HrWk": data['weekly_hours'] if 'weekly_hours' in data else '',
                                    "SeNo": data['standard_schedule'] if 'standard_schedule' in data else ''
                                }
                            }
                        }
                    }
                }
            }
        }

        # Add allowed fields to the body if they are added to the data
        for field in (allowed_fields.keys() & data.keys()):
            base_body['AfasEmployee']['Element']['Objects']['AfasTimeTable']['Element']['Fields'].update({allowed_fields[field]: data[field]})
        # Add custom fields to the body
        base_body['AfasEmployee']['Element']['Objects']['AfasTimeTable']['Element']['Fields'].update(overload_fields) if overload_fields is not None else ''

        # Add a workschedule to the body if the fields are added to the data
        if any(field in data.keys() for field in fields_workschedule):
            for field in fields_workschedule:
                if field not in data.keys():
                    raise KeyError('Field {field} is required. Required fields for workschedules are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))

            workschedule = {
                "Objects": [
                    {
                        "AfasWorkTime": {
                            "Element": {
                                "@DaBe": data['startdate_workcycle'],
                                "Fields": {
                                    "Twcy": data['workcycle'],
                                    "Twcp": data['start_week'],
                                    "Twcc": data['index_number']
                                }
                            }
                        }
                    }
                ]
            }
            base_body['AfasEmployee']['Element']['Objects']['AfasTimeTable']['Element'].update(workschedule)

        if self.debug:
            print(json.dumps(base_body))

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def new_wage_component(self, data: dict, overload_fields: dict = None, method="POST") -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :param method: request type
        :return: status code for request and optional error message
        """
        allowed_fields = ['enddate', 'contract_no', 'apply_type']
        required_fields = ['employee_id', 'parameter', 'startdate', 'value']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        if method == 'DELETE':
            url = f"https://{self.environment}.{self.base_url}/ProfitRestServices/connectors/HrVarValue/HrVarValue/VaId,Va,EmId,DaBe/{data['parameter']},{data['value']},{data['employee_id']},{data['startdate']}"
            base_body = {}
        else:
            url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'HrVarValue')
            base_body = {
                "HrVarValue": {
                    "Element": {
                        "Fields": {
                            "VaId": data['parameter'],
                            "Va": data['value'],
                            "EmId": data['employee_id'],
                            "DaBe": data['startdate']
                        }
                    }
                }
            }
            fields_to_update = {}

            # Add fields that you want to update a dict (adding to body itself is too much text)
            fields_to_update.update({"EnSe": data['contract_no']} if 'contract_no' in data else fields_to_update)
            fields_to_update.update({"DaEn": data['enddate']} if 'enddate' in data else fields_to_update)
            fields_to_update.update({"DiTp": data['apply_type']} if 'apply_type' in data else fields_to_update)

            fields_to_update.update(overload_fields) if overload_fields is not None else ''

            # Update the request body with update fields
            base_body['HrVarValue']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def new_wage_mutation(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: status code for request and optional error message
        """
        allowed_fields = ['period_table', 'date']
        required_fields = ['employee_id', 'year', 'month', 'employer_id', 'wage_component_id', 'value']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'HrCompMut')

        # Build the base body
        base_body = {
            "HrCompMut": {
                "Element": {
                    "@Year": data['year'],
                    "@PeId": data['month'],
                    "@EmId": data['employee_id'],
                    "@ErId": data['employer_id'],
                    "@Sc02": data['wage_component_id'],
                    # The 'Fields' node is typically for the actual wage values and custom fields
                    "Fields": {
                        "VaD1": data['value']
                    }
                }
            }
        }

        # Default 'period_table' to 5 if not provided or if it's empty
        period_table = data.get('period_table')
        if not period_table:  # This checks for None, '', or other "falsy" values
            period_table = 5
        base_body["HrCompMut"]["Element"]["@PtId"] = period_table

        # Add date if present
        if 'date' in data:
            base_body["HrCompMut"]["Element"]["@DaTi"] = data['date']

        # Add any overload_fields to the "Fields" node
        if overload_fields:
            base_body['HrCompMut']['Element']['Fields'].update(overload_fields)

        # Make the POST request
        response = requests.request("POST", url, data=json.dumps(base_body), headers=self.headers)

        return response

    def update_wage_mutation(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed_fields array.
        :param overload_fields: (Optional) custom fields in this dataset, e.g. {'DFEDS8-DSF9uD-DDSA': 'Vrij veld'}.
        :return: The requests.Response object
        """
        allowed_fields = ['period_table', 'date']
        required_fields = ['employee_id', 'year', 'month', 'employer_id', 'wage_component_id', 'value', 'guid']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrCompMutGUID'

        # Build the request body with top-level attributes
        base_body = {
            "HrCompMutGUID": {
                "Element": {
                    # The GUID for the mutation we want to update
                    "@GuLi": data['guid'],
                    "@Year": data['year'],
                    "@PeId": data['month'],
                    "@EmId": data['employee_id'],
                    "@ErId": data['employer_id'],
                    "@Sc02": data['wage_component_id'],
                    # The 'Fields' node is typically for the actual wage values and custom fields
                    "Fields": {
                        "VaD1": data['value']
                    }
                }
            }
        }

        # We can handle optional fields here
        # If 'period_table' is in data, treat it as an attribute. Otherwise, default to 5
        period_table = data.get('period_table', 5)
        base_body["HrCompMutGUID"]["Element"]["@PtId"] = period_table

        # If date is present, add it as an attribute: @DaTi
        if 'date' in data:
            base_body["HrCompMutGUID"]["Element"]["@DaTi"] = data['date']

        # If you have any overload_fields, add them to the "Fields" dictionary
        if overload_fields:
            base_body['HrCompMutGUID']['Element']['Fields'].update(overload_fields)

        # Make the PUT request
        update = requests.request("PUT", url, data=json.dumps(base_body), headers=self.headers)
        return update

    def delete_wage_mutation(self, data: dict) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: status code for request and optional error message
        """
        allowed_fields = []
        required_fields = ['guid']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrCompMutGUID/HrCompMutGUID/@GuLi/{data["guid"]}'

        update = requests.request("DELETE", url, headers=self.headers)

        return update

    def update_bank_account(self, data: dict, overload_fields: dict = None, method='PUT') -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Custom Fields with custom ID's can be entered here with key: value
        :param method: request type
        :return: status code for request and optional error message
        """
        required_fields = ['employee_id', 'iban']
        allowed_fields = ['bankname', 'country', 'cash_payment', 'salary_bank_account', 'acc_outside_sepa', 'bank_type', 'iban_check', 'sequence_number', 'bic_code',
                          'payment_reference', 'deviating_name', 'wage_component_id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        if method == 'DELETE':
            url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnEmployee/AfasEmployee/@EmId/{data['employee_id']}/AfasBankInfo/SeNo/{data['sequence_number']}"
            base_body = {}
        else:
            url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasBankInfo')
            base_body = {
                "AfasEmployee": {
                    "Element": {
                        "@EmId": data['employee_id'],
                        "Objects": {
                            "AfasBankInfo": {
                                "Element": {
                                    "@AcId":data['iban'],
                                    "@NoBk": False if 'cash_payment' not in data else data['cash_payment'],
                                    "Fields": {
                                        "IbCk":  True,  # IBAN check (always true)
                                        "Iban": data['iban']  # "NL91ABNA0417164300"
                                    }
                                }
                            }
                        }
                    }
                }
            }

            fields_to_update = {}

            # Add fields that you want to update a dict (adding to body itself is too much text)
            fields_to_update.update({"BkIc": data['bankname']}) if 'bankname' in data else fields_to_update
            fields_to_update.update({"CoId": data['country']}) if 'country' in data else fields_to_update
            fields_to_update.update({"SaAc": data['salary_bank_account']}) if 'salary_bank_account' in data else fields_to_update
            fields_to_update.update({"FoPa": data['acc_outside_sepa']}) if 'acc_outside_sepa' in data else fields_to_update
            fields_to_update.update({"BkTp": data['bank_type']}) if 'bank_type' in data else fields_to_update
            fields_to_update.update({"IbCk": data['iban_check']}) if 'iban_check' in data else fields_to_update
            fields_to_update.update({"SeNo": data['sequence_number']}) if 'sequence_number' in data else fields_to_update
            fields_to_update.update({"Bic": data['bic_code']}) if 'bic_code' in data else fields_to_update
            fields_to_update.update({"Ds": data['payment_reference']}) if 'payment_reference' in data else fields_to_update
            fields_to_update.update({"Nm": data['deviating_name']}) if 'deviating_name' in data else fields_to_update
            # Add wage_component_id if its in the data and if its not a 0 or ''
            fields_to_update.update({"ScId": data['wage_component_id']}) if 'wage_component_id' in data and data['wage_component_id'] != 0 and data['wage_component_id'] != '' else fields_to_update

            fields_to_update.update(overload_fields) if overload_fields is not None else ''

            # Update the request body with update fields
            base_body['AfasEmployee']['Element']['Objects']['AfasBankInfo']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_bank_account_person(self, data: dict, overload_fields: dict = None, method='POST') -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :param method: request type
        :return: status code for request and optional error message
        """
        allowed_fields = ['bankname', 'country', 'bank_type', 'bic_code', 'match_employees_on', 'ssn']
        required_fields = ['person_id', 'iban', 'iban_check']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnPerson/KnBankAccount'
        base_body = {
            "KnPerson": {
                "Element": {
                    "Fields": {
                        "MatchPer": "1" if "match_employees_on" not in data else data['match_employees_on'],
                        "BcCo": data['person_id']
                    },
                    "Objects": {
                        "KnBankAccount": {
                            "Element": {
                                "Fields": {
                                    "Iban": data['iban'],
                                    "IbCk": data['iban_check']
                                }
                            }
                        }
                    }
                }
            }
        }

        fields_to_update = {}
        fields_to_update_person = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"CoId": data['country']}) if 'country' in data else fields_to_update
        fields_to_update.update({"BkTp": data['bank_type']}) if 'bank_type' in data else fields_to_update
        fields_to_update.update({"IbCk": data['iban_check']}) if 'iban_check' in data else fields_to_update
        fields_to_update.update({"Bic": data['bic_code']}) if 'bic_code' in data else fields_to_update
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        fields_to_update_person.update({"SoSe": data['ssn']}) if 'ssn' in data else fields_to_update_person

        # Update the request body with update fields
        base_body['KnPerson']['Element']['Objects']['KnBankAccount']['Element']['Fields'].update(fields_to_update)

        base_body['KnPerson']['Element']['Fields'].update(fields_to_update_person)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def new_employee_with_first_contract(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Any custom fields that are not in the allowed or required fields. Specify sub dictionaries for each section you want to update.
        Available options are: employee, person, contract, function, schedule, salary. Specify like: overload_fields = {"employee": {"field": value}}
        :return: status code for request and optional error message
        """
        # Check if the person already exist and only needs to be linked to the new employee. Other option is to create the person together with the employee
        match_person_on = data.get('match_person_on')
        if str(match_person_on) == '0':
            required_fields_person =['person_id']
            allowed_fields_person, required_fields_address, allowed_fields_address = [], [], []
        else:
            required_fields_person = ['last_name', 'gender', 'first_name', 'date_of_birth', 'ssn']
            allowed_fields_person = ['employee_id', 'employee_status', 'employee_blocked', 'date_of_death', 'initials', 'email_work', 'email_home', 'country_of_birth', 'place_of_birth', 'prefix',
                                     'birth_name_separate', 'name_use', 'send_payslip', 'send_annual_statement', 'match_employees_on', 'nickname', 'birthname', 'prefix_birthname',
                                     'prefix_birthname_partner', 'secure_email_attachment', 'email_password', 'mail_digital_documents', 'date_of_divorce', 'title_salutation', 'second_title_salutation',
                                     'birthname_partner', 'mail_work', 'mail_private', 'mobile_work', 'mobile_private', 'marital_status', 'date_of_marriage', 'phone_work', 'phone_private',
                                     'nationality', 'auto_number']
            required_fields_address = ['house_number', 'street', 'postal_code', 'city', 'address_country']
            allowed_fields_address = ['search_address_by_postal_code', 'street_number_add', 'postal_address_applied', 'postal_address', 'address_addition']

        # Continue with Contract fields
        required_fields_contract = ['date_effective', 'type_of_contract', 'collective_agreement', 'terms_of_employment', 'employment', 'type_of_employee', 'employer']
        allowed_fields_contract = ['end_date_contract', 'seniority_date', 'date_in_service_original', 'probation_period_code', 'end_date_probation_period', 'contract_chain_code',
                                   'start_date_contract_chain', 'number_income_ratio', 'date_of_termination', 'period_number_period', 'repeat_after_n_periods', 'period_next_raise',
                                   'employment_id', 'written_contract', 'termination_initiative', 'termination_reason', 'reason_end_of_contract']

        # function fields
        required_fields_function = ['organizational_unit', 'date_effective', 'function_id', 'costcenter']
        allowed_fields_function = ['costcarrier']

        # schedule fields
        if 'standard_schedule' in data:
            required_fields_schedule = ['standard_schedule']
            allowed_fields_schedule = []
        else:
            required_fields_schedule = ['weekly_hours', 'parttime_percentage']
            allowed_fields_schedule = ['changing_work_pattern', 'days_per_week', 'fte', 'type_of_schedule', 'on-call_contract', 'on_call_agreement', 'deviation_hours_per_week_report',
                                       'absence_hours_week_tax']

        # Workschedule fields (Optional: If one field is given, all fields are required)
        fields_workschedule = ['startdate_workcycle', 'workcycle', 'start_week', 'index_number']

        fields_tax_authority = ['tax_authority_code', 'income_relationship_type', 'nature_of_employment', 'table_colour', 'table_code', 'payroll_tax_credit',
                                'zvw', 'zvw_code', 'vw', 'ww', 'wia', 'risk_group_sector', 'risk_group_sector_diff', 'cbs_cla', 'cbs_cla_diff', 'on_call_with', 'apply_day_table']

        # Salary fields
        required_fields_salary = ['type_of_salary']
        allowed_fields_salary = ['step', 'salary_scale', 'salary_scale_type', 'function_scale', 'function_scale_type', 'salary_year', 'net_salary', 'apply_timetable', 'amount',
                                 'period_table']

        allowed_fields = allowed_fields_person + allowed_fields_function + allowed_fields_salary + allowed_fields_schedule + allowed_fields_contract + allowed_fields_address + fields_tax_authority
        required_fields = required_fields_contract + required_fields_function + required_fields_schedule + required_fields_salary + required_fields_address + required_fields_person

        # Check if there are fields that are not allowed or fields missing that are required
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee')

        body = {
            "AfasEmployee": {
                "Element": {
                    "Fields": {},
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": data['match_person_on'],
                                }
                            }
                        },
                        "AfasContract": {
                            "Element": {
                                "@DaBe": data['date_effective'],
                                "Fields": {
                                    "ClId": data['collective_agreement'],  # Cao - fixed
                                    "WcId": data['terms_of_employment'],
                                    "ApCo": data['type_of_contract'],  # Type of contract
                                    "CmId": data['employer'],  # employer - fixed
                                    "EmMt": data['type_of_employee'],  # Type of employee (1=personeelslid)
                                    "ViEt": data['employment']  # Dienstbetrekking
                                }
                            }
                        },
                        "AfasOrgunitFunction": {
                            "Element": {
                                "@DaBe": data['date_effective'],  # Startdate organizational unit
                                "Fields": {
                                    "DpId": data['organizational_unit'],  # OE
                                    "FuId": data['function_id'],  # Function 0232=medewerk(st)er
                                    "CrId": data['costcenter']  # Cost center
                                }
                            }
                        },
                        "AfasTimeTable": {
                            "Element": {
                                "@DaBg": data['date_effective'],  # Startdate Timetable
                                "Fields": {

                                }
                            }
                        },
                        "AfasSalary": {
                            "Element": {
                                "@DaBe": data['date_effective'],  # Startdate salary
                                "Fields": {
                                    "SaPe": data['type_of_salary'],  # Sort of salary - fixed (V=vast)
                                    "PtId": data['period_table'] if 'period_table' in data else 5  # Period table - fixed (periode HRM)
                                }
                            }
                        },
                        "AfasAgencyFiscus": {
                            "Element": {
                                "Fields": {
                                }
                            }
                        }
                    }
                }
            }
        }

        if any(field in data.keys() for field in fields_workschedule):
            for field in fields_workschedule:
                if field not in data.keys():
                    raise KeyError(
                        'Field {field} is required. Required fields for workschedules are: {required_fields}'.format(
                            field=field, required_fields=tuple(required_fields)))

            workschedule = {
                "Objects": [
                    {
                        "AfasWorkTime": {
                            "Element": {
                                "@DaBe": data['startdate_workcycle'],
                                "Fields": {
                                    "Twcy": data['workcycle'],
                                    "Twcp": data['start_week'],
                                    "Twcc": data['index_number']
                                }
                            }
                        }
                    }
                ]
            }
            body['AfasEmployee']['Element']['Objects']['AfasTimeTable']['Element'].update(workschedule)

        knadres_object = None
        if 'house_number' in data:
            knadres_object={"Objects": [
                {
                    "KnBasicAddressAdr": {
                        "Element": {
                            "Fields": {
                                "CoId": data['address_country'],
                                "PbAd": False,  # Postbusadres
                                "Ad": data['street'],
                                "HmNr": data['house_number'],
                                "ZpCd": data['postal_code'],
                                "Rs": data['city'],
                                "ResZip": data['search_address_by_postal_code'] if 'search_address_by_postal_code' in data.keys() else True,
                            }
                        }
                    }
                },
                {
                    "KnBasicAddressPad": {
                        "Element": {
                            "Fields": {
                                "CoId": data['address_country'],
                                "PbAd": False,  # Postbusadres
                                "Ad": data['street'],
                                "HmNr": data['house_number'],
                                "ZpCd": data['postal_code'],
                                "Rs": data['city'],
                                "ResZip": data['search_address_by_postal_code'] if 'search_address_by_postal_code' in data.keys() else True,
                            }
                        }
                    }
                }
            ]}
            body['AfasEmployee']['Element']['Objects']['KnPerson']['Element'].update(knadres_object)

            # Add overload fields to the base of the address data
            fields_to_update_address = {}
            fields_to_update_address.update({"HmAd": data['street_number_add']}) if 'street_number_add' in data else fields_to_update_address
            if overload_fields is not None and 'address' in overload_fields.keys():
                fields_to_update_address.update(overload_fields['address'])
            # Update the request body with update fields
            body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Objects'][0]['KnBasicAddressAdr']['Element']['Fields'].update(fields_to_update_address)
            body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Objects'][0]['KnBasicAddressPad']['Element']['Fields'].update(fields_to_update_address)

        # Add overload fields to the base of the employee data
        fields_to_update_employee = {}
        fields_to_update_employee.update({"DaMa": data['date_of_marriage']}) if 'date_of_marriage' in data else fields_to_update_employee
        fields_to_update_employee.update({"DaDe": data['date_of_death']}) if 'date_of_death' in data else fields_to_update_employee
        fields_to_update_employee.update({"DaDi": data['date_of_divorce']}) if 'date_of_divorce' in data else fields_to_update_employee
        fields_to_update_employee.update({"PsPv": data['send_payslip']}) if 'send_payslip' in data else fields_to_update_employee
        fields_to_update_employee.update({"YsPv": data['send_annual_statement']}) if 'send_annual_statement' in data else fields_to_update_employee
        fields_to_update_employee.update({"ViSe": data['employee_status']}) if 'employee_status' in data else fields_to_update_employee
        fields_to_update_employee.update({"Bl": data['employee_blocked']}) if 'employee_blocked' in data else fields_to_update_employee
        fields_to_update_employee.update({"SeAt": data['secure_email_attachment']}) if 'secure_email_attachment' in data else fields_to_update_employee
        fields_to_update_employee.update({"EmAd": data['mail_digital_documents']}) if 'mail_digital_documents' in data else fields_to_update_employee
        fields_to_update_employee.update({"PwEm": data['email_password']}) if 'email_password' in data else fields_to_update_employee
        if "employee_id" in data:
            body['AfasEmployee']['Element'].update({"@EmId": data['employee_id']})
        # add overload employee fields to  the body
        if overload_fields is not None and 'employee' in overload_fields.keys():
            fields_to_update_employee.update(overload_fields['employee'])
        body['AfasEmployee']['Element']['Fields'].update(fields_to_update_employee)

        # Add overload fields to the base of the contract data
        fields_to_update_contract = {}
        fields_to_update_contract.update({"DaEn": data['end_date_contract']}) if 'end_date_contract' in data else fields_to_update_contract
        fields_to_update_contract.update({"StAc": data['seniority_date']}) if 'seniority_date' in data else fields_to_update_contract
        fields_to_update_contract.update({"ViTo": data['probation_period_code']}) if 'probation_period_code' in data else fields_to_update_contract
        fields_to_update_contract.update({"DaEt": data['end_date_probation_period']}) if 'end_date_probation_period' in data else fields_to_update_contract
        fields_to_update_contract.update({"DaSc": data['start_date_contract_chain']}) if 'start_date_contract_chain' in data else fields_to_update_contract
        fields_to_update_contract.update({"ViKe": data['contract_chain_code']}) if 'contract_chain_code' in data else fields_to_update_contract
        fields_to_update_contract.update({"DbYs": data['date_in_service_original']}) if 'date_in_service_original' in data else fields_to_update_contract
        fields_to_update_contract.update({"EnS2": data['number_income_ratio']}) if 'number_income_ratio' in data else fields_to_update_contract
        fields_to_update_contract.update({"DaEe": data['date_of_termination']}) if 'date_of_termination' in data else fields_to_update_contract
        fields_to_update_contract.update({"ViIe": data['termination_initiative']}) if 'termination_initiative' in data else fields_to_update_contract
        fields_to_update_contract.update({"ViRe": data['termination_reason']}) if 'termination_reason' in data else fields_to_update_contract
        fields_to_update_contract.update({"PeNo": data['period_number_period']}) if 'period_number_period' in data else fields_to_update_contract
        fields_to_update_contract.update({"PeRp": data['repeat_after_n_periods']}) if 'repeat_after_n_periods' in data else fields_to_update_contract
        fields_to_update_contract.update({"PeFt": data['period_next_raise']}) if 'period_next_raise' in data else fields_to_update_contract
        fields_to_update_contract.update({"EnSe": data['employment_id']}) if 'employment_id' in data else fields_to_update_contract
        fields_to_update_contract.update({"WrCt": data['written_contract']}) if 'written_contract' in data else fields_to_update_contract
        fields_to_update_contract.update({"DvbViAo": data['reason_end_of_contract']}) if 'reason_end_of_contract' in data else fields_to_update_contract
        # add overload contract fields to  the body
        if overload_fields is not None and 'contract' in overload_fields.keys():
            fields_to_update_contract.update(overload_fields['contract'])
        body['AfasEmployee']['Element']['Objects']['AfasContract']['Element']['Fields'].update(
            fields_to_update_contract)

        # Add overload fields to the base of the job data
        fields_to_update_job = {}
        fields_to_update_job.update({"CcId": data['costcarrier']}) if 'costcarrier' in data else fields_to_update_job
        # add overload contract fields to  the body
        if overload_fields is not None and 'job' in overload_fields.keys():
            fields_to_update_job.update(overload_fields['job'])
        body['AfasEmployee']['Element']['Objects']['AfasOrgunitFunction']['Element']['Fields'].update(
            fields_to_update_job)

        # Add overload fields to the base of the salary data
        fields_to_update_salary = {}
        fields_to_update_salary.update({"SaSt": data['step']}) if 'step' in data else fields_to_update_salary
        fields_to_update_salary.update({"SaYe": data['salary_year']}) if 'salary_year' in data else fields_to_update_salary
        fields_to_update_salary.update({"PtId": data['period_table']}) if 'period_table' in data else fields_to_update_salary.update({"PtId": 5})
        fields_to_update_salary.update({"VaSc": data['salary_scale']}) if 'salary_scale' in data else fields_to_update_salary
        fields_to_update_salary.update({"TaId": data['salary_scale_type']}) if 'salary_scale_type' in data else fields_to_update_salary
        fields_to_update_salary.update({"FuSc": data['function_scale']}) if 'function_scale' in data else fields_to_update_salary
        fields_to_update_salary.update({"FuTa": data['function_scale_type']}) if 'function_scale_type' in data else fields_to_update_salary
        fields_to_update_salary.update({"NtSa": data['net_salary']}) if 'net_salary' in data else fields_to_update_salary
        fields_to_update_salary.update({"TtPy": data['apply_timetable']}) if 'apply_timetable' in data else fields_to_update_salary
        fields_to_update_salary.update({"EmSa": data['amount']}) if 'amount' in data else fields_to_update_salary
        if overload_fields is not None and 'salary' in overload_fields.keys():
            fields_to_update_salary.update(overload_fields['salary'])
        # Update the request body with update fields
        body['AfasEmployee']['Element']['Objects']['AfasSalary']['Element']['Fields'].update(fields_to_update_salary)

        # Add overload fields to the base of the person data
        fields_to_update_person = {}
        fields_to_update_person.update({"In": data['initials']}) if 'initials' in data else fields_to_update_person
        fields_to_update_person.update({"CoBi": data['country_of_birth']}) if 'country_of_birth' in data else fields_to_update_person
        fields_to_update_person.update({"RsBi": data['place_of_birth']}) if 'place_of_birth' in data else fields_to_update_person
        fields_to_update_person.update({"IsBi": data['birthname_prefix']}) if 'birthname_prefix' in data else fields_to_update_person
        fields_to_update_person.update({"NmBi": data['birthname']}) if 'birthname' in data else fields_to_update_person
        fields_to_update_person.update({"IsPa": data['prefix_birthname_partner']}) if 'prefix_birthname_partner' in data else fields_to_update_person
        fields_to_update_person.update({"NmPa": data['birthname_partner']}) if 'birthname_partner' in data else fields_to_update_person
        fields_to_update_person.update({"EmAd": data['email_work']}) if 'email_work' in data else fields_to_update_person
        fields_to_update_person.update({"EmAd": data['mail_work']}) if 'mail_work' in data else fields_to_update_person
        fields_to_update_person.update({"EmA2": data['email_home']}) if 'email_home' in data else fields_to_update_person
        fields_to_update_person.update({"EmA2": data['mail_private']}) if 'mail_private' in data else fields_to_update_person
        fields_to_update_person.update({"SpNm": data['birth_name_separate']}) if 'birth_name_separate' in data else fields_to_update_person
        fields_to_update_person.update({"ViUs": data['name_use']}) if 'name_use' in data else fields_to_update_person
        fields_to_update_person.update({"Is": data['prefix']}) if 'prefix' in data else fields_to_update_person
        fields_to_update_person.update({"CaNm": data['nickname']}) if 'nickname' in data else fields_to_update_person
        fields_to_update_person.update({"MbNr": data['mobile_work']}) if 'mobile_work' in data else fields_to_update_person
        fields_to_update_person.update({"MbN2": data['mobile_private']}) if 'mobile_private' in data else fields_to_update_person
        fields_to_update_person.update({"CaNm": data['nickname']}) if 'nickname' in data else fields_to_update_person
        fields_to_update_person.update({"PsNa": data['nationality']}) if 'nationality' in data else fields_to_update_person
        fields_to_update_person.update({"ViCs": data['marital_status']}) if 'marital_status' in data else fields_to_update_person
        fields_to_update_person.update({"DaMa": data['date_of_marriage']}) if 'date_of_marriage' in data else fields_to_update_person
        fields_to_update_person.update({"TeNr": data['phone_work']}) if 'phone_work' in data else fields_to_update_person
        fields_to_update_person.update({"TeN2": data['phone_private']}) if 'phone_private' in data else fields_to_update_person
        fields_to_update_person.update({"PadAdr": data['postal_address_applied']}) if 'postal_address_applied' in data else fields_to_update_person
        fields_to_update_person.update({"ApAd": data['postal_address']}) if 'postal_address' in data else fields_to_update_person
        fields_to_update_person.update({"AdAd": data['address_addition']}) if 'address_addition' in data else fields_to_update_person
        fields_to_update_person.update({"Ttid": data['title_salutation']}) if 'title_salutation' in data else fields_to_update_person
        fields_to_update_person.update({"TtEx": data['second_title_salutation']}) if 'second_title_salutation' in data else fields_to_update_person
        fields_to_update_person.update({"BcCo": data['employee_id']}) if 'employee_id' in data else fields_to_update_person
        fields_to_update_person.update({"AutoNum": False if 'auto_number' not in data.keys() else data['auto_number']})
        fields_to_update_person.update({"SeNm": data['last_name'][:10]}) if 'last_name' in data else fields_to_update_person
        fields_to_update_person.update({"FiNm": data['first_name']})  if 'first_name' in data else fields_to_update_person
        fields_to_update_person.update({"LaNm": data['last_name']}) if 'last_name' in data else fields_to_update_person
        fields_to_update_person.update({"SpNm": data['birth_name_separate']}) if 'birth_name_separate' in data else fields_to_update_person
        fields_to_update_person.update({"NmBi": data['last_name']}) if 'birthname' in data else fields_to_update_person
        fields_to_update_person.update({"ViUs": data['name_use']}) if 'name_use' in data else fields_to_update_person
        fields_to_update_person.update({"ViGe": data['gender']})  if 'gender' in data else fields_to_update_person
        fields_to_update_person.update({"DaBi": data['date_of_birth']}) if 'date_of_birth' in data else fields_to_update_person
        fields_to_update_person.update({"SoSe": data['ssn']}) if 'ssn' in data else fields_to_update_person
        if overload_fields is not None and 'person' in overload_fields.keys():
            fields_to_update_person.update(overload_fields['person'])
        # Update the request body with update fields
        body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Fields'].update(fields_to_update_person)

        # Add overload fields to the base of the schedule data
        fields_to_update_schedule = {}
        fields_to_update_schedule.update({"StPa": data['changing_work_pattern']}) if 'changing_work_pattern' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"DyWk": data['days_per_week']}) if 'days_per_week' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"Ft": data['fte']}) if 'fte' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"EtTy": data['type_of_schedule']}) if 'type_of_schedule' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"ClAg": data['on-call_contract']}) if 'on-call_contract' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"ClAg": data['on_call_agreement']}) if 'on_call_agreement' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"DfHo": data['deviation_hours_per_week_report']}) if 'deviation_hours_per_week_report' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"Stpa": data['changing_work_pattern']}) if 'changing_work_pattern' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"HrWk": data['weekly_hours']}) if 'weekly_hours' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"PcPt": data['parttime_percentage']}) if 'parttime_percentage' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"SeNo": data['standard_schedule']}) if 'standard_schedule' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"HrMo": data['hours_monday']}) if 'hours_monday' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"HrTu": data['hours_tuesday']}) if 'hours_tuesday' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"HrWe": data['hours_wednesday']}) if 'hours_wednesday' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"HrTh": data['hours_thursday']}) if 'hours_thursday' in data else fields_to_update_schedule
        fields_to_update_schedule.update({"HrFr": data['hours_friday']}) if 'hours_friday' in data else fields_to_update_schedule

        if overload_fields is not None and 'schedule' in overload_fields.keys():
            fields_to_update_schedule.update(overload_fields['schedule'])

        # Update the request body with update fields
        body['AfasEmployee']['Element']['Objects']['AfasTimeTable']['Element']['Fields'].update(fields_to_update_schedule)

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update_organisational_unit = {}
        if overload_fields is not None and 'organisational_unit' in overload_fields.keys():
            fields_to_update_organisational_unit.update(overload_fields['organisational_unit'])
        # Update the request body with update fields
        body['AfasEmployee']['Element']['Objects']['AfasOrgunitFunction']['Element']['Fields'].update(fields_to_update_organisational_unit)

        # Add tax authority data
        fields_to_update_tax_authority_base = {}
        fields_to_update_tax_authority_base.update({"@DaBe": data['date_effective']}) if 'tax_authority_code' in data else fields_to_update_tax_authority_base
        fields_to_update_tax_authority_base.update({"@AyId": data['tax_authority_code']}) if 'tax_authority_code' in data else fields_to_update_tax_authority_base

        fields_to_update_tax_authority = {}
        fields_to_update_tax_authority.update({"ViIn": data['income_relationship_type']}) if 'income_relationship_type' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViEm": data['nature_of_employment']}) if 'nature_of_employment' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViTs": data['table_colour']}) if 'table_colour' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViCd": data['table_code']}) if 'table_code' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViLk": data['payroll_tax_credit']}) if 'payroll_tax_credit' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"YnZW": data['zw']}) if 'zw' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"YnWW": data['ww']}) if 'ww' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"YWAO": data['wia']}) if 'wia' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViRi": data['risk_group_sector_diff']}) if 'risk_group_sector_diff' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViFc": data['cbs_cla_diff']}) if 'cbs_cla_diff' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"TxGn": data['on_call_with']}) if 'on_call_with' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"TyDt": data['apply_day_table']}) if 'apply_day_table' in data else fields_to_update_tax_authority
        fields_to_update_tax_authority.update({"ViZv": data['zvw_code']}) if 'zvw_code' in data else fields_to_update_tax_authority

        if len(fields_to_update_tax_authority) > 0:
            # see https://help.afas.nl/meldingen/NL/SE/124356.htm for this ridiculous logic and when you find this, curse AFAS that they did not map this automatically like they do in the UI
            fiscal_year = datetime.strptime(data["date_effective"], '%Y-%m-%d').year
            if 'zvw_code' in data:
                zvw_code = data['zvw_code']
            else:
                if fiscal_year < 2006:
                    zvw_code = "C"
                elif fiscal_year < 2013:
                    zvw_code = "CEF"
                else:
                    zvw_code = "K"
            body['AfasEmployee']['Element']['Objects']['AfasAgencyFiscus']['Element'].update(fields_to_update_tax_authority_base)
            body['AfasEmployee']['Element']['Objects']['AfasAgencyFiscus']['Element']['Fields'].update(fields_to_update_tax_authority)
            body['AfasEmployee']['Element']['Objects']['AfasAgencyFiscus']['Element']['Fields'].update({"ViZv": zvw_code})

        if self.debug:
            print(json.dumps(body))

        update = requests.request('POST', url, data=json.dumps(body), headers=self.headers, timeout=60)

        return update

    def create_car(self, data: dict, overload_fields: dict = None) -> requests.Response:
        required_fields = ['car_id', 'employer_id', 'start_date', 'license_plate']
        allowed_fields = ['type_of_vehicle', 'contract_number', 'lease_amount', 'end_date',
                          'end_contract_mileage', 'gray_license_plate', 'serial_number', 'brand', 'model', 'extras', 'remark',
                          'general_use', 'initial_mileage', 'first_registration_date', 'catalog_value', 'fuel', 'standard_deductible', 'leasing_company',
                          'benefit_in_kind_percentage', 'benefit_in_kind_threshold_amount', 'benefit_in_kind_above_threshold_percentage', 'co2_emissions',
                          'energy_label', 'replacement_car', 'leasing_type', 'sd_leasing_company', 'lease_duration', 'annual_mileage', 'light_truck', 'false_hybrid',
                          'co2_non_hybrid', 'co2_false_hybrid', 'co2_wltp_false_hybrid', 'co2_wltp', 'exclude_from_delivery_to_social_secretariat',
                          'vehicle_category', 'utility_residential_work', 'co2_coefficient', 'license_plate_country']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)
        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrMobility"

        payload = {
            "HrMobility": {
                "Element": {
                    "@CcSn": data['car_id'],
                    "Fields": {
                        "CmId": data['employer_id'],
                        "DaBl": data['start_date'],
                        "RgNr": data['license_plate']
                    }
                }
            }
        }

        # Add allowed fields to the payload if they are present in the data
        fields_to_update = {}
        fields_to_update.update({"TrTy": data['type_of_vehicle']}) if 'type_of_vehicle' in data else fields_to_update
        fields_to_update.update({"CoNu": data['contract_number']}) if 'contract_number' in data else fields_to_update
        fields_to_update.update({"LsAm": data['lease_amount']}) if 'lease_amount' in data else fields_to_update
        fields_to_update.update({"DaEl": data['end_date']}) if 'end_date' in data else fields_to_update
        fields_to_update.update({"NrKm": data['end_contract_mileage']}) if 'end_contract_mileage' in data else fields_to_update
        fields_to_update.update({"GrRg": data['gray_license_plate']}) if 'gray_license_plate' in data else fields_to_update
        fields_to_update.update({"SeNu": data['serial_number']}) if 'serial_number' in data else fields_to_update
        fields_to_update.update({"ViMr": data['brand']}) if 'brand' in data else fields_to_update
        fields_to_update.update({"ViMd": data['model']}) if 'model' in data else fields_to_update
        fields_to_update.update({"Ad": data['extras']}) if 'extras' in data else fields_to_update
        fields_to_update.update({"Re": data['remark']}) if 'remark' in data else fields_to_update
        fields_to_update.update({"CmUs": data['general_use']}) if 'general_use' in data else fields_to_update
        fields_to_update.update({"InKm": data['initial_mileage']}) if 'initial_mileage' in data else fields_to_update
        fields_to_update.update({"DaPr": data['first_registration_date']}) if 'first_registration_date' in data else fields_to_update
        fields_to_update.update({"CtVl": data['catalog_value']}) if 'catalog_value' in data else fields_to_update
        fields_to_update.update({"ViFl": data['fuel']}) if 'fuel' in data else fields_to_update
        fields_to_update.update({"OnVl": data['standard_deductible']}) if 'standard_deductible' in data else fields_to_update
        fields_to_update.update({"AgId": data['leasing_company']}) if 'leasing_company' in data else fields_to_update
        fields_to_update.update({"PeAd": data['benefit_in_kind_percentage']}) if 'benefit_in_kind_percentage' in data else fields_to_update
        fields_to_update.update({"AdLi": data['benefit_in_kind_threshold_amount']}) if 'benefit_in_kind_threshold_amount' in data else fields_to_update
        fields_to_update.update({"HiAd": data['benefit_in_kind_above_threshold_percentage']}) if 'benefit_in_kind_above_threshold_percentage' in data else fields_to_update
        fields_to_update.update({"CO2": data['co2_emissions']}) if 'co2_emissions' in data else fields_to_update
        fields_to_update.update({"ViEl": data['energy_label']}) if 'energy_label' in data else fields_to_update
        fields_to_update.update({"ReVe": data['replacement_car']}) if 'replacement_car' in data else fields_to_update
        fields_to_update.update({"LeTy": data['leasing_type']}) if 'leasing_type' in data else fields_to_update
        fields_to_update.update({"LeCo": data['sd_leasing_company']}) if 'sd_leasing_company' in data else fields_to_update
        fields_to_update.update({"LeDu": data['lease_duration']}) if 'lease_duration' in data else fields_to_update
        fields_to_update.update({"KmYe": data['annual_mileage']}) if 'annual_mileage' in data else fields_to_update
        fields_to_update.update({"LiFr": data['light_truck']}) if 'light_truck' in data else fields_to_update
        fields_to_update.update({"FaHy": data['false_hybrid']}) if 'false_hybrid' in data else fields_to_update
        fields_to_update.update({"CO2n": data['co2_non_hybrid']}) if 'co2_non_hybrid' in data else fields_to_update
        fields_to_update.update({"COfh": data['co2_false_hybrid']}) if 'co2_false_hybrid' in data else fields_to_update
        fields_to_update.update({"CWfh": data['co2_wltp_false_hybrid']}) if 'co2_wltp_false_hybrid' in data else fields_to_update
        fields_to_update.update({"CWtp": data['co2_wltp']}) if 'co2_wltp' in data else fields_to_update
        fields_to_update.update({"ExSs": data['exclude_from_delivery_to_social_secretariat']}) if 'exclude_from_delivery_to_social_secretariat' in data else fields_to_update
        fields_to_update.update({"CaPa": data['vehicle_category']}) if 'vehicle_category' in data else fields_to_update
        fields_to_update.update({"UtWw": data['utility_residential_work']}) if 'utility_residential_work' in data else fields_to_update
        fields_to_update.update({"CoPa": data['co2_coefficient']}) if 'co2_coefficient' in data else fields_to_update
        fields_to_update.update({"KpPa": data['license_plate_country']}) if 'license_plate_country' in data else fields_to_update

        payload['HrMobility']['Element']['Fields'].update(fields_to_update)

        return requests.post(url, data=json.dumps(payload), headers=self.headers)

    def update_employee_car(self, data: dict) -> requests.Response:
        required_fields = ['employee_id', 'car_id', 'date_effective']
        allowed_fields = ['personal_contribution_private_use', 'personal_contribution_other_reason', 'end_date_contract', 'include_in_payroll',
                          'benefit_in_kind_percentage', 'benefit_in_kind_threshold_amount', 'benefit_in_kind_above_threshold_percentage']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)
        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrMobility/HrEmployeeMobility"

        payload = {
            "HrMobility": {
                "Element": {
                    "@CcSn": data['car_id'],
                    "Objects": [
                        {
                            "HrEmployeeMobility": {
                                "Element": {
                                    "@EmId": data['employee_id'],
                                    "Fields": {
                                        "DaEf": data['date_effective']
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }

        # Add allowed fields to the payload if they are present in the data
        fields_to_update = {}
        fields_to_update.update({"OwCo": data['personal_contribution_private_use']}) if 'personal_contribution_private_use' in data else fields_to_update
        fields_to_update.update({"OwAn": data['personal_contribution_other_reason']}) if 'personal_contribution_other_reason' in data else fields_to_update
        fields_to_update.update({"DaEn": data['end_date_contract']}) if 'end_date_contract' in data else fields_to_update
        fields_to_update.update({"PaVr": data['include_in_payroll']}) if 'include_in_payroll' in data else fields_to_update
        fields_to_update.update({"PeAd": data['benefit_in_kind_percentage']}) if 'benefit_in_kind_percentage' in data else fields_to_update
        fields_to_update.update({"AdLi": data['benefit_in_kind_threshold_amount']}) if 'benefit_in_kind_threshold_amount' in data else fields_to_update
        fields_to_update.update({"HiAd": data['benefit_in_kind_above_threshold_percentage']}) if 'benefit_in_kind_above_threshold_percentage' in data else fields_to_update
        payload['HrMobility']['Element']['Objects'][0]['HrEmployeeMobility']['Element']['Fields'].update(fields_to_update)

        return requests.post(url, data=json.dumps(payload), headers=self.headers)

    def update_deviating_tax_agency(self, data: dict) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        # Check if the person already exist and only needs to be linked to the new employee. Other option is to create the person together with the employee
        required_fields = ['employee_id', 'employment_id']
        allowed_fields = ['income_relationship_type', 'nature_of_employment', 'table_colour', 'table_code', 'zvw_code', 'zw', 'ww', 'wia', 'risk_group_sector_diff', 'on_call_with']

        # Check if there are fields that are not allowed or fields missing that are required
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'HrDvb')

        body = {
            "HrDvb": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "@DvSn": data['employment_id'],
                    "Fields": {
                        "AgEx": 'true'
                    }
                }
            }
        }

        fields_to_update = {}
        fields_to_update.update({"ViIn": data['income_relationship_type']}) if 'income_relationship_type' in data else fields_to_update
        fields_to_update.update({"ViEm": data['nature_of_employment']}) if 'nature_of_employment' in data else fields_to_update
        fields_to_update.update({"ViTs": data['table_colour']}) if 'table_colour' in data else fields_to_update
        fields_to_update.update({"ViCd": data['table_code']}) if 'table_code' in data else fields_to_update
        fields_to_update.update({"ViZv": data['zvw_code']}) if 'zvw_code' in data else fields_to_update
        fields_to_update.update({"YnZW": data['zw']}) if 'zw' in data else fields_to_update
        fields_to_update.update({"YnWW": data['ww']}) if 'ww' in data else fields_to_update
        fields_to_update.update({"YWAO": data['wia']}) if 'wia' in data else fields_to_update
        fields_to_update.update({"ViRi": data['risk_group_sector_diff']}) if 'risk_group_sector_diff' in data else fields_to_update
        fields_to_update.update({"TxGn": data['on_call_with']}) if 'on_call_with' in data else fields_to_update

        body['HrDvb']['Element']['Fields'].update(fields_to_update)

        if self.debug:
            print(json.dumps(body))

        update = requests.request('PUT', url, data=json.dumps(body), headers=self.headers, timeout=60)

        return update


    def create_sickleave(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: status code for request and optional error message
        """

        allowed_fields = {
            'safety_net': 'SfNt',
            'end_date': 'DaEn',
            'end_date_report_date': 'DMeE',
            'reason_ending': 'ViRs',
            'end_date_expected': 'DaEs',
            'available_first_day': 'TPBe',
            'total_hours': 'ThAb'
        }
        required_fields = ['employee_id', 'start_date', 'start_date_report_date', 'type_of_sickleave', 'percentage_available']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=list(allowed_fields.keys()))

        base_body = {
            "HrIllness": {
                "Element": {
                    "Fields": {
                        "EmId": f"{data['employee_id']}",
                        "DaBe": f"{data['start_date']}",
                        "DMeB": f"{data['start_date_report_date']}",
                        "ViIt": f"{data['type_of_sickleave']}"
                    },
                    "Objects": [
                        {
                            "HrAbsIllnessProgress": {
                                "Element": {
                                    "Fields": {
                                        "DaTi": f"{data['start_date']}",
                                        "PsPc": f"{data['percentage_available']}"
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            base_body['HrIllness']['Element']['Fields'].update({allowed_fields[field]: data[field]})

        # Add custom fields to the body
        base_body['HrIllness']['Element']['Fields'].update(overload_fields) if overload_fields is not None else ''

        update = requests.post(url=f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrIllness', data=json.dumps(base_body), headers=self.headers)

        return update

    def update_sickleave(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: status code for request and optional error message
        """
        allowed_fields = {
            'safety_net': 'SfNt',
            'end_date': 'DaEn',
            'end_date_report_date': 'DMeE',
            'reason_ending': 'ViRs',
            'start_date': 'DaBe',
            'start_date_report_date': 'DMeB',
            'end_date_expected': 'DaEs',
            'available_first_day': 'TPBe',
            'type_of_sickleave': 'ViIt',
            'total_hours': 'ThAb'
        }
        allowed_fields_progress = {
            'guid_sickleave_progress': '@GUID',
            'date_time_sickleave_progress': 'DaTi',
            'percentage_sickleave_progress': 'PsPc',
            'comment_sickleave_progress': 'Re'
        }
        required_fields = ['guid']

        total_fields_list = list(allowed_fields.keys()) + list(allowed_fields_progress.keys())
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=total_fields_list)

        base_body = {
            "HrIllnessGUID": {
                "Element": {
                    "@GUID": f"{data['guid']}",
                    "Fields": {
                    }
                }
            }
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            base_body['HrIllnessGUID']['Element']['Fields'].update({allowed_fields[field]: data[field]})

        # Add allowed fields to the body for progress
        # add the object to the body if there is a field in allowed_fields_progress
        if 'guid_sickleave_progress' in data.keys():
            base_body['HrIllnessGUID']['Element']['Objects'] = [
                {
                    "HrAbsIllnessProgress": {
                        "Element": {
                            "Fields": {}
                        }
                    }
                }
            ]
        for field in (allowed_fields_progress.keys() & data.keys()):
            if field == 'guid_sickleave_progress':
                base_body['HrIllnessGUID']['Element']['Objects'][0]['HrAbsIllnessProgress']['Element'].update({allowed_fields_progress[field]: data[field]})
            else:
                base_body['HrIllnessGUID']['Element']['Objects'][0]['HrAbsIllnessProgress']['Element']['Fields'].update({allowed_fields_progress[field]: data[field]})

        # Add custom fields to the body
        base_body['HrIllnessGUID']['Element']['Fields'].update(overload_fields) if overload_fields is not None else ''

        response = requests.put(url=f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrIllnessGUID',
                                data=json.dumps(base_body), headers=self.headers)

        return response

    def delete_sickleave(self, sickleave_guid: Union[int, str]) -> requests.Response:
        response = requests.delete(url=f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrIllnessGUID/HrIllnessGUID/@GUID/{sickleave_guid}",
                                   headers=self.headers)
        return response

    def create_leave(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Custom Fields with custom ID's can be entered here with key: value
        :return: status code for request and optional error message
        """
        allowed_fields = {
            'total_hours': "DuRa",
            'partial_leave': "LeDt",
            'employment_id': "EnSe",
            'reason_of_leave': "ViLr",
            'leave_id': "Id"
        }
        required_fields = ['employee_id', 'start_date', 'end_date', 'type_of_leave']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=list(allowed_fields.keys()))

        base_body = {
            "HrAbsence": {
                "Element": {
                    "Fields": {
                        "EmId": data["employee_id"],
                        "ViAt": data["type_of_leave"],
                        "DaBe": data["start_date"],
                        "DaEn": data["end_date"]
                    }
                }
            }
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            base_body['HrAbsence']['Element']['Fields'].update({allowed_fields[field]: data[field]})

        # Add custom fields to the body
        base_body['HrAbsence']['Element']['Fields'].update(overload_fields) if overload_fields is not None else ''

        response = requests.post(url=f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrAbsence',
                                 data=json.dumps(base_body), headers=self.headers)

        return response

    def update_leave(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Custom Fields with custom ID's can be entered here with key: value
        :return: status code for request and optional error message
        """
        allowed_fields = {
            "total_hours": "DuRa",
            "partial_leave": "LeDt",
            "employment_id": "EnSe",
            "reason_of_leave": "ViLr",
            "leave_id": "Id",
            "employee_id": "EmId",
            "type_of_leave": "ViAt",
            "start_date": "DaBe",
            "end_date": "DaEn"
        }
        required_fields = ['leave_id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=list(allowed_fields.keys()))

        base_body = {
            "HrAbsenceID": {
                "Element": {
                    "Fields": {
                        "Id": data["leave_id"]
                    }
                }
            }
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            base_body['HrAbsenceID']['Element']['Fields'].update({allowed_fields[field]: data[field]})

        # Add custom fields to the body
        base_body['HrAbsenceID']['Element']['Fields'].update(overload_fields) if overload_fields is not None else ''

        response = requests.put(url=f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrAbsenceID',
                                data=json.dumps(base_body),
                                headers=self.headers)

        return response

    def delete_leave(self, leave_id: Union[int, str]) -> requests.Response:
        """
        method used to delete leave from AFAS
        :param leave_id: leave id, may be a string or number
        :return: response object
        """
        response = requests.delete(url=f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrAbsenceID/HrAbsenceID/Id/{leave_id}",
                                   headers=self.headers)

        return response

    def create_leave_balance(self, data: dict, overload_fields: dict = None) -> requests.Response:
        # has to be implemented still. Different endpoint then leave balance corrections
        pass

    def update_leave_balance(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Custom Fields with custom ID's can be entered here with key: value
        :return: status code for request and optional error message
        """
        allowed_fields = {
            "correction_reason": "ViCr",
            "booking_date": "RgDa",
            "employment_id": "EnSe",
            "note": "Re",
            "process_in_payroll": "CcPy",
            "leave_balance": "BlId",
            "weeks": "CoWk"
        }
        required_fields = ['employee_id', 'type_of_leave', 'hours']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=list(allowed_fields.keys()))

        base_body = {
            "HrAbsCorrection": {
                "Element": {
                    "Fields": {
                        "EmId": data["employee_id"],
                        "ViAt": data["type_of_leave"],
                        "HhMm": data["hours"]
                    }
                }
            }
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            base_body['HrAbsCorrection']['Element']['Fields'].update({allowed_fields[field]: data[field]})

        # Add custom fields to the body
        base_body['HrAbsCorrection']['Element']['Fields'].update(overload_fields) if overload_fields is not None else ''

        response = requests.post(url=f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrAbsCorrection',
                                 data=json.dumps(base_body),
                                 headers=self.headers)

        return response

    def create_post_calculation(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Custom Fields with custom ID's can be entered here with key: value
        :return: status code for request and optional error message
        """
        allowed_fields = {
            'id': "Id",
            'external_key': "XpRe",
            'quantity': "Qu",
            'employee_id': "EmId",
            'type_of_hours': "StId",
            "costcenter_employee": "CrId",
            "approved": "Ap",
            "description": "Ds",
            "project_id": "PrId",
            "project_phase": "PrSt",
            "specification_axis_code_1": "V1Cd",
            "specification_axis_code_2": "V2Cd",
            "specification_axis_code_3": "V3Cd",
            "specification_axis_code_4": "V4Cd",
            "specification_axis_code_5": "V5Cd"
        }
        required_fields = ['date', 'item_type', 'item_code']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=list(allowed_fields.keys()))

        base_body = {
            "PtRealization": {
                "Element": {
                    "Fields": {
                        "DaTi": data["date"],
                        "VaIt": data["item_type"],
                        "ItCd": data["item_code"]
                    }
                }
            }
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            base_body['PtRealization']['Element']['Fields'].update({allowed_fields[field]: data[field]})

        # Add custom fields to the body
        base_body['PtRealization']['Element']['Fields'].update(overload_fields) if overload_fields is not None else ''

        response = requests.post(url=f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/PtRealization',
                                 data=json.dumps(base_body), headers=self.headers)

        return response

    def update_post_calculation(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: Custom Fields with custom ID's can be entered here with key: value
        :return: status code for request and optional error message
        """
        allowed_fields = {
            'external_key': "XpRe",
            'quantity': "Qu",
            'employee_id': "EmId",
            'type_of_hours': "StId",
            'date': "DaTi",
            'item_type': "VaIt",
            'item_code': "ItCd",
            "costcenter_employee": "CrId",
            "approved": "Ap",
            "description": "Ds",
            "project_id": "PrId",
            "project_phase": "PrSt",
            "specification_axis_code_1": "V1Cd",
            "specification_axis_code_2": "V2Cd",
            "specification_axis_code_3": "V3Cd",
            "specification_axis_code_4": "V4Cd",
            "specification_axis_code_5": "V5Cd"
        }
        required_fields = ['id']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=list(allowed_fields.keys()))

        base_body = {
            "PtRealization": {
                "Element": {
                    "Fields": {
                        "Id": data["id"]
                    }
                }
            }
        }

        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            base_body['PtRealization']['Element']['Fields'].update({allowed_fields[field]: data[field]})

        # Add custom fields to the body
        base_body['PtRealization']['Element']['Fields'].update(overload_fields) if overload_fields is not None else ''

        response = requests.put(url=f'https://{self.environment}.{self.base_url}/profitrestservices/connectors/PtRealization',
                                data=json.dumps(base_body),
                                headers=self.headers)

        return response

    def delete_post_calculation(self, post_calculation_id: Union[int, str], date: str) -> requests.Response:
        """
        method used to delete postcalculation from AFAS
        :param post_calculation_id: post_calculation_id id, may be a string or number
        :param date: date, must be yyyy-mm-dd, is DaTi from original booking
        :return: response object
        """
        response = requests.delete(url=f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/PtRealization/PtRealization/Id,DaTi/{post_calculation_id},{date}",
                                   headers=self.headers)

        return response

    def update_cost_center(self, data: dict, method: str, custom_fields: dict = None) -> requests.Response:
        """
        This function updates HR cost centers with the AFAS updateconnect 'HrCosteCentre'.
        :param data: Deliver all the data which should be updated in list format. The data should at least contain the required_fields and can contain also the allowed fields
        :param method: Is a PUT for an update of an existing cost center. is a POST for an insert of a new cost center
        :param custom_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: The status code from AFAS Profit
        """
        required_fields = ['cost_center_id', 'cost_center_description', 'employer_id', 'blocked']
        allowed_fields = ['cost_center_type']

        # Check if the fields in data exists in the required or allowed fields
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        if method != 'PUT' and method != 'POST' and method != 'DELETE':
            raise ValueError('Parameter method should be PUT, POST or DELETE (in uppercase)')

        # Do a delete call if the method is a delete. Delete do not need a body
        if method == 'DELETE':
            url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrCostCentre/HrCostCentre/CmId,CrId,CrDs,Bl/{data['employer_id']},{data['cost_center_id']},{data['cost_center_description']},{data['blocked']}"
            base_body = {}
        else:
            url = 'https://{}.{}/profitrestservices/connectors/HrCostCentre'.format(self.environment, self.base_url)

            base_body = {
                "HrCostCentre": {
                    "Element": {
                        "Fields": {
                            "CmId": data['employer_id'],
                            "CrId": data['cost_center_id'],
                            "CrDs": data['cost_center_description'],
                            "Bl": data['blocked']
                        }
                    }
                }
            }

            # Now create a dict for all the allowed fields. This fields are not by default added to the base_body because they're not always present in the dataset
            fields_to_update = {}
            fields_to_update.update({"CrTy": data['cost_center_type']}) if 'cost_center_type' in data else fields_to_update

            # Also add custom_fields to the base_body.
            fields_to_update.update(custom_fields) if custom_fields is not None else ''

            # Update the request body with update fields
            base_body['HrCostCentre']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def update_cost_carrier(self, data: dict, method: str, custom_fields: dict = None) -> requests.Response:
        """
        This function updates HR cost carriers with the AFAS updateconnect 'HrCosteCarrier'.
        :param data: Deliver all the data which should be updated in list format. The data should at least contain the required_fields and can contain also the allowed fields
        :param method: Is a PUT for an update of an existing cost carrier. is a POST for an insert of a new cost carrier
        :param custom_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: The status code from AFAS Profit
        """
        required_fields = ['cost_carrier_id', 'cost_carrier_description', 'employer_id', 'blocked']
        allowed_fields = []

        # Check if the fields in data exists in the required or allowed fields
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        if method != 'PUT' and method != 'POST' and method != 'DELETE':
            raise ValueError('Parameter method should be PUT, POST or DELETE (in uppercase)')

        if method == 'DELETE':
            url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrCostCarrier/HrCostCarrier/CmId,CcId,CcDs,Bl/{data['employer_id']},{data['cost_carrier_id']},{data['cost_carrier_description']},{data['blocked']}"
            base_body = {}
        else:
            url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'HrCostCarrier')

            base_body = {
                "HrCostCarrier": {
                    "Element": {
                        "Fields": {
                            "CmId": data['employer_id'],
                            "CcId": data['cost_carrier_id'],
                            "CcDs": data['cost_carrier_description'],
                            "Bl": data['blocked']
                        }
                    }
                }
            }

            # Now create a dict for all the custom fields. This fields are not by default added to the base_body because they're not always present in the dataset
            fields_to_update = {}
            fields_to_update.update(custom_fields) if custom_fields is not None else ''

            # Update the request body with update fields
            base_body['HrCostCarrier']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def terminate_employee(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: status code for request and optional error message
        """
        allowed_fields = ['termination_initiative', 'termination_reason', 'reason_end_of_employment']
        required_fields = ['employee_id', 'termination_date', 'end_date_contract', 'start_date_contract']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee')

        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "AfasContract": {
                            "Element": {
                                "@DaBe": data['start_date_contract'],
                                "Fields": {
                                    "DaEn": data['end_date_contract'],
                                    "DaEe": data['termination_date']
                                }
                            }
                        }
                    }
                }
            }
        }

        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"ViIe": data['termination_initiative']}) if 'termination_initiative' in data else fields_to_update
        fields_to_update.update({"ViRe": data['termination_reason']}) if 'termination_reason' in data else fields_to_update
        fields_to_update.update({"DvbViAo": data['reason_end_of_employment']}) if 'reason_end_of_employment' in data else fields_to_update
        fields_to_update.update(overload_fields) if overload_fields is not None else ''

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasContract']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=self.headers)

        return update

    def create_dossieritem_reaction(self, data: dict, attachments: dict = None) -> requests.Response:
        allowed_fields = {
            'reaction_to': 'RTId',
        }
        required_fields = ['dossieritem_id', 'reaction', 'reaction_visibility']

        required_fields_attachment = ['filename', 'attachment_filepath']
        allowed_fields_attachment = []

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=list(allowed_fields.keys()))

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnSubjectReaction"

        payload = {
            "KnReaction": {
                "Element": {
                    "Fields": {
                        "SbId": data['dossieritem_id'],  # Dossieritem ID
                        "SbTx": data['reaction'],  # reaction text
                        "VaRe": data['reaction_visibility']  # either I for Internal or IE for Internal and External
                    }
                }
            }
        }
        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['KnReaction']['Element']['Fields'].update({allowed_fields[field]: data[field]})

        if attachments is not None:
            attachment_basebody = {
                "Objects": [{
                    "KnReactionAttachment": {
                        "Element": []
                    }
                }]
            }

            for attachment in attachments:
                self.__check_fields(data=attachment, required_fields=required_fields_attachment, allowed_fields=allowed_fields_attachment)
                attachment_basebody['Objects'][0]['KnReactionAttachment']['Element'].append({"Fields": {"FileName": attachment['filename'],
                                                                                                        "FileStream": base64.b64encode(bytearray(open(attachment['attachment_filepath'], mode='rb').read())).decode("utf-8")
                                                                                                        }
                                                                                             })

            # now update main body with attachment body
            payload['KnReaction']['Element'].update(attachment_basebody)

        if self.debug:
            print(json.dumps(payload))

        update = requests.post(url, data=json.dumps(payload), headers=self.headers)

        return update

    def upload_dossieritem(self, data: dict, attachments: Union[List[dict], None] = None, overload_fields: List = None) -> requests.Response:
        """
        :param data: any fields that are in required and allowed_fields
        :param attachments: list of dicts that should each contain a filename and attachment_filepath
        :param overload_fields: list of dicts that should each contain a complete object for a free dossieritem. Example:
        [{
            "KnS15": {
                "Element": {
                    "@SbId": dossieritemId,
                    "Fields": {
                        "U51DC4BF14827261B10A2F69D9B460346": "value1",
                        "U5CAEF2DE4FD25D4E7AA8B99999969318": "value2",
                    }
                }
            }
        }]
        :return: response
        """
        allowed_fields = {
            'subject': 'Ds',
            'note': 'SbTx',
            'date_created': 'Da',
            'created_by': 'UsId',
            'person_responsible': 'EmId',
            'is_done': 'St',
            'property_1': 'FvF1',
            'property_2': 'FvF2',
            'property_3': 'FvF3',
            'save_file_with_subject': 'FileTrans',
            'profile_id': 'ProfileId'
        }
        allowed_fields_subject_link = {
            'sales_administration_id': "SiUn",
            'sales_invoice_type_id': "SiTp",
            'sales_invoice_id': "SiId",
            'purchase_administration_id': "PiUn",
            'purchase_invoice_type_id': "PiTp",
            'purchase_invoice_id': "PiId",
            'project_id': "PjId",
            'campaign_id': "CaId",
            'active': "FaSn",
            'precalculation_id': "QuId",
            'subscription_id': "SuNr",
            'item_type': "VaIt",
            'item_code': "BiId",
            'course_id': "CrId",
            'forecast_id': "FoSn",
            'car_id': "CcSn",
            'organizational_unit': "OE",
            'purchase_order_id': "Por",
            'sales_offer_id': "Squ",
            'sales_order_id': "Sor",
            'purchase_offer_id': "Pqu",
            'location_id': "LoId",
            'application_id': "ApId",
            "to_purchase_relation": "ToPR",
            "to_sales_relation": "ToSR",
            "to_applicant": "ToAp",
            "to_employee": "ToEm",
            "to_person": "ToBC",
            "absence_id": "AbId",
            "destination_type_id": "SfTp",
            # this field is a bit tricky. This is actually the destination, which mostly will be the employee ID
            # However it can also contain other IDs such as the purchase relation ID or the applicant ID.
            # It should never contain the person_id, that should go in the person_id field. This logic is very weird but thats how AFAS wants it
            "destination": "SfId",
            # Usually employee_id is used instead of destination, but if you want to use destination, you can use this field to specify the type of destination
            "employee_id": "SfId",
            "person_id": "BcId",
            "mobility_id": "CcSn"
        }
        required_fields = ['dossieritem_type_id']

        required_fields_attachment = ['filename', 'attachment_filepath']
        allowed_fields_attachment = []

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=list(allowed_fields.keys()))
        if "employee_id" not in data and "person_id" not in data:
            warnings.warn("Either employee_id or person_id should likely be specified")
        if "employee_id" in data and "destination" in data:
            raise ValueError("Either employee_id or destination should be specified, not both")

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnSubject"

        payload = {
            "KnSubject": {
                "Element": {
                    # "@SbId": id, # optional dossieritem ID
                    "Fields": {
                        "StId": data['dossieritem_type_id'],  # Dossieritem type
                        "Ds": data['subject'] if 'subject' in data else data['filename'],  # this is for legacy reasons, used to be same as filename
                    },
                    "Objects": [
                        {
                            "KnSubjectLink": {
                                "Element": {
                                    # "@SbId": id, # optional dossieritem ID
                                    "Fields": {
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }
        # Add allowed fields to the body
        for field in (allowed_fields.keys() & data.keys()):
            payload['KnSubject']['Element']['Fields'].update({allowed_fields[field]: data[field]})

        # Add allowed fields to the body
        for field in (allowed_fields_subject_link.keys() & data.keys()):
            payload['KnSubject']['Element']['Objects'][0]['KnSubjectLink']['Element']['Fields'].update({allowed_fields_subject_link[field]: data[field]})

        # check if the attachments parameter is specified, if not, use the legacy way (does not support multiple attachments)
        if attachments is None and 'filename' in data and 'attachment_filepath' in data:
            attachments = [{"filename": data['filename'],
                            "attachment_filepath": data['attachment_filepath']}]
        elif attachments is None:
            attachments = []

        # add overload objects to  the body (custom dossieritems)
        for dossieritem in overload_fields:
            payload['KnSubject']['Element']['Objects'].append(dossieritem)

        attachment_body = {
            "KnSubjectAttachment": {
                "Element": []
            }
        }
        for attachment in attachments:
            self.__check_fields(data=attachment, required_fields=required_fields_attachment, allowed_fields=allowed_fields_attachment)
            attachment_body["KnSubjectAttachment"]["Element"].append({
                "Fields": {
                    "FileName": attachment['filename'],
                    "FileStream": base64.b64encode(bytearray(open(attachment['attachment_filepath'], mode='rb').read())).decode("utf-8")
                }
            })
        payload['KnSubject']['Element']['Objects'].append(attachment_body)

        if self.debug:
            print(json.dumps(payload))

        update = requests.post(url, data=json.dumps(payload), headers=self.headers)

        return update

    def create_journalentries(self, df: pd.DataFrame):
        """
        This function can be used to upload journalentries to Afas profit
        :param df: The dataframe with the journal entries of a certain administration id specified.
        :return: upload_summary containing a string with information about the upload
        :return: status_codes containing the status codes corresponding to the upload_summary
        """
        # Check if all necessary columns are present
        columns_in_df = df.columns.tolist()
        required_fields_financial_entry = ['general_ledger_id', 'cost_centre_id', 'description', 'date_approved', 'date_booking', 'booking_number', 'debet', 'credit', 'year', 'period', 'administration_id', 'journal_id']
        self.__check_fields(data=columns_in_df, required_fields=required_fields_financial_entry, allowed_fields=[])

        upload_summary = []
        status_codes = []  # extract all period and year data as a list and drop duplicates from the list
        df['unique_period_year_per_administration'] = df['period'].astype(str) + df['year'].astype(str) + df['administration_id'].astype(str) + df['journal_id'].astype(str)
        year_period_per_administration_list = df['unique_period_year_per_administration'].unique().tolist()
        for unique_period in year_period_per_administration_list:
            df_period = df[df['unique_period_year_per_administration'] == unique_period]
            # drop the columns that are not needed for the upload iteration
            df_period = df_period.sort_values(by=['booking_number', 'date_booking'])
            # pass the index payload and the dataframe to the upload method
            # reset the index of the dataframe
            df_period = df_period.reset_index(drop=True)
            update = self.__create_journalentry_for_period(df=df_period)
            json_update = update.json()
            if 200 <= update.status_code < 300:
                upload_summary.append(f"Journal entries for year {df_period.iloc[0]['year']}, period {df_period.iloc[0]['period']}, adminstration {df_period.iloc[0]['administration_id']} and journal {df_period.iloc[0]['journal_id']} uploaded successfully. Status code: {update.status_code}")
                status_codes.append(update.status_code)
            else:
                upload_summary.append(f"Journal entries for year {df_period.iloc[0]['year']}, period {df_period.iloc[0]['period']}, adminstration {df_period.iloc[0]['administration_id']} and journal {df_period.iloc[0]['journal_id']} failed. Status code: {update.status_code} {json_update['externalMessage']}")
                status_codes.append(update.status_code)

        return upload_summary, status_codes

    def __create_journalentry_for_period(self, df: pd.DataFrame) -> requests.Response:
        """
        This function is an internal function used in conjunction with upload_journalentries. This function updates Afas profit for updateconnector: 'Fientries'.
        :param df: The dataframe with the journal entries for the year period and administration id specified in the data. This dataframe needs debit and credit values that equal out per booking number.
        :return: The response from AFAS Profit
        """
        base_body = {
            "FiEntryPar": {
                "Element": {
                    "Fields": {
                        "Year": df.iloc[0]['year'],
                        "Peri": df.iloc[0]["period"],
                        "UnId": df.iloc[0]['administration_id'],
                        "JoCo": df.iloc[0]['journal_id']
                    },
                    "Objects": [
                        {
                            "FiEntries": {
                                "Element": []
                            }
                        }
                    ]
                }
            }
        }
        for row in df.to_dict(orient='records'):
            single_entry = {
                "Fields": {
                    "VaAs": "1",
                    "AcNr": row["general_ledger_id"],
                    "EnDa": row['date_booking'],
                    "BpDa": row['date_approved'],
                    "BpNr": row['booking_number'],
                    "Ds": row['description'],
                    "AmDe": row['debet'],
                    "AmCr": row['credit']
                },
                "Objects": [
                    {
                        "FiDimEntries": {
                            "Element": {
                                "Fields": {
                                    "DiC1": row['cost_centre_id'],
                                    "DiC2": row['cost_carrier_id']
                                }
                            }
                        }
                    }
                ]
            }
            base_body['FiEntryPar']["Element"]["Objects"][0]["FiEntries"]["Element"].append(single_entry)

        json_body = json.dumps(base_body)
        update = requests.request("POST", url=f'https://{self.environment}.{self.base_url}/ProfitRestServices/connectors/FiEntries', data=json_body, headers=self.headers)

        return update

    def update_applicant(self, data: dict, method: str, overload_fields: dict = None) -> requests.Response:
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :param method: Method to be used in update function
        :param overload_fields: overload_fields: The custom fields in this dataset. Give the key of the field and the value. For example: {DFEDS8-DSF9uD-DDSA: 'Vrij veld'}
        :return: status code for request and optional error message
        """
        required_fields = ['last_name', 'gender', 'application_number']
        allowed_fields = ['initials', 'first_name', 'date_of_birth', 'email', 'mobile_phone', 'country', 'street', 'housenumber',
                          'housenumber_addition', 'postal_code', 'city', 'site_guid', 'work_email', 'person_id']

        # Check if the fields in data exists in the required or allowed fields
        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        if method != 'PUT' and method != 'POST':
            raise ValueError('Parameter method should be PUT or POST (in uppercase)')

        if method == 'DELETE':
            raise ValueError('Parameter method should NOT be DELETE')
        else:
            url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'HrCreateApplicant')

            base_body = {
                "HrCreateApplicant": {
                    "Element": {
                        "Fields": {
                            "VcSn": data['application_number'],
                            "LaNm": data['last_name'],  # prefix incorporated
                            "ViGe": data['gender']  # M, O, V of X
                        }
                    }
                }
            }

            # Add allowed fields to the basebody if they are available in the data. Fields that are not exists in the basebody, should not be added tot this basebody to prevent errors.
            fields_to_update = {}
            fields_to_update.update({"In": data['initials']}) if 'initials' in data else fields_to_update  # initials, afleiden van de naam
            fields_to_update.update({"FiNm": data['first_name']}) if 'first_name' in data else fields_to_update  # first name
            fields_to_update.update({"DaBi": data['date_of_birth']}) if 'date_of_birth' in data else fields_to_update  # "YYYY-MM-DD", date of birth
            fields_to_update.update({"EmA2": data['email']}) if 'email' in data else fields_to_update  # private email
            fields_to_update.update({"EmAd": data['work_email']}) if 'work_email' in data else fields_to_update  # private email
            fields_to_update.update({"MbN2": data['mobile_phone']}) if 'mobile_phone' in data else fields_to_update  # private mobile phone
            fields_to_update.update({"CoId": data['country']}) if 'country' in data else fields_to_update  # country, default at Stibbe is NL
            fields_to_update.update({"Ad": data['street']}) if 'street' in data else fields_to_update
            fields_to_update.update({"HmNr": data['housenumber']}) if 'housenumber' in data else fields_to_update
            fields_to_update.update({"HmAd": data['housenumber_addition']}) if 'housenumber_addition' in data else fields_to_update
            fields_to_update.update({"ZpCd": data['postal_code']}) if 'postal_code' in data else fields_to_update
            fields_to_update.update({"Rs": data['city']}) if 'city' in data else fields_to_update
            fields_to_update.update({"StId": data['site_guid']}) if 'site_guid' in data else fields_to_update
            fields_to_update.update({"BcCo": data['person_id']}) if 'person_id' in data else fields_to_update

            base_body['HrCreateApplicant']['Element']['Fields'].update(fields_to_update)

            # Now create a dict for all the custom fields. This fields are not by default added to the base_body because they're not always present in the dataset
            fields_to_update = {}
            fields_to_update.update(overload_fields) if overload_fields is not None else ''

            # Update the request body with possibly extra fields as defined in the script
            base_body['HrCreateApplicant']['Element']['Fields'].update(fields_to_update)

        update = requests.request(method, url, data=json.dumps(base_body), headers=self.headers)

        return update

    def upload_payslip(self, data: dict) -> requests.Response:
        """
        This method is for uploading payslip dossieritems on the internal AFAS dossieritem type (-2).
        :param data:
        :return:
        """
        allowed_fields = []
        required_fields = ['filename', 'subject', 'employee_id', 'attachment_filepath']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/HrEmpPaySlip"

        payload = {
            "HrEmpPaySlip": {
                "Element": {
                    "Fields": {
                        "EmId": data['employee_id'],
                        "Ds": data['subject'],
                        "FileName": data['filename'],
                        "FileStream": base64.b64encode(bytearray(open(data['attachment_filepath'], mode='rb').read())).decode("utf-8")
                    }
                }
            }
        }

        response = requests.post(url, data=json.dumps(payload), headers=self.headers)

        return response

    def create_organisational_unit(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        This method is for creating organisational units in AFAS.
        """
        allowed_fields = ['reporting_unit', 'manager', 'cockpit_1', 'cockpit_2', 'cockpit_3', 'cockpit_4', 'cockpit_5']
        required_fields = ['organisational_unit_id', 'organisational_unit_description', 'staff', 'contains_employees', 'reports_to_unit_above']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnOrgUnit"

        payload = {
            "KnOrgunit": {
                "Element": {
                    "@OuId": data['organisational_unit_id'],
                    "Fields": {
                        "Ds": data['organisational_unit_description'],
                        "OTId": data['organisational_unit_type_id'],
                        "StUn": data['staff'],
                        "Empl": data['contains_employees'],
                        "RpOu": data['reports_to_unit_above']
                    }
                }
            }
        }

        # Add allowed fields to the payload if they are present in the data
        fields_to_update = {}
        fields_to_update.update({"ReOu": data['reporting_unit']}) if 'reporting_unit' in data else fields_to_update
        fields_to_update.update({"MaId": data['manager']}) if 'manager' in data else fields_to_update
        fields_to_update.update({"Cpt1": data['cockpit_1']}) if 'cockpit_1' in data else fields_to_update
        fields_to_update.update({"Cpt2": data['cockpit_2']}) if 'cockpit_2' in data else fields_to_update
        fields_to_update.update({"Cpt3": data['cockpit_3']}) if 'cockpit_3' in data else fields_to_update
        fields_to_update.update({"Cpt4": data['cockpit_4']}) if 'cockpit_4' in data else fields_to_update
        fields_to_update.update({"Cpt5": data['cockpit_5']}) if 'cockpit_5' in data else fields_to_update
        payload['KnOrgunit']['Element']['Fields'].update(fields_to_update)

        # Now create a dict for all the custom fields. This fields are not by default added to the base_body because they're not always present in the dataset
        fields_to_update = {}
        fields_to_update.update(overload_fields) if overload_fields is not None else ''
        payload['KnOrgunit']['Element']['Fields'].update(fields_to_update)

        return requests.post(url, data=json.dumps(payload), headers=self.headers)

    def update_organisational_unit(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        This method is for creating organisational units in AFAS.
        """
        allowed_fields = ['reporting_unit', 'manager', 'cockpit_1', 'cockpit_2', 'cockpit_3', 'cockpit_4', 'cockpit_5']
        required_fields = ['organisational_unit_id', 'organisational_unit_description', 'staff', 'contains_employees', 'reports_to_unit_above']

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)

        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnOrgUnit"

        payload = {
            "KnOrgunit": {
                "Element": {
                    "@OuId": data['organisational_unit_id'],
                    "Fields": {
                        "Ds": data['organisational_unit_description'],
                        "OTId": data['organisational_unit_type_id'],
                        "StUn": data['staff'],
                        "Empl": data['contains_employees'],
                        "RpOu": data['reports_to_unit_above']
                    }
                }
            }
        }

        # Add allowed fields to the payload if they are present in the data
        fields_to_update = {}
        fields_to_update.update({"ReOu": data['reporting_unit']}) if 'reporting_unit' in data else fields_to_update
        fields_to_update.update({"MaId": data['manager']}) if 'manager' in data else fields_to_update
        fields_to_update.update({"Cpt1": data['cockpit_1']}) if 'cockpit_1' in data else fields_to_update
        fields_to_update.update({"Cpt2": data['cockpit_2']}) if 'cockpit_2' in data else fields_to_update
        fields_to_update.update({"Cpt3": data['cockpit_3']}) if 'cockpit_3' in data else fields_to_update
        fields_to_update.update({"Cpt4": data['cockpit_4']}) if 'cockpit_4' in data else fields_to_update
        fields_to_update.update({"Cpt5": data['cockpit_5']}) if 'cockpit_5' in data else fields_to_update
        payload['KnOrgunit']['Element']['Fields'].update(fields_to_update)

        # Now create a dict for all the custom fields. This fields are not by default added to the base_body because they're not always present in the dataset
        fields_to_update = {}
        fields_to_update.update(overload_fields) if overload_fields is not None else ''
        payload['KnOrgunit']['Element']['Fields'].update(fields_to_update)

        return requests.put(url, data=json.dumps(payload), headers=self.headers)

    def update_agencies(self, data: dict) -> requests.Response:
        """
        This method is for updating agencies in AFAS.
        """
        required_fields = ['employee_id', 'agency_id', 'start_date']
        allowed_fields = ['end_date', "instantie", "einddatum", "soort_inkomstenverhouding", "aard_arbeidsverhouding", "tabelkleur", "tabelcode", "loonheffingskorting",
                          "zvw", "zw", "ww", "wao_wia", "ufo", "afwijkende_sector_risicogroep", "afwijkende_cbs_cao", "vakantiebonnen", "reden_geen_bijtelling_auto",
                          "studenten_en_scholierenregeling", "vervoer_vanwege_inhoudingsplichtige", "zelfstandige_binnenschipper", "huispersoneel_en_of_meewerkende_kinderen",
                          "echtgenoot_of_familie_van_eigenaar_dga", "vorige_eigenaar", "directeur_grootaandeelhouder", "oproep_invalkracht_zonder_verplichting", "oproep_invalkracht_met_verplichting",
                          "aow_uitkering_voor_alleenstaanden", "wajong_uitkering", "doorbetaler_i_v_m_doorbetaaldloonregeling", "gemoedsbezwaard", "premievrijstelling_marginale_arbeid",
                          "no_riskpolis", "lkv_arbeidsgehandicapte_werknemer", "lkv_banenafspraak_scholingsbelemmerden", "lkv_herplaatsen_arbeidsgehandicapte_werknemer", "bronheffing_buitenland",
                          "einddatum_loonkostenvoordeel", "lkv_oudere_werknemer", "afwijkend_woonland", "ww_herzien", "cao_code_inlener", "toepassing_dagtabel"]

        self.__check_fields(data=data, required_fields=required_fields, allowed_fields=allowed_fields)
        url = f"https://{self.environment}.{self.base_url}/profitrestservices/connectors/KnEmployee/AfasAgencyFiscus"

        payload = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": [
                        {
                            "AfasAgencyFiscus": {
                                "Element": {
                                    "@DaBe": data['start_date'],
                                    "@AyId": data['agency_id'],
                                    "Fields": {

                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }

        # Add allowed fields to the payload if they are present in the data
        fields_to_update = {}
        fields_to_update.update({"ViIn": data['soort_inkomstenverhouding']}) if 'soort_inkomstenverhouding' in data else fields_to_update
        fields_to_update.update({"ViEm": data['aard_arbeidsverhouding']}) if 'aard_arbeidsverhouding' in data else fields_to_update
        fields_to_update.update({"ViTs": data['tabelkleur']}) if 'tabelkleur' in data else fields_to_update
        fields_to_update.update({"ViCd": data['tabelcode']}) if 'tabelcode' in data else fields_to_update
        fields_to_update.update({"ViLk": data['loonheffingskorting']}) if 'loonheffingskorting' in data else fields_to_update
        fields_to_update.update({"ViZv": data['zvw']}) if 'zvw' in data else fields_to_update
        fields_to_update.update({"YnZW": data['zw']}) if 'zw' in data else fields_to_update
        fields_to_update.update({"YnWW": data['ww']}) if 'ww' in data else fields_to_update
        fields_to_update.update({"YWAO": data['wao_wia']}) if 'wao_wia' in data else fields_to_update
        fields_to_update.update({"DoPs": data['ufo']}) if 'ufo' in data else fields_to_update
        fields_to_update.update({"ViRi": data['afwijkende_sector_risicogroep']}) if 'afwijkende_sector_risicogroep' in data else fields_to_update
        fields_to_update.update({"ViFc": data['afwijkende_cbs_cao']}) if 'afwijkende_cbs_cao' in data else fields_to_update
        fields_to_update.update({"ViVb": data['vakantiebonnen']}) if 'vakantiebonnen' in data else fields_to_update
        fields_to_update.update({"ViCx": data['reden_geen_bijtelling_auto']}) if 'reden_geen_bijtelling_auto' in data else fields_to_update
        fields_to_update.update({"TxF4": data['studenten_en_scholierenregeling']}) if 'studenten_en_scholierenregeling' in data else fields_to_update
        fields_to_update.update({"TrI": data['vervoer_vanwege_inhoudingsplichtige']}) if 'vervoer_vanwege_inhoudingsplichtige' in data else fields_to_update
        fields_to_update.update({"TxIs": data['zelfstandige_binnenschipper']}) if 'zelfstandige_binnenschipper' in data else fields_to_update
        fields_to_update.update({"TxHc": data['huispersoneel_en_of_meewerkende_kinderen']}) if 'huispersoneel_en_of_meewerkende_kinderen' in data else fields_to_update
        fields_to_update.update({"TxGf": data['echtgenoot_of_familie_van_eigenaar_dga']}) if 'echtgenoot_of_familie_van_eigenaar_dga' in data else fields_to_update
        fields_to_update.update({"TxGo": data['vorige_eigenaar']}) if 'vorige_eigenaar' in data else fields_to_update
        fields_to_update.update({"TxCs": data['directeur_grootaandeelhouder']}) if 'directeur_grootaandeelhouder' in data else fields_to_update
        fields_to_update.update({"TxGy": data['oproep_invalkracht_zonder_verplichting']}) if 'oproep_invalkracht_zonder_verplichting' in data else fields_to_update
        fields_to_update.update({"TxGn": data['oproep_invalkracht_met_verplichting']}) if 'oproep_invalkracht_met_verplichting' in data else fields_to_update
        fields_to_update.update({"TxAo": data['aow_uitkering_voor_alleenstaanden']}) if 'aow_uitkering_voor_alleenstaanden' in data else fields_to_update
        fields_to_update.update({"TxF5": data['wajong_uitkering']}) if 'wajong_uitkering' in data else fields_to_update
        fields_to_update.update({"Dblr": data['doorbetaler_i_v_m_doorbetaaldloonregeling']}) if 'doorbetaler_i_v_m_doorbetaaldloonregeling' in data else fields_to_update
        fields_to_update.update({"Cons": data['gemoedsbezwaard']}) if 'gemoedsbezwaard' in data else fields_to_update
        fields_to_update.update({"PMA": data['premievrijstelling_marginale_arbeid']}) if 'premievrijstelling_marginale_arbeid' in data else fields_to_update
        fields_to_update.update({"NRsk": data['no_riskpolis']}) if 'no_riskpolis' in data else fields_to_update
        fields_to_update.update({"PiAw": data['lkv_arbeidsgehandicapte_werknemer']}) if 'lkv_arbeidsgehandicapte_werknemer' in data else fields_to_update
        fields_to_update.update({"PkBa": data['lkv_banenafspraak_scholingsbelemmerden']}) if 'lkv_banenafspraak_scholingsbelemmerden' in data else fields_to_update
        fields_to_update.update({"PkHa": data['lkv_herplaatsen_arbeidsgehandicapte_werknemer']}) if 'lkv_herplaatsen_arbeidsgehandicapte_werknemer' in data else fields_to_update
        fields_to_update.update({"PkBc": data['bronheffing_buitenland']}) if 'bronheffing_buitenland' in data else fields_to_update
        fields_to_update.update({"DaEk": data['einddatum_loonkostenvoordeel']}) if 'einddatum_loonkostenvoordeel' in data else fields_to_update
        fields_to_update.update({"Lkvo": data['lkv_oudere_werknemer']}) if 'lkv_oudere_werknemer' in data else fields_to_update
        fields_to_update.update({"CoDi": data['afwijkend_woonland']}) if 'afwijkend_woonland' in data else fields_to_update
        fields_to_update.update({"WWHe": data['ww_herzien']}) if 'ww_herzien' in data else fields_to_update
        fields_to_update.update({"CAHi": data['cao_code_inlener']}) if 'cao_code_inlener' in data else fields_to_update
        fields_to_update.update({"TyDt": data['toepassing_dagtabel']}) if 'toepassing_dagtabel' in data else fields_to_update
        payload['AfasEmployee']['Element']['Objects'][0]['AfasAgencyFiscus']['Element']['Fields'].update(fields_to_update)

        return requests.put(url, data=json.dumps(payload), headers=self.headers)

    def post(self, rest_type, updateconnector, data) -> requests.Response:
        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, updateconnector)

        update = requests.request(rest_type, url, data=data, headers=self.headers)

        return update

    @staticmethod
    def __check_fields(data: Union[dict, List], required_fields: List, allowed_fields: List, either_or_fields: List = None):

        if isinstance(data, dict):
            data = data.keys()

        for field in data:
            if field not in allowed_fields and field not in required_fields:
                warnings.warn('Field {field} is not implemented. Optional fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields)))

        if either_or_fields is not None:
            # Check if at least one field from either_or_fields is present
            if isinstance(either_or_fields[0], list):
                # Handle case where either_or_fields is a list of lists
                for either_or_field_group in either_or_fields:
                    if not any(field in data for field in either_or_field_group):
                        raise ValueError('Either field {either_or_field} should be specified'.format(either_or_field=either_or_field_group))
            else:
                # Handle case where either_or_fields is a simple list of strings
                if not any(field in data for field in either_or_fields):
                    raise ValueError('Either field {either_or_field} should be specified'.format(either_or_field=either_or_fields))

        for field in required_fields:
            if field not in data:
                raise ValueError('Field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields)))
