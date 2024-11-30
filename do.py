
def step_up_calculator():
    # Helper function to format values in Indian currency units
    def format_currency(value):
        """Format value in Indian currency units."""
        if value >= 1_00_00_00_000:  # 100 crores
            return f"₹ {value / 1_00_00_00_000:.2f} Crores"
        elif value >= 1_00_00_000:  # 1 crore
            return f"₹ {value / 1_00_00_000:.2f} Crores"
        elif value >= 1_00_000:  # 1 lakh
            return f"₹ {value / 1_00_000:.2f} Lakhs"
        elif value >= 1_000:  # 1 thousand
            return f"₹ {value / 1_000:.2f} Thousand"
        else:
            return f"₹ {value:.2f}"

    # Input function with boundaries and validation
    def get_input_with_validation(prompt, value_type=float, lower_bound=None, upper_bound=None):
        while True:
            try:
                value = value_type(input(prompt))
                if lower_bound is not None and value < lower_bound:
                    print(f"Value must be greater than or equal to {lower_bound}.")
                    continue
                if upper_bound is not None and value > upper_bound:
                    print(f"Value must be less than or equal to {upper_bound}.")
                    continue
                return value
            except ValueError:
                print("Invalid input, please try again.")

    # Get user input with validation
    investment = get_input_with_validation("Enter Monthly Investment Amount: ₹", float, 0.01)
    growth_rate = get_input_with_validation("Enter Growth in Investment Amount (in %): ", float, 0, 100)
    rate_of_return = get_input_with_validation("Enter Expected Rate of Return (in %): ", float, 1, 50)
    tenure = get_input_with_validation("Enter Tenure (in years): ", int, 1, 50)

    # Validating boundaries
    if tenure < 1 or tenure > 50:
        return "Tenure must be between 1 and 50 years."
    if rate_of_return < 1 or rate_of_return > 50:
        return "Rate of return must be between 1% and 50%."
    if growth_rate < 0:
        return "Growth rate must be non-negative."

    # Converting percentage to decimal
    annual_rate = rate_of_return / 100
    monthly_rate = annual_rate / 12
    total_months = tenure * 12
    
    future_value = 0
    total_deposit = 0

    for year in range(1, tenure + 1):
        # Calculate the investment amount for the current year (growth starts from the second year)
        current_investment = investment * ((1 + growth_rate / 100) ** (year - 1))
        for month in range(12):
            # For each month, calculate future value and total deposit
            months_remaining = total_months - ((year - 1) * 12 + month)
            future_value += current_investment * ((1 + monthly_rate) ** months_remaining)
            total_deposit += current_investment

    # Total Earnings
    total_earnings = future_value - total_deposit
    
    # Formatting output using the currency formatter
    future_value_formatted = format_currency(future_value)
    total_earnings_formatted = format_currency(total_earnings)
    total_deposit_formatted = format_currency(total_deposit)
    
    print("\n--- Step-Up SIP Investment Details ---")
    print(f"Total Amount Invested: {total_deposit_formatted}\n"
          f"Total Earnings: {total_earnings_formatted}\n"
          f"Total Corpus Value: {future_value_formatted}")
step_up_calculator()
