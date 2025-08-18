# Nestle Sentiment Analysis Project

This project analyzes sentiment toward Nestle using social media data from Threads, providing detailed confidence-based sentiment scoring and interactive visualizations.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
python setup_environment.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one from [OpenAI Platform](https://platform.openai.com/api-keys))
- Internet connection for API calls

## 🔧 Setup Instructions

1. **Clone or download this project**
2. **Run the setup script:**
   ```bash
   python setup_environment.py
   ```
3. **Configure your API key:**
   - Edit the `.env` file
   - Replace `your_openai_api_key_here` with your actual OpenAI API key
4. **Run the analysis:**
   ```bash
   python step_2_sentimnt_analysis.py
   python step_3_dashboard.py
   ```

## 📁 Project Structure

```
Nestle Sentiment Analysis/
├── step_2_sentimnt_analysis.py    # Main sentiment analysis script
├── step_3_dashboard.py            # Dashboard generation script
├── threads_scraper.js             # Data collection script
├── requirements.txt               # Python dependencies
├── setup_environment.py          # Environment setup script
├── README.md                     # This file
└── .env                          # API configuration (created during setup)
```

## 🔍 How It Works

### Step 1: Data Collection
- Uses `threads_scraper.js` to collect posts about Nestle from Threads
- Saves data in JSON format with timestamps

### Step 2: Sentiment Analysis
- `step_2_sentimnt_analysis.py` processes the collected data
- Uses OpenAI's GPT-4o-mini model via LangChain
- Assigns confidence scores (0.0-1.0) for sentiment toward Nestle
- Lower scores = more negative/pro-boycott sentiment
- Higher scores = more positive/pro-Nestle sentiment

### Step 3: Dashboard Generation
- `step_3_dashboard.py` creates interactive visualizations
- Generates HTML dashboard with multiple charts
- Provides detailed sentiment breakdown and statistics

## 📊 Confidence Score Scale

- **0.0 - 0.1**: Extremely negative toward Nestle, strongly pro-boycott
- **0.1 - 0.3**: Clearly negative, supports boycott
- **0.3 - 0.4**: Somewhat negative, mild criticism
- **0.4 - 0.6**: Neutral, balanced, or unclear sentiment
- **0.6 - 0.7**: Somewhat positive, mild support
- **0.7 - 0.9**: Clearly positive, opposes boycotts
- **0.9 - 1.0**: Extremely positive, strong brand advocacy

## 📈 Dashboard Features

- **Sentiment Timeline**: Confidence scores over time
- **Distribution Charts**: Overall sentiment breakdown
- **Volume Analysis**: Post frequency over time
- **Monthly Breakdown**: Sentiment trends by month
- **Length Analysis**: Sentiment vs post length correlation
- **Word Frequency**: Common words in positive/negative posts
- **Interactive Charts**: Hover for details, zoom, pan

## 🔧 Configuration

### Environment Variables (.env file)
```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.0
```

### Customization Options
- **Model**: Change `OPENAI_MODEL` to use different OpenAI models
- **Temperature**: Adjust `OPENAI_TEMPERATURE` (0.0 = deterministic, 1.0 = creative)
- **Analysis**: Modify prompts in `step_2_sentimnt_analysis.py`
- **Visualization**: Customize charts in `step_3_dashboard.py`

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **API Key Issues**
   - Ensure your OpenAI API key is valid and has credits
   - Check the `.env` file format

3. **Memory Issues**
   - Process data in smaller batches
   - Use a machine with more RAM

4. **Rate Limiting**
   - Add delays between API calls
   - Use OpenAI's rate limiting features

### Getting Help
- Check the console output for error messages
- Verify all dependencies are installed: `python setup_environment.py`
- Ensure your API key has sufficient credits

## 📝 Output Files

- `nestle_threads_sentiment_analysis_YYYY-MM-DD.json`: Raw analysis results
- `nestle_sentiment_dashboard.html`: Interactive dashboard
- Console output with detailed statistics

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your OpenAI API key secure
- The `.env` file is already in `.gitignore`

## 📚 Dependencies

- **LangChain**: AI/LLM framework
- **OpenAI**: API client for GPT models
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computing

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this project.

## 📄 License

This project is for educational and research purposes. Please respect OpenAI's terms of service and data privacy regulations.

