import os, shutil, random

base = '../dataset'

for cls in os.listdir(os.path.join(base, 'train')):
    train_path = os.path.join(base, 'train', cls)
    val_path   = os.path.join(base, 'val', cls)
    test_path  = os.path.join(base, 'test', cls)

    os.makedirs(val_path, exist_ok=True)
    os.makedirs(test_path, exist_ok=True)

    imgs = [f for f in os.listdir(train_path)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    random.shuffle(imgs)
    n = len(imgs)

    val_imgs  = imgs[:int(n * 0.2)]
    test_imgs = imgs[int(n * 0.2):int(n * 0.3)]

    for img in val_imgs:
        shutil.move(os.path.join(train_path, img),
                    os.path.join(val_path, img))
    for img in test_imgs:
        shutil.move(os.path.join(train_path, img),
                    os.path.join(test_path, img))

    print(f"{cls}: train={n - len(val_imgs) - len(test_imgs)}, "
          f"val={len(val_imgs)}, test={len(test_imgs)}")

print("\nDone! Dataset split complete.")