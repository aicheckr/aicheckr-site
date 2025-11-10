# 🛸 Morty Rescue Mission - Sphinx HQ Challenge

**Wubba Lubba Dub Dub!** This repository contains the solution for rescuing 1000 Morties from the Council of Ricks by optimizing portal travel through dangerous planets.

## 🎯 Challenge Overview

- **Objective**: Save as many Morties as possible by sending them from the Citadel to Planet Jessica
- **Constraint**: Must travel through one of three intermediate planets with changing survival rates
- **Goal**: Maximize `morties_on_planet_jessica` (up to 1000)

### The Three Planets

1. **Planet 0** - "On a Cob" Planet
2. **Planet 1** - Cronenberg World
3. **Planet 2** - The Purge Planet

Each planet's survival rate changes dynamically based on the number of trips taken!

## 🚀 Quick Start

### 1. Get Your API Token

First, request an API token:

```bash
curl -X POST https://challenge.sphinxhq.com/api/auth/request-token/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Name",
    "email": "your.email@example.com"
  }'
```

The token will be sent to your email.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - API communication
- `numpy` - Numerical analysis
- `matplotlib` - Visualization
- `scipy` - Pattern fitting

### 3. Set Your API Token

```bash
export MORTY_API_TOKEN="your_token_here"
```

Or the script will prompt you for it when you run it.

### 4. Run the Rescue Mission

```bash
python morty_rescue.py
```

You'll be presented with three strategy options:

1. **Full Exploration + Optimization** (most thorough, slower)
   - Explores each planet/group combination with 30 trips
   - Then optimizes based on learned patterns
   - Best for understanding all patterns

2. **Adaptive Strategy** (balanced) ⭐ **RECOMMENDED**
   - Quick exploration (15 trips per combination)
   - Continuous learning and adaptation
   - Good balance of exploration and exploitation

3. **Quick Adaptive** (faster, less exploration)
   - Minimal exploration (10 trips per combination)
   - Faster completion
   - May miss some pattern nuances

## 📊 Strategy Explained

### Phase 1: Exploration

The script systematically tests each combination of:
- **Planets**: 0, 1, 2
- **Group sizes**: 1, 2, 3 Morties

This gathers data on survival rates and identifies patterns.

### Phase 2: Pattern Analysis

For each planet and group size, the analyzer:

1. **Detects sinusoidal patterns** (especially for Planet 2 with period ~200)
2. **Fits mathematical models** to predict future survival rates
3. **Calculates expected values** for each action

### Phase 3: Optimization

Uses the learned patterns to:
- Predict survival probability for each possible action
- Calculate expected value (probability × morty_count)
- Always choose the action with highest expected value
- Continuously update predictions as more data comes in

## 🔬 Key Findings

Based on initial exploration:

- **Planet 2** exhibits **sinusoidal patterns** with period ≈ 200 trips
- **Different group sizes** (1, 2, 3 Morties) follow **different curves** on the same planet
- Survival rates change over time, requiring **adaptive strategies**

## 📈 Output

The script generates:

1. **Console output** with real-time progress
2. **Visualization plots**:
   - `morty_rescue_analysis.png` - Detailed patterns for each planet/group
   - `morty_rescue_summary.png` - Mission progress and planet usage
3. **Results JSON** (`morty_rescue_results.json`) with complete trip history

### Sample Output

```
🏁 MISSION COMPLETE!
============================================================

📊 FINAL SCORE: 847 Morties saved! 🎉
💀 Morties lost: 153
🏰 Morties remaining in Citadel: 0
📈 Total steps taken: 287
✅ Success rate: 84.7%
```

## 🧠 Advanced Usage

### Analyzing Specific Patterns

You can modify the script to focus exploration on specific planets:

```python
# In the exploration_phase method, focus on Planet 2
for planet in [2]:  # Only test Planet 2
    for morty_count in range(1, 4):
        # ... exploration code
```

### Custom Pattern Models

Add your own pattern detection in the `PatternAnalyzer` class:

```python
def custom_model(self, x, *params):
    # Your custom mathematical model
    return ...
```

### Adjusting Exploration Depth

```python
strategy.exploration_trips_per_combo = 20  # Adjust number of exploration trips
```

## 🏆 Optimization Tips

1. **Early Exploration**: Gather enough data to detect patterns (at least 20 trips per combination)

2. **Expected Value**: Always choose the action with highest `probability × morty_count`

3. **Continuous Learning**: Update predictions after every trip to adapt to changing patterns

4. **Pattern Period**: For sinusoidal patterns, align your trips with high-probability phases

5. **Group Size Strategy**: Sometimes sending 3 Morties at 70% is better than 1 Morty at 90%!

## 🔧 Troubleshooting

### API Token Issues

If you get authentication errors:
- Check that your token is correctly set
- Ensure the token hasn't expired
- Verify the email address used for token request

### Missing Dependencies

```bash
pip install --upgrade requests numpy matplotlib scipy
```

### Visualization Errors

If matplotlib fails to save plots, install the backend:

```bash
# On Ubuntu/Debian
sudo apt-get install python3-tk

# On macOS
brew install python-tk
```

## 📚 API Reference

### Start Episode
```bash
POST /api/mortys/start/
Headers: Authorization: Bearer YOUR_TOKEN
```

### Send Morties
```bash
POST /api/mortys/portal/
Headers: Authorization: Bearer YOUR_TOKEN
Body: {"planet": 0-2, "morty_count": 1-3}
```

### Check Status
```bash
GET /api/mortys/status/
Headers: Authorization: Bearer YOUR_TOKEN
```

## 🎮 The Challenge

This is part of the **Sphinx HQ Morty Express Challenge** with real prizes:

- 🥇 **1st Place**: $10,000 + Flight to SF
- 🥈 **2nd Place**: $4,000 + Remote Interview
- 🥉 **3rd Place**: $2,000 + Remote Interview

## 🤝 Contributing

Feel free to improve the algorithm! Some ideas:

- Implement reinforcement learning approaches
- Add multi-armed bandit algorithms
- Optimize the sinusoidal pattern detection
- Parallel universe exploration (multiple episodes simultaneously)

## 📝 License

This is for the Sphinx HQ challenge. Wubba Lubba Dub Dub!

---

*"Listen Morty, the universe is basically an animal. It grazes on the ordinary. It creates infinite idiots just to eat them. Smart people get a chance to climb on top, take reality for a ride."* - Rick Sanchez
