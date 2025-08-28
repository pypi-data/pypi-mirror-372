# Standard library imports
import json
import threading
import time
import uuid

# Third-party imports
from pymavlink import mavutil

# Local application imports
from vyomcloudbridge.utils.abc_listener import AbcListener
from vyomcloudbridge.utils.configs import Configs
from vyomcloudbridge.utils.logger_setup import setup_logger
from rclpy_message_converter import message_converter
from vyomcloudbridge.utils.shared_memory import SharedMemoryUtil


class MavListener(AbcListener):
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MavListener, cls).__new__(cls)
                    print("MavListener singleton initialized")
        print("MavListener client service started")
        return cls._instance

    def __init__(self):
        try:
            super().__init__(multi_thread=False, daemon=False) # TODO: we can remove multi_thread, daemon later
            self.logger.info("MavListener initializing...")

            # compulsory
            self.channel = "mavlink"

            self.mission_id = 0
            self.user_id = 1
            self.mission_status = 2
            self.chunk_retry_count = 3
            self.chunk_retry_timeout = 5
            self.chunk_result_recheck_delay = 0.1
            self.udp_connection_timeout = 5
            self.udp_heartbeat_timeout = 5

            # machine configs
            self.machine_config = Configs.get_machine_config()
            self.machine_id = self.machine_config.get("machine_id", "-") or "-"

            self.ack_data_received = {}
            self.data_received = {}

            # MAVLink connection setup
            self.master = mavutil.mavlink_connection(
                # vyom_settings.MAVLINK_COMMANDER_IP,
                "udp:127.0.0.1:14557",
                source_system=101,
                source_component=191,
            )
            self.master.wait_heartbeat(timeout=self.udp_heartbeat_timeout)
            self.logger.info(
                "Heartbeat received. MavListener initialized successfully!"
            )

            self.logger.info(f"Machine id {self.machine_id}")

            self.shared_mem = SharedMemoryUtil()
          

        except Exception as e:
            self.logger.error(f"Error init MavListener: {str(e)}")
            raise

    def set_ack_data_received(self, data_name):  # AMAR
        """
        Update acknowledgment data in shared memory
        """

        self.shared_mem.set_data(data_name, True)

    def serialise_msg(self, message):
        # If it's a string or dict, treat accordingly
        if isinstance(message, str):
            return json.dumps(dict(typ="string", msg=message))

        elif isinstance(message, dict):
            return json.dumps(dict(typ="dict", msg=message))

        else:
            msg_type = type(message).__name__
            msg_to_sent = message_converter.convert_ros_message_to_dictionary(message)
            return json.dumps(dict(typ=msg_type, msg=msg_to_sent))

    def send_mav_msg(self, msgid, ack_msg):
        try:
            self.master.mav.vyom_message_send(
                0,  # target_system
                0,  # target_component
                msgid.encode("utf-8"),  # 6-byte message_id
                self.serialise_msg(ack_msg).encode("utf-8"),  # The 233-byte msg_text
                1,  # Total number of chunks
                0,  # Current chunk index
                int(time.time()),  # Unix timestamp
            )
            self.logger.info(f"Sent MAV message with msgid: {msgid}")
        except Exception as e:
            self.logger.error(f"Failed to send MAV message with msgid: {msgid}. Error: {e}")


    def update_data_received(self, msgid, total_chunks, chunk_id, msg_text):
        self.logger.debug(
            f"Received msg_text {msg_text}"
        )
        if self.data_received[msgid][chunk_id] == -1:
            self.data_received[msgid][chunk_id] = msg_text
            self.data_received[msgid][total_chunks] += 1
        else:
            self.logger.debug(f"Duplicate chunk {chunk_id} for msgid {msgid}")

        self.logger.debug(
            f"Received chunk_id {chunk_id}. Number of chunks recieved {self.data_received[msgid][total_chunks]} of {total_chunks} total chunks"
        )

        self.logger.debug("New chunks received and sent ack")

        # check if entire msg is receieved
        if self.data_received[msgid][total_chunks] == total_chunks:
            full_message = "".join(self.data_received[msgid][:total_chunks])
            self.logger.info(
                f"All chunks received for msgid: {msgid}. Receieved full message"
            )
            self.logger.debug(
                f"Full message: {full_message}"
            )

            try:
                message_dict = json.loads(full_message)
                self.logger.debug(
                    f"messages: {message_dict} type: {type(message_dict)}"
                )
                
                
                self.logger.debug(
                    f"typ: {message_dict.get('typ')} id = {self.machine_id}"
                )
                                
                self.handle_message("gcs_data", message_dict, self.machine_id, 0)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse full_message as JSON: {e}")

            # TODO: if all msg received push to ros
            # self.handle_message()
            # def handle_message(self, typ, full_message, self.machine_id, source_id)

            message = json.loads(full_message)

            # remove the msgid from the dictionary
            self.handle_msg(message)
            self.data_received.pop(msgid)
            self.data_received[msgid] = 1

    def handle_msg(self, message):
        pass

    def msg_acknowledged(self, msgid, chunk_index):  # AMAR
        ack = self.set_ack_data_received(f"mavlink_ack_data-{msgid}-{chunk_index}")

    # def msg_acknowledged(self, msgid, chunk_index): # AMAR
    #     ack = self.ack_data_received.get(msgid)
    #     if not ack:
    #         self.ack_data_received.update({msgid: {str(chunk_index): 1}})

    #         self.logger.info(f"Updating ack_data_received {self.ack_data_received}")
    #     else:
    #         ack.update({str(chunk_index): 1})

    def acknowledge_msg(self, msgid, chunk_index):
        try:
            self.master.mav.vyom_message_send(
                0,  # target_system
                0,  # target_component
                msgid.encode("ascii"),  # 6-byte message_id
                "ACK".encode("ascii"),  # The 233-byte msg_text
                1,  # Total number of chunks
                chunk_index,  # Current chunk index
                int(time.time()),  # Unix timestamp
            )
            self.logger.debug(f"Acknowledged chunk {chunk_index} for msgid: {msgid}")
        except Exception as e:
            self.logger.error(f"Failed to acknowledge chunk {chunk_index} for msgid: {msgid}. Error: {e}")


    def receive_mav_message(self):
        self.logger.debug(
            f"Receiveing mav_messages background proccess started - is_running={self.is_running}"
        )
        while self.is_running:
            msg = self.master.recv_match(type="VYOM_MESSAGE", blocking=True)

            if msg:
                self.logger.debug(
                    f"Received mav_messages msg {msg}"
                )
                # extract the data
                msgid = msg.message_id
                chunk_id = msg.chunk_index
                msg_text = msg.msg_text
                total_chunks = msg.total_chunks

                if msg_text == "ACK":
                    self.msg_acknowledged(msgid, chunk_id)
                    continue
                else:
                    self.acknowledge_msg(msgid, chunk_id)

                    self.logger.debug(
                        f"Received chunk_id {chunk_id} total chunks {total_chunks}"
                    )

                    # Update the dictionary for new msg
                    # if the msgid is not existing in the dictionary
                    if msgid not in self.data_received:
                        self.data_received[msgid] = [-1] * (total_chunks + 1)

                        # last value is used as counter number of chunks received
                        self.data_received[msgid][total_chunks] = 0

                    # If msgid was already received and all chunks are joined
                    if self.data_received[msgid] == 1:
                        self.logger.debug("all chunks already added")
                    else:
                        self.logger.debug("Receiving chunks for the msgid")
                        self.update_data_received(
                            msgid, total_chunks, chunk_id, msg_text
                        )

    def start(self):
        try:
            self.logger.debug("MAVLink message listener thread starting...")
            self.is_running = True
            self._listener_thread = threading.Thread(
                target=self.receive_mav_message, daemon=True
            )

            self._listener_thread.start()
            self.logger.info("Started MAVLink message listener thread.")
        except Exception as e:
            self.logger.error(f"Failed to start listener thread: {str(e)}")

    def stop(self):
        self.logger.info("Stopping MavListener...")
        self.is_running = False
        self.cleanup()
        self.logger.info("Stoped MavListener successfully!")

    def cleanup(self):
        # TODO: Implement connection cleanup: TO check if this works
        self.logger.info("Cleaning up MAVLink connection...")
        try:
            if self.master:
                self.master.close()
            self.logger.info("MAVLink cleanup successful!")
        except Exception as e:
            self.logger.error(f"MAVLink cleanup failed error: {str(e)}")

    def is_healthy(self):
        # TODO Implement if connection is working
        # return true
        # else false
        pass


def main():
    listener = MavListener()
    listener.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[INFO] Interrupted. Cleaning up...")
    listener.stop()


if __name__ == "__main__":
    main()
