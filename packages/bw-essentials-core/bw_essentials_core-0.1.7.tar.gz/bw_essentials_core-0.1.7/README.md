# bw-essentials

Here’s a rephrased version of your description with improved flow and clarity:

---

**`bw-essentials`** is a Python utility package offering modular and production-ready wrappers for core infrastructure tasks. It simplifies operations such as **AWS S3 interactions**, **email notifications**, and **version-controlled data lake workflows using LakeFS**. Designed for flexibility and ease of integration, it's well-suited for use across microservices, data pipelines, and automation frameworks.

In addition to infrastructure utilities, it also includes service-specific wrappers for:

1. Master Data  
2. Market Pricer  
3. Broker  
4. Model Portfolio Reporting  
5. Trade Placement  
6. User Portfolio  
7. User Portfolio Reporting

---

## 📦 Installation

```bash
pip install bw-essentials
```

---

## 📁 S3Utils

`S3Utils` provides a high-level interface to interact with AWS S3 and S3-compatible services like MinIO or LocalStack.

### 🔧 Initialization

```python
from bw_essentials.s3_utils import S3Utils

s3 = S3Utils()
```

### ✅ Available Methods

| Method                                                        | Description                                   |
|---------------------------------------------------------------|-----------------------------------------------|
| `upload_file(bucket, key, file_path)`                         | Upload a local file to S3                     |
| `download_file(bucket, key, dest_path)`                       | Download a file from S3                       |
| `list_files(bucket, prefix="")`                               | List all files under a prefix                 |
| `read_file(bucket, key)`                                      | Read and return the content of a file         |
| `delete_file(bucket, key)`                                    | Delete a specific file                        |
| `file_exists(bucket, key)`                                    | Check if a file exists                        |
| `get_latest_file(bucket, prefix)`                             | Get the latest file by modified time          |
| `sync_local_to_s3(bucket, prefix, local_path)`                | Recursively upload a local directory to S3    |
| `sync_s3_to_local(bucket, prefix, local_path)`                | Recursively download an S3 prefix to local    |
| `generate_presigned_url(bucket_name, object_key, expiration)` | Generates Pre Signed Url for given S3 Object. |

---

## 📬 EmailClient

`EmailClient` helps send email notifications with or without attachments using any SMTP server.

### 🔧 Initialization

```python
from bw_essentials.email_client import EmailClient

client = EmailClient(
    sender_email="noreply@example.com",
    sender_name="BW Notifier"
)
```

### ✅ Available Methods

| Method | Description |
|--------|-------------|
| `send_email_without_attachment(to_addresses, cc_addresses, subject, body, is_html=True)` | Send an email without attachment |
| `send_email_with_attachment(to_addresses, cc_addresses, subject, body, attachment_path, is_html=True)` | Send an email with a file attachment |

- Supports both plain text and HTML.
- Accepts single or multiple recipients (`str` or `List[str]`).
- Gracefully handles invalid paths and logs detailed errors.

---

## 🏞️ DataLoch (LakeFS Wrapper)

`DataLoch` wraps LakeFS Python client for working with versioned data over S3. Useful for managing commits, branches, and file operations in a data lake.

### 🔧 Initialization

```python
from bw_essentials.data_loch import LakeFS

dl = LakeFS()
```

You can pass `branch` and `repo` to individual methods or initialize them via `dl.repo = "repo"` and `dl.branch = "branch"`.

### ✅ Available Methods

| Method | Description |
|--------|-------------|
| `upload_file(local_path, repo, branch, dest_path)` | Upload a single file to a branch |
| `download_file(repo, branch, file_path, dest_path)` | Download a single file |
| `sync_local_to_lakefs(local_path, repo, branch, dest_prefix)` | Recursively upload a directory |
| `sync_lakefs_to_local(repo, branch, src_prefix, local_path)` | Recursively download a directory |
| `commit(repo, branch, message)` | Commit the current changes on a branch |
| `get_latest_file(repo, branch, prefix)` | Get latest file (by time) under a prefix |
| `delete_file(repo, branch, file_path)` | Delete a specific file |

- Supports S3-compatible object storage behind LakeFS.
- Handles versioning and commit messages for reproducibility.

---

## 🧪 Example Use Case

```python
# Send notification with S3 report
from bw_essentials.s3_utils import S3Utils
from bw_essentials.email_client import EmailClient

s3 = S3Utils("AK", "SK")
file_path = "/tmp/report.csv"
s3.download_file("my-bucket", "reports/weekly.csv", file_path)

email_client = EmailClient("me@example.com", "Report Bot")
email_client.send_email_with_attachment(
    to_addresses="client@example.com",
    cc_addresses=["ops@example.com"],
    subject="Weekly Report",
    body="<h1>Attached is your report</h1>",
    attachment_path=file_path
)
```

Here’s the updated `setup.py` with a module docstring and updated dependencies:



## 🔔 Notifications

`Notifications` helps send structured alerts and logs to external communication tools like **Microsoft Teams** and **Zenduty**. Ideal for operational awareness and incident response workflows.

### 🔧 Initialization

```python
from bw_essentials.notifications import Notifications

notifier = Notifications(
    title="BW Alerts",
    summary="Pipeline Failure",
    message="Daily data sync failed.",
    webhook_url="https://sample.webhook.url"
)
```

### ✅ Available Methods

| Method | Description |
|--------|-------------|
| `notify_message(message=None, summary=None, alert=False)` | Send a general log message to Teams |
| `notify_error(message=None, summary=None, alert=True, trace=None, request_id=None)` | Send an error alert to Teams and Zenduty |

- Automatically uses different formats for logs vs. alerts.
- Teams messages are sent via Adaptive Cards.
- Zenduty alerts include critical summaries and tracebacks.
- You can override the default `message`, `summary`, `trace`, and `request_id` per notification.

### 📘 Example Use Case

```python
notifier.notify_error(
    message="ETL job failed due to timeout.",
    summary="Job: daily-prices-sync",
    trace="Traceback (most recent call last): ...",
    request_id="req-123abc"
)
```

---

Let me know if you'd like a logo badge, GitHub Actions setup, or example `.whl` build as well.

## 📬 Contact

For bugs or feature requests, open an issue or contact [support+tech@investorai.in](mailto:your-email@example.com)