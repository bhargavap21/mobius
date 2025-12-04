# Mobius Feature Issues

Copy and paste these into GitHub Issues at: https://github.com/bhargavap21/mobius/issues/new

---

## Issue 1: Integrate with Brokerage Services

**Title:** Integrate with Brokerage Services

**Labels:** `enhancement`, `integration`

**Description:**

### Summary
Integrate Mobius with multiple brokerage services beyond Alpaca to give users more options for deploying their trading strategies.

### Motivation
Currently, Mobius only supports Alpaca. Users may want to use other brokers like Interactive Brokers, TD Ameritrade, or Robinhood.

### Proposed Implementation
- [ ] Research brokerage APIs (Interactive Brokers, TD Ameritrade, Robinhood, etc.)
- [ ] Create abstraction layer for broker interface
- [ ] Implement broker-specific adapters
- [ ] Add broker selection in deployment UI
- [ ] Update deployment engine to support multiple brokers
- [ ] Add broker-specific configuration/credentials management

### Acceptance Criteria
- Users can select their preferred broker when deploying a strategy
- Deployment engine correctly executes trades on selected broker
- All existing Alpaca functionality continues to work

---

## Issue 2: Provide Agents with Relevant MCP Servers

**Title:** Provide Agents with Relevant MCP Servers

**Labels:** `enhancement`, `agents`, `infrastructure`

**Description:**

### Summary
Integrate Model Context Protocol (MCP) servers to provide agents with relevant external data sources and tools.

### Motivation
Agents need access to real-time data, market information, and external APIs to make better trading decisions and generate more sophisticated strategies.

### Proposed Implementation
- [ ] Research MCP server specifications
- [ ] Identify relevant MCP servers for trading (market data, news, sentiment, etc.)
- [ ] Implement MCP client in agent framework
- [ ] Connect agents to appropriate MCP servers based on strategy type
- [ ] Add MCP server configuration management
- [ ] Document available MCP servers for each agent

### Acceptance Criteria
- Agents can access external data through MCP servers
- Strategy generation uses MCP data when relevant
- System remains performant with MCP integration

---

## Issue 3: Support Additional Asset Classes (Forex, Options)

**Title:** Support Additional Asset Classes (Forex and Options)

**Labels:** `enhancement`, `feature`, `trading`

**Description:**

### Summary
Extend Mobius beyond stocks to support forex trading and options strategies.

### Motivation
Many traders want to trade forex pairs and options. Supporting these asset classes makes Mobius more versatile.

### Proposed Implementation
- [ ] Research forex and options data sources
- [ ] Update strategy parser to recognize forex pairs and options symbols
- [ ] Add forex-specific indicators (currency strength, correlation, etc.)
- [ ] Add options-specific logic (Greeks, IV, spreads, etc.)
- [ ] Update backtester to handle forex and options pricing
- [ ] Add asset class selection in UI
- [ ] Update deployment engine for forex/options execution

### Acceptance Criteria
- Users can create strategies for forex pairs (e.g., EUR/USD)
- Users can create options strategies (calls, puts, spreads)
- Backtesting accurately reflects forex/options behavior
- Live trading supports forex and options execution

---

## Issue 4: Turn Prompts into Zapier Workflow

**Title:** Turn Strategy Prompts into Zapier Workflow

**Labels:** `enhancement`, `integration`, `automation`

**Description:**

### Summary
Create a Zapier integration that allows users to trigger strategy creation and deployment through Zapier workflows.

### Motivation
Users may want to automate strategy creation based on external triggers (emails, Slack messages, webhooks, etc.).

### Proposed Implementation
- [ ] Create Zapier app for Mobius
- [ ] Implement webhook endpoints for Zapier triggers
- [ ] Add "Create Strategy" Zapier action
- [ ] Add "Deploy Strategy" Zapier action
- [ ] Add "Pause/Resume Strategy" Zapier action
- [ ] Create Zapier templates for common workflows
- [ ] Document Zapier integration

### Example Use Cases
- Receive email → Parse strategy from email → Create and backtest
- Slack message → Deploy trading bot
- RSS feed alert → Create strategy based on news

### Acceptance Criteria
- Mobius appears in Zapier app directory
- Users can trigger strategy creation from Zapier
- Workflows execute reliably end-to-end

---

## Issue 5: Integrate with BrowserBase for Custom Dataset Creation

**Title:** Integrate with BrowserBase for Custom Dataset Scraping

**Labels:** `enhancement`, `data`, `integration`

**Description:**

