# 🌾 AI-Based Crop Disease and Treatment Recommendation System

An AI-powered web application that detects crop diseases from leaf images and recommends suitable treatments, helping farmers identify plant health issues quickly and take timely action.

## 📌 Overview

This project uses a Convolutional Neural Network (CNN) built on **MobileNetV2** to classify crop diseases from leaf images. The model is served through a **Flask** backend API, with a **React** frontend that allows users to upload images and instantly view predictions along with treatment recommendations.

## ✨ Features

- 🔍 Upload a leaf image and get an instant disease prediction
- 🌱 Treatment recommendations based on the detected disease
- ⚡ Fast inference using a lightweight MobileNetV2 architecture
- 💻 Clean, responsive React-based user interface
- 🔗 REST API built with Flask for model inference

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Deep Learning Model | TensorFlow, Keras, CNN (MobileNetV2) |
| Backend | Python, Flask |
| Frontend | React, JavaScript, CSS |
| Image Processing | OpenCV |
| Other Tools | NumPy, Pandas, Scikit-learn |

## 📂 Project Structure

```
AI-crop-disease-detection/
│
├── backend/                # Flask API and model inference code
│   ├── app.py
│   ├── model/               # Trained MobileNetV2 model
│   └── requirements.txt
│
├── frontend/                # React application
│   ├── src/
│   ├── public/
│   └── package.json
│
└── README.md
```
*(Update this structure to match your actual folder layout)*

## ⚙️ How It Works

1. User uploads a leaf image through the React frontend
2. The image is sent to the Flask backend via a REST API call
3. The MobileNetV2 model processes the image and predicts the disease class
4. The backend returns the predicted disease along with a recommended treatment
5. The frontend displays the results to the user

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js and npm

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

The app should now be running locally — backend on `http://localhost:5000` and frontend on `http://localhost:3000` (update ports if different).

## 📊 Model Details

- **Architecture:** MobileNetV2 (transfer learning)
- **Dataset:** *(mention dataset name/source, e.g., PlantVillage)*
- **Accuracy:** *(add your model's accuracy, e.g., 95% on validation set)*
- **Classes:** *(number of disease classes the model can detect)*

## 📸 Screenshots

*(Add screenshots of your app here — upload page, prediction results, etc.)*

## 🔮 Future Improvements

- Add support for more crop types and diseases
- Deploy the app on a cloud platform (Render, AWS, etc.)
- Add multilingual support for farmers
- Mobile app version

## 👤 Author

**Jeevitha**
BCA (AI & ML), Mangalore University
[LinkedIn](#) • [GitHub](https://github.com/jeevimv856-cloud)

## 📄 License

This project is licensed under the MIT License.
