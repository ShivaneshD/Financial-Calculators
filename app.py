from flask import *
import requests , json , logging
import math
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/calculators')
def calculators():
    return render_template('calculators.html')

@app.route('/currency_converter', methods=['GET', 'POST'])
def currency_converter():
    api_key = "490f8e1a6cb26290a1ca1189"  # Your API key

    # Fetch available currencies from the API
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/codes"
    response = requests.get(url)
    data = response.json()

    # Create a dictionary of currency codes and names
    if response.status_code == 200 and 'supported_codes' in data:
        currencies = {code[0]: f"{code[1]} ({code[0]})" for code in data['supported_codes']}
    else:
        currencies = {
            'USD': 'United States Dollar (USD)',
            'EUR': 'Euro (EUR)',
            'GBP': 'British Pound (GBP)',
            'INR': 'Indian Rupee (INR)',
            'JPY': 'Japanese Yen (JPY)',
            'CAD': 'Canadian Dollar (CAD)',
            'AUD': 'Australian Dollar (AUD)',
            'CNY': 'Chinese Yuan (CNY)',
            'SGD': 'Singapore Dollar (SGD)',
            'ZAR': 'South African Rand (ZAR)'
        }  # Fallback if the API fails

    if request.method == 'POST':
        base_currency = request.form['base_currency']
        target_currency = request.form['target_currency']
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
                return render_template('currency_converter_index.html', currencies=currencies, error=f"Conversion rate for {target_currency} not found.")
        else:
            return render_template('currency_converter_index.html', currencies=currencies, error="Error fetching conversion rate. Please check the base currency and try again.")
    
    return render_template('currency_converter_index.html', currencies=currencies)

@app.route('/simple_interest', methods=['GET', 'POST'])
def simple_interest():
    # Default values
    si = None
    principal = 0
    rate = 0
    time = 0
    inflation_rate = 0
    nominal_si = 0
    nominal_total = 0
    real_si = 0
    real_total = 0

    if request.method == 'POST':
        # Get user inputs
        principal = float(request.form['principal'])
        rate = float(request.form['rate'])
        time = float(request.form['time'])
        inflation_rate = float(request.form['inflation_rate'])

        # Calculate Simple Interest (Nominal)
        nominal_si = (principal * rate * time) / 100
        nominal_total = principal + nominal_si

        # Adjusting for inflation (Real Interest and Total)
        inflation_factor = 1 + inflation_rate / 100
        real_si = nominal_si / inflation_factor
        real_total = principal + real_si

        # Define result to be passed to the template
        si = {
            'nominal_si': nominal_si,
            'nominal_total': nominal_total,
            'real_si': real_si,
            'real_total': real_total,
            'principal': principal
        }

    return render_template('simple_interest.html', si=si, principal=principal, nominal_si=nominal_si,
                           nominal_total=nominal_total, real_si=real_si, real_total=real_total, inflation_rate=inflation_rate)

@app.route('/compound_interest', methods=['GET', 'POST'])
def compound_interest():
    if request.method == 'POST':
        principal = float(request.form.get('principal'))
        rate = float(request.form.get('rate'))
        time = float(request.form.get('time'))
        inflation_rate = float(request.form.get('inflation_rate'))
        frequency_choice = request.form.get('frequency')

        # Determine compounding frequency
        if frequency_choice == 'daily':
            n = 365
        elif frequency_choice == 'monthly':
            n = 12
        elif frequency_choice == 'quarterly':
            n = 4
        elif frequency_choice == 'semi-annually':
            n = 2
        elif frequency_choice == 'annually':
            n = 1
        else:
            n = 1  # Default to annual compounding

        # Calculate compound interest without inflation
        ci = principal * (1 + rate / (100 * n)) ** (n * time) - principal
        total_amount = principal + ci

        # Adjust for inflation
        adjusted_rate = rate - inflation_rate
        adjusted_ci = principal * (1 + adjusted_rate / (100 * n)) ** (n * time) - principal
        adjusted_total_amount = principal + adjusted_ci

        # Prepare data for JSON response or rendering
        chart_data = {
            'principal': principal,
            'interest': adjusted_ci,
            'total': adjusted_total_amount
        }

        return jsonify({
            'principal': principal,
            'ci': adjusted_ci,
            'total_amount': adjusted_total_amount,
            'chart_data': chart_data
        })

    return render_template('compound_interest_calculator.html')

