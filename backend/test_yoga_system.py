import requests
import base64
import json
import cv2
import numpy as np
from PIL import Image
import io
import time

class YogaSystemTester:
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
    
    def test_api_connection(self):
        """Test if the API is running"""
        try:
            response = requests.get(f"{self.api_url}/")
            if response.status_code == 200:
                print("✅ API is running successfully!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ API returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to API. Make sure the Flask app is running.")
            return False
        except Exception as e:
            print(f"❌ Error testing API connection: {e}")
            return False
    
    def test_health_check(self):
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed!")
                print(f"Model loaded: {data.get('model_loaded', 'Unknown')}")
                print(f"Supported poses: {data.get('supported_poses', 'Unknown')}")
                return True
            else:
                print(f"❌ Health check failed with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error in health check: {e}")
            return False
    
    def test_get_poses(self):
        """Test getting list of poses"""
        try:
            response = requests.get(f"{self.api_url}/poses")
            if response.status_code == 200:
                data = response.json()
                print("✅ Successfully retrieved poses list!")
                print(f"Total poses: {data.get('total_poses', 'Unknown')}")
                
                # Show a few examples
                poses_by_difficulty = data.get('poses_by_difficulty', {})
                for difficulty, poses in poses_by_difficulty.items():
                    print(f"{difficulty}: {len(poses)} poses")
                    if poses:
                        print(f"  Example: {poses[0]['name']}")
                return True
            else:
                print(f"❌ Failed to get poses list: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error getting poses list: {e}")
            return False
    
    def test_pose_info(self, pose_name="Mountain Pose"):
        """Test getting information about a specific pose"""
        try:
            response = requests.get(f"{self.api_url}/pose/{pose_name}")
            if response.status_code == 200:
                data = response.json()
                pose_info = data.get('pose', {})
                print(f"✅ Successfully retrieved info for {pose_name}!")
                print(f"Difficulty: {pose_info.get('difficulty', 'Unknown')}")
                print(f"Benefits: {pose_info.get('benefits', [])}")
                print(f"Feedback tips: {len(pose_info.get('feedback', []))} tips available")
                return True
            else:
                print(f"❌ Failed to get pose info: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error getting pose info: {e}")
            return False
    
    def create_test_image(self):
        """Create a simple test image"""
        # Create a simple colored image
        img = np.zeros((400, 300, 3), dtype=np.uint8)
        img.fill(255)  # White background
        
        # Add some simple shapes to simulate a person
        cv2.rectangle(img, (140, 50), (160, 150), (0, 0, 255), -1)  # Head (red)
        cv2.rectangle(img, (130, 150), (170, 250), (0, 255, 0), -1)  # Body (green)
        cv2.rectangle(img, (100, 180), (130, 220), (255, 0, 0), -1)  # Left arm (blue)
        cv2.rectangle(img, (170, 180), (200, 220), (255, 0, 0), -1)  # Right arm (blue)
        cv2.rectangle(img, (135, 250), (155, 350), (0, 255, 255), -1)  # Left leg (cyan)
        cv2.rectangle(img, (155, 250), (175, 350), (0, 255, 255), -1)  # Right leg (cyan)
        
        return img
    
    def image_to_base64(self, image):
        """Convert OpenCV image to base64 string"""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(image_rgb)
        
        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{img_str}"
    
    def test_pose_detection(self):
        """Test pose detection with a test image"""
        try:
            # Create test image
            test_image = self.create_test_image()
            
            # Convert to base64
            image_data = self.image_to_base64(test_image)
            
            # Send detection request
            payload = {"image": image_data}
            response = requests.post(f"{self.api_url}/detect", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    if data.get('pose_detected'):
                        print("✅ Pose detection successful!")
                        print(f"Detected pose: {data.get('pose_name', 'Unknown')}")
                        print(f"Confidence: {data.get('confidence', 0):.2f}")
                        print(f"Accuracy: {data.get('accuracy', 0):.1f}%")
                        print(f"Difficulty: {data.get('difficulty', 'Unknown')}")
                        print(f"Feedback points: {len(data.get('feedback', []))}")
                        return True
                    else:
                        print("⚠️ No pose detected in image")
                        print(f"Message: {data.get('message', 'No message')}")
                        return True  # This is still a successful API call
                else:
                    print(f"❌ Detection failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ Detection request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error in pose detection test: {e}")
            return False
    
    def test_feedback_endpoint(self):
        """Test the feedback endpoint"""
        try:
            payload = {
                "pose_name": "Mountain Pose",
                "accuracy": 85
            }
            response = requests.post(f"{self.api_url}/feedback", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Feedback endpoint working!")
                    print(f"Pose: {data.get('pose_name')}")
                    print(f"Accuracy: {data.get('accuracy')}%")
                    print(f"Feedback: {data.get('feedback', [])}")
                    return True
                else:
                    print(f"❌ Feedback failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Feedback request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing feedback endpoint: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧘 Starting Yoga Detection System Tests\n")
        
        tests = [
            ("API Connection", self.test_api_connection),
            ("Health Check", self.test_health_check),
            ("Get Poses List", self.test_get_poses),
            ("Get Pose Info", self.test_pose_info),
            ("Pose Detection", self.test_pose_detection),
            ("Feedback Endpoint", self.test_feedback_endpoint)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            print("-" * 40)
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)  # Small delay between tests
        
        # Summary
        print("\n" + "="*50)
        print("🏆 TEST SUMMARY")
        print("="*50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nTotal: {passed}/{len(results)} tests passed")
        
        if passed == len(results):
            print("🎉 All tests passed! Your yoga detection system is working perfectly!")
        else:
            print("⚠️ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    tester = YogaSystemTester()
    tester.run_all_tests()