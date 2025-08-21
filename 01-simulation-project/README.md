# Personal Futures Backtesting System

A simplified microservices-based futures backtesting platform for personal trading strategy development.

## 🎯 Project Overview

This system provides reliable futures backtesting capabilities with proper contract handling, risk management, and machine learning integration - designed for personal use without Docker complexity.

## 🏗️ Architecture

- **6 Python Microservices**: Data, Backtest, Risk, ML, Portfolio, Dashboard
- **Redis Communication**: Simple pub/sub messaging between services
- **SQLite Database**: Lightweight local data storage
- **One-Command Startup**: `python run_system.py`

## 📁 Project Structure

```
personal-futures-backtester/
├── development-documents/     # Project planning and specifications
├── old/                      # Previous versions and archives
├── services/                 # Microservices (to be created)
├── shared/                   # Common utilities (to be created)
├── dashboard/                # Streamlit UI (to be created)
├── data/                     # Database files (to be created)
└── run_system.py            # Main startup script (to be created)
```

## 📋 Implementation Plan

See `development-documents/SIMPLE-MICROSERVICES-PLAN.md` for the complete 6-month development roadmap.

## 🚀 Quick Start

*Coming soon - Week 1 of development will create the basic startup system*

## 📚 Documentation

- **[Implementation Plan](development-documents/SIMPLE-MICROSERVICES-PLAN.md)** - Complete development roadmap
- **[Personal PRD](development-documents/PERSONAL-FUTURES-BACKTESTING-PRD.md)** - Project requirements

## 🎯 Success Targets

- **Phase 1 (Month 1)**: Basic backtesting operational
- **Phase 2 (Month 2)**: Core services complete  
- **Phase 3 (Month 3)**: Futures features working
- **Phase 4 (Month 4)**: Dashboard functional
- **Phase 5 (Month 5)**: Integration testing
- **Phase 6 (Month 6)**: Production ready

## ⚡ Technology Stack

- **Language**: Python 3.11+ only
- **Framework**: FastAPI (services) + Streamlit (dashboard)
- **Database**: SQLite + Redis
- **Backtesting**: PyBroker
- **Deployment**: Simple Python scripts (no Docker)

---

**Status**: 📋 Planning Complete → 🚀 Ready for Implementation