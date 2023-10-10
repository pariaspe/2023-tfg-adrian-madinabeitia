# run with python filename.py -i rosbag_dir/
# "../rosbagsCar/rosbag2_2023_10_09-11_50_46/rosbag2_2023_10_09-11_50_46_0.db3"
## Links: https://stackoverflow.com/questions/73420147/how-to-read-custom-message-type-using-ros2bag

from rosbags.rosbag2 import Reader as ROS2Reader
from rosbags.serde import deserialize_cdr
import matplotlib.pyplot as plt

import argparse
import torch
import torchvision
import torchvision.transforms as transforms

# PyTorch TensorBoard support
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

def get_img(rosbag_dir, topic):
    imgs = []
    with ROS2Reader(rosbag_dir) as ros2_reader:
        
        channels = 3 # Encoding = bgr8
        ros2_conns = [x for x in ros2_reader.connections]
        ros2_messages = ros2_reader.messages(connections=ros2_conns)      

        for m, msg in enumerate(ros2_messages):
            (connection, timestamp, rawdata) = msg
                
            if (connection.topic == topic):
                data = deserialize_cdr(rawdata, connection.msgtype)

                # Saves the image in a readable format
                img = np.array(data.data, dtype=data.data.dtype)
                resizeImg = img.reshape((data.height, data.width, channels))
                imgs.append(resizeImg)

                # # To save the raw data
                # imgs.append(data.data)
    
    return imgs

def get_vel(rosbag_dir, topic):
    vel = []

    with ROS2Reader(rosbag_dir) as ros2_reader:

        ros2_conns = [x for x in ros2_reader.connections]
        ros2_messages = ros2_reader.messages(connections=ros2_conns)
        
        for m, msg in enumerate(ros2_messages):
            (connection, timestamp, rawdata) = msg
                
            if (connection.topic == topic):
                data = deserialize_cdr(rawdata, connection.msgtype)
                linear = data.linear.x
                angular = data.angular.z
                vel.append([linear, angular])
    
    return vel

def train(vel_data, img_data):
    # transform = transforms.Compose(
    # [transforms.ToTensor(),
    # transforms.Normalize((0.5,), (0.5,))])

    # Create datasets for training & validation, download if necessary
    training_loader = torch.utils.data.DataLoader(img_data, batch_size=4, shuffle=True)
    print('Training set has {} instances'.format(len(img_data)))

def showData(img, vel):
    print(vel)
    # Display the image
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

def main():
    parser = argparse.ArgumentParser(description='Extract images from rosbag.')
    # input will be the folder containing the .db3 and metadata.yml file
    parser.add_argument('--input','-i',type=str, help='rosbag input location')
    
    args = parser.parse_args()
    rosbag_dir = args.input

    vel_data = get_vel(rosbag_dir, "/cmd_vel")
    img_data = get_img(rosbag_dir, "/filtered_img")

    showData(img_data[50], vel_data[50])


if __name__ == "__main__":
    main()