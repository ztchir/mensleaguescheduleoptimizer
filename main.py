import pandas as pd
from tools import optimize_schedule


if __name__ == "__main__":
    # Load the data, assuming it is in a CSV file
    csv_file = './data/schedule.csv'
    try:
        # Attempt to read the CSV file, skipping bad lines
        original_schedule_df = pd.read_csv(csv_file, header=0, index_col='Name', encoding='utf-8')
        original_schedule_df.fillna('NaN', inplace=True)
    except pd.errors.ParserError as e:
        print(f"Error reading CSV file: {e}")
        print("Attempting to read with different encoding...")
        try:
            # Attempt to read the CSV file with a different encoding
            original_schedule_df = pd.read_csv(csv_file, header=2, encoding='latin1', on_bad_lines='skip')
            original_schedule_df.fillna('NaN', inplace=True)
    

        except pd.errors.ParserError as e2:
            print(f"Error reading CSV file with alternate encoding: {e2}")
            print("Please ensure the CSV file is properly formatted and readable.")
            exit()  # Exit if the file cannot be read
    
    print(original_schedule_df.head())
    # Extract player names and date columns, handling potential errors
    players = list(original_schedule_df.index)
    dates = list(original_schedule_df.columns)

    # Create the schedule - use the global variable
    optimized_schedule = optimize_schedule(players, dates, original_schedule_df, iterations=1000)

    # Save the optimized schedule to a new CSV file
    optimized_schedule.to_csv("./data/optimized_golf_schedule.csv", index=True)
    print("Optimized schedule saved to optimized_golf_schedule.csv")