"""Upload a work-order photo and print its expiring download URL."""
from infrai_storage import InfraiStorage
from work_order import WorkOrder, photo_request
import time


def main() -> None:
    storage = InfraiStorage()
    bucket = f"field-service-photos-{time.time_ns()}"
    order = WorkOrder("WO-1042", "completed", "tech-7", "WO-1042/site-photo.jpg")
    storage.create_bucket(bucket)
    try:
        storage.put_object(bucket, order.photo_key, b"field-service-photo")
        key = photo_request(order, "tech-7")
        if key is None:
            print("Photo access denied")
            return
        signed = storage.presign_download(bucket, key)
        print(f"Download URL issued for {order.work_order_id}: {signed['url']}")
    finally:
        storage.delete_object(bucket, order.photo_key)
        storage.delete_bucket(bucket)
        storage.wait_for_cleanup(bucket, order.photo_key)

if __name__ == "__main__":
    main()
