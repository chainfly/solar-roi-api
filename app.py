from flask import Flask, request, jsonify, render_template

from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)  # Swagger UI enabled

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/roi', methods=['POST'])
def calculate_roi():
    """
    Calculate ROI and Payback Period for a Solar Plant Investment
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            capex:
              type: number
              example: 200000
              description: Capital Expenditure (₹)
            opex:
              type: number
              example: 5000
              description: Operating Expenses per year (₹)
            generation:
              type: number
              example: 8000
              description: Energy Generation per year (kWh)
            tariff:
              type: number
              example: 6.0
              description: Tariff (₹/kWh)
            lifetime:
              type: integer
              example: 25
              description: Lifetime of the plant (years)
            inflation_rate:
              type: number
              example: 0.022
              description: Annual inflation rate (default 2.2%)
            discount_rate:
              type: number
              example: 0.04
              description: Discount rate for present value (default 4%)
            efficiency_drift:
              type: number
              example: 0.005
              description: Annual panel degradation rate (default 0.5%)
            one_time_incentive:
              type: number
              example: 10000
              description: One-time government incentive/subsidy (₹)
            feed_in_tariff_bonus:
              type: number
              example: 0.5
              description: ₹/kWh bonus if selling power to grid (optional)
    responses:
      200:
        description: ROI and Payback Period calculated successfully
        examples:
          application/json:
            annual_savings: [43000.0, 42785.0, 42571.0]
            payback_period_years: 4.65
            roi_percent: 330.0
            total_profit: 660000.0
    """

    try:
        data = request.json

        capex = float(data['capex'])
        opex = float(data['opex'])
        generation = float(data['generation'])
        tariff = float(data['tariff'])

        # Optional parameters with defaults
        lifetime = int(data.get('lifetime', 25))
        inflation_rate = float(data.get('inflation_rate', 0.022))
        discount_rate = float(data.get('discount_rate', 0.04))
        efficiency_drift = float(data.get('efficiency_drift', 0.005))
        one_time_incentive = float(data.get('one_time_incentive', 0))
        feed_in_tariff_bonus = float(data.get('feed_in_tariff_bonus', 0))

        annual_savings = []
        utility_costs = []
        cumulative_savings = []

        current_generation = generation
        total_discounted_savings = 0
        cumulative = 0
        payback_year = None

        for year in range(1, lifetime + 1):
            degraded_gen = current_generation * (1 - efficiency_drift) ** (year - 1)
            effective_tariff = tariff + feed_in_tariff_bonus
            annual_revenue = degraded_gen * effective_tariff
            annual_profit = annual_revenue - opex
            inflated_utility_cost = tariff * degraded_gen * ((1 + inflation_rate) ** (year - 1))

            discounted_profit = annual_profit / ((1 + discount_rate) ** year)
            total_discounted_savings += discounted_profit
            cumulative += annual_profit

            annual_savings.append(round(annual_profit, 2))
            utility_costs.append(round(inflated_utility_cost, 2))
            cumulative_savings.append(round(cumulative, 2))

            if not payback_year and cumulative >= capex - one_time_incentive:
                payback_year = year

        net_profit = cumulative - capex + one_time_incentive
        roi_percent = (net_profit / capex) * 100

        return jsonify({
            "capex": capex,
            "opex": opex,
            "lifetime": lifetime,
            "inflation_rate": inflation_rate,
            "discount_rate": discount_rate,
            "efficiency_drift": efficiency_drift,
            "annual_savings": annual_savings,
            "utility_costs": utility_costs,
            "cumulative_savings": cumulative_savings,
            "payback_period_years": payback_year if payback_year else "Not achieved",
            "roi_percent": round(roi_percent, 2),
            "total_profit": round(net_profit, 2)
        })

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


import os

if __name__ == '__main__':
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
