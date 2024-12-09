from transformers import pipeline
from PIL import Image
pipe = pipeline("image-segmentation", model="briaai/RMBG-1.4", trust_remote_code=True, accelerator="ort", device='cpu')

def remove_bg(image: Image):
    '''
    this is a little silly but here you go lol
    '''
    rmbg_image = pipe(image)
    return rmbg_image
