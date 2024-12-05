from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse

from SDupscale_engine import upscale_image
from PIL import Image
import os
import requests
import json
from io import BytesIO

import shutil

# globals (probably)
OUTPUT_DIR = 'upscaled_imgs'
os.makedirs(OUTPUT_DIR, exist_ok = True)

BASE_DIR = os.getcwd()

KARLO_API_BASE_URL = os.getenv("KARLO_API_BASE_URL", 'http://karlo:9001')

#typing request model
from pydantic import BaseModel, ConfigDict

class SDupscaleImgInput(BaseModel):
    filename: str

class SDupscaleImgOutput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    images: Image

class SDupscaleJSONOutput(BaseModel):
    imagelinks: str

# requesting img input from gen server
def return_img_from_server(filename:str, endpoint:str = 'http://karlo:9001'): #make this responsive to server location I guess - I'm lazy though and this will work locally with docker-compose
    byteobj = requests.get(endpoint+'/download/'+filename)
    img = Image.open(BytesIO(byteobj.content))
    return img
    
    
# api endpoint
app = FastAPI(
    title="SD upscale inference server - depends on karlo server",
    description="upscales inputs to higher res",
    version=0.1,
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upscale")
async def upscale(inputs: SDupscaleImgInput):
    '''
    takes a single image filename from server as input, generates links to upscaled photo as output
    '''
    filename = inputs.filename
    cand_img = return_img_from_server(filename, KARLO_API_BASE_URL)
    upscaled_img = upscale_image(cand_img)
    upres_filename = filename.replace('.png', '_upscale.png')
    upscaled_img.save(f"{OUTPUT_DIR}/{upres_filename}")
    return {'imagelinks': upres_filename}
    


@app.get("/download/{filename}") # <- change this for shared S3 bucket, if used. This will generally need a refactor for whatever it is that's deployed. Will likely need changes for user-specific dirs as well.
async def download_image(filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    print(filepath)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(
        os.path.join(BASE_DIR, filepath), 
        media_type="image/png"
    )

@app.get("/clear_imgs")
async def clear_imgs():
    shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)