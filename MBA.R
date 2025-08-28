getwd()
setwd("/Users/s.d.h.fernando/Documents/Level 04 Sem 01 /CS 4104/2025/Assignment 01")

#Load the libraries for each task
library(readxl)

# Load the dataset
retail_data <- read_excel("Online Retail.xlsx")

# View structure & summary
str(retail_data)
summary(retail_data)

# Check missing values by column
colSums(is.na(retail_data))

# Focus on CustomerID and Description
sum(is.na(retail_data$CustomerID))
sum(is.na(retail_data$Description))

#Load the library to handle missing values
library(dplyr)

# Remove rows with missing CustomerID or Description
retail_data <- retail_data %>%
  filter(!is.na(CustomerID), !is.na(Description))

# Check remaining rows after handling the missing values. 
nrow(retail_data) 

library(stringr)

# Remove rows where InvoiceNo starts with "C"
retail_data <- retail_data %>%
  filter(!str_starts(InvoiceNo, "C"))

# Check remaining rows
nrow(retail_data)

# Filter positive Quantity and UnitPrice
retail_data <- retail_data %>%
  filter(Quantity > 0, UnitPrice > 0)

# Check min values
summary(retail_data$Quantity)
summary(retail_data$UnitPrice)

# Drop InvoiceNo & CustomerID (not needed for Apriori)
retail_data <- retail_data %>%
  select(-CustomerID, -InvoiceDate, -StockCode)

# Keep cleaned dataset
head(retail_data)

write.csv(retail_data, "Cleaned_OnlineRetail.csv", row.names = FALSE)

library(ggplot2)

# Count transactions per country
country_counts <- retail_data %>%
  group_by(Country) %>%
  summarise(Total = n()) %>%
  arrange(desc(Total))

# View top countries
head(country_counts, 10)

# Plot top 10 countries
ggplot(head(country_counts, 10), aes(x = reorder(Country, -Total), y = Total)) +
  geom_bar(stat = "identity", fill = "steelblue") +
  labs(title = "Top 10 Countries by Transactions", x = "Country", y = "Transaction Count") +
  theme_minimal()

#Quantity distribution
summary(retail_data$Quantity)
ggplot(retail_data, aes(x = Quantity))+
  geom_histogram(bins = 50, fill = "orange", color = "black") +
  xlim(0,100) +
  labs(title = "Distribution of Quantity", x = "Quantity", y = "Count")

#unit price distribution
summary(retail_data$UnitPrice)
ggplot(retail_data, aes(x = UnitPrice)) +
  geom_histogram(bins = 50, fill = "green", color = "black")+
  xlim (0,20) +
  labs(title = "Distribution of unit price", x = "Unit Price", y = "Count")

#Make the baskets 
# Top 3 countries by number of transactions
top_countries <- head(country_counts$Country, 3)
print(top_countries)

library(arules)
library(arulesViz)

#Apply Aprori algorithm

for (country in top_countries) {
  cat("\n====================", country, "====================\n")
  
  # Filter data for the country
  country_data <- retail_data %>% filter(Country == country)
  
  # Create transaction data: group products by InvoiceNo
  trans_data <- split(country_data$Description, country_data$InvoiceNo)
  
  # Convert to transactions
  trans <- as(trans_data, "transactions")
  
  # Summary of transactions
  cat("Number of transactions:", length(trans), "\n")
  inspect(trans[1:3])  # view first 3 transactions
  
  # Apply Apriori
  rules <- apriori(trans, parameter = list(supp = 0.01, conf = 0.5, minlen = 2))
  
  # Show top rules sorted by lift
  rules_sorted <- sort(rules, by="lift", decreasing=TRUE)
  inspect(head(rules_sorted, 10))
  
  # Plot rules
  plot(rules_sorted, method = "grouped")
}


