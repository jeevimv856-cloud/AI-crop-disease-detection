# train_model.py — CNN Model Training (PyTorch version)
# Arecanut & Tomato Disease Detection
# Model: MobileNetV2 Transfer Learning

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
import numpy as np
import json, os

# —— Configuration ————————————————————————————————
IMG_SIZE    = (224, 224)
BATCH_SIZE  = 32
EPOCHS      = 30
DATASET_DIR = "../dataset/"
MODEL_PATH  = "model/crop_disease_model.pth"
LABELS_PATH = "model/class_labels.json"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# —— Data Transforms ——————————————————————————————
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(30),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])
val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# —— Load Datasets ————————————————————————————————
train_dataset = datasets.ImageFolder(
    os.path.join(DATASET_DIR, 'train'), transform=train_transform)
val_dataset = datasets.ImageFolder(
    os.path.join(DATASET_DIR, 'val'), transform=val_transform)
test_dataset = datasets.ImageFolder(
    os.path.join(DATASET_DIR, 'test'), transform=val_transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE,
                          shuffle=True, num_workers=0)
val_loader   = DataLoader(val_dataset, batch_size=BATCH_SIZE,
                          shuffle=False, num_workers=0)
test_loader  = DataLoader(test_dataset, batch_size=BATCH_SIZE,
                          shuffle=False, num_workers=0)

NUM_CLASSES = len(train_dataset.classes)
print(f"Classes ({NUM_CLASSES}): {train_dataset.classes}")

# —— Save Class Labels ————————————————————————————
os.makedirs("model", exist_ok=True)
with open(LABELS_PATH, 'w') as f:
    json.dump(train_dataset.class_to_idx, f)
print(f"Labels saved to {LABELS_PATH}")

# —— Build Model (MobileNetV2) ————————————————————
model = models.mobilenet_v2(weights='IMAGENET1K_V1')

# Freeze base layers
for param in model.parameters():
    param.requires_grad = False

# Replace classifier
model.classifier[1] = nn.Linear(model.last_channel, NUM_CLASSES)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.2, patience=3)

# —— Training Function ————————————————————————————
def train_epoch(loader):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        correct += (outputs.argmax(1) == labels).sum().item()
        total += labels.size(0)
    return total_loss / len(loader), correct / total

def eval_epoch(loader):
    model.eval()
    total_loss, correct, total = 0, 0, 0
    with torch.no_grad():
        for imgs, labels in loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            total_loss += loss.item()
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)
    return total_loss / len(loader), correct / total

# —— Phase 1: Train classifier only (15 epochs) ———
print("\n=== Phase 1: Training classifier layers ===")
best_val_acc = 0
for epoch in range(15):
    train_loss, train_acc = train_epoch(train_loader)
    val_loss, val_acc     = eval_epoch(val_loader)
    scheduler.step(val_loss)
    print(f"Epoch {epoch+1}/15 | "
          f"Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | "
          f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}%")
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), MODEL_PATH)
        print(f"  ✅ Model saved (val_acc={val_acc*100:.2f}%)")

# —— Phase 2: Fine-tune last 30 layers ————————————
print("\n=== Phase 2: Fine-tuning ===")
for param in model.parameters():
    param.requires_grad = True
# Freeze all except last 30
all_params = list(model.parameters())
for param in all_params[:-30]:
    param.requires_grad = False

optimizer2 = optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()), lr=0.0001)
scheduler2 = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer2, mode='min', factor=0.2, patience=3)

for epoch in range(15, EPOCHS):
    train_loss, train_acc = train_epoch(train_loader)
    val_loss, val_acc     = eval_epoch(val_loader)
    scheduler2.step(val_loss)
    print(f"Epoch {epoch+1}/{EPOCHS} | "
          f"Train Loss: {train_loss:.4f} Acc: {train_acc*100:.2f}% | "
          f"Val Loss: {val_loss:.4f} Acc: {val_acc*100:.2f}%")
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), MODEL_PATH)
        print(f"  ✅ Model saved (val_acc={val_acc*100:.2f}%)")

# —— Evaluate on Test Set —————————————————————————
print("\n=== Test Set Evaluation ===")
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
test_loss, test_acc = eval_epoch(test_loader)
print(f"Test Accuracy: {test_acc*100:.2f}%  |  Loss: {test_loss:.4f}")
print(f"\nModel saved at: {MODEL_PATH}")