@app.route('/fixed_deposit', methods=['GET', 'POST'])
def fixed_deposit():
    if request.method == 'POST':
        try:
            # Get form inputs
            principal = float(request.form.get('principal'))
            rate = float(request.form.get('rate'))
            time_choice = request.form.get('time_choice')
            time = 0

            # Determine time period based on the user's selection
            if time_choice == 'days':
                time_in_days = float(request.form.get('time_in_days'))
                time = time_in_days / 365
            elif time_choice == 'months':
                time_in_months = float(request.form.get('time_in_months'))
                time = time_in_months / 12
            elif time_choice == 'years':
                time = float(request.form.get('time_in_years'))

            # Quarterly compounding
            n = 4
            maturity_amount = principal * (1 + rate / (100 * n)) ** (n * time)
            estimated_returns = maturity_amount - principal

            # Data for the pie chart
            chart_data = {
                'invested': principal,
                'maturity': maturity_amount
            }

            return render_template('fixed_deposit_index.html', principal=principal, estimated_returns=estimated_returns,
                                   maturity_amount=maturity_amount, chart_data=chart_data, show_result=True)
        except ValueError:
            return render_template('fixed_deposit_index.html', error="Invalid input. Please enter numeric values.", show_result=False)

    return render_template('fixed_deposit_index.html', show_result=False)

@app.route('/recurring_deposit', methods=['GET', 'POST'])
def recurring_deposit():
    if request.method == 'POST':
        try:
            # Fetch the form data
            monthly_deposit = float(request.form.get('monthly_deposit'))
            rate = float(request.form.get('rate'))
            tenure_value = float(request.form.get('tenure_value'))
            tenure_type = request.form.get('tenure_type')
            inflation_rate = float(request.form.get('inflation_rate'))

            # Determine tenure in years based on tenure type (months or years)
            if tenure_type == 'years':
                tenure_years = tenure_value
                total_installments = tenure_years * 12  # Convert years to months
            elif tenure_type == 'months':
                tenure_years = tenure_value / 12  # Convert months to years
                total_installments = tenure_value
            else:
                flash('Invalid tenure type selected.', 'danger')
                return redirect(url_for('recurring_deposit'))

            # Calculate invested amount
            invested_amount = monthly_deposit * total_installments

            # Calculate maturity amount (adjusted for nominal interest rate minus inflation)
            real_rate = ((1 + rate / 100) / (1 + inflation_rate / 100) - 1) * 100
            maturity_amount = monthly_deposit * (((1 + (real_rate / 400)) ** (4 * tenure_years) - 1) /
                                                 (1 - (1 + (real_rate / 400)) ** (-1 / 3)))

            # Calculate the estimated return (maturity amount - invested amount)
            estimated_return = maturity_amount - invested_amount

            # Round the results for presentation
            invested_amount = round(invested_amount, 2)
            estimated_return = round(estimated_return, 2)
            maturity_amount = round(maturity_amount, 2)

            return render_template('recurring_deposit.html',
                                   invested_amount=invested_amount,
                                   estimated_return=estimated_return,
                                   maturity_amount=maturity_amount,
                                   inflation_rate=inflation_rate)

        except (ValueError, TypeError):
            flash('Please enter valid numerical values.', 'danger')
            return redirect(url_for('recurring_deposit'))

    return render_template('recurring_deposit.html')

