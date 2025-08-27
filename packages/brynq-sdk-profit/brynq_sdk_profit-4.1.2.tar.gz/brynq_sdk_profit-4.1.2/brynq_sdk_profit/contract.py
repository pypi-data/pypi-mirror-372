import asyncio
import pandas as pd
from typing import Optional
import requests
from datetime import datetime

from .schemas.contract import ContractGetSchema, ContractUpdateSchema


class Contract:
    """Contract management class for AFAS integration"""

    def __init__(self, afas_connector):
        """
        Initialize Contract class with AFAS connector

        Args:
            afas_connector: AFAS connection handler instance
        """
        self.afas = afas_connector
        self.field_mappings = {
            'contract': {
                'end_date_contract': 'DaEn',
                'type_of_employment': 'PEmTy',
                'termination_initiative': 'ViIe',
                'termination_reason': 'ViRe',
                'probation_period': 'ViTo',
                'probation_end_date': 'DaEt',
                'cao': 'ClId',
                'terms_of_employment': 'WcId',
                'type_of_contract': 'ApCo',
                'employer_nmbr': 'CmId',
                'type_of_employee': 'EmMt',
                'employment': 'ViEt',
                'seniority_date': 'StAc',
                'start_date_contract_chain': 'DaSc',
                'contract_chain_code': 'ViKe',
                'date_in_service_original': 'DbYs',
                'number_income_ratio': 'EnS2',
            },
            'function': {
                'organizational_unit': 'DpId',
                'function_id': 'FuId',
                'cost_center_id': 'CrId',
                'cost_carrier_id': 'CcId'
            },
            'timetable': {
                'changing_work_pattern': 'StPa',
                'weekly_hours': 'HrWk',
                'part_time_percentage': 'PcPt',
                'days_per_week': 'DyWk',
                'fte': 'Ft',
                'on_call_contract': 'ClAg',
                'type_of_schedule': 'EtTy',
                'hours_for_tax_decleration': "DfHo",  # Afw. uren p.w. aangifte
                'actual_working_pattern_days_monday': 'HrMo',
                'actual_working_pattern_days_tuesday': 'HrTu',
                'actual_working_pattern_days_wednesday': 'HrWe',
                'actual_working_pattern_days_thursday': 'HrTh',
                'actual_working_pattern_days_friday': 'HrFr',
                'actual_working_pattern_days_saturday': 'HrSa',
                'actual_working_pattern_days_sunday': 'HrSu'

            },
            'salary': {
                'step': 'SaSt',
                'type_of_salary': 'SaPe',
                'salary_amount': 'EmSa',
                'period_table': 'PtId',
                'salary_scale': 'VaSc',
                'salary_scale_type': 'TaId',
                'function_scale': 'FuSc',
                'function_scale_type': 'FuTa',
                'salary_year_amount': 'SaYe',
                'net_salary': 'NtSa',
                'apply_timetable': 'TtPy'
            },
            'fiscal': {
            }
        }
        self.required_fields = ['employee_id', 'start_date_contract', 'organizational_unit',
                                'function_id', 'costcenter_id',
                                'weekly_hours', 'parttime_percentage',
                                'type_of_salary', 'period_table', 'start_date_workcycle',
                                'workcycle', 'start_week', 'index_number']
        self.get_url = f"{self.afas.base_url}/brynq_sdk_contract"

    def get(self, filter_fields: dict = None) -> pd.DataFrame:
        """
        Get contract information from AFAS

        Args:
            filter_fields (dict, optional): Dictionary of filters in format {field_name: value}

        Returns:
            pd.DataFrame: DataFrame containing contract information

        Raises:
            Exception: If get contract operation fails
        """
        try:
            return asyncio.run(self.afas.base_get(url=self.get_url, schema=ContractGetSchema, filter_fields=filter_fields))
        except Exception as e:
            raise Exception(f"Get contract failed: {str(e)}") from e

    def __build_only_contract_req_body(self, data: dict, overload_fields: dict = None) -> dict:
        """
        Prepare request body for contract update.

        Args:
            data: Dictionary containing contract data
            overload_fields: Optional field overrides

        Returns:
            dict: Formatted request body for AFAS API
        """

        try:
            # Base request body
            base_body = {
                "AfasEmployee": {
                    "Element": {
                        "@EmId": data['employee_id'],
                        "Objects": [
                            {
                                "AfasContract": {
                                    "Element": {
                                        "@DaBe": data['start_date_contract'],
                                        "Fields": {}
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            # Add contract fields
            contract_fields = {}
            for field, afas_field in self.field_mappings['contract'].items():
                if field in data:
                    value = data[field]
                    if not pd.isna(value) and value != '' and value != None:
                        contract_fields[afas_field] = data[field]

            base_body['AfasEmployee']['Element']['Objects'][0]['AfasContract']['Element']['Fields'].update(
                contract_fields)

            return base_body

        except Exception as e:
            raise Exception("Build request body failed: " + str(e)) from e

    def __build_req_body(self, data: dict, overload_fields: dict = None) -> dict:
        """
        Prepare request body for contract update.

        Args:
            data: Dictionary containing contract data
            overload_fields: Optional field overrides

        Returns:
            dict: Formatted request body for AFAS API
        """

        try:
            # Base request body
            base_body = {
                "AfasEmployee": {
                    "Element": {
                        "@EmId": data['employee_id'],
                        "Objects": [
                            {
                                "AfasContract": {
                                    "Element": {
                                        "@DaBe": data['start_date_contract'],
                                        "Fields": {}
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            # Add contract fields
            contract_fields = {}
            for field, afas_field in self.field_mappings['contract'].items():
                if field in data:
                    value = data[field]
                    if not pd.isna(value) and value != '' and value is not None:
                        contract_fields[afas_field] = data[field]
            base_body['AfasEmployee']['Element']['Objects'][0]['AfasContract']['Element']['Fields'].update(
                contract_fields)

            # Add function fields if present
            if any(field in data for field in self.field_mappings['function']):

                function_updates = {}
                for field, afas_field in self.field_mappings['function'].items():
                    if field in data:
                        value = data[field]
                        if not pd.isna(value) and value != '' and value != None:
                            function_updates[afas_field] = data[field]

                function_dict = {
                    "AfasOrgunitFunction": {
                        "Element": {
                            "@DaBe": data['start_date_contract'],
                            "Fields": function_updates
                        }
                    }
                }
                base_body['AfasEmployee']['Element']['Objects'].append(function_dict)


            # Add timetable fields if present
            if any(field in data for field in self.field_mappings['timetable']):
                timetable_updates = {"StPa": data.get('changing_work_pattern', True)}  # Default to True if not provided
                for field, afas_field in self.field_mappings['timetable'].items():
                    if field in data:
                        value = data[field]
                        if not pd.isna(value) and value != '' and value != None:
                            timetable_updates[afas_field] = data[field]

                timetable_dict = {
                    "AfasTimeTable": {
                        "Element": {
                            "@DaBg": data['start_date_contract'],
                            "Fields": timetable_updates
                        }
                    }
                }

                base_body['AfasEmployee']['Element']['Objects'].append(timetable_dict)

            # Add salary fields if present
            if any(field in data for field in self.field_mappings['salary']):
                salary_updates = {}
                for field, afas_field in self.field_mappings['salary'].items():
                    if field in data:
                        value = data[field]
                        if not pd.isna(value) and value != '' and value != None:
                            salary_updates[afas_field] = data[field]

                salary_dict = {
                    "AfasSalary": {
                        "Element": {
                            "@DaBe": data['start_date_contract'],
                            "Fields": salary_updates
                        }
                    }
                }

                base_body['AfasEmployee']['Element']['Objects'].append(salary_dict)
            fiscal_dict = {
                "AfasAgencyFiscus": {
                    "Element": {
                        "@DaBe": data['start_date_contract'],
                        "@AyId": "F",  # Default authority code for Fiscus
                    }
                }
            }
            if any(field in data for field in self.field_mappings['fiscal']):
                fiscal_updates = {}
                # ZVW code logic
                fiscal_year = datetime.strptime(data['start_date_contract'], '%Y-%m-%d').year
                if 'zvw_code' in data:
                    fiscal_updates['ViZv'] = data['zvw_code']
                else:
                    if fiscal_year < 2006:
                        fiscal_updates['ViZv'] = "C"
                    elif fiscal_year < 2013:
                        fiscal_updates['ViZv'] = "CEF"
                    else:
                        fiscal_updates['ViZv'] = "K"

                # Add other fiscal fields
                for field, afas_field in self.field_mappings['fiscal'].items():
                    if field in data:
                        value = data[field]
                        if not pd.isna(value) and value != '' and value != None:
                            fiscal_updates[afas_field] = data[field]
                if fiscal_updates:
                    fiscal_dict["AfasAgencyFiscus"]["Element"]["Fields"] = fiscal_updates

            base_body['AfasEmployee']['Element']['Objects'].append(fiscal_dict)
            return base_body

        except Exception as e:
            raise Exception("Build request body failed: " + str(e)) from e

    def update(self, data: dict, overload_fields: dict = None, only_contract: bool = False) -> Optional[
        requests.Response]:
        """
        Update contract in AFAS

        Args:
            data: Dictionary containing contract data
            overload_fields: Optional dictionary of fields to override
            only_contract: Update only contract or not

        Returns:
            requests.Response: Response from AFAS API

        Raises:
            ValueError: If validation fails or unsupported method
        """

        try:
            try:
                # Data validation
                valid_data = ContractUpdateSchema(**data).model_dump()
                valid_data = self.afas.convert_timestamp_columns(valid_data)
            except Exception as e:
                raise Exception("Data validation failed:" + str(e)) from e
            if not only_contract:
                req_body = self.__build_req_body(valid_data, overload_fields)
            else:
                req_body = self.__build_only_contract_req_body(valid_data, overload_fields)

            return self.afas.session.post(
                url=f"{self.afas.base_url}/KnEmployee/AfasContract",
                json=req_body, timeout=self.afas.timeout
            )
        except Exception as e:
            raise Exception("Update contract failed: " + str(e)) from e
