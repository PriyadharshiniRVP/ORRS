from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the dataset
data = pd.read_csv(R"C:\Users\priya\Downloads\OnlineRetail (1) (1).xlsx - OnlineRetail.csv")

# Convert InvoiceDate to datetime format
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])

# Add a month column for month-wise analysis
data['Month'] = data['InvoiceDate'].dt.month

# Find globally popular items
global_popularity = data.groupby('StockCode')['Quantity'].sum().sort_values(ascending=False)

# Find country-wise popular items
country_popularity = data.groupby(['Country', 'StockCode'])['Quantity'].sum().sort_values(ascending=False)

# Find month-wise popular items
month_popularity = data.groupby(['Month', 'StockCode'])['Quantity'].sum().sort_values(ascending=False)

def get_recommendations(context='global', country=None, month=None, num_recommendations=5):
    """
    Generate product recommendations based on popularity.

    Parameters:
    - context (str): The type of recommendation ('global', 'country', 'month').
    - country (str): The country for country-based recommendations.
    - month (int): The month (1-12) for month-based recommendations.
    - num_recommendations (int): The number of recommendations to return.

    Returns:
    - List of recommended products with IDs and names.
    """
    
    recommendations = []
    
    if context == 'global':
        top_items = global_popularity.head(num_recommendations).index.tolist()
        for item in top_items:
            product_info = data[data['StockCode'] == item].iloc[0]
            recommendations.append((item, product_info['Description']))
    
    elif context == 'country' and country:
        country_data = country_popularity.loc[country].sort_values(ascending=False)
        top_items = country_data.head(num_recommendations).index.tolist()
        for item in top_items:
            product_info = data[data['StockCode'] == item].iloc[0]
            recommendations.append((item, product_info['Description']))
    
    elif context == 'month' and month:
        month_data = month_popularity.loc[month].sort_values(ascending=False)
        top_items = month_data.head(num_recommendations).index.tolist()
        for item in top_items:
            product_info = data[data['StockCode'] == item].iloc[0]
            recommendations.append((item, product_info['Description']))
    
    return recommendations

@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    if request.method == 'POST':
        context = request.form.get('context')
        country = request.form.get('country')
        month = request.form.get('month')

        if context == 'country' and country:
            recommendations = get_recommendations(context='country', country=country)
        elif context == 'month' and month:
            recommendations = get_recommendations(context='month', month=int(month))
        else:
            recommendations = get_recommendations(context='global')

    return render_template('index.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)

