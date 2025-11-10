# 🚀 Morty Rescue - Mass Simulation Guide

## Strategy: Run Thousands of Simulations to Crack the Patterns

This guide shows you how to run **thousands** of rescue episodes to gather massive amounts of data and discover the true mathematical patterns behind each planet's survival rates.

---

## 📋 Prerequisites

1. **Python 3.7+** installed
2. **Valid API token** from Sphinx HQ
3. **Dependencies** installed (requests, numpy, matplotlib, scipy)

---

## 🎯 Quick Start: Complete Step-by-Step Terminal Guide

### Step 1: Clone and Setup

```bash
# Navigate to the project directory
cd /path/to/aicheckr-site

# Or clone if you haven't yet
git clone https://github.com/aicheckr/aicheckr-site.git
cd aicheckr-site

# Pull the latest changes with the simulation scripts
git pull origin claude/morty-rescue-api-optimization-011CUyHdZqyWk3QoPYDtzMGU
```

### Step 2: Install Dependencies

```bash
# Install required Python packages
pip install requests numpy matplotlib scipy

# Or use requirements.txt
pip install -r requirements.txt
```

### Step 3: Get Your API Token

```bash
# Request a token (you'll need to provide your info)
python morty_api_helper.py --request-token --name "Pinesito" --email "nassimbscasa@gmail.com"

# Check your email for the token
# Then set it as an environment variable
export MORTY_API_TOKEN="your_token_here"
```

### Step 4: Test Your Connection

```bash
# Verify your token works
python morty_api_helper.py --test

# Should output:
# ✅ API connection successful!
```

---

## 🔬 Strategy 1: Focused Pattern Discovery (Recommended for Initial Research)

**Goal:** Discover the exact sinusoidal pattern for a specific planet and group size.

### Planet 2 Deep Dive (Your Finding: Period ~200)

```bash
# Run 10 episodes focusing ONLY on Planet 2 with 3 Morties
python morty_pattern_discovery.py \
  --token $MORTY_API_TOKEN \
  --planet 2 \
  --morty-count 3 \
  --episodes 10 \
  --output pattern_discovery

# This will:
# - Run 10 full episodes (10,000 Morties total)
# - Send ALL Morties to Planet 2 in groups of 3
# - Gather ~3,333 data points
# - Perform FFT analysis to detect period
# - Fit sinusoidal model
# - Generate detailed visualizations
```

**Expected Output:**
- `pattern_discovery/discovery_P2_M3_progress.json` - All trip data
- `pattern_discovery/model_P2_M3.json` - Fitted mathematical model
- `pattern_discovery/pattern_P2_M3_analysis.png` - Visualizations

### Run All Combinations for Complete Picture

```bash
# Planet 0, 1 Morty at a time (quick test)
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 0 -m 1 -e 5

# Planet 0, 2 Morties
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 0 -m 2 -e 5

# Planet 0, 3 Morties
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 0 -m 3 -e 5

# Planet 1, all group sizes
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 1 -m 1 -e 5
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 1 -m 2 -e 5
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 1 -m 3 -e 5

# Planet 2, all group sizes (to compare curves)
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 2 -m 1 -e 10
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 2 -m 2 -e 10
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 2 -m 3 -e 10
```

---

## 🎲 Strategy 2: Bulk Adaptive Simulations

**Goal:** Run hundreds of adaptive episodes to test overall strategy effectiveness.

### Run 100 Adaptive Episodes

```bash
# Run 100 episodes using the adaptive strategy
python morty_bulk_simulator.py \
  --token $MORTY_API_TOKEN \
  --episodes 100 \
  --strategy adaptive \
  --delay 1.0 \
  --output bulk_results

# This will:
# - Run 100 complete episodes
# - Use adaptive strategy (learns patterns on-the-fly)
# - Save progress after each episode
# - Generate meta-analysis
# - Take ~2-3 hours (with 1 second delay between episodes)
```

**Expected Output:**
- `bulk_results/episode_0001.json` through `episode_0100.json`
- `bulk_results/meta_analysis_summary.json` - Statistics across all episodes
- `bulk_results/bulk_simulation_analysis.png` - Visualizations
- `bulk_results/bulk_progress.pkl` - Resumable progress

### Resume Interrupted Simulation

```bash
# If interrupted, just run again - it will resume from last episode
python morty_bulk_simulator.py \
  --token $MORTY_API_TOKEN \
  --episodes 100 \
  --strategy adaptive \
  --output bulk_results
```

