"""RPC client services for customer app."""

from typing import Any, Literal

from kaiju_tools.http import RPCClientService
from kaiju_tools.services import SERVICE_CLASS_REGISTRY

from .types import Customer, CustomerCreate, CustomerId, CustomerUpdate, SearchFilter


class ElementoCustomersClient(RPCClientService):
    """Auto-generated ElementoCustomers RPC client.

    Configuration example:

    .. code-block:: yaml

      - cls: HTTPService
        name: elemento_customers_conn
        settings:
          host: http://0.0.0.0:10001
      - cls: ElementoCustomersClient
        settings:
          transport: elemento_customers_conn

    """

    async def create(
        self, customer: CustomerCreate.Fields, _max_timeout: int = None, _nowait: bool = False
    ) -> Customer.Fields:
        """Call Customers.create."""
        result = await self.call(
            method="Customers.create", params=dict(customer=customer), max_timeout=_max_timeout, nowait=_nowait
        )
        return Customer.get_struct(result)

    async def get(
        self, id: CustomerId | int, _max_timeout: int = None, _nowait: bool = False
    ) -> Customer.Fields | None:
        """Get customer data by id or return `None` if not exists."""
        result = await self.call(method="Customers.get", params=dict(id=id), max_timeout=_max_timeout, nowait=_nowait)
        if result:
            result = Customer.get_struct(result)
        return result

    async def get_by_phone(self, phone: str, _max_timeout: int = None, _nowait: bool = False) -> Customer.Fields | None:
        """Find a customer by phone number or return `None` if not exists."""
        result = await self.call(
            method="Customers.get_by_phone", params=dict(phone=phone), max_timeout=_max_timeout, nowait=_nowait
        )
        if result:
            result = Customer.get_struct(result)
        return result

    async def find(
        self,
        *,
        query: str = "",
        filters: SearchFilter = None,
        offset: int = 0,
        limit: int = 100,
        sort_key: str = None,
        sort_order: Literal["asc", "desc"] = None,
        _max_timeout: int = None,
        _nowait: bool = False,
    ) -> list[Customer.Fields]:
        """Find and list customers.

        :param query: query string
        :param filters: list of search conditions
        :param offset: pagination offset
        :param limit: pagination limit
        :param sort_key: sorting key
        :param sort_order: sorting order
        :param _max_timeout: max request timeout in sec (None == server default)
        :param _nowait: do not wait for the response (equivalent to id: null in JSONRPC)
        """
        result = await self.call(
            method="Customers.find",
            params=dict(
                query=query, filters=filters, offset=offset, limit=limit, sort_key=sort_key, sort_order=sort_order
            ),
            max_timeout=_max_timeout,
            nowait=_nowait,
        )
        return [Customer.get_struct(row) for row in result]

    async def block(self, id: CustomerId | int, _max_timeout: int = None, _nowait: bool = False) -> None:
        """Set customer status to `blocked`."""
        return await self.call(method="Customers.block", params=dict(id=id), max_timeout=_max_timeout, nowait=_nowait)

    async def unblock(self, id: CustomerId | int, _max_timeout: int = None, _nowait: bool = False) -> None:
        """Revert customer `blocked` status."""
        return await self.call(method="Customers.unblock", params=dict(id=id), max_timeout=_max_timeout, nowait=_nowait)

    async def change_phone(self, id: CustomerId, phone: str, _max_timeout: int = None, _nowait: bool = False) -> bool:
        """Change customer phone number."""
        return await self.call(
            method="Customers.change_phone", params=dict(id=id, phone=phone), max_timeout=_max_timeout, nowait=_nowait
        )

    async def delete(self, id: CustomerId | int, _max_timeout: int = None, _nowait: bool = False) -> None:
        """Delete customer completely and all its data."""
        return await self.call(method="Customers.delete", params=dict(id=id), max_timeout=_max_timeout, nowait=_nowait)

    async def update(
        self,
        id: CustomerId | int,
        customer: CustomerUpdate.Fields | dict[str, Any],
        _max_timeout: int = None,
        _nowait: bool = False,
    ) -> Customer.Fields:
        """Update certain customer profile data or other parameters."""
        result = await self.call(
            method="Customers.update", params=dict(id=id, customer=customer), max_timeout=_max_timeout, nowait=_nowait
        )
        return Customer.get_struct(result)

    async def get_settings(self, _max_timeout: int = None, _nowait: bool = False) -> dict[str, Any]:
        """Get current service shared settings.

        :param _max_timeout: max request timeout in sec (None == server default)
        :param _nowait: do not wait for the response (equivalent to id: null in JSONRPC)
        """
        return await self.call(method="Customers.settings.get", params=dict(), max_timeout=_max_timeout, nowait=_nowait)

    async def set_settings(
        self, value: dict[str, Any], _max_timeout: int = None, _nowait: bool = False
    ) -> dict[str, Any]:
        """Create or update service shared settings.

        :param value: new settings (you can pass only updated keys here)
        :param _max_timeout: max request timeout in sec (None == server default)
        :param _nowait: do not wait for the response (equivalent to id: null in JSONRPC)
        """
        return await self.call(
            method="Customers.settings.set", params=dict(value=value), max_timeout=_max_timeout, nowait=_nowait
        )

    async def reset_settings(self, _max_timeout: int = None, _nowait: bool = False) -> dict[str, Any]:
        """Reset service settings to the initial values.

        :param _max_timeout: max request timeout in sec (None == server default)
        :param _nowait: do not wait for the response (equivalent to id: null in JSONRPC)
        """
        return await self.call(
            method="Customers.settings.reset", params=dict(), max_timeout=_max_timeout, nowait=_nowait
        )

    async def init_search_index(
        self, load_docs: bool = True, _max_timeout: int = None, _nowait: bool = False
    ) -> int | None:
        """Init search index if not exists.

        :returns: a number of loaded search documents or `None` if index already exists.
        """
        return await self.call(
            method="Customers.search.idx.init",
            params=dict(load_docs=load_docs),
            max_timeout=_max_timeout,
            nowait=_nowait,
        )

    async def flush_search_index(self, _max_timeout: int = None, _nowait: bool = False) -> None:
        """Remove the search index and all related search documents."""
        return await self.call(
            method="Customers.search.idx.flush", params=dict(), max_timeout=_max_timeout, nowait=_nowait
        )

    async def migrate_search_index(
        self, load_docs: bool = False, _max_timeout: int = None, _nowait: bool = False
    ) -> int:
        """Migrate to a new index.

        Use this when you have modified the customer profile schema and need to update the search according to that.

        :returns: a number of loaded search documents
        """
        return await self.call(
            method="Customers.search.idx.migrate",
            params=dict(load_docs=load_docs),
            max_timeout=_max_timeout,
            nowait=_nowait,
        )


SERVICE_CLASS_REGISTRY.register(ElementoCustomersClient)
