from flask import Flask, render_template, request
import requests,math

app = Flask(__name__)

# Additional calculators (CAGR, Lumpsum) can follow similar patterns
@app.route('/currency_converter', methods=['GET', 'POST'])
def currency_converter():
    if request.method == 'POST':
        api_key = "490f8e1a6cb26290a1ca1189"  # Your API key
        base_currency = request.form['base_currency'].upper()
        target_currency = request.form['target_currency'].upper()
        amount = float(request.form['amount'])

        # Fetch conversion rates from the API
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and 'conversion_rates' in data:
            conversion_rate = data['conversion_rates'].get(target_currency)
            if conversion_rate:
                converted_amount = amount * conversion_rate
                return render_template('currency_converter_result.html', converted_amount=converted_amount, target_currency=target_currency)
            else:
                return render_template('currency_converter_index.html', error=f"Conversion rate for {target_currency} not found.")
        else:
            return render_template('currency_converter_index.html', error="Error fetching conversion rate. Please check the base currency and try again.")
    
    return render_template('currency_converter_index.html')

@app.route('/', methods=['GET', 'POST'])
def simple_interest():
    if request.method == 'POST':
        principal = float(request.form.get('principal'))
        rate = float(request.form.get('rate'))
        time = float(request.form.get('time'))
        si = (principal * rate * time) / 100
        total_amount = principal + si
        
        return render_template('simple_interest_result.html', principal=principal, si=si, total_amount=total_amount)
    return render_template('simple_interest_index.html')

@app.route('/', methods=['GET', 'POST'])
def compound_interest():
    if request.method == 'POST':
        principal = float(request.form.get('principal'))
        rate = float(request.form.get('rate'))
        time = float(request.form.get('time'))
        frequency_choice = request.form.get('frequency')
        
        # Determine compounding frequency
        if frequency_choice == 'daily':
            n = 365  # Daily compounding
        elif frequency_choice == 'monthly':
            n = 12  # Monthly compounding
        elif frequency_choice == 'quarterly':
            n = 4   # Quarterly compounding
        elif frequency_choice == 'semi-annually':
            n = 2   # Semi-annual compounding
        elif frequency_choice == 'annually':
            n = 1   # Annual compounding
        else:
            n = 1  # Default to annual compounding
        
        ci = principal * (1 + rate/(100*n))**(n*time) - principal
        total_amount = principal + ci
        
        return render_template('compound_interest_result.html', principal=principal, ci=ci, total_amount=total_amount)

    return render_template('compound_interest_index.html')

@app.route('/', methods=['GET', 'POST'])
def fixed_deposit():
    if request.method == 'POST':
        principal = float(request.form.get('principal'))
        rate = float(request.form.get('rate'))
        time_choice = request.form.get('time_choice')
        time = 0

        if time_choice == 'days':
            time_in_days = float(request.form.get('time_in_days'))
            time = time_in_days / 365  # Convert days to years
        elif time_choice == 'months':
            time_in_months = float(request.form.get('time_in_months'))
            time = time_in_months / 12  # Convert months to years
        elif time_choice == 'years':
            time = float(request.form.get('time_in_years'))
        else:
            return "Invalid choice."

        # Formula for compound interest with quarterly compounding: A = P * (1 + r/n)^(nt)
        n = 4  # Quarterly compounding
        maturity_amount = principal * (1 + rate / (100 * n)) ** (n * time)

        # Estimated returns is the difference between maturity amount and invested amount
        estimated_returns = maturity_amount - principal

        return render_template('fixed_deposit_result.html', principal=principal, estimated_returns=estimated_returns, maturity_amount=maturity_amount)

    return render_template('fixed_deposit_index.html')

@app.route('/', methods=['GET', 'POST'])
def recurring_deposit():
    if request.method == 'POST':
        monthly_deposit = float(request.form.get('monthly_deposit'))
        rate = float(request.form.get('rate'))
        frequency_choice = request.form.get('frequency_choice')
        
        if frequency_choice == 'monthly':
            while True:
                time_period = float(request.form.get('time_period_months'))
                if 1 <= time_period <= 12:
                    break
                else:
                    return "Invalid input. Months must be between 1 and 12."
            tenure_years = time_period / 12  # Convert months to years
            total_installments = time_period
        elif frequency_choice == 'yearly':
            tenure_years = float(request.form.get('tenure_years'))
            total_installments = tenure_years * 12  # Convert years to months
        else:
            return "Invalid choice."

        # Invested amount is the total deposit made
        invested_amount = monthly_deposit * total_installments

        # Formula for maturity amount in recurring deposit
        maturity_amount = monthly_deposit * (((1 + (rate / 400))**(4 * tenure_years) - 1) / (1 - (1 + (rate / 400))**(-1/3)))

        # Estimated return is the maturity amount minus invested amount
        estimated_return = maturity_amount - invested_amount

        return render_template('recurring_deposit_result.html', invested_amount=invested_amount, estimated_return=estimated_return, maturity_amount=maturity_amount)

    return render_template('recurring_deposit_index.html')

