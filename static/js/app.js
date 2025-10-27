// Global state
let appData = {
    globalMetrics: null,
    wins: null,
    continentPerformance: null,
    countryPerformance: null,
    topImprovements: null,
    topCountries: null,
    continentStats: null,
    countries: null
};

let charts = {};
let currentSort = { column: null, direction: 'asc' };

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    setupNavigation();
    setupCTANavigation();
    await loadAllData();
    renderOverviewSection();
    renderCountriesSection();
    renderContinentsSection();
    renderForecastSection();
}

// Setup CTA button navigation
function setupCTANavigation() {
    // Helper function to navigate to a section
    window.navigateToSection = function(sectionName) {
        const navTabs = document.querySelectorAll('.nav-tab');
        const sections = document.querySelectorAll('.section');
        
        // Find the target tab
        const targetTab = Array.from(navTabs).find(tab => tab.dataset.section === sectionName);
        
        if (targetTab) {
            // Update active tab
            navTabs.forEach(t => t.classList.remove('active'));
            targetTab.classList.add('active');
            
            // Update active section
            sections.forEach(s => s.classList.remove('active'));
            const targetSection = document.getElementById(`${sectionName}-section`);
            if (targetSection) {
                targetSection.classList.add('active');
            }
            
            // Save to localStorage
            localStorage.setItem('lastSection', sectionName);
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };
}

// Setup navigation
function setupNavigation() {
    const navTabs = document.querySelectorAll('.nav-tab');
    const sections = document.querySelectorAll('.section');

    // Restore last visited section
    const lastSection = localStorage.getItem('lastSection') || 'hero';
    
    navTabs.forEach(t => t.classList.remove('active'));
    sections.forEach(s => s.classList.remove('active'));
    
    const savedTab = Array.from(navTabs).find(tab => tab.dataset.section === lastSection);
    if (savedTab) {
        savedTab.classList.add('active');
        const savedSection = document.getElementById(`${lastSection}-section`);
        if (savedSection) {
            savedSection.classList.add('active');
        }
    }

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetSection = tab.dataset.section;

            // Update active tab
            navTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update active section
            sections.forEach(s => s.classList.remove('active'));
            document.getElementById(`${targetSection}-section`).classList.add('active');

            // Save to localStorage
            localStorage.setItem('lastSection', targetSection);

            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    // Hide/show navbar on scroll
    setupScrollHideNavbar();
}

// Hide navbar when scrolling down, show when scrolling up
function setupScrollHideNavbar() {
    let lastScroll = 0;
    const header = document.querySelector('.header');

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll <= 0) {
            // At the top
            header.classList.remove('hidden');
        } else if (currentScroll > lastScroll && currentScroll > 100) {
            // Scrolling down
            header.classList.add('hidden');
        } else {
            // Scrolling up
            header.classList.remove('hidden');
        }

        lastScroll = currentScroll;
    });
}

