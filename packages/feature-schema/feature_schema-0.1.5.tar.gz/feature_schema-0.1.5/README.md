# feature_schema

`feature_schema` is a lightweight Python package that automatically extracts and documents **feature metadata** from a pandas DataFrame.  
It’s designed for **machine learning workflows** where you need to understand, validate, or dynamically generate user inputs for model features.  

---

## Features

- Extract feature name
- Auto-detect feature types (`int`, `float`, `string`, `bool`, `datetime`)  
- Numeric metadata: min, max, range  
- Categorical metadata: unique values & counts  
- Nullability check: detect if features contain missing values  
- Human-readable docs (`__str__`) for quick schema inspection  
- Exportable schema to dict / DataFrame for further use  

---

## Installation

```bash
pip install feature_schema
```

## Usage

### 1. Create the Schema for a DataFrame

```python
import pandas as pd
from feature_schema import FeatureSchema

# Sample dataset
df = pd.DataFrame({
    "age": [25, 30, 40, 22],
    "salary": [50000.0, 60000.5, 80000.2, 45000.0],
    "city": ["NY", "SF", "LA", "NY"]
})

# Create Feature schema object
fs = FeatureSchema(df)

# Print schema (human readable)
print(fs.to_dict())

```
### Output:
```json
[
    {'column_name': 'age', 'dtype': 'int64', 'type': 'int', 'nullable': np.False_, 'min': 22.0, 'max': 40.0, 'unique_values': 4}, {'column_name': 'salary', 'dtype': 'float64', 'type': 'float', 'nullable': np.False_, 'min': 45000.0, 'max': 80000.2, 'unique_values': 4}, {'column_name': 'city', 'dtype': 'object', 'type': 'string', 'nullable': np.False_, 'unique_values': 3, 'unique_list': ['NY', 'SF', 'LA']}
]
```

### 2. Export Schema as Dictionary / DataFrame

```python
# As dictionary
schema_dict = fs.to_dict()
print(schema_dict)

# As Object
schema_df = fs.schema
print(schema_df)

# As DataFrame
schema_df = fs.to_dataframe()
print(schema_df)
```
### 3. Save the Model with Feature Schema 

```python
model = LinearRegression()
model.fit(X, y)

# Extract feature schema
fs = FeatureSchema(df)

# Bundle model + schema
package = {
    "model": model,
    "schema": fs.to_dict()  }

# Save with pickle
with open("model_with_schema.pkl", "wb") as f:
    pickle.dump(package, f)

print("✅ Model + schema saved!")
```
### 4. Use the Pre-trained Model with Schema for Dynamic Feature Input

# Load the pickled package (model + schema)

```python
import pickle
import streamlit as st

uploaded_file = st.file_uploader("Upload your trained ML model (.pkl)", type=["pkl","pickle"])

if uploaded_file is not None:
    package = pickle.load(uploaded_file)
    model = package["model"]
    schema = package["schema"]

    st.success("✅ Model loaded successfully!")
    st.subheader("Enter Input Features:")

    feature_values = []

    # Dynamically generate input widgets based on schema
    for feat in schema:
        col_name = feat["column_name"]
        dtype = feat["type"]
        min_val = feat.get("min", 0)   # default 0 if None
        max_val = feat.get("max", 100) # default 100 if None

        # Unique key to avoid Streamlit widget conflicts
        key = f"input_{col_name}"

        # Render input widgets based on feature type
        if dtype == "int":
            val = st.number_input(
                col_name, min_value=int(min_val), max_value=int(max_val),
                value=int(min_val), step=1, key=key
            )
        elif dtype == "float":
            val = st.number_input(
                col_name, min_value=float(min_val), max_value=float(max_val),
                value=float(min_val), key=key
            )
        else:  # string or other types
            val = st.text_input(col_name, key=key)

        feature_values.append(val)
```

## Why Use feature_schema?
- Eliminate hardcoding of feature names, types, and value ranges.
- Automatically generate dynamic input forms for Streamlit or validation schemas for FastAPI.
- Save and bundle schema with ML models for reproducibility and consistency.
- Instantly document datasets for your team or project.
- Validate incoming data to prevent type or value mismatches before predictions.