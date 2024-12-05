import streamlit as st
import requests
import io
from PIL import Image
import os

# Configuration
KARLO_API_BASE_URL = os.getenv("KARLO_API_BASE_URL", 'http://karlo:9001')
UPSCALE_API_BASE_URL = os.getenv("UPSCALE_API_BASE_URL", 'http://sd-upscale:1337')

def generate_images(weights):
    """Call image generation API"""
    try:
        response = requests.post(f"{KARLO_API_BASE_URL}/generate", json={"weights": weights, "num_imgs": 2})
        response.raise_for_status()
        return response.json()['imagelinks']
    except requests.RequestException as e:
        st.error(f"Error generating images: {e}")
        return []

def upscale_image(filename):
    """Call upscaling API"""
    try:
        response = requests.post(f"{UPSCALE_API_BASE_URL}/upscale", json={"filename": filename})
        response.raise_for_status()
        return response.json()['imagelinks']
    except requests.RequestException as e:
        st.error(f"Error upscaling image: {e}")
        return None

def download_image(filename, API_URL):
    """Download image from API"""
    try:
        response = requests.get(f"{API_URL}/download/{filename}")
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except requests.RequestException as e:
        st.error(f"Error downloading image: {e}")
        return None


# APP
st.title("Character generator!")

# Input weights



weight_names = [
    "Scroll Seeker",
    "Meme Maven", 
    "Fandom Fox",
    "Nostalgic Navigator", 
    "Social Synthesiser",
    "Chaos Clicker",
    "Eco Explorer",
    "News Nerd",
    "Trend Tracker", 
    "Digital Daydreamer"
]

weights = []
with st.sidebar:
    st.header("Enter the weights of your characters!")
    for i, name in enumerate(weight_names):
        weight = st.number_input(f"{name}", value=0.0, step=0.01, key=f"weight_{i}")
        weights.append(weight)

# Generate button
if st.button("Generate characters"):
    with st.spinner("Generating characters..."):
        # Store generated image filenames in session state
        st.session_state.image_filenames = generate_images(weights)
        
        # Prepare to display images
        st.session_state.generated_images = [
            download_image(filename, KARLO_API_BASE_URL) for filename in st.session_state.image_filenames
        ]

# Display generated images with upscale buttons
if hasattr(st.session_state, 'generated_images'):
    st.header("Generated characters")
    
    # Create columns for images
    cols = st.columns(len(st.session_state.generated_images))
    
    for i, (image, filename) in enumerate(zip(st.session_state.generated_images, st.session_state.image_filenames)):
        if image:
            with cols[i]:
                # Display original image
                st.image(image, caption=f"Generated Image {i+1}")
                
                # Upscale button
                if st.button(f"Upscale Image {i+1}"):
                    with st.spinner("Upscaling image..."):
                        # Call upscale API
                        upscaled_filename = upscale_image(filename)
                        
                        if upscaled_filename:
                            # Download and display upscaled image
                            upscaled_image = download_image(upscaled_filename, UPSCALE_API_BASE_URL)
                            if upscaled_image:
                                st.image(upscaled_image, caption=f"Upscaled Image {i+1}")

    if st.button("clear cache and start again!"): #maybe make this automatic upon each generation??? I'm too lazy. Think about it though.
        requests.get(f"{KARLO_API_BASE_URL}/clear_imgs")
        requests.get(f"{UPSCALE_API_BASE_URL}/clear_imgs")
