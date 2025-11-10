#!/usr/bin/env python3
"""
Advanced Pattern Analyzer for Morty Rescue Mission

This script analyzes saved trip data to identify patterns and optimize strategy.
Especially useful for understanding the sinusoidal patterns in Planet 2.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
import argparse
from typing import Dict, List, Tuple


class AdvancedPatternAnalyzer:
    """Deep analysis of planet survival patterns"""

    def __init__(self, results_file: str = None):
        self.results = None
        if results_file:
            self.load_results(results_file)

    def load_results(self, filename: str):
        """Load results from a previous run"""
        with open(filename, 'r') as f:
            self.results = json.load(f)
        print(f"✅ Loaded {len(self.results['trip_history'])} trips from {filename}")

    def sinusoidal_model(self, x, amplitude, period, phase, offset):
        """Sinusoidal model: y = offset + amplitude * sin(2π * x / period + phase)"""
        return offset + amplitude * np.sin(2 * np.pi * x / period + phase)

    def analyze_planet_deep(self, planet: int, morty_count: int = None):
        """
        Deep analysis of a specific planet's patterns

        Args:
            planet: Planet index (0, 1, or 2)
            morty_count: Optional filter for specific group size (1, 2, or 3)
        """
        planet_names = ["On a Cob Planet", "Cronenberg World", "Purge Planet"]

        print(f"\n{'='*60}")
        print(f"🔬 DEEP ANALYSIS: {planet_names[planet]}")
        if morty_count:
            print(f"Group Size: {morty_count} Morty(s)")
        print(f"{'='*60}\n")

        # Filter trips for this planet
        trips = [t for t in self.results['trip_history'] if t['planet'] == planet]
        if morty_count:
            trips = [t for t in trips if t['morty_count'] == morty_count]

        if len(trips) == 0:
            print("⚠️  No data available for this combination")
            return

        # Separate by group size if not filtering
        if morty_count is None:
            for mc in [1, 2, 3]:
                mc_trips = [t for t in trips if t['morty_count'] == mc]
                if len(mc_trips) >= 10:
                    print(f"\n--- {mc} Morty Group ---")
                    self._analyze_trip_sequence(mc_trips, f"{planet_names[planet]} - {mc} Morty(s)")
        else:
            self._analyze_trip_sequence(trips, f"{planet_names[planet]} - {morty_count} Morty(s)")

    def _analyze_trip_sequence(self, trips: List[Dict], title: str):
        """Analyze a sequence of trips"""
        # Extract data
        trip_nums = [t['cumulative_trips'] for t in trips]
        survived = [1 if t['survived'] else 0 for t in trips]

        # Basic statistics
        total = len(trips)
        survived_count = sum(survived)
        survival_rate = survived_count / total if total > 0 else 0

        print(f"\n📊 {title}")
        print(f"Total trips: {total}")
        print(f"Survived: {survived_count} ({survival_rate:.1%})")
        print(f"Lost: {total - survived_count} ({(1-survival_rate):.1%})")

        if len(trips) < 20:
            print("⚠️  Insufficient data for pattern analysis (need at least 20 trips)")
            return

        # Detect patterns
        self._detect_periodicity(trip_nums, survived, title)
        self._fit_sinusoidal(trip_nums, survived, title)

    def _detect_periodicity(self, trip_nums: List[int], survived: List[int], title: str):
        """Detect periodic patterns using autocorrelation"""
        print("\n🔍 Periodicity Detection:")

        # Compute autocorrelation
        survived_array = np.array(survived, dtype=float)
        survived_centered = survived_array - np.mean(survived_array)

        if len(survived_centered) < 50:
            print("⚠️  Not enough data for autocorrelation analysis")
            return

        # Autocorrelation
        autocorr = np.correlate(survived_centered, survived_centered, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]  # Normalize

        # Find peaks in autocorrelation
        peaks, properties = find_peaks(autocorr[1:], height=0.1, distance=10)
        peaks = peaks + 1  # Adjust for starting at index 1

        if len(peaks) > 0:
            print(f"✅ Detected potential periods at trip intervals: {peaks[:5]}")
            estimated_period = peaks[0] if len(peaks) > 0 else None
            if estimated_period:
                print(f"📏 Primary period estimate: {estimated_period} trips")
        else:
            print("❌ No clear periodic pattern detected")

    def _fit_sinusoidal(self, trip_nums: List[int], survived: List[int], title: str):
        """Fit sinusoidal model to the data"""
        print("\n📈 Sinusoidal Model Fitting:")

        x = np.array(trip_nums, dtype=float)
        y = np.array(survived, dtype=float)

        # Apply moving average to smooth data for fitting
        window = min(20, len(y) // 4)
        if window > 1:
            y_smooth = np.convolve(y, np.ones(window)/window, mode='valid')
            x_smooth = x[:len(y_smooth)]
        else:
            y_smooth = y
            x_smooth = x

        try:
            # Initial guess - try multiple periods
            best_fit = None
            best_r2 = -np.inf

            for initial_period in [50, 100, 150, 200, 250, 300]:
                try:
                    popt, pcov = curve_fit(
                        self.sinusoidal_model,
                        x_smooth,
                        y_smooth,
                        p0=[0.3, initial_period, 0, 0.5],
                        bounds=([-1, 30, -2*np.pi, 0], [1, 500, 2*np.pi, 1]),
                        maxfev=10000
                    )

                    # Calculate R²
                    y_pred = self.sinusoidal_model(x_smooth, *popt)
                    ss_res = np.sum((y_smooth - y_pred) ** 2)
                    ss_tot = np.sum((y_smooth - np.mean(y_smooth)) ** 2)
                    r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

                    if r2 > best_r2:
                        best_r2 = r2
                        best_fit = popt

                except:
                    continue

            if best_fit is not None:
                amplitude, period, phase, offset = best_fit

                print(f"✅ Sinusoidal fit successful!")
                print(f"   Amplitude: {amplitude:.3f}")
                print(f"   Period: {period:.1f} trips")
                print(f"   Phase: {phase:.3f} radians ({np.degrees(phase):.1f}°)")
                print(f"   Offset (baseline): {offset:.3f}")
                print(f"   R² score: {best_r2:.3f}")

                # Calculate predicted peaks and troughs
                print(f"\n🎯 Optimal Trip Timing:")
                print(f"   Peak survival occurs every {period:.1f} trips")
                print(f"   Current phase shift: {phase:.3f}")

                # Find next peak from the last trip
                last_trip = x[-1] if len(x) > 0 else 0
                # Peaks occur when sin() = 1, i.e., when 2π*x/period + phase = π/2
                # x_peak = (π/2 - phase) * period / (2π) + n*period
                base_peak = (np.pi/2 - phase) * period / (2*np.pi)
                # Find the next peak after last_trip
                n_periods = np.ceil((last_trip - base_peak) / period)
                next_peak = base_peak + n_periods * period

                print(f"   Next predicted peak: trip ~{int(next_peak)}")

                return {
                    'amplitude': amplitude,
                    'period': period,
                    'phase': phase,
                    'offset': offset,
                    'r2': best_r2,
                    'next_peak': next_peak
                }

        except Exception as e:
            print(f"❌ Sinusoidal fitting failed: {e}")

        return None

    def compare_all_planets(self):
        """Compare patterns across all three planets"""
        print(f"\n{'='*60}")
        print("🌍 COMPARING ALL PLANETS")
        print(f"{'='*60}\n")

        fig, axes = plt.subplots(3, 3, figsize=(20, 16))
        planet_names = ["On a Cob Planet", "Cronenberg World", "Purge Planet"]

        for planet in range(3):
            for morty_count in range(1, 4):
                ax = axes[planet][morty_count - 1]

                # Get trips for this combination
                trips = [t for t in self.results['trip_history']
                        if t['planet'] == planet and t['morty_count'] == morty_count]

                if len(trips) == 0:
                    ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
                           transform=ax.transAxes, fontsize=14)
                    ax.set_title(f"P{planet}: {planet_names[planet]}\n{morty_count} Morty(s)",
                               fontsize=11, fontweight='bold')
                    continue

                trip_nums = [t['cumulative_trips'] for t in trips]
                survived = [1 if t['survived'] else 0 for t in trips]

                # Plot raw data
                colors = ['red' if s == 0 else 'green' for s in survived]
                ax.scatter(trip_nums, survived, alpha=0.4, s=30, c=colors, edgecolors='black', linewidth=0.5)

                # Plot moving average
                window = min(15, len(survived) // 3)
                if window > 1 and len(survived) >= window:
                    survived_ma = np.convolve(survived, np.ones(window)/window, mode='valid')
                    trips_ma = trip_nums[:len(survived_ma)]
                    ax.plot(trips_ma, survived_ma, 'b-', linewidth=2.5, label=f'{window}-trip MA', alpha=0.7)

                # Try to fit sinusoidal
                try:
                    x = np.array(trip_nums, dtype=float)
                    y = np.array(survived, dtype=float)

                    if len(y) >= 20:
                        y_smooth = np.convolve(y, np.ones(min(15, len(y)//3))/min(15, len(y)//3), mode='valid')
                        x_smooth = x[:len(y_smooth)]

                        # Try fitting with period around 200 for planet 2, varied for others
                        initial_periods = [200] if planet == 2 else [100, 150, 200]

                        best_fit = None
                        best_r2 = -np.inf

                        for init_period in initial_periods:
                            try:
                                popt, _ = curve_fit(
                                    self.sinusoidal_model,
                                    x_smooth, y_smooth,
                                    p0=[0.3, init_period, 0, 0.5],
                                    bounds=([-1, 50, -2*np.pi, 0], [1, 400, 2*np.pi, 1]),
                                    maxfev=10000
                                )

                                y_pred = self.sinusoidal_model(x_smooth, *popt)
                                r2 = 1 - np.sum((y_smooth - y_pred)**2) / np.sum((y_smooth - np.mean(y_smooth))**2)

                                if r2 > best_r2:
                                    best_r2 = r2
                                    best_fit = popt
                            except:
                                continue

                        if best_fit is not None and best_r2 > 0.1:
                            x_range = np.linspace(min(trip_nums), max(trip_nums), 300)
                            y_pred = self.sinusoidal_model(x_range, *best_fit)
                            ax.plot(x_range, y_pred, 'purple', linewidth=2,
                                   label=f'Sin(T={best_fit[1]:.0f}, R²={best_r2:.2f})', linestyle='--')
                except:
                    pass

                # Calculate and show survival rate
                survival_rate = sum(survived) / len(survived)
                ax.axhline(y=survival_rate, color='orange', linestyle=':', linewidth=2,
                          label=f'Avg={survival_rate:.1%}')

                ax.set_title(f"P{planet}: {planet_names[planet]}\n{morty_count} Morty(s) | Rate: {survival_rate:.1%}",
                           fontsize=11, fontweight='bold')
                ax.set_xlabel('Trip Number (to this planet)', fontsize=10)
                ax.set_ylabel('Survived', fontsize=10)
                ax.set_ylim(-0.1, 1.1)
                ax.legend(fontsize=8, loc='upper right')
                ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_file = '/home/user/aicheckr-site/morty_pattern_comparison.png'
        plt.savefig(output_file, dpi=200, bbox_inches='tight')
        print(f"✅ Comparison visualization saved to: {output_file}")

    def predict_optimal_strategy(self):
        """Predict the optimal strategy going forward"""
        print(f"\n{'='*60}")
        print("🎯 OPTIMAL STRATEGY PREDICTION")
        print(f"{'='*60}\n")

        # Analyze patterns for each planet/group combination
        predictions = {}

        for planet in range(3):
            for morty_count in range(1, 4):
                trips = [t for t in self.results['trip_history']
                        if t['planet'] == planet and t['morty_count'] == morty_count]

                if len(trips) < 20:
                    continue

                trip_nums = np.array([t['cumulative_trips'] for t in trips])
                survived = np.array([1 if t['survived'] else 0 for t in trips])

                # Fit pattern
                try:
                    y_smooth = np.convolve(survived, np.ones(min(15, len(survived)//3))/min(15, len(survived)//3), mode='valid')
                    x_smooth = trip_nums[:len(y_smooth)]

                    popt, _ = curve_fit(
                        self.sinusoidal_model,
                        x_smooth, y_smooth,
                        p0=[0.3, 200, 0, 0.5],
                        bounds=([-1, 50, -2*np.pi, 0], [1, 400, 2*np.pi, 1]),
                        maxfev=10000
                    )

                    # Predict next few trips
                    last_trip = int(trip_nums[-1])
                    future_trips = np.arange(last_trip + 1, last_trip + 51)
                    future_probs = self.sinusoidal_model(future_trips, *popt)
                    future_probs = np.clip(future_probs, 0, 1)

                    avg_prob = np.mean(future_probs)
                    max_prob = np.max(future_probs)
                    max_prob_trip = future_trips[np.argmax(future_probs)]

                    predictions[(planet, morty_count)] = {
                        'avg_prob': avg_prob,
                        'max_prob': max_prob,
                        'max_prob_trip': max_prob_trip,
                        'expected_value': avg_prob * morty_count,
                        'period': popt[1]
                    }

                except:
                    # Fall back to empirical average
                    avg_prob = np.mean(survived)
                    predictions[(planet, morty_count)] = {
                        'avg_prob': avg_prob,
                        'expected_value': avg_prob * morty_count,
                        'period': None
                    }

        # Rank by expected value
        ranked = sorted(predictions.items(), key=lambda x: x[1]['expected_value'], reverse=True)

        planet_names = ["On a Cob", "Cronenberg", "Purge"]

        print("🏆 Top 5 Strategies (by expected value):\n")
        for i, ((planet, morty_count), pred) in enumerate(ranked[:5], 1):
            ev = pred['expected_value']
            prob = pred['avg_prob']
            print(f"{i}. Planet {planet} ({planet_names[planet]}), {morty_count} Morty(s)")
            print(f"   Expected Value: {ev:.3f} | Survival Prob: {prob:.1%}")
            if pred.get('period'):
                print(f"   Pattern: Sinusoidal with period {pred['period']:.1f}")
            if pred.get('max_prob_trip'):
                print(f"   Next peak at trip ~{pred['max_prob_trip']}")
            print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Advanced Morty Rescue Pattern Analyzer')
    parser.add_argument('--results', '-r', default='/home/user/aicheckr-site/morty_rescue_results.json',
                       help='Path to results JSON file')
    parser.add_argument('--planet', '-p', type=int, choices=[0, 1, 2],
                       help='Analyze specific planet (0, 1, or 2)')
    parser.add_argument('--morty-count', '-m', type=int, choices=[1, 2, 3],
                       help='Analyze specific group size (1, 2, or 3)')
    parser.add_argument('--compare', '-c', action='store_true',
                       help='Compare all planets')
    parser.add_argument('--predict', action='store_true',
                       help='Predict optimal strategy')

    args = parser.parse_args()

    print("🔬 ADVANCED MORTY RESCUE PATTERN ANALYZER")
    print("=" * 60)

    analyzer = AdvancedPatternAnalyzer(args.results)

    if analyzer.results is None:
        print("❌ No results file found. Run morty_rescue.py first!")
        return

    if args.planet is not None:
        analyzer.analyze_planet_deep(args.planet, args.morty_count)

    if args.compare:
        analyzer.compare_all_planets()

    if args.predict:
        analyzer.predict_optimal_strategy()

    if not any([args.planet is not None, args.compare, args.predict]):
        # Default: do everything
        print("\n Running full analysis...\n")
        for planet in range(3):
            analyzer.analyze_planet_deep(planet)
        analyzer.compare_all_planets()
        analyzer.predict_optimal_strategy()


if __name__ == "__main__":
    main()
