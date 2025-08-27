import asyncio
import pandas as pd
import requests

from .schemas.employee import (
    EmployeeUpdateSchema,
    EmployeeTerminateSchema,
    EmployeeCreateSchema,
    EmployeeGetSchema
)

from .family import Family
from .leaves import Leaves
from .sick_leaves import SickLeaves
from .address import Address
from .contract import Contract
from .functions import EmployeeFunction
from .salaries import Salaries
from .wage_mutations import WageMutations
from .wage_components import WageComponents
from .payslips import Payslips

class Employees:
    """Employee management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize Employees class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.address = Address(afas_connector)
        self.function = EmployeeFunction(afas_connector)
        self.contract = Contract(afas_connector)
        self.leaves = Leaves(afas_connector)
        self.sick_leaves = SickLeaves(afas_connector)
        self.salaries = Salaries(afas_connector)
        self.family = Family(afas_connector)
        self.payslips = Payslips(afas_connector)
        self.wage_components = WageComponents(afas_connector)
        self.wage_mutations = WageMutations(afas_connector)
        self.family = Family(afas_connector)
        self.get_url = f"{self.afas.base_url}/brynq_sdk_employee_actual_data"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get employee information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing employee information

        Raises:
            Exception: If get employee operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=EmployeeGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get employee failed: {str(e)}") from e

    def __build_req_body(self, data: dict) -> dict:
        try:
            base_body = {
                "AfasEmployee": {
                    "Element": {
                        "@EmId": data["employee_id"],
                        "Fields": {
                            "ViSe": data.get("employment_status", "I"),
                            "Bl": data.get("blocked", "0"),
                            "LgId": data.get("different_language", "001")
                        },
                        "Objects": [
                            {
                                "KnPerson": {
                                    "Element": {
                                        "Fields": {
                                            "BcCo": data.get("person_id"),
                                            "PadAdr": data.get("postal_address_applied", "1"),
                                            "AutoNum": data.get("auto_number", "0"),
                                            "MatchPer": data.get("match_person", "7"),
                                            "SeNm": data.get("last_name", ""),
                                            "CaNm": data.get("first_name", ""),
                                            "FiNm": data.get("first_name", ""),
                                            "Is": data.get("prefix", ""),
                                            "In": data.get("initials", ""),
                                            "LaNm": data.get("last_name", ""),
                                            "SpNm": data.get("birth_name_seperate", "1"),
                                            "NmBi": data.get("last_name", ""),
                                            "ViUs": data.get("name_usage", "0"),
                                            "ViGe": data.get("gender", ""),
                                            "DaBi": data.get("personal_birth_date", ""),
                                            "TtId": data.get("salutation", "")
                                        },
                                        "Objects": [
                                            {
                                                "KnBasicAddressAdr": {
                                                    "Element": {
                                                        "Fields": {
                                                            "CoId": self.afas.iso2_mapping.get(data.get("country"), ""),
                                                            "PbAd": data.get("postal_address_applied", "0"),
                                                            "StAd": data.get("street", ""),
                                                            "Ad": data.get("street", ""),
                                                            "HmNr": data.get("house_number", ""),
                                                            "HmAd": data.get("street_number_add", ""),
                                                            "ZpCd": data.get("postal_code", ""),
                                                            "Rs": data.get("city", ""),
                                                            "BeginDate": data.get("work_start_date", "")
                                                        }
                                                    }
                                                }
                                            },
                                            {
                                                "KnBasicAddressPad": {
                                                    "Element": {
                                                        "Fields": {
                                                            "CoId": self.afas.iso2_mapping.get(data.get("country"), ""),
                                                            "PbAd": data.get("postal_address_applied", "0"),
                                                            "StAd": data.get("street", ""),
                                                            "Ad": data.get("street", ""),
                                                            "HmNr": data.get("house_number", ""),
                                                            "ZpCd": data.get("postal_code", ""),
                                                            "Rs": data.get("city", ""),
                                                            "BeginDate": data.get("work_start_date", "")
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            return base_body
        except Exception as e:
            raise Exception("Build request body failed: " + str(e)) from e

    def create(self, data: dict) -> requests.Response:
        """
        Create employee in AFAS

        Args:
            data: Dictionary containing employee data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = EmployeeCreateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            base_body = self.__build_req_body(data=valid_data)
            return self.afas.session.post(
                url=f"{self.afas.base_url}/KnEmployee",
                json=base_body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Create Employee failed: {str(e)}") from e

    def __build_update_req_body(self, data: dict, overload_fields: dict) -> dict:
        try:
            base_body = {
                "AfasEmployee": {
                    "Element": {
                        "@EmId": data['employee_id'],
                        "Fields": {"LwRs": data["city_of_birth"]}
                    }
                }
            }
            if overload_fields:
                base_body['AfasEmployee']['Element']['Fields'].update(overload_fields)

            return base_body
        except Exception as e:
            raise Exception("Build request body failed: " + str(e)) from e

    def update(self, data: dict, overload_fields: dict = None) -> requests.Response:
        try:
            try:
                data = self.afas.validate(schema=EmployeeUpdateSchema, data=data)
            except Exception as e:
                raise ValueError("Data validation failed: " + str(e))

            body = self.__build_update_req_body(data=data, overload_fields=overload_fields)

            return self.afas.session.put(
                url=f"{self.afas.base_url}/KnEmployee",
                json=body,
                timeout=self.afas.timeout
            )

        except Exception as e:
            raise Exception(f"Employee update failed: {str(e)}")

    def delete(self, employee_id: str) -> requests.Response:
        """
        Delete an employee from AFAS
        
        Args:
            employee_id: The ID of the employee to delete
            
        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            url = f"{self.afas.base_url}/KnEmployee/AfasEmployee/@EmId/{employee_id}"
            return self.afas.session.delete(url, timeout=self.afas.timeout)
        except Exception as e:
            raise Exception(f"Delete employee failed: {str(e)}")

    def __build_terminate_body(self, data, overload_fields):
        try:
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
            fields_to_update.update(
                {"ViIe": data['termination_initiative']}) if 'termination_initiative' in data else fields_to_update
            fields_to_update.update(
                {"ViRe": data['termination_reason']}) if 'termination_reason' in data else fields_to_update
            fields_to_update.update(
                {"DvbViAo": data['reason_end_of_employment']}) if 'reason_end_of_employment' in data else fields_to_update
            fields_to_update.update(overload_fields) if overload_fields is not None else ''

            # Update the request body with update fields
            base_body['AfasEmployee']['Element']['Objects']['AfasContract']['Element']['Fields'].update(fields_to_update)
            return base_body
        except Exception as e:
            raise Exception("Build request body failed: " + str(e)) from e

    def terminate(self, data: dict, overload_fields: dict = None) -> requests.Response:
        """
        Terminate employee in AFAS

        Args:
            data: Dictionary containing termination data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                data = self.afas.validate(schema=EmployeeTerminateSchema, data=data)
                data = self.afas.convert_timestamp_columns(data)
            except Exception as e:
                raise ValueError(f"Data validation failed: {str(e)}")
            body = self.__build_terminate_body(data=data, overload_fields=overload_fields)

            return self.afas.session.put(
                url=f"{self.afas.base_url}/KnEmployee",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Employee terminate failed: {str(e)}")