@app.route('/savings_goal', methods=['GET', 'POST'])
def savings_goal_calculator():
    if request.method == 'POST':
        goal_amount = float(request.form.get('goal_amount'))
        monthly_contribution = float(request.form.get('monthly_contribution'))
        annual_interest_rate = float(request.form.get('annual_interest_rate'))
        inflation_rate = float(request.form.get('inflation_rate'))

        # Convert annual rates to monthly rates
        monthly_interest_rate = annual_interest_rate / 100 / 12
        monthly_inflation_rate = inflation_rate / 100 / 12

        # Adjusted goal accounting for inflation over time
        inflation_adjusted_goal = goal_amount * ((1 + monthly_inflation_rate) ** (12 * 10))

        # Calculate number of months required
        if monthly_interest_rate == 0:
            months = inflation_adjusted_goal / monthly_contribution
        else:
            numerator = math.log((inflation_adjusted_goal * monthly_interest_rate + monthly_contribution) / monthly_contribution)
            denominator = math.log(1 + monthly_interest_rate)
            months = numerator / denominator

        # Calculate total invested and estimated return
        total_invested = monthly_contribution * months
        estimated_return = inflation_adjusted_goal - total_invested

        # Calculate years and months
        years = int(months // 12)
        remaining_months = int(round(months % 12))

        # Prepare data for interest table
        interest_table = []
        total_balance = 0
        for month in range(1, int(months) + 1):
            total_invested_this_month = monthly_contribution
            total_balance += total_invested_this_month
            interest_earned = total_balance * monthly_interest_rate
            total_balance += interest_earned
            interest_table.append({
                'month': month,
                'invested_amount': total_balance - interest_earned,
                'interest_earned': interest_earned,
                'total_balance': total_balance
            })

        return render_template('savings_goal.html', calculated=True,
                               goal_amount=goal_amount, principal=total_invested,
                               estimated_return=estimated_return, years=years,
                               remaining_months=remaining_months, interest_table=interest_table)

    return render_template('savings_goal.html', calculated=False)

@app.route('/loan_analysis', methods=['GET', 'POST'])
def loan_analysis_calculator():
    import math

    # Function to calculate monthly payment
    def calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years, loan_term_months):
        total_months = loan_term_years * 12 + loan_term_months
        monthly_interest_rate = (annual_interest_rate / 100) / 12

        if monthly_interest_rate == 0:
            monthly_payment = loan_amount / total_months
        else:
            monthly_payment = loan_amount * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -total_months)

        total_payment = monthly_payment * total_months
        total_interest = total_payment - loan_amount
        annual_payment = monthly_payment * 12

        # Generate payment schedule
        payment_schedule = []
        balance = loan_amount
        for month in range(1, total_months + 1):
            interest = balance * monthly_interest_rate
            principal = monthly_payment - interest
            balance -= principal
            payment_schedule.append({
                'month': month,
                'principal': round(principal, 2),
                'interest': round(interest, 2),
                'balance': round(max(balance, 0), 2)
            })

        # Correct the final balance to ensure it ends at zero
        payment_schedule[-1]['balance'] = 0
        return monthly_payment, total_payment, total_interest, annual_payment, payment_schedule

    # Function to calculate loan amount
    def calculate_loan_amount(monthly_payment, annual_interest_rate, loan_term_years, loan_term_months):
        total_months = loan_term_years * 12 + loan_term_months
        monthly_interest_rate = (annual_interest_rate / 100) / 12

        if monthly_interest_rate == 0:
            loan_amount = monthly_payment * total_months
        else:
            loan_amount = monthly_payment * (1 - (1 + monthly_interest_rate) ** -total_months) / monthly_interest_rate

        total_payment = monthly_payment * total_months
        total_interest = total_payment - loan_amount
        annual_payment = monthly_payment * 12

        # Generate payment schedule
        payment_schedule = []
        balance = loan_amount
        for month in range(1, total_months + 1):
            interest = balance * monthly_interest_rate
            principal = monthly_payment - interest
            balance -= principal
            payment_schedule.append({
                'month': month,
                'principal': round(principal, 2),
                'interest': round(interest, 2),
                'balance': round(max(balance, 0), 2)
            })

        payment_schedule[-1]['balance'] = 0
        return loan_amount, total_payment, total_interest, annual_payment, payment_schedule

    # Function to calculate loan term
    def calculate_loan_term(loan_amount, annual_interest_rate, monthly_payment):
        monthly_interest_rate = (annual_interest_rate / 100) / 12
        try:
            if monthly_interest_rate == 0:
                total_months = loan_amount / monthly_payment
            else:
                total_months = -math.log(1 - (loan_amount * monthly_interest_rate) / monthly_payment) / math.log(1 + monthly_interest_rate)

            total_months = math.ceil(total_months)
            loan_term_years = int(total_months // 12)
            loan_term_months = int(total_months % 12)
            
            # Recalculate the total payments with the found term
            monthly_payment, total_payment, total_interest, annual_payment, payment_schedule = calculate_monthly_payment(
                loan_amount, annual_interest_rate, loan_term_years, loan_term_months)

            return loan_term_years, loan_term_months, total_payment, total_interest, annual_payment, payment_schedule
        except (ValueError, ZeroDivisionError):
            raise ValueError("Monthly payment is too low to cover the loan amount and interest.")

    if request.method == 'POST':
        choice = request.form.get('choice')

        try:
            if choice == '1':
                # Calculate Monthly Payment
                loan_amount = float(request.form.get('loan_amount'))
                annual_interest_rate = float(request.form.get('annual_interest_rate'))
                loan_term_years = int(request.form.get('loan_term_years'))
                loan_term_months = int(request.form.get('loan_term_months'))

                monthly_payment, total_payment, total_interest, annual_payment, payment_schedule = calculate_monthly_payment(
                    loan_amount, annual_interest_rate, loan_term_years, loan_term_months)

                return jsonify({
                    'result': round(monthly_payment, 2),
                    'category': "Monthly Payment",
                    'total_payment': round(total_payment, 2),
                    'total_interest': round(total_interest, 2),
                    'annual_payment': round(annual_payment, 2),
                    'payment_schedule': payment_schedule
                })

            elif choice == '2':
                # Calculate Loan Amount
                monthly_payment = float(request.form.get('monthly_payment'))
                annual_interest_rate = float(request.form.get('annual_interest_rate'))
                loan_term_years = int(request.form.get('loan_term_years'))
                loan_term_months = int(request.form.get('loan_term_months'))

                loan_amount, total_payment, total_interest, annual_payment, payment_schedule = calculate_loan_amount(
                    monthly_payment, annual_interest_rate, loan_term_years, loan_term_months)

                return jsonify({
                    'result': round(loan_amount, 2),
                    'category': "Loan Amount",
                    'total_payment': round(total_payment, 2),
                    'total_interest': round(total_interest, 2),
                    'annual_payment': round(annual_payment, 2),
                    'payment_schedule': payment_schedule
                })

            elif choice == '3':
                # Calculate Loan Term
                loan_amount = float(request.form.get('loan_amount'))
                annual_interest_rate = float(request.form.get('annual_interest_rate'))
                monthly_payment = float(request.form.get('monthly_payment'))

                loan_term_years, loan_term_months, total_payment, total_interest, annual_payment, payment_schedule = calculate_loan_term(
                    loan_amount, annual_interest_rate, monthly_payment)

                return jsonify({
                    'result': f"{loan_term_years} years and {loan_term_months} months",
                    'category': "Loan Term",
                    'total_payment': round(total_payment, 2),
                    'total_interest': round(total_interest, 2),
                    'annual_payment': round(annual_payment, 2),
                    'payment_schedule': payment_schedule
                })

        except ValueError as e:
            return jsonify({'error': str(e)})

    return render_template('loan_analysis.html')


@app.route('/retirement_planner', methods=['GET', 'POST'])
def retirement_savings_calculator():
    result_message = None

    # Inner function to calculate monthly savings needed
    def calculate_monthly_savings(currently_saved, amount_at_retirement, years_until_retirement, annual_return_rate):
        r = (annual_return_rate / 100) / 12  # Monthly interest rate
        n = years_until_retirement * 12  # Total number of months

        if r == 0:
            if n == 0:
                raise ValueError("Years until retirement cannot be zero.")
            return (amount_at_retirement - currently_saved) / n

        try:
            monthly_savings = (amount_at_retirement - currently_saved * (1 + r) ** n) / (((1 + r) ** n - 1) / r)
        except ZeroDivisionError:
            raise ValueError("Invalid interest rate leading to division by zero.")
        return monthly_savings

    # Inner function to calculate retirement amount
    def calculate_retirement_amount(currently_saved, monthly_savings, years_until_retirement, annual_return_rate):
        r = (annual_return_rate / 100) / 12  # Monthly interest rate
        n = years_until_retirement * 12  # Total number of months

        if r == 0:
            return currently_saved + monthly_savings * n

        retirement_amount = currently_saved * (1 + r) ** n + monthly_savings * (((1 + r) ** n - 1) / r)
        return retirement_amount

    # Inner function to calculate years until retirement
    def calculate_years_until_retirement(currently_saved, amount_at_retirement, monthly_savings, annual_return_rate):
        r = (annual_return_rate / 100) / 12  # Monthly interest rate
        P = monthly_savings
        C = currently_saved

        if (C * r + P) <= 0 or (amount_at_retirement * r + P) <= 0:
            raise ValueError("Invalid input values leading to logarithm of non-positive number.")

        total_months = math.log((amount_at_retirement * r + P) / (C * r + P)) / math.log(1 + r)
        years = int(total_months // 12)
        months = int(total_months % 12)

        return years, months

    if request.method == 'POST':
        option = request.form.get('option')
        if not option:
            return jsonify({'error': "Missing 'option' in the request."}), 400

        try:
            currently_saved = float(request.form.get('currently_saved', 0))
            annual_return_rate = float(request.form.get('annual_return_rate', 0)) if option in ['1', '2', '3'] else None
            amount_at_retirement = float(request.form.get('amount_at_retirement', 0)) if option in ['1', '3'] else None
            years_until_retirement = int(request.form.get('years_until_retirement', 0)) if option in ['1', '2'] else None
            monthly_savings = float(request.form.get('monthly_savings', 0)) if option in ['2', '3'] else None

        except ValueError as ve:
            return jsonify({'error': f'Invalid input. {str(ve)}'}), 400

        try:
            if option == '1':
                result = calculate_monthly_savings(currently_saved, amount_at_retirement, years_until_retirement, annual_return_rate)
                result_message = f"Monthly Savings Needed: ₹{result:.2f}"
            elif option == '2':
                result = calculate_retirement_amount(currently_saved, monthly_savings, years_until_retirement, annual_return_rate)
                result_message = f"Amount at Retirement: ₹{result:.2f}"
            elif option == '3':
                years, months = calculate_years_until_retirement(currently_saved, amount_at_retirement, monthly_savings, annual_return_rate)
                result_message = f"Years until Retirement: {years} years and {months} months"
            else:
                return jsonify({'error': "Invalid option selected."}), 400

            return jsonify({'result': result_message})

        except Exception as e:
            return jsonify({'error': f'An error occurred: {str(e)}'}), 400

    return render_template('retirement_savings_index.html', result=result_message)
@app.route('/stock-return-calculator', methods=['GET', 'POST'])
def stock_return_calculator():
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
        total_tax_sell = stt_ctt_sell + transaction_charges_sell + gst_sell + dp_charges
        total_tax = total_tax_buy + total_tax_sell

        # Net return after taxes
        net_return = gross_return - total_tax
        net_return_percentage = (net_return / invested_amount) * 100

        # Prepare results to display
        result_message = {
            "invested_amount": f"₹{invested_amount:.2f}",
            "total_sell_amount": f"₹{total_sell_amount:.2f}",
            "result_type": result_type,
            "gross_return": f"₹{abs(gross_return):.2f}",
            "gross_return_percentage": f"{gross_return_percentage:.2f}%",
            "net_return": f"₹{abs(net_return):.2f}",
            "net_return_percentage": f"{net_return_percentage:.2f}%"
        }

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

        # Return result and tax details as JSON
        return jsonify(result=result_message, tax=tax_details)

    return render_template('stock_return_calculator.html')

@app.route('/tip_calculator', methods=['GET', 'POST'])
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

        return jsonify(result=result_message)

    return render_template('tip_index.html', result_message=result_message)


@app.route('/lumpsum-calculator', methods=['GET', 'POST'])
def lumpsum_calculator():
    if request.method == 'GET':
        # Render the HTML form when accessing the route
        return render_template('lumpsum_index.html')
    elif request.method == 'POST':
        try:
            # Process the form data for calculation
            initial_investment = float(request.form['initial_investment'])
            annual_rate = float(request.form['annual_rate']) / 100
            tenure_years = int(request.form['tenure_years'])
            inflation_rate = float(request.form['inflation_rate']) / 100

            # Calculate future value
            future_value = initial_investment * (1 + annual_rate) ** tenure_years

            # Adjust for inflation
            inflation_adjusted_future_value = future_value / ((1 + inflation_rate) ** tenure_years)

            # Prepare response
            result = {
                "future_value": f"₹{future_value:,.2f}",
                "inflation_adjusted_future_value": f"₹{inflation_adjusted_future_value:,.2f}"
            }
            return jsonify(result)

        except (ValueError, KeyError):
            return jsonify({"error": "Invalid input. Please check your inputs and try again."}), 400


@app.route('/sip', methods=['GET', 'POST'])
def sip_calculator():
    result_message = None

    if request.method == 'POST':
        # User inputs
        frequency_choice = int(request.form['frequency_choice'])
        monthly_investment = float(request.form['monthly_investment'])
        
        # Validate expected rate input
        while True:
            expected_rate = float(request.form['expected_rate'])
            if 1 <= expected_rate <= 50:
                break
            else:
                return jsonify(error="Invalid input. Please enter a rate between 1 and 50."), 400

        # Validate tenure input
        while True:
            tenure_years = int(request.form['tenure_years'])
            if 1 <= tenure_years <= 50:
                break
            else:
                return jsonify(error="Invalid input. Please enter a tenure between 1 and 50."), 400

        # Validate inflation rate input
        inflation_rate = float(request.form['inflation_rate'])
        if inflation_rate < 0 or inflation_rate > 50:
            return jsonify(error="Invalid input. Please enter an inflation rate between 0 and 50."), 400

        # Determine deposits per year based on frequency choice
        deposits_per_year = 12 if frequency_choice == 1 else 1

        # Adjusted rate accounting for inflation
        real_rate = ((1 + expected_rate / 100) / (1 + inflation_rate / 100) - 1) * 100

        # Annual rate divided by the number of deposits per year
        period_rate = (real_rate / 100) / deposits_per_year
        total_periods = tenure_years * deposits_per_year

        # Future value calculation using the SIP formula adjusted for inflation
        future_value = monthly_investment * (((1 + period_rate) ** total_periods - 1) / period_rate) * (1 + period_rate)

        # Total amount deposited
        total_amount_deposited = monthly_investment * total_periods

        # Total earnings (future value + total amount deposited)
        total_earnings = total_amount_deposited + future_value

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
            "total_deposited": f"Total Amount Deposited: {format_amount(total_amount_deposited)}",
            "real_rate": f"Adjusted Rate (after inflation): {real_rate:.2f}%"
        }

        return jsonify(result=result_message, future_value=future_value, total_amount_deposited=total_amount_deposited)

    return render_template('sip_calculator.html', result_message=result_message)


@app.route('/step-up-calculator', methods=['GET', 'POST'])
def step_up_calculator():
    if request.method == 'POST':
        try:
            investment = float(request.form.get('investment', 0))
            growth_rate = float(request.form.get('growth_rate', 0))
            rate_of_return = float(request.form.get('rate_of_return', 0))
            tenure = int(request.form.get('tenure', 0))
            inflation_rate = float(request.form.get('inflation_rate', 0))  # New field for inflation
        except ValueError:
            return jsonify(result_message="Invalid input. Please enter numerical values."), 400

        # Input Validation
        if tenure < 1 or tenure > 50:
            return jsonify(result_message="Tenure must be between 1 and 50 years."), 400
        if rate_of_return < 1 or rate_of_return > 50:
            return jsonify(result_message="Rate of return must be between 1% and 50%."), 400
        if growth_rate < 0 or growth_rate > 100:
            return jsonify(result_message="Growth rate must be between 0% and 100%."), 400
        if inflation_rate < 0 or inflation_rate > 100:
            return jsonify(result_message="Inflation rate must be between 0% and 100%."), 400  # Inflation validation
        if investment < 0.01:
            return jsonify(result_message="Monthly Investment Amount must be at least ₹0.01."), 400

        # Converting percentage to decimal
        annual_rate = rate_of_return / 100
        monthly_rate = annual_rate / 12
        total_months = tenure * 12

        future_value = 0
        total_deposit = 0
        data = {}

        for year in range(1, tenure + 1):
            # Calculate the investment amount for the current year
            current_investment = investment * ((1 + growth_rate / 100) ** (year - 1))
            for month in range(1, 13):
                # Calculate remaining months from the current investment point
                month_number = (year - 1) * 12 + month
                months_remaining = total_months - month_number + 1
                future_value += current_investment * ((1 + monthly_rate) ** months_remaining)
                total_deposit += current_investment

            # Store future value for each year
            data[year] = round(future_value, 2)

        # Adjust for inflation
        future_value_adjusted = future_value / ((1 + (inflation_rate / 100)) ** tenure)

        # Total Earnings
        total_earnings = future_value_adjusted - total_deposit

        # Calculate adjusted corpus value for inflation
        adjusted_corpus_value = future_value_adjusted / ((1 + (inflation_rate / 100)) ** tenure)

        # Formatting currency
        def format_currency(value):
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

        result = {
            "total_invested": format_currency(total_deposit),
            "total_earnings": format_currency(total_earnings),
            "total_corpus_value": format_currency(future_value_adjusted),
            "adjusted_corpus_value": format_currency(adjusted_corpus_value)
        }

        return jsonify(result_message=result, data=data)

    return render_template('step_up_calculator.html')

@app.route('/cagr-calculator', methods=['GET', 'POST'])
def cagr_calculator():
    result_message = None
    cagr_return = None

    def calculate_cagr(beginning_value, ending_value, tenure, inflation_rate):
        """Calculate the Compound Annual Growth Rate (CAGR) adjusted for inflation."""
        # Adjust the ending value for inflation
        adjusted_ending_value = ending_value / ((1 + inflation_rate / 100) ** tenure)
        return ((adjusted_ending_value / beginning_value) ** (1 / tenure) - 1) * 100

    if request.method == 'POST':
        try:
            # User inputs
            beginning_value = float(request.form['beginning_value'])
            ending_value = float(request.form['ending_value'])
            tenure = int(request.form['tenure'])
            inflation_rate = float(request.form['inflation_rate'])

            # Validate tenure
            if tenure < 1 or tenure > 50:
                result_message = "Tenure must be between 1 and 50 years."
            else:
                # Calculate CAGR adjusted for inflation
                cagr_return = calculate_cagr(beginning_value, ending_value, tenure, inflation_rate)
                result_message = f"CAGR Return (adjusted for inflation): {cagr_return:.2f}%"
        except ValueError:
            result_message = "Please enter valid numerical values."

    return render_template('cagr_calculator.html', result_message=result_message, cagr_return=cagr_return)


@app.route('/ppf_calculator', methods=['GET', 'POST'])
def ppf_calculator():
    if request.method == 'POST':
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
        inflation_rate = float(request.form['inflation_rate']) / 100  # Convert percentage to decimal

        # Determine frequency multiplier
        deposits_per_year = {1: 12, 2: 4, 3: 2, 4: 1}.get(frequency_choice, 0)

        total_deposited = investment_amount * deposits_per_year * tenure_years
        maturity_amount = 0
        annual_interest_rate = 7.1 / 100  # Annual interest rate

        years = []
        maturity_values = []

        for year in range(tenure_years):
            # Add the deposits for this year
            for month in range(12):
                if deposits_per_year == 12 or (deposits_per_year == 4 and month % 3 == 0) or (deposits_per_year == 2 and month % 6 == 0) or (deposits_per_year == 1 and month == 0):
                    maturity_amount += investment_amount

            # Calculate interest for the current balance at the end of the year
            interest_for_year = maturity_amount * annual_interest_rate
            maturity_amount += interest_for_year

            # Track yearly maturity amount for line chart
            years.append(year + 1)
            maturity_values.append(maturity_amount)

        # Total interest earned
        interest_earned = maturity_amount - total_deposited

        # Calculate real returns after inflation
        real_maturity_amount = maturity_amount / ((1 + inflation_rate) ** tenure_years)
        real_interest_earned = real_maturity_amount - total_deposited

        results = {
            'total_deposited': format_amount(total_deposited),
            'interest_earned': format_amount(interest_earned),
            'real_interest_earned': format_amount(real_interest_earned),
            'maturity_amount': format_amount(maturity_amount),
            'real_maturity_amount': format_amount(real_maturity_amount),
            'years': years,
            'maturity_values': maturity_values
        }

        return jsonify(results)

    return render_template('ppf_calculator.html')


if __name__ == '__main__':
    app.run(debug=True)
