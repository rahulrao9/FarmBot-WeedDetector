import torch
from torchvision import transforms, models
from skimage import io
import segmentation_models_pytorch as smp
import torch.nn.functional as F
import torch.nn as nn
from matplotlib import pyplot as plt
import numpy as np

checkpoints = "./models/"

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

# Load and preprocess the image
image_path = './downloaded_images/2024-08-01_11-37-41.png'
image = io.imread(image_path)
image = transform(image).unsqueeze(0)  # Add batch dimension
image = image.to(device)


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

# # Load the DeepLabV3 model
# state = torch.load(checkpoints + 'deeplabv3checkpoint-10.pkl', map_location=device)
# deeplabv3 = models.segmentation.deeplabv3_resnet50(pretrained=True, progress=True)
# # Change classifier to predict only 3 classes
# deeplabv3.classifier[4] = nn.Conv2d(256, num_classes, kernel_size=(1, 1), stride=(1, 1))
# deeplabv3.aux_classifier[4] = nn.Conv2d(256, num_classes, kernel_size=(1, 1), stride=(1, 1))
# deeplabv3.load_state_dict(state['net'])
# deeplabv3.to(device)
# deeplabv3.eval()

# # Load and define the UNet model
# unet = smp.Unet('resnet50', encoder_weights='imagenet', classes=num_classes, in_channels=3)
# state = torch.load(checkpoints + 'unetcheckpoint-15.pkl', map_location=device)
# unet.load_state_dict(state['net'])
# unet.to(device)
# unet.eval()

# # Simulate a batch from your data iterator (assuming `iterator` is defined somewhere)
# testloader = torch.utils.data.DataLoader(test_set, batch_size=1, shuffle=False)
# iterator = iter(testloader)
# batch = next(iterator)
# img = batch['image'].to(device)
# annot = batch['annotation'].to(device)

# Make predictions with all three models
with torch.no_grad():
    # FCN_ResNet50 prediction
    output1 = fcnresnet50(image)['out']
    
    # # DeepLabV3 prediction
    # output2 = deeplabv3(image)['out']
    
    # UNet prediction
    patch_size = 224
    patch_stride = 224
    img_patches = F.unfold(image, patch_size, stride=patch_stride)
    patch_num = img_patches.shape[2]
    batch_size = img_patches.shape[0]
    img_size = img_patches.shape[1]
    img_patches = img_patches.permute(0, 2, 1)
    img_patches = img_patches.reshape(patch_num * batch_size, img_size)
    img_patches = img_patches.view(patch_num * batch_size, 3, patch_size, patch_size)
    # output3 = unet(img_patches)
    # output3 = output3.view(patch_num * batch_size, num_classes * patch_size * patch_size)
    # output3 = output3.permute(1, 0)
    # output3 = output3.unsqueeze(0)
    # recon_out = F.fold(output3, (1120, 1568), patch_size, stride=patch_stride)

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
# deeplabv3_pred = process_output(output2, num_classes)
# unet_pred = process_output(recon_out, num_classes)

# Visualize the input image and the predictions
print(image.size)

print('Input image:')
imshow(image.cpu().squeeze())

cropped_image = image[:, :, :1120, :1568]
print('Cropped input image:')
imshow(cropped_image.cpu().squeeze())

# print('Ground truth:')
# imshow(annot[0].cpu().squeeze())

print('FCN_ResNet50 prediction:')
imshow(fcnresnet_pred.cpu().squeeze())

# print('DeepLabV3 prediction:')
# imshow(deeplabv3_pred.cpu().squeeze())

# print('UNet prediction:')
# imshow(unet_pred.cpu().squeeze())
