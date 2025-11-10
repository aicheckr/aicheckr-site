#!/usr/bin/env python3
"""
Morty Bulk Simulator - Run thousands of episodes to discover true patterns

This script runs multiple rescue episodes sequentially, aggregating data
across all runs to perform meta-analysis and discover optimal strategies.

Perfect for running overnight to gather massive statistical datasets!
"""

import requests
import json
import numpy as np
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
from datetime import datetime
import os
import pickle
from collections import defaultdict


@dataclass
class EpisodeResult:
    """Results from a single episode"""
    episode_number: int
    morties_saved: int
    morties_lost: int
    steps_taken: int
    success_rate: float
    strategy_used: str
    timestamp: str
    trip_history: List[Dict]


class BulkSimulator:
    """Runs multiple episodes and aggregates data"""

    BASE_URL = "https://challenge.sphinxhq.com"

    def __init__(self, token: str, output_dir: str = "/home/user/aicheckr-site/bulk_results"):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        self.output_dir = output_dir
        self.episodes_completed = []
        self.aggregate_data = defaultdict(lambda: defaultdict(list))

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Load previous progress if exists
        self.progress_file = f"{output_dir}/bulk_progress.pkl"
        self.load_progress()

    def load_progress(self):
        """Load previous simulation progress"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'rb') as f:
                    data = pickle.load(f)
                    self.episodes_completed = data.get('episodes', [])
                    self.aggregate_data = data.get('aggregate_data', defaultdict(lambda: defaultdict(list)))
                print(f"✅ Loaded progress: {len(self.episodes_completed)} episodes completed")
            except Exception as e:
                print(f"⚠️  Could not load progress: {e}")

    def save_progress(self):
        """Save current progress"""
        try:
            with open(self.progress_file, 'wb') as f:
                pickle.dump({
                    'episodes': self.episodes_completed,
                    'aggregate_data': dict(self.aggregate_data)
                }, f)
        except Exception as e:
            print(f"⚠️  Could not save progress: {e}")

    def start_episode(self) -> bool:
        """Start a new episode"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/mortys/start/",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Failed to start episode: {e}")
            return False

    def send_morties(self, planet: int, morty_count: int) -> Tuple[bool, Dict]:
        """Send Morties through portal"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/api/mortys/portal/",
                headers=self.headers,
                json={"planet": planet, "morty_count": morty_count},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, {}
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False, {}

    def run_single_episode(self, episode_num: int, strategy: str = "adaptive") -> Optional[EpisodeResult]:
        """
        Run a single episode with specified strategy

        Strategies:
        - 'explore_P0': Focus exploration on Planet 0
        - 'explore_P1': Focus exploration on Planet 1
        - 'explore_P2': Focus exploration on Planet 2
        - 'adaptive': Balanced adaptive strategy
        - 'greedy_empirical': Pure greedy based on empirical rates
        """
        print(f"\n{'='*60}")
        print(f"🚀 EPISODE {episode_num} - Strategy: {strategy}")
        print(f"{'='*60}")

        if not self.start_episode():
            return None

        trip_history = []
        planet_trip_counts = [0, 0, 0]
        planet_outcomes = {(p, m): [] for p in range(3) for m in range(1, 4)}

        morties_in_citadel = 1000
        morties_saved = 0
        morties_lost = 0
        steps = 0

        # Strategy implementation
        if strategy.startswith("explore_P"):
            # Focus exploration on a specific planet
            focus_planet = int(strategy[-1])
            trips_taken = 0

            while morties_in_citadel > 0:
                # Cycle through group sizes on the focus planet
                morty_count = ((trips_taken % 3) + 1)

                if morties_in_citadel < morty_count:
                    morty_count = morties_in_citadel

                success, data = self.send_morties(focus_planet, morty_count)

                if not success:
                    break

                survived = data.get('survived', False)
                trip_history.append({
                    'step': steps,
                    'planet': focus_planet,
                    'morty_count': morty_count,
                    'survived': survived,
                    'cumulative_trips_to_planet': planet_trip_counts[focus_planet]
                })

                planet_trip_counts[focus_planet] += 1
                planet_outcomes[(focus_planet, morty_count)].append((planet_trip_counts[focus_planet] - 1, survived))

                morties_in_citadel = data['morties_in_citadel']
                morties_saved = data['morties_on_planet_jessica']
                morties_lost = data['morties_lost']
                steps = data['steps_taken']
                trips_taken += 1

                if trips_taken % 50 == 0:
                    survival_rate = sum(1 for _, s in planet_outcomes[(focus_planet, morty_count)] if s) / len(planet_outcomes[(focus_planet, morty_count)])
                    print(f"  Trip {trips_taken}: Rate={survival_rate:.1%}, Saved={morties_saved}, Lost={morties_lost}, Remaining={morties_in_citadel}")

        elif strategy == "adaptive":
            # Quick exploration then optimization
            exploration_trips = 10

            # Quick exploration
            for planet in range(3):
                for morty_count in range(1, 4):
                    for _ in range(exploration_trips):
                        if morties_in_citadel < morty_count:
                            break

                        success, data = self.send_morties(planet, morty_count)
                        if not success:
                            break

                        survived = data.get('survived', False)
                        trip_history.append({
                            'step': steps,
                            'planet': planet,
                            'morty_count': morty_count,
                            'survived': survived,
                            'cumulative_trips_to_planet': planet_trip_counts[planet]
                        })

                        planet_trip_counts[planet] += 1
                        planet_outcomes[(planet, morty_count)].append((planet_trip_counts[planet] - 1, survived))

                        morties_in_citadel = data['morties_in_citadel']
                        morties_saved = data['morties_on_planet_jessica']
                        morties_lost = data['morties_lost']
                        steps = data['steps_taken']

            # Optimization phase
            while morties_in_citadel > 0:
                best_ev = -1
                best_action = None

                for planet in range(3):
                    for morty_count in range(1, min(4, morties_in_citadel + 1)):
                        outcomes = planet_outcomes[(planet, morty_count)]
                        if len(outcomes) == 0:
                            prob = 0.5
                        else:
                            prob = sum(1 for _, s in outcomes if s) / len(outcomes)

                        ev = prob * morty_count
                        if ev > best_ev:
                            best_ev = ev
                            best_action = (planet, morty_count)

                if best_action is None:
                    break

                planet, morty_count = best_action
                success, data = self.send_morties(planet, morty_count)

                if not success:
                    break

                survived = data.get('survived', False)
                trip_history.append({
                    'step': steps,
                    'planet': planet,
                    'morty_count': morty_count,
                    'survived': survived,
                    'cumulative_trips_to_planet': planet_trip_counts[planet]
                })

                planet_trip_counts[planet] += 1
                planet_outcomes[(planet, morty_count)].append((planet_trip_counts[planet] - 1, survived))

                morties_in_citadel = data['morties_in_citadel']
                morties_saved = data['morties_on_planet_jessica']
                morties_lost = data['morties_lost']
                steps = data['steps_taken']

        print(f"✅ Episode {episode_num} complete: {morties_saved} saved, {morties_lost} lost ({morties_saved/10:.1f}%)")

        result = EpisodeResult(
            episode_number=episode_num,
            morties_saved=morties_saved,
            morties_lost=morties_lost,
            steps_taken=steps,
            success_rate=morties_saved / 1000.0,
            strategy_used=strategy,
            timestamp=datetime.now().isoformat(),
            trip_history=trip_history
        )

        return result

    def run_bulk_simulation(self, num_episodes: int, strategy: str = "adaptive",
                           delay_between_episodes: float = 1.0):
        """
        Run multiple episodes

        Args:
            num_episodes: Number of episodes to run
            strategy: Strategy to use for all episodes
            delay_between_episodes: Seconds to wait between episodes (be nice to API)
        """
        print(f"\n{'='*60}")
        print(f"🎯 BULK SIMULATION: {num_episodes} EPISODES")
        print(f"Strategy: {strategy}")
        print(f"{'='*60}\n")

        start_episode = len(self.episodes_completed) + 1

        for i in range(start_episode, start_episode + num_episodes):
            print(f"\n[Episode {i}/{start_episode + num_episodes - 1}]")

            try:
                result = self.run_single_episode(i, strategy)

                if result is None:
                    print(f"⚠️  Episode {i} failed, skipping...")
                    continue

                self.episodes_completed.append(result)

                # Aggregate trip data
                for trip in result.trip_history:
                    key = (trip['planet'], trip['morty_count'])
                    self.aggregate_data[key]['trips'].append(trip['cumulative_trips_to_planet'])
                    self.aggregate_data[key]['survived'].append(1 if trip['survived'] else 0)

                # Save progress after each episode
                self.save_progress()

                # Save individual episode result
                episode_file = f"{self.output_dir}/episode_{i:04d}.json"
                with open(episode_file, 'w') as f:
                    json.dump(asdict(result), f, indent=2)

                # Brief summary
                print(f"\n📊 Running Statistics (after {i} episodes):")
                avg_saved = np.mean([e.morties_saved for e in self.episodes_completed])
                best_saved = max([e.morties_saved for e in self.episodes_completed])
                print(f"   Average saved: {avg_saved:.1f}")
                print(f"   Best saved: {best_saved}")
                print(f"   Average success rate: {avg_saved/10:.1f}%")

            except KeyboardInterrupt:
                print(f"\n⚠️  Interrupted by user. Progress saved.")
                break
            except Exception as e:
                print(f"❌ Episode {i} error: {e}")
                continue

            # Delay before next episode
            if i < start_episode + num_episodes - 1:
                time.sleep(delay_between_episodes)

        print(f"\n{'='*60}")
        print(f"🏁 BULK SIMULATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total episodes: {len(self.episodes_completed)}")

        self.generate_meta_analysis()

    def generate_meta_analysis(self):
        """Generate comprehensive analysis across all episodes"""
        if len(self.episodes_completed) == 0:
            print("⚠️  No episodes to analyze")
            return

        print(f"\n{'='*60}")
        print(f"📊 META-ANALYSIS: {len(self.episodes_completed)} EPISODES")
        print(f"{'='*60}\n")

        # Overall statistics
        saved_counts = [e.morties_saved for e in self.episodes_completed]

        print("📈 Overall Performance:")
        print(f"   Episodes run: {len(self.episodes_completed)}")
        print(f"   Average saved: {np.mean(saved_counts):.1f} ± {np.std(saved_counts):.1f}")
        print(f"   Median saved: {np.median(saved_counts):.1f}")
        print(f"   Best episode: {np.max(saved_counts)}")
        print(f"   Worst episode: {np.min(saved_counts)}")
        print(f"   Success rate range: {np.min(saved_counts)/10:.1f}% - {np.max(saved_counts)/10:.1f}%")

        # Per-planet analysis
        print(f"\n🌍 Per-Planet Analysis:")
        planet_names = ["On a Cob", "Cronenberg", "Purge"]

        for planet in range(3):
            print(f"\n  Planet {planet} ({planet_names[planet]}):")

            for morty_count in range(1, 4):
                key = (planet, morty_count)
                if key not in self.aggregate_data or len(self.aggregate_data[key]['survived']) == 0:
                    print(f"    {morty_count} Morty(s): No data")
                    continue

                survived = self.aggregate_data[key]['survived']
                avg_survival = np.mean(survived)
                total_trips = len(survived)

                print(f"    {morty_count} Morty(s): {avg_survival:.1%} survival ({total_trips} trips total)")

        # Save comprehensive results
        summary_file = f"{self.output_dir}/meta_analysis_summary.json"
        summary = {
            'total_episodes': len(self.episodes_completed),
            'statistics': {
                'mean_saved': float(np.mean(saved_counts)),
                'std_saved': float(np.std(saved_counts)),
                'median_saved': float(np.median(saved_counts)),
                'min_saved': int(np.min(saved_counts)),
                'max_saved': int(np.max(saved_counts))
            },
            'planet_analysis': {}
        }

        for planet in range(3):
            summary['planet_analysis'][f'planet_{planet}'] = {}
            for morty_count in range(1, 4):
                key = (planet, morty_count)
                if key in self.aggregate_data and len(self.aggregate_data[key]['survived']) > 0:
                    survived = self.aggregate_data[key]['survived']
                    summary['planet_analysis'][f'planet_{planet}'][f'{morty_count}_morties'] = {
                        'survival_rate': float(np.mean(survived)),
                        'total_trips': len(survived),
                        'std': float(np.std(survived))
                    }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n💾 Meta-analysis saved to: {summary_file}")

        # Generate visualizations
        self.visualize_bulk_results()

    def visualize_bulk_results(self):
        """Create visualizations of bulk simulation results"""
        print("\n📊 Generating visualizations...")

        # Figure 1: Episode scores over time
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Scores over episodes
        ax1 = axes[0, 0]
        episode_nums = [e.episode_number for e in self.episodes_completed]
        scores = [e.morties_saved for e in self.episodes_completed]

        ax1.plot(episode_nums, scores, 'b-', alpha=0.6, linewidth=1)
        ax1.axhline(y=np.mean(scores), color='r', linestyle='--', label=f'Mean: {np.mean(scores):.1f}')
        ax1.set_xlabel('Episode Number')
        ax1.set_ylabel('Morties Saved')
        ax1.set_title(f'Performance Across {len(self.episodes_completed)} Episodes')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Distribution of scores
        ax2 = axes[0, 1]
        ax2.hist(scores, bins=30, color='green', alpha=0.7, edgecolor='black')
        ax2.axvline(x=np.mean(scores), color='r', linestyle='--', linewidth=2, label=f'Mean: {np.mean(scores):.1f}')
        ax2.axvline(x=np.median(scores), color='orange', linestyle='--', linewidth=2, label=f'Median: {np.median(scores):.1f}')
        ax2.set_xlabel('Morties Saved')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Distribution of Episode Scores')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        # Plot 3: Planet survival rates
        ax3 = axes[1, 0]
        planet_names = ["On a Cob", "Cronenberg", "Purge"]

        for planet in range(3):
            all_rates = []
            for morty_count in range(1, 4):
                key = (planet, morty_count)
                if key in self.aggregate_data and len(self.aggregate_data[key]['survived']) > 0:
                    rate = np.mean(self.aggregate_data[key]['survived'])
                    all_rates.append(rate)

            if all_rates:
                avg_rate = np.mean(all_rates)
                ax3.bar(planet, avg_rate, alpha=0.7, label=planet_names[planet])

        ax3.set_xlabel('Planet')
        ax3.set_ylabel('Average Survival Rate')
        ax3.set_title('Average Survival Rate by Planet')
        ax3.set_xticks(range(3))
        ax3.set_xticklabels(planet_names)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')

        # Plot 4: Success rate by group size
        ax4 = axes[1, 1]
        group_sizes = [1, 2, 3]
        avg_rates = []

        for morty_count in group_sizes:
            all_rates = []
            for planet in range(3):
                key = (planet, morty_count)
                if key in self.aggregate_data and len(self.aggregate_data[key]['survived']) > 0:
                    rate = np.mean(self.aggregate_data[key]['survived'])
                    all_rates.append(rate)

            if all_rates:
                avg_rates.append(np.mean(all_rates))
            else:
                avg_rates.append(0)

        ax4.bar(group_sizes, avg_rates, color=['#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.7)
        ax4.set_xlabel('Group Size (Morties)')
        ax4.set_ylabel('Average Survival Rate')
        ax4.set_title('Survival Rate by Group Size')
        ax4.set_xticks(group_sizes)
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        output_file = f"{self.output_dir}/bulk_simulation_analysis.png"
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"✅ Bulk analysis visualization saved to: {output_file}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Run bulk Morty rescue simulations')
    parser.add_argument('--token', '-t', required=True, help='API token')
    parser.add_argument('--episodes', '-e', type=int, default=10, help='Number of episodes to run')
    parser.add_argument('--strategy', '-s', default='adaptive',
                       choices=['adaptive', 'explore_P0', 'explore_P1', 'explore_P2'],
                       help='Strategy to use')
    parser.add_argument('--delay', '-d', type=float, default=1.0,
                       help='Delay between episodes (seconds)')
    parser.add_argument('--output', '-o', default='/home/user/aicheckr-site/bulk_results',
                       help='Output directory')

    args = parser.parse_args()

    print("🛸 MORTY BULK SIMULATOR")
    print("="*60)
    print(f"Episodes to run: {args.episodes}")
    print(f"Strategy: {args.strategy}")
    print(f"Output directory: {args.output}")
    print("="*60)

    simulator = BulkSimulator(args.token, args.output)
    simulator.run_bulk_simulation(args.episodes, args.strategy, args.delay)

    print("\n🎉 ALL DONE! Check the output directory for results.")


if __name__ == "__main__":
    main()
