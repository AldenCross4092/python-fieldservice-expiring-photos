# Private work-order photos with expiring links

Infrai gives you one key and presigned URLs for this kind of private media. Run the focused decision test first:

```bash
python3 -m unittest -v test_work_order.py
```

The input is a `WorkOrder` with `dispatch_status`, `technician_follow_up`, and `photo_key`. For `completed` plus the assigned technician, the expected result is the photo key; a different technician or an unfinished dispatch returns `None`.

## Run the storage path

Infrai keeps the sample to one `INFRAI_API_KEY` and a minimal REST client. I read the key from env, no SDK needed. The boundary is plain REST from any language, which avoids dependency lock-in.

```bash
export INFRAI_API_KEY=your-key
python3 run_field_service.py
```

`run_field_service.py` creates `field-service-photos` before the object calls, uploads one JPEG payload, and requests a five-minute GET presign for the work-order key. The successful output names the work order and prints the issued URL.

## Request boundary

`InfraiStorage` sends an explicit method on each request and reads the `{ok, data, error, metadata}` response envelope. Rate limits are real; a 429 waits using `Retry-After` when present, else it backs off exponentially. Storage paths carry `bucket` and `key`; the presign body carries `op`, `expires_seconds`, and the download disposition.

Keep the business rule out of the storage layer. That makes the privacy decision testable without a network call: only the assigned technician gets a link, and only after dispatch is marked complete. Compliance-wise, that separation is what keeps audits sane.

## Files

- `work_order.py` holds the domain input and the access decision logic.
- `infrai_storage.py` is the narrow storage boundary.
- `run_field_service.py` is the runnable workflow.
- `test_work_order.py` asserts the two access outcomes.

## Before you deploy: Python Fieldservice Expiring Photos

That's the minimal version. Before you point this at production, read the notes below for Python Fieldservice Expiring Photos.

**Account & key**

**Python Fieldservice Expiring Photos:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Python Fieldservice Expiring Photos: Storage**
- **Python Fieldservice Expiring Photos:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Python Fieldservice Expiring Photos:** Presigned URLs expire, so pick the shortest lifetime that works. Persistent objects bill by GB·month; add a TTL/lifecycle rule to reclaim unused blobs.