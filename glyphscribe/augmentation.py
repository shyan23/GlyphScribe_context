from torchvision import transforms
import torch
import numpy as np

class Transformations:
    class RandomNoise(object):
        """
        The transformation first adds the generated noise to the input tensor.
        noise.unsqueeze(0) adds a channel dimension back to the noise (e.g., from [H, W] to [1, H, W]). 
        The result is then clamped between 0 and 1, ensuring the pixel values remain valid (standard for normalized images).
        """    

        # enters noise(distortion to the image tensor with some range ig)
        def __init__(self, min_noise_level=0.1, max_noise_level=0.3):
            self.min_noise_level = min_noise_level
            self.max_noise_level = max_noise_level
        # this is the main place where stuff is working
        #Clamps all elements in the input tensor into the range [min,max].
        def __call__(self, tensor):
            noise = torch.randn_like(tensor[0]) * np.random.uniform(self.min_noise_level, self.max_noise_level)
            return torch.clamp(tensor + noise.unsqueeze(0), 0, 1)

    class ElasticGrid(object):
        """
        generates elastic distortion on the image,simulating non-linear local deformations.
        Parameters: 
            alpha (controls the intensity of the displacement),
            sigma (controls the smoothness of the displacement),
            interpolation (resampling filter), 
            and fill (value for points outside the input boundaries).
        """

        def __init__(self, sigma=5.0):
            self.sigma = sigma

        def __call__(self, tensor):
            return transforms.ElasticTransform(
                alpha=max(2, 9-(20/1000)*tensor.shape[0]), 
                sigma=self.sigma, 
                interpolation=transforms.InterpolationMode.BILINEAR, 
                fill=1)(tensor)

    class Resize(object):
        """
        applies a random horizontal and vertical resizing/stretching to the image
        Resizes the image to the given size.
        Parameters:
            size (the desired output size, often a tuple (H, W) or a single integer),
            and optional interpolation
        """
        def __init__(self, horizontal_ratio=(0.3,1.5), vertical_ratio=(0.9,1.1)):
            self.horizontal_ratio = horizontal_ratio
            self.vertical_ratio = vertical_ratio

        def __call__(self, tensor):
            _, height, width = tensor.shape
            return transforms.Resize(
                (int(height * np.random.uniform(*self.vertical_ratio)), int(width * np.random.uniform(*self.horizontal_ratio))), 
                interpolation=transforms.InterpolationMode.BILINEAR
            )(tensor)
            
    
data_transformer = transforms.Compose([
    transforms.ToTensor(),   # image to tensor
    transforms.Grayscale(),  #Reduce the image to a single channel
    transforms.RandomApply([transforms.RandomRotation(degrees=1, fill=1)], p=0.5), # small random rotation is implemented
    transforms.RandomApply([Transformations.RandomNoise(min_noise_level=0.1, max_noise_level=0.2)], p=0.8), # p=0.8	Adds Gaussian (normal) noise with random intensity (0.1-0.2).
    transforms.RandomApply([transforms.functional.invert],p=0.01), # Inverts the image colors (img=1−img).
    transforms.RandomApply([Transformations.ElasticGrid(sigma=5.0)], p=0.8), # elastic grid,non-linear, local geometric distortion
    transforms.RandomApply([Transformations.Resize()], p=0.5), # Applies a random stretch/compression to the aspect ratio.  
    transforms.ToPILImage()
])