### Summary
Integrate with BrowserBase to enable scraping of custom datasets for trading strategies using browser automation.

### Motivation
Many valuable trading signals come from websites that require JavaScript rendering or authentication. BrowserBase allows us to scrape these sources reliably.

### Sub-tasks
- [ ] **Firecrawl Integration** - Basic web crawling
- [x] **Reddit PRAW Scraper** - Already implemented for sentiment
- [ ] **Apify Integration** - Prebuilt scraping actors
- [ ] **Apify Twitter Scraper** - Twitter/X sentiment and trends
- [ ] **12labs Video Analysis** - Extract insights from trading videos/earnings calls

### Proposed Implementation
- [ ] Set up BrowserBase account and API access
- [ ] Create scraper management system
- [ ] Implement scrapers for each data source
- [ ] Store scraped data in datasets (Supabase)
- [ ] Allow users to specify custom scraping targets
- [ ] Add scraper scheduling/automation

### Acceptance Criteria
- Users can create custom datasets from web scraping
- Scraped data is stored and accessible to strategies
- Scrapers run reliably and handle errors gracefully

---

## Issue 6: Clarification Agent - Ask Relevant Questions Before Generation

**Title:** Improve Clarification Agent to Ask Relevant Questions

**Labels:** `enhancement`, `agents`, `ux`

**Description:**

### Summary
✅ **COMPLETED** - The clarification agent now asks relevant questions before generating strategies.

### What Was Implemented
- [x] Clarification agent asks about missing parameters
- [x] Supports entry conditions, exit conditions, timeframes
- [x] Asks about partial position exits (sell 50% vs 100%)
- [x] Multi-turn conversation until all required parameters are collected

### Recent Improvements (Nov 13, 2025)
- [x] Added support for partial exit percentages
- [x] Agent now proactively asks: "Sell entire position or scale out partially?"
- [x] Examples and prompts updated to encourage partial exits

### Future Enhancements (Optional)
- [ ] Add risk tolerance assessment questions
- [ ] Ask about portfolio allocation preferences
- [ ] Suggest similar successful strategies
- [ ] Learn from user preferences over time

---

## Issue 7: AI Suggestions in Refine Tab

**Title:** Add AI-Powered Strategy Suggestions in Refine Tab

**Labels:** `enhancement`, `ai`, `ux`

**Description:**

### Summary
Add AI-powered suggestions in the Refine tab that analyze backtest results and recommend improvements.

### Motivation
Users may not know how to improve underperforming strategies. AI can analyze results and suggest specific changes.

### Proposed Implementation
- [ ] Create suggestion agent that analyzes backtest metrics
- [ ] Generate specific, actionable recommendations
- [ ] Show suggestions in Refine tab UI
- [ ] Allow users to apply suggestions with one click
- [ ] Track which suggestions improve performance

### Example Suggestions
- "Your win rate is 35%. Consider tightening stop loss from 2% to 1.5%"
- "Strategy triggered only 3 times. Try increasing RSI threshold from 30 to 35"
- "Strong performance in tech stocks. Consider creating a portfolio with AAPL, MSFT, NVDA"

### Acceptance Criteria
- Refine tab shows AI-generated suggestions
- Suggestions are specific and actionable
- Users can apply suggestions with one click
- Applied suggestions improve backtest results

---

## Issue 8: Multistock Portfolio Strategies

**Title:** Enhanced Multistock Portfolio Strategy Support

**Labels:** `enhancement`, `feature`, `portfolio`

**Description:**

### Summary
✅ **PARTIALLY COMPLETED** - Basic portfolio mode exists. Need enhancements.

### Current State
- [x] Portfolio mode for multiple static tickers
- [x] Equal weight allocation
- [x] Signal-weighted allocation
- [x] Dynamic trending stock selection (Reddit WSB)

### Proposed Enhancements
- [ ] Better portfolio visualization in UI
- [ ] Show individual asset performance breakdown
- [ ] Correlation analysis between portfolio assets
- [ ] Rebalancing strategies (weekly, monthly, signal-based)
- [ ] Risk parity allocation
- [ ] Market cap weighted allocation
- [ ] Custom allocation rules (user-defined weights)

### Acceptance Criteria
- Users can easily create portfolio strategies
- Portfolio performance metrics are clear and comprehensive
- Multiple allocation strategies are available
- Rebalancing logic is configurable

---

## Issue 9: Agent Orchestration with Follow-up Questions

**Title:** Intelligent Agent Orchestration with Contextual Follow-ups

**Labels:** `enhancement`, `agents`, `ux`

**Description:**

