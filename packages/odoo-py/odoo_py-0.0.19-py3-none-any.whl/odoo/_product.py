from __future__ import annotations
from typing import Any
from ._integration import OdooIntegration
from .exceptions import ProductNotFoundError


class ProductModel(OdooIntegration):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get_product_by_id(self, product_id: int) -> list[dict[str, Any]]:
        response = self.read("product.product", [product_id])
        return response

    def get_product_id_by_reference(self, reference_id: str) -> int:
        response = self.search(
            "product.product", [[["default_code", "=", reference_id]]]
        )
        if response:
            return response[0]
        raise ProductNotFoundError(f"Product '{reference_id}' not found")
