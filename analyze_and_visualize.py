#!/usr/bin/env python3
"""
Comprehensive wheat production analysis and visualization
Generates charts and extracts insights for presentation
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style for better-looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 10

# Create charts directory
CHARTS_DIR = Path("charts")
CHARTS_DIR.mkdir(exist_ok=True)

def load_data():
    """Load normalized wheat production data"""
    df = pd.read_csv('wheat_production_normalized.csv')
    return df

def chart1_global_production_trend(df):
    """Chart: Global wheat production trend over time"""
    world_data = df[df['Country'] == 'World total'].copy()

    plt.figure(figsize=(14, 7))
    plt.plot(world_data['Year'], world_data['Production_Million_Tonnes'],
             marker='o', linewidth=2, markersize=6, color='#2E86AB')

    # Add trend line
    z = np.polyfit(world_data['Year'], world_data['Production_Million_Tonnes'], 1)
    p = np.poly1d(z)
    plt.plot(world_data['Year'], p(world_data['Year']),
             "--", alpha=0.8, color='#A23B72', linewidth=2, label=f'Trend')

    plt.title('Global Wheat Production (1996-2022)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Production (Million Tonnes)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '01_global_production_trend.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Calculate growth
    growth = ((world_data.iloc[-1]['Production_Million_Tonnes'] -
               world_data.iloc[0]['Production_Million_Tonnes']) /
              world_data.iloc[0]['Production_Million_Tonnes'] * 100)

    return {
        'chart': '01_global_production_trend.png',
        'insight': f"Global wheat production increased by {growth:.1f}% from 1996 to 2022, growing from {world_data.iloc[0]['Production_Million_Tonnes']:.1f}M to {world_data.iloc[-1]['Production_Million_Tonnes']:.1f}M tonnes."
    }

def chart2_top_producers_comparison(df):
    """Chart: Top 10 producers in 2022 vs 1996"""
    top_2022 = df[(df['Year'] == 2022) & (df['Country'] != 'World total')].nsmallest(10, 'Rank')
    countries = top_2022['Country'].tolist()

    data_1996 = df[(df['Year'] == 1996) & (df['Country'].isin(countries))]
    data_2022 = df[(df['Year'] == 2022) & (df['Country'].isin(countries))]

    fig, ax = plt.subplots(figsize=(14, 8))
    x = np.arange(len(countries))
    width = 0.35

    bars1 = ax.bar(x - width/2, data_1996.set_index('Country').loc[countries, 'Production_Million_Tonnes'],
                   width, label='1996', color='#F18F01', alpha=0.8)
    bars2 = ax.bar(x + width/2, data_2022.set_index('Country').loc[countries, 'Production_Million_Tonnes'],
                   width, label='2022', color='#2E86AB', alpha=0.8)

    ax.set_xlabel('Country', fontsize=12)
    ax.set_ylabel('Production (Million Tonnes)', fontsize=12)
    ax.set_title('Top 10 Wheat Producers: 1996 vs 2022', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(countries, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '02_top_producers_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Find biggest grower
    growth_df = data_2022.set_index('Country')['Production_Million_Tonnes'] - data_1996.set_index('Country')['Production_Million_Tonnes']
    biggest_grower = growth_df.idxmax()
    growth_amount = growth_df.max()

    return {
        'chart': '02_top_producers_comparison.png',
        'insight': f"{biggest_grower} showed the largest absolute growth among top producers, increasing production by {growth_amount:.1f}M tonnes between 1996 and 2022."
    }

def chart3_market_share_evolution(df):
    """Chart: Market share evolution of top 5 producers"""
    top_5_2022 = df[(df['Year'] == 2022) & (df['Country'] != 'World total')].nsmallest(5, 'Rank')['Country'].tolist()

    plt.figure(figsize=(14, 8))

    for country in top_5_2022:
        country_data = df[df['Country'] == country].sort_values('Year')
        plt.plot(country_data['Year'], country_data['Percentage_of_World'],
                marker='o', linewidth=2, markersize=4, label=country)

    plt.title('Market Share Evolution: Top 5 Producers (1996-2022)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Percentage of World Production (%)', fontsize=12)
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '03_market_share_evolution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Analyze market concentration
    top5_share_1996 = df[(df['Year'] == 1996) & (df['Country'].isin(top_5_2022))]['Percentage_of_World'].sum()
    top5_share_2022 = df[(df['Year'] == 2022) & (df['Country'].isin(top_5_2022))]['Percentage_of_World'].sum()

    return {
        'chart': '03_market_share_evolution.png',
        'insight': f"The top 5 producers controlled {top5_share_2022:.1f}% of global wheat production in 2022, compared to {top5_share_1996:.1f}% in 1996, showing {'increased' if top5_share_2022 > top5_share_1996 else 'decreased'} market concentration."
    }

def chart4_growth_rates(df):
    """Chart: Growth rates by country (1996-2022)"""
    countries = df[(df['Year'] == 2022) & (df['Country'] != 'World total')].nsmallest(15, 'Rank')['Country'].tolist()

    growth_rates = []
    for country in countries:
        prod_1996 = df[(df['Country'] == country) & (df['Year'] == 1996)]['Production_Million_Tonnes'].values[0]
        prod_2022 = df[(df['Country'] == country) & (df['Year'] == 2022)]['Production_Million_Tonnes'].values[0]
        growth_rate = ((prod_2022 - prod_1996) / prod_1996) * 100
        growth_rates.append(growth_rate)

    # Sort by growth rate
    sorted_data = sorted(zip(countries, growth_rates), key=lambda x: x[1], reverse=True)
    sorted_countries, sorted_rates = zip(*sorted_data)

    plt.figure(figsize=(14, 8))
    colors = ['#06A77D' if x > 0 else '#D62828' for x in sorted_rates]
    bars = plt.barh(sorted_countries, sorted_rates, color=colors, alpha=0.8)

    plt.xlabel('Growth Rate (%)', fontsize=12)
    plt.ylabel('Country', fontsize=12)
    plt.title('Wheat Production Growth Rate by Country (1996-2022)', fontsize=16, fontweight='bold', pad=20)
    plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    plt.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '04_growth_rates.png', dpi=300, bbox_inches='tight')
    plt.close()

    fastest_grower = sorted_countries[0]
    fastest_rate = sorted_rates[0]

    return {
        'chart': '04_growth_rates.png',
        'insight': f"{fastest_grower} had the highest growth rate at {fastest_rate:.1f}%, while some countries experienced production declines over the 26-year period."
    }

def chart5_volatility_analysis(df):
    """Chart: Production volatility by country"""
    countries = df[(df['Year'] == 2022) & (df['Country'] != 'World total')].nsmallest(12, 'Rank')['Country'].tolist()

    volatility_data = []
    avg_production = []

    for country in countries:
        country_data = df[df['Country'] == country]['Production_Million_Tonnes']
        volatility = country_data.std() / country_data.mean() * 100  # Coefficient of variation
        volatility_data.append(volatility)
        avg_production.append(country_data.mean())

    fig, ax = plt.subplots(figsize=(14, 8))
    scatter = ax.scatter(avg_production, volatility_data, s=200, alpha=0.6, c=range(len(countries)), cmap='viridis')

    for i, country in enumerate(countries):
        ax.annotate(country, (avg_production[i], volatility_data[i]),
                   fontsize=9, ha='center', va='bottom')

    ax.set_xlabel('Average Production (Million Tonnes)', fontsize=12)
    ax.set_ylabel('Production Volatility (Coefficient of Variation %)', fontsize=12)
    ax.set_title('Production Stability vs Scale: Top 12 Producers', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '05_volatility_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()

    most_volatile_idx = volatility_data.index(max(volatility_data))
    most_stable_idx = volatility_data.index(min(volatility_data))

    return {
        'chart': '05_volatility_analysis.png',
        'insight': f"{countries[most_volatile_idx]} shows the highest production volatility ({volatility_data[most_volatile_idx]:.1f}%), while {countries[most_stable_idx]} has the most stable production ({volatility_data[most_stable_idx]:.1f}%)."
    }

def chart6_recent_trends(df):
    """Chart: Recent trends (2018-2022)"""
    recent_years = [2018, 2019, 2020, 2021, 2022]
    top_countries = df[(df['Year'] == 2022) & (df['Country'] != 'World total')].nsmallest(8, 'Rank')['Country'].tolist()

    fig, ax = plt.subplots(figsize=(14, 8))

    for country in top_countries:
        country_data = df[(df['Country'] == country) & (df['Year'].isin(recent_years))].sort_values('Year')
        ax.plot(country_data['Year'], country_data['Production_Million_Tonnes'],
               marker='o', linewidth=2.5, markersize=8, label=country)

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Production (Million Tonnes)', fontsize=12)
    ax.set_title('Recent Production Trends: Top 8 Producers (2018-2022)', fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(recent_years)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '06_recent_trends.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Analyze 2020-2022 trend (COVID period)
    world_2020 = df[(df['Year'] == 2020) & (df['Country'] == 'World total')]['Production_Million_Tonnes'].values[0]
    world_2022 = df[(df['Year'] == 2022) & (df['Country'] == 'World total')]['Production_Million_Tonnes'].values[0]
    covid_growth = ((world_2022 - world_2020) / world_2020) * 100

    return {
        'chart': '06_recent_trends.png',
        'insight': f"Despite global disruptions (2020-2022), world wheat production increased by {covid_growth:.1f}%, demonstrating sector resilience."
    }

def chart7_regional_contribution(df):
    """Chart: Regional/continental contribution heatmap"""
    # Define regional groupings
    regions = {
        'Asia': ['China', 'India', 'Pakistan', 'Turkey', 'Iran', 'Kazakhstan', 'Uzbekistan', 'Afghanistan', 'Bangladesh', 'Syria', 'Iraq', 'Myanmar'],
        'Europe': ['Russia', 'France', 'Germany', 'Ukraine', 'Poland', 'United Kingdom', 'Romania', 'Spain', 'Italy', 'Czech Republic', 'Denmark', 'Bulgaria', 'Hungary', 'Lithuania', 'Serbia'],
        'North America': ['United States', 'Canada', 'Mexico'],
        'South America': ['Argentina', 'Brazil'],
        'Oceania': ['Australia'],
        'Africa': ['Egypt', 'Morocco', 'Algeria', 'Ethiopia', 'South Africa', 'Kenya', 'Tanzania']
    }

    # Calculate regional production by year
    years = sorted(df['Year'].unique())
    regional_data = {region: [] for region in regions.keys()}

    for year in years:
        year_data = df[df['Year'] == year]
        for region, countries in regions.items():
            region_prod = year_data[year_data['Country'].isin(countries)]['Production_Million_Tonnes'].sum()
            regional_data[region].append(region_prod)

    # Create stacked area chart
    plt.figure(figsize=(14, 8))
    plt.stackplot(years, *[regional_data[region] for region in regions.keys()],
                 labels=regions.keys(), alpha=0.8)

    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Production (Million Tonnes)', fontsize=12)
    plt.title('Global Wheat Production by Region (1996-2022)', fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '07_regional_contribution.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Calculate dominant region
    region_2022 = {region: regional_data[region][-1] for region in regions.keys()}
    dominant_region = max(region_2022, key=region_2022.get)

    return {
        'chart': '07_regional_contribution.png',
        'insight': f"{dominant_region} dominates global wheat production with {region_2022[dominant_region]:.1f}M tonnes in 2022, accounting for a significant share of world output."
    }

def generate_insights_summary(all_insights):
    """Generate comprehensive insights summary"""
    insights = {
        'key_findings': [],
        'trends': [],
        'leaders': [],
        'challenges': []
    }

    # Extract specific insights from data
    df = load_data()

    # Key finding 1: Overall growth
    world_1996 = df[(df['Year'] == 1996) & (df['Country'] == 'World total')]['Production_Million_Tonnes'].values[0]
    world_2022 = df[(df['Year'] == 2022) & (df['Country'] == 'World total')]['Production_Million_Tonnes'].values[0]
    total_growth = ((world_2022 - world_1996) / world_1996) * 100
    insights['key_findings'].append(f"Global wheat production grew {total_growth:.1f}% over 26 years ({world_1996:.1f}M to {world_2022:.1f}M tonnes)")

    # Top 3 producers
    top_3 = df[(df['Year'] == 2022) & (df['Country'] != 'World total')].nsmallest(3, 'Rank')
    top_3_share = top_3['Percentage_of_World'].sum()
    insights['leaders'].append(f"Top 3 producers (China, India, Russia) control {top_3_share:.1f}% of global production")

    # Growth champions
    countries = df[(df['Year'] == 2022) & (df['Country'] != 'World total')]['Country'].unique()
    max_growth = -999
    growth_champion = ""
    for country in countries:
        try:
            prod_1996 = df[(df['Country'] == country) & (df['Year'] == 1996)]['Production_Million_Tonnes'].values[0]
            prod_2022 = df[(df['Country'] == country) & (df['Year'] == 2022)]['Production_Million_Tonnes'].values[0]
            if prod_1996 > 10:  # Only consider significant producers
                growth = ((prod_2022 - prod_1996) / prod_1996) * 100
                if growth > max_growth:
                    max_growth = growth
                    growth_champion = country
        except:
            pass

    if growth_champion:
        insights['trends'].append(f"{growth_champion} leads in growth rate with {max_growth:.1f}% increase since 1996")

    # Recent resilience
    insights['trends'].append("Production remained resilient during 2020-2022 global disruptions")

    # Market concentration
    insights['challenges'].append("Increasing market concentration among top producers raises supply chain risks")

    return insights

def main():
    """Main analysis function"""
    print("=" * 60)
    print("WHEAT PRODUCTION ANALYSIS AND VISUALIZATION")
    print("=" * 60)
    print()

    # Load data
    print("Loading data...")
    df = load_data()
    print(f"✓ Loaded {len(df)} records covering {df['Year'].nunique()} years and {df['Country'].nunique()} countries\n")

    # Generate charts
    all_insights = []

    print("Generating charts...")
    print("-" * 60)

    charts = [
        ("Global Production Trend", chart1_global_production_trend),
        ("Top Producers Comparison", chart2_top_producers_comparison),
        ("Market Share Evolution", chart3_market_share_evolution),
        ("Growth Rates Analysis", chart4_growth_rates),
        ("Volatility Analysis", chart5_volatility_analysis),
        ("Recent Trends", chart6_recent_trends),
        ("Regional Contribution", chart7_regional_contribution)
    ]

    for i, (name, func) in enumerate(charts, 1):
        print(f"{i}. {name}...", end=" ")
        result = func(df)
        all_insights.append(result)
        print(f"✓ Saved: {result['chart']}")

    print()
    print(f"✓ All charts saved to '{CHARTS_DIR}/' directory")
    print()

    # Generate insights summary
    print("Generating insights summary...")
    insights = generate_insights_summary(all_insights)

    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print()
    print("Charts generated:")
    for i, result in enumerate(all_insights, 1):
        print(f"  {i}. {result['chart']}")
    print()
    print("Key Insights:")
    for insight in all_insights:
        print(f"  • {insight['insight']}")
    print()

    return all_insights, insights

if __name__ == "__main__":
    main()
