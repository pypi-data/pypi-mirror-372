# AutoDS Copilot

🤖 **A GenAI-powered agent-based tool for automated data science workflows**

AutoDS Copilot is an intelligent Python package that automates exploratory data analysis, feature engineering, and machine learning model development through natural language prompts. Simply describe what you want to achieve, and let the AI agent handle the implementation details.

## 🚀 Key Features

- **Natural Language Interface**: Interact with your data using simple prompts like "Build a regression model with target = price"
- **Automated EDA**: Comprehensive exploratory data analysis with visualizations and insights
- **Smart Feature Engineering**: Automatic categorical encoding (OneHot, Ordinal, Target, etc.)
- **ML Model Selection**: Dynamically selects and trains suitable models for classification or regression
- **Safe Code Execution**: Internal Python interpreter with security safeguards
- **Modular Architecture**: Clean, extensible design for easy customization
- **Multiple Data Sources**: Support for CSV files and pandas DataFrames
- **Rich Outputs**: Evaluation metrics, visualizations, and model interpretability

## 📦 Installation

```bash
pip install autods-copilot
```

## 🔧 Quick Start

```python
from autods_copilot import AutoDSCopilotAgent

# Initialize the agent
agent = AutoDSCopilotAgent()

# Load your dataset
agent.load_csv("data/house_prices.csv")

# Let the AI handle the rest!
result = agent.run("Perform EDA and build a regression model to predict house prices")

# Get insights and visualizations
print(result.summary)
result.show_plots()
```

### Advanced Usage

```python
# More specific prompts
agent.run("Create correlation heatmap and identify top 5 features for price prediction")
agent.run("Apply one-hot encoding to categorical variables and train Random Forest")
agent.run("Compare performance of Linear Regression vs XGBoost vs Neural Network")

# Direct data loading
import pandas as pd
df = pd.read_csv("your_data.csv")
agent.load_dataframe(df)
agent.run("Build classification model for target column 'category'")
```

### With OpenAI Integration (Enhanced)

```python
import os
from autods_copilot import AutoDSCopilotAgent

# Set your OpenAI API key
agent = AutoDSCopilotAgent(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    llm_model="gpt-4o"  # or "gpt-4o-mini" for cost-effective option
)

# Load data
agent.load_csv("titanic.csv")

# Ask sophisticated natural language questions
result = agent.run("""
    Analyze the Titanic dataset to understand survival patterns.
    Focus on how passenger class, age, and gender influenced survival rates.
    Create visualizations and build a predictive model.
""")
```
```

## 📁 Package Structure

```
autods_copilot/
├── __init__.py                 # Package initialization
├── agent/
│   ├── __init__.py
│   ├── copilot_agent.py       # Main agent orchestrator
│   └── response_handler.py    # Response processing
├── interpreter/
│   ├── __init__.py
│   ├── python_executor.py     # Safe code execution engine
│   └── security.py           # Security validators
├── modules/
│   ├── __init__.py
│   ├── eda/
│   │   ├── __init__.py
│   │   ├── analyzer.py        # EDA analysis
│   │   └── visualizer.py      # Plot generation
│   ├── encoding/
│   │   ├── __init__.py
│   │   ├── categorical.py     # Encoding strategies
│   │   └── numerical.py       # Numerical preprocessing
│   └── modeling/
│       ├── __init__.py
│       ├── classifier.py      # Classification models
│       ├── regressor.py       # Regression models
│       └── evaluator.py       # Model evaluation
├── prompts/
│   ├── __init__.py
│   ├── templates/
│   │   ├── eda_prompts.py     # EDA prompt templates
│   │   ├── encoding_prompts.py # Encoding prompts
│   │   └── modeling_prompts.py # ML prompts
│   └── prompt_manager.py      # Prompt orchestration
├── utils/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging utilities
│   └── validators.py          # Input validation
└── config/
    ├── default_config.yaml    # Default settings
    └── model_configs.yaml     # ML model parameters
```

## 🎯 Use Cases

- **Data Scientists**: Rapid prototyping and baseline model development
- **Business Analysts**: Quick insights from data without coding
- **ML Engineers**: Automated feature engineering pipelines
- **Students**: Learning data science through AI guidance
- **Researchers**: Fast experimental setup and comparison

## 🛣️ Roadmap

### Phase 1: Core Foundation ✅
- [x] Basic agent architecture
- [x] Safe code execution engine
- [x] Modular EDA capabilities
- [x] Simple encoding strategies

### Phase 2: Enhanced Intelligence 🚧
- [ ] Advanced prompt engineering
- [ ] Context-aware model selection
- [ ] Automated hyperparameter tuning
- [ ] Multi-step workflow planning

### Phase 3: LLM Integration 📋
- [ ] OpenAI GPT-4 adapter
- [ ] Anthropic Claude support
- [ ] Local LLM compatibility (Ollama)
- [ ] Custom fine-tuned models

### Phase 4: Advanced Features 📋
- [ ] Time series analysis
- [ ] Deep learning models
- [ ] AutoML integration
- [ ] Model deployment helpers
- [ ] Interactive dashboards

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Development setup
git clone https://github.com/your-org/autods-copilot.git
cd autods-copilot
pip install -e ".[dev]"
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for the data science community
- Inspired by the need for accessible AI-powered analytics
- Special thanks to all contributors and beta testers

---

**Ready to revolutionize your data science workflow? Install AutoDS Copilot today!**

[![PyPI version](https://badge.fury.io/py/autods-copilot.svg)](https://badge.fury.io/py/autods-copilot)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