### Summary
Improve agent orchestration to ask intelligent follow-up questions and gather more context before generating strategies.

### Motivation
Sometimes the initial query lacks context. Agents should proactively ask for clarification to create better strategies.

### Proposed Implementation
- [ ] Create orchestration layer that manages multi-agent conversations
- [ ] Implement context tracking across conversation turns
- [ ] Add follow-up question generation based on initial query
- [ ] Allow agents to request specific information from other agents
- [ ] Store conversation history for learning

### Example Flow
1. User: "Create a momentum strategy"
2. Agent: "What timeframe? Day trading or swing trading?"
3. User: "Swing trading"
4. Agent: "Which sector or stocks should I focus on?"
5. User: "Tech stocks"
6. Agent: Creates strategy for tech momentum swing trading

### Acceptance Criteria
- Agents ask relevant follow-up questions
- Context is maintained across conversation
- Final strategy reflects all gathered information
- Conversation flow feels natural

---

## Issue 10: Automatic Strategy Optimizer

**Title:** Implement Automatic Strategy Optimizer

**Labels:** `enhancement`, `optimization`, `ai`

**Description:**

### Summary
Create an automatic optimizer that tests parameter variations and finds the best-performing configuration for a strategy.

### Motivation
Users may create good strategies but not optimal ones. An optimizer can test thousands of combinations to find better parameters.

### Proposed Implementation
- [ ] Create optimizer agent that generates parameter variations
- [ ] Implement grid search for parameter optimization
- [ ] Add genetic algorithm for complex optimization
- [ ] Run parallel backtests for different configurations
- [ ] Rank results by key metrics (return, Sharpe ratio, win rate)
- [ ] Show optimization results in UI
- [ ] Allow users to select best configuration

### Example
**Original Strategy:** RSI < 30 entry, RSI > 70 exit, 2% TP, 1% SL
**Optimizer Tests:**
- RSI thresholds: 25-35 (entry), 65-75 (exit)
- TP: 1-5%
- SL: 0.5-2%

**Result:** RSI < 28 entry, RSI > 72 exit, 3.5% TP, 1.2% SL → +45% return vs +18% original

### Acceptance Criteria
- Optimizer tests multiple parameter combinations
- Results are ranked by performance metrics
- Users can select and apply optimized parameters
- Optimization runs efficiently (parallel execution)

---

## Issue 11: Deploy Strategies to Alpaca for Live Trading

**Title:** Enable Live Strategy Deployment to Alpaca

**Labels:** `enhancement`, `feature`, `critical`, `deployment`

**Description:**

### Summary
✅ **MOSTLY COMPLETED** - Need final testing and polish.

### Current State
- [x] Deployment table in database
- [x] Live trading engine that monitors positions
- [x] Entry/exit signal detection
- [x] Order execution via Alpaca API
- [x] Multi-bot tracking and management

### Remaining Tasks
- [ ] Thorough end-to-end testing on paper trading
- [ ] Add deployment health monitoring dashboard
- [ ] Implement deployment pause/resume controls
- [ ] Add real-time trade notifications
- [ ] Create deployment logs/audit trail
- [ ] Add performance tracking for live deployments
- [ ] Write deployment documentation

### Critical Safety Features Needed
- [ ] Confirmation modal before deploying to live account
- [ ] Daily loss limits
- [ ] Maximum position size enforcement
- [ ] Emergency stop-all button
- [ ] Paper trading mode toggle in UI

### Acceptance Criteria
- Users can deploy strategies from UI
- Strategies execute trades automatically on Alpaca
- All safety features are working
- Performance tracking matches backtest expectations
- Documentation is complete

---

## Priority Recommendations

**High Priority (Do First):**
1. Issue 11 - Deploy strategies to Alpaca (core feature)
2. Issue 7 - AI suggestions in refine tab (improves UX significantly)
3. Issue 6 - Clarification agent (✅ mostly done, just polish)

**Medium Priority:**
4. Issue 9 - Agent orchestration with follow-ups
5. Issue 10 - Automatic strategy optimizer
6. Issue 8 - Enhanced portfolio strategies

**Lower Priority (Nice to Have):**
7. Issue 1 - Additional brokerages
8. Issue 3 - Forex/Options support
9. Issue 2 - MCP servers
10. Issue 4 - Zapier integration
11. Issue 5 - BrowserBase scraping

---

**Note:** You can create these issues on GitHub at: https://github.com/bhargavap21/mobius/issues/new

Copy each issue section into the GitHub issue form and adjust labels/milestones as needed.
