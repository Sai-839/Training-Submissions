from typing import Dict, Any, Optional, List

Inventory = Dict[str, Dict[str, Dict[str, Any]]]
# structure:
# {
#   "<category>": {
#       "<sku>": {"name": str, "price": float, "qty": int}
#   }
# }

# ---------- Core helpers ----------
def ensure_category(inv: Inventory, category: str) -> None:
    if category not in inv:
        inv[category] = {}

def get_item(inv: Inventory, category: str, sku: str) -> Optional[Dict[str, Any]]:
    return inv.get(category, {}).get(sku)

# ---------- CRUD-style ops ----------
def add_item(inv: Inventory, category: str, sku: str, name: str, price: float, qty: int = 0) -> None:
    ensure_category(inv, category)
    if sku in inv[category]:
        raise ValueError(f"SKU '{sku}' already exists in '{category}'.")
    inv[category][sku] = {"name": name, "price": float(price), "qty": int(qty)}

def restock(inv: Inventory, category: str, sku: str, qty: int) -> None:
    item = get_item(inv, category, sku)
    if not item:
        raise KeyError(f"SKU '{sku}' not found in '{category}'.")
    if qty <= 0:
        raise ValueError("Restock qty must be greater than 0.")
    item["qty"] += qty

def sell(inv: Inventory, category: str, sku: str, qty: int) -> float:
    item = get_item(inv, category, sku)
    if not item:
        raise KeyError(f"SKU '{sku}' not found in '{category}'.")
    if qty <= 0:
        raise ValueError("Sell qty must be > 0.")
    if item["qty"] < qty:
        raise ValueError(f"Not enough stock: have {item['qty']}, need {qty}.")
    item["qty"] -= qty
    return round(qty * item["price"], 2)

def set_price(inv: Inventory, category: str, sku: str, price: float) -> None:
    item = get_item(inv, category, sku)
    if not item:
        raise KeyError(f"SKU '{sku}' not found in '{category}'.")
    if price < 0:
        raise ValueError("Price must be >= 0.")
    item["price"] = float(price)

# ---------- Queries / reports ----------
def list_items(inv: Inventory, category: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = []
    cats = [category] if category else inv.keys()
    for cat in cats:
        for sku, item in inv.get(cat, {}).items():
            rows.append({"category": cat, "sku": sku, **item})
    return rows

def inventory_value(inv: Inventory, category: Optional[str] = None) -> float:
    total = 0.0
    for row in list_items(inv, category):
        total += row["price"] * row["qty"]
    return round(total, 2)

def search(inv: Inventory, query: str) -> List[Dict[str, Any]]:
    q = query.lower()
    return [
        row for row in list_items(inv)
        if q in row["sku"].lower() or q in row["name"].lower() or q in row["category"].lower()
    ]

def remove_item(inv: Inventory, category: str, sku: str) -> None:
    if category in inv and sku in inv[category]:
        del inv[category][sku]
        if not inv[category]:
            del inv[category]
    else:
        raise KeyError(f"SKU '{sku}' not found in '{category}'.")

# ---------- Pretty output ----------
def print_table(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        print("(no items)")
        return
    cols = ["category", "sku", "name", "price", "qty"]
    widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}
    line = " | ".join(c.upper().ljust(widths[c]) for c in cols)
    print(line)
    print("-" * len(line))
    for r in rows:
        print(" | ".join(str(r[c]).ljust(widths[c]) for c in cols))

# ---------- Tiny CLI to play ----------
def demo_inventory() -> Inventory:
    inv: Inventory = {}
    add_item(inv, "Electronics", "LAP-001", "Laptop 14\"", 999.99, 5)
    add_item(inv, "Electronics", "HDP-002", "Headphones", 149.99, 12)
    add_item(inv, "Grocery", "APL-010", "Apples (1lb)", 3.49, 30)
    add_item(inv, "Grocery", "MLK-001", "Milk 1Gallon", 1.29, 20)
    return inv

def main():
    inv = demo_inventory()
    menu = """
Mini Inventory — choose an option:
 1) List all items
 2) List by category
 3) Add item
 4) Restock
 5) Sell
 6) Set price
 7) Search
 8) Total value (all/categories)
 9) Remove item
 0) Quit
> """
    while True:
        choice = input(menu).strip()
        try:
            if choice == "1":
                print_table(list_items(inv))
            elif choice == "2":
                cat = input("Category: ").strip()
                print_table(list_items(inv, cat))
            elif choice == "3":
                cat = input("Category: ").strip()
                sku = input("SKU: ").strip()
                name = input("Name: ").strip()
                price = float(input("Price: ").strip())
                qty = int(input("Qty: ").strip())
                add_item(inv, cat, sku, name, price, qty)
                print("Item added.")
            elif choice == "4":
                cat = input("Category: ").strip()
                sku = input("SKU: ").strip()
                qty = int(input("Add qty: ").strip())
                restock(inv, cat, sku, qty)
                print("Restocked.")
            elif choice == "5":
                cat = input("Category: ").strip()
                sku = input("SKU: ").strip()
                qty = int(input("Sell qty: ").strip())
                revenue = sell(inv, cat, sku, qty)
                print(f"Sold. Revenue: ${revenue}")
            elif choice == "6":
                cat = input("Category: ").strip()
                sku = input("SKU: ").strip()
                price = float(input("New price: ").strip())
                set_price(inv, cat, sku, price)
                print("Price updated.")
            elif choice == "7":
                q = input("Search (sku/name/category): ").strip()
                print_table(search(inv, q))
            elif choice == "8":
                cat = input("Leave blank for ALL or enter category: ").strip() or None
                print(f"Total value: ${inventory_value(inv, cat)}")
            elif choice == "9":
                cat = input("Category: ").strip()
                sku = input("SKU: ").strip()
                remove_item(inv, cat, sku)
                print("Item removed.")
            elif choice == "0":
                print("See You Soon....!")
                break
            else:
                print("Invalid choice.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
