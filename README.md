# AutoDataCleanser

AutoDataCleanser is a full-stack application for automated data cleaning and analysis. It provides a modern web interface for uploading, cleaning, and analyzing CSV data files with powerful features like automatic data type detection, outlier removal, and data quality metrics.

## Features

- 🔐 Secure authentication with Supabase
- 📤 CSV file upload and validation
- 🧹 Automated data cleaning
- 📊 Data profiling and analysis
- 📈 Feature engineering
- 📥 Clean data download
- 🧪 Comprehensive smoke testing

## Tech Stack

### Backend
- FastAPI (Python web framework)
- Supabase (Authentication & Database)
- Pandas (Data manipulation)
- Scikit-learn (Data analysis)
- Uvicorn (ASGI server)

### Frontend
- Next.js (React framework)
- TailwindCSS (Styling)
- AG Grid (Data grid)
- Axios (HTTP client)
- Supabase JS Client

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm 8+
- Supabase account and project

## Environment Setup

### Backend (.env)
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_JWT_SECRET=your_jwt_secret
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_BASE=http://localhost:8000/api
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AutoDataCleanser.git
cd AutoDataCleanser
```

2. Install Python dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

## Development

1. Start the development servers:
```bash
python build.py
```

This will:
- Set up Python virtual environment
- Install all dependencies
- Start the backend server (http://localhost:8000)
- Start the frontend server (http://localhost:3000)
- Run smoke tests to verify functionality

## Smoke Tests

The smoke test suite verifies:
1. Authentication (signup/signin)
2. File upload
3. Data profiling
4. Data cleaning
5. Feature engineering
6. Data download

Run tests manually:
```bash
python smoke_test.py
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user

### Data Operations
- `POST /api/upload` - Upload CSV file
- `GET /api/profile/{session_id}` - Get data profile
- `POST /api/clean` - Clean data
- `GET /api/download/{session_id}` - Download cleaned data
- `POST /api/features` - Generate features

## Error Handling

The application includes comprehensive error handling:
- Input validation
- File format verification
- Authentication checks
- Data processing safeguards
- Detailed error logging

## Logging

Logs are written to:
- `build.log` - Build and setup process
- `smoke_test.log` - Test execution
- Backend logs in `backend/logs/`
- Frontend logs in browser console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details 