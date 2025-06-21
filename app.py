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
              example: 20
              description: Lifetime of the plant (years)
    responses:
      200:
        description: ROI and Payback Period calculated successfully
        examples:
          application/json: {
            "annual_profit": 43000.0,
            "payback_period_years": 4.65,
            "roi_percent": 330.0,
            "total_profit": 660000.0
          }

    """
    try:
        data = request.json

        capex = float(data['capex'])
        opex = float(data['opex'])
        generation = float(data['generation'])
        tariff = float(data['tariff'])
        lifetime = int(data.get('lifetime', 25))

        annual_revenue = generation * tariff
        annual_profit = annual_revenue - opex

        if annual_profit <= 0:
            return jsonify({"error": "Annual profit is zero or negative. Please check your inputs."}), 400

        payback_period = capex / annual_profit
        roi = ((annual_profit * lifetime - capex) / capex) * 100
        total_profit = annual_profit * lifetime - capex

        return jsonify({
            "annual_profit": round(annual_profit, 2),
            "payback_period_years": round(payback_period, 2),
            "roi_percent": round(roi, 2),
            "total_profit": round(total_profit, 2)
        })

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
