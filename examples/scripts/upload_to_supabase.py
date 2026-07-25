#!/usr/bin/env python3
"""
Supabase Storage Upload Script for Project Athena
Upload files to Supabase Storage buckets.
"""

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv

from supabase import Client, create_client

# Load environment
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Default buckets
DEFAULT_BUCKETS = ["sessions", "exports", "diagrams"]


def get_client() -> Client:
    """Create and return Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Missing Supabase credentials in .env")
        sys.exit(1)
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_file(supabase: Client, file_path: str, bucket: str, remote_path: str = None):
    """Upload a single file to a bucket."""
    path = Path(file_path)

    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return None

    # Use filename as remote path if not specified
    remote_path = remote_path or path.name

    try:
        with open(path, "rb") as f:
            file_bytes = f.read()

        # Upload to Supabase Storage
        supabase.storage.from_(bucket).upload(
            path=remote_path,
            file=file_bytes,
            file_options={"content-type": _get_content_type(path.suffix)}
        )

        # Get public URL
        public_url = supabase.storage.from_(bucket).get_public_url(remote_path)

        print(f"✅ Uploaded: {path.name} → {bucket}/{remote_path}")
        print(f"   URL: {public_url}")
        return public_url

    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print(f"⏭️  Already exists: {bucket}/{remote_path}")
            return supabase.storage.from_(bucket).get_public_url(remote_path)
        print(f"❌ Upload failed: {e}")
        return None


def upload_directory(supabase: Client, dir_path: str, bucket: str, prefix: str = ""):
    """Upload all files in a directory to a bucket in parallel."""
    path = Path(dir_path)

    if not path.exists() or not path.is_dir():
        print(f"❌ Directory not found: {dir_path}")
        return

    files = list(path.glob("*"))
    # Filter for files only
    files = [f for f in files if f.is_file()]

    if not files:
        print(f"📂 No files found in {dir_path}")
        return

    print(f"📁 Uploading {len(files)} files from {dir_path} to {bucket}/ (Parallel Mode)...")

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_file = {}
        for file_path in files:
            remote_path = f"{prefix}/{file_path.name}" if prefix else file_path.name
            future = executor.submit(upload_file, supabase, str(file_path), bucket, remote_path)
            future_to_file[future] = file_path

        completed = 0
        file_count = len(files)

        for future in as_completed(future_to_file):
            f = future_to_file[future]
            try:
                future.result()
                completed += 1
            except Exception as e:
                print(f"❌ Error uploading {f.name}: {e}")

        if completed == file_count:
            print(f"✅ Uploaded {completed}/{file_count} file(s) to {bucket}/{prefix}")
        else:
            print(f"⚠️  Uploaded {completed}/{file_count} file(s) to {bucket}/{prefix} — "
                  f"{file_count - completed} failed")


def list_files(supabase: Client, bucket: str, prefix: str = ""):
    """List files in a bucket."""
    try:
        result = supabase.storage.from_(bucket).list(prefix)

        if not result:
            print(f"📂 {bucket}/ is empty")
            return

        print(f"📂 Files in {bucket}/{prefix}:")
        for item in result:
            name = item.get("name", "unknown")
            size = item.get("metadata", {}).get("size", 0)
            size_kb = size / 1024 if size else 0
            print(f"   • {name} ({size_kb:.1f} KB)")

    except Exception as e:
        print(f"❌ Error listing files: {e}")


def download_file(supabase: Client, bucket: str, remote_path: str, local_path: str = None):
    """Download a file from a bucket."""
    try:
        result = supabase.storage.from_(bucket).download(remote_path)

        local_path = local_path or Path(remote_path).name
        with open(local_path, "wb") as f:
            f.write(result)

        print(f"✅ Downloaded: {bucket}/{remote_path} → {local_path}")
        return local_path

    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None


def create_bucket(supabase: Client, bucket: str, public: bool = False):
    """Create a new storage bucket."""
    try:
        supabase.storage.create_bucket(bucket, options={"public": public})
        visibility = "public" if public else "private"
        print(f"✅ Created bucket: {bucket} ({visibility})")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"⏭️  Bucket already exists: {bucket}")
        else:
            print(f"❌ Failed to create bucket: {e}")


def _get_content_type(suffix: str) -> str:
    """Get content type from file extension."""
    content_types = {
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".json": "application/json",
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".py": "text/x-python",
    }
    return content_types.get(suffix.lower(), "application/octet-stream")


def main():
    parser = argparse.ArgumentParser(description="Supabase Storage Manager for Athena")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Upload file
    upload_parser = subparsers.add_parser("upload", help="Upload a file")
    upload_parser.add_argument("file", help="File to upload")
    upload_parser.add_argument("--bucket", "-b", default="exports", help="Target bucket")
    upload_parser.add_argument("--name", "-n", help="Remote filename (default: same as local)")

    # Upload directory
    upload_dir_parser = subparsers.add_parser("upload-dir", help="Upload a directory")
    upload_dir_parser.add_argument("directory", help="Directory to upload")
    upload_dir_parser.add_argument("--bucket", "-b", default="exports", help="Target bucket")
    upload_dir_parser.add_argument("--prefix", "-p", default="", help="Remote path prefix")

    # List files
    list_parser = subparsers.add_parser("list", help="List files in a bucket")
    list_parser.add_argument("bucket", help="Bucket name")
    list_parser.add_argument("--prefix", "-p", default="", help="Path prefix")

    # Download file
    download_parser = subparsers.add_parser("download", help="Download a file")
    download_parser.add_argument("bucket", help="Bucket name")
    download_parser.add_argument("file", help="Remote file path")
    download_parser.add_argument("--output", "-o", help="Local output path")

    # Create bucket
    create_parser = subparsers.add_parser("create-bucket", help="Create a new bucket")
    create_parser.add_argument("bucket", help="Bucket name")
    create_parser.add_argument("--public", action="store_true", help="Make bucket public")

    # Init buckets
    subparsers.add_parser("init", help="Initialize default buckets")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    supabase = get_client()
    print(f"🔌 Connected to Supabase: {SUPABASE_URL}")

    if args.command == "upload":
        upload_file(supabase, args.file, args.bucket, args.name)

    elif args.command == "upload-dir":
        upload_directory(supabase, args.directory, args.bucket, args.prefix)

    elif args.command == "list":
        list_files(supabase, args.bucket, args.prefix)

    elif args.command == "download":
        download_file(supabase, args.bucket, args.file, args.output)

    elif args.command == "create-bucket":
        create_bucket(supabase, args.bucket, args.public)

    elif args.command == "init":
        print("🚀 Initializing default buckets...")
        for bucket in DEFAULT_BUCKETS:
            create_bucket(supabase, bucket, public=False)
        print("✅ Done!")


if __name__ == "__main__":
    main()
