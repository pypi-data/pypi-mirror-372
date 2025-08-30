# In a new shared file (e.g., shared_memory_utils.py)
import json
import pickle
import os
from multiprocessing import shared_memory
import threading
from vyomcloudbridge.utils.logger_setup import setup_logger


class SharedMemoryUtil:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SharedMemoryUtil, cls).__new__(cls)
                    cls._instance.logger = setup_logger(
                        name=cls.__module__ + "." + cls.__name__,
                        show_terminal=False,
                    )
                    cls._instance._init_shared_memory()
        return cls._instance

    def _init_shared_memory(self):
        # Define initial empty dict
        init_data = {}
        serialized_data = pickle.dumps(init_data)

        # Size with some buffer for growth
        buffer_size = max(len(serialized_data) * 10, 10240)  # At least 10KB

        try:
            # Try to attach to existing shared memory
            self.shm = shared_memory.SharedMemory(name="mavlink_ack_data")
        except FileNotFoundError:
            self.shm = self._create_shared_memory_with_permissions(
                "mavlink_ack_data", buffer_size
            )
            # Initialize with empty dict, and store the length
            self.shm.buf[: len(serialized_data)] = serialized_data
            length_bytes = len(serialized_data).to_bytes(4, byteorder="little")
            self.shm.buf[buffer_size - 4 : buffer_size] = length_bytes
        except PermissionError:
            # try:
            #     # Try to unlink/clean any existing stale shared memory
            #     temp_shm = shared_memory.SharedMemory(name="mavlink_ack_data")
            #     temp_shm.close()
            #     temp_shm.unlink()
            #     try:  # Here we are cleared memory and recreating it
            #         self.shm = self._create_shared_memory_with_permissions(
            #             "mavlink_ack_data", buffer_size
            #         )
            #         # Initialize with empty dict, and store the length
            #         self.shm.buf[: len(serialized_data)] = serialized_data
            #         length_bytes = len(serialized_data).to_bytes(4, byteorder="little")
            #         self.shm.buf[buffer_size - 4 : buffer_size] = length_bytes
            #     except Exception as e:
            #         self.logger.error(f"Error recreating shared memory: {e}")
            #         raise
            # except PermissionError:
            #     self.logger.error("Permission error in unlinking shared memory")
            #     raise
            # except Exception as e:
            #     self.logger.error(
            #         f"Error in unlinking shared memory, unknown error: {e}"
            #     )
            self.logger.error(
                f"Permission denied error attaching to shared memory, error: {e}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Error in attaching to shared memory, unknown error: {e}"
            )
            raise

    def _create_shared_memory_with_permissions(self, data_name, buffer_size):
        """Set shared memory permissions to be accessible by all users"""
        try:
            old_umask = os.umask(0)
            try:
                shm = shared_memory.SharedMemory(
                    name=data_name, create=True, size=buffer_size
                )
                return shm
            finally:
                os.umask(old_umask)
        except Exception as e:
            self.logger.error(
                f"Failed to create shared memory for dt={data_name}, sz={buffer_size}, with permissions: {e}"
            )
            raise

    def get_data(self, data_name):
        try:
            # Attach to existing shared memory
            return shared_memory.SharedMemory(name=data_name)
        except FileNotFoundError:
            # If it doesn't exist, return None or raise an error
            return None

    def set_data(self, data_name, data):
        with self._lock:
            try:
                # Try to create new shared memory
                shm = self._create_shared_memory_with_permissions(data_name, 1)
                shm.close()
            except FileExistsError:
                # If it already exists, that's fine - we can use it
                pass
            except PermissionError:
                self.logger.error(
                    "Permission error in set_data for data_name: " + data_name
                )
                # If permission denied, try to clean up and recreate
                try:
                    temp_shm = shared_memory.SharedMemory(name=data_name)
                    temp_shm.close()
                    temp_shm.unlink()
                    # Try again after cleanup
                    shm = self._create_shared_memory_with_permissions(data_name, 1)
                    shm.close()
                except (FileNotFoundError, PermissionError, FileExistsError):
                    # If still can't access, just return without failing
                    return

    def cleanup(self):
        self.shm.close()
        # Unlink only when the application is shutting down
        # to avoid removing shared memory while other processes are using it
        self.shm.unlink()
