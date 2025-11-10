#!/usr/bin/env python3
"""
Morty Rescue Script - Save the Morties from the Council of Ricks!

This script interacts with the Sphinx HQ API to optimize Morty rescue through
portal travel, adapting to changing survival rates across different planets.
"""

import requests
import json
import numpy as np
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os


@dataclass
class GameState:
    """Tracks the current state of the rescue mission"""
    morties_in_citadel: int
    morties_on_planet_jessica: int
    morties_lost: int
    steps_taken: int
    status_message: str


@dataclass
class TripResult:
    """Records the outcome of a single portal trip"""
    step: int
    planet: int
    morty_count: int
    survived: bool
    cumulative_trips_to_planet: int


class MortyRescueAPI:
    """API client for the Morty Rescue challenge"""

    BASE_URL = "https://challenge.sphinxhq.com"

    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        self.trip_history: List[TripResult] = []
        self.planet_trip_counts = [0, 0, 0]  # Track trips per planet

    def start_episode(self) -> GameState:
        """Initialize a new rescue episode"""
        response = requests.post(
            f"{self.BASE_URL}/api/mortys/start/",
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        return GameState(**data)

    def send_morties(self, planet: int, morty_count: int) -> Tuple[bool, GameState]:
        """
        Send Morties through a portal

        Args:
            planet: 0 (On a Cob), 1 (Cronenberg), or 2 (Purge Planet)
            morty_count: 1, 2, or 3 Morties

        Returns:
            Tuple of (survived, GameState)
        """
        response = requests.post(
            f"{self.BASE_URL}/api/mortys/portal/",
            headers=self.headers,
            json={"planet": planet, "morty_count": morty_count}
        )
        response.raise_for_status()
        data = response.json()

        survived = data.get("survived", False)
        state = GameState(
            morties_in_citadel=data["morties_in_citadel"],
            morties_on_planet_jessica=data["morties_on_planet_jessica"],
            morties_lost=data["morties_lost"],
            steps_taken=data["steps_taken"],
            status_message=data.get("status_message", "")
        )

        # Record this trip
        trip = TripResult(
            step=state.steps_taken,
            planet=planet,
            morty_count=morty_count,
            survived=survived,
            cumulative_trips_to_planet=self.planet_trip_counts[planet]
        )
        self.trip_history.append(trip)
        self.planet_trip_counts[planet] += 1

        return survived, state

    def get_status(self) -> GameState:
        """Get current episode status"""
        response = requests.get(
            f"{self.BASE_URL}/api/mortys/status/",
            headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        return GameState(**data)


class PatternAnalyzer:
    """Analyzes survival patterns for each planet and group size"""

    def __init__(self):
        # Store outcomes for each (planet, morty_count) combination
        self.outcomes: Dict[Tuple[int, int], List[Tuple[int, bool]]] = {
            (p, m): [] for p in range(3) for m in range(1, 4)
        }

    def record_outcome(self, planet: int, morty_count: int, trip_num: int, survived: bool):
        """Record the outcome of a trip"""
        key = (planet, morty_count)
        self.outcomes[key].append((trip_num, survived))

    def sinusoidal_model(self, x, amplitude, period, phase, offset):
        """Sinusoidal model for survival probability"""
        return offset + amplitude * np.sin(2 * np.pi * x / period + phase)

    def analyze_planet_pattern(self, planet: int, morty_count: int) -> Optional[Dict]:
        """
        Analyze the survival pattern for a specific planet and group size

        Returns:
            Dictionary with pattern parameters if detected, None otherwise
        """
        key = (planet, morty_count)
        data = self.outcomes[key]

        if len(data) < 20:  # Need enough data points
            return None

        trips = np.array([d[0] for d in data])
        survived = np.array([1.0 if d[1] else 0.0 for d in data])

        # Try to fit a sinusoidal pattern
        try:
            # Initial guess based on user's finding for planet 2
            if planet == 2:
                initial_period = 200
            else:
                initial_period = 100

            # Use a rolling average to smooth the data for fitting
            window = min(20, len(survived) // 3)
            if window > 1:
                survived_smooth = np.convolve(survived, np.ones(window)/window, mode='valid')
                trips_smooth = trips[:len(survived_smooth)]
            else:
                survived_smooth = survived
                trips_smooth = trips

            # Fit sinusoidal model
            popt, _ = curve_fit(
                self.sinusoidal_model,
                trips_smooth,
                survived_smooth,
                p0=[0.3, initial_period, 0, 0.5],
                bounds=([-1, 50, -2*np.pi, 0], [1, 400, 2*np.pi, 1]),
                maxfev=10000
            )

            amplitude, period, phase, offset = popt

            return {
                'type': 'sinusoidal',
                'amplitude': amplitude,
                'period': period,
                'phase': phase,
                'offset': offset,
                'model': lambda x: self.sinusoidal_model(x, *popt)
            }
        except:
            # If fitting fails, return simple average
            return {
                'type': 'average',
                'probability': np.mean(survived)
            }

    def predict_survival_probability(self, planet: int, morty_count: int, trip_num: int) -> float:
        """Predict the survival probability for a given trip"""
        pattern = self.analyze_planet_pattern(planet, morty_count)

        if pattern is None:
            # Not enough data, use empirical average
            key = (planet, morty_count)
            data = self.outcomes[key]
            if len(data) == 0:
                return 0.5  # Default guess
            survived_count = sum(1 for _, s in data if s)
            return survived_count / len(data)

        if pattern['type'] == 'sinusoidal':
            prob = pattern['model'](trip_num)
            return np.clip(prob, 0, 1)  # Ensure probability is in [0, 1]
        else:
            return pattern['probability']

    def get_survival_rate(self, planet: int, morty_count: int) -> float:
        """Get empirical survival rate for a planet/group combination"""
        key = (planet, morty_count)
        data = self.outcomes[key]
        if len(data) == 0:
            return 0.5
        survived_count = sum(1 for _, s in data if s)
        return survived_count / len(data)


class MortyRescueStrategy:
    """Implements the rescue strategy"""

    def __init__(self, api: MortyRescueAPI, analyzer: PatternAnalyzer):
        self.api = api
        self.analyzer = analyzer
        self.exploration_trips_per_combo = 30  # Trips per (planet, morty_count) during exploration

    def exploration_phase(self, state: GameState) -> GameState:
        """
        Exploration phase: gather data on all planets and group sizes
        """
        print("\n🔬 EXPLORATION PHASE STARTED")
        print("=" * 60)

        # Test each combination systematically
        combinations = [
            (p, m) for p in range(3) for m in range(1, 4)
        ]

        for planet, morty_count in combinations:
            planet_names = ["On a Cob Planet", "Cronenberg World", "Purge Planet"]
            print(f"\n📡 Exploring Planet {planet} ({planet_names[planet]}) with {morty_count} Morty(s)")

            trips_done = 0
            while trips_done < self.exploration_trips_per_combo and state.morties_in_citadel >= morty_count:
                actual_count = min(morty_count, state.morties_in_citadel)
                survived, state = self.api.send_morties(planet, actual_count)

                trip_num = self.api.planet_trip_counts[planet] - 1
                self.analyzer.record_outcome(planet, actual_count, trip_num, survived)

                trips_done += 1

                if trips_done % 10 == 0:
                    rate = self.analyzer.get_survival_rate(planet, morty_count)
                    print(f"  Trip {trips_done}/{self.exploration_trips_per_combo}: "
                          f"Survival rate = {rate:.2%}, "
                          f"Citadel: {state.morties_in_citadel}, "
                          f"Jessica: {state.morties_on_planet_jessica}, "
                          f"Lost: {state.morties_lost}")

            if state.morties_in_citadel < morty_count:
                print(f"⚠️  Not enough Morties left to continue exploration")
                break

        print("\n✅ Exploration phase complete!")
        print(f"📊 Morties on Planet Jessica: {state.morties_on_planet_jessica}")
        print(f"💀 Morties lost: {state.morties_lost}")
        print(f"🏰 Morties in Citadel: {state.morties_in_citadel}")

        return state

    def optimization_phase(self, state: GameState) -> GameState:
        """
        Optimization phase: use learned patterns to maximize survival
        """
        print("\n🎯 OPTIMIZATION PHASE STARTED")
        print("=" * 60)

        step_count = 0
        while state.morties_in_citadel > 0:
            # Evaluate all possible actions
            best_score = -1
            best_action = None

            for planet in range(3):
                for morty_count in range(1, 4):
                    if state.morties_in_citadel < morty_count:
                        continue

                    # Predict probability for this trip
                    trip_num = self.api.planet_trip_counts[planet]
                    prob = self.analyzer.predict_survival_probability(planet, morty_count, trip_num)

                    # Expected value: probability * number of morties
                    expected_value = prob * morty_count

                    if expected_value > best_score:
                        best_score = expected_value
                        best_action = (planet, morty_count, prob)

            if best_action is None:
                break

            planet, morty_count, predicted_prob = best_action

            # Execute the best action
            actual_count = min(morty_count, state.morties_in_citadel)
            survived, state = self.api.send_morties(planet, actual_count)

            trip_num = self.api.planet_trip_counts[planet] - 1
            self.analyzer.record_outcome(planet, actual_count, trip_num, survived)

            step_count += 1
            if step_count % 20 == 0:
                print(f"Step {step_count}: Planet {planet}, {actual_count} Morty(s), "
                      f"Predicted: {predicted_prob:.2%}, Survived: {survived}, "
                      f"Citadel: {state.morties_in_citadel}, "
                      f"Jessica: {state.morties_on_planet_jessica}, "
                      f"Lost: {state.morties_lost}")

        print("\n🎉 OPTIMIZATION PHASE COMPLETE!")
        print(f"📊 Final score - Morties on Planet Jessica: {state.morties_on_planet_jessica}")
        print(f"💀 Morties lost: {state.morties_lost}")

        return state

    def adaptive_strategy(self, state: GameState) -> GameState:
        """
        Combined strategy with shorter exploration and continuous adaptation
        """
        print("\n🚀 ADAPTIVE RESCUE STRATEGY")
        print("=" * 60)

        # Quick initial exploration (fewer trips per combination)
        initial_exploration = 15
        combinations = [(p, m) for p in range(3) for m in range(1, 4)]

        print("\n🔬 Quick exploration of all routes...")
        for planet, morty_count in combinations:
            for _ in range(min(initial_exploration, state.morties_in_citadel // morty_count)):
                if state.morties_in_citadel < morty_count:
                    break

                actual_count = min(morty_count, state.morties_in_citadel)
                survived, state = self.api.send_morties(planet, actual_count)
                trip_num = self.api.planet_trip_counts[planet] - 1
                self.analyzer.record_outcome(planet, actual_count, trip_num, survived)

        print(f"✅ Initial exploration complete. Status: Citadel={state.morties_in_citadel}, "
              f"Jessica={state.morties_on_planet_jessica}, Lost={state.morties_lost}")

        # Now exploit with continuous learning
        print("\n🎯 Adaptive exploitation phase...")
        step = 0
        while state.morties_in_citadel > 0:
            # Find the best action based on current predictions
            best_ev = -1
            best_action = None

            for planet in range(3):
                for morty_count in range(1, min(4, state.morties_in_citadel + 1)):
                    trip_num = self.api.planet_trip_counts[planet]
                    prob = self.analyzer.predict_survival_probability(planet, morty_count, trip_num)
                    ev = prob * morty_count

                    if ev > best_ev:
                        best_ev = ev
                        best_action = (planet, morty_count, prob, ev)

            if best_action is None:
                break

            planet, morty_count, prob, ev = best_action
            actual_count = min(morty_count, state.morties_in_citadel)
            survived, state = self.api.send_morties(planet, actual_count)

            trip_num = self.api.planet_trip_counts[planet] - 1
            self.analyzer.record_outcome(planet, actual_count, trip_num, survived)

            step += 1
            if step % 50 == 0 or state.morties_in_citadel < 10:
                print(f"Step {step}: P{planet}, {actual_count}M, EV={ev:.2f}, Survived={survived}, "
                      f"Citadel={state.morties_in_citadel}, Jessica={state.morties_on_planet_jessica}")

        return state


def visualize_results(api: MortyRescueAPI, analyzer: PatternAnalyzer):
    """Create visualization of the rescue mission results"""
    print("\n📊 Generating visualizations...")

    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    planet_names = ["On a Cob Planet", "Cronenberg World", "Purge Planet"]

    for planet in range(3):
        for morty_count in range(1, 4):
            ax = axes[planet][morty_count - 1]

            key = (planet, morty_count)
            data = analyzer.outcomes[key]

            if len(data) == 0:
                ax.text(0.5, 0.5, 'No Data', ha='center', va='center', transform=ax.transAxes)
                ax.set_title(f"{planet_names[planet]}\n{morty_count} Morty(s)")
                continue

            trips = [d[0] for d in data]
            survived = [1 if d[1] else 0 for d in data]

            # Plot raw data
            ax.scatter(trips, survived, alpha=0.3, s=10, label='Actual', color='blue')

            # Plot moving average
            window = min(20, len(survived) // 3)
            if window > 1 and len(survived) >= window:
                survived_ma = np.convolve(survived, np.ones(window)/window, mode='valid')
                trips_ma = trips[:len(survived_ma)]
                ax.plot(trips_ma, survived_ma, 'r-', linewidth=2, label=f'{window}-trip MA')

            # Plot fitted pattern if available
            pattern = analyzer.analyze_planet_pattern(planet, morty_count)
            if pattern and pattern['type'] == 'sinusoidal':
                x_range = np.linspace(min(trips), max(trips), 200)
                y_pred = [pattern['model'](x) for x in x_range]
                ax.plot(x_range, y_pred, 'g--', linewidth=2,
                       label=f"Sin fit (T={pattern['period']:.1f})")

            survival_rate = sum(survived) / len(survived)
            ax.axhline(y=survival_rate, color='orange', linestyle=':',
                      label=f'Avg={survival_rate:.2%}')

            ax.set_title(f"{planet_names[planet]}\n{morty_count} Morty(s) - Rate: {survival_rate:.1%}")
            ax.set_xlabel('Trip Number')
            ax.set_ylabel('Survived (1) / Lost (0)')
            ax.set_ylim(-0.1, 1.1)
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save the plot
    output_file = '/home/user/aicheckr-site/morty_rescue_analysis.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Visualization saved to: {output_file}")

    # Create a summary plot
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Cumulative progress
    steps = [t.step for t in api.trip_history]
    cumulative_saved = []
    cumulative_lost = []
    current_saved = 0
    current_lost = 0

    for trip in api.trip_history:
        if trip.survived:
            current_saved += trip.morty_count
        else:
            current_lost += trip.morty_count
        cumulative_saved.append(current_saved)
        cumulative_lost.append(current_lost)

    ax1.plot(steps, cumulative_saved, 'g-', linewidth=2, label='Morties Saved')
    ax1.plot(steps, cumulative_lost, 'r-', linewidth=2, label='Morties Lost')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Cumulative Morties')
    ax1.set_title('Rescue Mission Progress')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Planet usage
    planet_usage = {0: 0, 1: 0, 2: 0}
    for trip in api.trip_history:
        planet_usage[trip.planet] += trip.morty_count

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    ax2.bar([planet_names[i] for i in range(3)],
           [planet_usage[i] for i in range(3)],
           color=colors)
    ax2.set_ylabel('Total Morties Sent')
    ax2.set_title('Planet Usage Distribution')
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file2 = '/home/user/aicheckr-site/morty_rescue_summary.png'
    plt.savefig(output_file2, dpi=150, bbox_inches='tight')
    print(f"✅ Summary visualization saved to: {output_file2}")


def main():
    """Main execution function"""
    print("=" * 60)
    print("🛸 MORTY RESCUE MISSION - WUBBA LUBBA DUB DUB! 🛸")
    print("=" * 60)

    # Get API token from environment variable
    token = os.environ.get('MORTY_API_TOKEN')
    if not token:
        print("\n⚠️  API token not found in environment variable MORTY_API_TOKEN")
        token = input("Please enter your API token: ").strip()

    # Initialize components
    api = MortyRescueAPI(token)
    analyzer = PatternAnalyzer()
    strategy = MortyRescueStrategy(api, analyzer)

    # Start the episode
    print("\n🎬 Starting new rescue episode...")
    state = api.start_episode()
    print(f"Initial state: {state.morties_in_citadel} Morties in Citadel")
    print(f"Status: {state.status_message}")

    # Choose strategy
    print("\n🤔 Choose your strategy:")
    print("1. Full Exploration + Optimization (most thorough)")
    print("2. Adaptive Strategy (balanced)")
    print("3. Quick Adaptive (faster, less exploration)")

    choice = input("\nEnter choice (1-3) [default: 2]: ").strip() or "2"

    if choice == "1":
        # Full exploration phase
        state = strategy.exploration_phase(state)

        # Optimization phase
        if state.morties_in_citadel > 0:
            state = strategy.optimization_phase(state)
    elif choice == "3":
        # Quick adaptive with minimal exploration
        strategy.exploration_trips_per_combo = 10
        state = strategy.adaptive_strategy(state)
    else:
        # Default: balanced adaptive strategy
        state = strategy.adaptive_strategy(state)

    # Final results
    print("\n" + "=" * 60)
    print("🏁 MISSION COMPLETE!")
    print("=" * 60)
    final_state = api.get_status()
    print(f"\n📊 FINAL SCORE: {final_state.morties_on_planet_jessica} Morties saved! 🎉")
    print(f"💀 Morties lost: {final_state.morties_lost}")
    print(f"🏰 Morties remaining in Citadel: {final_state.morties_in_citadel}")
    print(f"📈 Total steps taken: {final_state.steps_taken}")
    print(f"✅ Success rate: {final_state.morties_on_planet_jessica / 1000 * 100:.1f}%")
    print(f"\n{final_state.status_message}")

    # Generate visualizations
    try:
        visualize_results(api, analyzer)
    except Exception as e:
        print(f"⚠️  Visualization failed: {e}")
        print("Continuing without visualizations...")

    # Save results to file
    results_file = '/home/user/aicheckr-site/morty_rescue_results.json'
    results = {
        'final_score': final_state.morties_on_planet_jessica,
        'morties_lost': final_state.morties_lost,
        'steps_taken': final_state.steps_taken,
        'success_rate': final_state.morties_on_planet_jessica / 1000,
        'trip_history': [
            {
                'step': t.step,
                'planet': t.planet,
                'morty_count': t.morty_count,
                'survived': t.survived,
                'cumulative_trips': t.cumulative_trips_to_planet
            }
            for t in api.trip_history
        ]
    }

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {results_file}")

    print("\n🚀 Good luck with the challenge, Morty! Don't screw it up! 🚀")


if __name__ == "__main__":
    main()