@app.route('/savings_goal', methods=['GET', 'POST'])
def savings_goal_calculator():
    if request.method == 'POST':
        goal_amount = float(request.form.get('goal_amount'))
        monthly_contribution = float(request.form.get('monthly_contribution'))
        annual_interest_rate = float(request.form.get('annual_interest_rate'))

        # Convert annual interest rate to a monthly rate
        monthly_interest_rate = annual_interest_rate / 100 / 12

        # Formula to calculate the number of months to reach the goal
        if monthly_interest_rate == 0:
            months = goal_amount / monthly_contribution
        else:
            numerator = math.log((goal_amount * monthly_interest_rate + monthly_contribution) / monthly_contribution)
            denominator = math.log(1 + monthly_interest_rate)
            months = numerator / denominator

        # Calculate total invested amount and estimated return
        total_invested = monthly_contribution * months
        estimated_return = goal_amount - total_invested

        # Calculate years and remaining months
        years = int(months // 12)
        remaining_months = int(round(months % 12))

        return render_template('savings_goal_result.html', total_invested=total_invested, estimated_return=estimated_return, goal_amount=goal_amount, years=years, remaining_months=remaining_months)

    return render_template('savings_goal_index.html')


@app.route('/loan_analysis', methods=['GET', 'POST'])
def loan_analysis_calculator():
    # Function to calculate monthly payment
    def calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years, loan_term_months):
        total_months = loan_term_years * 12 + loan_term_months
        monthly_interest_rate = (annual_interest_rate / 100) / 12

        # Monthly payment calculation
        monthly_payment = loan_amount * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -total_months)

        # Total payment and interest
        total_payment = monthly_payment * total_months
        total_interest = total_payment - loan_amount
        annual_payment = monthly_payment * 12

        return monthly_payment, total_payment, total_interest, annual_payment

    # Function to calculate loan amount
    def calculate_loan_amount(monthly_payment, annual_interest_rate, loan_term_years, loan_term_months):
        total_months = loan_term_years * 12 + loan_term_months
        monthly_interest_rate = (annual_interest_rate / 100) / 12

        # Loan amount calculation
        loan_amount = monthly_payment * (1 - (1 + monthly_interest_rate) ** -total_months) / monthly_interest_rate

        # Total payment and interest
        total_payment = monthly_payment * total_months
        total_interest = total_payment - loan_amount
        annual_payment = monthly_payment * 12

        return loan_amount, total_payment, total_interest, annual_payment

    # Function to calculate loan term
    def calculate_loan_term(loan_amount, annual_interest_rate, monthly_payment):
        monthly_interest_rate = (annual_interest_rate / 100) / 12

        # Loan term calculation
        total_months = - (math.log(1 - (loan_amount * monthly_interest_rate) / monthly_payment) / math.log(1 + monthly_interest_rate))
        loan_term_years = int(total_months // 12)
        loan_term_months = int(total_months % 12)

        # Total payment and interest
        total_payment = monthly_payment * total_months
        total_interest = total_payment - loan_amount
        annual_payment = monthly_payment * 12

        return loan_term_years, loan_term_months, total_payment, total_interest, annual_payment

    # Function to calculate annual interest rate
    def calculate_annual_interest_rate(loan_amount, loan_term_years, loan_term_months, monthly_payment):
        total_months = loan_term_years * 12 + loan_term_months
        tolerance = 1e-6
        max_iterations = 1000
        low = 0.0
        high = 1.0  # Interest rate upper bound (100%)

        for _ in range(max_iterations):
            mid = (low + high) / 2
            monthly_interest_rate = mid / 12
            guessed_payment = loan_amount * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -total_months)

            if abs(guessed_payment - monthly_payment) < tolerance:
                annual_interest_rate = mid * 100
                return annual_interest_rate

            if guessed_payment < monthly_payment:
                low = mid
            else:
                high = mid

        raise ValueError("Could not converge to a solution")

    if request.method == 'POST':
        choice = request.form.get('choice')

        if choice == '1':
            loan_amount = float(request.form.get('loan_amount'))
            annual_interest_rate = float(request.form.get('annual_interest_rate'))
            loan_term_years = int(request.form.get('loan_term_years'))
            loan_term_months = int(request.form.get('loan_term_months'))
            monthly_payment, total_payment, total_interest, annual_payment = calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years, loan_term_months)
            return render_template('loan_analysis_result.html', result=monthly_payment, category="Monthly Payment", total_payment=total_payment, total_interest=total_interest, annual_payment=annual_payment)

        elif choice == '2':
            monthly_payment = float(request.form.get('monthly_payment'))
            annual_interest_rate = float(request.form.get('annual_interest_rate'))
            loan_term_years = int(request.form.get('loan_term_years'))
            loan_term_months = int(request.form.get('loan_term_months'))
            loan_amount, total_payment, total_interest, annual_payment = calculate_loan_amount(monthly_payment, annual_interest_rate, loan_term_years, loan_term_months)
            return render_template('loan_analysis_result.html', result=loan_amount, category="Loan Amount", total_payment=total_payment, total_interest=total_interest, annual_payment=annual_payment)

        elif choice == '3':
            loan_amount = float(request.form.get('loan_amount'))
            annual_interest_rate = float(request.form.get('annual_interest_rate'))
            monthly_payment = float(request.form.get('monthly_payment'))
            loan_term_years, loan_term_months, total_payment, total_interest, annual_payment = calculate_loan_term(loan_amount, annual_interest_rate, monthly_payment)
            return render_template('loan_analysis_result.html', result=f"{loan_term_years} years and {loan_term_months} months", category="Loan Term", total_payment=total_payment, total_interest=total_interest, annual_payment=annual_payment)

        elif choice == '4':
            loan_amount = float(request.form.get('loan_amount'))
            loan_term_years = int(request.form.get('loan_term_years'))
            loan_term_months = int(request.form.get('loan_term_months'))
            monthly_payment = float(request.form.get('monthly_payment'))
            annual_interest_rate = calculate_annual_interest_rate(loan_amount, loan_term_years, loan_term_months, monthly_payment)
            total_payment = monthly_payment * (loan_term_years * 12 + loan_term_months)
            total_interest = total_payment - loan_amount
            annual_payment = monthly_payment * 12
            return render_template('loan_analysis_result.html', result=annual_interest_rate, category="Annual Interest Rate", total_payment=total_payment, total_interest=total_interest, annual_payment=annual_payment)

    return render_template('loan_analysis_index.html')

