

import pandas as pd
import glob

for file in glob.glob(f"/workspaces/FinGPT/data/*.xlsx"):
    # Load Excel file
    xlsx = pd.ExcelFile(file)
    original_filename = file.split("/")[-1]
    # Loop through sheets
    for sheet in xlsx.sheet_names:

        # Read sheet into dataframe
        df = pd.read_excel(xlsx, sheet_name=sheet)

        # Save as CSV 
        csv_path = "data/" + original_filename + '_' + sheet + '.csv'
        df.to_csv(csv_path, index=False)

        print(f'Saved {sheet} as {csv_path}')