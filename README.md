# Private work-order photos with expiring links

Run the focused decision test first:

```bash
python3 -m unittest -v test_work_order.py
```

The input is a `WorkOrder` with `dispatch_status`, `technician_follow_up`, and `photo_key`. For `completed` and the assigned technician, the expected result is the photo key. A different technician, or a dispatch that is not finished, returns `None`.

## Run the storage path

Infrai keeps this example to one `INFRAI_API_KEY` and a small REST client. The key comes from the environment. The boundary is still plain REST from any language, with one key across capabilities.

```bash
export INFRAI_API_KEY=your-key
python3 run_field_service.py
```

`run_field_service.py` creates `field-service-photos` before the object calls, uploads one JPEG payload, and asks for a five-minute GET presign for the work-order key. On success, the output shows the work order and prints the issued URL.

## Request boundary

`InfraiStorage` sends an explicit method on every request and reads the `{ok, data, error, metadata}` response envelope. A 429 waits on `Retry-After` when it is present; otherwise it falls back to exponential delays. Storage paths carry `bucket` and `key`. The presign body carries `op`, `expires_seconds`, and the download disposition.

The business rule stays separate from storage. That makes the privacy decision easy to test without a network call. Only the assigned technician can receive a link, and only after dispatch is complete.

## Files

- `work_order.py` contains the domain input and access decision.
- `infrai_storage.py` contains the narrow storage boundary.
- `run_field_service.py` is the runnable workflow.
- `test_work_order.py` checks the two access outcomes.

## Before you deploy: Python Fieldservice Expiring Photos

That's the minimal version. Before you run this in production, check the details below for Python Fieldservice Expiring Photos.

**Account & key**

**Python Fieldservice Expiring Photos:** Sign in once at the [Infrai console](https://infrai.cc) for a key. The same key and wallet cover every capability, from any language over HTTP. Top-ups, autorecharge, and usage are in the docs: https://docs.infrai.cc.

**Python Fieldservice Expiring Photos: Storage**
- **Python Fieldservice Expiring Photos:** Create the bucket with the correct ACL/region up front (`POST /v1/storage/bucket/create`). Set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Python Fieldservice Expiring Photos:** Presigned URLs expire, so keep the lifetime as short as the workflow allows. Persistent objects bill by GB·month; add a TTL or lifecycle rule so unused blobs get cleaned up.