@app.route('/', methods=['GET', 'POST'])
def retirement_savings_calculator():
    result_message = None

    # Inner function to calculate monthly savings needed
    def calculate_monthly_savings(currently_saved, amount_at_retirement, years_until_retirement, annual_return_rate):
        r = (annual_return_rate / 100) / 12  # Monthly interest rate
        n = years_until_retirement * 12  # Total number of months
        
        monthly_savings = (amount_at_retirement - currently_saved * (1 + r) ** n) / (((1 + r) ** n - 1) / r)
        
        return monthly_savings

    # Inner function to calculate retirement amount
    def calculate_retirement_amount(currently_saved, monthly_savings, years_until_retirement, annual_return_rate):
        r = (annual_return_rate / 100) / 12  # Monthly interest rate
        n = years_until_retirement * 12  # Total number of months
        
        retirement_amount = currently_saved * (1 + r) ** n + monthly_savings * (((1 + r) ** n - 1) / r)
        
        return retirement_amount

    # Inner function to calculate years until retirement
    def calculate_years_until_retirement(currently_saved, amount_at_retirement, monthly_savings, annual_return_rate):
        r = (annual_return_rate / 100) / 12  # Monthly interest rate
        P = monthly_savings
        C = currently_saved
        
        total_months = math.log((amount_at_retirement * r + P) / (C * r + P)) / math.log(1 + r)
        years = int(total_months // 12)
        months = int(total_months % 12)
        
        return years, months

    # Inner function to calculate annual return rate
    def calculate_annual_return_rate(currently_saved, amount_at_retirement, years_until_retirement, monthly_savings):
        low = 0.0
        high = 1.0  # Interest rate upper bound (100%)
        tolerance = 1e-6
        max_iterations = 1000
        n = years_until_retirement * 12  # Total number of months
        
        for _ in range(max_iterations):
            mid = (low + high) / 2
            r = mid / 12  # Monthly interest rate
            guessed_retirement_amount = currently_saved * (1 + r) ** n + monthly_savings * (((1 + r) ** n - 1) / r)
            
            if abs(guessed_retirement_amount - amount_at_retirement) < tolerance:
                annual_return_rate = mid * 100
                return annual_return_rate
            
            if guessed_retirement_amount < amount_at_retirement:
                low = mid
            else:
                high = mid

        raise ValueError("Could not converge to a solution")

    if request.method == 'POST':
        option = request.form['option']
        currently_saved = float(request.form['currently_saved'])
        amount_at_retirement = float(request.form['amount_at_retirement'])
        years_until_retirement = int(request.form['years_until_retirement'])
        annual_return_rate = float(request.form['annual_return_rate'])
        
        if option == '1':
            result = calculate_monthly_savings(currently_saved, amount_at_retirement, years_until_retirement, annual_return_rate)
            result_message = f"Monthly Savings Needed: ₹{result:.2f}"
        elif option == '2':
            monthly_savings = float(request.form['monthly_savings'])
            result = calculate_retirement_amount(currently_saved, monthly_savings, years_until_retirement, annual_return_rate)
            result_message = f"Amount at Retirement: ₹{result:.2f}"
        elif option == '3':
            monthly_savings = float(request.form['monthly_savings'])
            years, months = calculate_years_until_retirement(currently_saved, amount_at_retirement, monthly_savings, annual_return_rate)
            result_message = f"Years until Retirement: {years} years and {months} months"
        elif option == '4':
            monthly_savings = float(request.form['monthly_savings'])
            result = calculate_annual_return_rate(currently_saved, amount_at_retirement, years_until_retirement, monthly_savings)
            result_message = f"Annual Return Rate: {result:.2f}%"

        return render_template('retirement_savings_result.html', result_message=result_message)

    return render_template('retirement_savings_index.html')


@app.route('/stock-return-calculator', methods=['GET', 'POST'])
def stock_return_calculator():
    result_message = None
    tax_details = None

    if request.method == 'POST':
        # Get form data
        buy_price = float(request.form['buy_price'])
        buy_qty = int(request.form['buy_qty'])
        sell_price = float(request.form['sell_price'])
        sell_qty = int(request.form['sell_qty'])

        # Calculating basic amounts
        invested_amount = buy_price * buy_qty
        total_sell_amount = sell_price * sell_qty
        gross_return = total_sell_amount - invested_amount
        
        # Display profit or loss explicitly
        result_type = "Profit" if gross_return > 0 else "Loss"
        gross_return_percentage = (gross_return / invested_amount) * 100

        # Tax calculations
        stt_ctt_buy = 0.001 * invested_amount  # 0.1% STT for buy
        stt_ctt_sell = 0.001 * total_sell_amount  # 0.1% STT for sell
        transaction_charges_buy = 0.0000322 * invested_amount  # 0.00322% for buy
        transaction_charges_sell = 0.0000322 * total_sell_amount  # 0.00322% for sell
        stamp_duty = 0.00015 * invested_amount  # 0.015% stamp duty for buy
        dp_charges = 15  # Flat DP charges

        # Total taxes for buy and sell
        brokerage = 0  # Given as 0
        gst_buy = 0.18 * (brokerage + transaction_charges_buy)
        gst_sell = 0.18 * (brokerage + transaction_charges_sell)

        total_tax_buy = stt_ctt_buy + transaction_charges_buy + stamp_duty + gst_buy
        total_tax_sell = stt_ctt_sell + transaction_charges_sell + gst_sell
        total_tax = total_tax_buy + total_tax_sell

        # Net return after taxes
        net_return = gross_return - total_tax
        net_return_percentage = (net_return / invested_amount) * 100

        # Prepare results to display
        result_message = f"Invested Amount: ₹{invested_amount:.2f}, Total Sell Amount: ₹{total_sell_amount:.2f}, " \
                         f"{result_type}: ₹{abs(gross_return):.2f}, Gross {result_type} Percentage: {gross_return_percentage:.2f}%, " \
                         f"Net {result_type}: ₹{abs(net_return):.2f}, Net {result_type} Percentage: {net_return_percentage:.2f}%"

        tax_details = {
            "STT/CTT on Buy": f"₹{stt_ctt_buy:.2f}",
            "STT/CTT on Sell": f"₹{stt_ctt_sell:.2f}",
            "Transaction Charges on Buy": f"₹{transaction_charges_buy:.2f}",
            "Transaction Charges on Sell": f"₹{transaction_charges_sell:.2f}",
            "Stamp Duty": f"₹{stamp_duty:.2f}",
            "DP Charges": f"₹{dp_charges:.2f}",
            "GST on Buy": f"₹{gst_buy:.2f}",
            "GST on Sell": f"₹{gst_sell:.2f}",
            "Total Tax": f"₹{total_tax:.2f}",
        }

    return render_template('stock_return_calculator.html', result_message=result_message, tax_details=tax_details)

@app.route('/', methods=['GET', 'POST'])
def tip_calculator():
    result_message = None

    if request.method == 'POST':
        # Get form data
        bill_amount = float(request.form['bill_amount'])
        tip_percentage = float(request.form['tip_percentage'])
        split = int(request.form['split'])

        # Calculations
        total_tip = (tip_percentage / 100) * bill_amount
        total_check = bill_amount + total_tip
        each_total_amount = total_check / split
        each_pay = total_tip / split

        # Prepare results to display
        result_message = {
            "total_tip": f"Total Tip Amount: ₹{total_tip:.2f}",
            "total_check": f"Total Check (Bill + Tip): ₹{total_check:.2f}",
            "each_total_amount": f"Each Pay Amount (Bill + Tip per person): ₹{each_total_amount:.2f}",
            "each_pay": f"Each Pay (Tip per person): ₹{each_pay:.2f}"
        }

    return render_template('tip_index.html', result_message=result_message)


@app.route('/lumpsum-calculator', methods=['GET', 'POST'])
def lumpsum_calculator():
    result_message = None

    if request.method == 'POST':
        # User inputs
        investment_amount = float(request.form['investment_amount'])
        expected_rate = float(request.form['expected_rate'])
        tenure_years = int(request.form['tenure_years'])

        # Calculate maturity amount using compound interest formula
        annual_interest_rate = expected_rate / 100
        maturity_amount = investment_amount * (1 + annual_interest_rate) ** tenure_years
        total_earnings = maturity_amount - investment_amount

        # Format the amounts for better readability
        def format_amount(amount):
            """Format the amount into lakhs or crores for better readability."""
            if amount >= 1e7:
                return f"₹{amount:.2f} ({amount / 1e7:.2f} Crores)"
            elif amount >= 1e5:
                return f"₹{amount:.2f} ({amount / 1e5:.2f} Lakhs)"
            else:
                return f"₹{amount:.2f}"

        # Prepare results to display
        result_message = {
            "total_investment": f"Total Investment Amount: {format_amount(investment_amount)}",
            "total_earnings": f"Total Earnings: {format_amount(total_earnings)}",
            "maturity_amount": f"Maturity Amount: {format_amount(maturity_amount)}"
        }

    return render_template('lumpsum_index.html', result_message=result_message)

@app.route('/', methods=['GET', 'POST'])
def sip_calculator():
    result_message = None

    if request.method == 'POST':
        # User inputs
        frequency_choice = int(request.form['frequency_choice'])
        monthly_investment = float(request.form['monthly_investment'])
        expected_rate = float(request.form['expected_rate'])
        tenure_years = int(request.form['tenure_years'])

        # Determine deposits per year based on frequency choice
        deposits_per_year = 12 if frequency_choice == 1 else 1

        # Annual rate divided by the number of deposits per year
        period_rate = (expected_rate / 100) / deposits_per_year
        total_periods = tenure_years * deposits_per_year

        # Future value calculation using the SIP formula
        future_value = monthly_investment * (((1 + period_rate) ** total_periods - 1) / period_rate) * (1 + period_rate)

        # Total amount deposited
        total_amount_deposited = monthly_investment * total_periods

        # Total earnings (future value - total amount deposited)
        total_earnings = future_value - total_amount_deposited

        # Format the amounts for better readability
        def format_amount(amount):
            """Format the amount into lakhs or crores for better readability."""
            if amount >= 1e7:
                return f"₹ {amount:.2f} ({amount / 1e7:.2f} Crores)"
            elif amount >= 1e5:
                return f"₹ {amount:.2f} ({amount / 1e5:.2f} Lakhs)"
            elif amount >= 1e3:
                return f"₹ {amount:.2f} ({amount / 1e3:.2f} Thousands)"
            else:
                return f"₹ {amount:.2f}"

        # Prepare results to display
        result_message = {
            "future_value": f"Your Future Value: {format_amount(future_value)}",
            "total_earnings": f"Total Earnings: {format_amount(total_earnings)}",
            "total_deposited": f"Total Amount Deposited: {format_amount(total_amount_deposited)}"
        }

    return render_template('sip_calculator.html', result_message=result_message)


@app.route('/step-up-calculator', methods=['GET', 'POST'])
def step_up_calculator():
    result_message = None

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

    if request.method == 'POST':
        # User inputs
        investment = float(request.form['investment'])
        growth_rate = float(request.form['growth_rate'])
        rate_of_return = float(request.form['rate_of_return'])
        tenure = int(request.form['tenure'])

        # Validating boundaries
        if tenure < 1 or tenure > 50:
            result_message = "Tenure must be between 1 and 50 years."
        elif rate_of_return < 1 or rate_of_return > 50:
            result_message = "Rate of return must be between 1% and 50%."
        elif growth_rate < 0:
            result_message = "Growth rate must be non-negative."
        else:
            # Converting percentage to decimal
            annual_rate = rate_of_return / 100
            monthly_rate = annual_rate / 12
            total_months = tenure * 12
            
            future_value = 0
            total_deposit = 0

            for year in range(1, tenure + 1):
                # Calculate the investment amount for the current year
                current_investment = investment * ((1 + growth_rate / 100) ** (year - 1))
                for month in range(12):
                    # Calculate future value and total deposit
                    months_remaining = total_months - ((year - 1) * 12 + month)
                    future_value += current_investment * ((1 + monthly_rate) ** months_remaining)
                    total_deposit += current_investment

            # Total Earnings
            total_earnings = future_value - total_deposit
            
            # Formatting output using the currency formatter
            result_message = {
                "total_invested": format_currency(total_deposit),
                "total_earnings": format_currency(total_earnings),
                "total_corpus_value": format_currency(future_value)
            }

    return render_template('step_up_calculator.html', result_message=result_message)

@app.route('/cagr-calculator', methods=['GET', 'POST'])
def cagr_calculator():
    result_message = None

    def calculate_cagr(beginning_value, ending_value, tenure):
        """Calculate the Compound Annual Growth Rate (CAGR)."""
        return ((ending_value / beginning_value) ** (1 / tenure) - 1) * 100

    if request.method == 'POST':
        # User inputs
        beginning_value = float(request.form['beginning_value'])
        ending_value = float(request.form['ending_value'])
        tenure = int(request.form['tenure'])

        # Validate tenure
        if tenure < 1 or tenure > 50:
            result_message = "Tenure must be between 1 and 50 years."
        else:
            # Calculate CAGR
            cagr_return = calculate_cagr(beginning_value, ending_value, tenure)
            result_message = f"CAGR Return: {cagr_return:.2f}%"

    return render_template('cagr_calculator.html', result_message=result_message)


@app.route('/ppf_calculator', methods=['POST'])
def ppf_calculator():
    def format_amount(amount):
        """Format the amount into lakhs or crores for better readability."""
        if amount >= 1e7:
            return f"₹{amount:.2f} ({amount / 1e7:.2f} Crores)"
        elif amount >= 1e5:
            return f"₹{amount:.2f} ({amount / 1e5:.2f} Lakhs)"
        else:
            return f"₹{amount:.2f}"

    # Get inputs from the form
    frequency_choice = int(request.form['frequency'])
    investment_amount = float(request.form['investment_amount'])
    tenure_years = int(request.form['tenure_years'])

    # Determine frequency multiplier
    deposits_per_year = {1: 12, 2: 4, 3: 2, 4: 1}.get(frequency_choice, 0)

    total_deposited = investment_amount * deposits_per_year * tenure_years
    maturity_amount = 0
    annual_interest_rate = 7.1 / 100  # Annual interest rate

    for year in range(tenure_years):
        annual_deposit = investment_amount * deposits_per_year
        maturity_amount += annual_deposit
        
        # Calculate interest for the current balance
        interest_for_year = maturity_amount * annual_interest_rate
        maturity_amount += interest_for_year

    # Total interest earned
    interest_earned = maturity_amount - total_deposited

    results = {
        'total_deposited': format_amount(total_deposited),
        'interest_earned': format_amount(interest_earned),
        'maturity_amount': format_amount(maturity_amount)
    }
    
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)

