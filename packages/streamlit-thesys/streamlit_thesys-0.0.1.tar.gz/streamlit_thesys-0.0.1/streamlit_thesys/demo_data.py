"""
Demo data for Thesys Streamlit component examples.
This file contains all the sample data used in the example.py file.
"""
# Sample DataFrame data
def get_sample_dataframe():
    """Returns a sample DataFrame for visualization examples."""
    return pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Sales': [100, 150, 200, 180, 220, 250],
        'Profit': [20, 30, 40, 35, 45, 50]
    })

# Enhanced demo datasets for better visualization examples
def get_sales_performance_data():
    """Returns a comprehensive sales performance dataset."""
    return pd.DataFrame({
        'Quarter': ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024', 'Q2 2024'],
        'Revenue': [120000, 135000, 142000, 158000, 145000, 162000],
        'Profit': [24000, 29000, 31000, 38000, 32000, 41000],
        'Units_Sold': [450, 520, 580, 640, 560, 675],
        'Customer_Satisfaction': [4.2, 4.3, 4.1, 4.5, 4.4, 4.6]
    })

def get_employee_data():
    """Returns employee performance and demographic data."""
    return pd.DataFrame({
        'Department': ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations'],
        'Employees': [45, 32, 18, 12, 15, 28],
        'Avg_Salary': [95000, 75000, 68000, 72000, 78000, 65000],
        'Satisfaction_Score': [4.2, 4.0, 4.3, 4.1, 3.9, 4.2],
        'Turnover_Rate': [8.5, 12.3, 15.2, 9.1, 7.8, 11.4]
    })

def get_website_analytics_data():
    """Returns website analytics data."""
    return pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=12, freq='M'),
        'Page_Views': [15420, 18350, 22100, 19875, 25600, 28900, 31200, 29800, 33500, 36200, 38900, 42100],
        'Unique_Visitors': [8900, 10200, 12500, 11400, 14800, 16200, 17800, 16900, 19200, 20800, 22400, 24100],
        'Bounce_Rate': [45.2, 42.8, 38.9, 41.2, 35.6, 33.4, 31.8, 34.2, 29.9, 28.5, 26.7, 25.3],
        'Conversion_Rate': [2.1, 2.4, 2.8, 2.6, 3.2, 3.5, 3.8, 3.6, 4.1, 4.3, 4.6, 4.9]
    })

# Demo data options for the UI
DEMO_DATA_OPTIONS = {
    "Sales Performance": get_sales_performance_data,
    "Employee Analytics": get_employee_data,
    "Website Analytics": get_website_analytics_data,
    "Simple Sales Data": get_sample_dataframe
}

# Default user message for chat tab
DEFAULT_USER_MESSAGE = "Show me statistics for population growth in the US versus the world for the last 100 years"
