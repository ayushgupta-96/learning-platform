# Education Platform

An online education platform for students and teachers with video chat and training features.

## Setup

1. Navigate to the backend directory:
   ```
   cd education-platform/backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```
   python run.py
   ```

## Access

Once the server is running, you can access the education platform at:
- **http://localhost:5000**

## Features

- Student and teacher registration/login
- Training sessions
- Video chat functionality
- Points system
- Real-time communication via Socket.IO