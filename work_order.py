"""Business decision for a private work-order photo."""
from dataclasses import dataclass

@dataclass(frozen=True)
class WorkOrder:
    work_order_id: str
    dispatch_status: str
    technician_follow_up: str
    photo_key: str

def photo_request(order: WorkOrder, technician_id: str) -> str | None:
    allowed = order.dispatch_status == "completed" and order.technician_follow_up == technician_id
    return order.photo_key if allowed else None
