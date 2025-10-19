# Statsig Integration Plan for Mobius Trading Platform

## 🎯 Hackathon Goal
**Challenge**: Build an AI-powered product that uses Statsig to experiment, personalize, or optimize the experience.

**Our Approach**: Use Statsig to A/B test different AI prompts, models, and parameters to determine which configurations generate the most profitable trading strategies.

---

## 📊 Key Metrics We'll Track

### Primary Metrics (Strategy Performance)
- **Backtest Total Return %** - Main success metric
- **Win Rate %** - Quality of trades
- **Number of Trades** - Strategy activity level
- **Max Drawdown %** - Risk management
- **Sharpe Ratio** - Risk-adjusted returns

### Secondary Metrics (User Engagement)
- **Strategy Generation Time** - User experience
- **Strategy Refinement Count** - User satisfaction indicator
- **Bot Save Rate** - User commitment
- **Deployment Rate** - Real usage indicator

### System Metrics
- **AI Response Time** - Performance
- **Error Rate** - Reliability
- **Iteration Count to Success** - Efficiency

---

## 🧪 Experiments We'll Run

### Experiment 1: AI Prompt Engineering
**Hypothesis**: Enhanced prompt templates produce higher-performing trading strategies

**Variants**:
- **Control**: Current standard prompts
- **Variant A**: More detailed technical indicator explanations
- **Variant B**: Risk-first prompt engineering (emphasize stop-loss, position sizing)
- **Variant C**: Performance-optimized prompts (focus on high win rate)

**Success Metric**: Average backtest total return %

**Implementation**:
```python
# backend/agents/code_generator.py
variant = statsig.get_experiment(user, "prompt_engineering_test")
prompt_template = variant.get("prompt_template", "standard")
```

---

### Experiment 2: Multi-Agent Iteration Count
**Hypothesis**: Different iteration counts affect strategy quality

**Variants**:
- **Control**: 3 iterations (current)
- **Variant A**: 5 iterations
- **Variant B**: Dynamic (stop when performance threshold met)

**Success Metric**: Win rate % and total return %

**Implementation**:
```python
# backend/agents/supervisor.py
config = statsig.get_dynamic_config(user, "iteration_config")
max_iterations = config.get("max_iterations", 3)
```

---

### Experiment 3: Strategy Personalization
**Hypothesis**: Personalized strategies based on user experience level perform better for that user

**Segments**:
- **Beginner**: Simple strategies (1-2 indicators, clear rules)
- **Intermediate**: Moderate complexity (3-4 indicators, multiple conditions)
- **Advanced**: Complex strategies (5+ indicators, custom logic)

**Success Metric**: User engagement (saves, deployments) + strategy performance

**Implementation**:
```python
# Determine user level based on past activity
user_level = determine_user_level(user_history)
statsig.log_event(user, "strategy_request", {"user_level": user_level})

config = statsig.get_dynamic_config(user, "strategy_complexity")
max_indicators = config.get("max_indicators", 3)
```

---

### Experiment 4: Backtesting Parameters
**Hypothesis**: Optimal backtesting window varies by strategy type

**Variants**:
- **Control**: 180 days (6 months)
- **Variant A**: 90 days (3 months) - more recent data
- **Variant B**: 365 days (1 year) - more historical data
- **Variant C**: Dynamic based on strategy type

**Success Metric**: Out-of-sample performance correlation

---

## 🚀 Implementation Steps

### Phase 1: Setup & Infrastructure (30 mins)

#### 1.1 Install Statsig SDKs
```bash
# Backend
cd backend
pip install statsig

# Frontend
cd frontend/frontend
npm install statsig-react
```

#### 1.2 Create Statsig Account & Get API Keys
- Sign up at statsig.com
- Create new project "Mobius Trading Bot"
- Get Server Secret Key (backend)
- Get Client SDK Key (frontend)

#### 1.3 Add Environment Variables
```bash
# backend/.env
STATSIG_SERVER_SECRET_KEY=secret-xxx

# frontend/.env
VITE_STATSIG_CLIENT_KEY=client-xxx
```

