from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import os
from pathlib import Path
import io
from PIL import Image
import uvicorn
import uuid

app = FastAPI(title="Gemini Image Generation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory
OUTPUT_DIR = Path("/home/yash/Desktop/Windows_Projects/Website/Backend/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyAY2cZM3ns-kUkfrhPB0Y3ZxQGrHb1ELwc"
client = genai.Client(api_key=GOOGLE_API_KEY)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Gemini Image Generation API",
        "endpoints": {
            "/generate-image/": "POST - Generate new image based on uploaded image + prompt",
            "/analyze-image/": "POST - Analyze image (text only)",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    api_configured = GOOGLE_API_KEY is not None
    return {
        "status": "healthy",
        "api_configured": api_configured,
        "models_available": ["gemini-2.5-flash-image", "gemini-1.5-pro"]
    }

@app.post("/generate-image/")
async def generate_image(
    image: UploadFile = File(...),
    prompt: str = Form("Transform this image creatively"),
):
    """
    Generate a NEW image using Gemini 2.5 Flash Image model
    
    Args:
        image: The input image file
        prompt: Creative prompt for image generation (e.g., "Make this cat wear a crown in a castle")
    
    Returns:
        Generated image file
    """
    try:
        # Read and open the uploaded image
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Save temporarily for processing
        temp_input_path = OUTPUT_DIR / f"temp_input_{uuid.uuid4()}.png"
        img.save(temp_input_path)
        
        # Load image for Gemini
        input_image = Image.open(temp_input_path)
        
        # Generate new image using Gemini 2.5 Flash Image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt, input_image],
        )
        
        # Extract generated image
        generated_image = None
        analysis_text = ""
        
        for part in response.parts:
            if part.text is not None:
                analysis_text += part.text
            elif part.inline_data is not None:
                generated_image = part.as_image()
        
        # Clean up temp input
        if temp_input_path.exists():
            os.remove(temp_input_path)
        
        if generated_image:
            # Save generated image
            output_filename = f"generated_{uuid.uuid4()}.png"
            output_path = OUTPUT_DIR / output_filename
            generated_image.save(output_path)
            
            # Return the generated image
            return FileResponse(
                output_path,
                media_type="image/png",
                headers={
                    "X-Original-Filename": image.filename,
                    "X-Prompt": prompt,
                    "X-Analysis": analysis_text[:500] if analysis_text else "No text response",
                    "Content-Disposition": f"attachment; filename={output_filename}"
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"No image generated. Model response: {analysis_text}"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating image: {str(e)}"
        )

@app.post("/generate-image-with-details/")
async def generate_image_with_details(
    image: UploadFile = File(...),
    prompt: str = Form("Transform this image creatively"),
):
    """
    Generate image and return both the image URL and analysis text
    
    Args:
        image: The input image file
        prompt: Creative prompt for image generation
    
    Returns:
        JSON with image path and analysis
    """
    try:
        # Read and open the uploaded image
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Save temporarily for processing
        temp_input_path = OUTPUT_DIR / f"temp_input_{uuid.uuid4()}.png"
        img.save(temp_input_path)
        
        # Load image for Gemini
        input_image = Image.open(temp_input_path)
        
        # Generate new image using Gemini 2.5 Flash Image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt, input_image],
        )
        
        # Extract generated image and text
        generated_image = None
        analysis_text = ""
        
        for part in response.parts:
            if part.text is not None:
                analysis_text += part.text
            elif part.inline_data is not None:
                generated_image = part.as_image()
        
        # Clean up temp input
        if temp_input_path.exists():
            os.remove(temp_input_path)
        
        if generated_image:
            # Save generated image
            output_filename = f"generated_{uuid.uuid4()}.png"
            output_path = OUTPUT_DIR / output_filename
            generated_image.save(output_path)
            
            return JSONResponse(content={
                "success": True,
                "prompt": prompt,
                "analysis": analysis_text,
                "generated_image_path": str(output_path),
                "generated_image_filename": output_filename,
                "original_image": image.filename
            })
        else:
            return JSONResponse(content={
                "success": False,
                "prompt": prompt,
                "analysis": analysis_text,
                "error": "No image was generated, only text response"
            })
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )

@app.post("/analyze-image/")
async def analyze_image(
    image: UploadFile = File(...),
    prompt: str = Form("Analyze this image in detail")
):
    """
    Analyze image using Gemini 1.5 Pro (text analysis only, no image generation)
    
    Args:
        image: The image file to analyze
        prompt: Analysis prompt
    
    Returns:
        JSON with analysis text
    """
    try:
        # Read image
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Save temporarily
        temp_path = OUTPUT_DIR / f"temp_analyze_{uuid.uuid4()}.png"
        img.save(temp_path)
        
        # Load for Gemini
        input_image = Image.open(temp_path)
        
        # Analyze with Gemini 1.5 Pro (text only)
        response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents=[prompt, input_image],
        )
        
        # Extract text
        analysis_text = ""
        for part in response.parts:
            if part.text is not None:
                analysis_text += part.text
        
        # Clean up
        if temp_path.exists():
            os.remove(temp_path)
        
        return {
            "success": True,
            "filename": image.filename,
            "prompt": prompt,
            "analysis": analysis_text,
            "image_dimensions": f"{img.size[0]}x{img.size[1]}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )

@app.get("/download/{filename}")
async def download_image(filename: str):
    """Download a generated image"""
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        filename=filename
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)