---

## 🌙 Overnight Mass Simulation (1000+ Episodes)

**Goal:** Run thousands of episodes overnight to gather ultimate dataset.

### Option A: Run 1000 Adaptive Episodes

```bash
# Run overnight (12+ hours)
nohup python morty_bulk_simulator.py \
  --token $MORTY_API_TOKEN \
  --episodes 1000 \
  --strategy adaptive \
  --delay 0.5 \
  --output bulk_results_1000 \
  > simulation.log 2>&1 &

# Check progress
tail -f simulation.log

# Or check the results directory
ls -lh bulk_results_1000/

# Count completed episodes
ls bulk_results_1000/episode_*.json | wc -l
```

### Option B: Planet-Specific Deep Dive (Best for Pattern Discovery)

```bash
# Planet 2, 3 Morties, 100 episodes (ultimate dataset)
nohup python morty_pattern_discovery.py \
  --token $MORTY_API_TOKEN \
  --planet 2 \
  --morty-count 3 \
  --episodes 100 \
  --output planet2_ultimate \
  > planet2.log 2>&1 &

# This will gather ~333,000 data points for Planet 2!
```

---

## 📊 Analyzing Your Results

### After Focused Pattern Discovery

```bash
# View the fitted model parameters
cat pattern_discovery/model_P2_M3.json

# Example output:
# {
#   "planet": 2,
#   "morty_count": 3,
#   "model": "sinusoidal",
#   "parameters": {
#     "amplitude": 0.287,
#     "period": 201.3,
#     "phase": 1.234,
#     "offset": 0.512
#   },
#   "r2_score": 0.856
# }

# View the visualization
open pattern_discovery/pattern_P2_M3_analysis.png
# (or use 'xdg-open' on Linux, 'start' on Windows)
```

### After Bulk Simulation

```bash
# View meta-analysis
cat bulk_results/meta_analysis_summary.json

# View visualizations
open bulk_results/bulk_simulation_analysis.png

# Advanced analysis with pattern analyzer
python morty_pattern_analyzer.py \
  --results bulk_results/episode_0001.json \
  --compare --predict
```

### Aggregate Analysis Across All Focused Runs

```bash
# Create a script to combine all pattern discovery results
# (You can manually inspect each model file or create aggregator)

# View all discovered models
cat pattern_discovery/model_*.json

# Compare periods across different group sizes
grep -A 5 '"period"' pattern_discovery/model_*.json
```

---

## 💡 Pro Tips for Mass Simulation

### 1. **Start Small, Scale Up**
```bash
# First, test with 5 episodes
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 2 -m 3 -e 5

# Verify results look good
cat pattern_discovery/model_P2_M3.json

# Then scale to 50-100
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 2 -m 3 -e 100
```

### 2. **Use Background Jobs for Multiple Planets**
```bash
# Run all 3 planets in parallel (careful with API rate limits!)
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 0 -m 3 -e 20 --output p0_data > p0.log 2>&1 &
sleep 2
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 1 -m 3 -e 20 --output p1_data > p1.log 2>&1 &
sleep 2
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 2 -m 3 -e 20 --output p2_data > p2.log 2>&1 &

# Monitor all jobs
jobs
tail -f p0.log p1.log p2.log
```

### 3. **Check API Rate Limits**
```bash
# If you get rate limit errors, increase delay
python morty_bulk_simulator.py -t $MORTY_API_TOKEN -e 100 --delay 2.0
```

### 4. **Monitor Progress**
```bash
# Watch the number of completed episodes
watch -n 10 'ls bulk_results/episode_*.json | wc -l'

# Or check the log
tail -f simulation.log | grep "Episode.*complete"
```

### 5. **Save Data Incrementally**
The scripts automatically save after each episode, so you can:
- Stop and resume anytime (Ctrl+C)
- Analyze partial results while simulation runs
- Recover from crashes

---

## 🎯 Recommended Workflow for Your Goal

Based on your finding that **Planet 2 has sinusoidal pattern with period ~200**:

### Phase 1: Validate Your Finding (1-2 hours)
```bash
# Deep dive into Planet 2, all group sizes
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 2 -m 1 -e 10 --output validation
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 2 -m 2 -e 10 --output validation
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 2 -m 3 -e 10 --output validation

# Check if period ~200 is consistent across group sizes
grep '"period"' validation/model_*.json
```

