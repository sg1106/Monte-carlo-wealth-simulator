from flask import Flask, render_template, request, jsonify
import numpy as np
import json
import os 

app = Flask(__name__)

def box_muller(n):
    """Fast vectorised normal samples via Box-Muller."""
    u1 = np.random.uniform(1e-10, 1.0, n)
    u2 = np.random.uniform(0.0, 1.0, n)
    r = np.sqrt(-2.0 * np.log(u1))
    return r * np.cos(2.0 * np.pi * u2)


def simulate_gbm(S0, mu_pct, sigma_pct, T, contrib_annual, n_sim, n_steps):
    """Simulate wealth paths using geometric Brownian motion."""
    mu_ = mu_pct / 100
    sigma_ = sigma_pct / 100
    dt = T / n_steps
    drift = (mu_ - 0.5 * sigma_ ** 2) * dt
    diff = sigma_ * np.sqrt(dt)
    contrib_step = contrib_annual * dt

    Z = box_muller(n_sim * n_steps).reshape(n_sim, n_steps)
    log_inc = drift + diff * Z
    log_paths = np.concatenate(
        [np.zeros((n_sim, 1)), np.cumsum(log_inc, axis=1)], axis=1
    )
    S = S0 * np.exp(log_paths)

    # Add contributions (compounded step by step)
    if contrib_step > 0:
        contrib_cumulative = np.zeros((n_sim, n_steps + 1))
        for t in range(1, n_steps + 1):
            contrib_cumulative[:, t] = (
                contrib_cumulative[:, t - 1] * np.exp(drift + diff * Z[:, t - 1])
                + contrib_step
            )
        S = S + contrib_cumulative

    return S


def percentile(arr, p):
    """Calculate percentile."""
    return np.percentile(arr, p)


def calculate_stats(final_values, initial_capital, time_horizon, ci_lower, ci_upper, inflation, n_sim, n_steps):
    """Calculate simulation statistics."""
    inflation_factor = (1 + inflation / 100) ** time_horizon
    
    p5 = percentile(final_values, ci_lower)
    p25 = percentile(final_values, 25)
    p50 = percentile(final_values, 50)
    p75 = percentile(final_values, 75)
    p95 = percentile(final_values, ci_upper)
    mean_final = np.mean(final_values)
    real_median = p50 / inflation_factor
    
    # Probability of reaching targets
    targets = {
        f"2× (${int(initial_capital*2):,})": initial_capital * 2,
        "$500K": 500_000,
        "$1M": 1_000_000,
        "$5M": 5_000_000,
    }
    probs = {k: float((final_values >= v).mean() * 100) for k, v in targets.items()}
    
    return {
        'p5': float(p5),
        'p25': float(p25),
        'p50': float(p50),
        'p75': float(p75),
        'p95': float(p95),
        'mean': float(mean_final),
        'real_median': float(real_median),
        'probs': probs
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/simulate', methods=['POST'])
def simulate():
    """Run Monte Carlo simulation."""
    try:
        data = request.json
        
        S0 = float(data['initial_capital'])
        mu = float(data['annual_return'])
        sigma = float(data['volatility'])
        T = float(data['time_horizon'])
        contrib = float(data['annual_contribution'])
        n_sim = int(data['n_simulations'])
        n_steps_per_year = int(data['steps_per_year'])
        ci_lower = float(data['ci_lower'])
        ci_upper = float(data['ci_upper'])
        inflation = float(data['inflation'])
        show_paths = int(data['show_paths'])
        
        n_steps = int(n_steps_per_year * T)
        
        # Run simulation
        paths = simulate_gbm(S0, mu, sigma, T, contrib, n_sim, n_steps)
        final_values = paths[:, -1]
        
        # Calculate statistics
        stats = calculate_stats(final_values, S0, T, ci_lower, ci_upper, inflation, n_sim, n_steps)
        
        # Prepare chart data
        times = np.linspace(0, T, n_steps + 1)
        
        pct_paths = {
            'p5': np.percentile(paths, ci_lower, axis=0),
            'p25': np.percentile(paths, 25, axis=0),
            'p50': np.percentile(paths, 50, axis=0),
            'p75': np.percentile(paths, 75, axis=0),
            'p95': np.percentile(paths, ci_upper, axis=0),
        }
        mean_path = np.mean(paths, axis=0)
        
        # Sample paths to show
        step = max(1, n_sim // show_paths) if show_paths > 0 else n_sim + 1
        sample_paths = []
        for i in range(0, min(n_sim, show_paths * step), step):
            sample_paths.append(paths[i].tolist())
        
        # Distribution histogram
        bins = 60
        counts, edges = np.histogram(final_values, bins=bins)
        bin_mids = ((edges[:-1] + edges[1:]) / 2).tolist()
        bin_counts = counts.tolist()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'chart': {
                'times': times.tolist(),
                'percentiles': {k: v.tolist() for k, v in pct_paths.items()},
                'mean_path': mean_path.tolist(),
                'sample_paths': sample_paths,
            },
            'distribution': {
                'bins': bin_mids,
                'counts': bin_counts,
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
