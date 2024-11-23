# YouTube Downloader

A fullstack web application for downloading YouTube videos, built with React for the frontend and FastAPI for the backend.

## Features

- Download YouTube videos in different formats
- Modern and responsive user interface
- RESTful API with FastAPI
- Support for different video qualities

## Requirements

- Python 3.8+
- Node.js 14+
- npm or yarn

## Installation

### Backend

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
cd youtube_downloader
uvicorn main:app --reload
```

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Paste the URL of the YouTube video you want to download
3. Select the desired format and quality
4. Click on "Download"

## Technologies Used

- Frontend:
  - React
  - Material-UI
  - Axios

- Backend:
  - FastAPI
  - pytube
  - python-multipart

## License

MIT
