# pip install --upgrade kite-order

from kite_bracket_orders import BracketOrderPlacer, KiteDashboard, safe_print, login, pip_upgrade, pip_install

order_data = {
    "segment"               : "NSE"     ,           # "NSE" or "NFO"
    "product_type"          : "MIS"     ,           # "MIS" or "CNC" or "NRML"
    "side"                  : "BUY"    ,           # "BUY" or "SELL"
    "entry_order_type"      : "LIMIT"   ,           # "LIMIT" or "MARKET"
    "sl_type"               : "SL-M"    ,           # choose: "SL" or "SL-M"

    "symbol"                : "IDEA"    ,           # e.g. "IDEA", "RELIANCE", or "NIFTY24JUL20000CE"
    "quantity"              : 1         ,           # Must match lot size for options; 1+ for stocks
    "entry_price"           : 7.34      ,           # Only used if LIMIT order
    "target_price"          : 7.45      ,
    "stop_loss_trigger"     : 7.28      ,
    "stop_loss_limit"       : 7.27                  # only used if SL (not SL-M)
}

if __name__ == "__main__":
    # pip_install()  # Optional: Uncomment if you want to auto-install packages

    enable_logging = True  # True or False Enable/disable logging

    while True:
        safe_print("\n📊  Select an option:")
        safe_print("━" * 30)
        safe_print("1. 🔐  Kite Login")
        safe_print("2. 📈  Show Dashboard")
        safe_print("3. 🛒  Place Order")
        safe_print("4. 🛒  Entry Order track")
        safe_print("5. 🛒  SL/target Order track")
        safe_print("6. 🛠️   pip Upgrade")
        safe_print("7. ❌  Exit")


        choice = input("\n👉 Select an option (1-7): ")


        if choice == "1":
            login()
        elif choice == "2":
            dash = KiteDashboard()
            dash.show_all()
        elif choice == "3":
            placer = BracketOrderPlacer(code_data=order_data, enable_logging=enable_logging)
            placer.load_kite_login_name_show()
            placer.place_bracket_order()
        elif choice == "4":
            placer = BracketOrderPlacer(code_data=order_data, enable_logging=enable_logging)
            placer.load_kite_login_name_show()
            safe_print("\n📋 Enter Entry Order Details:")
            entry_order_id = input("🔢 Entry Order ID: ").strip()
            target_price = float(input("🎯 Target Price: "))
            stop_loss_trigger = float(input("🛑 Stop Loss Trigger Price: "))
            sl_type = input("🛑 Stop Loss Type (SL or SL-M): ").strip().upper()
            stop_loss_limit = float(input("🛑 Stop Loss Limit Price (if SL, else enter 0): ")) if sl_type == "SL" else 0
            placer.track_entry_order(entry_order_id, target_price, stop_loss_trigger, stop_loss_limit, sl_type)
        elif choice == "5":
            placer = BracketOrderPlacer(code_data=order_data, enable_logging=enable_logging)
            placer.load_kite_login_name_show()
            safe_print("\n📋 Enter SL/Target Order Details:")
            target_order_id = input("🎯 Target Order ID: ").strip()
            sl_order_id = input("🛑 Stop Loss Order ID: ").strip()
            placer.track_sl_target_orders(target_order_id, sl_order_id)
        elif choice == "6":
            pip_upgrade()
        elif choice == "7":
            safe_print("\n👋 Exiting... Have a profitable day!")
            break
        else:
            safe_print("❗ Invalid option. Please try again.")