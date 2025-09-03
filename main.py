from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
import qrcode
import random
import os
import base64
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="Recipe QR Generator API")

# -------------------
# Enable CORS for all origins (for testing/demo purposes)
# -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the folder for QR codes exists
if not os.path.exists("qr_codes"):
    os.makedirs("qr_codes")

# API keys for team access
VALID_KEYS = ["TEAMKEY1", "TEAMKEY2", "TEAMKEY3"]

# Predefined recipes
recipes = [
    {
        "name": "Spaghetti Carbonara",
        "ingredients": ["Spaghetti", "Eggs", "Parmesan", "Bacon", "Black Pepper"]
    },
    {
        "name": "Avocado Toast",
        "ingredients": ["Bread", "Avocado", "Lemon", "Salt", "Pepper"]
    },
    {
        "name": "Chocolate Mug Cake",
        "ingredients": ["Flour", "Cocoa Powder", "Sugar", "Egg", "Milk", "Butter"]
    },
    {
        "name": "Chicken Salad",
        "ingredients": ["Chicken Breast", "Lettuce", "Tomatoes", "Cucumber", "Olive Oil"]
    }
]

# -------------------
# Root endpoint
# -------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Recipe QR Generator API! Use /docs to explore endpoints."}

# -------------------
# Generate recipe + QR (Base64)
# -------------------
@app.get("/recipe_qr")
def generate_recipe_qr(x_api_key: str = Header(...)):
    if x_api_key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    # Pick a random recipe
    recipe = random.choice(recipes)
    recipe_text = f"{recipe['name']}\nIngredients:\n" + "\n".join(recipe['ingredients'])
    
    # Generate QR code
    qr_img = qrcode.make(recipe_text)

    # Save QR code to memory
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)
    
    # Encode as Base64
    qr_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    
    # Also save PNG file for reference (optional)
    filename = f"qr_codes/{recipe['name'].replace(' ', '_')}.png"
    qr_img.save(filename)
    
    return {
        "recipe_name": recipe['name'],
        "ingredients": recipe['ingredients'],
        "qr_code_base64": qr_base64,
        "qr_code_file": filename
    }

# -------------------
# Retrieve QR image
# -------------------
@app.get("/recipe_qr_image/{recipe_name}")
def get_qr_image(recipe_name: str, x_api_key: str = Header(...)):
    if x_api_key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    filename = f"qr_codes/{recipe_name.replace(' ', '_')}.png"
    if os.path.exists(filename):
        return FileResponse(filename, media_type="image/png")
    else:
        return {"error": "QR code not found. Generate recipe first."}

# -------------------
# Check API key validity
# -------------------
@app.get("/check_key")
def check_key(x_api_key: str = Header(...)):
    if x_api_key in VALID_KEYS:
        return {"status": "API Key is valid"}
    else:
        raise HTTPException(status_code=401, detail="Invalid API Key")
