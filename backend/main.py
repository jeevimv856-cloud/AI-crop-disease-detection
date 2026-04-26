# main.py — FastAPI Backend (PyTorch version)
# Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np
from PIL import Image
import io, json, os

app = FastAPI(title="Crop Disease Detection API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# —— Load Model & Labels on Startup ————————————————
NUM_CLASSES = 9
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, NUM_CLASSES)
    model.load_state_dict(torch.load("model/crop_disease_model.pth",
                                     map_location=device))
    model.to(device)
    model.eval()
    return model

MODEL = None
LABELS = None
IDX2CLS = None

@app.on_event("startup")
def startup_event():
    global MODEL, LABELS, IDX2CLS
    if os.path.exists("model/crop_disease_model.pth") and \
       os.path.exists("model/class_labels.json"):
        MODEL = load_model()
        LABELS = json.load(open("model/class_labels.json"))
        IDX2CLS = {v: k for k, v in LABELS.items()}

# —— Treatment Database ————————————————————————————
TREATMENTS = {
  "Arecanut_Healthy": {
    "status": "Healthy",
    "description": "Plant is healthy. No disease detected.",
    "treatment": ["Continue regular watering and fertilization.",
                  "Apply balanced NPK fertilizer every 3 months.",
                  "Ensure proper drainage to prevent waterlogging."],
    "severity": "None",
    "prevention": ["Regular monitoring", "Maintain field hygiene"]
  },
  "Arecanut_BudRot": {
    "status": "Diseased",
    "description": "Bud Rot caused by Phytophthora palmivora fungus.",
    "treatment": ["Remove and destroy infected plant parts immediately.",
                  "Apply Bordeaux mixture (1%) to the crown of the palm.",
                  "Spray Metalaxyl + Mancozeb @ 2g/L water.",
                  "Avoid overhead irrigation to reduce humidity."],
    "severity": "High",
    "prevention": ["Good drainage", "Avoid bud injuries"]
  },
  "Arecanut_Koleroga": {
    "status": "Diseased",
    "description": "Koleroga (Fruit Rot) caused by Phytophthora meadii.",
    "treatment": ["Spray Bordeaux mixture (1%) before monsoon.",
                  "Apply Copper oxychloride @ 3g/L on bunches.",
                  "Remove and bury all fallen fruits away from field."],
    "severity": "High",
    "prevention": ["Pre-monsoon spraying", "Remove fallen fruits"]
  },
  "Arecanut_YellowLeaf": {
    "status": "Diseased",
    "description": "Yellow Leaf Disease caused by phytoplasma.",
    "treatment": ["Remove and destroy severely infected palms.",
                  "Spray Imidacloprid @ 0.5ml/L to control leafhoppers.",
                  "Apply micronutrient mixture (zinc, boron)."],
    "severity": "High",
    "prevention": ["Control leafhoppers", "Use certified seedlings"]
  },
  "Tomato_Healthy": {
    "status": "Healthy",
    "description": "Plant is healthy. No disease detected.",
    "treatment": ["Continue regular watering schedule.",
                  "Apply balanced fertilizer weekly."],
    "severity": "None",
    "prevention": ["Crop rotation", "Proper spacing"]
  },
  "Tomato_EarlyBlight": {
    "status": "Diseased",
    "description": "Early Blight caused by Alternaria solani fungus.",
    "treatment": ["Remove infected lower leaves immediately.",
                  "Spray Mancozeb @ 2.5g/L water every 7-10 days.",
                  "Apply Chlorothalonil @ 2g/L water."],
    "severity": "Medium",
    "prevention": ["Crop rotation", "Mulching"]
  },
  "Tomato_LateBlight": {
    "status": "Diseased",
    "description": "Late Blight caused by Phytophthora infestans.",
    "treatment": ["Act immediately — this disease spreads very fast.",
                  "Spray Metalaxyl + Mancozeb @ 2.5g/L water.",
                  "Repeat every 5-7 days during cool wet weather."],
    "severity": "Very High",
    "prevention": ["Resistant varieties", "Avoid overhead irrigation"]
  },
  "Tomato_LeafCurl": {
    "status": "Diseased",
    "description": "Leaf Curl Virus spread by whiteflies.",
    "treatment": ["Spray Imidacloprid @ 0.5ml/L to control whiteflies.",
                  "Use yellow sticky traps to catch whiteflies.",
                  "Remove and destroy heavily infected plants."],
    "severity": "High",
    "prevention": ["Insect-proof nets", "Reflective mulches"]
  },
  "Tomato_SeptoriaLeafSpot": {
    "status": "Diseased",
    "description": "Septoria Leaf Spot caused by Septoria lycopersici.",
    "treatment": ["Remove infected leaves immediately.",
                  "Spray Chlorothalonil @ 2g/L water every 7-10 days.",
                  "Apply Copper oxychloride @ 3g/L water."],
    "severity": "Medium",
    "prevention": ["Crop rotation", "Remove plant debris"]
  }
}

# —— Image Preprocessing ———————————————————————————
preprocess_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def preprocess(img_bytes: bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    tensor = preprocess_transform(img).unsqueeze(0)
    return tensor.to(device)

# —— Routes ————————————————————————————————————————
@app.get("/")
def root():
    return {"message": "Crop Disease Detection API is running"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(400, "Only JPG/PNG accepted.")
    if MODEL is None:
        raise HTTPException(503, "Model not loaded. Please train the model first.")
    img_bytes = await file.read()
    inp = preprocess(img_bytes)
    with torch.no_grad():
        outputs = MODEL(inp)
        probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()
    idx = int(np.argmax(probs))
    conf = float(np.max(probs)) * 100
    cls = IDX2CLS[idx]
    info = TREATMENTS.get(cls, {})
    top3 = [{"disease": IDX2CLS[i],
              "confidence": round(float(probs[i]) * 100, 2)}
             for i in np.argsort(probs)[::-1][:3]]
    return JSONResponse({
        "success": True,
        "predicted_class": cls,
        "confidence": round(conf, 2),
        "crop": "Arecanut" if "Arecanut" in cls else "Tomato",
        "disease_name": cls.split("_", 1)[1],
        "status": info.get("status", "Unknown"),
        "description": info.get("description", ""),
        "severity": info.get("severity", "Unknown"),
        "treatment": info.get("treatment", []),
        "prevention": info.get("prevention", []),
        "top3_predictions": top3
    })