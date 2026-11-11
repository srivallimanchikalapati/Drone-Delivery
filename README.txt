# Smart Drone Food Delivery — Fresh Setup

This is a beginner-friendly Flask + SQLite college project prototype.

## Included
- Five sample restaurant cards and restaurant-specific menus (sample data for Ongole).
- Cart with quantity controls, totals, and package-weight calculation.
- Checkout with customer name, phone number, restaurant, delivery address and optional notes.
- SQLite order storage (`orders.db` is created automatically).
- Server-side price/quantity validation.
- Demo drone selection using package payload, battery percentage and range limits.
- Simulated-annealing metaheuristic for waypoint order; route and distance are illustrative.
- Order detail page, simulated delivery status updates and feedback storage.

## Requirements
- Python 3.10 or newer
- Internet connection for remote food photos (the website itself runs locally)
- VS Code (recommended)

## Windows setup (PowerShell)
1. Extract this ZIP to a folder such as `D:\SmartDroneFoodDelivery`.
2. Open that folder in VS Code: **File → Open Folder**.
3. Open **Terminal → New Terminal**.
4. Run these commands one at a time:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

If `py` is not recognized, install Python from https://www.python.org/downloads/ and tick **Add python.exe to PATH** during setup. Restart VS Code after installation.

5. Open this address in your browser: http://127.0.0.1:5000
6. Keep the terminal open while using the website. Stop the server with `Ctrl+C`.

## Test the full flow
1. Choose one restaurant and add menu items from that same restaurant to the cart.
2. Check total price and package weight.
3. Enter a name, 10–13 digit phone number, and delivery address.
4. Click **Place Food Order**.
5. On the order page, inspect the selected demo drone and route.
6. Try status updates and submit a rating.

## Important project limitation
This is a software simulation for a final-year demonstration. Restaurant data, coordinates, route distances, battery levels, and drone capabilities are illustrative. It does not connect to live maps, GPS, payment gateways, restaurant systems, or physical drones. The landing-page style follows the available SmartDrone Eats design reference, but if the approved design has other exact text/images that are not in the saved code, restore those exact assets before presenting it as pixel-identical.
