from typing import List

from benchling_api_client.v2.stable.api.connect import (
    convert_to_asm as api_client_convert_to_asm,
    convert_to_csv as api_client_convert_to_csv,
    list_allotropy_vendors as api_client_list_allotropy_vendors,
)
from benchling_api_client.v2.stable.models.convert_to_asm import ConvertToASM
from benchling_api_client.v2.stable.models.convert_to_asm_response_200 import ConvertToASMResponse_200
from benchling_api_client.v2.stable.models.convert_to_csv import ConvertToCSV
from benchling_api_client.v2.stable.models.convert_to_csv_response_200_item import (
    ConvertToCSVResponse_200Item,
)

from benchling_sdk.errors import raise_for_status
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.services.v2.base_service import BaseService


class ConnectService(BaseService):
    """
    Connect.

    Connect endpoints support Benchling Connect actions, like instrument data conversion.

    See https://benchling.com/api/reference#/Connect
    """

    @api_method
    def convert_to_asm(self, file_info: ConvertToASM) -> ConvertToASMResponse_200:
        """
        Convert an input blob or file containing instrument data to ASM (Allotrope Simple Model) JSON.

        May provide the name of the instrument vendor (see /connect/list-allotropy-vendors) or the ID of a
        connection associated with an instrument vendor.

        See https://benchling.com/api/reference#/Connect/convertToASM
        """
        response = api_client_convert_to_asm.sync_detailed(client=self.client, json_body=file_info)
        response = raise_for_status(response)
        return model_from_detailed(response)

    @api_method
    def convert_to_csv(self, file_info: ConvertToCSV) -> List[ConvertToCSVResponse_200Item]:
        """
        Convert a blob or file containing ASM, JSON, or instrument data to CSV.

        If the file is ASM JSON, specify either no transform type (in which case all transform types will be
        returned), a matching transform type for the ASM schema, or a custom JSON mapper config.

        If the file non-ASM JSON, must provide a JSON mapper config argument, which specifies how to map the
        JSON to CSV. Reach out to Benchling Support for more information about how to create a JSON mapper
        config.

        If the file is an instrument file, must also specify an instrument vendor. The file will be converted
        first to ASM JSON and then to CSV. Only the CSV output will be returned.

        May provide an AutomationOutputFile with CSV transform arguments configured to read the transform type
        or mapper config from.

        May provide a connection ID associated with an instrument to read the vendor from.

        See https://benchling.com/api/reference#/Connect/convertToCSV
        """
        response = api_client_convert_to_csv.sync_detailed(client=self.client, json_body=file_info)
        response = raise_for_status(response)
        return model_from_detailed(response)

    @api_method
    def list_allotropy_vendors(self) -> List[None]:
        """
        Return the list of available allotropy instrument vendor types.

        See https://benchling.com/api/reference#/Connect/listAllotropyVendors
        """
        response = api_client_list_allotropy_vendors.sync_detailed(client=self.client)
        response = raise_for_status(response)
        return model_from_detailed(response)
