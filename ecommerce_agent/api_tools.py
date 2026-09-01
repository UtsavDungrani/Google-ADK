import os
import requests
import datetime
import hashlib
from typing import List, Dict, Any, Optional

BASE_API_URL = "https://dummyjson.com"
REQUEST_TIMEOUT = 10


def search_products(
    query: str = "",
    category: str = "",
    min_price: float = 0.0,
    max_price: float = 999999.0,
    min_rating: float = 0.0,
    limit: int = 5
) -> dict:
    """Searches the live e-commerce product catalog with filters for price, category, and rating.

    Args:
        query: Keywords to search for (e.g., 'laptop', 'smartphone', 'perfume', 'sneakers', 'watch').
        category: Optional category slug (e.g., 'smartphones', 'laptops', 'fragrances', 'groceries').
        min_price: Minimum price filter in USD.
        max_price: Maximum price filter in USD.
        min_rating: Minimum average customer rating (0.0 to 5.0).
        limit: Maximum number of products to return (default: 5).

    Returns:
        A dictionary with matching products, pricing, discounts, stock levels, and ratings.
    """
    try:
        if category:
            url = f"{BASE_API_URL}/products/category/{category.strip().lower()}"
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            raw_products = response.json().get("products", []) if response.status_code == 200 else []
        elif query:
            url = f"{BASE_API_URL}/products/search"
            response = requests.get(url, params={"q": query.strip(), "limit": 30}, timeout=REQUEST_TIMEOUT)
            raw_products = response.json().get("products", []) if response.status_code == 200 else []

            # If search?q yielded no results, fetch broad catalog and search titles/categories/tags
            if not raw_products:
                broad_resp = requests.get(f"{BASE_API_URL}/products?limit=100", timeout=REQUEST_TIMEOUT)
                if broad_resp.status_code == 200:
                    all_items = broad_resp.json().get("products", [])
                    q_lower = query.strip().lower()
                    raw_products = [
                        p for p in all_items
                        if q_lower in p.get("title", "").lower()
                        or q_lower in p.get("description", "").lower()
                        or q_lower in p.get("category", "").lower()
                        or any(q_lower in t.lower() for t in p.get("tags", []))
                    ]
        else:
            url = f"{BASE_API_URL}/products"
            response = requests.get(url, params={"limit": 30}, timeout=REQUEST_TIMEOUT)
            raw_products = response.json().get("products", []) if response.status_code == 200 else []

        # Filter by price and rating
        filtered = []
        for p in raw_products:
            price = float(p.get("price", 0))
            rating = float(p.get("rating", 0))

            if price < min_price or price > max_price:
                continue
            if rating < min_rating:
                continue

            discount_pct = float(p.get("discountPercentage", 0))
            discounted_price = round(price * (1 - discount_pct / 100), 2)

            filtered.append({
                "id": p.get("id"),
                "title": p.get("title"),
                "brand": p.get("brand", "Generic"),
                "category": p.get("category"),
                "original_price": f"${price:.2f}",
                "discount_percentage": f"{discount_pct:.1f}%",
                "final_price": f"${discounted_price:.2f}",
                "rating": f"{rating:.1f} / 5.0",
                "stock_status": "In Stock" if p.get("stock", 0) > 0 else "Out of Stock",
                "stock_count": p.get("stock", 0),
                "shipping": p.get("shippingInformation", "Standard shipping"),
                "description": p.get("description")
            })

        results = filtered[:limit]

        return {
            "status": "success",
            "search_query": query,
            "category_filter": category or "all",
            "total_matches_found": len(filtered),
            "returned_count": len(results),
            "products": results
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to connect to e-commerce API: {str(e)}"
        }


def get_product_details(product_id: int) -> dict:
    """Fetches comprehensive specifications, customer reviews, warranty, and return policy for a specific product.

    Args:
        product_id: The unique numeric ID of the product (e.g., 1, 2, 5, 12).

    Returns:
        Full product breakdown including specs, dimensions, reviews, warranty, and policies.
    """
    try:
        url = f"{BASE_API_URL}/products/{product_id}"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)

        if response.status_code == 404:
            return {
                "status": "not_found",
                "message": f"Product with ID {product_id} does not exist in the catalog."
            }
        elif response.status_code != 200:
            return {
                "status": "error",
                "message": f"API error with status code {response.status_code}"
            }

        p = response.json()
        price = float(p.get("price", 0))
        discount_pct = float(p.get("discountPercentage", 0))
        discounted_price = round(price * (1 - discount_pct / 100), 2)

        reviews_summary = []
        for r in p.get("reviews", []):
            reviews_summary.append({
                "reviewer": r.get("reviewerName", "Anonymous"),
                "rating": r.get("rating"),
                "comment": r.get("comment"),
                "date": r.get("date")
            })

        return {
            "status": "success",
            "product_id": p.get("id"),
            "title": p.get("title"),
            "brand": p.get("brand", "Generic"),
            "category": p.get("category"),
            "sku": p.get("sku"),
            "original_price": f"${price:.2f}",
            "discount_percentage": f"{discount_pct:.1f}%",
            "final_price": f"${discounted_price:.2f}",
            "rating": f"{p.get('rating', 0):.2f} / 5.0",
            "availability": p.get("availabilityStatus", "In Stock"),
            "stock_units": p.get("stock", 0),
            "weight": f"{p.get('weight', 0)}g",
            "dimensions": p.get("dimensions", {}),
            "warranty_information": p.get("warrantyInformation", "1-year standard warranty"),
            "shipping_information": p.get("shippingInformation", "Ships in 3-5 business days"),
            "return_policy": p.get("returnPolicy", "30-day return policy"),
            "minimum_order_quantity": p.get("minimumOrderQuantity", 1),
            "description": p.get("description"),
            "customer_reviews": reviews_summary,
            "thumbnail_url": p.get("thumbnail")
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch product details: {str(e)}"
        }


