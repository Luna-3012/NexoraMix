# Nexora - Brand Mixologist

An AI-powered brand fusion gaming platform that creates innovative brand combinations using advanced AI technologies.

## Features

- **AI-Powered Brand Fusion**: Generate creative brand combinations using Claude AI
- **Multiple Fusion Modes**: Competitive, Collaborative, and Fusion approaches
- **Image Generation**: Create visual representations using Stable Diffusion
- **Real-time Leaderboard**: Vote and rank the best brand combinations
- **Knowledge Base**: Powered by LlamaIndex with brand information
- **Modern UI**: Built with React, Framer Motion, and modern design principles

## Tech Stack

### Frontend
- React 18 with Vite
- Framer Motion for animations
- Modern CSS with custom properties
- Responsive design

### Backend
- Python Flask API
- Claude AI (Anthropic) for text generation
- Stable Diffusion XL for image generation
- LlamaIndex for knowledge retrieval
- ChromaDB for vector storage
- Supabase for database and storage

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- API keys for Anthropic, HuggingFace, and Supabase

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd nexora-brand-mixologist
```

2. **Install frontend dependencies**
```bash
npm install
```

3. **Install backend dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Setup**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Initialize the knowledge base**
```bash
python scripts/initialize_services.py
```

6. **Start the development servers**

Frontend:
```bash
npm run dev
```

Backend (in a separate terminal):
```bash
npm run backend
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# HuggingFace API for Image Generation
HF_API_TOKEN=your_huggingface_api_token_here
HF_IMAGE_MODEL=stabilityai/stable-diffusion-xl-base-1.0

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Frontend Configuration
VITE_API_URL=http://localhost:5000
VITE_SUPABASE_URL=your_supabase_project_url_here
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

## API Endpoints

- `POST /generate` - Generate brand fusion
- `GET /leaderboard` - Get top combinations
- `POST /vote` - Vote for a combination
- `GET /stats` - Get platform statistics
- `GET /health` - Service health check

## Database Schema

The application uses Supabase with the following main table:

```sql
brand_combos (
  id uuid PRIMARY KEY,
  name text NOT NULL,
  slogan text,
  description text,
  product1 text NOT NULL,
  product2 text NOT NULL,
  mode text DEFAULT 'competitive',
  votes integer DEFAULT 0,
  host_reaction text,
  image_url text,
  compatibility_score integer DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
)
```

## Architecture

### Frontend Architecture
- **React Components**: Modular component structure
- **State Management**: React hooks for local state
- **API Layer**: Axios-based service layer
- **Animations**: Framer Motion for smooth transitions
- **Styling**: Modern CSS with CSS custom properties

### Backend Architecture
- **Service Layer**: Modular services for different AI providers
- **Fallback System**: Graceful degradation when services are unavailable
- **Error Handling**: Comprehensive error handling and logging
- **Database Integration**: Supabase for persistent storage

## Development

### Adding New Brands
1. Update `utils/constants.py` with new brand categories
2. Run the data pipeline: `python scripts/run_pipeline.py`
3. Restart the backend server

### Customizing AI Responses
- Modify prompts in `backend/services/claude_service.py`
- Adjust fallback responses for offline mode
- Update image generation prompts in `backend/services/image_service.py`

## Deployment

### Frontend (Netlify/Vercel)
```bash
npm run build
# Deploy the dist/ folder
```

### Backend (Railway/Heroku)
```bash
# Set environment variables in your hosting platform
# Deploy the backend/ folder
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue on GitHub or contact the development team.