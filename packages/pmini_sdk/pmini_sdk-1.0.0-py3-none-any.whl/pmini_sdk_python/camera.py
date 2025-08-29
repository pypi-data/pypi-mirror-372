import socket

import cv2
import numpy as np
import rerun as rr


class Config:
    def __init__(self, udp_address, udp_port, is_logging):
        self.udp_address = udp_address
        self.udp_port = udp_port
        self.is_logging = is_logging


class Camera:
    def __init__(self, config: Config):
        self.config = config
        # Set up UDP socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        message = "GET IMAGE"
        self.udp_socket.sendto(message.encode(), (config.udp_address, config.udp_port))
        self.chunk_length = 1460
        if self.config.is_logging:
            # Initialize rerun
            rr.init("image_logging")
            rr.save("./recording_img.rrd")

    # Function to receive image data
    def receive_image(self):
        chunks = []
        while True:
            chunk, _ = self.udp_socket.recvfrom(self.chunk_length)
            chunks.append(chunk)
            if len(chunk) < self.chunk_length:
                break
        return b"".join(chunks)

    def get_image(self):
        image_data = self.receive_image()

        # Convert image data to numpy array
        nparr = np.frombuffer(image_data, np.uint8)

        # Decode JPEG image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Check if the image was decoded properly
        if image is None and self.config.is_logging:
            rr.log("logs", rr.TextLog("Image is none. Failed to decode image", level=rr.TextLogLevel.Warning))
            return None

        try:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB
        except Exception as e:
            # Catch any unexpected exceptions and log them
            if self.config.is_logging:
                rr.log("logs", rr.TextLog(f"Unexpected error in get_image: {str(e)}", level=rr.TextLogLevel.Error))
            return None
        if self.config.is_logging:
            rr.log("image", rr.Image(image).compress(60))

        return image

    def stop(self):
        # Release resources
        self.udp_socket.close()