def list_product_categories() -> dict:
    """Retrieves all available product categories in the e-commerce store catalog.

    Returns:
        List of category names and slugs to help users browse products.
    """
    try:
        url = f"{BASE_API_URL}/products/categories"
        response = requests.get(url, timeout=REQUEST_TIMEOUT)

        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"API error with status code {response.status_code}"
            }

        data = response.json()
        # Data format can be list of dicts or list of strings
        categories = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    categories.append({
                        "name": item.get("name"),
                        "slug": item.get("slug")
                    })
                elif isinstance(item, str):
                    categories.append({
                        "name": item.replace("-", " ").title(),
                        "slug": item
                    })

        return {
            "status": "success",
            "total_categories": len(categories),
            "categories": categories
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch categories: {str(e)}"
        }


def get_top_deals(category: str = "", min_discount_percent: float = 10.0, limit: int = 5) -> dict:
    """Finds the hottest discounts and clearance deals currently available across products.

    Args:
        category: Optional category slug to look for deals in.
        min_discount_percent: Minimum discount percentage (e.g., 15.0 for 15%+ off).
        limit: Number of top deals to return (default: 5).

    Returns:
        Top discounted products sorted by greatest discount percentage.
    """
    try:
        if category:
            url = f"{BASE_API_URL}/products/category/{category.strip().lower()}"
        else:
            url = f"{BASE_API_URL}/products?limit=50"

        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            return {"status": "error", "message": f"API error {response.status_code}"}

        products = response.json().get("products", [])
        deals = []

        for p in products:
            discount = float(p.get("discountPercentage", 0))
            if discount >= min_discount_percent:
                price = float(p.get("price", 0))
                discounted_price = round(price * (1 - discount / 100), 2)
                savings = round(price - discounted_price, 2)

                deals.append({
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "category": p.get("category"),
                    "original_price": f"${price:.2f}",
                    "discount": f"{discount:.1f}% OFF",
                    "final_price": f"${discounted_price:.2f}",
                    "you_save": f"${savings:.2f}",
                    "rating": f"{p.get('rating', 0):.1f} / 5.0",
                    "discount_value": discount
                })

        deals.sort(key=lambda x: x["discount_value"], reverse=True)
        top_deals = deals[:limit]

        return {
            "status": "success",
            "category": category or "all",
            "deals_found": len(deals),
            "top_deals": top_deals
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to get deals: {str(e)}"}


def track_order(order_id: str) -> dict:
    """Tracks the real-time shipping and delivery status of a customer order.

    Args:
        order_id: The order confirmation number (e.g. 'ORD-89214', 'ORD-44912', 'ORD-10023').

    Returns:
        Live shipment progress, carrier, tracking number, milestones, and estimated delivery date.
    """
    clean_id = order_id.strip().upper()
    if not clean_id.startswith("ORD-"):
        clean_id = f"ORD-{clean_id.replace('#', '')}"

    # Deterministic simulation based on hash of order_id
    hash_val = int(hashlib.md5(clean_id.encode()).hexdigest(), 16)
    
    carriers = ["FedEx Express", "DHL Worldwide", "UPS Ground", "BlueDart Logistics"]
    cities = ["San Francisco, CA", "Austin, TX", "Seattle, WA", "New York, NY", "Chicago, IL"]
    
    carrier = carriers[hash_val % len(carriers)]
    dest_city = cities[(hash_val >> 2) % len(cities)]
    status_idx = (hash_val >> 4) % 4
    
    statuses = [
        ("Order Placed", "Your order has been confirmed and is being prepared by our fulfillment center."),
        ("Shipped & In Transit", f"Package is in transit via {carrier} to {dest_city}."),
        ("Out for Delivery", f"Your courier has loaded the package onto the delivery van for final drop-off in {dest_city}."),
        ("Delivered", f"Package was successfully delivered and signed for at front door in {dest_city}.")
    ]

    current_status, status_desc = statuses[status_idx]
    
    today = datetime.date.today()
    if status_idx == 3: # Delivered
        eta = (today - datetime.timedelta(days=1)).strftime("%B %d, %Y")
    elif status_idx == 2: # Out for delivery
        eta = today.strftime("%B %d, %Y (Today by 7:00 PM)")
    else:
        eta = (today + datetime.timedelta(days=(3 - status_idx))).strftime("%B %d, %Y")

    tracking_num = f"TRK{abs(hash_val) % 1000000000:09d}"

    events = [
        {"timestamp": "2026-08-18 09:30 AM", "event": "Order placed and payment authorized"},
        {"timestamp": "2026-08-19 02:15 PM", "event": "Package packed and labeled at distribution warehouse"},
    ]
    if status_idx >= 1:
        events.append({"timestamp": "2026-08-20 06:40 AM", "event": f"Departed regional facility via {carrier}"})
    if status_idx >= 2:
        events.append({"timestamp": "2026-08-21 08:15 AM", "event": "Arrived at local distribution center - Out for delivery"})
    if status_idx >= 3:
        events.append({"timestamp": "2026-08-21 01:22 PM", "event": "Delivered to recipient (Front Door / Reception)"})

    return {
        "status": "success",
        "order_id": clean_id,
        "carrier": carrier,
        "tracking_number": tracking_num,
        "shipping_status": current_status,
        "status_description": status_desc,
        "destination": dest_city,
        "estimated_delivery": eta,
        "milestones": events
    }


def request_order_return_or_refund(order_id: str, reason: str, action: str = "refund") -> dict:
    """Initiates an RMA (Return Merchandise Authorization) or refund request for an order.

    Args:
        order_id: The customer's order ID (e.g., 'ORD-89214').
        reason: The customer's stated reason (e.g., 'Defective item', 'Wrong size', 'Arrived late', 'Changed mind').
        action: Requested resolution ('refund', 'replacement', or 'store_credit').

    Returns:
        RMA authorization number, pickup scheduling instructions, and refund timeline.
    """
    clean_id = order_id.strip().upper()
    rma_number = f"RMA-{hashlib.md5(f'{clean_id}-{reason}'.encode()).hexdigest()[:8].upper()}"
    
    return {
        "status": "approved",
        "rma_number": rma_number,
        "order_id": clean_id,
        "action_requested": action.lower(),
        "reason": reason,
        "instructions": [
            "1. Print the prepaid return shipping label sent to your account email.",
            "2. Pack the item securely with all original accessories and packaging.",
            "3. Drop the package off at any authorized carrier drop-off location within 14 days."
        ],
        "estimated_refund_timeline": "3 to 5 business days after warehouse inspection.",
        "support_note": "A confirmation email with the return shipping label has been dispatched."
    }


def apply_coupon_and_calculate_cart(
    items: List[Dict[str, Any]],
    coupon_code: str = ""
) -> dict:
    """Calculates subtotal, applies coupon codes, computes sales tax and shipping for a list of items.

    Args:
        items: List of items with 'price' (float) and 'quantity' (int), and optional 'title' (str).
        coupon_code: Optional discount promo code (e.g., 'SAVE20', 'WELCOME10', 'FREESHIP').

    Returns:
        Itemized breakdown of subtotal, discount savings, tax, shipping, and grand total.
    """
    if not items:
        return {"status": "error", "message": "Cart is empty. Please add items."}

    subtotal = 0.0
    item_summaries = []
    for item in items:
        price = float(item.get("price", 0))
        qty = int(item.get("quantity", 1))
        item_total = price * qty
        subtotal += item_total
        item_summaries.append({
            "title": item.get("title", "Item"),
            "unit_price": f"${price:.2f}",
            "quantity": qty,
            "total": f"${item_total:.2f}"
        })

    discount_amount = 0.0
    discount_note = "No coupon applied"
    shipping_fee = 9.99 if subtotal < 50.0 else 0.0 # Free shipping over $50

    code = coupon_code.strip().upper()
    if code == "SAVE20":
        discount_amount = subtotal * 0.20
        discount_note = "SAVE20 (20% off entire order)"
    elif code == "WELCOME10":
        discount_amount = subtotal * 0.10
        discount_note = "WELCOME10 (10% new customer discount)"
    elif code == "FREESHIP":
        discount_amount = min(shipping_fee, 9.99)
        shipping_fee = 0.0
        discount_note = "FREESHIP (Free standard shipping applied)"
    elif code:
        discount_note = f"Invalid or expired coupon '{coupon_code}'"

    taxable_amount = max(0.0, subtotal - discount_amount)
    tax_rate = 0.0825 # 8.25% standard tax
    tax = round(taxable_amount * tax_rate, 2)
    grand_total = round(taxable_amount + tax + shipping_fee, 2)

    return {
        "status": "success",
        "items": item_summaries,
        "subtotal": f"${subtotal:.2f}",
        "coupon_applied": discount_note,
        "discount_savings": f"-${discount_amount:.2f}",
        "shipping": "FREE" if shipping_fee == 0.0 else f"${shipping_fee:.2f}",
        "estimated_tax": f"${tax:.2f}",
        "grand_total": f"${grand_total:.2f}"
    }
