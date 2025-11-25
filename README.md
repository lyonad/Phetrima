# Phetrima - GDP Forecasting with Prophet & ARIMA

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Flask](https://img.shields.io/badge/flask-3.1.2-green)
![License](https://img.shields.io/badge/license-MIT-green)

**Professional interactive research platform comparing ARIMA vs Prophet models on World Bank GDP data 2000-2025**

[Quick Start](#-quick-start) • [Features](#-features) • [API](#-api-endpoints) • [Deployment](#-deployment)

</div>

---

## Overview

Phetrima (Prophet + ARIMA) is a comprehensive forecasting research platform that evaluates two powerful time series models: **Prophet** and **ARIMA** for predicting GDP across **117 countries** over **25 years** (2000-2025).

### Key Results

| Metric | Prophet | ARIMA | Winner |
|--------|---------|-------|--------|
| **MAE** | 76.0B USD | 101.4B USD | Prophet |
| **RMSE** | 80.6B USD | 106.8B USD | Prophet |
| **MAPE** | 11.4% | 13.6% | Prophet |
| **Countries Won** | 72 (61.5%) | 45 (38.5%) | Prophet |

---

## Quick Start

### Cara Termudah (Windows)

```bash
start_server.bat
```

### Cara Termudah (Linux/Mac)

```bash
chmod +x start_server.sh && ./start_server.sh
```

### Manual Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python app.py
```

Kemudian buka browser: **http://localhost:5000**

---

## Fitur Utama

### Overview Dashboard
- Metrik global ARIMA vs Prophet (MAE, RMSE, MAPE)
- Distribusi kemenangan model (chart donut)
- Top 10 peningkatan terbesar menggunakan Prophet
- Top 10 ekonomi dunia berdasarkan GDP
- Visualisasi bar chart perbandingan metrik global

### Analisis Per Negara
- Tabel interaktif dengan 118 negara
- Filter by benua & model pemenang
- Real-time search berdasarkan nama negara
- Sortable columns untuk semua metrik
- Export ke CSV functionality
- Indikator visual model terbaik per negara

### Analisis Per Benua
- Chart perbandingan RMSE per benua
- Statistics cards per benua (wins, MAPE average)
- Detailed metrics table dengan semua metrik
- Identifikasi regional pattern

### Forecast Detail
- Time series GDP visualization
- Historical vs Forecast comparison
- Perbandingan ARIMA vs Prophet per tahun
- Winner per tahun forecast (2022-2025)
- Summary card menampilkan model terbaik overall

### Insights & Rekomendasi
- Temuan utama penelitian
- Kapan Prophet/ARIMA unggul
- 4 rekomendasi strategis
- Metodologi & keterbatasan penelitian

---

## Struktur Proyek

```
World-GDP-Project/
│
├── Application Files
│   ├── app.py              # Flask backend dengan 9 API endpoints
│   ├── config.py           # Configuration settings
│   ├── run.py              # Enhanced runner script
│   │
│   ├── templates/
│   │   └── index.html      # Main HTML dengan 5 section
│   │
│   └── static/
│       ├── css/style.css   # Modern styling & responsive design
│       └── js/app.js       # Frontend logic & Chart.js integration
│
├── Data & Reports
│   ├── Data/
│   │   └── gdp_2000_2025.csv              # Dataset utama dari World Bank
│   │
│   ├── reports/
│   │   ├── model_performance_by_country.csv
│   │   ├── summary_global_fixed.csv
│   │   ├── summary_by_continent.csv
│   │   ├── summary_wins.csv
│   │   └── forecast_outputs.csv
│   │
│   └── figures/
│       ├── forecast_comparison_*.png      # Forecast visualizations
│
├── Deployment
│   ├── Dockerfile          # Docker configuration
│   ├── docker-compose.yml  # Docker Compose setup
│   ├── Procfile            # Heroku deployment
│   ├── runtime.txt         # Python version
│   ├── start_server.bat    # Windows launcher
│   └── start_server.sh     # Linux/Mac launcher
│
└── 📖 Documentation
    ├── README.md           # This file (comprehensive guide)
    └── requirements.txt    # Python dependencies
```

---

## 🔧 Teknologi

### Backend
- **Python 3.11** - Core language
- **Flask 3.1.2** - Web framework
- **Pandas 2.3.3** - Data processing & manipulation
- **Flask-CORS 6.0.1** - API support

### Data Analysis & ML
- **Statsmodels 0.14.5** - ARIMA implementation
- **Prophet 1.2.1** - Time series forecasting
- **pmdarima 2.0.4** - Auto ARIMA
- **scikit-learn 1.7.2** - Machine learning utilities

### Frontend
- **HTML5/CSS3** - Structure & modern styling
- **JavaScript ES6+** - Interactivity & filters
- **Chart.js 4.4.0** - Data visualizations
- **Responsive Design** - Mobile-friendly

### Deployment
- **Docker** - Containerization
- **Gunicorn 23.0.0** - Production WSGI server
- **Cloud Ready** - Heroku, Railway, Render, GCP, AWS

---

## API Endpoints

### Global Metrics
```bash
GET /api/global-metrics
# Returns: { arima: { mae, rmse, mape }, prophet: { mae, rmse, mape } }
```

### Model Wins Distribution
```bash
GET /api/wins
# Returns: Array of win statistics
```

### Performance by Continent
```bash
GET /api/continent-performance
# Returns: Performance metrics grouped by continent
```

### Performance by Country
```bash
GET /api/country-performance
# Returns: Array of country-level metrics with winner determination
```

### Top Improvements
```bash
GET /api/top-improvements
# Returns: Top 10 countries with biggest improvement using Prophet
```

### Top Countries by GDP
```bash
GET /api/top-countries
# Returns: Top 10 countries by recent GDP
```

### Continent Statistics
```bash
GET /api/continent-stats
# Returns: Detailed statistics by continent
```

### List All Countries
```bash
GET /api/countries
# Returns: List of all countries with continent info
```

### GDP Trends for Country
```bash
GET /api/gdp-trends/<country>
# Returns: Historical GDP data for specific country
```

### Forecast Detail
```bash
GET /api/forecast-detail/<country>
# Returns: Forecast comparison, winners per year, trend data
```

---

## Metodologi Penelitian

### Dataset
- **Source**: World Bank Open Data
- **Period**: 2000-2025 (25 years)
- **Countries**: 118 (after filtering min 15 observations)
- **Variables**: GDP (USD), Country, Continent

### Data Split
- **Training**: 2000-2021 (22 years)
- **Testing**: 2022-2025 (4 years)

### Model ARIMA
- Grid search SARIMAX
- Order (p,d,q) = 0-2
- AIC-based selection
- Auto ARIMA with pmdarima

### Model Prophet
- Multiplicative seasonality
- Yearly frequency
- Automatic changepoints
- Robust to outliers

### Metrics
- **MAE**: Mean Absolute Error (billion USD)
- **RMSE**: Root Mean Square Error (billion USD)
- **MAPE**: Mean Absolute Percentage Error (%)

---

## Key Insights

### Prophet Unggul Pada:
- Ekonomi dengan pertumbuhan nonlinear (China, India, Indonesia)
- Tren pasca-pandemi yang tajam
- Asia region (54% improvement)
- Negara berkembang dengan changepoints signifikan

### ARIMA Lebih Baik Pada:
- Ekonomi stabil dan mature (USA, Japan, France)
- Volatilitas tinggi dengan pola konsisten
- Dataset kecil dengan noise rendah
- Ekonomi dengan fluktuasi cyclical

### Per Benua:
- **Asia**: Prophet dominan (MAE: 92.1B vs ARIMA: 192.1B)
- **Africa**: Prophet lebih baik (MAE: 20.3B vs ARIMA: 26.3B)
- **Europe**: Prophet menang tipis (MAE: 39.6B vs ARIMA: 54.1B)
- **North America**: Kompetitif, tergantung skala ekonomi

---

## Docker Deployment

### Build & Run

```bash
# Build Docker image
docker build -t gdp-dashboard .

# Run container
docker run -p 5000:5000 gdp-dashboard
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ☁️ Cloud Deployment

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create gdp-forecasting

# Deploy
git push heroku main

# Open app
heroku open
```

### Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Render.com

1. Connect GitHub repository
2. Create new Web Service
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Deploy automatically

---

## Use Cases

### 🎓 Academic Research
- Penelitian ekonomi dan forecasting
- Analisis time series komparatif
- Model comparison studies
- Economic policy research

### 🏛️ Policy Making
- Perencanaan ekonomi nasional
- GDP forecasting untuk budgeting
- Regional economic analysis
- International comparison

### 💼 Business Analysis
- Market research dan forecasting
- Investment decision support
- Economic trend analysis
- International business expansion

### 📖 Education
- Teaching time series forecasting
- Model demonstration & comparison
- Real-world data analysis
- Data science education

---

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd World-GDP-Project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

### Code Quality

```bash
# Install linting tools
pip install flake8 black pylint

# Check code style
flake8 app.py --max-line-length=120

# Format code
black app.py

# Security check
pip install bandit
bandit -r .
```

---

## Performance

- **Initial Load**: < 2 seconds
- **API Response**: < 100ms per endpoint
- **Chart Rendering**: < 500ms
- **Real-time Filters**: < 50ms response time
- **Data Size**: ~3MB total

---

## 🐛 Troubleshooting

### Port Already in Use

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:5000 | xargs kill -9
```

### Module Not Found

```bash
pip install -r requirements.txt --force-reinstall --no-cache-dir
```

### Permission Denied (Linux/Mac)

```bash
chmod +x start_server.sh
```

### Docker Issues

```bash
# Rebuild image
docker build --no-cache -t gdp-dashboard .

# Remove old containers
docker-compose down -v
```

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Contribution Guidelines
- Follow PEP 8 style guide
- Write clear commit messages
- Add comments for complex logic
- Test thoroughly before submitting

---

## 🔐 Configuration

### Environment Variables

Create `.env` file for production:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DEBUG=False
```

### Flask Configuration

The `config.py` file provides three environments:

- **DevelopmentConfig**: Debug mode enabled
- **ProductionConfig**: Optimized for production
- **TestingConfig**: For unit testing

---

## 📝 Dependencies

Main dependencies from `requirements.txt`:

```txt
Flask==3.1.2          # Web framework
pandas==2.3.3          # Data processing
prophet==1.2.1         # Facebook Prophet
statsmodels==0.14.5   # ARIMA models
pmdarima==2.0.4       # Auto ARIMA
gunicorn==23.0.0      # Production server
flask-cors==6.0.1     # CORS support
```

Full list: 43 packages in `requirements.txt`

---

## 🌟 Features Roadmap

### v1.1 (Next Release)
- [ ] Authentication system
- [ ] Redis caching for performance
- [ ] PDF export functionality
- [ ] Multi-country comparison chart
- [ ] Custom date range selection

### v1.2 (Future)
- [ ] ML predictions (XGBoost, LSTM)
- [ ] Dark mode toggle
- [ ] Multi-language support (EN, ID)
- [ ] Email report generation
- [ ] Advanced analytics dashboard

---

## 📞 Support & Resources

### Data Sources
- [World Bank Open Data](https://data.worldbank.org/)
- [Kaggle Dataset](https://www.kaggle.com/datasets/naveenapaleti/world-bank-gdp-by-country-and-continent20002025)

### Documentation
- [Prophet Documentation](https://facebook.github.io/prophet/)
- [Statsmodels ARIMA](https://www.statsmodels.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Chart.js Guide](https://www.chartjs.org/)

---

## Statistics

- **118 Countries** analyzed
- **25 Years** of data (2000-2025)
- **2 Models** compared (ARIMA vs Prophet)
- **3 Metrics** evaluated (MAE, RMSE, MAPE)
- **10 API Endpoints** available
- **100% Responsive** design
- **Production Ready**

---

## 📄 License

© 2025 GDP Forecasting Research Project. All rights reserved.

---

## 🙏 Acknowledgments

- **World Bank** - GDP Open Data
- **Facebook Research** - Prophet library
- **Statsmodels Team** - ARIMA implementation
- **Flask Community** - Web framework
- **Chart.js** - Visualization library

---

<div align="center">

### Ready to Explore?

```bash
python app.py
```

Open **http://localhost:5000** in your browser!

---

**Made with ❤️ for Data Science & Economics Research**

⭐ Star this project if you find it useful!

</div>

---

*Last Updated: January 2025 | Version 1.0.0 | Status: Production Ready*
