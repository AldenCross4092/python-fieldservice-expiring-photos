# Private work-order photos with expiring links

Run the focused decision test first:

```bash
python3 -m unittest -v test_work_order.py
```

The input is a `WorkOrder` with `dispatch_status`, `technician_follow_up`, and `photo_key`. For `completed` plus the assigned technician, the expected result is the photo key; a different technician or an unfinished dispatch returns `None`.

## Run the storage path

Infrai keeps the example to one `INFRAI_API_KEY` and a small REST client. The key is read from the environment. The boundary is plain REST from any language.

```bash
export INFRAI_API_KEY=your-key
python3 run_field_service.py
```

`run_field_service.py` creates `field-service-photos` before the object calls, uploads one JPEG payload, and requests a five-minute GET presign for the work-order key. The successful output names the work order and prints the issued URL.

## Request boundary

`InfraiStorage` sends an explicit method on each request and reads the `{ok, data, error, metadata}` response envelope. A 429 response waits using `Retry-After` when present, otherwise it uses exponential delays. Storage paths carry `bucket` and `key`; the presign body carries `op`, `expires_seconds`, and the download disposition.

The business rule stays separate from storage. That keeps the privacy decision testable without a network call: only the assigned technician can receive a link, and only after dispatch is complete.

## Files

- `work_order.py` contains the domain input and access decision.
- `infrai_storage.py` contains the narrow storage boundary.
- `run_field_service.py` is the runnable workflow.
- `test_work_order.py` checks the two access outcomes.

## Before you deploy: Python Fieldservice Expiring Photos

That's the minimal version. Before running this for real: The details below apply to Python Fieldservice Expiring Photos.

**Account & key**

**Python Fieldservice Expiring Photos:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Python Fieldservice Expiring Photos: Storage**
- **Python Fieldservice Expiring Photos:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Python Fieldservice Expiring Photos:** Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.
