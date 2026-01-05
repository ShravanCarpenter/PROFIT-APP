import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json
import os
import logging
from PIL import Image
import glob
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YogaPoseTrainer:
    def __init__(self):
        # Initialize MediaPipe pose detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Yoga pose classes (matching your Flask app)
        self.pose_classes = [
            'Akarna Dhanurasana', 'Bharadvajas Twist Pose', 'Boat Pose', 'Bound Angle Pose',
            'Bow Pose', 'Bridge Pose', 'Camel Pose', 'Cat Cow Pose', 'Chair Pose', 'Child Pose',
            'Cobra Pose', 'Cockerel Pose', 'Corpse Pose', 'Cow Face Pose', 'Crane Pose',
            'Dolphin Plank Pose', 'Dolphin Pose', 'Downward Dog', 'Eagle Pose', 'Eight-Angle Pose',
            'Extended Puppy Pose', 'Extended Revolved Side Angle Pose', 'Extended Revolved Triangle Pose',
            'Feathered Peacock Pose', 'Firefly Pose', 'Fish Pose', 'Four-Limbed Staff Pose',
            'Frog Pose', 'Garland Pose', 'Gate Pose', 'Half Lord of the Fishes Pose',
            'Half Moon Pose', 'Handstand Pose', 'Happy Baby Pose', 'Head-to-Knee Forward Bend',
            'Heron Pose', 'Intense Side Stretch Pose', 'Legs-Up-the-Wall Pose', 'Locust Pose',
            'Lord of the Dance Pose', 'Low Lunge Pose', 'Mountain Pose', 'Noose Pose',
            'Peacock Pose', 'Pigeon Pose', 'Plank Pose', 'Plow Pose', 'Pose Dedicated to Sage Koundinya',
            'Rajakapotasana', 'Reclining Hand-to-Big-Toe Pose', 'Revolved Head-to-Knee Pose',
            'Scale Pose', 'Scorpion Pose', 'Seated Forward Bend', 'Shoulder-Pressing Pose',
            'Side Crane Pose', 'Side Plank Pose', 'Side-Reclining Leg Lift', 'Sitting Pose',
            'Split Pose', 'Staff Pose', 'Standing Big Toe Hold', 'Standing Forward Bend',
            'Standing Split', 'Supported Headstand', 'Supported Shoulderstand', 'Supta Baddha Konasana',
            'Supta Virasana', 'Tortoise Pose', 'Tree Pose', 'Triangle Pose', 'Upward Bow Pose',
            'Upward Facing Two-Foot Staff Pose', 'Upward Plank Pose', 'Reverse Warrior Pose',
            'Virasana', 'Warrior I', 'Warrior II', 'Warrior III', 'Wide-Angle Seated Forward Bend',
            'Wide-Legged Forward Bend', 'Wild Thing Pose', 'Wind Relieving Pose', 'Yogic Sleep Pose'
        ]
        
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(self.pose_classes)
        
    def extract_keypoints(self, image_path):
        """Extract pose keypoints from an image using MediaPipe"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process the image
            results = self.pose.process(rgb_image)
            
            if results.pose_landmarks:
                # Extract keypoints
                keypoints = []
                for landmark in results.pose_landmarks.landmark:
                    keypoints.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
                
                return np.array(keypoints)
            else:
                return None
        except Exception as e:
            logger.error(f"Error extracting keypoints from {image_path}: {e}")
            return None
    
    def generate_synthetic_data(self, num_samples_per_class=100):
        """Generate synthetic training data for yoga poses"""
        logger.info("Generating synthetic training data...")
        
        X = []
        y = []
        
        # Generate synthetic keypoints for each pose class
        for pose_class in self.pose_classes:
            logger.info(f"Generating data for {pose_class}...")
            
            for _ in range(num_samples_per_class):
                # Generate synthetic keypoints (33 landmarks * 4 coordinates each = 132 features)
                # Add some realistic constraints and variations
                
                # Base keypoints with some pose-specific modifications
                keypoints = np.random.rand(132) * 0.8 + 0.1  # Values between 0.1 and 0.9
                
                # Add pose-specific patterns
                if 'Mountain' in pose_class or 'Standing' in pose_class:
                    # Standing poses - feet on ground, upright posture
                    keypoints[91:95] = [0.3, 0.9, 0.0, 0.9]  # Left ankle
                    keypoints[95:99] = [0.7, 0.9, 0.0, 0.9]  # Right ankle
                    keypoints[43:47] = [0.5, 0.3, 0.0, 0.9]  # Nose - centered and high
                
                elif 'Child' in pose_class or 'Seated' in pose_class:
                    # Seated/ground poses
                    keypoints[91:95] = [0.3, 0.7, 0.0, 0.9]  # Left ankle
                    keypoints[95:99] = [0.7, 0.7, 0.0, 0.9]  # Right ankle
                    keypoints[43:47] = [0.5, 0.6, 0.0, 0.9]  # Nose - lower
                
                elif 'Warrior' in pose_class:
                    # Warrior poses - wide stance
                    keypoints[91:95] = [0.2, 0.8, 0.0, 0.9]  # Left ankle
                    keypoints[95:99] = [0.8, 0.8, 0.0, 0.9]  # Right ankle
                    keypoints[43:47] = [0.5, 0.3, 0.0, 0.9]  # Nose
                
                elif 'Downward' in pose_class:
                    # Downward dog - inverted V shape
                    keypoints[63:67] = [0.3, 0.7, 0.0, 0.9]  # Left wrist
                    keypoints[67:71] = [0.7, 0.7, 0.0, 0.9]  # Right wrist
                    keypoints[91:95] = [0.3, 0.8, 0.0, 0.9]  # Left ankle
                    keypoints[95:99] = [0.7, 0.8, 0.0, 0.9]  # Right ankle
                    keypoints[43:47] = [0.5, 0.75, 0.0, 0.9]  # Nose - between hands and feet
                
                # Add noise for variation
                noise = np.random.normal(0, 0.02, 132)
                keypoints += noise
                keypoints = np.clip(keypoints, 0, 1)  # Keep values in valid range
                
                X.append(keypoints)
                y.append(pose_class)
        
        logger.info(f"Generated {len(X)} samples across {len(self.pose_classes)} classes")
        return np.array(X), np.array(y)
    
    def load_real_data(self, data_dir):
        """Load real yoga pose images from directory structure"""
        logger.info(f"Loading real data from {data_dir}...")
        
        X = []
        y = []
        
        if not os.path.exists(data_dir):
            logger.warning(f"Data directory {data_dir} not found. Using synthetic data only.")
            return np.array(X), np.array(y)
        
        # Expected directory structure: data_dir/pose_name/image_files
        for pose_class in self.pose_classes:
            pose_dir = os.path.join(data_dir, pose_class.replace(' ', '_'))
            if os.path.exists(pose_dir):
                image_files = glob.glob(os.path.join(pose_dir, '*.jpg')) + \
                             glob.glob(os.path.join(pose_dir, '*.png')) + \
                             glob.glob(os.path.join(pose_dir, '*.jpeg'))
                
                for image_file in image_files:
                    keypoints = self.extract_keypoints(image_file)
                    if keypoints is not None:
                        X.append(keypoints)
                        y.append(pose_class)
                
                if image_files:
                    logger.info(f"Loaded {len(image_files)} images for {pose_class}")
        
        logger.info(f"Loaded {len(X)} real samples")
        return np.array(X), np.array(y)
    
    def create_model(self, input_shape):
        """Create the neural network model"""
        model = Sequential([
            Dense(512, activation='relu', input_shape=(input_shape,)),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(256, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(128, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(64, activation='relu'),
            Dropout(0.2),
            
            Dense(len(self.pose_classes), activation='softmax')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train_model(self, data_dir=None, epochs=100, batch_size=32):
        """Train the yoga pose detection model"""
        logger.info("Starting model training...")
        
        # Load data
        if data_dir and os.path.exists(data_dir):
            X_real, y_real = self.load_real_data(data_dir)
            X_synthetic, y_synthetic = self.generate_synthetic_data(50)  # Less synthetic data if we have real data
            
            if len(X_real) > 0:
                X = np.vstack([X_real, X_synthetic])
                y = np.hstack([y_real, y_synthetic])
            else:
                X, y = X_synthetic, y_synthetic
        else:
            X, y = self.generate_synthetic_data(200)  # More synthetic data if no real data
        
        # Encode labels
        y_encoded = self.label_encoder.transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        logger.info(f"Training set: {X_train.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        # Create model
        model = self.create_model(X_train.shape[1])
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=10,
            min_lr=0.0001
        )
        
        # Train model
        history = model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, reduce_lr],
            verbose=1
        )
        
        # Evaluate model
        test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
        logger.info(f"Test accuracy: {test_accuracy:.4f}")
        
        return model, history
    
    def save_model(self, model, model_path='yoga_pose_model.h5', labels_path='yoga_pose_model_labels.json'):
        """Save the trained model and labels"""
        logger.info(f"Saving model to {model_path}")
        model.save(model_path)
        
        # Save labels
        label_data = {
            'classes': self.pose_classes,
            'num_classes': len(self.pose_classes)
        }
        
        with open(labels_path, 'w') as f:
            json.dump(label_data, f, indent=2)
        
        logger.info(f"Labels saved to {labels_path}")
    
    def plot_training_history(self, history):
        """Plot training history"""
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        plt.subplot(1, 2, 2)
        plt.plot(history.history['accuracy'], label='Training Accuracy')
        plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('training_history.png')
        plt.show()

def main():
    """Main training function"""
    trainer = YogaPoseTrainer()
    
    # Train the model
    # If you have a dataset, provide the path like: data_dir='path/to/your/yoga_dataset'
    model, history = trainer.train_model(data_dir=None, epochs=50, batch_size=32)
    
    # Save the model
    trainer.save_model(model)
    
    # Plot training history
    trainer.plot_training_history(history)
    
    logger.info("Training completed successfully!")
    logger.info("Files generated:")
    logger.info("- yoga_pose_model.h5")
    logger.info("- yoga_pose_model_labels.json")
    logger.info("- training_history.png")

if __name__ == "__main__":
    main()