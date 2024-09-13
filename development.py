import pandas as pd

# Load CSV files (assume the CSV files are named as follows and stored in the same directory)
weight_male_df = pd.read_csv('weight_male.csv')
height_male_df = pd.read_csv('height_male.csv')
weight_female_df = pd.read_csv('weight_female.csv')
height_female_df = pd.read_csv('height_female.csv')

def find_percentile(age, value, df):
    """Finds the percentile category for a given age and value in the data."""
    row = df[df['Age (months)'] == age]
    if row.empty:
        return "Age not in data"
    
    percentiles = ["3rd percentile", "50th percentile", "97th percentile"]
    for i in range(len(percentiles) - 1):
        lower_bound = row[percentiles[i]].values[0]
        upper_bound = row[percentiles[i + 1]].values[0]
        if lower_bound <= value <= upper_bound:
            return f"Between {percentiles[i]} and {percentiles[i + 1]}"
    
    if value < row["3rd percentile"].values[0]:
        return "Below 3rd percentile"
    elif value > row["97th percentile"].values[0]:
        return "Above 97th percentile"
    
    return "Within 50th percentile"

# Main program
def analyze_child_growth():
    try:
        # Input section
        gender = input("Enter child's gender (male/female): ").strip().lower()
        child_age = int(input("Enter child's age in months: "))
        child_weight = float(input("Enter child's weight in kg: "))
        child_height = float(input("Enter child's height in cm: "))
        
        # Determine which data to use based on gender
        if gender == "male":
            weight_df = weight_male_df
            height_df = height_male_df
        elif gender == "female":
            weight_df = weight_female_df
            height_df = height_female_df
        else:
            print("Invalid gender. Please enter 'male' or 'female'.")
            return
        
        # Analyze weight and height percentiles
        weight_percentile = find_percentile(child_age, child_weight, weight_df)
        height_percentile = find_percentile(child_age, child_height, height_df)
        
        # Output
        print(f"Weight Percentile: {weight_percentile}")
        print(f"Height Percentile: {height_percentile}")
    
    except ValueError:
        print("Invalid input. Please enter numeric values for age, weight, and height.")

# Call the function
analyze_child_growth()