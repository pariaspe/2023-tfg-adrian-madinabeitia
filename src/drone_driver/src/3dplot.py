import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import os
from PIL import Image
from imblearn.over_sampling import RandomOverSampler
from imblearn.over_sampling import SMOTE

# Sets the label to a velocity
def updateNumAngular(value):
    label = 0
    if value > 0.50:
        label = 3

    elif value > 0.25:
        label = 2

    else:
        label = 1
    return label


def read_image_folder_sorted_by_timestamp(folder_path):
    images = []

    try:
        # Lists the files
        files = os.listdir(folder_path)

        # Only reads .jpg
        jpg_files = [file for file in files if file.endswith('.jpg')]

        # Sort by timestamp
        sorted_files = sorted(jpg_files, key=lambda x: int(os.path.splitext(x)[0]))

        # Reads the images
        for file_name in sorted_files:
            file_path = os.path.join(folder_path, file_name)

            image = Image.open(file_path)
            image_array = np.array(image)
            images.append(image_array)

    except FileNotFoundError:
        print("Error: Carpeta no encontrada.")

    return images


def get_labels(folder_path):
    labels = []

    try:
        # Lists the files
        files = os.listdir(folder_path)

        # Only reads .txt
        txt_files = [file for file in files if file.endswith('.txt')]

        # Sort by timestamp
        sorted_files = sorted(txt_files, key=lambda x: int(os.path.splitext(x)[0]))

        # Reads the files
        for file_name in sorted_files:
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                content = file.read()
                numbers = [float(num) for num in content.split(',')]

                # Updates the count
                if numbers[1] > 0:
                    labels.append(updateNumAngular(numbers[1]))
                else:
                    labels.append(-updateNumAngular(abs(numbers[1])))

    except FileNotFoundError:
        print("Error: Carpeta no encontrada.")
    
    return labels

def plot_3d_bars(x, y, z, colors, xlabel='X', ylabel='Y', zlabel='Z', title='3D Plot'):
    # Create the figure and 3D axes
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Adjust the heights of the bars to go from 0 to their respective z values
    bottoms = np.zeros_like(z)
    width = depth = 0.8

    # Create the 3D bars with different colors for each row
    for i, color in zip(range(3), colors):
        indices = y == i
        ax.bar3d(x[indices], y[indices], bottoms[indices], dx=width, dy=depth, dz=z[indices], color=color)

    # Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    ax.set_title(title)

    # Show the plot
    plt.show()



def getLabelDistribution(labels):
    positiveAngVels = [0, 0, 0]
    negativeAngVels = [0, 0, 0]

    # Counts the number of labels of each type
    for label in labels:

        if label == 3:
            positiveAngVels[2] += 1

        elif label == 2:
            positiveAngVels[1] += 1

        elif label == 1:
            positiveAngVels[0] += 1

        elif label == -3:
            negativeAngVels[2] += 1

        elif label == -2:
            negativeAngVels[1] += 1
        
        else:
            negativeAngVels[0] += 1


    return positiveAngVels, negativeAngVels


def main():
    # Data paths
    labels_path = '../dataset/simple_circuit/labels'
    images_path = '../dataset/simple_circuit/frontal_images'

    labels = get_labels(labels_path)
    images = read_image_folder_sorted_by_timestamp(images_path)

    nAngVelPositive, nAngVelNeagtive = getLabelDistribution(labels)

    # Data for the columns with linear
    x = np.array([-1, 0, 1, -1, 0, 1, -1, 0, 1])
    y = np.array([0, 0, 0, 1, 1, 1, 2, 2, 2])

    z = np.array([0, 0, 0, 
                  nAngVelNeagtive[0], nAngVelNeagtive[1], nAngVelNeagtive[2], 
                  nAngVelPositive[0], nAngVelPositive[1], nAngVelPositive[2]])

    # Colors for each row
    colors = ['green', 'lightblue', 'blue']

    # Graphics
    plot_3d_bars(x, y, z, colors, xlabel='Min mel    Medium vel   Max vel ', ylabel='Linear, -Ang, +Ang', zlabel='Samples', title='Simple circuit')

    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(images, labels)

if __name__ == "__main__":
    main()