# vyomcloudbridge/queue_writer_file.py
from datetime import datetime, timezone
import time
import random
import configparser
import os
import signal
import sys
from typing import Dict, Any, List, Tuple
import hashlib
import mimetypes
from pathlib import Path
import json
import base64
from vyomcloudbridge.services.chunk_merger import ChunkMerger
from vyomcloudbridge.services.rabbit_queue.queue_main import RabbitMQ
from vyomcloudbridge.utils.common import get_file_info
from vyomcloudbridge.utils.configs import Configs
from vyomcloudbridge.utils.logger_setup import setup_logger
from vyomcloudbridge.constants.constants import (
    MAX_FILE_SIZE,
    data_buffer_key,
    default_project_id,
)


# logger = setup_logger(name=__name__, show_terminal=False)


class QueueWriterFile:
    """Main class for handling message queue writing operations."""

    # Mapping file extensions to data types
    def __init__(self):
        self.rabbit_mq = RabbitMQ()
        self.machine_config = Configs.get_machine_config()
        self.machine_id = self.machine_config.get("machine_id", "-") or "-"
        self.organization_id = self.machine_config.get("organization_id", "-") or "-"
        self.logger = setup_logger(
            name=self.__class__.__module__ + "." + self.__class__.__name__,
            show_terminal=True,
        )
        self.chunk_merger = ChunkMerger()
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            self.logger.info("Shutting down...")
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def _calculate_md5(self, data: bytes) -> str:
        """Calculate MD5 hash of binary data."""
        return hashlib.md5(data).hexdigest()

    def _read_file_in_chunks(self, filepath: str) -> Tuple[List[bytes], str]:
        """
        Read file in chunks and calculate MD5.
        Returns: (list of chunks, MD5 hash)
        """
        chunks = []
        md5_hash = hashlib.md5()
        try:
            with open(filepath, "rb") as file:
                while True:
                    chunk = file.read(MAX_FILE_SIZE)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    md5_hash.update(chunk)
            return chunks, md5_hash.hexdigest()
        except Exception as e:
            self.logger.error("Error reading file-", {filepath})
            raise IOError(f"Error reading file {filepath}: {str(e)}")

    def _read_file(self, filepath: str) -> Tuple[List[bytes], str]:
        """
        Read file in chunks and calculate MD5.
        Returns: (file_data, MD5 hash)
        """
        try:
            with open(filepath, "rb") as file:
                file_data = file.read()
            file_md5 = hashlib.md5(file_data).hexdigest()
            return file_data, file_md5
        except Exception as e:
            self.logger.error("Error reading file-", {filepath})
            raise IOError(f"Error reading file {filepath}: {str(e)}")

    def write_from_file(
        self,
        filepath: str,
        properties: Dict,
        data_source: str,
        file_dir: str,
        chunk_dir: str,
        merge_chunks: bool,
        buffer_key: str,  # str(mission_id) OR {data_buffer_key}
        priority: int,
        destination_ids,
    ) -> None:
        try:
            # Validate filepath
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")

            # Get file information
            filename, file_extension, data_type, file_size = get_file_info(filepath)
            should_chunk = file_size > MAX_FILE_SIZE

            if should_chunk:
                file_chunks, file_md5 = self._read_file_in_chunks(filepath)
            else:
                file_data, file_md5 = self._read_file(filepath)
                file_chunks = []

            # Send file info message
            file_info_data = {
                "filename": f"{filename}.{file_extension}",
                "data_type": data_type,
                "file_md5": file_md5,
                "total_size": file_size,
                "file_dir": file_dir,
                "properties": properties,
            }

            if should_chunk:
                file_info_data.update(
                    {
                        "is_chunked": True,
                        "total_chunks": len(file_chunks),
                        "chunk_dir": chunk_dir,
                        "merge_chunks": merge_chunks,
                        "chunk_name": filename,
                    }
                )
            else:
                file_info_data.update(
                    {
                        "is_chunked": False,
                    }
                )

            message_body = json.dumps(file_info_data)
            file_properties_topic = f"{file_dir}/file_properties/{filename}.json"
            headers = {
                "topic": file_properties_topic,
                "message_type": "json",
                "destination_ids": destination_ids,
                "data_source": data_source,
                # meta data
                "buffer_key": buffer_key,
                "buffer_size": 0,
                "data_type": data_type,
            }
            self.rabbit_mq.enqueue_message(
                message=message_body, headers=headers, priority=priority
            )
            self.logger.info(
                f"Data enqueued to {file_properties_topic}, with priority: {priority}"
            )

            # Send file content
            if should_chunk:
                # Send chunk messages
                total_chunks = len(file_chunks)
                padding_length = len(str(total_chunks))
                for i, chunk in enumerate(file_chunks):
                    try:
                        formatted_index = str(i + 1).zfill(padding_length)
                        message_body = chunk
                        headers = {
                            "message_type": "binary",
                            "topic": f"{chunk_dir}/{filename}_{formatted_index}.bin",
                            "destination_ids": destination_ids,
                            "data_source": data_source,
                            # meta data
                            "buffer_key": buffer_key,
                            "buffer_size": len(chunk),
                            "data_type": data_type,
                        }
                        self.rabbit_mq.enqueue_message(
                            message=message_body, headers=headers, priority=priority
                        )

                    except Exception as e:
                        self.logger.error("Error in publishing chunk-", i, e)
                self.logger.info(
                    f"Data enqueued to all {chunk_dir}/{filename}_*.bin, with priority: {priority}"
                )
                if merge_chunks:
                    s3_prop_key = f"{file_dir}/file_properties/{filename}.json"
                    self.chunk_merger.on_chunk_file_arrive(s3_prop_key)
            else:
                # Send the entire file for small files
                try:
                    message_body = file_data
                    headers = {
                        "message_type": "binary",
                        "topic": f"{file_dir}/{filename}.{file_extension}",
                        "destination_ids": destination_ids,
                        "data_source": data_source,
                        # meta data
                        "buffer_key": buffer_key,
                        "buffer_size": len(file_data),
                        "data_type": data_type,
                    }
                    self.rabbit_mq.enqueue_message(
                        message=message_body, headers=headers, priority=priority
                    )
                    self.logger.info(
                        f"Data enqueued to {file_dir}/{filename}.{file_extension}, with priority: {priority}"
                    )
                except Exception as e:
                    self.logger.error(f"Error in publishing file: {e}")
        except Exception as e:
            self.logger.error(f"Error in write_from_file: {e}")
            raise

    def cleanup(self):
        """Clean up resources."""
        if self.chunk_merger:
            try:
                self.chunk_merger.stop()
                self.logger.info("chunk_merger cleaned up successfully")
            except Exception as e:
                self.logger.error(
                    f"Error cleaning chunk_merger: {str(e)}", exc_info=True
                )

        try:
            self.rabbit_mq.close()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def is_healthy(self):
        """
        Override health check to add additional service-specific checks.
        """
        return self.rabbit_mq.is_healthy() and self.chunk_merger.is_healthy()

    def __del__(self):
        """Destructor called by garbage collector to ensure resources are cleaned up, when object is about to be destroyed"""
        try:
            if self.is_healthy():
                self.logger.error(
                    "Destructor called by garbage collector to cleanup QueueWriterFile"
                )
                self.cleanup()
        except Exception as e:
            pass