### Phase 2: Explore Other Planets (2-3 hours)
```bash
# Discover patterns for Planet 0 and 1
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 0 -m 3 -e 10 --output exploration
python morty_pattern_discovery.py -t $MORTY_API_TOKEN -p 1 -m 3 -e 10 --output exploration
```

### Phase 3: Mass Data Collection (Overnight)
```bash
# Run 100 episodes for each planet/group combo (3x3 = 9 runs)
# This gives you ~1 million total data points!

for planet in 0 1 2; do
  for morties in 1 2 3; do
    nohup python morty_pattern_discovery.py \
      -t $MORTY_API_TOKEN \
      -p $planet \
      -m $morties \
      -e 100 \
      --output ultimate_dataset \
      > "p${planet}_m${morties}.log" 2>&1 &
    sleep 5  # Stagger starts
  done
done

# Check all jobs
jobs

# Monitor all logs
tail -f p*.log
```

### Phase 4: Build Optimal Strategy
```bash
# After gathering data, analyze all patterns
ls ultimate_dataset/model_*.json

# Create optimal strategy based on discovered patterns
# Then test it with bulk simulator
python morty_bulk_simulator.py \
  -t $MORTY_API_TOKEN \
  -e 100 \
  --strategy adaptive \
  --output strategy_test
```

---

## 🏆 Expected Results

After running thousands of simulations, you should discover:

1. **Exact sinusoidal parameters** for each planet/group combination
2. **Optimal timing** for sending Morties (peak phases)
3. **Best planet selection** based on current trip count
4. **Group size optimization** (sometimes 1 Morty at high probability beats 3 at low)

This data will let you build a **perfect strategy** that adapts to the changing survival rates!

---

## 🆘 Troubleshooting

### API Token Issues
```bash
# Test your token
python morty_api_helper.py --test

# Request new token if expired
python morty_api_helper.py --request-token --name "Your Name" --email "your@email.com"
```

### Interrupted Simulations
```bash
# Just run the same command again - it will resume
python morty_bulk_simulator.py -t $MORTY_API_TOKEN -e 100 --output bulk_results
```

### Low Survival Rates
- This is expected during exploration! You're gathering data, not optimizing yet
- Focus pattern discovery runs will have ~50% survival (gathering data from all phases)
- Adaptive strategy should achieve 80-90% after learning

### Out of Memory
```bash
# If processing too much data, run smaller batches
# E.g., 10 episodes at a time instead of 100
```

---

## 📁 File Organization

After running simulations, your directory structure will look like:

```
aicheckr-site/
├── morty_rescue.py                    # Original single-run script
├── morty_bulk_simulator.py            # Bulk adaptive simulation
├── morty_pattern_discovery.py         # Focused pattern discovery
├── morty_pattern_analyzer.py          # Analysis tool
├── morty_api_helper.py                # API utilities
├── requirements.txt                    # Dependencies
├── MORTY_RESCUE_README.md            # Original guide
├── BULK_SIMULATION_GUIDE.md          # This guide
│
├── bulk_results/                      # Adaptive simulation results
│   ├── episode_0001.json
│   ├── episode_0002.json
│   ├── ...
│   ├── meta_analysis_summary.json
│   ├── bulk_simulation_analysis.png
│   └── bulk_progress.pkl
│
├── pattern_discovery/                 # Pattern discovery results
│   ├── model_P0_M1.json              # Planet 0, 1 Morty model
│   ├── model_P0_M2.json
│   ├── model_P2_M3.json              # Planet 2, 3 Morties model
│   ├── discovery_P2_M3_progress.json
│   ├── pattern_P2_M3_analysis.png
│   └── ...
│
└── ultimate_dataset/                  # Mass collection results
    ├── model_P0_M1.json
    ├── model_P0_M2.json
    ├── ...
    └── (9 models + their visualizations)
```

---

## 🎉 Success Metrics

You'll know you're succeeding when:

- ✅ **R² scores > 0.7** for sinusoidal fits (good pattern match)
- ✅ **Consistent periods** across episodes for same planet/group
- ✅ **Survival rates > 85%** in adaptive strategy runs
- ✅ **Clear visualizations** showing sinusoidal patterns
- ✅ **1000+ data points** per planet/group combination

---

**Good luck saving those Morties! May your simulations run smoothly and your patterns be discovered! 🚀**

Wubba Lubba Dub Dub!
