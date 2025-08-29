from vyomcloudbridge.services.queue_writer_json import QueueWriterJson
import time
import requests
from urllib.parse import urlparse

default_mission_id = "_all_"
data_type = "binary"
data_source = "TEST_FILE"
total_size = 100 # MB
writer = QueueWriterJson()

try:
    
    file_size = 10 # MB
    loop_len = total_size/file_size
    if(total_size%file_size):
        loop_len = loop_len +1 # 1 more increment
    padding_length = len(str(loop_len))
    # URLs for the images
    image_url = "https://www.sample-videos.com/img/Sample-jpg-image-10mb.jpg",
    parsed_url = urlparse(image_url)
    file_extension = parsed_url.path.split(".")[-1]
    epoch_ms = int(time.time() * 1000)
    
    response = requests.get(image_url)
    if response.status_code == 200:
        file_data = response.content
        for i in range(loop_len):
            formatted_index = str(i + 1).zfill(padding_length)
            filename = f"{epoch_ms}_{formatted_index}.{file_extension}"
            writer.write_message(
                message_data=file_data,
                filename=filename,
                data_source=data_source,
                data_type=data_type,
                mission_id=default_mission_id,
                priority=2,
                destination_ids=["s3"],
                merge_chunks=True,
                background=False,
            )
    else:
        print(
            f"Failed to download image from {image_url}. Status code: {response.status_code}"
        )
except Exception as e:
    print(f"Error writing test messages: {e}")
finally:
    writer.cleanup()
