#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""File uploader implementation for the MU Invenio CLI application."""
import asyncio
import os

import aiohttp

from mu_invenio_cli.uploaders.base_uploader import BaseUploader


def calculate_chunks(file_size, chunk_size):
    return (file_size + chunk_size - 1) // chunk_size


def calculate_chunk_size(file_size):
    min_chunk_size = 5 * 1024 * 1024
    max_chunk_size = 100 * 1024 * 1024
    max_chunks = 10000

    chunk_size = max(min_chunk_size, (file_size + max_chunks - 1) // max_chunks)
    return min(chunk_size, max_chunk_size)


class MultipartUploader(BaseUploader):
    def upload(self, file_path):
        print(f"Uploading file: {file_path}")
        file_name = file_path.split("/")[-1]
        file_size = os.path.getsize(file_path)
        chunk_size = calculate_chunk_size(file_size)
        chunks = calculate_chunks(file_size, chunk_size)

        init_data = [{
            "key": file_name,
            "size": file_size,
            "transfer": {
                "type": "M",
                "parts": chunks,
                "part_size": chunk_size
            }
        }]
        init_file = self.init_file(file_name, init_data)
        if not init_file:
            return 0
        print(f"[1/3]: File {file_name} - initialized")
        parts = init_file.get("links", {}).get("parts", {})
        if not parts or len(parts) != chunks:
            print("Error: Invalid parts information from server.")
            return -1
        upload_success = asyncio.run(
            self.upload_parts_async(file_path, file_name, parts, chunk_size)
        )
        if not upload_success:
            return -1
        print(f"[2/3]: File content - uploaded")
        commit_success = self.commit_file(file_name)
        if not commit_success:
            return -1
        print(f"[3/3]: File {file_name} - created")
        return 1

    async def upload_part(self, session, semaphore, file_path, part_info, chunk_size, max_retries=3):
        part_number = part_info["part"]
        url = part_info["url"]
        offset = (part_number - 1) * chunk_size

        async with semaphore:
            for attempt in range(1, max_retries + 1):
                try:
                    with open(file_path, "rb") as f:
                        f.seek(offset)
                        data = f.read(chunk_size)
                    async with session.put(url, data=data) as resp:
                        if resp.status in (200, 201, 204):
                            print(f"Uploaded part {part_number}")
                            return True
                        else:
                            print(f"Failed part {part_number}, status: {resp.status}")
                except Exception as e:
                    print(f"Error uploading part {part_number}: {e}")
                if attempt == max_retries:
                    print(f"Giving up on part {part_number} after {max_retries} attempts.")
                    return False

    async def upload_parts_async(self, file_path, file_name, parts, chunk_size, max_retries=3):
        semaphore = asyncio.Semaphore(10)
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.upload_part(session, semaphore, file_path, part_info, chunk_size, max_retries)
                for part_info in parts
            ]
            results = await asyncio.gather(*tasks)
        if all(results):
            print("All parts uploaded successfully.")
            return True
        else:
            print("Some parts failed to upload.")
            return False
