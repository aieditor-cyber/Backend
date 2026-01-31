# Gemini Image Generation API

FastAPI backend for generating and analyzing images using Google's Gemini AI models.

## Features

- 🎨 **Image Generation**: Generate new images using Gemini 2.5 Flash Image model
- 🔍 **Image Analysis**: Analyze images with Gemini 1.5 Pro (text-only analysis)
- 📦 **Multiple Response Formats**: Get images directly or with detailed JSON metadata
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose

## API Endpoints

### `POST /generate-image/`
Generate a new image based on an uploaded image and prompt.

**Parameters:**
- `image`: Image file (multipart/form-data)
- `prompt`: Creative transformation prompt (default: "Transform this image creatively")

**Returns:** Generated image file

### `POST /generate-image-with-details/`
Generate image and return both the image path and analysis text.

**Parameters:**
- `image`: Image file
- `prompt`: Creative transformation prompt

**Returns:** JSON with image path, analysis, and metadata

### `POST /analyze-image/`
Analyze an image using Gemini 1.5 Pro (text analysis only).

**Parameters:**
- `image`: Image file
- `prompt`: Analysis prompt (default: "Analyze this image in detail")

**Returns:** JSON with analysis text

### `GET /download/{filename}`
Download a previously generated image.

### `GET /health`
Health check endpoint.

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and run:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Stop:**
   ```bash
   docker-compose down
   ```

### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t gemini-image-api .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -v $(pwd)/outputs:/app/outputs \
     -e GOOGLE_API_KEY=your_api_key_here \
     --name gemini-api \
     gemini-image-api
   ```

3. **View logs:**
   ```bash
   docker logs -f gemini-api
   ```

4. **Stop and remove:**
   ```bash
   docker stop gemini-api
   docker rm gemini-api
   ```

## Local Development

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python app.py
   ```

   Or with uvicorn:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

## Environment Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key (required)

## Testing the API

### Using curl

**Generate an image:**
```bash
curl -X POST "http://localhost:8000/generate-image/" \
  -F "image=@/path/to/your/image.jpg" \
  -F "prompt=Make this cat wear a crown in a castle" \
  --output generated_image.png
```

**Analyze an image:**
```bash
curl -X POST "http://localhost:8000/analyze-image/" \
  -F "image=@/path/to/your/image.jpg" \
  -F "prompt=Describe this image in detail"
```

### Using Python

```python
import requests

# Generate image
with open('input.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/generate-image/',
        files={'image': f},
        data={'prompt': 'Transform this into a watercolor painting'}
    )
    
with open('output.png', 'wb') as f:
    f.write(response.content)

# Analyze image
with open('input.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/analyze-image/',
        files={'image': f},
        data={'prompt': 'What objects are in this image?'}
    )
    
print(response.json())
```

## Project Structure

```
Backend/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── .dockerignore         # Docker build exclusions
├── .gitignore           # Git exclusions
├── .env                 # Environment variables (not in git)
└── outputs/             # Generated images directory
```

## Models Used

- **Gemini 2.5 Flash Image**: For image generation
- **Gemini 1.5 Pro**: For image analysis (text only)

## License

MIT
