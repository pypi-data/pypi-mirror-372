import asyncio
import pandas as pd
from typing import Optional
import requests

from .schemas.leaves import SickLeaveCreateSchema, SickLeaveUpdateSchema, SickLeaveGetSchema

class SickLeaves:
    """Sick Leave management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize SickLeaves class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_sick_leaves_url = f"{self.afas.base_url}/brynq_sdk_absence"

    def __build_create_body(self, data, overload_fields:dict) -> dict:
        """
        Creates request body for creating sick leave

        Args:
            data: Dictionary containing sick leave data
            overload_fields: Optional custom fields

        Returns:
            dict: Request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
            base_body = {
                "HrIllness": {
                    "Element": {
                        "Fields": {
                            "EmId": f"{data['employee_id']}",
                            "DaBe": f"{data['start_date']}",
                            "ViRs":data.get('reason_for_closing',"1"),
                            "ViIt": data.get('absence_type_id',"S")
                        },
                        "Objects": [
                            {
                                "HrAbsIllnessProgress": {
                                    "Element": {
                                        "Fields": {
                                            "DaTi": f"{data['start_date']}",
                                        "PsPc": data.get('percentage_available',"")
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            # Sickleave fields mapping
            sickleave_mapping = {
                'safety_net': 'SfNt',
                'end_date': 'DaEn',
                'available_first_day': 'TPBe',
                'total_hours': 'ThAb'
           }

            # Add mapped fields
            sickleave_fields = {
                sickleave_mapping[key]: value
                for key, value in data.items()
                if key in sickleave_mapping
                   and pd.notna(value)
                   and value != ''
                   and value != 0
            }

            base_body['HrIllness']['Element']['Fields'].update(sickleave_fields)

            if overload_fields:
                base_body['HrIllness']['Element']['Fields'].update(overload_fields)

            return base_body
        except Exception as e:
            raise Exception(f"Build request body failed: {str(e)}")

    def __build_update_body(self, data, overload_fields) -> dict:
        """
        Creates request body for updating sick leave

        Args:
            data: Dictionary containing sick leave update data
            overload_fields: Optional custom fields

        Returns:
            dict: Request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
            base_body = {
                "HrIllnessGUID": {
                    "Element": {
                        "@GUID": data['guid'],
                        "Fields": {},
                        "Objects": {
                            "HrAbsIllnessProgress": {
                                "Element": {
                                    "@GUID": data['guid'],
                                    "Fields": {
                                        "DaTi": data['start_date'],
                                        "PsPc": data.get('percentage_available',""),
                                        "PsHr": data.get('hours_per_week_presence',"0"),
                                        "PsSp": data.get('specify_presence',"0")
                                    }
                                }
                            }
                        }
                    }
                }
            }

            # Sickleave fields mapping
            sickleave_mapping = {
                'safety_net': 'SfNt',
                'end_date': 'DaEn',
                'end_date_report_date': 'DMeE',
                'reason_ending': 'ViRs',
                'start_date': 'DaBe',
                'start_date_report_date': 'DMeB',
                'end_date_expected': 'DaEs',
                'available_first_day': 'TPBe',
                'type_of_leave': 'ViIt',
                'total_hours': 'ThAb'
            }

            sickleave_fields = {
                sickleave_mapping[key]: value
                for key, value in data.items()
                if key in sickleave_mapping
                   and pd.notna(value)
                   and value != ''
                   and key != 'guid'
            }

            if sickleave_fields:
                base_body['HrIllnessGUID']['Element']['Fields'].update(sickleave_fields)

            if overload_fields:
                non_empty_overloads = {
                    k: v for k, v in overload_fields.items()
                    if v is not None and v != '' and pd.notna(v)
                }
                if non_empty_overloads:
                    base_body['HrIllnessGUID']['Element']['Fields'].update(non_empty_overloads)

            return base_body
        except Exception as e:
            raise Exception(f"Build request body failed: {str(e)}")

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get sick leaves information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing sick leaves information

        Raises:
            Exception: If get sick leaves operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_sick_leaves_url, schema=SickLeaveGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get sick leaves failed: {str(e)}") from e

    def create(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Create sick leave information in AFAS

        Args:
            data: Dictionary containing sick leave data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = SickLeaveCreateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Sickleave data validation failed: {str(e)}")

            body = self.__build_create_body(data=valid_data, overload_fields=overload_fields)
            return self.afas.session.post(
                url=f"{self.afas.base_url}/HrIllness",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Create request body failed: {str(e)}")

    def delete(self, guid: str or int) -> requests.Response:
        """
        method used to delete sick leave from AFAS
        :param guid: sick leave guid, may be a string or number
        :return: response object
        """
        try:
            return self.afas.session.delete(url=f"{self.afas.base_url}/HrIllnessGUID/HrIllnessGUID/@GUID/{guid}", timeout=self.afas.timeout)
        except Exception as e:
            raise Exception(f"Delete sick_leave failed: {str(e)}")

    def update(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Update sick_leave information in AFAS

        Args:
            data: Dictionary containing sick_leave update data including guid
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = SickLeaveUpdateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")

            body = self.__build_update_body(data=valid_data, overload_fields=overload_fields)
            return self.afas.session.put(
                url=f"{self.afas.base_url}/HrIllnessGUID",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Update request body failed: {str(e)}")
