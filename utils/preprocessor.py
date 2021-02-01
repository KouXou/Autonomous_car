import PIL.Image
import torchvision.transforms as transforms
import torch
import jetson.utils
import numpy


class ImagePreProcessor:
    def __init__(self, width=224, height=224):
        self.height = height
        self.width = width

    def preprocessImage(self, image):
        # allocate the output, with half the size of the input
        imgOutput = jetson.utils.cudaAllocMapped(width=self.width,
                                                 height=self.height,
                                                 format=image.format)

        # rescale the image (the dimensions are taken from preprocessor)
        jetson.utils.cudaResize(image, imgOutput)

        # convert to numpy Array (RGBA)
        array = jetson.utils.cudaToNumpy(imgOutput).astype(numpy.uint8)
        # Get only 3 channels RGB
        image = PIL.Image.fromarray(array[:, :, :3])

        # crop top 50px from image
        image = transforms.functional.crop(image, 50, 0, 174, 224)

        # transform input image
        preprocess = transforms.Compose([
            transforms.Resize(size=(self.width, self.height)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )])

        img_t = preprocess(image)
        return torch.unsqueeze(img_t, 0)
