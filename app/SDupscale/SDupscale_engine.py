from diffusers import StableDiffusionUpscalePipeline
import requests
import json
from io import BytesIO
from PIL import Image
import torch

torch_device = "cuda" if torch.cuda.is_available() else "cpu" #NOTE: this is ONLY for build time - the ensuing dtypes of float16 later on make inference impossible on cpu. Can refactor for this, but seems silly as it will be insanely slow without a GPU.

model_id = "stabilityai/stable-diffusion-x4-upscaler"
upres_pipeline = StableDiffusionUpscalePipeline.from_pretrained(model_id, torch_dtype=torch.float16)
upres_pipeline = upres_pipeline.to(torch_device)
upres_pipeline.enable_model_cpu_offload()

#the one and only function I need here lol
def upscale_image(img):    
    upscaled_image = upres_pipeline(prompt = 'high quality, no artifacts, 4k,', image=img).images[0]
    return upscaled_image