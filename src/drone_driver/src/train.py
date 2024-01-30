#!/usr/bin/env python3


from torch.utils.tensorboard import SummaryWriter
from torch import nn
import torch
from torch.serialization import save
from torch.utils.data import DataLoader

import torch.optim as optim
import sys

import ament_index_python

writer = SummaryWriter()

package_path = ament_index_python.get_package_share_directory("drone_driver")
sys.path.append(package_path)

from include.data import rosbagDataset, dataset_transforms, DATA_PATH
from include.models import pilotNet

CHECKPOINT_PATH = package_path + "/utils/network.tar"


def should_resume():
    return "--resume" in sys.argv or "-r" in sys.argv


def save_checkpoint(model: pilotNet, optimizer: optim.Optimizer):
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, CHECKPOINT_PATH)


def load_checkpoint(model: pilotNet, optimizer: optim.Optimizer = None):
    package_path = ament_index_python.get_package_share_directory("drone_driver")
    CHECKPOINT_PATH = package_path + "/utils/network.tar"
    
    checkpoint = torch.load(CHECKPOINT_PATH)

    model.load_state_dict(checkpoint["model_state_dict"])

    if optimizer != None:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])




def train(model: pilotNet, optimizer: optim.Optimizer):

    criterion = nn.MSELoss()

    dataset = rosbagDataset(DATA_PATH, dataset_transforms)
    print("** Image len = ", len(dataset.imgData), "    Vel len = ", len(dataset.velData))


    train_loader = DataLoader(dataset, batch_size=20)

    for epoch in range(10):

        running_loss = 0.0

        for i, data in enumerate(train_loader, 0):

            # get the inputs; data is a list of [inputs, labels]
            label, image = data

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = model(image)
            loss = criterion(outputs, label)
            writer.add_scalar("Loss/train", loss, epoch)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            if i % 10 == 0:    # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, loss))
                running_loss = 0.0
                # print("Output = ", outputs,  "labels = ", label, "==== Loss = ", loss, "\n\n")

                save_checkpoint(model, optimizer)
            
            

    print('Finished Training')


if __name__ == "__main__":
    model = pilotNet()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.1)

    if should_resume():
        load_checkpoint(model, optimizer)

    device = torch.device("cuda:0")
    model.to(device)
    model.train(True)

    train(
        model,
        optimizer,
    )