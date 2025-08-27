import time
import threading
import os
import json
import base64
import uuid
from typing import Callable
from awscrt import mqtt
from awsiot import mqtt_connection_builder
from concurrent.futures import TimeoutError
from vyomcloudbridge.utils.configs import Configs
from vyomcloudbridge.utils.logger_setup import setup_logger
from vyomcloudbridge.constants.constants import (
    cert_file_path,
    pri_key_file_path,
    root_ca_file_path,
    MQTT_ENTPOINT,
)
from vyomcloudbridge.utils.abc_sender import AbcSender


class AwsiotMqttSender(AbcSender):
    def __init__(self, daemon: bool = False):
        try:
            super().__init__()
            self.logger.info("AwsiotMqttSender initializing...")
            # compulsory
            self.channel = "mqtt"
            self.combine_by_target_id = True

            # machine specific
            self.machine_config = Configs.get_machine_config()
            self.machine_id = self.machine_config.get("machine_id", "-") or "-"
            self.client_id = f"machine{self.machine_id}Prod-{uuid.uuid4().hex[:8]}"  # using different clients for each sender

            # class specific
            self.daemon = daemon
            self.endpoint = MQTT_ENTPOINT
            self.cert_path = cert_file_path
            self.pri_key_path = pri_key_file_path
            self.root_ca_path = root_ca_file_path
            self.client_id = f"machine{self.machine_id}Prod-{uuid.uuid4().hex[:8]}"

            self._verify_cert_files()

            # Connection state tracking
            self.is_connected = False
            self.connection_lock = threading.Lock()
            self._connection_in_progress = False

            # Connection and reconnection parameters
            self.max_reconnect_attempts = 3
            self.base_reconnect_delay = 2  # Base delay in seconds
            self.max_reconnect_delay = 60

            self.connection_retry_loop_delay = 30  # seconds

            # Initialize the MQTT connection
            self.mqtt_connection = None
            if self.daemon:
                # self._start_background_connection()
                self._start_backgd_conn_monitor()
                self.logger.info(
                    "AwsiotMqttSender initialization in background thread started..."
                )
            else:
                self._create_mqtt_connection()
                self._start_backgd_conn_monitor()
                self.logger.info("AwsiotMqttSender initialized successfully!")

        except Exception as e:
            self.logger.error(f"Error init AwsiotMqttSender error: {str(e)}")
            raise

    def _create_mqtt_connection(self):
        """Create a new MQTT connection with exponential backoff"""
        with self.connection_lock:  # Acquire lock to prevent concurrent attempts
            if self.is_connected:
                self._connection_in_progress = False
                self.logger.info(
                    "Connection already established, skipping reconnection"
                )
                return

            self._connection_in_progress = True
            try:
                for attempt in range(self.max_reconnect_attempts):
                    try:
                        # Use exponential backoff for reconnection attempts
                        delay = min(
                            self.base_reconnect_delay * (2**attempt),
                            self.max_reconnect_delay,
                        )

                        # Create MQTT connection with keep-alive and will message
                        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
                            endpoint=self.endpoint,
                            cert_filepath=self.cert_path,
                            pri_key_filepath=self.pri_key_path,
                            ca_filepath=self.root_ca_path,
                            client_id=self.client_id,
                            clean_session=False,
                            keep_alive_secs=1200,  # 20 minutes
                            ping_timeout_ms=3000,  # 3 seconds
                            on_connection_interrupted=self._on_connection_interrupted,
                            on_connection_resumed=self._on_connection_resumed,
                        )

                        # Connect to AWS IoT Core
                        connect_future = self.mqtt_connection.connect()
                        connect_future.result()  # Wait for connection
                        self.is_connected = True
                        self.logger.info("Successfully connected to AWS IoT Core")
                        return

                    except Exception as e:
                        self.logger.debug(
                            f"Warning: AWS IoT core connection attempt {attempt + 1} failed, error: {str(e)}"
                        )
                        if attempt < self.max_reconnect_attempts - 1:
                            time.sleep(delay)

                # If all attempts fail
                raise ConnectionError(
                    f"Could not connect to AWS IoT Core after {self.max_reconnect_attempts} attempts"
                )

            finally:
                self._connection_in_progress = False

    # def _start_background_connection(self):
    #     """Start connection attempts in a background thread"""

    #     def connection_thread():
    #         while True:
    #             try:
    #                 if not self.is_connected and not self._connection_in_progress:
    #                     self._create_mqtt_connection()
    #                     self._start_backgd_conn_monitor()
    #                 time.sleep(self.connection_retry_loop_delay)
    #             except Exception as e:
    #                 self.logger.error(f"Background connection thread error: {str(e)}")
    #                 time.sleep(self.connection_retry_loop_delay)

    #     # Start connection thread
    #     connection_thread = threading.Thread(target=connection_thread, daemon=True)
    #     connection_thread.start()

    def _start_backgd_conn_monitor(self):
        """
        Start a background thread to monitor connection health
        Uses built-in AWS IoT SDK reconnection mechanisms
        """

        def monitor_connection():
            while True:
                try:
                    if not self.is_connected:
                        self._create_mqtt_connection()
                    time.sleep(self.connection_retry_loop_delay)
                except Exception as e:
                    self.logger.error(f"Connection monitoring failed, error: {str(e)}")
                    time.sleep(self.connection_retry_loop_delay)

        # Start monitoring in a daemon thread
        monitor_thread = threading.Thread(target=monitor_connection, daemon=True)
        monitor_thread.start()

    def _verify_cert_files(self):
        for file_path in [self.cert_path, self.pri_key_path, self.root_ca_path]:
            if not os.path.exists(file_path):
                self.logger.error(f"ERROR: File not found: {file_path}")
                raise FileNotFoundError(f"Required file not found: {file_path}")
            else:
                with open(file_path, "r") as f:
                    pass

    def _on_connection_interrupted(self, connection, error, **kwargs):
        """
        Callback when connection is interrupted
        This method is called automatically by AWS IoT SDK
        """
        self.logger.warning(f"Connection interrupted, error: {error}")
        with self.connection_lock:
            self.is_connected = False

    def _on_connection_resumed(
        self, connection, return_code, session_present, **kwargs
    ):
        """
        Callback when connection is resumed
        This method is called automatically by AWS IoT SDK
        """
        if return_code == mqtt.ConnectReturnCode.ACCEPTED:
            self.logger.info("Connection resumed successfully")

            with self.connection_lock:
                self.is_connected = True
        else:
            self.logger.error(
                f"Connection resume failed with return code: {return_code}"
            )

    def publish_message_to_topic(self, topic: str, payload):
        """
        Publish message with connection state check
        """
        try:
            # TODO remove later
            start_time_in_epoch = int(time.time() * 1000)

            path_parts = topic.split("/")
            if len(path_parts) > 8:
                self.logger.error(
                    "Topic length exceeded - a maximum of 8 sub-parts are allowed in a topic."
                )
                return False

            # with self.connection_lock:
            #     if not self.is_connected and self._connection_in_progress:
            #         self.logger.error(
            #             f"Publish to {topic} failed: aws iot core is not connected"
            #         )
            #         return False

            # Outside the lock, create connection if needed
            if not self.is_connected:
                self.logger.debug(
                    "Warning: MQTT connection not established, skipping publishing..."
                )
                return False
            self.logger.debug(f"Message publishing...... to topic: {topic}")
            publish_future, _ = self.mqtt_connection.publish(
                topic=topic, payload=payload, qos=mqtt.QoS.AT_LEAST_ONCE
            )
            publish_future.result(timeout=10)
            self.logger.debug(f"Message published to topic: {topic}")

            # TODO remove later
            end_time_in_epoch = int(time.time() * 1000)
            time_diff = end_time_in_epoch - start_time_in_epoch
            self.logger.debug(f"MQTT time ms= {time_diff}")

            return True
        except TimeoutError:

            # TODO remove later
            end_time_in_epoch = int(time.time() * 1000)
            time_diff = end_time_in_epoch - start_time_in_epoch
            self.logger.debug(f"MQTT timeout ms= {time_diff}")

            self.logger.error(
                f"Publish to {topic} failed: TimeoutError, exiting in ms= {time_diff}"
            )
            return False
        except Exception as e:
            self.logger.error(
                f"Publish to {topic} failed, error: {str(e)} , message_type={type(payload)}"
            )
            return False

    def _get_topic(self, dest_id, data_source, filename):
        return f"vyom-mqtt-msg/{dest_id}/{self.machine_id}/{data_source}/{filename}"

    def send_message(
        self,
        message,
        message_type,
        data_source,
        target_des_id,
        destination_id,
        source_id,
        topic,
    ):
        """
        Publish message with connection state check
        """
        try:
            filename = topic.split("/")[-1]  # Extract the filename from the topic path
            topic = (
                topic
                if target_des_id == "s3"
                else self._get_topic(target_des_id, data_source, filename)
            )
            result = self.publish_message_to_topic(topic, message)
            if result:
                self.logger.debug(
                    f"Message successfully sent to target_des_id-{target_des_id}, having topic-{topic}"
                )
            return result
        except Exception as e:
            self.logger.error(f"Publish to {topic} failed error: {str(e)}")
            return False

    def is_healthy(self):
        """Gracefully close the MQTT connection"""
        try:
            if self.mqtt_connection:
                disconnect_future = self.mqtt_connection.disconnect()
                disconnect_future.result(timeout=10)
                self.mqtt_connection = None

            with self.connection_lock:
                self.is_connected = False

            self.logger.info("MQTT AWS IoT Core connection closed successfully")

        except Exception as e:
            self.logger.error(f"Failed to close MQTT connection error: {str(e)}")

    def cleanup(self):
        """Gracefully close the MQTT connection"""
        try:
            if self.mqtt_connection:
                disconnect_future = self.mqtt_connection.disconnect()
                disconnect_future.result(timeout=10)
                self.mqtt_connection = None

            with self.connection_lock:
                self.is_connected = False

            self.logger.info("MQTT AWS IoT Core connection closed successfully")

        except Exception as e:
            self.logger.error(f"Failed to close MQTT connection error: {str(e)}")


logger = setup_logger(name=__name__, show_terminal=True)


def minimal_mqtt_sender_example():
    try:
        # Initialize AwsiotMqttSender
        sender = AwsiotMqttSender()
        machine_id = sender.machine_id
        message = {
            "timestamp": "2025-04-10T10:00:00Z",
            "data": {"status": "online", "temperature": 25.5, "humidity": 60},
        }
        result = sender.send_message(
            message=json.dumps(message),
            message_type="json",
            data_source="sample_source",
            target_des_id="s3",
            destination_id="s3",
            source_id=machine_id,
            topic="vyom-mqtt-msg/s3/" + str(machine_id) + "/sample_topic",
        )

        if result:
            logger.info("Message sent successfully")
        else:
            logger.error("Failed to send message")

        # Close the connection when done
        sender.cleanup()

    except Exception as e:
        logger.error(f"Error in minimal_mqtt_sender_example error: {str(e)}")


if __name__ == "__main__":
    minimal_mqtt_sender_example()
