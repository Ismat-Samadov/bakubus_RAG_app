#!/usr/bin/env python3
"""
Bus Route Analysis - Business Intelligence Charts Generator
Generates business-focused visualizations for executive decision-making
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from collections import Counter

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11

# Create charts directory
CHARTS_DIR = Path("charts")
CHARTS_DIR.mkdir(exist_ok=True)

def load_data():
    """Load bus data from JSON file"""
    print("Loading bus route data...")
    with open('data/bus_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✓ Loaded data for {len(data)} bus routes\n")
    return data

def prepare_business_metrics(data):
    """Transform raw data into business-focused metrics"""
    print("Calculating business KPIs...")

    metrics = []
    for bus in data:
        # Skip buses with missing critical data
        if not bus.get('routLength') or not bus.get('durationMinuts'):
            continue

        metric = {
            'bus_number': bus.get('number', 'N/A'),
            'route_length_km': bus.get('routLength', 0),
            'duration_min': bus.get('durationMinuts', 0),
            'num_stops': len(bus.get('stops', [])),
            'carrier': bus.get('carrier', 'Unknown'),
            'tariff_azn': bus.get('tariff', 0) / 100 if bus.get('tariff') else 0,
            'region': bus.get('region', {}).get('name', 'Unknown'),
            'payment_type': bus.get('paymentType', {}).get('name', 'Unknown'),
            'working_zone': bus.get('workingZoneType', {}).get('name', 'Unknown'),
            'first_point': bus.get('firstPoint', 'N/A'),
            'last_point': bus.get('lastPoint', 'N/A'),
        }

        # Calculate derived KPIs
        metric['avg_speed_kmh'] = (metric['route_length_km'] / metric['duration_min'] * 60) if metric['duration_min'] > 0 else 0
        metric['stop_density'] = (metric['num_stops'] / metric['route_length_km']) if metric['route_length_km'] > 0 else 0
        metric['avg_distance_between_stops_km'] = (metric['route_length_km'] / metric['num_stops']) if metric['num_stops'] > 0 else 0

        # Count transport hubs
        metric['transport_hubs'] = sum(1 for stop in bus.get('stops', [])
                                      if stop.get('stop', {}).get('isTransportHub', False))

        metrics.append(metric)

    df = pd.DataFrame(metrics)
    print(f"✓ Processed {len(df)} routes with complete data\n")
    return df

def chart1_route_efficiency_ranking(df):
    """Top 15 Most Efficient Routes (Speed)"""
    print("Generating Chart 1: Route Efficiency Ranking...")

    top_15 = df.nlargest(15, 'avg_speed_kmh')[['bus_number', 'avg_speed_kmh']].sort_values('avg_speed_kmh')

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(range(len(top_15)), top_15['avg_speed_kmh'].values, color='#2ecc71')
    ax.set_yticks(range(len(top_15)))
    ax.set_yticklabels([f"Bus {num}" for num in top_15['bus_number'].values])
    ax.set_xlabel('Average Speed (km/h)')
    ax.set_title('Top 15 Fastest Bus Routes - Operational Efficiency Leaders', fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, (idx, row) in enumerate(top_15.iterrows()):
        ax.text(row['avg_speed_kmh'] + 0.5, i, f"{row['avg_speed_kmh']:.1f}", va='center')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '01_route_efficiency_ranking.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 01_route_efficiency_ranking.png")

def chart2_longest_journeys(df):
    """Routes with Longest Journey Times - Resource Intensity Analysis"""
    print("Generating Chart 2: Longest Journey Times...")

    top_15 = df.nlargest(15, 'duration_min')[['bus_number', 'duration_min', 'route_length_km']].sort_values('duration_min')

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(range(len(top_15)), top_15['duration_min'].values, color='#e74c3c')
    ax.set_yticks(range(len(top_15)))
    ax.set_yticklabels([f"Bus {num}" for num in top_15['bus_number'].values])
    ax.set_xlabel('Journey Time (minutes)')
    ax.set_title('Top 15 Longest Journey Times - Resource Intensive Routes', fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)

    # Add value labels with distance
    for i, (idx, row) in enumerate(top_15.iterrows()):
        ax.text(row['duration_min'] + 2, i, f"{int(row['duration_min'])} min\n({row['route_length_km']:.1f} km)",
                va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '02_longest_journeys.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 02_longest_journeys.png")

def chart3_top_carriers(df):
    """Top 10 Carriers - Market Leaders"""
    print("Generating Chart 3: Top 10 Carriers Analysis...")

    carrier_stats = df.groupby('carrier').agg({
        'bus_number': 'count',
        'route_length_km': 'sum',
        'avg_speed_kmh': 'mean'
    }).round(2)
    carrier_stats.columns = ['Routes', 'Coverage_km', 'Avg_Speed']
    top_10 = carrier_stats.nlargest(10, 'Routes').sort_values('Routes')

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(range(len(top_10)), top_10['Routes'].values, color='#3498db')
    ax.set_yticks(range(len(top_10)))
    ax.set_yticklabels(top_10.index)
    ax.set_xlabel('Number of Routes Operated', fontweight='bold')
    ax.set_title('Top 10 Carriers by Routes Operated - Market Share Leaders', fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)

    # Add value labels
    for i, (carrier, row) in enumerate(top_10.iterrows()):
        ax.text(row['Routes'] + 0.5, i, f"{int(row['Routes'])} routes\n{row['Coverage_km']:.0f} km",
                va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '03_top_carriers.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 03_top_carriers.png")

def chart4_route_length_distribution(df):
    """Route Length Categories - Service Design Analysis"""
    print("Generating Chart 4: Route Length Distribution...")

    # Categorize routes
    bins = [0, 10, 20, 30, 40, 100]
    labels = ['Short\n(0-10 km)', 'Medium\n(10-20 km)', 'Long\n(20-30 km)', 'Very Long\n(30-40 km)', 'Ultra Long\n(40+ km)']
    df['route_category'] = pd.cut(df['route_length_km'], bins=bins, labels=labels)

    category_counts = df['route_category'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.bar(range(len(category_counts)), category_counts.values, color='#16a085')
    ax.set_xticks(range(len(category_counts)))
    ax.set_xticklabels(category_counts.index)
    ax.set_ylabel('Number of Routes')
    ax.set_title('Route Length Distribution - Network Design Analysis', fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)

    for i, val in enumerate(category_counts.values):
        percentage = (val / len(df)) * 100
        ax.text(i, val + 1, f"{val}\n({percentage:.1f}%)", ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '04_route_length_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 04_route_length_distribution.png")

def chart5_stop_density_analysis(df):
    """Stop Density vs Route Length - Service Quality Indicator"""
    print("Generating Chart 5: Stop Density Analysis...")

    fig, ax = plt.subplots(figsize=(14, 8))

    scatter = ax.scatter(df['route_length_km'], df['stop_density'],
                        s=100, alpha=0.6, c=df['avg_speed_kmh'], cmap='RdYlGn')

    ax.set_xlabel('Route Length (km)', fontweight='bold')
    ax.set_ylabel('Stop Density (stops per km)', fontweight='bold')
    ax.set_title('Stop Density vs Route Length - Service Accessibility Analysis', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Avg Speed (km/h)', fontweight='bold')

    # Add reference lines
    avg_density = df['stop_density'].median()
    ax.axhline(y=avg_density, color='red', linestyle='--', alpha=0.5, label=f'Median Density: {avg_density:.2f}')
    ax.legend()

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '05_stop_density_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 05_stop_density_analysis.png")

def chart6_duration_vs_distance(df):
    """Travel Time vs Distance - Route Efficiency Matrix"""
    print("Generating Chart 6: Time-Distance Efficiency...")

    fig, ax = plt.subplots(figsize=(14, 8))

    scatter = ax.scatter(df['route_length_km'], df['duration_min'],
                        s=100, alpha=0.6, c=df['num_stops'], cmap='viridis')

    ax.set_xlabel('Route Length (km)', fontweight='bold')
    ax.set_ylabel('Travel Duration (minutes)', fontweight='bold')
    ax.set_title('Travel Time vs Distance - Operational Efficiency Matrix', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Number of Stops', fontweight='bold')

    # Add trend line
    z = np.polyfit(df['route_length_km'], df['duration_min'], 1)
    p = np.poly1d(z)
    ax.plot(df['route_length_km'].sort_values(), p(df['route_length_km'].sort_values()),
            "r--", alpha=0.8, linewidth=2, label=f'Trend: {z[0]:.1f} min/km')
    ax.legend()

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '06_duration_vs_distance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 06_duration_vs_distance.png")

def chart7_transport_hub_coverage(df):
    """Transport Hub Integration - Network Connectivity"""
    print("Generating Chart 7: Transport Hub Analysis...")

    # Routes with most transport hubs
    top_hub_routes = df.nlargest(15, 'transport_hubs')[['bus_number', 'transport_hubs', 'num_stops']].sort_values('transport_hubs')

    fig, ax = plt.subplots(figsize=(12, 8))

    x = range(len(top_hub_routes))
    width = 0.35

    ax.barh([i - width/2 for i in x], top_hub_routes['transport_hubs'].values,
            width, label='Transport Hubs', color='#e67e22')
    ax.barh([i + width/2 for i in x], top_hub_routes['num_stops'].values,
            width, label='Total Stops', color='#95a5a6', alpha=0.6)

    ax.set_yticks(x)
    ax.set_yticklabels([f"Bus {num}" for num in top_hub_routes['bus_number'].values])
    ax.set_xlabel('Count')
    ax.set_title('Top 15 Routes by Transport Hub Integration - Network Connectivity', fontweight='bold', pad=20)
    ax.legend()
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '07_transport_hub_coverage.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 07_transport_hub_coverage.png")

def chart8_payment_methods(df):
    """Payment Method Adoption - Revenue Collection Analysis"""
    print("Generating Chart 8: Payment Method Distribution...")

    payment_counts = df['payment_type'].value_counts()

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.bar(range(len(payment_counts)), payment_counts.values, color='#27ae60')
    ax.set_xticks(range(len(payment_counts)))
    ax.set_xticklabels(payment_counts.index, rotation=45, ha='right')
    ax.set_ylabel('Number of Routes')
    ax.set_title('Payment Method Distribution Across Routes', fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)

    for i, val in enumerate(payment_counts.values):
        percentage = (val / len(df)) * 100
        ax.text(i, val + 2, f"{val}\n({percentage:.1f}%)", ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '08_payment_methods.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 08_payment_methods.png")

def chart9_tariff_analysis(df):
    """Tariff Structure - Pricing Strategy Overview"""
    print("Generating Chart 9: Tariff Analysis...")

    tariff_counts = df['tariff_azn'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.bar(range(len(tariff_counts)), tariff_counts.values, color='#f39c12')
    ax.set_xticks(range(len(tariff_counts)))
    ax.set_xticklabels([f"{val:.2f} AZN" for val in tariff_counts.index])
    ax.set_ylabel('Number of Routes')
    ax.set_title('Tariff Distribution - Pricing Strategy Analysis', fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)

    for i, val in enumerate(tariff_counts.values):
        percentage = (val / len(df)) * 100
        ax.text(i, val + 2, f"{val}\n({percentage:.1f}%)", ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '09_tariff_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 09_tariff_analysis.png")

def chart10_regional_coverage(df):
    """Regional Service Distribution"""
    print("Generating Chart 10: Regional Coverage...")

    region_stats = df.groupby('region').agg({
        'bus_number': 'count',
        'route_length_km': 'sum'
    }).sort_values('bus_number', ascending=False)
    region_stats.columns = ['Routes', 'Total Coverage (km)']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # Routes by region
    ax1.bar(range(len(region_stats)), region_stats['Routes'].values, color='#8e44ad')
    ax1.set_xticks(range(len(region_stats)))
    ax1.set_xticklabels(region_stats.index, rotation=45, ha='right')
    ax1.set_ylabel('Number of Routes')
    ax1.set_title('Routes by Region', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    for i, val in enumerate(region_stats['Routes'].values):
        ax1.text(i, val + 1, str(int(val)), ha='center', va='bottom', fontweight='bold')

    # Coverage by region
    ax2.bar(range(len(region_stats)), region_stats['Total Coverage (km)'].values, color='#c0392b')
    ax2.set_xticks(range(len(region_stats)))
    ax2.set_xticklabels(region_stats.index, rotation=45, ha='right')
    ax2.set_ylabel('Total Route Length (km)')
    ax2.set_title('Network Coverage by Region', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)

    for i, val in enumerate(region_stats['Total Coverage (km)'].values):
        ax2.text(i, val + 20, f"{val:.0f}", ha='center', va='bottom', fontweight='bold')

    plt.suptitle('Regional Service Distribution Analysis', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '10_regional_coverage.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 10_regional_coverage.png")

def chart11_avg_stop_distance(df):
    """Average Distance Between Stops - Service Frequency Indicator"""
    print("Generating Chart 11: Stop Spacing Analysis...")

    # Get top 20 routes by stop spacing
    top_spacing = df.nlargest(20, 'avg_distance_between_stops_km')[['bus_number', 'avg_distance_between_stops_km']].sort_values('avg_distance_between_stops_km', ascending=False)
    bottom_spacing = df.nsmallest(20, 'avg_distance_between_stops_km')[['bus_number', 'avg_distance_between_stops_km']].sort_values('avg_distance_between_stops_km')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Express routes (large spacing)
    ax1.barh(range(len(top_spacing)), top_spacing['avg_distance_between_stops_km'].values, color='#16a085')
    ax1.set_yticks(range(len(top_spacing)))
    ax1.set_yticklabels([f"Bus {num}" for num in top_spacing['bus_number'].values])
    ax1.set_xlabel('Avg Distance Between Stops (km)')
    ax1.set_title('Express/Rapid Routes (Larger Stop Spacing)', fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)

    # Local routes (small spacing)
    ax2.barh(range(len(bottom_spacing)), bottom_spacing['avg_distance_between_stops_km'].values, color='#d35400')
    ax2.set_yticks(range(len(bottom_spacing)))
    ax2.set_yticklabels([f"Bus {num}" for num in bottom_spacing['bus_number'].values])
    ax2.set_xlabel('Avg Distance Between Stops (km)')
    ax2.set_title('Local Routes (Dense Stop Spacing)', fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)

    plt.suptitle('Stop Spacing Analysis - Service Type Classification', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '11_avg_stop_distance.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 11_avg_stop_distance.png")

def chart12_efficiency_matrix(df):
    """Route Performance Quadrant Analysis"""
    print("Generating Chart 12: Performance Quadrant Matrix...")

    median_speed = df['avg_speed_kmh'].median()
    median_stops = df['num_stops'].median()

    fig, ax = plt.subplots(figsize=(14, 10))

    # Color by quadrant
    colors = []
    for _, row in df.iterrows():
        if row['avg_speed_kmh'] >= median_speed and row['num_stops'] >= median_stops:
            colors.append('#2ecc71')  # High efficiency, high coverage
        elif row['avg_speed_kmh'] >= median_speed and row['num_stops'] < median_stops:
            colors.append('#3498db')  # High efficiency, low coverage
        elif row['avg_speed_kmh'] < median_speed and row['num_stops'] >= median_stops:
            colors.append('#f39c12')  # Low efficiency, high coverage
        else:
            colors.append('#e74c3c')  # Low efficiency, low coverage

    scatter = ax.scatter(df['num_stops'], df['avg_speed_kmh'],
                        c=colors, s=100, alpha=0.6, edgecolors='black', linewidth=0.5)

    ax.axhline(y=median_speed, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=median_stops, color='gray', linestyle='--', alpha=0.5)

    ax.set_xlabel('Number of Stops', fontweight='bold')
    ax.set_ylabel('Average Speed (km/h)', fontweight='bold')
    ax.set_title('Route Performance Quadrant Analysis', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)

    # Add quadrant labels
    ax.text(df['num_stops'].max() * 0.75, df['avg_speed_kmh'].max() * 0.95,
            'High Coverage\nHigh Efficiency', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.3))
    ax.text(df['num_stops'].min() * 1.5, df['avg_speed_kmh'].max() * 0.95,
            'Express Routes\nHigh Efficiency', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='#3498db', alpha=0.3))
    ax.text(df['num_stops'].max() * 0.75, df['avg_speed_kmh'].min() * 1.2,
            'High Coverage\nNeeds Optimization', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.3))
    ax.text(df['num_stops'].min() * 1.5, df['avg_speed_kmh'].min() * 1.2,
            'Low Coverage\nNeeds Review', ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.3))

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '12_efficiency_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: 12_efficiency_matrix.png")

def generate_summary_statistics(df):
    """Generate summary statistics for README"""
    stats = {
        'total_routes': int(len(df)),
        'total_network_km': float(df['route_length_km'].sum()),
        'avg_route_length': float(df['route_length_km'].mean()),
        'avg_speed': float(df['avg_speed_kmh'].mean()),
        'total_stops': int(df['num_stops'].sum()),
        'avg_stops_per_route': float(df['num_stops'].mean()),
        'fastest_route': str(df.loc[df['avg_speed_kmh'].idxmax(), 'bus_number']),
        'fastest_speed': float(df['avg_speed_kmh'].max()),
        'slowest_route': str(df.loc[df['avg_speed_kmh'].idxmin(), 'bus_number']),
        'slowest_speed': float(df['avg_speed_kmh'].min()),
        'longest_route': str(df.loc[df['route_length_km'].idxmax(), 'bus_number']),
        'longest_distance': float(df['route_length_km'].max()),
        'carriers': int(df['carrier'].nunique()),
        'regions': int(df['region'].nunique()),
        'avg_tariff': float(df['tariff_azn'].mean()),
        'total_hubs': int(df['transport_hubs'].sum()),
    }
    return stats

def main():
    """Main execution function"""
    print("=" * 70)
    print("BUS ROUTE BUSINESS INTELLIGENCE ANALYSIS")
    print("=" * 70)
    print()

    # Load and prepare data
    data = load_data()
    df = prepare_business_metrics(data)

    # Generate all charts
    print("Generating business intelligence charts...")
    print("-" * 70)

    chart1_route_efficiency_ranking(df)
    chart2_longest_journeys(df)
    chart3_top_carriers(df)
    chart4_route_length_distribution(df)
    chart5_stop_density_analysis(df)
    chart6_duration_vs_distance(df)
    chart7_transport_hub_coverage(df)
    chart8_payment_methods(df)
    chart9_tariff_analysis(df)
    chart10_regional_coverage(df)
    chart11_avg_stop_distance(df)
    chart12_efficiency_matrix(df)

    print("-" * 70)
    print(f"\n✓ All charts generated successfully in '{CHARTS_DIR}/' directory\n")

    # Generate and save summary statistics
    stats = generate_summary_statistics(df)
    with open('charts/summary_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print("✓ Summary statistics saved to 'charts/summary_stats.json'\n")

    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\nKey Metrics:")
    print(f"  • Total Routes Analyzed: {stats['total_routes']}")
    print(f"  • Total Network Coverage: {stats['total_network_km']:.1f} km")
    print(f"  • Total Stops: {int(stats['total_stops'])}")
    print(f"  • Average Route Speed: {stats['avg_speed']:.1f} km/h")
    print(f"  • Number of Carriers: {stats['carriers']}")
    print(f"  • Transport Hubs: {int(stats['total_hubs'])}")
    print()

if __name__ == "__main__":
    main()
