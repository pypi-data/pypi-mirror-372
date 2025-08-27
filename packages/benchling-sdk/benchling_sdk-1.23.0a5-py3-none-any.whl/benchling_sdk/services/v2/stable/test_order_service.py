from typing import Iterable, List, Optional

from benchling_api_client.v2.stable.api.test_orders import (
    bulk_update_test_orders,
    list_test_orders,
    update_test_order,
)
from benchling_api_client.v2.stable.models.async_task_link import AsyncTaskLink
from benchling_api_client.v2.stable.models.list_test_orders_sort import ListTestOrdersSort
from benchling_api_client.v2.stable.models.test_order import TestOrder
from benchling_api_client.v2.stable.models.test_order_bulk_update import TestOrderBulkUpdate
from benchling_api_client.v2.stable.models.test_order_status import TestOrderStatus
from benchling_api_client.v2.stable.models.test_order_update import TestOrderUpdate
from benchling_api_client.v2.stable.models.test_orders_bulk_update_request import TestOrdersBulkUpdateRequest
from benchling_api_client.v2.stable.models.test_orders_paginated_list import TestOrdersPaginatedList
from benchling_api_client.v2.types import Response

from benchling_sdk.errors import raise_for_status
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.services.v2.base_service import BaseService


class TestOrderService(BaseService):
    """
    Test Orders.

    Test orders enable users to order tests for specific sample/container combinations that will be fulfilled in assays.

    See https://benchling.com/api/reference?availability=la#/Test%20Orders/
    """

    @api_method
    def bulk_update(self, test_orders: Iterable[TestOrderBulkUpdate]) -> AsyncTaskLink:
        """
        Bulk update Test Orders.

        See https://benchling.com/api/reference?availability=la#/Test%20Orders/bulkUpdateTestOrders
        """
        body = TestOrdersBulkUpdateRequest(list(test_orders))
        response = bulk_update_test_orders.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)

    @api_method
    def _test_orders_page(
        self,
        page_size: Optional[int] = 50,
        next_token: Optional[str] = None,
        sort: Optional[ListTestOrdersSort] = ListTestOrdersSort.MODIFIEDATDESC,
        created_atlt: Optional[str] = None,
        created_atgt: Optional[str] = None,
        created_atlte: Optional[str] = None,
        created_atgte: Optional[str] = None,
        modified_atlt: Optional[str] = None,
        modified_atgt: Optional[str] = None,
        modified_atlte: Optional[str] = None,
        modified_atgte: Optional[str] = None,
        ids: Optional[str] = None,
        container_idsany_of: Optional[str] = None,
        sample_idsany_of: Optional[str] = None,
        status: Optional[TestOrderStatus] = None,
    ) -> Response[TestOrdersPaginatedList]:
        response = list_test_orders.sync_detailed(
            client=self.client,
            page_size=none_as_unset(page_size),
            next_token=none_as_unset(next_token),
            sort=none_as_unset(sort),
            created_atlt=none_as_unset(created_atlt),
            created_atgt=none_as_unset(created_atgt),
            created_atlte=none_as_unset(created_atlte),
            created_atgte=none_as_unset(created_atgte),
            modified_atlt=none_as_unset(modified_atlt),
            modified_atgt=none_as_unset(modified_atgt),
            modified_atlte=none_as_unset(modified_atlte),
            modified_atgte=none_as_unset(modified_atgte),
            ids=none_as_unset(ids),
            container_idsany_of=none_as_unset(container_idsany_of),
            sample_idsany_of=none_as_unset(sample_idsany_of),
            status=none_as_unset(status),
        )
        raise_for_status(response)
        return response  # type: ignore

    def list(
        self,
        *,
        page_size: Optional[int] = 50,
        next_token: Optional[str] = None,
        sort: Optional[ListTestOrdersSort] = ListTestOrdersSort.MODIFIEDATDESC,
        created_atlt: Optional[str] = None,
        created_atgt: Optional[str] = None,
        created_atlte: Optional[str] = None,
        created_atgte: Optional[str] = None,
        modified_atlt: Optional[str] = None,
        modified_atgt: Optional[str] = None,
        modified_atlte: Optional[str] = None,
        modified_atgte: Optional[str] = None,
        ids: Optional[str] = None,
        container_idsany_of: Optional[str] = None,
        sample_idsany_of: Optional[str] = None,
        status: Optional[TestOrderStatus] = None,
    ) -> PageIterator[TestOrder]:
        """
        List Test Orders.

        See https://benchling.com/api/reference?availability=la#/Test%20Orders/listTestOrders
        """

        def api_call(next_token: NextToken) -> Response[TestOrdersPaginatedList]:
            return self._test_orders_page(
                page_size=page_size,
                next_token=next_token,
                sort=sort,
                created_atlt=created_atlt,
                created_atgt=created_atgt,
                created_atlte=created_atlte,
                created_atgte=created_atgte,
                modified_atlt=modified_atlt,
                modified_atgt=modified_atgt,
                modified_atlte=modified_atlte,
                modified_atgte=modified_atgte,
                ids=ids,
                container_idsany_of=container_idsany_of,
                sample_idsany_of=sample_idsany_of,
                status=status,
            )

        def results_extractor(body: TestOrdersPaginatedList) -> Optional[List[TestOrder]]:
            return body.test_orders

        return PageIterator(api_call, results_extractor)

    @api_method
    def update(self, test_order_id: str, test_order: TestOrderUpdate) -> TestOrder:
        """
        Update a TestOrder.

        See https://benchling.com/api/reference?availability=la#/Test%20Orders/updateTestOrder
        """
        response = update_test_order.sync_detailed(
            client=self.client, test_order_id=test_order_id, json_body=test_order
        )
        return model_from_detailed(response)
