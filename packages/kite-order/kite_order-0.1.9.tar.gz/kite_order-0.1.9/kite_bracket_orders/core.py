import json
import time
from kiteconnect import KiteConnect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from colorama import Fore, Style
from .utils import *
from .auth import main as run_login  # Import login if needed


class BracketOrderPlacer:
    def __init__(self, code_data=None, enable_logging=True):  # Added enable_logging param (defaults to True)
        if enable_logging:
            setup_logging()  # Call only if logging is enabled
        self.kite = self.load_kite()
        self.code_data = code_data  # Store hardcoded data from order.py for choice "1"


    # --- Load Kite API --- (unchanged)
    def load_kite(self):
        with open("credentials/config.json") as f:
            config = json.load(f)
        kite = KiteConnect(api_key=config["KITE"]["API_KEY"])
        try:
            kite.set_access_token(config["SESSION"]["ACCESS_TOKEN"])
        except KeyError:
            run_login()  # Run login if token missing
            with open("credentials/config.json") as f:  # Reload config after login
                config = json.load(f)
            kite.set_access_token(config["SESSION"]["ACCESS_TOKEN"])
        return kite


    # --- Load Kite API and Show Login Name --- (unchanged)
    def load_kite_login_name_show(self):
        with open("credentials/config.json") as f:
            config = json.load(f)
        kite = KiteConnect(api_key=config["KITE"]["API_KEY"])
        try:
            kite.set_access_token(config["SESSION"]["ACCESS_TOKEN"])
        except KeyError:
            run_login()  # Run login if token missing
            with open("credentials/config.json") as f:  # Reload config after login
                config = json.load(f)
            kite.set_access_token(config["SESSION"]["ACCESS_TOKEN"])
        profile = kite.profile()  # Fetch user profile after authentication
        safe_print(f"✅ Logged in as: 🧔 {profile.get('user_name')} ({profile.get('user_id')})")
        return kite


    # --- Load Google Sheets --- (unchanged)
    def load_sheets(self):
        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials/credentials.json", scope)
            client = gspread.authorize(creds)
            sheet = client.open("PyTrade").worksheet("Trade Plans")
            sheet_data = sheet.get_all_records()
            if not sheet_data:
                logging.error("❌ No data found in 'PyTrade' Google Sheet.")  # Logs only if enabled
                return []
            safe_print(f"\n📋 Loaded {len(sheet_data)} rows from 'PyTrade' Google Sheet")
            return sheet_data
        except Exception as e:
            logging.error(f"❌ Failed to load 'PyTrade' Google Sheet: {e}")  # Logs only if enabled
            return []


    # --- Track Entry Order --- (new method)
    def track_entry_order(self, entry_order_id, target_price, stop_loss_trigger, stop_loss_limit, sl_type):
        self.kite = self.load_kite()
        safe_print(f"\n⌛ Tracking entry order: {entry_order_id}...")
        # Wait for entry order to fill
        retry_until_success(
            is_filled,
            self.kite,
            entry_order_id,
            interval=30,
            reconnect_func=lambda: (safe_print(f"\n🔌 Monitor error. Reconnecting..."), setattr(self, 'kite', self.load_kite())),
            periodic_msg="⌛ Reconnected, Waiting for entry fill..."
        )
        safe_print(f"\n✅ {Fore.MAGENTA}Entry Order filled!{Style.RESET_ALL}")

        # Fetch order details to get symbol, quantity, etc.
        try:
            order_details = self.kite.order_history(entry_order_id)[-1]
            symbol = order_details["tradingsymbol"]
            quantity = order_details["quantity"]
            exchange = order_details["exchange"]
            product = order_details["product"]
            transaction_type = order_details["transaction_type"]
            exit_transaction_type = self.kite.TRANSACTION_TYPE_SELL if transaction_type == self.kite.TRANSACTION_TYPE_BUY else self.kite.TRANSACTION_TYPE_BUY
        except Exception as e:
            safe_print(f"❌ Failed to fetch order details: {e}")
            return

        # Place Target Order
        target_id = self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange=exchange,
            tradingsymbol=symbol,
            transaction_type=exit_transaction_type,
            quantity=quantity,
            order_type=self.kite.ORDER_TYPE_LIMIT,
            price=target_price,
            product=product,
        )

        # Place Stop Loss Order
        sl_order_type = self.kite.ORDER_TYPE_SL if sl_type == "SL" else self.kite.ORDER_TYPE_SLM
        sl_order = {
            "variety": self.kite.VARIETY_REGULAR,
            "exchange": exchange,
            "tradingsymbol": symbol,
            "transaction_type": exit_transaction_type,
            "quantity": quantity,
            "order_type": sl_order_type,
            "trigger_price": stop_loss_trigger,
            "product": product
        }
        if sl_type == "SL":
            sl_order["price"] = stop_loss_limit
        sl_id = self.kite.place_order(**sl_order)

        safe_print(f"\n🎯 Target placed: {target_id}")
        safe_print(f"🛑 Stop-loss placed: {sl_id} ({sl_type})")

        # Monitor Until One Hits
        safe_print("\n📡 Monitoring SL/Target...")
        while True:
            try:
                if is_filled(self.kite, target_id):
                    safe_print(f"\n🎯🎯 {Fore.GREEN}Target Hit. Cancelling SL...{Style.RESET_ALL}")
                    cancel_order_safe(self.kite, sl_id)
                    break
                elif is_filled(self.kite, sl_id):
                    safe_print(f"\n🛑🛑 {Fore.RED}SL Hit. Cancelling Target...{Style.RESET_ALL}")
                    cancel_order_safe(self.kite, target_id)
                    break
            except Exception as e:
                safe_print(f"\n🔌 Monitor error. Reconnecting... {e}")
                self.kite = self.load_kite()
                safe_print("\n📡 Reconnected, Monitoring SL/Target...")
                time.sleep(30)

        safe_print("\n✅✅ Bracket order cycle completed ✅✅")


    # --- Track SL/Target Orders --- (new method)
    def track_sl_target_orders(self, target_order_id, sl_order_id):
        self.kite = self.load_kite()
        safe_print("\n📡 Monitoring SL/Target...")
        while True:
            try:
                if is_filled(self.kite, target_order_id):
                    safe_print(f"\n🎯🎯 {Fore.GREEN}Target Hit. Cancelling SL...{Style.RESET_ALL}")
                    cancel_order_safe(self.kite, sl_order_id)
                    break
                elif is_filled(self.kite, sl_order_id):
                    safe_print(f"\n🛑🛑 {Fore.RED}SL Hit. Cancelling Target...{Style.RESET_ALL}")
                    cancel_order_safe(self.kite, target_order_id)
                    break
            except Exception as e:
                safe_print(f"\n🔌 Monitor error. Reconnecting... {e}")
                self.kite = self.load_kite()
                safe_print("\n📡 Reconnected, Monitoring SL/Target...")
                time.sleep(30)
        safe_print("\n✅✅ Bracket order cycle completed ✅✅")


    # --- Place Bracket Order --- (unchanged)
    def place_bracket_order(self):
        # === Market Check and AMO Prompt ===
        is_closed = not is_market_open() or is_weekend()
        use_amo = False
        if is_closed:
            safe_print("\n" + "="*50)
            safe_print(f"        ❌ Market is currently {Fore.RED}CLOSED{Style.RESET_ALL} ❌")
            safe_print("="*50 + "\n")
            while True:
                user_amo = input(f"⚠️  Do you want to place {Fore.GREEN}AMO Order{Style.RESET_ALL} ? (Y/N): ").strip().upper()
                if user_amo == "Y":
                    use_amo = True
                    safe_print("✅ Proceeding with AMO entry order only...")
                    break
                elif user_amo == "N":
                    safe_print("❌ Cancelled by user due to market closure.")
                    return
                else:
                    safe_print("❌ Invalid input. Please enter Y or N.")


        safe_print("\n📊 Order Options:")
        safe_print("━"*18 + "\n")
        safe_print("1. Use Code Input")
        safe_print("2. Use Google Sheets Input")
        choice = input("\n🔘 Choose 1 or 2: ").strip()


        required_keys = [
            "segment", "product_type", "side", "entry_order_type", "sl_type",
            "symbol", "quantity", "entry_price", "target_price", "stop_loss_trigger", "stop_loss_limit"
        ]
        data = None
        if choice == "1":
            if self.code_data is None:
                safe_print("❌ No code data provided in order.py. Please define 'order_data' and pass it to BracketOrderPlacer.")
                return
            data = self.code_data
        elif choice == "2":
            sheet_data = self.load_sheets()
            if not sheet_data:
                safe_print("❌ No trade data found in Google Sheet 'Trade' worksheet 'Trade plan'.")
                return
            if len(sheet_data) > 1:
                safe_print("━" * 60)
                for i, row in enumerate(sheet_data):
                    side = row.get('side', 'SELL').upper()
                    side_colored = "\033[92mBUY\033[0m" if side == "BUY" else "\033[91mSELL\033[0m"
                    safe_print(f"\nRow {i + 1}:   🏢 Exchange : {row.get('segment', 'NSE')} | {row.get('product_type', 'MIS')} | B/S: {side_colored}")
                    safe_print(f"\n         🪙  Symbol  : {row.get('symbol', 'N/A')} | Qty: {row.get('quantity', 1)} ")
                    safe_print(f"\n         📈 Entry   : ₹{row.get('entry_price', 0):.2f} ({row.get('entry_order_type', 'LIMIT')})")
                    safe_print(f"         🎯 Target  : ₹{row.get('target_price', 0):.2f}")
                    safe_print(f"         🛑 SL Type : {row.get('sl_type', 'SL-M')} | Trigger: ₹{row.get('stop_loss_trigger', 0):.2f}" +
                        (f" | Limit: ₹{row.get('stop_loss_limit', 0):.2f}" if row.get('sl_type', 'SL-M') == 'SL' else ""))
                    safe_print("━" * 60)
                row_idx = int(input("\n📋 Select Row to execute: ")) - 1
                if row_idx < 0 or row_idx >= len(sheet_data):
                    safe_print("❌ Invalid row index selected.")
                    return
                data = sheet_data[row_idx]
            elif len(sheet_data) == 1:
                data = sheet_data[0]
            else:
                safe_print("❌ No trade data found in Google Sheet 'Trade' worksheet 'Trade plan'.")
                return
        else:
            safe_print("❌ Invalid choice. Please select 1 or 2.")
            return


        missing_keys = [key for key in required_keys if key not in data or data[key] is None]
        if missing_keys:
            safe_print(f"❌ Missing or invalid required keys in data: {missing_keys}")
            return


        segment = data["segment"]
        product_type = data["product_type"]
        side = data["side"]
        entry_order_type = data["entry_order_type"]
        sl_type = data["sl_type"]
        symbol = data["symbol"]
        quantity = data["quantity"]
        entry_price = data["entry_price"]
        target_price = data["target_price"]
        stop_loss_trigger = data["stop_loss_trigger"]
        stop_loss_limit = data["stop_loss_limit"]


        self.kite = self.load_kite()
        exchange = self.kite.EXCHANGE_NFO if segment == "NFO" else self.kite.EXCHANGE_NSE
        product = self.kite.PRODUCT_NRML if product_type == "NRML" else self.kite.PRODUCT_MIS
        transaction_type = self.kite.TRANSACTION_TYPE_BUY if side == "BUY" else self.kite.TRANSACTION_TYPE_SELL
        exit_transaction_type = self.kite.TRANSACTION_TYPE_SELL if side == "BUY" else self.kite.TRANSACTION_TYPE_BUY


        if entry_order_type == "MARKET":
            order_type_enum = self.kite.ORDER_TYPE_MARKET
        elif entry_order_type == "LIMIT":
            order_type_enum = self.kite.ORDER_TYPE_LIMIT
        elif entry_order_type == "SL":
            order_type_enum = self.kite.ORDER_TYPE_SL
        elif entry_order_type == "SL-M":
            order_type_enum = self.kite.ORDER_TYPE_SLM
        else:
            safe_print("❌ Invalid entry order type.")
            return


        if product_type == "CNC" or segment == "NFO":
            leverage = 1
        else:
            leverage = 5


        if not use_amo:
            positions = self.kite.positions()["net"]
            for pos in positions:
                if pos["tradingsymbol"] == symbol and pos["exchange"] == exchange and pos["quantity"] != 0:
                    safe_print(f"❌ Existing open position in {symbol}. Qty = {pos['quantity']}")
                    return


        cash = self.kite.margins()["equity"]["available"]["cash"]
        required = (entry_price * quantity) / leverage
        safe_print(f"\n📋 Order Summary:")
        safe_print("━"*18 + "\n")
        safe_print(f"💰 Available: ₹{cash:.2f} | Required: ₹{required:.2f}")
        if cash < required:
            safe_print("❌ Not enough margin.")
            return


        capital_used = (entry_price * quantity) / leverage
        profit_amount = (target_price - entry_price) * quantity if side == "BUY" else (entry_price - target_price) * quantity
        loss_amount = (entry_price - stop_loss_trigger) * quantity if side == "BUY" else (stop_loss_trigger - entry_price) * quantity
        profit_pct = (profit_amount / capital_used) * 100
        loss_pct = (loss_amount / capital_used) * 100
        rr_ratio = round(profit_amount / loss_amount, 2) if loss_amount != 0 else "∞"


        side_colored = "\033[92mBUY\033[0m" if side.upper() == "BUY" else "\033[91mSELL\033[0m"
        safe_print(f"\n🏢 Exchange : {exchange} | MIS/CNC: {product_type} | B/S: {side_colored}")
        safe_print(f"\n🪙  Symbol : {symbol} | Qty: {quantity}")
        safe_print(f"📈 Entry  : ₹{entry_price} ({entry_order_type})")
        safe_print(f"🎯 Target : ₹{target_price}")
        safe_print(f"🛑 SL Type: {sl_type} | Trigger: ₹{stop_loss_trigger}" +
            (f" | Limit: ₹{stop_loss_limit}" if sl_type == "SL" else ""))
        safe_print(f"\n💰 Capital Used  : ₹{capital_used:.2f}")
        safe_print(f"📈 Target Profit : {Fore.GREEN} ₹{profit_amount:.2f} ({profit_pct:.2f}%) {Style.RESET_ALL}")
        safe_print(f"📉 Max Loss      : {Fore.RED} ₹{loss_amount:.2f} ({loss_pct:.2f}%) {Style.RESET_ALL}")
        safe_print(f"\n⚖️  Risk:Reward   : {rr_ratio} : 1")
        confirm = input("\n✅ Proceed with order? (Y/N): ").strip().upper()
        if confirm != "Y":
            safe_print("❌ Cancelled by user.")
            return


        entry_order = {
            "variety": self.kite.VARIETY_AMO if use_amo else self.kite.VARIETY_REGULAR,
            "exchange": exchange,
            "tradingsymbol": symbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "order_type": order_type_enum,
            "product": product
        }
        if entry_order_type in ["LIMIT", "SL"]:
            entry_order["price"] = entry_price
        if entry_order_type in ["SL", "SL-M"]:
            entry_order["trigger_price"] = stop_loss_trigger
        entry_id = self.kite.place_order(**entry_order)
        safe_print(f"\n✅ Entry order placed: {entry_id}")


        if use_amo:
            safe_print(f"⏳ {Fore.MAGENTA}AMO Entry order placed.{Style.RESET_ALL}")
            return


        safe_print("⌛ Waiting for entry fill...")
        retry_until_success(
            is_filled,
            self.kite,
            entry_id,
            interval=30,
            reconnect_func=lambda: (safe_print(f"\n🔌 Monitor error. Reconnecting..."), setattr(self, 'kite', self.load_kite())),
            periodic_msg="⌛ Reconnected, Waiting for entry fill..."
        )
        safe_print(f"\n✅ {Fore.MAGENTA}Entry Order filled!{Style.RESET_ALL}")


        target_id = self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange=exchange,
            tradingsymbol=symbol,
            transaction_type=exit_transaction_type,
            quantity=quantity,
            order_type=self.kite.ORDER_TYPE_LIMIT,
            price=target_price,
            product=product,
        )


        sl_order_type = self.kite.ORDER_TYPE_SL if sl_type == "SL" else self.kite.ORDER_TYPE_SLM
        sl_order = {
            "variety": self.kite.VARIETY_REGULAR,
            "exchange": exchange,
            "tradingsymbol": symbol,
            "transaction_type": exit_transaction_type,
            "quantity": quantity,
            "order_type": sl_order_type,
            "trigger_price": stop_loss_trigger,
            "product": product
        }
        if sl_type == "SL":
            sl_order["price"] = stop_loss_limit
        sl_id = self.kite.place_order(**sl_order)


        safe_print(f"\n🎯 Target placed: {target_id}")
        safe_print(f"🛑 Stop-loss placed: {sl_id} ({sl_type})")


        safe_print("\n📡 Monitoring SL/Target...")
        while True:
            try:
                if is_filled(self.kite, target_id):
                    safe_print(f"\n🎯🎯 {Fore.GREEN}Target Hit. Cancelling SL...{Style.RESET_ALL}")
                    cancel_order_safe(self.kite, sl_id)
                    break
                elif is_filled(self.kite, sl_id):
                    safe_print(f"\n🛑🛑 {Fore.RED}SL Hit. Cancelling Target...{Style.RESET_ALL}")
                    cancel_order_safe(self.kite, target_id)
                    break
            except Exception as e:
                safe_print(f"\n🔌 Monitor error. Reconnecting... {e}")
                self.kite = self.load_kite()
                safe_print("\n📡 Reconnected, Monitoring SL/Target...")
                time.sleep(30)


        safe_print("\n✅✅ Bracket order cycle completed ✅✅")