def main():
    writer = QueueWriterFile()
    machine_config = Configs.get_machine_config()

    try:
        print(f"pushing all files")
        # Example usage with actual files
        # test_files = [
        #     ("/path/to/image.jpg", "camera1", "34556", 1),
        #     ("/path/to/video.mp4", "camera2", "34556", 2),
        #     ("/path/to/document.pdf", "event", "34556", 1),
        # ]

        test_files = [
            # ("/Users/amardeepsaini/Documents/VYOM/vyom-mqtt/mqtt_pub_sub/file/232561_small.mp4", "camera1", "34556", 2),
            # ("/Users/amardeepsaini/Documents/VYOM/vyom-mqtt/mqtt_pub_sub/file/elephant_istockphoto.jpg", "camera1", "34556", 1),
            # ("/Users/amardeepsaini/Documents/VYOM/vyom-mqtt/mqtt_pub_sub/file/elephant_maximus.jpg", "camera1", "34556", 1),
            # (
            #     "/Users/amardeepsaini/Documents/VYOM/vyom-mqtt/mqtt_pub_sub/file/Equine_Trot_400fps_Right.avi",
            #     "camera1",
            #     "34556",
            #     1,
            # ),
            (
                "/Users/amardeepsaini/Documents/VYOM/vyom-mqtt/mqtt_pub_sub/file/sample_20.mp4",
                "camera1",
                "34556",
                1,
            ),
            # (
            #     "/Users/amardeepsaini/Documents/VYOM/vyom-mqtt/mqtt_pub_sub/file/sample_70.mp4",
            #     "camera1",
            #     "34556",
            #     1,
            # ),
            # (
            #     "/Users/amardeepsaini/Documents/VYOM/vyom-mqtt/mqtt_pub_sub/file/sample_140.mp4",
            #     "camera1",
            #     "34556",
            #     1,
            # ),
        ]
        properties = {
            "mission_id": 33444,
            "data_source": "camera2",
        }
        machine_id = machine_config.get("machine_id", "-") or "-"

        for file_path in test_files:
            try:
                writer.write_from_file(
                    filepath=file_path,
                    properties=properties,
                    data_source="camera2",
                    file_dir=f"1/{default_project_id}/2025-02-21/{machine_id}/23444/camera1/",
                    chunk_dir=f"1/{default_project_id}/2025-02-21/{machine_id}/23444/camera1/chunk",
                    merge_chunks=False,
                    buffer_key=str(33444),
                    priority=2,
                    destination_ids=["s3"],
                )
            except FileNotFoundError as e:
                print(f"File not found: {file_path}", str(e))
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        writer.cleanup()


if __name__ == "__main__":
    main()
