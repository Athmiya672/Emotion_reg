Algorithms:

Face Detection: The system employs deep learning-based face detection algorithms such as SSD (Single Shot MultiBox Detector) and RetinaFace. These algorithms are responsible for accurately locating faces within the video frames.

Emotion Recognition: For emotion classification, the project leverages advanced deep learning models like VGG-Face, FaceNet, and OpenFace. These models extract unique facial embeddings which are then used to predict emotions.

Libraries and Frameworks:

Python: The core programming language for the entire system.

OpenCV (cv2): Used for fundamental video processing tasks, including capturing frames from the webcam, performing basic image preprocessing (like flipping), and overlaying visual information (text, rectangles) onto the video feed. It also handles displaying the video in console mode.

DeepFace: This is a crucial, high-level library that wraps and integrates the various face detection and emotion recognition algorithms (VGG-Face, FaceNet, OpenFace, SSD, RetinaFace). It simplifies the complex pipeline of facial analysis, allowing the system to easily utilize these state-of-the-art models.

pyttsx3: Provides cross-platform text-to-speech capabilities, enabling the optional audio announcements of detected emotions.

tkinter & Pillow (PIL): These are used together to build the graphical user interface (GUI). tkinter provides the UI elements (windows, buttons, labels), while Pillow assists in handling and displaying image data within the Tkinter environment.

numpy: Essential for efficient numerical operations, particularly when working with image data represented as arrays.

threading & queue: These Python modules are vital for managing concurrency. threading allows different parts of the application (like video processing, UI updates, and voice output) to run simultaneously without blocking each other, and queue facilitates safe communication between these threads.

json, os, datetime: Standard Python libraries used for file operations (like creating directories and saving logs), handling JSON data for logging, and managing timestamps for log entries and screenshots.
