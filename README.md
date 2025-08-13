# Nexora Brand Mixologist

An AI-powered creative platform that generates unique brand fusion concepts using LlamaIndex, Claude AI, and Stable Diffusion XL.

## 🚀 Features

- **Intelligent Brand Retrieval**: Uses LlamaIndex to query Wikipedia facts stored in ChromaDB
- **Creative AI Fusion**: Claude AI generates unique mashup concepts and marketing copy
- **High-Quality Image Generation**: Stable Diffusion XL creates professional visuals
- **Persistent Storage**: Supabase database for storing results and user interactions
- **Interactive Leaderboard**: Community voting and ranking system
- **Real-time Frontend**: Modern React interface with smooth animations

## 🛠 Technology Stack

- **Backend**: Flask, Python
- **AI Services**: LlamaIndex, Claude AI, Stable Diffusion XL
- **Database**: Supabase (PostgreSQL)
- **Vector Store**: ChromaDB
- **Frontend**: React, Vite, Framer Motion
- **Styling**: Custom CSS with glassmorphism design

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- API Keys for:
  - Anthropic Claude
  - HuggingFace (for Stable Diffusion)
  - Supabase project

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nexora-brand-mixologist
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   npm install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your API keys:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   HF_API_TOKEN=your_huggingface_api_token_here
   SUPABASE_URL=your_supabase_project_url_here
   SUPABASE_ANON_KEY=your_supabase_anon_key_here
   ```

5. **Set up Supabase database**
   - Create a new Supabase project
   - Run the migration in `supabase/migrations/create_brand_combos_table.sql`

6. **Initialize the knowledge base**
   ```bash
   python scripts/initialize_services.py
   ```

## 🚀 Running the Application

1. **Start the backend server**
   ```bash
   python backend/app.py
   ```

2. **Start the frontend development server**
   ```bash
   npm run dev
   ```

3. **Open your browser**
   Navigate to `http://localhost:3000`

## 🎯 How It Works

1. **User Input**: Select two brands and a fusion mode (competitive, collaborative, or fusion)

2. **Knowledge Retrieval**: LlamaIndex queries the ChromaDB vector store for relevant Wikipedia information about both brands

3. **AI Generation**: Claude AI processes the brand information and generates:
   - Creative fusion name
   - Marketing slogan
   - Detailed description
   - Host reaction
   - Compatibility score

4. **Image Creation**: Stable Diffusion XL generates a high-quality visual representation

5. **Storage**: Results are saved to Supabase for persistence and community interaction

6. **Community Features**: Users can vote on creations and view the leaderboard

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude AI API key | Yes |
| `HF_API_TOKEN` | HuggingFace API token | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Yes |
| `CLAUDE_MODEL` | Claude model version | No |
| `HF_IMAGE_MODEL` | Stable Diffusion model | No |

### Service Status

The application provides real-time service status indicators:
- 🟢 **LlamaIndex**: Knowledge retrieval system
- 🟢 **Claude AI**: Text generation service  
- 🟢 **Image Generation**: Stable Diffusion service
- 🟢 **Supabase**: Database and storage

## 📁 Project Structure

```
nexora-brand-mixologist/
├── backend/
│   ├── services/           # AI and database services
│   ├── app.py             # Flask application
├── frontend/
│   ├── components/        # React components
│   ├── lib/              # API and utilities
│   └── index.css         # Styling
├── scripts/              # Data pipeline and utilities
├── supabase/
│   └── migrations/       # Database schema
├── data/                 # Generated data and embeddings
└── requirements.txt      # Python dependencies
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check that all required environment variables are set
   - Ensure Python dependencies are installed
   - Verify API keys are valid

2. **Services showing as inactive**
   - Verify API keys in `.env` file
   - Check internet connection
   - Ensure Supabase project is properly configured

3. **Knowledge base not working**
   - Run `python scripts/initialize_services.py`
   - Check that ChromaDB files are created in `data/chroma/`

4. **Image generation failing**
   - Verify HuggingFace API token
   - Check that the model is accessible
   - Ensure sufficient API quota

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude AI
- **HuggingFace** for Stable Diffusion XL
- **LlamaIndex** for the retrieval framework
- **Supabase** for the backend infrastructure
- **ChromaDB** for vector storage