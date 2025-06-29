import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam

# === Step 1: Configurations ===
IMG_SIZE = 224
BATCH_SIZE = 8
EPOCHS = 5
DATASET_PATH = 'dataset'
MODEL_PATH = 'model/fake_payment_detector_model.h5'

# === Step 2: Prepare Data ===
print("🔄 Loading and preprocessing dataset...")

datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_data = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='training'
)

val_data = datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary',
    subset='validation'
)

# === Step 3: Load MobileNetV2 base ===
print("📦 Loading MobileNetV2 model...")
base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_tensor=Input(shape=(IMG_SIZE, IMG_SIZE, 3))
)
base_model.trainable = False  # Freeze pretrained layers

# === Step 4: Add Custom Classification Layers ===
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(64, activation='relu')(x)
output = Dense(1, activation='sigmoid')(x)  # Binary classification

model = Model(inputs=base_model.input, outputs=output)

# === Step 5: Compile Model ===
model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# === Step 6: Train the Model ===
print("🚀 Training started...")
model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS
)
print("✅ Training complete.")

# === Step 7: Save the Model ===
if not os.path.exists('model'):
    os.makedirs('model')

model.save(MODEL_PATH)
print(f"📁 Model saved at: {MODEL_PATH}")