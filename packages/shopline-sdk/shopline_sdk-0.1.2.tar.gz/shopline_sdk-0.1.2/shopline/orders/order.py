#!/usr/bin/python3
# @Time    : 2025-06-17
# @Author  : Kevin Kong (kfx2007@163.com)

from shopline.comm import Comm
from shopline.comm import API_URL

class Order(Comm):
    
    def get_orders(self, updated_after=None, updated_before=None,created_after=None, created_before=None, order_ids=[], per_page=50, page=1, sort_by="asc", previous_id=None):
        """
        Get the list of orders.
        :param updated_after: Filter orders updated after this date.
        :param updated_before: Filter orders updated before this date.
        :param created_after: Filter orders created after this date.
        :param created_before: Filter orders created before this date.
        :param order_ids: List of specific order IDs to retrieve.
        :param per_page: Number of orders per page.
        :param page: Page number to retrieve.
        :param sort_by: Field to sort the orders by.
        :param previous_id: ID of the last order from the previous page, used for pagination
        
        :return: List of orders.
        """
        
        url = f"{API_URL}/orders"
        params = {
            "updated_after": updated_after,
            "updated_before": updated_before,
            "created_after": created_after,
            "created_before": created_before,
            "order_ids": order_ids,
            "per_page": per_page,
            "page": page,
            "sort_by": sort_by,
            "previous_id": previous_id
        }
        response = self.get(url, params=params)
        return response.json() if response.status_code == 200 else None
    
    def search(
        self,
        previous_id=None,
        per_page=24,
        page=1,
        query=None,
        shipped_before=None,
        shipped_after=None,
        arrived_before=None,
        arrived_after=None,
        collected_before=None,
        collected_after=None,
        returned_before=None,
        returned_after=None,
        cancelled_before=None,
        cancelled_after=None,
        paid_before=None,
        paid_after=None,
        updated_before=None,
        updated_after=None,
        status=None,
        statuses=None,
        payment_id=None,
        payment_status=None,
        delivery_address=None,  # dict
        delivery_option_id=None,
        delivery_option_type=None,
        delivery_status=None,
        delivery_statuses=None,
        affiliate_data=None,  # dict
        created_before=None,
        created_after=None,
        created_by=None,
        order_number=None,
        customer_id=None,
        customer_email=None,
        name=None,
        phone_number=None,
        delivery_data_tracking_number=None,
        promotion_id=None,
        item_id=None,
        delivery_data=None  # dict, e.g. scheduled_delivery_date_before/after
    ):
        """
        Search orders with filters against /orders/search.

        :param previous_id: ID of the last order from the previous page, used for pagination
        :param previous_id: ID of the last order from the previous page, used for pagination.
        :param per_page: Maximum number of records to return per page (capped at 999). Default: 24.
        :param page: Page number for offset pagination when previous_id is not used. Default: 1.
        :param query: Free-text query to search orders (e.g., order number, customer name/email).
        :param shipped_before: Return orders shipped strictly before this timestamp (ISO 8601 string or datetime).
        :param shipped_after: Return orders shipped at or after this timestamp (ISO 8601 string or datetime).
        :param arrived_before: Return orders arrived strictly before this timestamp (ISO 8601 string or datetime).
        :param arrived_after: Return orders arrived at or after this timestamp (ISO 8601 string or datetime).
        :param collected_before: Return orders collected strictly before this timestamp (ISO 8601 string or datetime).
        :param collected_after: Return orders collected at or after this timestamp (ISO 8601 string or datetime).
        :param returned_before: Return orders returned strictly before this timestamp (ISO 8601 string or datetime).
        :param returned_after: Return orders returned at or after this timestamp (ISO 8601 string or datetime).
        :param cancelled_before: Return orders cancelled strictly before this timestamp (ISO 8601 string or datetime).
        :param cancelled_after: Return orders cancelled at or after this timestamp (ISO 8601 string or datetime).
        :param paid_before: Return orders paid strictly before this timestamp (ISO 8601 string or datetime).
        :param paid_after: Return orders paid at or after this timestamp (ISO 8601 string or datetime).
        :param updated_before: Return orders updated strictly before this timestamp (ISO 8601 string or datetime).
        :param updated_after: Return orders updated at or after this timestamp (ISO 8601 string or datetime).
        :param status: Filter by a single order status (string).
        :param statuses: Filter by one or more order statuses (string or iterable of strings). Sent as statuses[] in query.
        :param payment_id: Filter by payment/transaction ID (string).
        :param payment_status: Filter by payment status (e.g., paid, unpaid, refunded).
        :param delivery_address: Nested filters for delivery address as a dict (e.g., {"country": "...", "city": "..."}). Flattened as delivery_address[key]=value.
        :param delivery_option_id: Filter by delivery/shipping option ID.
        :param delivery_option_type: Filter by delivery option type (e.g., standard, express, pickup).
        :param delivery_status: Filter by a single delivery/shipment status (string).
        :param delivery_statuses: Filter by one or more delivery statuses (string or iterable of strings). Sent as delivery_statuses[] in query.
        :param affiliate_data: Nested filters for affiliate metadata as a dict (e.g., {"source": "...", "campaign": "..."}). Flattened as affiliate_data[key]=value.
        :param created_before: Return orders created strictly before this timestamp (ISO 8601 string or datetime).
        :param created_after: Return orders created at or after this timestamp (ISO 8601 string or datetime).
        :param created_by: Filter by creator identifier (e.g., staff ID, system).
        :param order_number: Filter by order number (human-readable).
        :param customer_id: Filter by customer ID.
        :param customer_email: Filter by customer email address.
        :param name: Filter by customer name.
        :param phone_number: Filter by customer phone number.
        :param delivery_data_tracking_number: Filter by shipment tracking number.
        :param promotion_id: Filter orders associated with a specific promotion ID.
        :param item_id: Filter orders containing a specific item/product ID.
        :param delivery_data: Nested filters for delivery-specific data as a dict (e.g., {"scheduled_delivery_date_before": "..."}). Flattened as delivery_data[key]=value.
        :return: Parsed JSON response (dict/list) when the request succeeds (HTTP 200); otherwise None.
        """
        url = f"{API_URL}/orders/search"

        # Cap per_page to API max
        if per_page is not None:
            try:
                per_page = min(int(per_page), 999)
            except Exception:
                pass

        params = {
            "previous_id": previous_id,
            "per_page": per_page,
            "page": page if not previous_id else None,  # follow API note
            "query": query,
            "shipped_before": shipped_before,
            "shipped_after": shipped_after,
            "arrived_before": arrived_before,
            "arrived_after": arrived_after,
            "collected_before": collected_before,
            "collected_after": collected_after,
            "returned_before": returned_before,
            "returned_after": returned_after,
            "cancelled_before": cancelled_before,
            "cancelled_after": cancelled_after,
            "paid_before": paid_before,
            "paid_after": paid_after,
            "updated_before": updated_before,
            "updated_after": updated_after,
            "status": status,
            "payment_id": payment_id,
            "payment_status": payment_status,
            "delivery_option_id": delivery_option_id,
            "delivery_option_type": delivery_option_type,
            "delivery_status": delivery_status,
            "created_before": created_before,
            "created_after": created_after,
            "created_by": created_by,
            "order_number": order_number,
            "customer_id": customer_id,
            "customer_email": customer_email,
            "name": name,
            "phone_number": phone_number,
            "delivery_data_tracking_number": delivery_data_tracking_number,
            "promotion_id": promotion_id,
            "item_id": item_id,
        }

        # List parameters -> use [] form as API examples show
        if statuses:
            params["statuses[]"] = list(statuses) if isinstance(statuses, (list, tuple, set)) else [statuses]
        if delivery_statuses:
            params["delivery_statuses[]"] = list(delivery_statuses) if isinstance(delivery_statuses, (list, tuple, set)) else [delivery_statuses]

        # Flatten nested dicts using bracket notation: key[subkey]=value
        def _flatten(prefix, data):
            if not isinstance(data, dict):
                return
            for k, v in data.items():
                if v is None:
                    continue
                params[f"{prefix}[{k}]"] = v

        if delivery_address:
            _flatten("delivery_address", delivery_address)
        if affiliate_data:
            _flatten("affiliate_data", affiliate_data)
        if delivery_data:
            _flatten("delivery_data", delivery_data)

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self.get(url, params=params)
        return response.json() if response.status_code == 200 else None
    
    def update(
        self,
        shopline_order_id,
        status=None,
        payment_status=None,
        delivery_address=None,  # dict
        delivery_option_id=None,
        delivery_option_type=None,
        delivery_data=None,  # dict
        note=None,
        tags=None,  # list[str]
        metadata=None,  # dict
        items=None,  # list[dict]
        customer_id=None,
        order_number=None,
        extra=None,  # dict, 任意补充字段，直接合并进请求体
        use_patch=True,
    ):
        """
        更新订单信息。

        :param shopline_order_id: Shopline 订单唯一标识。
        :param status: 订单状态。
        :param payment_status: 支付状态（如 paid/unpaid/refunded）。
        :param delivery_address: 配送地址信息字典（如 {"country": "...", "city": "..."}）。
        :param delivery_option_id: 配送方式 ID。
        :param delivery_option_type: 配送方式类型（如 standard/express/pickup）。
        :param delivery_data: 配送相关数据字典（如 {"scheduled_delivery_date": "..."}）。
        :param note: 订单备注。
        :param tags: 标签列表。
        :param metadata: 自定义扩展字段字典。
        :param items: 订单行项目列表，每项为字典（如 [{"item_id": "...", "quantity": 1}]）。
        :param customer_id: 客户 ID。
        :param order_number: 订单号（可用于对齐外部系统）。
        :param extra: 额外需要合并到请求体中的原始字段字典（可覆盖同名字段）。
        :param use_patch: 是否使用 PATCH（部分更新）。False 则使用 PUT（整体更新）。
        :return: 请求成功时返回解析后的 JSON；204 无内容时返回 True；否则返回 None。
        """
        url = f"{API_URL}/orders/{shopline_order_id}"

        payload = {
            "status": status,
            "payment_status": payment_status,
            "delivery_address": delivery_address,
            "delivery_option_id": delivery_option_id,
            "delivery_option_type": delivery_option_type,
            "delivery_data": delivery_data,
            "note": note,
            "tags": tags,
            "metadata": metadata,
            "items": items,
            "customer_id": customer_id,
            "order_number": order_number,
        }

        # 去除值为 None 的字段
        payload = {k: v for k, v in payload.items() if v is not None}

        # 合并额外字段
        if isinstance(extra, dict) and extra:
            payload.update(extra)

        # 递归移除 None（确保嵌套结构也干净）
        def _drop_none(obj):
            if isinstance(obj, dict):
                return {k: _drop_none(v) for k, v in obj.items() if v is not None}
            if isinstance(obj, list):
                return [ _drop_none(v) for v in obj if v is not None ]
            return obj

        payload = _drop_none(payload)

        response = self.patch(url, json=payload)
        return response.json() if response.status_code == 200 else None
