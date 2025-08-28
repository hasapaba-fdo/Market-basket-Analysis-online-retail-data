import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
df = pd.read_excel("Online Retail.xlsx")

# --- Check structure & summary ---
print(df.info())
print(df.describe())
print(df.isnull().sum())

# --- Remove missing CustomerID or Description ---
df = df.dropna(subset=["CustomerID", "Description"])

# --- Remove cancellations (InvoiceNo starting with 'C') ---
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

# --- Keep only positive Quantity & UnitPrice ---
df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

# --- Save cleaned dataset ---
df_clean = df.drop(columns=["CustomerID", "InvoiceDate", "StockCode"])
df_clean.to_csv("Cleaned_OnlineRetail.csv", index=False)

# --- Country distribution ---
country_counts = df_clean["Country"].value_counts()
print(country_counts.head(10))

sns.barplot(x=country_counts.head(10).index, y=country_counts.head(10).values)
plt.title("Top 10 Countries by Transactions")
plt.xticks(rotation=45)
plt.show()

# --- Quantity distribution ---
sns.histplot(df_clean["Quantity"], bins=50, color="orange")
plt.xlim(0,100)
plt.title("Quantity Distribution")
plt.show()

# --- Unit Price distribution ---
sns.histplot(df_clean["UnitPrice"], bins=50, color="green")
plt.xlim(0,20)
plt.title("Unit Price Distribution")
plt.show()

# --- Correlation ---
print(df_clean[["Quantity", "UnitPrice"]].corr())

from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd

# Assuming df_clean is your cleaned dataframe from before

top_countries = df_clean["Country"].value_counts().head(3).index
print("Top 3 Countries:", list(top_countries))

for country in top_countries:
    print(f"\n=== Apriori for {country} ===")

    # Filter data for the country
    country_data = df_clean[df_clean["Country"] == country]

    # Group items by InvoiceNo into baskets
    baskets = country_data.groupby("InvoiceNo")["Description"].apply(list).tolist()

    # Encode transactions
    te = TransactionEncoder()
    te_array = te.fit(baskets).transform(baskets)
    country_df = pd.DataFrame(te_array, columns=te.columns_)

    # Apply Apriori (support=1%, confidence=50%)
    frequent_itemsets = apriori(country_df, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

    # Sort rules by lift descending
    rules_sorted = rules.sort_values(by="lift", ascending=False)


    # Prepare rules for saving (convert frozensets to strings)
    def frozenset_to_string(x):
        return ', '.join(list(x))


    def clean_and_format_items(x):
        # Remove leading/trailing spaces and title case each item
        items = [item.strip().title() for item in x.split(',')]
        return ", ".join(items)


    # Apply the formatting function to antecedents and consequents after converting frozenset to string
    rules_sorted["antecedents"] = rules_sorted["antecedents"].apply(frozenset_to_string).apply(clean_and_format_items)
    rules_sorted["consequents"] = rules_sorted["consequents"].apply(frozenset_to_string).apply(clean_and_format_items)

    # Round numerical columns for better readability
    rules_sorted["support"] = rules_sorted["support"].round(4)
    rules_sorted["confidence"] = (rules_sorted["confidence"] * 100).round(4)  # in %
    rules_sorted["lift"] = rules_sorted["lift"].round(4)
    rules_sorted["leverage"] = rules_sorted["leverage"].round(4)
    rules_sorted["conviction"] = rules_sorted["conviction"].round(4)

    # Optionally convert confidence to a string with % symbol
    rules_sorted["confidence"] = rules_sorted["confidence"].astype(str) + "%"

    # Select relevant columns to save
    rules_to_save = rules_sorted[
        ["antecedents", "consequents", "support", "confidence", "lift", "leverage", "conviction"]]

    # Save to CSV
    filename = f"association_rules_{country.replace(' ', '_')}.csv"
    rules_to_save.to_csv(filename, index=False)

    print(f"Saved {len(rules_to_save)} rules to {filename}")







