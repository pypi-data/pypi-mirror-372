import asyncio
import pandas as pd
from typing import Optional
import requests

from .schemas.person import PersonGetSchema, PersonUpdateSchema, PersonCreateSchema

class Person:
    """Person management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize Person class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_url = f"{self.afas.base_url}/brynq_sdk_person"
        self.field_mapping = {
            "mail_work": "EmAd",
            "mail_private": "EmA2",
            "mobile_work": "MbNr",
            "mobile_private": "MbN2",
            "nickname": "CaNm",
            "first_name": "FiNm",
            "initials": "In",
            "prefix": "Is",
            "last_name": "LaNm",
            "prefix_birth_name": "IsBi",
            "personel_birth_name": "NmBi",
            "gender": "ViGe",
            "nationality": "PsNa",
            "birth_date": "DaBi",
            "country_of_birth": "RsBi",
            "ssn": "SoSe",
            "marital_status": "ViCs",
            "date_of_marriage": "DaMa",
            "date_of_divorce": "DaMa",
            "phone_work": "TeNr",
            "phone_private": "TeN2",
            "city_of_birth": "RsBi",
            "birth_name_separate": "SpNm",
            "name_use": "ViUs",
            "birthname_partner": "NmPa",
            "prefix_birthname_partner": "IsPa"
        }

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get person information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing person information

        Raises:
            Exception: If get person operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=PersonGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get person failed: {str(e)}") from e

    def __build_update_body(self, data, overload_fields: dict = None):
        base_body = {
            "KnPerson": {
                "Element": {
                    "Fields": {
                        "MatchPer": data.get("match_person", "0"),
                        "BcCo": data.get("person_id"),
                    }
                }
            }
        }

        person_fields = {}
        for key, value in data.items():
            if key in self.field_mapping and pd.notna(value) and value != "":
                person_fields[self.field_mapping[key]] = value
        person_fields["CaNm"] = data.get("first_name") # Call name.
        person_fields["NmBi"] = data.get("last_name") # Birth name.
        person_fields.update(overload_fields) if overload_fields is not None else ''

        # Update the base body with mapped fields
        base_body['KnPerson']['Element']['Fields'].update(person_fields)
        if "ssn" in data and pd.notna(data["ssn"]) and data["ssn"] != "":
            base_body['KnPerson']['Element']['Fields']["Sose"] = data['ssn']

        base_body["KnPerson"]["Element"]["Fields"].update({"PsNa": data["nationality"]})

        return base_body

    def update(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Update person information in AFAS

        Args:
            data: Dictionary containing person data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
            
        Raises:
            Exception: If validation or update fails
        """
        try:
            try:
                valid_data = PersonUpdateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")
            body = self.__build_update_body(data=valid_data, overload_fields=overload_fields)
            return self.afas.session.put(
                url=f"{self.afas.base_url}/KnPerson",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Person update failed: {str(e)}")

    def __build_create_body(self, data: dict):
        base_body = {
            "KnPerson": {
                "Element": {
                    "Fields": {
                        "AutoNum": data.get("auto_number", True),
                        "MatchPer": data.get("match_person", "7"),
                    }
                }
            }
        }

        # Map validated data to AFAS fields
        person_fields = {}
        for key, value in data.items():
            if key in self.field_mapping and pd.notna(value) and value != '':
                person_fields[self.field_mapping[key]] = value

        # Update base body with mapped fields
        base_body['KnPerson']['Element']['Fields'].update(person_fields)

        # Add SSN if available
        if "ssn" in data and pd.notna(data["ssn"]):
            base_body['KnPerson']['Element']['Fields']["Sose"] = data['ssn']
        # Add default contact role object
        base_body['KnPerson']['Element']['Objects'] = [{
            "KnContactAutRole": {
                "Element": {
                    "Fields": {
                        "AutRoleDs": data.get("contact_role", "Sollicitant")
                    }
                }
            }
        }]

        return base_body

    def create(self, data: dict) -> Optional[requests.Response]:
        """
        Create a new person in AFAS

        Args:
            data: Dictionary containing person data

        Returns:
            requests.Response: Response from AFAS API
            
        Raises:
            Exception: If validation or creation fails
        """
        try:
            try:
                valid_data = PersonCreateSchema(**data).model_dump()
                valid_data= self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")
            body = self.__build_create_body(valid_data)
            return self.afas.session.post(
                url=f"{self.afas.base_url}/KnPerson",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Person creation failed: {str(e)}")
