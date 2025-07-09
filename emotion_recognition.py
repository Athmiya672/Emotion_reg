
import cv2
import numpy as np
from deepface import DeepFace
import pyttsx3
import threading
import time
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import queue

class EmotionRecognitionSystem:
    def __init__(self):
        self.cap = None
        self.is_running = False
        self.current_emotion = "Unknown"
        self.current_confidence = 0.0
        self.emotion_history = []
        self.voice_enabled = True
        self.last_voice_time = 0
        self.voice_cooldown = 3  # seconds
        
        # Initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.8)
        except:
            self.tts_engine = None
            print("Warning: Text-to-speech not available")
        
        # Create logs directory
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Emotion colors for display
        self.emotion_colors = {
            'happy': (0, 255, 0),      # Green
            'sad': (255, 0, 0),        # Blue
            'angry': (0, 0, 255),      # Red
            'surprise': (255, 255, 0), # Cyan
            'fear': (128, 0, 128),     # Purple
            'disgust': (0, 128, 128),  # Olive
            'neutral': (128, 128, 128) # Gray
        }

    def initialize_camera(self):
        """Initialize the webcam"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open webcam")
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False

    def detect_emotion(self, frame):
        """Detect emotion from frame using DeepFace"""
        try:
            # Analyze emotion
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            
            # Handle both single face and multiple faces
            if isinstance(result, list):
                result = result[0]
            
            dominant_emotion = result['dominant_emotion']
            confidence = result['emotion'][dominant_emotion]
            
            return dominant_emotion, confidence, result['emotion']
        
        except Exception as e:
            print(f"Emotion detection error: {e}")
            return "unknown", 0.0, {}

    def speak_emotion(self, emotion, confidence):
        """Speak the detected emotion"""
        if not self.tts_engine or not self.voice_enabled:
            return
        
        current_time = time.time()
        if current_time - self.last_voice_time < self.voice_cooldown:
            return
        
        def speak():
            try:
                message = f"You seem {emotion} with {int(confidence)} percent confidence"
                self.tts_engine.say(message)
                self.tts_engine.runAndWait()
            except:
                pass
        
        # Run TTS in separate thread to avoid blocking
        threading.Thread(target=speak, daemon=True).start()
        self.last_voice_time = current_time

    def log_emotion(self, emotion, confidence, all_emotions):
        """Log emotion data to file"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'dominant_emotion': emotion,
            'confidence': confidence,
            'all_emotions': all_emotions
        }
        
        log_file = f"logs/emotion_log_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            # Read existing logs
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new entry
            logs.append(log_entry)
            
            # Write back to file
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Logging error: {e}")

    def draw_emotion_info(self, frame, emotion, confidence, all_emotions):
        """Draw emotion information on frame"""
        height, width = frame.shape[:2]
        
        # Get color for current emotion
        color = self.emotion_colors.get(emotion.lower(), (255, 255, 255))
        
        # Main emotion text
        main_text = f"{emotion.upper()} - {confidence:.1f}%"
        cv2.putText(frame, main_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, color, 2, cv2.LINE_AA)
        
        # Draw emotion bar chart
        y_start = 60
        bar_height = 20
        max_width = 200
        
        cv2.putText(frame, "Emotion Breakdown:", (10, y_start), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        for i, (emo, conf) in enumerate(all_emotions.items()):
            y_pos = y_start + 25 + (i * 25)
            bar_width = int((conf / 100) * max_width)
            emo_color = self.emotion_colors.get(emo.lower(), (255, 255, 255))
            
            # Draw bar
            cv2.rectangle(frame, (10, y_pos), (10 + bar_width, y_pos + bar_height), 
                         emo_color, -1)
            cv2.rectangle(frame, (10, y_pos), (10 + max_width, y_pos + bar_height), 
                         (255, 255, 255), 1)
            
            # Draw text
            text = f"{emo}: {conf:.1f}%"
            cv2.putText(frame, text, (220, y_pos + 15), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.4, (255, 255, 255), 1)
        
        # Instructions
        instructions = [
            "Press 'q' to quit",
            "Press 'v' to toggle voice",
            "Press 's' to save screenshot"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (width - 250, height - 60 + (i * 20)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

    def run_console_mode(self):
        """Run the emotion recognition in console mode"""
        if not self.initialize_camera():
            return
        
        print("🎭 Real-Time Emotion Recognition System Started!")
        print("Press 'q' to quit, 'v' to toggle voice, 's' to save screenshot")
        print("-" * 50)
        
        self.is_running = True
        frame_count = 0
        
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Process every 3rd frame for better performance
            frame_count += 1
            if frame_count % 3 == 0:
                emotion, confidence, all_emotions = self.detect_emotion(frame)
                
                if emotion != "unknown":
                    self.current_emotion = emotion
                    self.current_confidence = confidence
                    
                    # Log emotion
                    self.log_emotion(emotion, confidence, all_emotions)
                    
                    # Speak emotion if high confidence
                    if confidence > 70:
                        self.speak_emotion(emotion, confidence)
                    
                    # Console output
                    print(f"Emotion: {emotion.upper()} - Confidence: {confidence:.1f}%")
            
            # Draw emotion info on frame
            if hasattr(self, 'current_emotion'):
                self.draw_emotion_info(frame, self.current_emotion, 
                                     self.current_confidence, all_emotions)
            
            # Display frame
            cv2.imshow('Emotion Recognition System', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('v'):
                self.voice_enabled = not self.voice_enabled
                status = "enabled" if self.voice_enabled else "disabled"
                print(f"Voice feedback {status}")
            elif key == ord('s'):
                # Save screenshot
                filename = f"emotion_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Screenshot saved as {filename}")
        
        self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("System stopped successfully!")

class EmotionGUI:
    def __init__(self):
        self.emotion_system = EmotionRecognitionSystem()
        self.root = tk.Tk()
        self.root.title("Real-Time Emotion Recognition System")
        self.root.geometry("800x600")
        
        self.video_frame = None
        self.is_running = False
        self.frame_queue = queue.Queue()
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video display
        self.video_label = ttk.Label(main_frame, text="Camera feed will appear here")
        self.video_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Emotion info
        info_frame = ttk.LabelFrame(main_frame, text="Emotion Information", padding="10")
        info_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.emotion_label = ttk.Label(info_frame, text="Emotion: Unknown", font=("Arial", 14))
        self.emotion_label.grid(row=0, column=0, pady=5)
        
        self.confidence_label = ttk.Label(info_frame, text="Confidence: 0%", font=("Arial", 12))
        self.confidence_label.grid(row=1, column=0, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Camera", command=self.start_camera)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Camera", command=self.stop_camera, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.voice_button = ttk.Button(button_frame, text="Toggle Voice", command=self.toggle_voice)
        self.voice_button.grid(row=0, column=2, padx=5)
        
        self.screenshot_button = ttk.Button(button_frame, text="Screenshot", command=self.take_screenshot)
        self.screenshot_button.grid(row=0, column=3, padx=5)
    
    def start_camera(self):
        """Start the camera and emotion recognition"""
        if self.emotion_system.initialize_camera():
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Start video processing thread
            threading.Thread(target=self.process_video, daemon=True).start()
            
            # Start GUI update
            self.update_gui()
        else:
            messagebox.showerror("Error", "Could not initialize camera")
    
    def stop_camera(self):
        """Stop the camera"""
        self.is_running = False
        self.emotion_system.cleanup()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.video_label.config(image="", text="Camera stopped")
    
    def toggle_voice(self):
        """Toggle voice feedback"""
        self.emotion_system.voice_enabled = not self.emotion_system.voice_enabled
        status = "enabled" if self.emotion_system.voice_enabled else "disabled"
        messagebox.showinfo("Voice Status", f"Voice feedback {status}")
    
    def take_screenshot(self):
        """Take a screenshot"""
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            filename = f"gui_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, self.current_frame)
            messagebox.showinfo("Screenshot", f"Screenshot saved as {filename}")
    
    def process_video(self):
        """Process video frames"""
        frame_count = 0
        
        while self.is_running:
            ret, frame = self.emotion_system.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            self.current_frame = frame.copy()
            
            # Process every 3rd frame
            frame_count += 1
            if frame_count % 3 == 0:
                emotion, confidence, all_emotions = self.emotion_system.detect_emotion(frame)
                
                if emotion != "unknown":
                    self.emotion_system.current_emotion = emotion
                    self.emotion_system.current_confidence = confidence
                    
                    # Log and speak
                    self.emotion_system.log_emotion(emotion, confidence, all_emotions)
                    if confidence > 70:
                        self.emotion_system.speak_emotion(emotion, confidence)
            
            # Convert frame for Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_pil = frame_pil.resize((640, 480), Image.Resampling.LANCZOS)
            frame_tk = ImageTk.PhotoImage(frame_pil)
            
            # Add to queue
            self.frame_queue.put((frame_tk, self.emotion_system.current_emotion, 
                                self.emotion_system.current_confidence))
    
    def update_gui(self):
        """Update the GUI with latest frame and emotion info"""
        try:
            if not self.frame_queue.empty():
                frame_tk, emotion, confidence = self.frame_queue.get_nowait()
                self.video_label.config(image=frame_tk, text="")
                self.video_label.image = frame_tk
                
                # Update emotion info
                self.emotion_label.config(text=f"Emotion: {emotion.upper()}")
                self.confidence_label.config(text=f"Confidence: {confidence:.1f}%")
        except queue.Empty:
            pass
        
        if self.is_running:
            self.root.after(30, self.update_gui)
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

def main():
    """Main function to run the application"""
    print("🎭 Real-Time Emotion Recognition System")
    print("=" * 50)
    print("Choose mode:")
    print("1. Console Mode (OpenCV window)")
    print("2. GUI Mode (Tkinter interface)")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            system = EmotionRecognitionSystem()
            system.run_console_mode()
        elif choice == "2":
            app = EmotionGUI()
            app.run()
        else:
            print("Invalid choice. Running console mode...")
            system = EmotionRecognitionSystem()
            system.run_console_mode()
            
    except KeyboardInterrupt:
        print("\nSystem interrupted by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    