// Load all data from API
// Helper function to fetch with error handling
async function fetchWithErrorHandling(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${url}`);
    }
    return response.json();
}

async function loadAllData() {
    try {
        const [
            globalMetrics,
            wins,
            continentPerformance,
            countryPerformance,
            topImprovements,
            topCountries,
            continentStats,
            countries
        ] = await Promise.all([
            fetchWithErrorHandling('/api/global-metrics'),
            fetchWithErrorHandling('/api/wins'),
            fetchWithErrorHandling('/api/continent-performance'),
            fetchWithErrorHandling('/api/country-performance'),
            fetchWithErrorHandling('/api/top-improvements'),
            fetchWithErrorHandling('/api/top-countries'),
            fetchWithErrorHandling('/api/continent-stats'),
            fetchWithErrorHandling('/api/countries')
        ]);

        appData = {
            globalMetrics,
            wins,
            continentPerformance,
            countryPerformance,
            topImprovements,
            topCountries,
            continentStats,
            countries
        };
    } catch (error) {
        console.error('Error loading data:', error);
        // Show user-friendly error message
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'background: #f44336; color: white; padding: 1rem; margin: 1rem; border-radius: 0.5rem; text-align: center;';
        errorDiv.innerHTML = '<strong>⚠️ Error Loading Data:</strong> Please refresh the page or check your connection.';
        document.querySelector('.container').prepend(errorDiv);
    }
}

// Render Overview Section
function renderOverviewSection() {
    renderGlobalMetrics();
    renderWinsChart();
    renderGlobalMetricsChart();
    renderImprovementsChart();
    renderTopCountriesTable();
}

function renderGlobalMetrics() {
    const { arima, prophet } = appData.globalMetrics;

    // Prophet metrics
    document.getElementById('prophet-mae').textContent = formatNumber(prophet.mae / 1e9, 1);
    document.getElementById('prophet-rmse').textContent = formatNumber(prophet.rmse / 1e9, 1) + 'B';
    document.getElementById('prophet-mape').textContent = formatNumber(prophet.mape, 2);

    // ARIMA metrics
    document.getElementById('arima-mae').textContent = formatNumber(arima.mae / 1e9, 1);
    document.getElementById('arima-rmse').textContent = formatNumber(arima.rmse / 1e9, 1) + 'B';
    document.getElementById('arima-mape').textContent = formatNumber(arima.mape, 2);
}

function renderWinsChart() {
    const ctx = document.getElementById('winsChart');
    const prophetWins = appData.wins.find(w => w.better_model === 'Prophet').Count;
    const arimaWins = appData.wins.find(w => w.better_model === 'ARIMA').Count;

    document.getElementById('prophet-wins').textContent = prophetWins;
    document.getElementById('arima-wins').textContent = arimaWins;

    if (charts.winsChart) charts.winsChart.destroy();

    charts.winsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Prophet', 'ARIMA'],
            datasets: [{
                data: [prophetWins, arimaWins],
                backgroundColor: ['#2b4257', '#88a9c3'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = prophetWins + arimaWins;
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} countries (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function renderGlobalMetricsChart() {
    const ctx = document.getElementById('globalMetricsChart');
    const { arima, prophet } = appData.globalMetrics;

    if (charts.globalMetricsChart) charts.globalMetricsChart.destroy();

    charts.globalMetricsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['MAE (Miliar USD)', 'RMSE (Miliar USD)', 'MAPE (%)'],
            datasets: [
                {
                    label: 'Prophet',
                    data: [prophet.mae / 1e9, prophet.rmse / 1e9, prophet.mape],
                    backgroundColor: '#2b4257',
                    borderRadius: 8
                },
                {
                    label: 'ARIMA',
                    data: [arima.mae / 1e9, arima.rmse / 1e9, arima.mape],
                    backgroundColor: '#88a9c3',
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y.toFixed(2);
                            return `${label}: ${value}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => formatNumber(value, 1)
                    }
                }
            }
        }
    });
}

function renderImprovementsChart() {
    const ctx = document.getElementById('improvementsChart');
    const data = appData.topImprovements;

    if (charts.improvementsChart) charts.improvementsChart.destroy();

    charts.improvementsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.country),
            datasets: [{
                label: 'Improvement (%)',
                data: data.map(d => d.mae_improvement),
                backgroundColor: '#667eea',
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const improvement = context.parsed.x.toFixed(1);
                            return `Improvement: ${improvement}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => value + '%'
                    }
                }
            }
        }
    });
}

function renderTopCountriesTable() {
    const tbody = document.querySelector('#topCountriesTable tbody');
    tbody.innerHTML = '';

    appData.topCountries.forEach((country, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${country.country}</strong></td>
            <td>${country.continent}</td>
            <td>$${formatNumber(country.gdp, 2)}T</td>
        `;
        tbody.appendChild(row);
    });
}

// Render Countries Section
function renderCountriesSection() {
    populateContinentFilter();
    renderCountriesTable(appData.countryPerformance);
    setupTableFilters();
    setupTableSort();
    setupExport();
}

function populateContinentFilter() {
    const select = document.getElementById('continentFilter');
    const continents = [...new Set(appData.countryPerformance.map(c => c.continent))].sort();

    continents.forEach(continent => {
        const option = document.createElement('option');
        option.value = continent;
        option.textContent = continent;
        select.appendChild(option);
    });
}

