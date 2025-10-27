"""
GDP Forecasting Research - ARIMA vs Prophet Model Training
This script trains ARIMA and Prophet models on GDP data and generates comprehensive reports.
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import os
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
import itertools
from tqdm import tqdm

warnings.filterwarnings('ignore')

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'Data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
FIGURES_DIR = os.path.join(BASE_DIR, 'figures')

# Create directories if they don't exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

def load_gdp_data():
    """Load and preprocess GDP data"""
    print("Loading GDP data...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'gdp_2000_2025.csv'))
    
    # Get year columns
    year_cols = [str(year) for year in range(2000, 2026)]
    year_cols_exist = [col for col in year_cols if col in df.columns]
    
    # Melt to long format
    id_vars = [col for col in df.columns if col not in year_cols_exist]
    df_long = pd.melt(df, id_vars=id_vars, value_vars=year_cols_exist,
                     var_name='year', value_name='gdp')
    
    df_long['year'] = df_long['year'].astype(int)
    df_long = df_long.sort_values(['Name of country', 'year']).reset_index(drop=True)
    
    print(f"Loaded {len(df_long)} records for {len(df['Name of country'].unique())} countries")
    return df_long

def calculate_metrics(actual, forecast):
    """Calculate MAE, RMSE, and MAPE"""
    # Filter out NaN values
    mask = ~(np.isnan(actual) | np.isnan(forecast))
    actual = actual[mask]
    forecast = forecast[mask]
    
    if len(actual) == 0:
        return np.nan, np.nan, np.nan
    
    mae = mean_absolute_error(actual, forecast)
    rmse = np.sqrt(mean_squared_error(actual, forecast))
    
    # MAPE (avoid division by zero)
    mask_actual = actual != 0
    if mask_actual.sum() > 0:
        mape = np.mean(np.abs((actual[mask_actual] - forecast[mask_actual]) / actual[mask_actual])) * 100
    else:
        mape = np.nan
    
    return mae, rmse, mape

def train_arima_model(training_data):
    """Train ARIMA model with grid search"""
    try:
        # Grid search for ARIMA order (p,d,q) - limited search space for efficiency
        best_aic = np.inf
        best_order = None
        best_model = None
        
        # Limited order space to reduce computation time
        orders = [(p, d, q) for p, d, q in itertools.product(range(0, 3), range(0, 2), range(0, 3))
                  if not (p == 0 and d == 0 and q == 0)]
        
        for order in orders:
            try:
                model = SARIMAX(training_data, order=order, enforce_stationarity=False, 
                               enforce_invertibility=False)
                fitted_model = model.fit(disp=False, maxiter=50, method='lbfgs')
                
                if fitted_model.aic < best_aic and not np.isnan(fitted_model.aic):
                    best_aic = fitted_model.aic
                    best_order = order
                    best_model = fitted_model
            except:
                continue
        
        return best_model, best_order
        
    except Exception as e:
        return None, None

def train_prophet_model(training_data, validation_data):
    """Train Prophet model"""
    try:
        # Prepare Prophet format
        df_prophet = pd.DataFrame({
            'ds': pd.date_range(start='2000-01-01', periods=len(training_data), freq='YS'),
            'y': training_data.values
        })
        
        # Initialize Prophet with multiplicative seasonality for yearly data
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
        
        model.fit(df_prophet)
        
        # Generate forecast
        future = model.make_future_dataframe(periods=len(validation_data), freq='YS')
        forecast = model.predict(future)
        
        return model, forecast
        
    except Exception as e:
        return None, None

def process_country(country_name, country_data, continent):
    """Process a single country and generate forecasts"""
    # Prepare time series
    training_data = country_data[country_data['year'] < 2022].sort_values('year')
    test_data = country_data[country_data['year'] >= 2022].sort_values('year')
    
    # Filter out missing values in training
    training_data = training_data[training_data['gdp'].notna()].copy()
    test_data = test_data[test_data['gdp'].notna()].copy()
    
    if len(training_data) < 15:  # Minimum 15 observations
        return None
    
    if len(test_data) == 0:
        return None
    
    # ARIMA Training and Forecasting
    arima_forecast = []
    
    try:
        arima_model, arima_order = train_arima_model(training_data['gdp'].values)
        if arima_model is not None:
            # Forecast for test period
            arima_forecast = arima_model.forecast(steps=len(test_data)).tolist()
        else:
            # If model fails, use naive forecast (last value)
            last_value = float(training_data['gdp'].iloc[-1])
            arima_forecast = [last_value] * len(test_data)
    except:
        last_value = float(training_data['gdp'].iloc[-1])
        arima_forecast = [last_value] * len(test_data)
    
    # Prophet Training and Forecasting
    prophet_forecast = []
    
    try:
        # Prepare Prophet format
        df_prophet = pd.DataFrame({
            'ds': pd.to_datetime([f'{int(row["year"])}-01-01' for _, row in training_data.iterrows()]),
            'y': training_data['gdp'].values
        })
        
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
        
        model.fit(df_prophet)
        
        # Make future dataframe
        future_periods = len(test_data)
        future_dates = pd.date_range(
            start=df_prophet['ds'].max(),
            periods=future_periods + 1,
            freq='YS'
        )[1:]
        
        future_df = pd.DataFrame({'ds': future_dates})
        forecast = model.predict(future_df)
        prophet_forecast = forecast['yhat'].tolist()
        
    except Exception as e:
        # Fallback to last value
        last_value = float(training_data['gdp'].iloc[-1])
        prophet_forecast = [last_value] * len(test_data)
    
    # Ensure forecasts are the right length
    if len(arima_forecast) < len(test_data):
        arima_forecast.extend([arima_forecast[-1]] * (len(test_data) - len(arima_forecast)))
    if len(prophet_forecast) < len(test_data):
        prophet_forecast.extend([prophet_forecast[-1]] * (len(test_data) - len(prophet_forecast)))
    
    arima_forecast = arima_forecast[:len(test_data)]
    prophet_forecast = prophet_forecast[:len(test_data)]
    
    # Calculate metrics
    actual = test_data['gdp'].values
    
    arima_mae, arima_rmse, arima_mape = calculate_metrics(actual, np.array(arima_forecast))
    prophet_mae, prophet_rmse, prophet_mape = calculate_metrics(actual, np.array(prophet_forecast))
    
    # Prepare results
    result = {
        'country': country_name,
        'continent': continent,
        'n_observations': len(country_data),
        'n_train': len(training_data),
        'n_test': len(test_data),
        'arima_mae': arima_mae if not np.isnan(arima_mae) else 0.0,
        'arima_rmse': arima_rmse if not np.isnan(arima_rmse) else 0.0,
        'arima_mape': arima_mape if not np.isnan(arima_mape) else 0.0,
        'prophet_mae': prophet_mae if not np.isnan(prophet_mae) else 0.0,
        'prophet_rmse': prophet_rmse if not np.isnan(prophet_rmse) else 0.0,
        'prophet_mape': prophet_mape if not np.isnan(prophet_mape) else 0.0
    }
    
    # Prepare forecast outputs
    forecast_outputs = []
    for idx, row in test_data.iterrows():
        year = int(row['year'])
        actual_value = float(row['gdp'])
        
        # Get forecast for this year (2022 is index 0, 2023 is index 1, etc.)
        year_idx = year - 2022
        
        arima_fc = float(arima_forecast[year_idx]) if year_idx < len(arima_forecast) else actual_value
        prophet_fc = float(prophet_forecast[year_idx]) if year_idx < len(prophet_forecast) else actual_value
        
        forecast_outputs.append({
            'Country': country_name,
            'Continent': continent,
            'Model': 'ARIMA',
            'Year': year,
            'Actual': actual_value,
            'Forecast': arima_fc
        })
        
        forecast_outputs.append({
            'Country': country_name,
            'Continent': continent,
            'Model': 'Prophet',
            'Year': year,
            'Actual': actual_value,
            'Forecast': prophet_fc
        })
    
    return result, forecast_outputs

def generate_summaries(results, forecast_outputs):
    """Generate summary statistics"""
    
    # Global Summary - calculate weighted average
    valid_results = [r for r in results if r is not None and 'arima_mae' in r]
    
    global_metrics = {
        'Metric': ['arima_mae', 'arima_rmse', 'arima_mape', 'prophet_mae', 'prophet_rmse', 'prophet_mape'],
        'Value': [
            np.mean([r['arima_mae'] for r in valid_results]),
            np.mean([r['arima_rmse'] for r in valid_results]),
            np.mean([r['arima_mape'] for r in valid_results]),
            np.mean([r['prophet_mae'] for r in valid_results]),
            np.mean([r['prophet_rmse'] for r in valid_results]),
            np.mean([r['prophet_mape'] for r in valid_results])
        ]
    }
    global_df = pd.DataFrame(global_metrics)
    
    # Continent Summary
    continent_summary = []
    continents = pd.unique([r['continent'] for r in valid_results])
    for continent in continents:
        continent_results = [r for r in valid_results if r['continent'] == continent]
        if len(continent_results) > 0:
            continent_summary.append({
                'continent': continent,
                'arima_mae': np.mean([r['arima_mae'] for r in continent_results]),
                'arima_rmse': np.mean([r['arima_rmse'] for r in continent_results]),
                'arima_mape': np.mean([r['arima_mape'] for r in continent_results]),
                'prophet_mae': np.mean([r['prophet_mae'] for r in continent_results]),
                'prophet_rmse': np.mean([r['prophet_rmse'] for r in continent_results]),
                'prophet_mape': np.mean([r['prophet_mape'] for r in continent_results])
            })
    continent_df = pd.DataFrame(continent_summary)
    
    # Wins Summary
    arima_wins = sum(1 for r in valid_results if r['arima_mae'] < r['prophet_mae'])
    prophet_wins = sum(1 for r in valid_results if r['prophet_mae'] < r['arima_mae'])
    wins_df = pd.DataFrame({
        'better_model': ['ARIMA', 'Prophet'],
        'Count': [arima_wins, prophet_wins]
    })
    
    return global_df, continent_df, wins_df

def generate_figures(df_long, results):
    """Generate forecast comparison figures for top 5 countries"""
    # Get top 5 countries by GDP
    latest_year = '2021'
    top_5 = df_long[df_long['year'] == 2021].nlargest(5, 'gdp')['Name of country'].tolist()
    
    print(f"\nGenerating figures for: {', '.join(top_5)}")
    
    for country in top_5:
        try:
            country_data = df_long[df_long['Name of country'] == country].copy()
            
            # Prepare forecast data
            forecast_df = pd.read_csv(os.path.join(REPORTS_DIR, 'forecast_outputs.csv'))
            country_forecast = forecast_df[forecast_df['Country'] == country]
            
            if country_forecast.empty:
                print(f"  ⚠ Skipping {country} - no forecast data")
                continue
            
            # Plot
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Historical data
            historical = country_data[country_data['year'] <= 2021]
            ax.plot(historical['year'], historical['gdp'] / 1e9, 'o-', label='Actual', color='black', linewidth=2)
            
            # ARIMA forecast
            arima_data = country_forecast[country_forecast['Model'] == 'ARIMA']
            if not arima_data.empty:
                ax.plot(arima_data['Year'], arima_data['Forecast'] / 1e9, 's--', 
                       label='ARIMA Forecast', color='blue', linewidth=2, markersize=8)
                ax.plot(arima_data['Year'], arima_data['Actual'] / 1e9, 's-', 
                       color='black', markersize=8)
            
            # Prophet forecast
            prophet_data = country_forecast[country_forecast['Model'] == 'Prophet']
            if not prophet_data.empty:
                ax.plot(prophet_data['Year'], prophet_data['Forecast'] / 1e9, '^--', 
                       label='Prophet Forecast', color='red', linewidth=2, markersize=8)
            
            ax.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax.set_ylabel('GDP (Billion USD)', fontsize=12, fontweight='bold')
            ax.set_title(f'GDP Forecast Comparison: {country}', fontsize=14, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            filename = os.path.join(FIGURES_DIR, f'forecast_comparison_{country.replace(" ", "_")}.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  [OK] Saved: {filename}")
        except Exception as e:
            print(f"  ⚠ Error generating figure for {country}: {e}")

def main():
    print("="*70)
    print("GDP FORECASTING RESEARCH - ARIMA vs PROPHET")
    print("="*70)
    
    # Load data
    df_long = load_gdp_data()
    
    # Process each country
    results = []
    forecast_outputs_list = []
    
    countries = df_long['Name of country'].unique()
    print(f"\nProcessing {len(countries)} countries...")
    
    for country in tqdm(countries, desc="Training models"):
        country_data = df_long[df_long['Name of country'] == country]
        continent = country_data['Continent'].iloc[0]
        
        result = process_country(country, country_data, continent)
        if result is not None:
            metrics, forecasts = result
            results.append(metrics)
            if forecasts:
                forecast_outputs_list.extend(forecasts)
    
    print(f"\nProcessed {len(results)} countries successfully")
    
    # Generate summaries
    print("\nGenerating summary reports...")
    global_df, continent_df, wins_df = generate_summaries(results, forecast_outputs_list)
    
    # Save results
    print("\nSaving reports...")
    
    # Model performance by country
    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(REPORTS_DIR, 'model_performance_by_country.csv'), index=False)
    print("  [OK] Saved: model_performance_by_country.csv")
    
    # Global summary
    global_df.to_csv(os.path.join(REPORTS_DIR, 'summary_global_fixed.csv'), index=False)
    print("  [OK] Saved: summary_global_fixed.csv")
    
    # Continent summary
    continent_df.to_csv(os.path.join(REPORTS_DIR, 'summary_by_continent.csv'), index=False)
    print("  [OK] Saved: summary_by_continent.csv")
    
    # Wins summary
    wins_df.to_csv(os.path.join(REPORTS_DIR, 'summary_wins.csv'), index=False)
    print("  [OK] Saved: summary_wins.csv")
    
    # Forecast outputs
    forecast_df = pd.DataFrame(forecast_outputs_list)
    forecast_df.to_csv(os.path.join(REPORTS_DIR, 'forecast_outputs.csv'), index=False)
    print("  [OK] Saved: forecast_outputs.csv")
    
    # Generate figures
    generate_figures(df_long, results)
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
    print(f"[OK] Total countries processed: {len(results)}")
    print(f"[OK] Reports saved in: {REPORTS_DIR}")
    print(f"[OK] Figures saved in: {FIGURES_DIR}")
    print("="*70)

if __name__ == "__main__":
    main()