#### 1.4 Initialize Statsig
**Backend**: `backend/services/statsig_service.py`
```python
from statsig import statsig
from config import settings
import logging

logger = logging.getLogger(__name__)

class StatsigService:
    def __init__(self):
        statsig.initialize(settings.statsig_server_secret_key)
        logger.info("✅ Statsig initialized")

    def get_experiment(self, user_id: str, experiment_name: str):
        user = {"userID": user_id}
        return statsig.get_experiment(user, experiment_name)

    def get_config(self, user_id: str, config_name: str):
        user = {"userID": user_id}
        return statsig.get_config(user, config_name)

    def check_gate(self, user_id: str, gate_name: str):
        user = {"userID": user_id}
        return statsig.check_gate(user, gate_name)

    def log_event(self, user_id: str, event_name: str, metadata: dict = None):
        user = {"userID": user_id}
        statsig.log_event(user, event_name, value=None, metadata=metadata)

statsig_service = StatsigService()
```

**Frontend**: `frontend/src/context/StatsigContext.jsx`
```jsx
import { StatsigProvider } from 'statsig-react'
import { useAuth } from './AuthContext'

export function StatsigWrapper({ children }) {
  const { user } = useAuth()

  return (
    <StatsigProvider
      sdkKey={import.meta.env.VITE_STATSIG_CLIENT_KEY}
      user={{
        userID: user?.id || 'anonymous',
        email: user?.email,
        custom: {
          userLevel: user?.level || 'beginner'
        }
      }}
      waitForInitialization={true}
    >
      {children}
    </StatsigProvider>
  )
}
```

---

### Phase 2: Experiment Implementation (45 mins)

#### 2.1 Prompt Engineering Experiment

**Create Experiment in Statsig Console**:
- Name: `prompt_engineering_test`
- Variants: control, enhanced_detail, risk_first, performance_optimized
- Parameter: `prompt_template` (string)

**Backend Integration**:
```python
# backend/agents/code_generator.py
from services.statsig_service import statsig_service

class CodeGeneratorAgent:
    def generate_code(self, strategy, user_id):
        # Get experiment variant
        experiment = statsig_service.get_experiment(user_id, "prompt_engineering_test")
        prompt_template = experiment.get("prompt_template", "standard")

        # Use different prompt based on variant
        if prompt_template == "enhanced_detail":
            system_prompt = ENHANCED_DETAIL_PROMPT
        elif prompt_template == "risk_first":
            system_prompt = RISK_FIRST_PROMPT
        elif prompt_template == "performance_optimized":
            system_prompt = PERFORMANCE_PROMPT
        else:
            system_prompt = STANDARD_PROMPT

        # Generate code
        code = self._generate_with_claude(strategy, system_prompt)

        return code
```

**Log Events**:
```python
# backend/main.py - After backtest completes
statsig_service.log_event(
    user_id=user_id,
    event_name="strategy_generated",
    metadata={
        "total_return": backtest_results.total_return,
        "win_rate": backtest_results.win_rate,
        "total_trades": backtest_results.total_trades,
        "max_drawdown": backtest_results.max_drawdown,
        "generation_time_seconds": elapsed_time,
        "prompt_variant": experiment.get("prompt_template"),
        "iteration_count": current_iteration
    }
)
```

#### 2.2 Iteration Count Experiment

**Create Dynamic Config**:
- Name: `iteration_config`
- Parameters:
  - `max_iterations` (integer): 3, 5, or 7
  - `early_stop_threshold` (float): 0.15 (15% return)

**Implementation**:
```python
# backend/agents/supervisor.py
def run_workflow(self, user_query, user_id):
    # Get dynamic config
    config = statsig_service.get_config(user_id, "iteration_config")
    max_iterations = config.get("max_iterations", 3)
    early_stop_threshold = config.get("early_stop_threshold", None)

    for iteration in range(1, max_iterations + 1):
        # Run iteration
        results = self._run_iteration(...)

        # Check early stop
        if early_stop_threshold and results.total_return >= early_stop_threshold:
            statsig_service.log_event(
                user_id,
                "early_stop_triggered",
                {"iteration": iteration, "return": results.total_return}
            )
            break
```

