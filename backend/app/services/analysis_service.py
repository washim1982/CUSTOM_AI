# backend/app/services/analysis_service.py

import pandas as pd
import matplotlib.pyplot as plt
import io
from typing import List

# Configure matplotlib to use a non-interactive backend
plt.switch_backend('Agg')

def read_excel_to_dataframe(file_buffer: io.BytesIO) -> pd.DataFrame:
    """Reads an Excel file from a buffer into a pandas DataFrame."""
    try:
        df = pd.read_excel(file_buffer)
        if df.empty:
            raise ValueError("Excel file is empty.")
        return df
    except Exception as e:
        # Catch pandas specific errors or general exceptions
        raise ValueError(f"Failed to parse Excel file: {e}")


def create_chart_from_dataframe(
    df: pd.DataFrame,
    x_axis_col: str,
    y_axis_col: str,
    chart_type: str = 'bar'
) -> io.BytesIO:
    """
    Generates a chart from specified columns of a DataFrame.
    Handles categorical x-axis data for bar charts.
    """
    try:
        if x_axis_col not in df.columns or y_axis_col not in df.columns:
            raise ValueError("Invalid column names provided.")

        plt.figure(figsize=(10, 6))

        # --- Handle Categorical X-Axis for Bar Charts ---
        if chart_type == 'bar':
            # Get unique categories and their corresponding y-values
            # If multiple rows have the same category, you might want to aggregate (e.g., sum, mean)
            # For simplicity here, let's plot each occurrence or maybe the first one?
            # A better approach is often to group and aggregate first.
            # Example: Group by Project Name and sum Days Required
            if pd.api.types.is_string_dtype(df[x_axis_col]) or pd.api.types.is_object_dtype(df[x_axis_col]):
                 # Group by the categorical column and aggregate the numerical one (e.g., sum)
                 aggregated_data = df.groupby(x_axis_col)[y_axis_col].sum().reset_index()
                 x_categories = aggregated_data[x_axis_col].astype(str) # Ensure strings
                 y_values = aggregated_data[y_axis_col]
                 plt.bar(x_categories, y_values)
                 plt.xticks(rotation=45, ha='right') # Rotate labels if many categories
            else:
                 # If x-axis is not string/object, treat as numeric (original behavior)
                 x_data = pd.to_numeric(df[x_axis_col], errors='coerce').fillna(0)
                 y_data = pd.to_numeric(df[y_axis_col], errors='coerce').fillna(0)
                 plt.bar(x_data, y_data)

        elif chart_type == 'line':
            # Line plots usually make more sense with ordered (numeric/datetime) x-axis
            try:
                 # Attempt conversion for sorting
                 df[x_axis_col] = pd.to_datetime(df[x_axis_col], errors='coerce') # Try datetime first
                 if df[x_axis_col].isnull().all(): # If datetime fails, try numeric
                     df[x_axis_col] = pd.to_numeric(df[x_axis_col], errors='coerce')

                 df_sorted = df.sort_values(by=x_axis_col).dropna(subset=[x_axis_col, y_axis_col])
                 x_data = df_sorted[x_axis_col]
                 y_data = pd.to_numeric(df_sorted[y_axis_col], errors='coerce') # Ensure y is numeric
                 plt.plot(x_data, y_data.dropna()) # Plot only valid y points
                 plt.xticks(rotation=45, ha='right')
            except Exception as e:
                 raise ValueError(f"Line plot failed. Ensure '{x_axis_col}' is suitable for ordering (numeric/date) and '{y_axis_col}' is numeric. Error: {e}")


        elif chart_type == 'scatter':
             # Scatter plots typically use two numeric columns
             x_data = pd.to_numeric(df[x_axis_col], errors='coerce')
             y_data = pd.to_numeric(df[y_axis_col], errors='coerce')
             plt.scatter(x_data.dropna(), y_data.dropna()) # Drop NaN pairs
             plt.xticks(rotation=45, ha='right')
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        plt.xlabel(x_axis_col)
        plt.ylabel(y_axis_col)
        plt.title(f'{y_axis_col} by {x_axis_col}')
        plt.tight_layout()

        # Save the plot to an in-memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close() # Close the figure
        buf.seek(0)

        return buf

    except Exception as e:
        plt.close() # Ensure figure is closed on error
        raise RuntimeError(f"Failed to generate chart: {e}")