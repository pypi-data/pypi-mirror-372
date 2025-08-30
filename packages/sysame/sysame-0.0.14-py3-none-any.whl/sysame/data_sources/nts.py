"""
Module Description: Briefly describe the module's purpose.
"""

##### IMPORTS #####
# Standard imports

# Third-party imports
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt


# Local imports

# Import Rules

##### CONSTANTS #####
# Define constants here

##### GLOBALS #####
# Define global variables here (use with caution)

##### CLASSES #####
# Define classes here


##### FUNCTIONS #####
def plot_income_distribution(df):
    """
    Plots the distribution of income categories across years.

    Parameters:
    df (pd.DataFrame): A DataFrame with columns 'income_category' and 'year'.
    """
    # Count occurrences of each income category per year
    income_dist = (
        df.groupby(["TWSYear", "HHIncome2002_B02ID"]).size().unstack(fill_value=0)
    )

    # Normalize to get proportions
    income_dist = income_dist.div(income_dist.sum(axis=1), axis=0)

    # Plot as stacked area chart
    plt.figure(figsize=(10, 6))
    income_dist.plot(kind="area", stacked=True, colormap="viridis", alpha=0.8)

    plt.title("Income Category Distribution Across Years")
    plt.xlabel("Year")
    plt.ylabel("Proportion")
    plt.legend(title="Income Category", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    plt.show()


##### MAIN #####
def main():
    """
    The main function of the module.
    """
    # read tab delimited file
    df = pd.read_csv(
        r"C:\Users\misht\OneDrive\Cloud\Data\NTS\UKDA-5340-tab\tab\household_eul_2002-2023.tab",
        sep="\t",
    )
    df = df[["HHIncome2002_B02ID", "TWSYear", "HHoldGOR_B02ID"]]
    # cast to integer
    for col in ["HHIncome2002_B02ID", "HHoldGOR_B02ID", "TWSYear"]:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )  # Convert to numeric, set invalid to NaN
        df = df.dropna(subset=[col])  # Remove rows with NaN values
        df[col] = df[col].astype(int)  # Convert valid values to int
        df = df.loc[df[col] > 0]
    df = df.loc[df["HHoldGOR_B02ID"] == 2]
    df = df.loc[df["TWSYear"] >= 2019]
    plot_income_distribution(df)
    #
    print("here!")


##### RUN #####
if __name__ == "__main__":
    main()
