from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse

from karlo_engine import woodford_karlo_func
from PIL import Image
import os
import uuid

#typing request model
from pydantic import BaseModel, ConfigDict

class GenRequest(BaseModel):
    weights: list[float]
    num_imgs: int | None = 2
    seed: int | None = None

class GenOutputs(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    images: list[Image]

class GenJSONOutputs(BaseModel):
    imagelinks: list[str]

#generate temporary output storage <- replace with a shared S3 or something at deployment
OUTPUT_DIR = "generated_images" #set this somewhere global, probably??? I dunno
os.makedirs(OUTPUT_DIR, exist_ok = True)

BASE_DIR = os.getcwd()

# api endpoint
app = FastAPI(
    title="karlo inference endpoint for mixed character generation",
    description="generates unique characters based on your classified persona",
    version=0.1,
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/generate")
async def generate(inputs: GenRequest) -> GenJSONOutputs:
    weights = inputs.weights
    num_imgs = inputs.num_imgs
    seed = inputs.seed
    outputs = woodford_karlo_func(weights, num_imgs, seed,)
    links = []
    for image in outputs: #<- change this to a shared S3 or something at deployment
        filename = f"{uuid.uuid4()}.png"
        filepath = f"{OUTPUT_DIR}/{filename}" #add stuff here if you want people to have folders based on their personal data
        links.append(filename) #change this if you need to access like, specific folders for specific people's gens
        image.save(filepath)
    return {'imagelinks': links}

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
### maybe add something that goes into particular folders in generated_images for old generations from the same donation
### open question - do all generations need to persist?