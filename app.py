from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

transport = pd.read_csv("transport.csv")
hotels = pd.read_csv("hotels.csv")
food = pd.read_csv("food.csv")
places = pd.read_csv("places.csv")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/result', methods=['POST'])
def result():
    budget = int(request.form['budget'])
    source = request.form['source'].strip().title()
    mid = request.form['mid'].strip().title()
    dest = request.form['destination'].strip().title()
    days = int(request.form['days'])
    mode = request.form['mode']
    hotel_type = request.form['hotel_type']

    t1_data = transport[(transport['From'] == source) & (transport['To'] == mid)]
    t2_data = transport[(transport['From'] == mid) & (transport['To'] == dest)]

    if t1_data.empty or t2_data.empty:
        return "No route available 😢"

    # Transport logic
    if mode == "cheap":
        t1 = t1_data.sort_values(by='Price').iloc[0]
        t2 = t2_data.sort_values(by='Price').iloc[0]

    elif mode == "fast":
        t1 = t1_data[t1_data['Type'] == 'Flight']
        t2 = t2_data[t2_data['Type'] == 'Flight']

        t1 = t1.iloc[0] if not t1.empty else t1_data.iloc[-1]
        t2 = t2.iloc[0] if not t2.empty else t2_data.iloc[-1]

    else:
        t1 = t1_data[t1_data['Type'] == 'Train'].iloc[0]
        t2 = t2_data[t2_data['Type'] == 'Train'].iloc[0]

    transport_cost = t1['Price'] + t2['Price']

    # Hotel logic
    h_data = hotels[(hotels['City'] == dest) & (hotels['Type'] == hotel_type)]
    if h_data.empty:
        return "No hotel type available 😢"

    h = h_data.iloc[0]

    f_data = food[food['City'] == dest]
    if f_data.empty:
        return "No food data 😢"

    f = f_data.sort_values(by='Price').iloc[0]

    hotel_cost = h['Price'] * days

    total = transport_cost + hotel_cost + f['Price']
    remaining = budget - total

    place_list = places[places['City'] == mid]['Place'].tolist()

    return render_template("result.html",
                           t1=t1, t2=t2,
                           h=h, f=f,
                           total=total,
                           remaining=remaining,
                           budget=budget,
                           mid=mid,
                           place_list=place_list)

@app.route('/book')
def book():
    return "<h2>Booking Successful ✅</h2>"

if __name__ == '__main__':
    app.run(debug=True)