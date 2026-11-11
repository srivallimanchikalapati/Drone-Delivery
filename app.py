from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import json
import math
import random
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "orders.db")

app = Flask(__name__)
app.secret_key = "smart-drone-food-delivery-local-demo-key"

# Sample project data. Replace restaurant names/addresses and coordinates with verified local data later.
RESTAURANTS = [
    {"id": "r1", "name": "Ongole Spice Kitchen", "area": "Ongole", "address": "Ongole, Andhra Pradesh",
     "description": "Andhra meals, biryani and homestyle favorites", "image": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=900&q=80"},
    {"id": "r2", "name": "Royal Biryani House", "area": "Ongole", "address": "Ongole, Andhra Pradesh",
     "description": "Aromatic biryani and rice specials", "image": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?auto=format&fit=crop&w=900&q=80"},
    {"id": "r3", "name": "Coastal Tiffins", "area": "Ongole", "address": "Ongole, Andhra Pradesh",
     "description": "Dosa, idli and South Indian tiffins", "image": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=900&q=80"},
    {"id": "r4", "name": "Pizza & More", "area": "Ongole", "address": "Ongole, Andhra Pradesh",
     "description": "Pizza, burgers and quick bites", "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=900&q=80"},
    {"id": "r5", "name": "Green Bowl Cafe", "area": "Ongole", "address": "Ongole, Andhra Pradesh",
     "description": "Fresh bowls, snacks and beverages", "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=900&q=80"},
]
MENU = [
    {"id": "m1", "restaurant_id": "r1", "name": "Andhra Veg Meals", "price": 160, "weight": 450, "image": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=700&q=80", "category": "Meals"},
    {"id": "m2", "restaurant_id": "r1", "name": "Chicken Biryani", "price": 220, "weight": 600, "image": "https://images.unsplash.com/photo-1633945274405-b6c8069047b0?auto=format&fit=crop&w=700&q=80", "category": "Biryani"},
    {"id": "m3", "restaurant_id": "r1", "name": "Paneer Curry with Rice", "price": 190, "weight": 500, "image": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=700&q=80", "category": "Meals"},
    {"id": "m4", "restaurant_id": "r2", "name": "Chicken Dum Biryani", "price": 240, "weight": 650, "image": "https://images.unsplash.com/photo-1563379091339-03246963d96c?auto=format&fit=crop&w=700&q=80", "category": "Biryani"},
    {"id": "m5", "restaurant_id": "r2", "name": "Veg Biryani", "price": 170, "weight": 500, "image": "https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&w=700&q=80", "category": "Biryani"},
    {"id": "m6", "restaurant_id": "r3", "name": "Masala Dosa", "price": 90, "weight": 350, "image": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?auto=format&fit=crop&w=700&q=80", "category": "Tiffins"},
    {"id": "m7", "restaurant_id": "r3", "name": "Idli (4 pieces)", "price": 60, "weight": 300, "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?auto=format&fit=crop&w=700&q=80", "category": "Tiffins"},
    {"id": "m8", "restaurant_id": "r4", "name": "Margherita Pizza", "price": 220, "weight": 550, "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=700&q=80", "category": "Fast Food"},
    {"id": "m9", "restaurant_id": "r4", "name": "Veg Burger", "price": 110, "weight": 300, "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=700&q=80", "category": "Fast Food"},
    {"id": "m10", "restaurant_id": "r5", "name": "Fresh Garden Bowl", "price": 150, "weight": 350, "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=700&q=80", "category": "Healthy"},
]

# Example delivery coordinates in a small fictional map area around Ongole.
# Distances are simulated for academic demonstration, not live GPS distances.
NODES = {
    "Restaurant": (0.0, 0.0),
    "Pickup Junction": (1.0, 2.0),
    "Main Road": (3.0, 1.5),
    "Market Junction": (4.0, 4.0),
    "Residential Area": (6.0, 3.0),
    "Customer Address": (7.0, 5.0),
}
WAYPOINTS = ["Pickup Junction", "Main Road", "Market Junction", "Residential Area", "Customer Address"]
# Simulated GPS coordinates for Ongole map tracking
MAP_COORDINATES = {
    "Restaurant": [15.5057, 80.0499],
    "Pickup Junction": [15.5080, 80.0520],
    "Main Road": [15.5100, 80.0550],
    "Market Junction": [15.5120, 80.0580],
    "Residential Area": [15.5150, 80.0610],
    "Customer Address": [15.5180, 80.0640],
}

DRONES = [
    {"name": "Drone Mini", "payload_g": 500, "range_km": 5.0, "battery_percent": 95},
    {"name": "Drone Standard", "payload_g": 1200, "range_km": 12.0, "battery_percent": 90},
    {"name": "Drone Pro", "payload_g": 2000, "range_km": 20.0, "battery_percent": 98},
]

def db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db_connection() as conn:
        conn.execute("""
            
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    customer TEXT NOT NULL,
    phone TEXT NOT NULL,
    restaurant_id TEXT NOT NULL,
    restaurant_name TEXT NOT NULL,
    address TEXT NOT NULL,
    notes TEXT,
    items_json TEXT NOT NULL,
    total REAL NOT NULL,
    total_weight_g INTEGER NOT NULL,
    drone_name TEXT NOT NULL,
    route_json TEXT NOT NULL,
    route_distance_km REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Order received',
    feedback INTEGER,
    feedback_note TEXT,
    payload_capacity_g INTEGER,
    payload_margin_g INTEGER,
    required_round_trip_km REAL,
    safe_range_km REAL,
    battery_start_percent INTEGER,
    battery_minimum_percent INTEGER,
    battery_margin_percent INTEGER
)
        """)

        
        # Safely add new drone-safety columns to existing databases.
        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(orders)").fetchall()
        }

        new_columns = {
            "payload_capacity_g": "INTEGER",
            "payload_margin_g": "INTEGER",
            "required_round_trip_km": "REAL",
            "safe_range_km": "REAL",
            "battery_start_percent": "INTEGER",
            "battery_minimum_percent": "INTEGER",
            "battery_margin_percent": "INTEGER",
            "initial_route_distance_km": "REAL",
            "optimization_savings_km": "REAL",
        }

        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                conn.execute(
                    f"ALTER TABLE orders ADD COLUMN {column_name} {column_type}"
                )


def distance(a, b):
    ax, ay = NODES[a]
    bx, by = NODES[b]
    return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)

def route_length(route):
    return sum(distance(route[i], route[i + 1]) for i in range(len(route) - 1))


def optimize_route():
    """
    Simulated Annealing route optimization for the project demo.
    Returns the initial route and the best route found.
    """
    initial_route = ["Restaurant"] + WAYPOINTS[:]
    current = WAYPOINTS[:]
    best = current[:]

    initial_distance = route_length(initial_route)
    best_distance = initial_distance
    current_distance = initial_distance

    temperature = 10.0

    for _ in range(1200):
        candidate = current[:]

        i, j = sorted(random.sample(range(len(candidate)), 2))
        candidate[i], candidate[j] = candidate[j], candidate[i]

        candidate_route = ["Restaurant"] + candidate
        candidate_distance = route_length(candidate_route)

        if (
            candidate_distance < current_distance
            or random.random() < math.exp(
                (current_distance - candidate_distance)
                / max(temperature, 0.01)
            )
        ):
            current = candidate
            current_distance = candidate_distance

        if current_distance < best_distance:
            best = current[:]
            best_distance = current_distance

        temperature *= 0.996

    optimized_route = ["Restaurant"] + best

    return {
        "initial_route": initial_route,
        "optimized_route": optimized_route,
        "initial_distance": round(initial_distance * 0.65, 2),
        "optimized_distance": round(best_distance * 0.65, 2),
    }


def select_drone(weight_g, route_distance):
    """
    Select a demo drone using package weight, route range,
    and a minimum battery threshold.
    All calculations are estimates for the project simulation.
    """
    required_round_trip_km = route_distance * 2

    for drone in DRONES:
        safe_range_km = drone["range_km"] * 0.75

        if (
            weight_g <= drone["payload_g"]
            and required_round_trip_km <= safe_range_km
            and drone["battery_percent"] >= 30
        ):
            selected_drone = drone.copy()
            selected_drone["battery_start_percent"] = drone["battery_percent"]

            # Additional safety information for the order report
            selected_drone["payload_margin_g"] = (
                drone["payload_g"] - weight_g
            )
            selected_drone["required_round_trip_km"] = round(
                required_round_trip_km, 2
            )
            selected_drone["safe_range_km"] = round(
                safe_range_km, 2
            )
            selected_drone["battery_minimum_percent"] = 30
            selected_drone["battery_margin_percent"] = (
                drone["battery_percent"] - 30
            )

            return selected_drone

    return None

@app.route("/", methods=["GET"])
def home():
    restaurant_id = request.args.get("restaurant", "")
    return render_template("index.html", restaurants=RESTAURANTS, menu=MENU,
                           selected_restaurant=restaurant_id)

@app.route("/place-order", methods=["POST"])
def place_order():
    customer = request.form.get("customer", "").strip()
    phone = request.form.get("phone", "").strip()
    restaurant_id = request.form.get("restaurant_id", "").strip()
    address = request.form.get("address", "").strip()
    notes = request.form.get("notes", "").strip()
    raw_items = request.form.get("items_json", "[]")

    if not customer or not phone or not address:
        flash("Please enter your name, phone number and delivery address.", "error")
        return redirect(url_for("home", _anchor="checkout"))
    if not phone.isdigit() or not (10 <= len(phone) <= 13):
        flash("Enter a valid phone number using 10 to 13 digits.", "error")
        return redirect(url_for("home", _anchor="checkout"))

    restaurant = next((r for r in RESTAURANTS if r["id"] == restaurant_id), None)
    if not restaurant:
        flash("Please choose a restaurant.", "error")
        return redirect(url_for("home", _anchor="checkout"))
    try:
        submitted_items = json.loads(raw_items)
    except (ValueError, TypeError):
        submitted_items = []
    if not isinstance(submitted_items, list) or not submitted_items:
        flash("Your cart is empty. Add at least one menu item before placing an order.", "error")
        return redirect(url_for("home", _anchor="food"))

    # Trust only server-side menu prices and weights, never browser-submitted prices.
    menu_by_id = {item["id"]: item for item in MENU if item["restaurant_id"] == restaurant_id}
    clean_items, total, total_weight = [], 0, 0
    for entry in submitted_items:
        if not isinstance(entry, dict):
            continue
        item = menu_by_id.get(str(entry.get("id", "")))
        try:
            quantity = int(entry.get("quantity", 0))
        except (ValueError, TypeError):
            quantity = 0
        if item and 1 <= quantity <= 20:
            subtotal = item["price"] * quantity
            weight = item["weight"] * quantity
            clean_items.append({"id": item["id"], "name": item["name"], "price": item["price"],
                                "quantity": quantity, "subtotal": subtotal, "weight_g": weight})
            total += subtotal
            total_weight += weight
    if not clean_items:
        flash("No valid items were found for that restaurant. Please add your food again.", "error")
        return redirect(url_for("home", _anchor="food"))

    route_result = optimize_route()
    route = route_result["optimized_route"]
    distance_km = route_result["optimized_distance"]  # scaled demo distance
    initial_distance_km = route_result["initial_distance"]
    optimization_savings_km = round(
        initial_distance_km - distance_km, 2
    )

    drone = select_drone(total_weight, distance_km)
    if drone is None:
        flash(f"Order weight is {total_weight} g. No demo drone passes the payload/range safety checks. Reduce the order weight.", "error")
        return redirect(url_for("home", _anchor="checkout"))

    
    with db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
    INSERT INTO orders (
        created_at, customer, phone, restaurant_id, restaurant_name,
        address, notes, items_json, total, total_weight_g,
        drone_name, route_json, route_distance_km, status,
        payload_capacity_g, payload_margin_g,
        required_round_trip_km, safe_range_km,
        battery_start_percent, battery_minimum_percent,
        battery_margin_percent, initial_route_distance_km,
        optimization_savings_km
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            customer,
            phone,
            restaurant_id,
            restaurant["name"],
            address,
            notes,
            json.dumps(clean_items),
            total,
            total_weight,
            drone["name"],
            json.dumps(route),
            distance_km,
            "Order received",
            drone["payload_g"],
            drone["payload_margin_g"],
            drone["required_round_trip_km"],
            drone["safe_range_km"],
            drone["battery_start_percent"],
            drone["battery_minimum_percent"],
            drone["battery_margin_percent"], 
            initial_distance_km,
            optimization_savings_km
        ))
        
        order_id = cur.lastrowid
    return redirect(url_for("order_detail", order_id=order_id))

@app.route("/order/<int:order_id>", methods=["GET"])
def order_detail(order_id):
    with db_connection() as conn:
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        flash("Order not found.", "error")
        return redirect(url_for("home"))
    data = dict(order)
    data["items"] = json.loads(data["items_json"])
    data["route"] = json.loads(data["route_json"])
    statuses = ["Order received", "Restaurant preparing", "Ready for pickup", "Drone assigned", "Out for delivery", "Delivered"]
    return render_template("order.html", order=data, statuses=statuses)
    
@app.route("/track/<int:order_id>")
def track_order(order_id):
    with db_connection() as conn:
        order = conn.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,)
        ).fetchone()

    if order is None:
        flash("Order not found.", "error")
        return redirect(url_for("home"))

    data = dict(order)
    data["route"] = json.loads(data["route_json"])

    map_route = []

    for point in data["route"]:
        if point in MAP_COORDINATES:
            map_route.append({
                "name": point,
                "coordinates": MAP_COORDINATES[point]
            })

    return render_template(
        "tracking.html",
        order=data,
        map_route=map_route,
        map_coordinates=MAP_COORDINATES
    )

@app.route("/order/<int:order_id>/status", methods=["POST"])
def update_status(order_id):
    # Academic demo control: allows stepping through simulated delivery states.
    next_status = request.form.get("status", "")
    allowed = ["Order received", "Restaurant preparing", "Ready for pickup", "Drone assigned", "Out for delivery", "Delivered"]
    if next_status not in allowed:
        flash("Invalid delivery status.", "error")
        return redirect(url_for("order_detail", order_id=order_id))
    with db_connection() as conn:
        exists = conn.execute("SELECT id FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not exists:
            flash("Order not found.", "error")
            return redirect(url_for("home"))
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (next_status, order_id))
    flash("Demo delivery status updated.", "success")
    return redirect(url_for("order_detail", order_id=order_id))

@app.route("/order/<int:order_id>/feedback", methods=["POST"])
def feedback(order_id):
    rating = request.form.get("rating", "")
    note = request.form.get("feedback_note", "").strip()
    if rating not in {"1", "2", "3", "4", "5"}:
        flash("Please select a rating from 1 to 5.", "error")
        return redirect(url_for("order_detail", order_id=order_id))
    with db_connection() as conn:
        exists = conn.execute("SELECT id FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not exists:
            flash("Order not found.", "error")
            return redirect(url_for("home"))
        conn.execute("UPDATE orders SET feedback = ?, feedback_note = ? WHERE id = ?",
                     (int(rating), note, order_id))
    flash("Thank you! Your feedback has been saved.", "success")
    return redirect(url_for("order_detail", order_id=order_id))

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "app": "Smart Drone Food Delivery"}

init_db()

print("\nREGISTERED FLASK ROUTES:")
print("TRACKING ROUTE:", app.view_functions.get("track_order"))
print("ALL ROUTES:", app.url_map)

if __name__ == "__main__":
    app.run(debug=True)