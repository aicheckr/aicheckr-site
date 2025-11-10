#!/usr/bin/env python3
"""
Morty Pattern Discovery - Deep dive into planet-specific patterns

This script focuses on discovering the exact mathematical patterns for each
planet by running many episodes sending all Morties to the same planet.

Perfect for overnight runs to gather thousands of data points per planet!
"""

import requests
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.fft import fft, fftfreq
import argparse
from collections import defaultdict
import os
from datetime import datetime


class PatternDiscovery:
    """Focused pattern discovery for a single planet"""

    BASE_URL = "https://challenge.sphinxhq.com"

    def __init__(self, token: str, planet: int, morty_count: int, output_dir: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        self.planet = planet
        self.morty_count = morty_count
        self.output_dir = output_dir
        self.planet_names = ["On a Cob Planet", "Cronenberg World", "Purge Planet"]

        os.makedirs(output_dir, exist_ok=True)

        # Aggregate data across all episodes
        self.all_trips = []  # (trip_number, survived)
        self.episode_results = []

    def start_episode(self) -> bool:
        """Start new episode"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/mortys/start/",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def send_morties(self, planet: int, count: int) -> tuple:
        """Send Morties through portal"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/mortys/portal/",
                headers=self.headers,
                json={"planet": planet, "morty_count": count},
                timeout=10
            )
            if response.status_code == 200:
                return True, response.json()
            return False, {}
        except:
            return False, {}

    def run_focused_episode(self, episode_num: int) -> list:
        """
        Run one episode sending all Morties to the target planet

        Returns list of (trip_number, survived) tuples
        """
        print(f"\n🚀 Episode {episode_num}: {self.planet_names[self.planet]}, {self.morty_count} Morty(s) per trip")

        if not self.start_episode():
            print("❌ Failed to start episode")
            return []

        trips = []
        trip_num = 0
        morties_remaining = 1000

        while morties_remaining >= self.morty_count:
            success, data = self.send_morties(self.planet, self.morty_count)

            if not success:
                print(f"❌ Trip {trip_num} failed")
                break

            survived = data.get('survived', False)
            trips.append((trip_num, survived))

            morties_remaining = data['morties_in_citadel']
            trip_num += 1

            if trip_num % 100 == 0:
                survival_rate = sum(1 for _, s in trips if s) / len(trips)
                print(f"  Trip {trip_num}: Rate={survival_rate:.1%}, Remaining={morties_remaining}")

        survival_count = sum(1 for _, s in trips if s)
        total_saved = survival_count * self.morty_count
        print(f"✅ Episode complete: {len(trips)} trips, {total_saved} Morties saved")

        return trips

    def run_discovery(self, num_episodes: int):
        """
        Run multiple episodes to gather extensive pattern data

        Args:
            num_episodes: Number of episodes to run
        """
        print(f"\n{'='*60}")
        print(f"🔬 PATTERN DISCOVERY")
        print(f"{'='*60}")
        print(f"Target: Planet {self.planet} ({self.planet_names[self.planet]})")
        print(f"Group size: {self.morty_count} Morty(s)")
        print(f"Episodes: {num_episodes}")
        print(f"{'='*60}\n")

        for i in range(1, num_episodes + 1):
            try:
                episode_data = self.run_focused_episode(i)

                if len(episode_data) == 0:
                    print(f"⚠️  Episode {i} yielded no data, skipping...")
                    continue

                # Add to aggregate data
                self.all_trips.extend(episode_data)
                self.episode_results.append({
                    'episode': i,
                    'trips': episode_data,
                    'total_trips': len(episode_data),
                    'survival_rate': sum(1 for _, s in episode_data if s) / len(episode_data)
                })

                # Save progress after each episode
                self.save_progress(i)

            except KeyboardInterrupt:
                print("\n⚠️  Interrupted by user. Saving progress...")
                break
            except Exception as e:
                print(f"❌ Episode {i} error: {e}")
                continue

        print(f"\n{'='*60}")
        print(f"🏁 DISCOVERY COMPLETE")
        print(f"{'='*60}")
        print(f"Total trips collected: {len(self.all_trips)}")
        print(f"Episodes completed: {len(self.episode_results)}")

        # Analyze patterns
        self.analyze_patterns()

    def save_progress(self, episode_num: int):
        """Save current progress"""
        progress_file = f"{self.output_dir}/discovery_P{self.planet}_M{self.morty_count}_progress.json"

        data = {
            'planet': self.planet,
            'morty_count': self.morty_count,
            'episodes_completed': episode_num,
            'total_trips': len(self.all_trips),
            'all_trips': self.all_trips,
            'episode_results': self.episode_results,
            'timestamp': datetime.now().isoformat()
        }

        with open(progress_file, 'w') as f:
            json.dump(data, f, indent=2)

    def sinusoidal_model(self, x, amplitude, period, phase, offset):
        """Sinusoidal model"""
        return offset + amplitude * np.sin(2 * np.pi * x / period + phase)

    def analyze_patterns(self):
        """Deep pattern analysis"""
        if len(self.all_trips) < 50:
            print("⚠️  Not enough data for pattern analysis")
            return

        print(f"\n{'='*60}")
        print(f"📊 PATTERN ANALYSIS")
        print(f"{'='*60}\n")

        # Extract data
        trip_numbers = np.array([t[0] for t in self.all_trips])
        survived = np.array([1.0 if t[1] else 0.0 for t in self.all_trips])

        # Basic statistics
        overall_rate = np.mean(survived)
        print(f"📈 Basic Statistics:")
        print(f"   Total trips: {len(self.all_trips)}")
        print(f"   Overall survival rate: {overall_rate:.1%}")
        print(f"   Standard deviation: {np.std(survived):.3f}")

        # Frequency analysis using FFT
        print(f"\n🔍 Frequency Analysis (FFT):")
        self.frequency_analysis(trip_numbers, survived)

        # Fit sinusoidal model
        print(f"\n📈 Sinusoidal Model Fitting:")
        self.fit_sinusoidal(trip_numbers, survived)

        # Generate visualizations
        self.visualize_patterns(trip_numbers, survived)

    def frequency_analysis(self, x, y):
        """Use FFT to detect dominant frequencies"""
        # Apply FFT
        n = len(y)
        yf = fft(y - np.mean(y))  # Remove DC component
        xf = fftfreq(n, 1.0)[:n//2]

        # Get magnitude
        magnitude = 2.0/n * np.abs(yf[0:n//2])

        # Find dominant frequencies
        peaks_idx = np.argsort(magnitude)[-5:][::-1]  # Top 5 peaks

        print("   Top 5 frequencies detected:")
        for idx in peaks_idx:
            if xf[idx] > 0:  # Skip DC component
                period = 1.0 / xf[idx]
                print(f"      Period ≈ {period:.1f} trips (magnitude: {magnitude[idx]:.3f})")

    def fit_sinusoidal(self, x, y):
        """Fit sinusoidal model with multiple initial guesses"""
        # Smooth data for fitting
        window = min(20, len(y) // 5)
        if window > 1:
            y_smooth = np.convolve(y, np.ones(window)/window, mode='valid')
            x_smooth = x[:len(y_smooth)]
        else:
            y_smooth = y
            x_smooth = x

        # Try multiple initial periods
        test_periods = [50, 100, 150, 200, 250, 300, 350, 400]
        best_fit = None
        best_r2 = -np.inf
        best_period_guess = None

        for initial_period in test_periods:
            try:
                popt, _ = curve_fit(
                    self.sinusoidal_model,
                    x_smooth, y_smooth,
                    p0=[0.3, initial_period, 0, 0.5],
                    bounds=([-1, 30, -2*np.pi, 0], [1, 500, 2*np.pi, 1]),
                    maxfev=20000
                )

                # Calculate R²
                y_pred = self.sinusoidal_model(x_smooth, *popt)
                ss_res = np.sum((y_smooth - y_pred) ** 2)
                ss_tot = np.sum((y_smooth - np.mean(y_smooth)) ** 2)
                r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

                if r2 > best_r2:
                    best_r2 = r2
                    best_fit = popt
                    best_period_guess = initial_period

            except Exception as e:
                continue

        if best_fit is not None:
            amplitude, period, phase, offset = best_fit

            print(f"   ✅ Best sinusoidal fit found:")
            print(f"      Amplitude: {amplitude:.3f}")
            print(f"      Period: {period:.1f} trips")
            print(f"      Phase: {phase:.3f} rad ({np.degrees(phase):.1f}°)")
            print(f"      Offset (baseline): {offset:.3f}")
            print(f"      R² score: {best_r2:.3f}")
            print(f"      (tested with initial period: {best_period_guess})")

            # Calculate peak locations
            print(f"\n   🎯 Peak Timing:")
            print(f"      Peaks occur every {period:.1f} trips")

            # Next peak calculation
            if len(x) > 0:
                last_trip = x[-1]
                base_peak = (np.pi/2 - phase) * period / (2*np.pi)
                n_periods = np.ceil((last_trip - base_peak) / period)
                next_peak = base_peak + n_periods * period
                print(f"      Next predicted peak: trip ~{int(next_peak)}")

            # Save model parameters
            model_file = f"{self.output_dir}/model_P{self.planet}_M{self.morty_count}.json"
            with open(model_file, 'w') as f:
                json.dump({
                    'planet': self.planet,
                    'morty_count': self.morty_count,
                    'model': 'sinusoidal',
                    'parameters': {
                        'amplitude': float(amplitude),
                        'period': float(period),
                        'phase': float(phase),
                        'offset': float(offset)
                    },
                    'r2_score': float(best_r2),
                    'total_data_points': len(self.all_trips)
                }, f, indent=2)
            print(f"\n   💾 Model saved to: {model_file}")

            return best_fit
        else:
            print("   ❌ Could not fit sinusoidal model")
            return None

    def visualize_patterns(self, x, y):
        """Create comprehensive visualizations"""
        print(f"\n📊 Generating visualizations...")

        fig, axes = plt.subplots(2, 2, figsize=(18, 12))

        # Plot 1: Raw data with moving average
        ax1 = axes[0, 0]
        colors = ['red' if val == 0 else 'green' for val in y]
        ax1.scatter(x, y, alpha=0.3, s=10, c=colors)

        # Moving average
        window = min(30, len(y) // 5)
        if window > 1:
            y_ma = np.convolve(y, np.ones(window)/window, mode='valid')
            x_ma = x[:len(y_ma)]
            ax1.plot(x_ma, y_ma, 'b-', linewidth=2, label=f'{window}-trip MA')

        # Fitted curve
        y_smooth = np.convolve(y, np.ones(min(20, len(y)//5))/min(20, len(y)//5), mode='valid')
        x_smooth = x[:len(y_smooth)]

        try:
            for initial_period in [200]:  # Focus on period 200 as suspected
                popt, _ = curve_fit(
                    self.sinusoidal_model,
                    x_smooth, y_smooth,
                    p0=[0.3, initial_period, 0, 0.5],
                    bounds=([-1, 30, -2*np.pi, 0], [1, 500, 2*np.pi, 1]),
                    maxfev=20000
                )

                x_pred = np.linspace(x[0], x[-1], 1000)
                y_pred = self.sinusoidal_model(x_pred, *popt)
                ax1.plot(x_pred, y_pred, 'purple', linewidth=2.5,
                        label=f'Sin(T={popt[1]:.0f})', linestyle='--')
                break
        except:
            pass

        ax1.set_xlabel('Trip Number', fontsize=12)
        ax1.set_ylabel('Survived (1) / Lost (0)', fontsize=12)
        ax1.set_title(f'{self.planet_names[self.planet]} - {self.morty_count} Morty(s)\n{len(self.all_trips)} total trips',
                     fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        # Plot 2: Histogram of outcomes over time bins
        ax2 = axes[0, 1]
        bin_size = 50
        bins = np.arange(0, max(x) + bin_size, bin_size)
        survival_by_bin = []

        for i in range(len(bins) - 1):
            mask = (x >= bins[i]) & (x < bins[i+1])
            if np.sum(mask) > 0:
                survival_by_bin.append(np.mean(y[mask]))
            else:
                survival_by_bin.append(np.nan)

        bin_centers = bins[:-1] + bin_size / 2
        ax2.plot(bin_centers, survival_by_bin, 'o-', linewidth=2, markersize=6)
        ax2.set_xlabel('Trip Number (binned)', fontsize=12)
        ax2.set_ylabel('Survival Rate', fontsize=12)
        ax2.set_title(f'Survival Rate Over Time (bins of {bin_size})', fontsize=14)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(-0.1, 1.1)

        # Plot 3: FFT Spectrum
        ax3 = axes[1, 0]
        n = len(y)
        yf = fft(y - np.mean(y))
        xf = fftfreq(n, 1.0)[:n//2]
        magnitude = 2.0/n * np.abs(yf[0:n//2])

        ax3.plot(xf, magnitude)
        ax3.set_xlabel('Frequency (1/trips)', fontsize=12)
        ax3.set_ylabel('Magnitude', fontsize=12)
        ax3.set_title('Frequency Spectrum (FFT)', fontsize=14)
        ax3.grid(True, alpha=0.3)
        ax3.set_xlim(0, 0.05)  # Focus on low frequencies

        # Plot 4: Episode comparison
        ax4 = axes[1, 1]
        if len(self.episode_results) > 1:
            episode_nums = [r['episode'] for r in self.episode_results]
            rates = [r['survival_rate'] for r in self.episode_results]

            ax4.plot(episode_nums, rates, 'o-', linewidth=2, markersize=8)
            ax4.axhline(y=np.mean(rates), color='r', linestyle='--', label=f'Mean: {np.mean(rates):.1%}')
            ax4.set_xlabel('Episode Number', fontsize=12)
            ax4.set_ylabel('Survival Rate', fontsize=12)
            ax4.set_title('Survival Rate Across Episodes', fontsize=14)
            ax4.legend(fontsize=10)
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'Need multiple episodes', ha='center', va='center',
                    transform=ax4.transAxes, fontsize=14)

        plt.tight_layout()

        output_file = f"{self.output_dir}/pattern_P{self.planet}_M{self.morty_count}_analysis.png"
        plt.savefig(output_file, dpi=200, bbox_inches='tight')
        print(f"✅ Visualization saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Discover patterns for a specific planet')
    parser.add_argument('--token', '-t', required=True, help='API token')
    parser.add_argument('--planet', '-p', type=int, required=True, choices=[0, 1, 2],
                       help='Planet to analyze (0, 1, or 2)')
    parser.add_argument('--morty-count', '-m', type=int, default=3, choices=[1, 2, 3],
                       help='Morties per trip (default: 3)')
    parser.add_argument('--episodes', '-e', type=int, default=5,
                       help='Number of episodes to run (default: 5)')
    parser.add_argument('--output', '-o', default='/home/user/aicheckr-site/pattern_discovery',
                       help='Output directory')

    args = parser.parse_args()

    planet_names = ["On a Cob Planet", "Cronenberg World", "Purge Planet"]

    print("🔬 MORTY PATTERN DISCOVERY")
    print("="*60)
    print(f"Planet: {args.planet} ({planet_names[args.planet]})")
    print(f"Group size: {args.morty_count} Morty(s)")
    print(f"Episodes: {args.episodes}")
    print("="*60)

    discoverer = PatternDiscovery(args.token, args.planet, args.morty_count, args.output)
    discoverer.run_discovery(args.episodes)

    print("\n🎉 Pattern discovery complete!")


if __name__ == "__main__":
    main()
