import asyncio
import pandas as pd
from typing import Optional
import requests

from .schemas.leaves import LeaveCreateSchema, LeaveUpdateSchema, LeaveBalanceUpdateSchema, LeaveGetSchema


class Leaves:
    """Leave management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize Leaves class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.get_leaves_url = f"{self.afas.base_url}/brynq_sdk_leaves"
    
    
    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get leaves information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing leaves information

        Raises:
            Exception: If get leaves operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_leaves_url, schema=LeaveGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get leaves failed: {str(e)}") from e


    def __build_update_body(self, data, overload_fields):
        """
        Build request body for leave update
        
        Args:
            data: Dictionary containing leave data
            overload_fields: Optional custom fields
            
        Returns:
            dict: Request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
            base_body = {
                "HrAbsenceID": {
                    "Element": {
                        "Fields": {
                            "Id": data["leave_id"]
                        }
                    }
                }
            }

            # Leave fields mapping
            leave_mapping = {
                "total_hours": "DuRa",
                "partial_leave": "LeDt",
                "employment_id": "EnSe",
                "reason_of_leave": "ViLr",
                "employee_id": "EmId",
                "type_of_leave": "ViAt",
                "start_date": "DaBe",
                "end_date": "DaEn"
            }

            # Add mapped fields
            leave_fields = {
                leave_mapping[key]: value
                for key, value in data.items()
                if key in leave_mapping and key != 'leave_id' and pd.notna(value)
            }

            base_body['HrAbsenceID']['Element']['Fields'].update(leave_fields)

            if overload_fields:
                base_body['HrAbsenceID']['Element']['Fields'].update(overload_fields)

            return base_body
        except Exception as e:
            raise Exception(f"Build update body failed: {str(e)}")

    def __build_balance_body(self, data, overload_fields):
        """
        Build request body for leave balance update
        
        Args:
            data: Dictionary containing leave balance data
            overload_fields: Optional custom fields
            
        Returns:
            dict: Request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
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

            # Leave balance fields mapping
            balance_mapping = {
                "correction_reason": "ViCr",
                "booking_date": "RgDa",
                "employment_id": "EnSe",
                "note": "Re",
                "process_in_payroll": "CcPy",
                "leave_balance": "BlId",
                "weeks": "CoWk"
            }

            # Add mapped fields
            balance_fields = {
                balance_mapping[key]: value
                for key, value in data.items()
                if key in balance_mapping and pd.notna(value)
            }

            base_body['HrAbsCorrection']['Element']['Fields'].update(balance_fields)

            if overload_fields:
                base_body['HrAbsCorrection']['Element']['Fields'].update(overload_fields)
            return base_body
        except Exception as e:
            raise Exception(f"Build balance body failed: {str(e)}")

    def __build_create_body(self, data: dict, overload_fields: dict = None) -> dict:
        """
        Build request body for leave creation
        
        Args:
            data: Dictionary containing leave data
            overload_fields: Optional custom fields
            
        Returns:
            dict: Request body for AFAS API
            
        Raises:
            Exception: If building request body fails
        """
        try:
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
            base_body = {
                "HrAbsenceID": {
                    "Element": {
                        "@EmId": data["employee_id"],
                        "Fields": {
                            'DuRa':data.get("total_hours", 0)
                        }
                    }
                }
            }

            # Add allowed fields to the body
            for field in (allowed_fields.keys() & data.keys()):
                base_body['HrAbsenceID']['Element']['Fields'].update({allowed_fields[field]: data[field]})

            # Add custom fields to the body
            base_body['HrAbsenceID']['Element']['Fields'].update(overload_fields) if overload_fields is not None else ''

            return base_body
        except Exception as e:
            raise Exception(f"Build create body failed: {str(e)}")



    def update(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Update leave information in AFAS

        Args:
            data: Dictionary containing leave data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = LeaveUpdateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}") from e
            body = self.__build_update_body(data=valid_data, overload_fields=overload_fields)
            response = self.afas.session.put(
                url=f"{self.afas.base_url}/HrAbsenceID",
                json=body,
                timeout=self.afas.timeout
            )
            return response
        except Exception as e:
            raise Exception(f"Update leave failed: {str(e)}")

    def update_leave_balance(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Update leave balance in AFAS

        Args:
            data: Dictionary containing leave balance data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = self.afas.validate(schema=LeaveBalanceUpdateSchema, data=data)
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise ValueError(f"Data validation failed: {str(e)}") from e
            body = self.__build_balance_body(data=valid_data, overload_fields=overload_fields)
            response = self.afas.session.post(
                url=f"{self.afas.base_url}/HrAbsCorrection",
                json=body,
                headers=self.afas.headers,
                timeout=self.afas.timeout
            )

            return response
        except Exception as e:
            raise Exception(f"Update leave balance failed: {str(e)}")

    def create(self, data: dict, overload_fields: dict = None) -> Optional[requests.Response]:
        """
        Create leave information in AFAS

        Args:
            data: Dictionary containing leave data
            overload_fields: Optional custom fields

        Returns:
            requests.Response: Response from AFAS API
        """
        try:
            try:
                valid_data = LeaveCreateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception(f"Data validation failed: {str(e)}")
            body = self.__build_create_body(data=valid_data, overload_fields=overload_fields)
            return self.afas.session.post(
                url=f"{self.afas.base_url}/HrAbsenceID",
                json=body,
                timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception(f"Create leave failed: {str(e)}")

    def delete(self, leave_id: str or int) -> requests.Response:
        """
        method used to delete leave from AFAS
        :param leave_id: leave id, may be a string or number
        :return: response object
        """
        try:
            return self.afas.session.delete(url=f"{self.afas.base_url}/HrAbsenceID/HrAbsenceID/@Id/{leave_id}", timeout=self.afas.timeout)
        except Exception as e:
            raise Exception(f"Delete leave failed: {str(e)}")