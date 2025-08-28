"""
Enhanced Natural Language Query Processor for AutoDS Copilot.

This module provides advanced natural language understanding for
more flexible and conversational data science queries.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class QueryIntent:
    """Represents a parsed query intent."""
    primary_action: str
    secondary_actions: List[str]
    entities: List[str]
    modifiers: List[str]
    question_type: str
    confidence: float


class EnhancedQueryProcessor:
    """
    Advanced natural language query processor for data science tasks.
    
    This processor can understand a wide variety of natural language
    patterns and convert them into actionable data science operations.
    """
    
    def __init__(self):
        """Initialize the query processor with patterns and mappings."""
        self.action_patterns = self._load_action_patterns()
        self.entity_patterns = self._load_entity_patterns()
        self.question_patterns = self._load_question_patterns()
        self.intent_mappings = self._load_intent_mappings()
    
    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryIntent:
        """
        Process a natural language query and extract intent.
        
        Args:
            query: Natural language query
            context: Optional context (dataset info, etc.)
            
        Returns:
            QueryIntent object with parsed information
        """
        query = query.lower().strip()
        
        # Extract primary action
        primary_action = self._extract_primary_action(query)
        
        # Extract secondary actions
        secondary_actions = self._extract_secondary_actions(query)
        
        # Extract entities (columns, targets, etc.)
        entities = self._extract_entities(query, context)
        
        # Extract modifiers (how to do the action)
        modifiers = self._extract_modifiers(query)
        
        # Determine question type
        question_type = self._determine_question_type(query)
        
        # Calculate confidence
        confidence = self._calculate_confidence(query, primary_action, entities)
        
        return QueryIntent(
            primary_action=primary_action,
            secondary_actions=secondary_actions,
            entities=entities,
            modifiers=modifiers,
            question_type=question_type,
            confidence=confidence
        )
    
    def generate_response_template(self, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """
        Generate appropriate response template based on intent.
        
        Args:
            intent: Parsed query intent
            context: Dataset and execution context
            
        Returns:
            Python code template as string
        """
        if intent.primary_action == "analyze":
            return self._generate_analysis_template(intent, context)
        elif intent.primary_action == "visualize":
            return self._generate_visualization_template(intent, context)
        elif intent.primary_action == "model":
            return self._generate_modeling_template(intent, context)
        elif intent.primary_action == "compare":
            return self._generate_comparison_template(intent, context)
        elif intent.primary_action == "explain":
            return self._generate_explanation_template(intent, context)
        elif intent.primary_action == "predict":
            return self._generate_prediction_template(intent, context)
        elif intent.primary_action == "summarize":
            return self._generate_summary_template(intent, context)
        else:
            return self._generate_generic_template(intent, context)
    
    def _load_action_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for identifying actions."""
        return {
            "analyze": [
                r"analyz[e|ing]", r"examin[e|ing]", r"investigat[e|ing]", 
                r"explor[e|ing]", r"stud[y|ying]", r"look at", r"understand",
                r"find out", r"discover", r"research"
            ],
            "visualize": [
                r"plot", r"chart", r"graph", r"visualiz[e|ation]", r"show",
                r"display", r"draw", r"create.*plot", r"make.*chart"
            ],
            "model": [
                r"model", r"predict", r"train", r"build.*model", r"machine learning",
                r"classification", r"regression", r"forecast"
            ],
            "compare": [
                r"compar[e|ing|ison]", r"contrast", r"difference", r"vs", 
                r"versus", r"against", r"between"
            ],
            "explain": [
                r"explain", r"why", r"how", r"what.*mean", r"interpret",
                r"reason", r"cause", r"factor"
            ],
            "predict": [
                r"predict", r"forecast", r"estimate", r"project", r"future"
            ],
            "summarize": [
                r"summariz[e|ation]", r"overview", r"summary", r"brief",
                r"quick.*look", r"highlights"
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for identifying entities."""
        return {
            "target": [
                r"target", r"dependent.*variable", r"outcome", r"label",
                r"response.*variable", r"y.*variable"
            ],
            "features": [
                r"feature", r"predictor", r"independent.*variable", 
                r"x.*variable", r"input", r"attribute"
            ],
            "columns": [
                r"column", r"field", r"variable"
            ],
            "data_quality": [
                r"missing.*value", r"null", r"nan", r"outlier", r"duplicate",
                r"data.*quality", r"clean", r"preprocessing"
            ],
            "statistics": [
                r"statistic", r"mean", r"median", r"std", r"correlation",
                r"distribution", r"variance"
            ]
        }
    
    def _load_question_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for question types."""
        return {
            "what": [r"^what", r"what.*is", r"what.*are"],
            "how": [r"^how", r"how.*to", r"how.*can"],
            "why": [r"^why", r"why.*is", r"why.*are"],
            "which": [r"^which", r"which.*one", r"which.*best"],
            "where": [r"^where", r"where.*is", r"where.*are"],
            "when": [r"^when", r"when.*is", r"when.*does"],
            "who": [r"^who", r"who.*is", r"who.*are"],
            "can": [r"^can.*you", r"can.*i", r"is.*it.*possible"],
            "should": [r"^should", r"should.*i", r"recommend"]
        }
    
    def _load_intent_mappings(self) -> Dict[str, str]:
        """Load mappings from actions to AutoDS categories."""
        return {
            "analyze": "eda",
            "visualize": "visualization", 
            "model": "modeling",
            "compare": "comparison",
            "explain": "interpretation",
            "predict": "prediction",
            "summarize": "summary"
        }
    
    def _extract_primary_action(self, query: str) -> str:
        """Extract the primary action from the query."""
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return action
        return "analyze"  # Default action
    
    def _extract_secondary_actions(self, query: str) -> List[str]:
        """Extract secondary actions from the query."""
        actions = []
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    actions.append(action)
        return list(set(actions))  # Remove duplicates
    
    def _extract_entities(self, query: str, context: Optional[Dict[str, Any]]) -> List[str]:
        """Extract entities mentioned in the query."""
        entities = []
        
        # Extract from patterns
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    entities.append(entity_type)
        
        # Extract column names if context provided
        if context and 'data_info' in context:
            columns = context['data_info'].get('columns', [])
            for col in columns:
                if col.lower() in query:
                    entities.append(f"column:{col}")
        
        return list(set(entities))
    
    def _extract_modifiers(self, query: str) -> List[str]:
        """Extract modifiers that specify how to perform the action."""
        modifiers = []
        
        modifier_patterns = {
            "detailed": [r"detailed", r"comprehensive", r"thorough", r"in-depth"],
            "quick": [r"quick", r"brief", r"fast", r"simple"],
            "visual": [r"visual", r"chart", r"plot", r"graph"],
            "statistical": [r"statistical", r"stats", r"numeric"],
            "advanced": [r"advanced", r"sophisticated", r"complex"],
            "basic": [r"basic", r"simple", r"elementary"]
        }
        
        for modifier, patterns in modifier_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    modifiers.append(modifier)
        
        return list(set(modifiers))
    
    def _determine_question_type(self, query: str) -> str:
        """Determine the type of question being asked."""
        for q_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return q_type
        return "statement"
    
    def _calculate_confidence(self, query: str, primary_action: str, entities: List[str]) -> float:
        """Calculate confidence in the intent parsing."""
        confidence = 0.5  # Base confidence
        
        # Boost for clear action words
        if primary_action != "analyze":
            confidence += 0.2
        
        # Boost for specific entities
        confidence += min(0.3, len(entities) * 0.1)
        
        # Boost for question words
        if any(re.search(f"^{q}", query) for q in ["what", "how", "why", "which"]):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_analysis_template(self, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Generate template for analysis tasks."""
        template_parts = [
            "# Advanced Data Analysis",
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "",
            "result = {}",
            ""
        ]
        
        if "detailed" in intent.modifiers or "comprehensive" in intent.modifiers:
            template_parts.extend([
                "# Comprehensive analysis",
                "result['basic_info'] = {",
                "    'shape': data.shape,",
                "    'columns': list(data.columns),",
                "    'dtypes': data.dtypes.to_dict(),",
                "    'missing_values': data.isnull().sum().to_dict()",
                "}",
                "",
                "# Statistical summary",
                "result['statistics'] = data.describe().to_dict()",
                "",
                "# Correlation analysis",
                "numeric_cols = data.select_dtypes(include=[np.number]).columns",
                "if len(numeric_cols) > 1:",
                "    result['correlations'] = data[numeric_cols].corr().to_dict()",
                "",
                "# Data quality check",
                "result['data_quality'] = {",
                "    'duplicates': data.duplicated().sum(),",
                "    'missing_percent': (data.isnull().sum() / len(data) * 100).to_dict()",
                "}",
                "",
                "print('📊 Comprehensive analysis completed!')",
                "print(f'Dataset shape: {data.shape}')",
                "print(f'Missing values: {data.isnull().sum().sum()}')"
            ])
        else:
            template_parts.extend([
                "# Basic analysis",
                "result['summary'] = {",
                "    'shape': data.shape,",
                "    'columns': list(data.columns),",
                "    'basic_stats': data.describe().to_dict()",
                "}",
                "print('📊 Basic analysis completed!')"
            ])
        
        return "\n".join(template_parts)
    
    def _generate_visualization_template(self, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Generate template for visualization tasks."""
        return """
# Data Visualization
import matplotlib.pyplot as plt
import seaborn as sns

result = {}

# Set up plotting style
plt.style.use('seaborn-v0_8')
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Distribution plots for numeric columns
numeric_cols = data.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    for i, col in enumerate(numeric_cols[:4]):
        row, col_idx = divmod(i, 2)
        axes[row, col_idx].hist(data[col], bins=30, alpha=0.7)
        axes[row, col_idx].set_title(f'Distribution of {col}')

plt.tight_layout()
plt.show()

# Correlation heatmap
if len(numeric_cols) > 1:
    plt.figure(figsize=(10, 8))
    correlation_matrix = data[numeric_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Feature Correlation Heatmap')
    plt.show()

result['visualizations_created'] = True
print('📊 Visualizations created successfully!')
"""
    
    def _generate_modeling_template(self, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Generate template for modeling tasks."""
        return """
# Machine Learning Model Building
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import classification_report, mean_squared_error, accuracy_score, f1_score, precision_score, recall_score

result = {}

# Automatically detect target column (usually 'Survived', or last column)
possible_targets = ['Survived', 'Target', 'y', 'target']
target_col = None

for col in possible_targets:
    if col in data.columns:
        target_col = col
        break

if target_col is None:
    # Use the last column as target
    target_col = data.columns[-1]

print("🎯 Using '" + str(target_col) + "' as target variable")

# Prepare features
feature_cols = [col for col in data.columns if col != target_col]

# Select numeric features for modeling
numeric_features = data[feature_cols].select_dtypes(include=[np.number])
X = numeric_features
y = data[target_col]

print("📊 Features: " + str(list(X.columns)))
print("📊 Target: " + str(target_col))
print("📊 Data shape: " + str(X.shape))

# Handle missing values (simple approach)
X = X.fillna(X.mean())

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Determine if classification or regression
is_classification = y.dtype == 'object' or y.nunique() <= 10

print("🔍 Task type: " + ("Classification" if is_classification else "Regression"))

if is_classification:
    # Classification models
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100)
    }
    
    best_score = 0
    best_model_name = None
    model_results = {}
    
    print("\\n🤖 Training Classification Models:")
    print("=" * 50)
    
    for name, model in models.items():
        try:
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            
            model_results[name] = {
                'accuracy': accuracy,
                'f1_score': f1,
                'precision': precision,
                'recall': recall,
                'model': model
            }
            
            print("\\n📈 " + name + " Results:")
            print("   Accuracy:  " + "{:.4f}".format(accuracy))
            print("   F1-Score:  " + "{:.4f}".format(f1))
            print("   Precision: " + "{:.4f}".format(precision))
            print("   Recall:    " + "{:.4f}".format(recall))
            
            if accuracy > best_score:
                best_score = accuracy
                best_model_name = name
                
        except Exception as e:
            print("❌ Error training " + name + ": " + str(e))
    
    # Store results
    result['task_type'] = 'classification'
    result['models'] = model_results
    result['best_model'] = {
        'name': best_model_name,
        'metrics': model_results.get(best_model_name, {})
    }
    
    print("\\n🏆 Best Model: " + str(best_model_name) + " (Accuracy: " + "{:.4f}".format(best_score) + ")")
    
else:
    # Regression models
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(random_state=42, n_estimators=100)
    }
    
    best_score = float('inf')
    best_model_name = None
    model_results = {}
    
    print("\\n🤖 Training Regression Models:")
    print("=" * 50)
    
    for name, model in models.items():
        try:
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            model_results[name] = {
                'mse': mse,
                'rmse': rmse,
                'model': model
            }
            
            print("\\n📈 " + name + " Results:")
            print("   MSE:  " + "{:.4f}".format(mse))
            print("   RMSE: " + "{:.4f}".format(rmse))
            
            if mse < best_score:
                best_score = mse
                best_model_name = name
                
        except Exception as e:
            print("❌ Error training " + name + ": " + str(e))
    
    # Store results
    result['task_type'] = 'regression'
    result['models'] = model_results
    result['best_model'] = {
        'name': best_model_name,
        'metrics': model_results.get(best_model_name, {})
    }
    
    print(f"\\n� Best Model: {best_model_name} (MSE: {best_score:.4f})")

print("\\n✅ Model training completed successfully!")
result['success'] = True
"""
    
    def _generate_comparison_template(self, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Generate template for comparison tasks."""
        return """
# Data Comparison Analysis
result = {}

# Compare distributions across categorical variables
categorical_cols = data.select_dtypes(include=['object', 'category']).columns
numeric_cols = data.select_dtypes(include=[np.number]).columns

if len(categorical_cols) > 0 and len(numeric_cols) > 0:
    cat_col = categorical_cols[0]
    num_col = numeric_cols[0]
    
    # Group comparison
    comparison = data.groupby(cat_col)[num_col].agg(['mean', 'median', 'std']).round(2)
    result['group_comparison'] = comparison.to_dict()
    
    print(f'📊 Comparison of {num_col} by {cat_col}:')
    print(comparison)
    
    # Visualization
    plt.figure(figsize=(10, 6))
    data.boxplot(column=num_col, by=cat_col)
    plt.title(f'{num_col} by {cat_col}')
    plt.show()

result['comparison_completed'] = True
"""
    
    def _generate_explanation_template(self, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Generate template for explanation tasks."""
        return """
# Data Explanation and Insights
result = {}

# Generate explanatory statistics
result['insights'] = []

# Basic dataset information
result['insights'].append(f"This dataset contains {data.shape[0]} rows and {data.shape[1]} columns.")

# Missing data analysis
missing_data = data.isnull().sum()
if missing_data.sum() > 0:
    result['insights'].append(f"There are {missing_data.sum()} missing values across {(missing_data > 0).sum()} columns.")

# Data types summary
dtype_counts = data.dtypes.value_counts()
result['insights'].append(f"Data types: {dtype_counts.to_dict()}")

# Numeric columns analysis
numeric_cols = data.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    result['insights'].append(f"Found {len(numeric_cols)} numeric columns for analysis.")
    
    # Find columns with high correlation
    if len(numeric_cols) > 1:
        corr_matrix = data[numeric_cols].corr()
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.7:
                    high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j]))
        
        if high_corr:
            result['insights'].append(f"High correlations found: {high_corr}")

