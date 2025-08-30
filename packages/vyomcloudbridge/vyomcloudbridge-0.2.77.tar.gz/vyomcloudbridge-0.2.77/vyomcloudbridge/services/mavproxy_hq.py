# === Standard Library Imports ===
import glob
import os
import shutil
import subprocess
import threading
import time
from datetime import datetime

# === Third-Party Imports ===
import psutil
from pymavlink import mavutil

# === Application-Specific Imports ===
from vyomcloudbridge.utils.common import ServiceAbstract
from vyomcloudbridge.utils.configs import Configs


class MavproxyHq(ServiceAbstract):
    def __init__(self):
        super().__init__()
        try:
            # Thread attributes
            self.mavproxy_hq_thread = None
            self.is_running = False
            self.proc = None
            self.prev_armed = None
            self.curr_armed = None
            self.logger.info("MavproxyHq service initialized")
        except Exception as e:
            self.logger.error(f"Error initializing MavproxyHq service: {str(e)}")

    def create_copy_data_logger(self, f_machine_id):
        try:
            base_log_dir = f"/var/log/vyomcloudbridge/mavlogs"
            log_dir = f"{base_log_dir}/{f_machine_id}/"

            dest_log_dir_base = f"{base_log_dir}/dir_watch_data_logs/logs/"

            if not os.path.isdir(log_dir):
                self.logger.info(f"Directory not found: {log_dir}")
                return

            # Find all .BIN files
            bin_files = glob.glob(os.path.join(log_dir, "*.BIN"))

            if not bin_files:
                self.logger.info("No numbered .BIN files found.")
            else:
                # Sort by numeric filename (e.g., 1.BIN → 1)
                bin_files.sort(key=lambda f: int(os.path.basename(f).split(".")[0]))
                latest_bin = bin_files[-1]
                self.logger.info(f"Copying latest BIN file: {latest_bin}")
                
                
                now = time.time()
                timestamp = int(now * 1000)
                
                date_folder = datetime.fromtimestamp(now).strftime("%Y_%m_%d")
                dest_log_dir = os.path.join(dest_log_dir_base, date_folder)

                os.makedirs(dest_log_dir, exist_ok=True)
                
                # Rename while copying to destination
                original_name = os.path.basename(latest_bin)
                new_name = f"{os.path.splitext(original_name)[0]}_{timestamp}.BIN"
                renamed_path = os.path.join(dest_log_dir, new_name)

                # Copy with new name only
                shutil.copyfile(latest_bin, renamed_path)
                self.logger.info(f"Copied and renamed to: {renamed_path}")


        except Exception as e:
            self.logger.error(f"Error copying data logger: {str(e)}")

    def start(self):
        try:
            self.is_running = True
            # Step 1: Auto-detect USB device
            tty_devices = glob.glob("/dev/ttyUSB*")
            if not tty_devices:
                self.logger.error("No /dev/ttyUSB* device found. Exiting.")
                return

            # machine configs
            machine_config = Configs.get_machine_config()
            machine_id = machine_config.get("machine_id", "-") or "-"
            self.logger.debug(f"Machine ID: {machine_id}")

            tty_usb = tty_devices[0]
            uart_baud = 921600

            # Step 2: Define system/component ID
            sysid_thismav = 156
            compid_thismav = 191

            # Step 3: Prepare log directory and filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_log_dir = f"/var/log/vyomcloudbridge/mavlogs"
            log_dir = f"{base_log_dir}/{machine_id}/"
            log_file = f"{log_dir}mavlog_{timestamp}.tlog"

            # Step 4: Ensure log directory exists
            if not os.path.exists(log_dir):
                self.logger.info(f"Creating log directory: {log_dir}")
                os.makedirs(log_dir, exist_ok=True)
            else:
                self.logger.debug(f"Log directory exists: {log_dir}")

            self.logger.debug(f"Using MAVProxy device: {tty_usb}")

            # Step 5: Build MAVProxy command
            mavproxy_cmd = [
                "/vyomos/venv/bin/mavproxy.py",
                f"--master={tty_usb},{uart_baud}",
                "--daemon",
                "--out=udp:127.0.0.1:14550",
                "--out=udp:127.0.0.1:14555",
                "--out=udp:127.0.0.1:14556",
                "--out=udp:127.0.0.1:14557",
                "--out=udp:127.0.0.1:14560",
                "--out=udp:127.0.0.1:14565",
                "--out=udp:127.0.0.1:14600",
                "--out=udp:127.0.0.1:14700",
                f"--source-system={sysid_thismav}",
                f"--source-component={compid_thismav}",
                f"--logfile={log_file}",
                "--load-module=dataflash_logger",
            ]

            # Step 6: Launch MAVProxy
            with open("/tmp/mavproxy.log", "w") as log_out:
                self.proc = subprocess.Popen(
                    mavproxy_cmd, stdout=log_out, stderr=subprocess.STDOUT
                )
                self.logger.debug(
                    f"MAVProxy started in background (PID: {self.proc.pid})"
                )

            # Step 7: Show log directory contents
            # self.logger.info("MAVProxy log files:")
            # subprocess.run(["ls", "-lh", log_dir])

            # Define the arm state monitor loop
            def arm_state_monitor_loop():
                master = mavutil.mavlink_connection("udp:127.0.0.1:14700")
                master.wait_heartbeat()
                self.logger.debug(
                    "Heartbeat received from system (system %u component %u)"
                    % (master.target_system, master.target_component)
                )

                def is_armed(base_mode):
                    return (base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0

                while self.is_running:
                    try:
                        msg = master.recv_match(type="HEARTBEAT", blocking=True)
                        if not msg:
                            continue

                        if msg.get_srcComponent() != 1:
                            continue

                        self.curr_armed = is_armed(msg.base_mode)
                        self.logger.debug(
                            f"[DEBUG] base_mode: {msg.base_mode}, prev_armed: {self.prev_armed}, curr_armed: {self.curr_armed}"
                        )

                        if self.prev_armed is not None:
                            if self.prev_armed is True and self.curr_armed is False:
                                self.logger.info("Transition: ARMED → DISARMED")
                                machine_config = Configs.get_machine_config()
                                machine_id = (
                                    machine_config.get("machine_id", "-") or "-"
                                )
                                self.create_copy_data_logger(machine_id)

                            elif self.prev_armed is False and self.curr_armed is True:
                                self.logger.info("Transition: DISARMED → ARMED")

                        self.prev_armed = self.curr_armed

                    except Exception as e:
                        self.logger.error(f"Error in arm state monitor loop: {str(e)}")
                        time.sleep(1)

            # Create and start the thread
            self.mavproxy_hq_thread = threading.Thread(
                target=arm_state_monitor_loop, daemon=True
            )
            self.mavproxy_hq_thread.start()

            self.logger.info("MavproxyHq service started!")

        except Exception as e:
            self.logger.error(f"Error starting Mavproxy service: {str(e)}")
            self.stop()
            raise

    def stop(self):
        self.is_running = False
        # Wait for thread to finish
        if (
            hasattr(self, "mavproxy_hq_thread")
            and self.mavproxy_hq_thread
            and self.mavproxy_hq_thread.is_alive()
        ):
            self.mavproxy_hq_thread.join(timeout=5)

        if self.proc:
            self.logger.info("Attempting to stop MAVProxy process...")

            # Get all children and kill them too
            try:
                parent = psutil.Process(self.proc.pid)
                children = parent.children(recursive=True)
                for child in children:
                    self.logger.info(f"Killing child process: {child.pid}")
                    child.kill()
                self.logger.info(f"Killing MAVProxy process: {self.proc.pid}")
                parent.kill()
                self.logger.info("MAVProxy process terminated.")
            except Exception as e:
                self.logger.error(f"Error stopping MAVProxy: {str(e)}")
        else:
            self.logger.warning("No MAVProxy process to stop.")

    def cleanup(self):
        pass

    def is_healthy(self):
        return self.is_running

    def __del__(self):
        """Destructor called by garbage collector to ensure resources are cleaned up, when object is about to be destroyed"""
        try:
            self.logger.error(
                "Destructor called by garbage collector to cleanup MavproxyHQ service"
            )
            self.stop()
        except Exception as e:
            pass


def main():
    """Mavproxy service"""
    print("Starting Mavproxy service")

    mavproxy_service = MavproxyHq()

    try:
        # Simulate data arriving
        mavproxy_service.start()
        # Let it run for a short while
        time.sleep(200)

    finally:
        # Clean up
        mavproxy_service.stop()

    print("Completed Mavproxy service")


if __name__ == "__main__":
    main()
