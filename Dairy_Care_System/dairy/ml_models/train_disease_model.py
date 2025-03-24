import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
import os
import json
from tensorflow.keras.models import load_model

def get_disease_classes(data_dir):
    """Get disease classes from directory structure"""
    try:
        # Get all subdirectories
        disease_classes = [d for d in os.listdir(data_dir) 
                         if os.path.isdir(os.path.join(data_dir, d))]
        
        if not disease_classes:
            raise Exception("No disease folders found!")
            
        # Print found classes
        print("\nFound disease classes:")
        for i, disease in enumerate(sorted(disease_classes)):
            num_images = len(os.listdir(os.path.join(data_dir, disease)))
            print(f"{i+1}. {disease} ({num_images} images)")
            
        return sorted(disease_classes)
    except Exception as e:
        print(f"Error reading disease classes: {str(e)}")
        raise

def train_disease_model(data_dir="C:/Users/TUF GAMING/Downloads/cows disease", 
                       model_save_path=None):
    print(f"\nAnalyzing directory: {data_dir}")
    
    if not os.path.exists(data_dir):
        raise Exception(f"Directory not found: {data_dir}")
        
    if model_save_path is None:
        model_dir = os.path.join(os.path.dirname(data_dir), 'ml_models')
        os.makedirs(model_dir, exist_ok=True)
        model_save_path = os.path.join(model_dir, 'cow_disease_model.h5')
    
    # Get disease classes
    disease_classes = get_disease_classes(data_dir)
    
    # Save class mapping
    class_indices = {i: class_name for i, class_name in enumerate(disease_classes)}
    class_map_path = os.path.join(os.path.dirname(model_save_path), 'class_mapping.json')
    
    print("\nSaving class mapping:")
    for idx, disease in class_indices.items():
        print(f"Class {idx}: {disease}")
        
    with open(class_map_path, 'w') as f:
        json.dump(class_indices, f, indent=4)
    print(f"\nClass mapping saved to: {class_map_path}")
    
    # Define parameters
    IMG_HEIGHT = 224
    IMG_WIDTH = 224
    BATCH_SIZE = 32
    EPOCHS = 20

    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        validation_split=0.2,
        brightness_range=[0.8, 1.2],
        fill_mode='nearest'
    )

    print("Loading and preprocessing training data...")
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )

    validation_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=True
    )

    print("Building model...")
    base_model = MobileNetV2(
        input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
        include_top=False,
        weights='imagenet'
    )
    base_model.trainable = False

    model = tf.keras.Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(1024, activation='relu'),
        Dropout(0.5),
        Dense(512, activation='relu'),
        Dropout(0.3),
        Dense(len(disease_classes), activation='softmax')
    ])

    # Compile model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    # Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=0.00001
        )
    ]

    print("Training model...")
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator,
        callbacks=callbacks,
        verbose=1
    )

    print(f"Saving model to {model_save_path}")
    model.save(model_save_path)
    
    return class_indices

if __name__ == "__main__":
    # Set the exact paths
    base_dir = r"C:\Users\TUF GAMING\Downloads\Dairy_Care_System\Dairy_Care_System"
    model_dir = os.path.join(base_dir, 'dairy', 'ml_models')
    os.makedirs(model_dir, exist_ok=True)
    
    model_save_path = os.path.join(model_dir, 'cow_disease_model.h5')
    class_map_path = os.path.join(model_dir, 'class_mapping.json')
    
    # Training data directory
    data_dir = r"C:/Users/TUF GAMING/Downloads/cows disease"
    
    print("\nConfiguration:")
    print(f"Model will be saved to: {model_save_path}")
    print(f"Class mapping will be saved to: {class_map_path}")
    print(f"Training data from: {data_dir}")
    
    try:
        # Verify training data directory exists
        if not os.path.exists(data_dir):
            raise Exception(f"Training data directory not found: {data_dir}")
            
        # Train model
        class_indices = train_disease_model(data_dir, model_save_path)
        
        # Verify files were created
        if not os.path.exists(model_save_path):
            raise Exception("Model file was not created")
        if not os.path.exists(class_map_path):
            raise Exception("Class mapping file was not created")
            
        print("\nTraining completed successfully!")
        print(f"Model saved to: {model_save_path}")
        print(f"Class mapping saved to: {class_map_path}")
        print(f"\nClass mapping: {class_indices}")
        
        # Verify model can be loaded
        test_model = load_model(model_save_path)
        print("Model loaded successfully for verification")
        
    except Exception as e:
        print(f"\nError during training: {str(e)}") 