# Print insights
for insight in result['insights']:
    print(f"💡 {insight}")

result['explanation_completed'] = True
"""
    
    def _generate_prediction_template(self, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Generate template for prediction tasks."""
        return self._generate_modeling_template(intent, context)
    
    def _generate_summary_template(self, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Generate template for summary tasks."""
        return """
# Data Summary
result = {}

# Quick overview
result['summary'] = {
    'dataset_shape': data.shape,
    'column_count': len(data.columns),
    'row_count': len(data),
    'memory_usage': data.memory_usage(deep=True).sum(),
    'data_types': data.dtypes.value_counts().to_dict()
}

# Key statistics
numeric_data = data.select_dtypes(include=[np.number])
if not numeric_data.empty:
    result['key_statistics'] = {
        'mean_values': numeric_data.mean().to_dict(),
        'missing_values': data.isnull().sum().to_dict()
    }

# Quick insights
print("📋 Dataset Summary:")
print(f"  • Shape: {data.shape}")
print(f"  • Columns: {len(data.columns)}")
print(f"  • Missing values: {data.isnull().sum().sum()}")
print(f"  • Data types: {data.dtypes.value_counts().to_dict()}")

result['summary_completed'] = True
"""
    
    def _generate_generic_template(self, intent: QueryIntent, context: Dict[str, Any]) -> str:
        """Generate generic template for unrecognized queries."""
        return """
# Generic Data Analysis
result = {}

# Basic exploration
result['basic_info'] = {
    'shape': data.shape,
    'columns': list(data.columns),
    'dtypes': data.dtypes.to_dict()
}

# Show first few rows
print("📊 Dataset Overview:")
print(f"Shape: {data.shape}")
print(f"Columns: {list(data.columns)}")
print("\\nFirst 5 rows:")
print(data.head())

result['generic_analysis_completed'] = True
"""
