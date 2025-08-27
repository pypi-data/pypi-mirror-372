"""Schema definitions for Profit package"""

from .contract import (
    ContractComponentSchema,
    ContractGetSchema,
    ContractUpdateSchema,
    ContractRehireSchema
    # RehireSalaryComponentSchema
)
from .address import (
    AddressBaseSchema,
    AddressGetSchema,
    AddressUpdateSchemaEmployee,
    EmployeeAddressUpdateSchema
)