#### 2.3 Feature Gates for New Features

**Create Feature Gates**:
- `enable_deployment_feature` - Gate for Alpaca deployment
- `enable_advanced_charts` - Gate for custom visualizations
- `enable_social_sentiment` - Gate for Twitter/Reddit data

**Implementation**:
```python
# backend/routes/deployment_routes.py
@router.post("/deployments")
async def create_deployment(user_id: UUID = Depends(get_current_user_id)):
    # Check feature gate
    if not statsig_service.check_gate(str(user_id), "enable_deployment_feature"):
        raise HTTPException(
            status_code=403,
            detail="Deployment feature not enabled for your account"
        )
    # ... rest of deployment logic
```

```jsx
// frontend/src/components/BacktestResults.jsx
import { useGate } from 'statsig-react'

function BacktestResults({ results }) {
  const { value: deploymentEnabled } = useGate('enable_deployment_feature')

  return (
    <>
      {/* Results display */}

      {deploymentEnabled && (
        <button onClick={() => setShowDeploymentPage(true)}>
          Proceed to Deployment →
        </button>
      )}
    </>
  )
}
```

---

### Phase 3: Analytics Dashboard (30 mins)

#### 3.1 Create Custom Metrics in Statsig

**Metrics to Create**:
1. **Average Strategy Return** - Average of `total_return` from `strategy_generated` events
2. **Win Rate by Variant** - Average `win_rate` grouped by variant
3. **Generation Success Rate** - % of strategies that complete without errors
4. **User Engagement Score** - Composite of saves, deployments, refinements

#### 3.2 Set Up Experiment Dashboards

For each experiment:
1. Primary metric scorecard
2. Secondary metrics comparison
3. Statistical significance calculator
4. Segment breakdown (beginner vs advanced users)

#### 3.3 Add In-App Analytics Display

```jsx
// frontend/src/components/StatsigDashboard.jsx
import { useStatsigClient } from 'statsig-react'

export function StatsigDashboard() {
  const { client } = useStatsigClient()

  // Display experiment assignments
  const experiments = client.getAllEvaluations().dynamic_configs

  return (
    <div className="p-6">
      <h2>Active Experiments</h2>
      {Object.entries(experiments).map(([name, config]) => (
        <div key={name}>
          <h3>{name}</h3>
          <pre>{JSON.stringify(config.value, null, 2)}</pre>
        </div>
      ))}
    </div>
  )
}
```

---

## 📈 Success Metrics for Hackathon

### Quantitative Metrics
- [ ] **3+ Active Experiments** running simultaneously
- [ ] **500+ Events** logged across all experiments
- [ ] **Statistical Significance** achieved on at least 1 experiment
- [ ] **10%+ Performance Improvement** in winning variant

### Qualitative Metrics
- [ ] **Clear Data Story** - Can explain which AI approach works best
- [ ] **Live Demo** - Show real-time experiment results
- [ ] **User Impact** - Demonstrate how experimentation improves user experience

---

## 🎨 Presentation Strategy

### Demo Flow (5 minutes)

1. **Problem Statement** (30s)
   - "How do we know which AI model/prompt generates the best trading strategies?"

2. **Solution Overview** (1 min)
   - Show Mobius platform
   - Explain multi-agent AI system
   - Introduce Statsig integration

3. **Live Experimentation** (2 min)
   - Show Statsig console with active experiments
   - Generate 2 strategies with different variants
   - Compare backtest results in real-time
   - Show event logging in Statsig

4. **Results & Insights** (1.5 min)
   - Display metrics dashboard
   - Show winning variant data
   - Explain business impact (e.g., "Risk-first prompts increased win rate by 15%")

5. **Technical Deep Dive** (30s)
   - Quick code walkthrough
   - Show feature gate implementation
   - Highlight dynamic configs

