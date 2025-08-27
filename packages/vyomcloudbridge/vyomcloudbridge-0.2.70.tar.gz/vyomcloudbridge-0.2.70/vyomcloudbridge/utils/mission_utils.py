from tracemalloc import start
import pika
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Union
import time
from vyomcloudbridge.services.rabbit_queue.queue_main import RabbitMQ
from vyomcloudbridge.constants.constants import (
    DEFAULT_RABBITMQ_URL,
)
from vyomcloudbridge.utils.configs import Configs
from vyomcloudbridge.utils.common import get_mission_upload_dir
from vyomcloudbridge.constants.constants import (
    default_project_id,
)
from vyomcloudbridge.utils.logger_setup import setup_logger


class MissionUtils:
    """
    A service that maintains mission data statistics using RabbitMQ as a persistent store.
    Each mission_id has its own queue in RabbitMQ that stores the latest state of its data.
    Also maintains current mission and current user data in dedicated queues.
    """

    def __init__(self):
        """
        Initialize the mission data service with RabbitMQ connection.

        Args:
            rabbitmq_url: Connection URL for RabbitMQ
            logger: Optional logger instance
        """
        self.logger = setup_logger(
            name=self.__class__.__module__ + "." + self.__class__.__name__,
            show_terminal=False,
        )
        self.host: str = "localhost"
        self.rabbitmq_url = DEFAULT_RABBITMQ_URL
        self.mission_live_priority = 3

        self.rmq_conn = None
        self.rmq_channel = None
        self.rabbit_mq = RabbitMQ()
        self.machine_config = Configs.get_machine_config()
        self.machine_id = self.machine_config.get("machine_id", "-") or "-"
        self.organization_id = self.machine_config.get("organization_id", "-") or "-"
        self.data_source_stats = "mission_stats"
        self.data_source_mission = "mission_message"
        self.data_source_summary = "mission_summary"
        self.current_mission_queue = "current_mission"
        self.last_mission_queue = "last_mission"

    def generate_mission_id(self):
        try:
            epoch_ms = int(time.time() * 1000)
            mission_id = f"{epoch_ms}{self.machine_id}"
            return int(mission_id)
        except Exception as e:
            self.logger.error(f"Failed to generate unique mission_id: {str(e)}")
            raise

    def _setup_connection(self):
        """Set up RabbitMQ connection and declare the exchange for mission data."""
        try:
            # Establish connection
            self.rmq_conn = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            # self.rmq_conn = pika.BlockingConnection(
            #     pika.ConnectionParameters(
            #         host=self.host,
            #         heartbeat=600,
            #         blocked_connection_timeout=300,
            #         socket_timeout=300,
            #     )
            # )
            self.rmq_channel = self.rmq_conn.channel()
            self.rmq_channel.queue_declare(
                queue=self.current_mission_queue, durable=True
            )
            self.rmq_channel.queue_declare(queue=self.last_mission_queue, durable=True)

            self.logger.info("RabbitMQ connection established successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize RabbitMQ: {str(e)}")
            raise

    def _ensure_connection(self) -> bool:
        """Ensure connection and channel are active and working"""
        try:
            if not self.rmq_conn or self.rmq_conn.is_closed:
                self._setup_connection()
                return True

            if not self.rmq_channel or self.rmq_channel.is_closed:
                self.logger.info("Closed channel found, re-establishing...")
                self.rmq_channel = self.rmq_conn.channel()
                self.rmq_channel.queue_declare(
                    queue=self.current_mission_queue, durable=True
                )
                self.logger.info("Channel re-established successfully")

            return True
        except Exception as e:
            self.logger.error(f"Failed to ensure connection: {e}")
            self.rmq_conn = None
            self.rmq_channel = None
            return False

    def get_last_mission(self) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Retrieve the current mission details from RabbitMQ.

        Returns:
            Tuple:
                - dict or None: Current mission details if available, else None
                - str or None: Error message if any issue occurs, else None
        """
        try:
            if not self._ensure_connection() or not self.rmq_channel:
                error_message = "Could not establish connection"
                self.logger.error(error_message)
                return None, error_message

            method_frame, _, body = self.rmq_channel.basic_get(
                queue=self.last_mission_queue, auto_ack=False
            )

            mission_detail = None
            if method_frame:
                mission_detail = json.loads(body.decode("utf-8"))
                self.rmq_channel.basic_nack(
                    delivery_tag=method_frame.delivery_tag, requeue=True
                )
                self.logger.info(
                    f"Retrieved last mission: {mission_detail.get('id', 'unknown')}"
                )
            return mission_detail, None
        except Exception as e:
            error_message = f"Error getting last mission: {str(e)}"
            self.logger.error(error_message)
            return None, error_message

    def get_current_mission(self) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Retrieve the current mission details from RabbitMQ.

        Returns:
            Tuple:
                - dict or None: Current mission details if available, else None
                - str or None: Error message if any issue occurs, else None
        """
        try:
            if not self._ensure_connection() or not self.rmq_channel:
                error_message = "Could not establish connection"
                self.logger.error(error_message)
                return None, error_message

            method_frame, _, body = self.rmq_channel.basic_get(
                queue=self.current_mission_queue, auto_ack=False
            )

            mission_detail = None
            if method_frame:
                mission_detail = json.loads(body.decode("utf-8"))
                self.rmq_channel.basic_nack(
                    delivery_tag=method_frame.delivery_tag, requeue=True
                )
                self.logger.info(
                    f"Retrieved current mission: {mission_detail.get('id', 'unknown')}"
                )
            return mission_detail, None
        except Exception as e:
            error_message = f"Error getting current mission: {str(e)}"
            self.logger.error(error_message)
            return None, error_message

    def start_mission(
        self,
        id=None,  # Unique mission_id from Vyom services if available
        name=None,  # Human-readable name for the mission
        description=None,  # Description about the mission
        creator_id=None,  # User ID of the person initiating the mission
        owner_id=None,  # If someone else is the mission owner, provide their user ID
        project_id: Optional[Union[str, int]] = None,  # Project ID if available
        mission_date: Optional[str] = None,
        start_time: Optional[str] = None,
        destination_ids: List[Union[str, int]] = ["s3"],  # array of destination_ids
        force_start: bool = False,
    ):
        """
        Start a new mission and publish its details to RabbitMQ for VyomIQ.

        Args:
            id (integer, optional): Unique mission ID. Auto-generated if not provided.
            name (str, optional): Name of the mission. Defaults to timestamp-based string.
            description (str, optional): Description of the mission.
            creator_id (int, optional): ID of the user creating the mission. Defaults to 1.
            owner_id (int, optional): ID of the mission owner. Defaults to creator_id.

        Returns:
            Tuple:
                - dict or None: Mission details if mission is successfully started, else None
                - str or None: Error message if any issue occurs, else None
        """
        if destination_ids and (
            isinstance(destination_ids, str) or isinstance(destination_ids, int)
        ):
            destination_ids = [str(destination_ids)]

        try:
            destination_ids = [str(x) for x in destination_ids]
        except Exception:
            self.logger.warning(
                f"Invalid destination_ids, must be a list of ids[str or int]"
            )
            destination_ids = ["s3"]

        existing_mission, mission_read_error = self.get_current_mission()
        if mission_read_error is not None:
            self.logger.error(
                f"Error in checking existing mission -{mission_read_error}"
            )
            return None, mission_read_error

        if existing_mission is not None:
            if existing_mission.get("mission_status") == 1:
                if force_start:
                    self.logger.info(
                        f"Force starting mission, existing mission with id={existing_mission.get('id')} will be marked completed"
                    )
                    mission_end_success, mission_end_error = self.end_current_mission(
                        destination_ids=destination_ids
                    )
                    if not mission_end_success:
                        self.logger.error(
                            f"Error in marking existing mission as completed: {mission_end_error}"
                        )
                        return None, mission_end_error
                else:
                    existing_mission_id = existing_mission.get("id")
                    error_message = f"Mission with id={existing_mission_id} is already in progress, please complete it OR mark complete before starting new mission"
                    self.logger.error(error_message)
                    return None, error_message
            else:
                pass  # Existing mission already completed, so start new one
        if project_id is not None:
            try:
                project_id = int(project_id)
            except Exception:
                project_id = None
        else:
            project_id = None

        if id is None:
            id = self.generate_mission_id()

        if name is None:
            name = (
                f"M_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')[:-3]}_UTC"
            )

        if mission_date is None:
            if start_time is None:
                mission_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            else:
                try:
                    dt = datetime.fromisoformat(start_time)
                    mission_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    self.logger.warning(
                        f"Invalid start_time: {start_time}, using today's date for mission_date"
                    )
                    mission_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        try:
            if creator_id is None:
                creator_id = 1
            if owner_id is None:
                owner_id = creator_id

            mission_detail = {
                "id": id,
                "name": name,
                "description": description,
                "creator_id": creator_id,
                "owner_id": owner_id,
                "mission_status": 1,
                "campaign_id": project_id,  # campaign ID if available, else None
                "mission_date": mission_date,
                "start_time": start_time or datetime.now(timezone.utc).isoformat(),
                "end_time": None,
                "mission_type": "",
                "machine_id": self.machine_id,
                "json_data": {},
            }

            if not self._ensure_connection() or not self.rmq_channel:
                error_message = "Could not establish connections, please try again"
                return None, error_message

            while True:
                method_frame, _, _ = self.rmq_channel.basic_get(
                    queue=self.current_mission_queue, auto_ack=True
                )
                if not method_frame:
                    break

            self.rmq_channel.basic_publish(
                exchange="",
                routing_key=self.current_mission_queue,
                body=json.dumps(mission_detail),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type="application/json",
                ),
            )
            self.logger.info(
                f"Updated current mission to {mission_detail.get('id', 'unknown')}"
            )

            # Publish mission data in real time
            now = datetime.now(timezone.utc)
            date = now.strftime("%Y-%m-%d")
            filename = int(time.time() * 1000)
            mission_upload_dir: str = get_mission_upload_dir(
                organization_id=self.organization_id,
                machine_id=self.machine_id,
                mission_id=id,
                data_source=self.data_source_mission,
                date=date,
                project_id=default_project_id,
            )

            # message_body = json.dumps({"mission": mission_detail, "data_stats": None})
            message_body = json.dumps(mission_detail)
            headers = {
                "topic": f"{mission_upload_dir}/{filename}.json",
                "message_type": "json",
                "destination_ids": destination_ids,
                "data_source": self.data_source_mission,
                # meta data
                "buffer_key": str(id),
                "buffer_size": 0,
                "data_type": "json",
            }
            self.rabbit_mq.enqueue_message(
                message=message_body,
                headers=headers,
                priority=self.mission_live_priority,
            )

            return mission_detail, None
        except Exception as e:
            error_message = f"Error updating current mission: {str(e)}"
            self.logger.error(error_message)
            return None, error_message

    def end_current_mission(self, destination_ids: List[Union[str, int]] = ["s3"]):
        """
        Mark the current mission as completed, move it to last_mission queue,
        and remove it from current_mission queue.

        Returns:
            Tuple:
            - success (bool): True if mission successfully completed or no active mission found; False if error
            - error_message (str): error message if there is any error, else None in case of success
        """
        try:
            if destination_ids and (
                isinstance(destination_ids, str) or isinstance(destination_ids, int)
            ):
                destination_ids = [str(destination_ids)]

            try:
                destination_ids = [str(x) for x in destination_ids]
            except Exception:
                self.logger.warning(
                    f"Invalid destination_ids, must be a list of ids[str or int]"
                )
                destination_ids = ["s3"]

            mission_detail, mission_read_error = self.get_current_mission()
            if mission_read_error is not None:
                return False, mission_read_error

            if not self._ensure_connection() or not self.rmq_channel:
                error_message = "Could not establish connection"
                return False, error_message

            if mission_detail is not None:
                if mission_detail.get("mission_status") == 1:
                    existing_mission_id = mission_detail.get("id", None)
                    if existing_mission_id is None:
                        error_message = "Mission ID is None in the existing mission. Cannot mark it complete. Removing this object from cache."
                        # Clear the current mission queue
                        self._clear_queue(self.current_mission_queue)
                        return False, error_message

                    # Mark mission as completed
                    mission_detail["mission_status"] = 2
                    mission_detail["end_time"] = datetime.now(timezone.utc).isoformat()

                    # Clear current mission queue (remove completed mission from current)
                    while True:
                        method_frame, _, _ = self.rmq_channel.basic_get(
                            queue=self.current_mission_queue, auto_ack=True
                        )
                        if not method_frame:
                            break

                    # Clear last mission queue first (to store only the latest completed mission)
                    while True:
                        method_frame, _, _ = self.rmq_channel.basic_get(
                            queue=self.last_mission_queue, auto_ack=True
                        )
                        if not method_frame:
                            break

                    # Add completed mission to last_mission queue
                    self.rmq_channel.basic_publish(
                        exchange="",
                        routing_key=self.last_mission_queue,
                        body=json.dumps(mission_detail),
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # make message persistent
                            content_type="application/json",
                        ),
                    )

                    # message_body = json.dumps(
                    #     {"mission": mission_detail, "data_stats": None}
                    # )
                    try:
                        # Publish mission completion data in real time
                        now = datetime.now(timezone.utc)
                        date = now.strftime("%Y-%m-%d")
                        filename = int(time.time() * 1000)
                        mission_upload_dir: str = get_mission_upload_dir(
                            organization_id=self.organization_id,
                            machine_id=self.machine_id,
                            mission_id=existing_mission_id,
                            data_source=self.data_source_mission,
                            date=date,
                            project_id=default_project_id,
                        )

                        message_body = json.dumps(mission_detail)
                        headers = {
                            "topic": f"{mission_upload_dir}/{filename}.json",
                            "message_type": "json",
                            "destination_ids": destination_ids,
                            "data_source": self.data_source_mission,
                            # meta data
                            "buffer_key": str(existing_mission_id),
                            "buffer_size": 0,
                            "data_type": "json",
                        }

                        self.rabbit_mq.enqueue_message(
                            message=message_body,
                            headers=headers,
                            priority=self.mission_live_priority,
                        )

                        self.logger.info(
                            f"Mission with id={existing_mission_id} completed and moved to last_mission queue"
                        )
                        return True, None
                    except Exception as e:
                        rabbitmq_error = f"Could not complete the current mission with id={existing_mission_id}, error sending to message to rabbitmq, error: {str(e)}"
                        self.logger.error(rabbitmq_error)

                        mission_detail["mission_status"] = 1
                        mission_detail.pop("end_time", None)

                        self._clear_queue(self.current_mission_queue)

                        self.rmq_channel.basic_publish(
                            exchange="",
                            routing_key=self.current_mission_queue,
                            body=json.dumps(mission_detail),
                            properties=pika.BasicProperties(
                                delivery_mode=2,  # make message persistent
                                content_type="application/json",
                            ),
                        )

                        return False, rabbitmq_error

                else:
                    self.logger.info(f"No active mission found to mark completed")
                    if mission_detail["mission_status"] == 2:
                        self._move_mission_to_last_queue(mission_detail)
                    return True, None
            else:
                self.logger.info(f"No active mission found to mark completed")
                return True, None

        except Exception as e:
            error_message = f"Error updating current mission: {str(e)}"
            self.logger.error(error_message)
            return False, error_message

    def _clear_queue(self, queue_name: str):
        """Helper method to clear all messages from a queue, connection should be checked before this itself"""
        try:
            while True:
                method_frame, _, _ = self.rmq_channel.basic_get(
                    queue=queue_name, auto_ack=True
                )
                if not method_frame:
                    break
        except Exception as e:
            self.logger.error(f"Error clearing queue {queue_name}: {str(e)}")

    def _move_mission_to_last_queue(self, mission_detail: Dict[str, Any]):
        """Helper method to move mission from current to last queue, connection should be checked before this itself"""
        try:
            # Clear current mission queue
            self._clear_queue(self.current_mission_queue)

            # Clear last mission queue (to store only the latest completed mission)
            self._clear_queue(self.last_mission_queue)

            # Add mission to last_mission queue
            self.rmq_channel.basic_publish(
                exchange="",
                routing_key=self.last_mission_queue,
                body=json.dumps(mission_detail),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                ),
            )
        except Exception as e:
            self.logger.error(f"Error moving mission to last queue: {str(e)}")
            raise

    def is_healthy(self):
        """
        Check if the service is healthy.
        """
        return hasattr(self, "rmq_conn") and self.rmq_conn and self.rmq_conn.is_open

    def cleanup(self):
        """
        Clean up resources, closing connections and channels.
        """
        if hasattr(self, "rmq_conn") and self.rmq_conn and self.rmq_conn.is_open:
            self.rmq_conn.close()
            self.logger.info("RabbitMQ connection closed")
        self.rabbit_mq.close()

    def __del__(self):
        """Destructor called by garbage collector to ensure resources are cleaned up, when object is about to be destroyed"""
        try:
            self.logger.error(
                "Destructor called by garbage collector to cleanup MissionUtils"
            )
            self.cleanup()
        except Exception as e:
            pass


