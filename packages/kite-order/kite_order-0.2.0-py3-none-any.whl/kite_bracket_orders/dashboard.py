import json
import logging
import os
from kiteconnect import KiteConnect

CONFIG_FILE = 'credentials/config.json'  # Updated path

class KiteDashboard:
    def __init__(self, config_path=CONFIG_FILE):
        self.config_path = config_path
        self.kite = None
        self.api_key = None
        self.api_secret = None
        self.access_token = None
        self._load_config()
        self._init_kite()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            logging.error(f"❌ '{self.config_path}' not found.")
            raise FileNotFoundError(f"Config file '{self.config_path}' is missing.")
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        kite_cfg = config.get('KITE', {})
        session = config.get('SESSION', {})
        self.api_key = kite_cfg.get('API_KEY')
        self.api_secret = kite_cfg.get('API_SECRET')
        self.access_token = session.get('ACCESS_TOKEN')
        if not self.api_key or not self.api_secret or not self.access_token:
            raise ValueError("Missing API_KEY, API_SECRET, or ACCESS_TOKEN in config.")

    def _init_kite(self):
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(self.access_token)

    def show_margin(self):
        try:
            margin = self.kite.margins()
            print("\n💰 Margin Details:")
            equity = margin.get("equity", {})
            print(f"         Net Balance     : ₹{equity.get('net', 0):.2f}")
            print(f"         Cash Available  : ₹{equity.get('available', {}).get('cash', 0):.2f}")
            print(f"         Opening Balance : ₹{equity.get('available', {}).get('opening_balance', 0):.2f}")
            print(f"         Utilised Margin : ₹{equity.get('utilised', {}).get('debits', 0):.2f}")
        except Exception as e:
            print(f"❌ Error fetching margin: {e}")

    def show_holdings(self):
        try:
            holdings = self.kite.holdings()
            print("📈 Holdings:")
            if not holdings:
                print("  No holdings found.")
                return
            print(f"{'Symbol':<12} {'Exchange':<6} {'Qty':>5} {'Avg Cost':>10} {'LTP':>10} {'PnL ₹':>10} {'PnL %':>8}")
            print("-" * 70)
            for h in holdings:
                symbol = h['tradingsymbol']
                exch = h['exchange']
                qty = h['quantity']
                avg_price = h['average_price'] or 0
                ltp = h['last_price'] or 0
                pnl = h['pnl'] or 0.0
                invested = avg_price * qty
                pnl_percent = (pnl / invested * 100) if invested > 0 else 0
                print(f"{symbol:<12} {exch:<6} {qty:>5} {avg_price:>10.2f} {ltp:>10.2f} {pnl:>10.2f} {pnl_percent:>7.2f}%")
        except Exception as e:
            print(f"❌ Error fetching holdings: {e}")

    def show_positions(self):
        try:
            positions = self.kite.positions()
            print("📊 Positions:")
            net_positions = positions.get("net", [])
            if not net_positions:
                print("  No open positions.")
                return
            print(f"{'Symbol':<12} {'Qty':>5} {'Buy Avg':>10} {'LTP':>10} {'PnL ₹':>10} {'PnL %':>8}")
            print("-" * 60)
            for p in net_positions:
                symbol = p['tradingsymbol']
                qty = p['quantity']
                buy_avg = p['average_price'] or 0
                ltp = p['last_price'] or 0
                pnl = p['pnl'] or 0.0
                invested = buy_avg * qty
                pnl_percent = (pnl / invested * 100) if invested > 0 else 0
                print(f"{symbol:<12} {qty:>5} {buy_avg:>10.2f} {ltp:>10.2f} {pnl:>10.2f} {pnl_percent:>7.2f}%")
        except Exception as e:
            print(f"❌ Error fetching positions: {e}")

    def show_orders(self, limit=50, status_filter=None):
        try:
            orders = self.kite.orders()
            print("\n📝 Recent Orders:")
            if not orders:
                print("  No orders found.")
                return
            if status_filter:
                orders = [o for o in orders if o['status'] == status_filter.upper()]
                if not orders:
                    print(f"  No orders found with status: {status_filter}")
                    return
            print(f"{'Order ID':<15} {'Symbol':<12} {'Type':<4} {'Status':<16} {'Qty':>5} {'Price':>8}")
            print("-" * 70)
            for o in orders[-limit:]:
                print(f"{o['order_id']:<15} {o['tradingsymbol']:<12} {o['transaction_type']:<4} "
                      f"{o['status']:<16} {o['quantity']:>5} {o['price']:>8.2f}")
            print("-" * 70)
        except Exception as e:
            print(f"❌ Error fetching orders: {e}")

    def show_all(self):
        self.show_margin()
        print()
        self.show_holdings()
        print()
        self.show_positions()
        print()
        self.show_orders(status_filter="OPEN")      # Only open orders
        self.show_orders(status_filter="COMPLETE")  # Only completed orders
        self.show_orders(status_filter="CANCELLED")  # Only CANCELLED orders
        self.show_orders()  # All orders

# --- Entry Point ---
if __name__ == "__main__":
    dash = KiteDashboard()
    dash.show_all()
