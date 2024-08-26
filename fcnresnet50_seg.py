import torch
from torchvision import transforms, models
from skimage import io
import segmentation_models_pytorch as smp
import torch.nn.functional as F
import torch.nn as nn
from torchvision import transforms, utils
from matplotlib import pyplot as plt
import numpy as np
import os

checkpoints = "./models/"
down_imgs = "./downloaded_images"
output_dir = './segmented_images'

def imshow(img):
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()

# Define the device
device = torch.device("mps" if torch.has_mps else "cuda" if torch.cuda.is_available() else "cpu")
print(device)

# Define the preprocessing transforms
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Load the FCN_ResNet50 model
num_classes = 3
state = torch.load(checkpoints + 'fcnresnet50checkpoint-10.pkl', map_location=device)
fcnresnet50 = models.segmentation.fcn_resnet50(pretrained=True, progress=True)
# Change classifier to predict only 3 classes
fcnresnet50.classifier[4] = nn.Conv2d(512, num_classes, kernel_size=(1, 1), stride=(1, 1))
fcnresnet50.aux_classifier[4] = nn.Conv2d(256, num_classes, kernel_size=(1, 1), stride=(1, 1))
fcnresnet50.load_state_dict(state['net'])
fcnresnet50.to(device)
fcnresnet50.eval()

os.makedirs(output_dir, exist_ok=True)

for image_name in os.listdir(down_imgs):
    # Load and preprocess the image
    image_path = os.path.join(down_imgs, image_name)
    image = io.imread(image_path)
    image = transform(image).unsqueeze(0)  # Add batch dimension
    image = image.to(device)

    # Make predictions with the model
    with torch.no_grad():
        # FCN_ResNet50 prediction
        output1 = fcnresnet50(image)['out']

    # Post-process the predictions
    def process_output(output, num_classes=3):
        output = output.squeeze()  # single image
        classes = torch.argmax(output, dim=0)
        r = torch.zeros_like(classes)
        g = torch.zeros_like(classes)
        b = torch.zeros_like(classes)

        idx = classes == 0
        r[idx] = 1
        idx = classes == 1
        g[idx] = 1
        idx = classes == 2
        b[idx] = 1

        return torch.stack([r, g, b], axis=0).float()

    fcnresnet_pred = process_output(output1, num_classes)
    
    # Crop and save the cropped image
    cropped_image = image[:, :, :1120, :1568]
    cropped_image_path = os.path.join(output_dir, f'{os.path.splitext(image_name)[0]}_cropped.png')
    utils.save_image(cropped_image.cpu().squeeze(), cropped_image_path)

    # Save the prediction
    prediction_image_path = os.path.join(output_dir, f'{os.path.splitext(image_name)[0]}_fcnresnet_pred.png')
    utils.save_image(fcnresnet_pred.cpu(), prediction_image_path)