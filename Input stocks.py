# Step 1: Accept portfolio from user
portfolio = {}

print("Enter your stock portfolio.")
print("Type 'done' when you're finished.\n")

while True:
    ticker = input("Enter stock ticker (e.g., AAPL): ").upper()
    if ticker == 'DONE':
        break
    try:
        shares = int(input(f"Enter number of shares for {ticker}: "))
        portfolio[ticker] = shares
    except ValueError:
        print("Please enter a valid number.\n")

print("\nYour Portfolio:")
print(portfolio)
