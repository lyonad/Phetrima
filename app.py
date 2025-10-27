from flask import Flask, render_template, jsonify
from flask_cors import CORS
import pandas as pd
import json
import os
import traceback

app = Flask(__name__)
CORS(app)

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'Data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
FIGURES_DIR = os.path.join(BASE_DIR, 'figures')

# Load data once at startup
def load_data():
    """Load all required data files"""
    data = {}
    
    try:
        print(f"BASE_DIR: {BASE_DIR}")
        print(f"DATA_DIR: {DATA_DIR}")
        print(f"REPORTS_DIR: {REPORTS_DIR}\n")
        
        # Load model performance by country
        perf_file = os.path.join(REPORTS_DIR, 'model_performance_by_country.csv')
        print(f"Loading: {perf_file}")
        data['performance'] = pd.read_csv(perf_file)
        print(f"[OK] Loaded performance data: {len(data['performance'])} rows")
        
        # Load summary data
        global_file = os.path.join(REPORTS_DIR, 'summary_global_fixed.csv')
        print(f"Loading: {global_file}")
        data['global_summary'] = pd.read_csv(global_file)
        print(f"[OK] Loaded global summary data")
        
        continent_file = os.path.join(REPORTS_DIR, 'summary_by_continent.csv')
        print(f"Loading: {continent_file}")
        data['continent_summary'] = pd.read_csv(continent_file)
        print(f"[OK] Loaded continent summary data")
        
        wins_file = os.path.join(REPORTS_DIR, 'summary_wins.csv')
        print(f"Loading: {wins_file}")
        data['wins_summary'] = pd.read_csv(wins_file)
        print(f"[OK] Loaded wins summary data")
        
        # Load GDP data
        gdp_file = os.path.join(DATA_DIR, 'gdp_2000_2025.csv')
        print(f"Loading: {gdp_file}")
        data['gdp_data'] = pd.read_csv(gdp_file)
        print(f"[OK] Loaded GDP data: {len(data['gdp_data'])} countries")
        
        # Load forecast outputs
        forecast_file = os.path.join(REPORTS_DIR, 'forecast_outputs.csv')
        print(f"Loading: {forecast_file}")
        data['forecast_data'] = pd.read_csv(forecast_file)
        print(f"[OK] Loaded forecast data: {len(data['forecast_data'])} rows")
        
        print("\n[SUCCESS] All data loaded successfully!\n")
        return data
        
    except Exception as e:
        print(f"\n[ERROR] Error loading data: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        raise

# Load data at startup
print("="*60)
print("Loading data...")
print("="*60)
app_data = load_data()
print("="*60)
print("Flask app ready!")
print("="*60 + "\n")

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering index: {e}")
        return f"Error: {e}", 500

@app.route('/api/global-metrics')
def global_metrics():
    """Get global performance metrics"""
    try:
        df = app_data['global_summary']
        metrics = {
            'arima': {
                'mae': float(df[df['Metric'] == 'arima_mae']['Value'].values[0]),
                'rmse': float(df[df['Metric'] == 'arima_rmse']['Value'].values[0]),
                'mape': float(df[df['Metric'] == 'arima_mape']['Value'].values[0])
            },
            'prophet': {
                'mae': float(df[df['Metric'] == 'prophet_mae']['Value'].values[0]),
                'rmse': float(df[df['Metric'] == 'prophet_rmse']['Value'].values[0]),
                'mape': float(df[df['Metric'] == 'prophet_mape']['Value'].values[0])
            }
        }
        return jsonify(metrics)
    except (KeyError, IndexError, ValueError) as e:
        print(f"Error in global_metrics: {e}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to load global metrics data'}), 500

@app.route('/api/wins')
def wins():
    """Get model wins summary"""
    try:
        df = app_data['wins_summary']
        wins_data = df.to_dict('records')
        return jsonify(wins_data)
    except Exception as e:
        print(f"Error in wins: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/continent-performance')
def continent_performance():
    """Get performance by continent"""
    try:
        df = app_data['continent_summary']
        continents_data = df.to_dict('records')
        return jsonify(continents_data)
    except Exception as e:
        print(f"Error in continent_performance: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/country-performance')
def country_performance():
    """Get performance by country"""
    try:
        df = app_data['performance']
        
        # Select relevant columns
        result = df[['country', 'continent', 'arima_mae', 'arima_rmse', 'arima_mape', 
                     'prophet_mae', 'prophet_rmse', 'prophet_mape']].copy()
        
        # Add winner column
        result['winner'] = result.apply(
            lambda row: 'Prophet' if row['prophet_mae'] < row['arima_mae'] else 'ARIMA', 
            axis=1
        )
        
        # Convert to billions for better readability
        for col in ['arima_mae', 'arima_rmse', 'prophet_mae', 'prophet_rmse']:
            result[col] = result[col] / 1e9
        
        return jsonify(result.to_dict('records'))
    except Exception as e:
        print(f"Error in country_performance: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-improvements')
def top_improvements():
    """Get countries with biggest improvements using Prophet"""
    try:
        df = app_data['performance'].copy()
        
        # Calculate improvement
        df['mae_improvement'] = ((df['arima_mae'] - df['prophet_mae']) / df['arima_mae'] * 100)
        df['rmse_improvement'] = ((df['arima_rmse'] - df['prophet_rmse']) / df['arima_rmse'] * 100)
        
        # Get top 10 improvements
        top_improvements = df.nlargest(10, 'mae_improvement')[
            ['country', 'continent', 'mae_improvement', 'rmse_improvement', 'arima_mae', 'prophet_mae']
        ].copy()
        
        # Convert MAE to billions
        top_improvements['arima_mae'] = top_improvements['arima_mae'] / 1e9
        top_improvements['prophet_mae'] = top_improvements['prophet_mae'] / 1e9
        
        return jsonify(top_improvements.to_dict('records'))
    except Exception as e:
        print(f"Error in top_improvements: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-countries')
def top_countries():
    """Get top 10 countries by recent GDP"""
    try:
        df = app_data['gdp_data'].copy()
        
        # Get column names
        country_col = 'Name of country' if 'Name of country' in df.columns else 'Country'
        continent_col = 'Continent'
        
        # Get year columns and find the most recent year with data
        year_columns = [col for col in df.columns if str(col).isdigit()]
        
        # Try to find the latest year with actual data
        latest_year = None
        for year in sorted(year_columns, key=int, reverse=True):
            if df[year].notna().sum() > 0:
                latest_year = year
                break
        
        if latest_year is None:
            # Fallback to last column if no year found
            latest_year = max(year_columns, key=int) if year_columns else '2024'
        
        # Filter out rows with NaN GDP and sort by latest GDP (descending)
        df_clean = df[[country_col, continent_col, latest_year]].copy()
        df_clean = df_clean.dropna(subset=[latest_year])
        df_clean = df_clean.sort_values(by=latest_year, ascending=False).head(10)
        
        # Prepare result
        result = []
        for idx, row in df_clean.iterrows():
            gdp_value = float(row[latest_year])
            if pd.notna(gdp_value) and gdp_value > 0:
                result.append({
                    'country': str(row[country_col]),
                    'continent': str(row[continent_col]),
                    'gdp': round(gdp_value / 1e12, 3),  # Convert to trillions, rounded
                    'year': str(latest_year)
                })
        
        return jsonify(result[:10])  # Return top 10
    except Exception as e:
        print(f"Error in top_countries: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/gdp-trends/<country>')
def gdp_trends(country):
    """Get GDP trends for a specific country"""
    try:
        df = app_data['gdp_data']
        
        # Get column names (handle different possible names)
        country_col = 'Name of country' if 'Name of country' in df.columns else 'Country'
        continent_col = 'Continent'
        
        # Find country row
        country_data = df[df[country_col] == country]
        
        if country_data.empty:
            return jsonify({'error': 'Country not found'}), 404
        
        # Extract year columns
        year_columns = sorted([col for col in df.columns if str(col).isdigit()], key=int)
        
        trends = []
        for year in year_columns:
            value = country_data[year].values[0]
            if pd.notna(value):
                trends.append({
                    'year': int(year),
                    'gdp': float(value) / 1e9  # Convert to billions
                })
        
        return jsonify({
            'country': country,
            'continent': country_data[continent_col].values[0],
            'trends': trends
        })
    except Exception as e:
        print(f"Error in gdp_trends: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/countries')
def countries():
    """Get list of all countries"""
    try:
        df = app_data['performance']
        countries_list = df[['country', 'continent']].sort_values('country').to_dict('records')
        return jsonify(countries_list)
    except Exception as e:
        print(f"Error in countries: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/continent-stats')
def continent_stats():
    """Get detailed statistics by continent"""
    try:
        df = app_data['performance']
        
        stats = []
        for continent in df['continent'].unique():
            continent_data = df[df['continent'] == continent]
            
            prophet_wins = len(continent_data[continent_data['prophet_mae'] < continent_data['arima_mae']])
            arima_wins = len(continent_data[continent_data['arima_mae'] < continent_data['prophet_mae']])
            
            stats.append({
                'continent': continent,
                'total_countries': len(continent_data),
                'prophet_wins': prophet_wins,
                'arima_wins': arima_wins,
                'avg_arima_mape': float(continent_data['arima_mape'].mean()),
                'avg_prophet_mape': float(continent_data['prophet_mape'].mean())
            })
        
        return jsonify(stats)
    except Exception as e:
        print(f"Error in continent_stats: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/forecast-detail/<country>')
def forecast_detail(country):
    """Get forecast detail for a specific country"""
    try:
        forecast_df = app_data['forecast_data']
        gdp_df = app_data['gdp_data']
        
        # Get forecast data for the country
        country_forecast = forecast_df[forecast_df['Country'] == country]
        
        if country_forecast.empty:
            return jsonify({'error': 'Country forecast data not found'}), 404
        
        # Get historical GDP data
        country_col = 'Name of country' if 'Name of country' in gdp_df.columns else 'Country'
        country_gdp = gdp_df[gdp_df[country_col] == country]
        
        if country_gdp.empty:
            return jsonify({'error': 'Country GDP data not found'}), 404
        
        # Extract year columns
        year_columns = sorted([col for col in gdp_df.columns if str(col).isdigit()], key=int)
        
        # Get historical data (training period: 2000-2021)
        historical = []
        for year in year_columns:
            if int(year) <= 2021:  # Training data
                value = country_gdp[year].values[0]
                if pd.notna(value):
                    historical.append({
                        'year': int(year),
                        'actual': float(value) / 1e9,  # Convert to billions
                        'forecast_arima': None,
                        'forecast_prophet': None
                    })
        
        # Get forecast data (2022-2025)
        for year in ['2022', '2023', '2024', '2025']:
            year_int = int(year)
            arima_data = country_forecast[
                (country_forecast['Model'] == 'ARIMA') & (country_forecast['Year'] == year_int)
            ]
            prophet_data = country_forecast[
                (country_forecast['Model'] == 'Prophet') & (country_forecast['Year'] == year_int)
            ]
            
            if not arima_data.empty:
                actual = float(arima_data['Actual'].values[0]) / 1e9
                forecast_arima = float(arima_data['Forecast'].values[0]) / 1e9
            else:
                actual = None
                forecast_arima = None
            
            if not prophet_data.empty:
                forecast_prophet = float(prophet_data['Forecast'].values[0]) / 1e9
            else:
                forecast_prophet = None
            
            historical.append({
                'year': year_int,
                'actual': actual if actual else None,
                'forecast_arima': forecast_arima,
                'forecast_prophet': forecast_prophet
            })
        
        # Calculate which model won per year
        winners = []
        arima_wins = 0
        prophet_wins = 0
        
        for year in ['2022', '2023', '2024', '2025']:
            year_int = int(year)
            arima_data = country_forecast[
                (country_forecast['Model'] == 'ARIMA') & (country_forecast['Year'] == year_int)
            ]
            prophet_data = country_forecast[
                (country_forecast['Model'] == 'Prophet') & (country_forecast['Year'] == year_int)
            ]
            
            if not arima_data.empty and not prophet_data.empty:
                # Calculate absolute error
                actual_val = float(arima_data['Actual'].values[0])
                arima_error = abs(actual_val - float(arima_data['Forecast'].values[0]))
                prophet_error = abs(actual_val - float(prophet_data['Forecast'].values[0]))
                
                winner = 'ARIMA' if arima_error < prophet_error else 'Prophet'
                winners.append({
                    'year': year_int,
                    'winner': winner,
                    'arima_error': arima_error / 1e9,  # Convert to billions
                    'prophet_error': prophet_error / 1e9
                })
                
                if winner == 'ARIMA':
                    arima_wins += 1
                else:
                    prophet_wins += 1
        
        return jsonify({
            'country': country,
            'continent': country_forecast['Continent'].values[0],
            'data': historical,
            'winners': winners,
            'arima_wins': arima_wins,
            'prophet_wins': prophet_wins,
            'total_forecast_years': len(winners)
        })
    except Exception as e:
        print(f"Error in forecast_detail: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Flask Development Server...")
    print("="*60)
    print("URL: http://localhost:5000")
    print("Mode: Debug")
    print("Press CTRL+C to stop")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