def main():
    # Example 1: Interective start and end mission
    from vyomcloudbridge.utils.mission_utils import MissionUtils

    mission_utils = MissionUtils()
    new_mission_id = mission_utils.generate_mission_id()
    print("Trying to start mission_id with-", new_mission_id)
    try:
        try:
            mission_start_time = datetime.now(timezone.utc).isoformat()
            mission_detail, start_mission_error = mission_utils.start_mission(
                id=new_mission_id,
                start_time=mission_start_time,
                destination_ids=["s3", "gcs_mqtt"],
            )
            if start_mission_error:
                print(f"Error starting mission: {start_mission_error}")
                # take user input, to start the current mission (this will stop the existing mission)
                user_input = input("Try force starting the current mission? [Y/n]?")
                if user_input.lower() == "y":
                    force_start_mission_success, force_start_mission_error = (
                        mission_utils.start_mission(
                            start_time=mission_start_time,
                            destination_ids=["s3", "gcs_mqtt"],
                            force_start=True,
                        )
                    )
                    if force_start_mission_error:
                        raise Exception(force_start_mission_error)
                    else:
                        print("Mission started successfully.\n")
                else:
                    raise Exception(start_mission_error)
            else:
                print("Mission started successfully.")
        except Exception as e:
            raise

        # wait for the user input, "Shall we end current misssion? [Y/n]?"
        try:
            user_input = input("Shall we end current misssion? [Y/n]?")
            if user_input.lower() == "y":
                try:
                    success, error = mission_utils.end_current_mission()
                    if error:
                        print("Failed to end current mission:", error)
                    else:
                        print("Current mission ended successfully.")
                except KeyboardInterrupt:
                    print("MissionUtils service interrupted by user.")
                except Exception as e:
                    print(f"An error in ending current mission: {str(e)}")
                finally:
                    mission_utils.cleanup()
                    print("MissionUtils service cleaned up and exited.")
            else:
                print("Skipping marking mission as completed...")
        except KeyboardInterrupt:
            print("MissionUtils service interrupted by user.")
        except Exception as e:
            print(f"An error in ending current mission: {str(e)}")

        print("\n\n\nNow let's try to fetch the curremt mission status")
        current_mission_message, current_mission_error = (
            mission_utils.get_current_mission()
        )
        if current_mission_error:
            print(f"Error fetching current mission: {current_mission_error}")
        else:
            print(f"Current mission status: {current_mission_message}")

        print("\n\n\nNow let's try to fetch the last mission status")
        last_mission_message, last_mission_error = mission_utils.get_last_mission()
        if last_mission_error:
            print(f"Error fetching last mission: {last_mission_error}")
        else:
            print(f"Last mission status: {last_mission_message}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        mission_utils.cleanup()
        print("MissionUtils service cleaned up and exited.")

    # # Example 2: Non-interactive start and end mission
    # try:
    #     mission_utils = MissionUtils()
    #     mission_detail, error = mission_utils.start_mission(
    #         name="optional_human_readable_name",
    #         description="Description of mission",
    #     )
    #     if error:
    #         print("Failed to start mission:", error)
    #     else:
    #         print("Mission started successfully:", mission_detail)
    #     print("Waiting for 10 seconds, before marking mission as completed...")
    #     time.sleep(10)
    #     # End the mission
    #     success, error = mission_utils.end_current_mission()
    #     if error:
    #         print("Failed to end current mission:", error)
    #     else:
    #         print("Mission ended successfully.")
    # except Exception as e:
    #     print(f"An error occurred: {str(e)}")
    # finally:
    #     mission_utils.cleanup()
    #     print("MissionUtils service cleaned up and exited.")


if __name__ == "__main__":
    main()
