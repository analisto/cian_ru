#!/usr/bin/env python3
"""
Script to normalize wheat production data
- Cleans column names
- Converts from wide to long format
- Handles missing values
- Adds normalized metrics (percentage of world production)
"""

import pandas as pd
import numpy as np

def normalize_wheat_data(input_file='wheat_production_data.csv', output_file='wheat_production_normalized.csv'):
    """
    Normalizes the wheat production data
    """
    print(f"Reading data from: {input_file}")

    # Read the CSV file
    df = pd.read_csv(input_file)

    print(f"Original shape: {df.shape}")
    print(f"Original columns: {list(df.columns)[:5]}...")

    # Clean column names - remove [1] reference markers
    df.columns = [col.replace('[1]', '').strip() for col in df.columns]

    # Convert from wide to long format
    # Keep 'Country' as identifier, melt all year columns
    year_columns = [col for col in df.columns if col != 'Country']

    df_long = df.melt(
        id_vars=['Country'],
        value_vars=year_columns,
        var_name='Year',
        value_name='Production_Million_Tonnes'
    )

    # Convert Year to integer
    df_long['Year'] = df_long['Year'].astype(int)

    # Convert production to numeric (handle any non-numeric values)
    df_long['Production_Million_Tonnes'] = pd.to_numeric(
        df_long['Production_Million_Tonnes'],
        errors='coerce'
    )

    # Sort by Year and Country
    df_long = df_long.sort_values(['Year', 'Country']).reset_index(drop=True)

    # Calculate percentage of world production for each year
    def calculate_world_percentage(group):
        world_total = group[group['Country'] == 'World total']['Production_Million_Tonnes'].values
        if len(world_total) > 0 and world_total[0] > 0:
            group['Percentage_of_World'] = (group['Production_Million_Tonnes'] / world_total[0]) * 100
        else:
            group['Percentage_of_World'] = np.nan
        return group

    df_long = df_long.groupby('Year', group_keys=False).apply(calculate_world_percentage)

    # Add rank by production for each year
    def add_rank(group):
        # Exclude 'World total' from ranking
        group_without_world = group[group['Country'] != 'World total'].copy()
        group_without_world['Rank'] = group_without_world['Production_Million_Tonnes'].rank(
            ascending=False,
            method='min'
        ).astype('Int64')

        # Merge back
        group = group.merge(
            group_without_world[['Country', 'Rank']],
            on='Country',
            how='left'
        )
        return group

    df_long = df_long.groupby('Year', group_keys=False).apply(add_rank)

    # Round numeric columns for readability
    df_long['Production_Million_Tonnes'] = df_long['Production_Million_Tonnes'].round(2)
    df_long['Percentage_of_World'] = df_long['Percentage_of_World'].round(2)

    # Reorder columns
    df_long = df_long[['Country', 'Year', 'Production_Million_Tonnes',
                       'Percentage_of_World', 'Rank']]

    # Save normalized data
    df_long.to_csv(output_file, index=False, encoding='utf-8')

    print(f"\nNormalized data saved to: {output_file}")
    print(f"Normalized shape: {df_long.shape}")
    print(f"\nColumn names:")
    for col in df_long.columns:
        print(f"  - {col}")

    # Show some statistics
    print(f"\nData summary:")
    print(f"  Years covered: {df_long['Year'].min()} - {df_long['Year'].max()}")
    print(f"  Number of countries: {df_long['Country'].nunique()}")
    print(f"  Total records: {len(df_long)}")
    print(f"  Missing values: {df_long['Production_Million_Tonnes'].isna().sum()}")

    print(f"\nSample of normalized data (2022):")
    print(df_long[df_long['Year'] == 2022].head(10).to_string(index=False))

    print(f"\nTop 5 producers in 2022:")
    top_2022 = df_long[(df_long['Year'] == 2022) & (df_long['Country'] != 'World total')].nsmallest(5, 'Rank')
    print(top_2022.to_string(index=False))

    return df_long

if __name__ == "__main__":
    normalize_wheat_data()
