# 🌊 Vibe Water Associates - Algorithmic Trading Platform

> A modern, chat-first algorithmic trading strategy builder that turns plain-English goals into validated, backtested strategies.

## 🚀 Quick Start

```bash
# Clone and navigate to the project
cd vibewater_associates

# Start all services with Docker
./start.sh

# Or manually with Docker Compose
docker-compose up -d
```

**Access the app**: http://localhost:3000

---

## 📖 Full Documentation

- **[PROJECT_README.md](./PROJECT_README.md)** - Complete setup instructions, architecture details, and API documentation
- **[RESEARCH_AGENT_QUICKREF.md](./RESEARCH_AGENT_QUICKREF.md)** - 🆕 Research Agent Quick Reference
- **[RESEARCH_AGENT_GUIDE.md](./RESEARCH_AGENT_GUIDE.md)** - 🆕 Complete Research Agent Documentation

---

## 🆕 Research Agent

The Research Agent is an autonomous AI system that can:
- ✅ Research trading strategies based on market conditions
- ✅ Generate multiple strategy schemas automatically
- ✅ Add strategies to the database
- ✅ Run backtests autonomously
- ✅ Identify highest probability performers

**Quick Start:**
```bash
cd backend
python quick_start_research.py
```

**Documentation:** See [RESEARCH_AGENT_QUICKREF.md](./RESEARCH_AGENT_QUICKREF.md)

---

## Project Overview
Vibewater Associates is a comprehensive platform for creating, backtesting, and managing algorithmic trading strategies. It combines conversational AI with visual strategy building to make algorithmic trading accessible to everyone.

## Problem Statement
Algorithmic trading and portfolio management rely heavily on precise, well-formulated prompts and strategies to be effective. However, maintaining and organizing these prompts can become challenging as teams grow, markets evolve, and strategies diversify. Vibewater Associates aims to solve this by offering a platform to manage, version, and collaborate on these prompts efficiently.

## Target Audience
The platform is aimed at:
- Quantitative traders and algorithmic trading teams.
- Portfolio managers and financial strategists.
- Financial firms and hedge funds looking to optimize collaboration on trading prompts.

The Ideal persona would be:
- Working Professionals 25 years old and above who want exposure in the crypto markets

## Key Features
1. **🤖 Research Agent (NEW!)**: Autonomous AI agent that researches strategies, generates them, runs backtests, and identifies highest probability performers. [Quick Start →](RESEARCH_AGENT_QUICKREF.md)
2. **Prompt Repository**: A centralized space to store, version, and retrieve trading prompts.
3. **Version Control**: Versioning for prompts to track changes and manage iterations.
4. **Collaboration Tools**: Built-in tools for teams to collaborate, discuss, and refine prompts.
5. **Template Library**: Pre-designed templates for common trading and portfolio management use cases.
6. **Integration**: APIs and integrations with trading platforms and data sources.
7. **Analytics Dashboard**: Insights and analytics on prompt performance for better decision-making.
8. **Access Control**: Role-based permissions for secure collaboration.

## Success Metrics
- Adoption rate by trading teams and financial firms.
- Reduction in time spent maintaining and managing prompts.
- User satisfaction scores for collaboration and usability.

## Technology Stack
- Backend: AWS Lambda
- Frontend: React with Next.js
- Database: DynamoDB
- Cloud Hosting: AWS

## Proof of Concept (PoC) Strategy
For the PoC, we are focusing on the **cryptocurrency market**. This decision was inspired by platforms like **[renora.io](https://renora.io)**, which have demonstrated the potential for innovation and success in the crypto trading space. By targeting crypto, we aim to leverage:
- The high volatility of the market to showcase the platform’s adaptability.
- 24/7 trading opportunities to highlight real-time prompt effectiveness.
- The growing demand for tools to manage inefficiencies and innovation in the emerging crypto market.

The PoC will demonstrate:
1. A basic prompt repository tailored for crypto trading strategies.
2. Integration with a popular crypto exchange API (e.g., Binance or Coinbase).
3. Core functionalities like prompt creation, versioning, and a simple analytics dashboard.

## Timeline
1. **Phase 1 - Ideation and Design** (2 Weeks): Finalize product design and architecture.
2. **Phase 2 - Development** (6-8 Weeks): Develop core features and functionalities.
3. **Phase 3 - Testing and Feedback** (2 Weeks): Test with a closed group of users and incorporate feedback.
4. **Phase 4 - Launch** (1 Week): Deploy the product and onboard initial users.

## Future Roadmap
- AI-Powered Prompt Suggestions: Use AI to suggest improvements and optimizations for prompts.
- Multi-Language Support: Support for prompts in multiple programming languages.
- Marketplace: A marketplace for users to share or sell their trading prompts and strategies.

---

This document serves as the starting point for the Vibewater Associates project. Feedback and iterations are welcome as we refine the vision and scope of the platform.