function renderCountriesTable(data) {
    const tbody = document.querySelector('#countriesTable tbody');
    tbody.innerHTML = '';

    data.forEach((country, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${country.country}</strong></td>
            <td>${country.continent}</td>
            <td>${formatNumber(country.arima_mae, 2)}</td>
            <td>${formatNumber(country.arima_mape, 2)}%</td>
            <td>${formatNumber(country.prophet_mae, 2)}</td>
            <td>${formatNumber(country.prophet_mape, 2)}%</td>
            <td><span class="badge badge-${country.winner.toLowerCase()}">${country.winner}</span></td>
        `;
        tbody.appendChild(row);
    });

    updateTableInfo(data.length, appData.countryPerformance.length);
}

function setupTableFilters() {
    const continentFilter = document.getElementById('continentFilter');
    const winnerFilter = document.getElementById('winnerFilter');
    const searchInput = document.getElementById('searchCountry');

    const applyFilters = () => {
        let filtered = [...appData.countryPerformance];

        // Continent filter
        if (continentFilter.value) {
            filtered = filtered.filter(c => c.continent === continentFilter.value);
        }

        // Winner filter
        if (winnerFilter.value) {
            filtered = filtered.filter(c => c.winner === winnerFilter.value);
        }

        // Search filter
        if (searchInput.value) {
            const search = searchInput.value.toLowerCase();
            filtered = filtered.filter(c => c.country.toLowerCase().includes(search));
        }

        renderCountriesTable(filtered);
    };

    continentFilter.addEventListener('change', applyFilters);
    winnerFilter.addEventListener('change', applyFilters);
    searchInput.addEventListener('input', applyFilters);
}

function setupTableSort() {
    const headers = document.querySelectorAll('#countriesTable th[data-sort]');

    headers.forEach(header => {
        header.addEventListener('click', () => {
            const column = header.dataset.sort;
            
            // Toggle sort direction
            if (currentSort.column === column) {
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.column = column;
                currentSort.direction = 'asc';
            }

            // Update header classes
            headers.forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            header.classList.add(`sort-${currentSort.direction}`);

            // Sort data
            const sorted = [...appData.countryPerformance].sort((a, b) => {
                let aVal = a[column];
                let bVal = b[column];

                if (typeof aVal === 'string') {
                    aVal = aVal.toLowerCase();
                    bVal = bVal.toLowerCase();
                }

                if (currentSort.direction === 'asc') {
                    return aVal > bVal ? 1 : -1;
                } else {
                    return aVal < bVal ? 1 : -1;
                }
            });

            renderCountriesTable(sorted);
        });
    });
}

function setupExport() {
    const exportBtn = document.getElementById('exportBtn');
    exportBtn.addEventListener('click', () => {
        const data = appData.countryPerformance;
        const csv = convertToCSV(data);
        downloadCSV(csv, 'country_performance.csv');
    });
}

// Render Continents Section
function renderContinentsSection() {
    renderContinentChart();
    renderContinentStatsCards();
    renderContinentTable();
}

function renderContinentChart() {
    const ctx = document.getElementById('continentChart');
    const data = appData.continentPerformance;

    if (charts.continentChart) charts.continentChart.destroy();

    charts.continentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.continent),
            datasets: [
                {
                    label: 'ARIMA RMSE',
                    data: data.map(d => d.arima_rmse / 1e9),
                    backgroundColor: '#88a9c3',
                    borderRadius: 8
                },
                {
                    label: 'Prophet RMSE',
                    data: data.map(d => d.prophet_rmse / 1e9),
                    backgroundColor: '#2b4257',
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y.toFixed(2);
                            return `${label}: ${value}B USD`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: (value) => formatNumber(value, 1) + 'B'
                    }
                }
            }
        }
    });
}

function renderContinentStatsCards() {
    const grid = document.getElementById('continentStatsGrid');
    grid.innerHTML = '';

    appData.continentStats.forEach(stat => {
        const card = document.createElement('div');
        card.className = 'continent-stat-card';
        
        const totalCountries = stat.total_countries;
        const prophetPercentage = ((stat.prophet_wins / totalCountries) * 100).toFixed(1);
        const arimaPercentage = ((stat.arima_wins / totalCountries) * 100).toFixed(1);

        card.innerHTML = `
            <h4>${stat.continent}</h4>
            <div class="continent-stat-row">
                <span class="continent-stat-label">Total Countries</span>
                <span class="continent-stat-value">${stat.total_countries}</span>
            </div>
            <div class="continent-stat-row">
                <span class="continent-stat-label">Prophet Wins</span>
                <span class="continent-stat-value">${stat.prophet_wins} (${prophetPercentage}%)</span>
            </div>
            <div class="continent-stat-row">
                <span class="continent-stat-label">ARIMA Wins</span>
                <span class="continent-stat-value">${stat.arima_wins} (${arimaPercentage}%)</span>
            </div>
            <div class="continent-stat-row">
                <span class="continent-stat-label">Avg MAPE (Prophet)</span>
                <span class="continent-stat-value">${formatNumber(stat.avg_prophet_mape, 2)}%</span>
            </div>
            <div class="continent-stat-row">
                <span class="continent-stat-label">Avg MAPE (ARIMA)</span>
                <span class="continent-stat-value">${formatNumber(stat.avg_arima_mape, 2)}%</span>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

function renderContinentTable() {
    const tbody = document.querySelector('#continentTable tbody');
    tbody.innerHTML = '';

    appData.continentPerformance.forEach((continent, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${continent.continent}</strong></td>
            <td>${formatNumber(continent.arima_mae / 1e9, 2)}</td>
            <td>${formatNumber(continent.arima_rmse / 1e9, 2)}</td>
            <td>${formatNumber(continent.arima_mape, 2)}%</td>
            <td>${formatNumber(continent.prophet_mae / 1e9, 2)}</td>
            <td>${formatNumber(continent.prophet_rmse / 1e9, 2)}</td>
            <td>${formatNumber(continent.prophet_mape, 2)}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Utility functions
function formatNumber(num, decimals = 0) {
    if (num === null || num === undefined) return '-';
    return num.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function updateTableInfo(displayed, total) {
    document.getElementById('displayedRows').textContent = displayed;
    document.getElementById('totalRows').textContent = total;
}

function convertToCSV(data) {
    if (!data || data.length === 0) return '';

    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];

    data.forEach(row => {
        const values = headers.map(header => {
            const value = row[header];
            return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
        });
        csvRows.push(values.join(','));
    });

    return csvRows.join('\n');
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Render Forecast Section
function renderForecastSection() {
    populateCountrySelector();
    setupForecastSelector();
}

function populateCountrySelector() {
    const select = document.getElementById('countrySelector');
    
    if (!appData.countries) return;
    
    appData.countries.forEach(country => {
        const option = document.createElement('option');
        option.value = country.country;
        option.textContent = `${country.country} (${country.continent})`;
        select.appendChild(option);
    });
}

function setupForecastSelector() {
    const select = document.getElementById('countrySelector');
    
    select.addEventListener('change', async (e) => {
        const country = e.target.value;
        
        if (!country) {
            document.getElementById('forecastChartCard').style.display = 'none';
            document.getElementById('forecastWinnerSummary').style.display = 'none';
            document.getElementById('yearWinnerTable').style.display = 'none';
            document.getElementById('forecastError').style.display = 'none';
            return;
        }
        
        // Show loading
        document.getElementById('forecastLoading').style.display = 'flex';
        document.getElementById('forecastChartCard').style.display = 'none';
        document.getElementById('forecastError').style.display = 'none';
        
        try {
            const response = await fetch(`/api/forecast-detail/${country}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            renderForecastChart(data);
            renderWinnerInfo(data);
            
            document.getElementById('forecastChartCard').style.display = 'block';
            document.getElementById('forecastWinnerSummary').style.display = 'grid';
            document.getElementById('yearWinnerTable').style.display = 'block';
            document.getElementById('forecastLoading').style.display = 'none';
            
            // Update title
            document.getElementById('forecastChartTitle').textContent = 
                `Forecast Detail: ${data.country}`;
            document.getElementById('forecastChartSubtitle').textContent = 
                `${data.continent} | GDP Historical vs Forecasted (2000-2025)`;
        } catch (error) {
            console.error('Error loading forecast:', error);
            document.getElementById('forecastError').style.display = 'block';
            document.getElementById('forecastChartCard').style.display = 'none';
            document.getElementById('forecastWinnerSummary').style.display = 'none';
            document.getElementById('yearWinnerTable').style.display = 'none';
            document.getElementById('forecastLoading').style.display = 'none';
        }
    });
}

function renderForecastChart(data) {
    const ctx = document.getElementById('forecastChart');
    
    if (charts.forecastChart) {
        charts.forecastChart.destroy();
    }
    
    const labels = data.data.map(d => d.year);
    const actual = data.data.map(d => d.actual);
    const forecastArima = data.data.map(d => d.forecast_arima);
    const forecastProphet = data.data.map(d => d.forecast_prophet);
    
    // Store winners data for tooltip
    const winnersMap = {};
    data.winners.forEach(w => {
        winnersMap[w.year] = w;
    });
    
    charts.forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Actual GDP',
                    data: actual,
                    borderColor: '#2b4257',
                    backgroundColor: 'rgba(43, 66, 87, 0.1)',
                    borderWidth: 3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'ARIMA Forecast',
                    data: forecastArima,
                    borderColor: '#88a9c3',
                    backgroundColor: 'rgba(136, 169, 195, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Prophet Forecast',
                    data: forecastProphet,
                    borderColor: '#2b4257',
                    backgroundColor: 'rgba(43, 66, 87, 0.1)',
                    borderWidth: 2,
                    borderDash: [10, 5],
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            onHover: (event, activeElements) => {
                // Change cursor to pointer when hovering over data points
                event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
            },
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return `${label}: ${formatNumber(value, 2)}B USD`;
                        },
                        footer: (tooltipItems) => {
                            // Get the year from the first item
                            const year = tooltipItems[0].label;
                            const winner = winnersMap[year];
                            
                            if (winner) {
                                const arimaErr = formatNumber(winner.arima_error, 2);
                                const prophetErr = formatNumber(winner.prophet_error, 2);
                                return [
                                    '',
                                    `Best Model: ${winner.winner}`,
                                    `│ ARIMA Error: ${arimaErr}B`,
                                    `│ Prophet Error: ${prophetErr}B`
                                ];
                            }
                            return '';
                        }
                    },
                    footerAlign: 'left',
                    footerFont: {
                        weight: 'bold',
                        size: 11
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: (value) => formatNumber(value, 1) + 'B',
                        font: {
                            size: 11
                        }
                    },
                    title: {
                        display: true,
                        text: 'GDP (Billion USD)',
                        font: {
                            size: 12
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 11
                        }
                    },
                    title: {
                        display: true,
                        text: 'Year',
                        font: {
                            size: 12
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

function renderWinnerInfo(data) {
    // Update summary cards
    document.getElementById('arimaScore').textContent = data.arima_wins;
    document.getElementById('prophetScore').textContent = data.prophet_wins;
    
    // Determine overall winner
    let overallWinner, percentage;
    if (data.arima_wins > data.prophet_wins) {
        overallWinner = 'ARIMA';
        percentage = ((data.arima_wins / data.total_forecast_years) * 100).toFixed(1);
    } else if (data.prophet_wins > data.arima_wins) {
        overallWinner = 'Prophet';
        percentage = ((data.prophet_wins / data.total_forecast_years) * 100).toFixed(1);
    } else {
        overallWinner = 'Tie';
        percentage = '50.0';
    }
    
    document.getElementById('overallWinner').textContent = overallWinner;
    document.getElementById('overallWinnerPercentage').textContent = `${percentage}%` + ' of years';
    
    // Update table
    const tbody = document.querySelector('#forecastWinnerTable tbody');
    tbody.innerHTML = '';
    
    data.winners.forEach((winner, index) => {
        const row = document.createElement('tr');
        const actualGdp = data.data.find(d => d.year === winner.year)?.actual || '-';
        
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${winner.year}</strong></td>
            <td>${formatNumber(actualGdp, 2)}</td>
            <td>${formatNumber(winner.arima_error, 2)}</td>
            <td>${formatNumber(winner.prophet_error, 2)}</td>
            <td><span class="badge badge-${winner.winner.toLowerCase()}">${winner.winner}</span></td>
        `;
        tbody.appendChild(row);
    });
}

