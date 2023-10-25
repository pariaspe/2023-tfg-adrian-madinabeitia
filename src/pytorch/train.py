from itertools import islice
from torch.utils.tensorboard import SummaryWriter
from torch import nn
import torch
from torch.serialization import save
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import torch.optim as optim
import sys
from models import pilotNet
import keyboard
from data import rosbagDataset


CHECKPOINT_PATH = "./network.tar"
DATA_PATH = "../rosbagsCar/rosbag2_2023_10_09-11_50_46"


def should_resume():
    return "--resume" in sys.argv or "-r" in sys.argv


def save_checkpoint(model: pilotNet, optimizer: optim.Optimizer):
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, CHECKPOINT_PATH)


def load_checkpoint(model: pilotNet, optimizer: optim.Optimizer = None):
    checkpoint = torch.load(CHECKPOINT_PATH)

    model.load_state_dict(checkpoint["model_state_dict"])

    if optimizer != None:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])


dataset_transforms = transforms.Compose([
    transforms.ToTensor(),
    transforms.Resize([66, 200]),
])


def train(model: pilotNet, optimizer: optim.Optimizer):
    # quit = False

    # def on_quit():
    #     nonlocal quit
    #     quit = True

    # keyboard.on_press_key("q", lambda _: on_quit())

    criterion = nn.MSELoss()

    dataset = rosbagDataset(DATA_PATH, dataset_transforms)
    train_loader = DataLoader(dataset, batch_size=200)

    for epoch in range(10):

        running_loss = 0.0

        for i, data in enumerate(train_loader, 0):
            # if quit:
            #     save_checkpoint(model, optimizer)
            #     return

            # get the inputs; data is a list of [inputs, labels]
            label, image = data

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = model(image)
            loss = criterion(outputs, label)
            loss.backward()
            optimizer.step()

            # print statistics
            running_loss += loss.item()
            if i % 10 == 0:    # print every 2000 mini-batches
                print('[%d, %5d] loss: %.3f' %
                      (epoch + 1, i + 1, running_loss / (2000)))
                running_loss = 0.0

                save_checkpoint(model, optimizer)

    print('Finished Training')


if __name__ == "__main__":
    model = pilotNet()
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.7)

    if should_resume():
        load_checkpoint(model, optimizer)

    device = torch.device("cuda:0")
    model.to(device)
    model.train(True)

    train(
        model,
        optimizer,
    )