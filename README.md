# Pothole Detection and Reporting System

An intelligent system leveraging YOLOv8 and computer vision to automatically detect potholes from video feeds, assess their severity, and report them to authorities via a user-friendly dashboard.

## 🚀 Features

- **Automated Detection**: Uses advanced YOLOv8 computer vision models to detect potholes in uploaded videos with high accuracy.
- **AI-Powered Severity Assessment**: Automatically calculates the priority of complaints based on the confidence and severity of detected potholes.
- **Location Tracking**: Reports include precise location data to help authorities dispatch repair crews efficiently.
- **User Dashboard**: simple interface for citizens to upload complaints and track their status.
- **Employee Dashboard**: Comprehensive view for authorities to manage, update, and resolve complaints.
- **Video Evidence**: securely stores and processes video evidence for every complaint.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI Model**: YOLOv8 (Ultralytics)
- **Database**: SQLite (Development), extensible to PostgreSQL
- **Computer Vision**: OpenCV

## 📦 Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js (optional, for advanced frontend dev)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Harshabarik2005/pothole-detection-and-reporting.git
cd pothole-detection-and-reporting
```

### 2. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the Server
Start the FastAPI server:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000`.

### 4. Frontend Setup
The frontend is built with vanilla HTML/JS. You can simply open the files in your browser or use a simple HTTP server.
For the best experience, run a local server in the `frontend` directory:
```bash
# using python
cd ../frontend
python -m http.server 8080
```
Then open `http://localhost:8080/login.html` in your browser.

## 📝 Usage

1. **Register** a new account.
2. **Log in** to access your dashboard.
3. **Submit a Complaint**: Upload a video of a road with potholes.
4. **View Status**: Track the progress of your complaint as it is processed and resolved.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
