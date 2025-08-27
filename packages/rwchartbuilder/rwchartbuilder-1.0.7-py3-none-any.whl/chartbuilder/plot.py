import pandas as pd
import matplotlib.pyplot as plt


def plot_dual_axis(df: pd.DataFrame, strBar: str, strLine: str):
    """
    Creates a dual y-axis chart with a bar plot and a line plot.

    Parameters:
    df (pd.DataFrame): The dataset containing the data.
    strBar (str): Column name for the bar chart.
    strLine (str): Column name for the line chart.
    """
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart on primary y-axis
    ax1.bar(df.index, df[strBar], color='lightgray', label=strBar)
    ax1.set_ylabel(strBar, color='lightgray')
    ax1.tick_params(axis='y', labelcolor='lightgray')

    # Line chart on secondary y-axis
    ax2 = ax1.twinx()
    ax2.plot(df.index, df[strLine], color='steelblue', linewidth=2, label=strLine)
    ax2.set_ylabel(strLine, color='steelblue')
    ax2.tick_params(axis='y', labelcolor='steelblue')

    # Title and layout
    plt.title(f'{strBar} vs {strLine} (Dual Axis)')
    fig.tight_layout()
    plt.show()

    return
