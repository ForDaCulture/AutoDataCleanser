# AutoDataCleanser Frontend

A modern Next.js frontend for the AutoDataCleanser application, providing an intuitive interface for data cleaning and transformation.

## Features

- User authentication with Supabase
- File upload with drag-and-drop support
- Data preview with Ag-Grid
- Column statistics and data profiling
- Data cleaning and transformation
- Download cleaned data
- Audit logging

## Tech Stack

- Next.js 14+
- React
- TypeScript
- Tailwind CSS
- Ag-Grid
- Supabase Auth
- Axios

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env.local` file with your Supabase credentials:
   ```
   NEXT_PUBLIC_SUPABASE_URL=https://wphdrdnzpxgpdjhirirr.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

The application will be available at [http://localhost:3000](http://localhost:3000)

## Development

- `pages/` - Next.js pages and routing
- `components/` - Reusable React components
- `utils/` - Helper functions and API clients
- `styles/` - Global styles and Tailwind configuration

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000/api`. All API requests are authenticated using Supabase JWT tokens.

## Security

- All API requests include JWT authentication
- Protected routes require authentication
- Secure file handling and downloads
- Environment variables for sensitive data 