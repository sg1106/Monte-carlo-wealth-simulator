# Monte Carlo Wealth Simulator v2

A beautiful, production-grade **no-Streamlit** Monte Carlo simulator with Flask backend and HTML/CSS/JavaScript frontend.

## Features

✨ **Advanced Simulation**
- Geometric Brownian Motion (GBM) with Box-Muller normal sampling
- Annual contribution support (properly compounded)
- Configurable time steps: monthly, weekly, or daily
- 200–5000 parallel simulation paths

📊 **Interactive Visualizations**
- Live Monte Carlo chart with IQR and CI bands
- Final value distribution histogram
- Probability of reaching financial targets
- Real-time metric updates

🎨 **Professional Design**
- Dark terminal/trading-floor aesthetic
- Responsive layout (desktop & mobile)
- Custom Charts.js visualizations
- IBM Plex typography

## Project Structure

```
.
├── app.py                    # Flask backend (Python)
├── templates/
│   └── index.html           # Frontend (HTML/CSS/JS)
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup & Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 3. Open in Browser

Navigate to **http://localhost:5000** in your web browser.

## Usage

**Sidebar Controls:**
- **Initial Capital**: Starting portfolio value ($1K–$10M)
- **Annual Contribution**: Recurring deposit ($0–$500K/year)
- **Annual Return**: Expected return μ (−10% to +25%)
- **Volatility σ**: Market risk (1%–60%)
- **Inflation Rate**: Real return adjustment (0%–8%)
- **Time Horizon**: Simulation length (1–50 years)
- **Simulations**: Number of paths (200–5000)
- **Steps/Year**: Frequency (monthly, weekly, daily)
- **Show Paths**: Sample paths to visualize (0–300)
- **CI Lower/Upper**: Confidence bands (e.g., 5%–95%)

**Outputs:**
- 5 metric cards: Median, Best, Worst, Mean, Real Value
- Interactive Monte Carlo chart with percentile bands
- Distribution histogram with probability zones
- Target achievement probability bars ($500K, $1M, $5M, etc.)

## Python Backend (app.py)

**Key Functions:**
- `simulate_gbm()`: Core Monte Carlo engine
- `box_muller()`: Fast normal random number generation
- `calculate_stats()`: Percentile and probability calculations
- `/api/simulate` endpoint: Handles POST requests from frontend

**Returns JSON** with:
```json
{
  "success": true,
  "stats": {
    "p5": 100000, "p50": 350000, "p95": 900000, "mean": 420000, ...
  },
  "chart": {
    "times": [...],
    "percentiles": { "p5": [...], "p50": [...], ... },
    "mean_path": [...],
    "sample_paths": [...]
  },
  "distribution": {
    "bins": [...],
    "counts": [...]
  }
}
```

## Frontend (index.html)

**Technology Stack:**
- **Framework**: Vanilla JavaScript (no libraries except Chart.js)
- **Charts**: Chart.js 4.4.1 (from CDN)
- **Fonts**: IBM Plex Mono & IBM Plex Sans (Google Fonts)
- **Styling**: CSS Grid, CSS Variables, dark theme

**Key Functions:**
- `runSimulation()`: Calls backend API
- `drawMainChart()`: Renders scatter/line chart
- `drawDistChart()`: Renders distribution histogram
- `drawProbBars()`: Updates probability progress bars
- `syncLabels()`: Real-time label updates as sliders move

## API Endpoint

### POST `/api/simulate`

**Request:**
```json
{
  "initial_capital": 10000,
  "annual_contribution": 0,
  "annual_return": 7.0,
  "volatility": 15.0,
  "inflation": 2.0,
  "time_horizon": 20,
  "n_simulations": 1000,
  "steps_per_year": 12,
  "show_paths": 100,
  "ci_lower": 5,
  "ci_upper": 95
}
```

**Response:** Full simulation data (see above).

## Customization

### Change Color Scheme
Edit CSS variables in `templates/index.html`:
```css
:root {
    --gold: #F5C842;
    --green: #3DD68C;
    --red: #FF5B5B;
    --bg: #0D0F14;
    /* ... etc */
}
```

### Adjust Default Parameters
In `index.html`, modify slider/input default `value` attributes:
```html
<input type="range" id="inp-mu" ... value="7">
```

In `app.py`, change default simulation steps:
```python
n_steps = int(n_steps_per_year * T)  # Default: monthly
```

## Performance

- **1000 paths × 20 years × 12 steps/year**: ~200ms
- **5000 paths × 50 years × 252 steps/year**: ~2–3s

Charts update smoothly with CSS animations (0.8s duration).

## Browser Support

✅ Chrome, Edge, Firefox, Safari (all modern versions)

## License

Unlicensed. Use freely for personal or commercial projects.

## Disclaimer

**This is a simulation tool only.** Past returns do not guarantee future results. Not financial advice. Always consult a professional financial advisor.

---

**Made with ❤️ using pure Python & JavaScript. No frameworks. No clutter.**
