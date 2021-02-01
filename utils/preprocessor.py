import PIL.Image
import torchvision.transforms as transforms
import torch


class ImagePreProcessor:
    def __init__(self, width=224, height=224):
        self.height = height
        self.width = width

    def preprocessImage(self, image):
        image = PIL.Image.fromarray(image)
        image = transforms.functional.crop(image, 50, 0, 174, 224)

        preprocess = transforms.Compose([
            transforms.Resize(size=(self.width, self.height)),
            # transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )])

        img_t = preprocess(image)
        return torch.unsqueeze(img_t, 0)