### Key Talking Points

✅ **"We're not just building AI - we're measuring what works"**
- Statsig lets us scientifically determine which AI approaches generate profitable strategies

✅ **"Real metrics, real impact"**
- Show actual backtest returns, win rates, and user engagement data

✅ **"Continuous optimization"**
- Feature gates let us roll out improvements gradually
- Dynamic configs enable real-time parameter tuning

✅ **"Personalized AI for every trader"**
- Beginner vs advanced user segments get optimized experiences

---

## 🔧 Technical Implementation Checklist

### Backend
- [ ] Install `statsig` Python SDK
- [ ] Create `statsig_service.py`
- [ ] Add environment variables
- [ ] Initialize Statsig in `main.py`
- [ ] Integrate experiments in CodeGenerator
- [ ] Add dynamic configs to Supervisor
- [ ] Implement feature gates for deployments
- [ ] Add event logging throughout workflow
- [ ] Create custom metrics endpoints

### Frontend
- [ ] Install `statsig-react` npm package
- [ ] Create StatsigContext wrapper
- [ ] Wrap app in StatsigProvider
- [ ] Add feature gates to UI components
- [ ] Implement experiment-aware UI variations
- [ ] Create analytics dashboard component
- [ ] Add event logging for user actions

### Statsig Console
- [ ] Create experiments with variants
- [ ] Set up dynamic configs
- [ ] Configure feature gates
- [ ] Define custom metrics
- [ ] Create dashboards
- [ ] Set up alerts for significant results

### Testing
- [ ] Verify experiments assignment works
- [ ] Test event logging
- [ ] Validate metrics calculation
- [ ] Check feature gate behavior
- [ ] Test across user segments

---

## 📊 Expected Results

### Experiment Hypotheses

**Prompt Engineering**
- **Expected Winner**: Risk-first prompts (20% higher win rate)
- **Rationale**: Better risk management = more consistent returns

**Iteration Count**
- **Expected Winner**: Dynamic early stopping (30% faster, similar quality)
- **Rationale**: Saves compute without sacrificing performance

**User Personalization**
- **Expected Winner**: Segment-specific strategies (25% higher engagement)
- **Rationale**: Tailored complexity matches user skill level

---

## 🏆 Hackathon Submission Materials

### Required Deliverables
1. **Working Demo** - Live Mobius platform with Statsig integration
2. **Code Repository** - Clean, documented code on GitHub
3. **Statsig Dashboard** - Screenshots/recording of metrics
4. **Presentation Deck** - 5-slide overview + demo
5. **Video Demo** - 3-minute walkthrough (backup for live demo)

### Bonus Points
- Real user testing data (even if just 5-10 users)
- Statistical significance achieved
- Clear ROI calculation (e.g., "15% better strategies = $X in potential trading profits")
- Open-source the integration as template for others

---

## ⏱️ Time Estimate

**Total Implementation Time: ~2-3 hours**

- Phase 1 (Setup): 30 mins
- Phase 2 (Experiments): 45 mins
- Phase 3 (Analytics): 30 mins
- Testing & Refinement: 30 mins
- Demo Preparation: 30 mins

---

## 🎯 Success Criteria

### Minimum Viable Integration
- ✅ 1 experiment running (prompt engineering)
- ✅ Event logging working
- ✅ Can show variant comparison
- ✅ Clear winner based on data

### Ideal Integration (Prize-Winning)
- ✅ 3+ experiments running
- ✅ Feature gates controlling rollouts
- ✅ Dynamic configs optimizing parameters
- ✅ Statistical significance achieved
- ✅ Clear business impact demonstrated
- ✅ Polished presentation with live demo

---

## 📝 Notes

- Start with prompt engineering experiment - easiest to show impact
- Focus on backtest returns as primary metric - most compelling
- Keep UI simple - Statsig should feel invisible to users
- Prepare backup data in case live demo has issues
- Practice the demo flow multiple times

**Let's ship this! 🚀**
