
import pandas as pd
import matplotlib.pyplot as plt

def create_trendline_chart(csv_path, output_path):
    """
    Creates a publication-quality trendline chart from the APICURON data,
    plotting the cumulative count of integrations over the years and
    annotating with the names of the integrated resources.

    Args:
        csv_path (str): The path to the input CSV file.
        output_path (str): The path to save the output chart image.
    """
    # Read and sort the data by year
    df = pd.read_csv(csv_path).sort_values('Year Added')

    # Calculate the cumulative count of new resources per year
    cumulative_counts = df.groupby('Year Added').size().cumsum()

    # Group resource names by the year they were added
    resources_per_year = df.groupby('Year Added')['Resource Name'].apply(list)

    # Set a clean, publication-ready style for the plot
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot the cumulative integration count as a trendline
    ax.plot(cumulative_counts.index, cumulative_counts.values, marker='o', linestyle='-', color='darkblue')

    # Define specific placements for resource labels
    placements = {
        'DisProt': 'above', 'PED': 'above', 'Biomappings': 'above',
        'Pfam': 'below', 'Bioregistry': 'below',
        'PomBase': 'below', 'Rfam': 'below', 'BioModels': 'below',
        'Reactome': 'below', 'IntAct': 'below', 'Complex Portal': 'below',
        'SABIO-RK': 'below', 'DOME Registry': 'below', 'PDBe': 'below',
        'ELIXIR Training Materials': 'below', 'Glittr.org': 'below',
        'microPublication': 'below', 'S3 School': 'below'
    }

    # Add annotations with specific placement logic
    for year, resources in resources_per_year.items():
        count = cumulative_counts[year]
        
        year_placements_count = {'above': 0, 'below': 0}
        
        for name in sorted(resources): # Sort for consistent placement
            placement = placements.get(name, 'below') # Default to 'below'

            if placement == 'above':
                offset = 0.5 + year_placements_count['above'] * 0.5
                vertical_alignment = 'bottom'
                year_placements_count['above'] += 1
            else: # 'below'
                offset = -0.5 - year_placements_count['below'] * 0.5
                vertical_alignment = 'top'
                year_placements_count['below'] += 1

            ax.text(year, count + offset, name, ha='left', va=vertical_alignment, fontsize=9)

    # Set axis labels and font sizes
    ax.set_xlabel("Year", fontsize=14)
    ax.set_ylabel("APICURON integration count", fontsize=14)

    # Customize tick parameters for clarity
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.xaxis.get_major_locator().set_params(integer=True)
    ax.yaxis.get_major_locator().set_params(integer=True)
    
    # Adjust plot margins to ensure all annotations are visible
    plt.subplots_adjust(right=0.85)

    # Save the chart to a file
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    create_trendline_chart('APICURON_paper_figure_trend_data.csv', 'apicuron_trendline.png')
