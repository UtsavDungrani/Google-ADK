"""
MongoDB Database Connection & Collection Manager for Customer Care
Provides connection lifecycle, indexing, and unified collections access for:
- tickets (vendor support tickets & supervisor escalations)
- orders (customer purchases & courier tracking)
- rma_returns (return authorizations & prepaid labels)
- warranty_claims (hardware replacement claims)
- courtesy_credits (customer satisfaction vouchers)
"""

import os
import sys
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

logger = logging.getLogger("customer_care.db")

try:
    from pymongo import MongoClient, ASCENDING, errors
    from bson import ObjectId
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    logger.warning("pymongo is not installed. Running in fallback mode.")

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "customer_care_db")

_client: Optional[Any] = None
_db: Optional[Any] = None


def get_mongo_client() -> Optional[Any]:
    """Returns or initializes the singleton MongoClient instance."""
    global _client
    if not PYMONGO_AVAILABLE:
        return None

    if _client is None:
        try:
            _client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=2500,
                connectTimeoutMS=2500,
                socketTimeoutMS=5000,
                maxPoolSize=50
            )
            # Verify connection
            _client.admin.command("ping")
        except Exception as e:
            logger.warning(f"Could not connect to MongoDB at {MONGODB_URI}: {e}")
            _client = None
    return _client


def get_db() -> Optional[Any]:
    """Returns the customer care MongoDB database object."""
    global _db
    client = get_mongo_client()
    if client is not None:
        _db = client[MONGODB_DB_NAME]
        return _db
    return None


def is_mongo_connected() -> bool:
    """Checks if MongoDB is accessible and responsive."""
    try:
        client = get_mongo_client()
        if client is not None:
            client.admin.command("ping")
            return True
    except Exception:
        pass
    return False


def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Sanitizes MongoDB BSON document into JSON-serializable dict, converting ObjectId."""
    if doc is None:
        return None
    res = dict(doc)
    if "_id" in res:
        res["_id"] = str(res["_id"])
    return res


def serialize_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sanitizes a list of MongoDB documents."""
    return [serialize_doc(d) for d in docs if d is not None]


# -------------------------------------------------------------
# Collection Getters
# -------------------------------------------------------------

def get_tickets_collection() -> Optional[Any]:
    db = get_db()
    return db["tickets"] if db is not None else None


def get_orders_collection() -> Optional[Any]:
    db = get_db()
    return db["orders"] if db is not None else None


def get_rma_collection() -> Optional[Any]:
    db = get_db()
    return db["rma_returns"] if db is not None else None


def get_claims_collection() -> Optional[Any]:
    db = get_db()
    return db["warranty_claims"] if db is not None else None


def get_credits_collection() -> Optional[Any]:
    db = get_db()
    return db["courtesy_credits"] if db is not None else None


def get_chat_sessions_collection() -> Optional[Any]:
    db = get_db()
    return db["chat_sessions"] if db is not None else None


# -------------------------------------------------------------
# Seed Data Definitions
# -------------------------------------------------------------

SEED_ORDERS = [
    {
        "order_id": "ORD-10021",
        "customer_name": "Alex Mercer",
        "customer_id": "CUST-9921",
        "customer_email": "alex.mercer@example.com",
        "purchase_date": "2026-08-05",
        "delivery_date": "2026-08-08",
        "item_name": "UltraHD 65\" 4K Smart TV",
        "item_model": "UTV-65-4K-PRO",
        "serial_number": "SN-TV-98214-X",
        "item_price": 799.99,
        "tax_paid": 64.00,
        "total_amount": 863.99,
        "delivery_status": "Delivered",
        "carrier": "FedEx Freight",
        "tracking_number": "FDX-9921840291",
        "estimated_delivery": "2026-08-09",
        "warranty_period_years": 2,
        "rma_status": None
    },
    {
        "order_id": "ORD-10022",
        "customer_name": "Sarah Connor",
        "customer_id": "CUST-8812",
        "customer_email": "s.connor@example.com",
        "purchase_date": "2026-08-15",
        "delivery_date": "2026-08-18",
        "item_name": "ProSound ANC Wireless Headphones",
        "item_model": "PS-ANC-900",
        "serial_number": "SN-HP-44019-B",
        "item_price": 249.99,
        "tax_paid": 20.00,
        "total_amount": 269.99,
        "delivery_status": "Delivered",
        "carrier": "UPS Express",
        "tracking_number": "1Z9999999999999999",
        "estimated_delivery": "2026-08-19",
        "warranty_period_years": 2,
        "rma_status": None
    },
    {
        "order_id": "ORD-10023",
        "customer_name": "David Kim",
        "customer_id": "CUST-7741",
        "customer_email": "david.kim@example.com",
        "purchase_date": "2026-08-19",
        "delivery_date": None,
        "item_name": "BaristaPro Espresso Machine",
        "item_model": "BPE-15BAR",
        "serial_number": "SN-ESP-11983-Z",
        "item_price": 499.99,
        "tax_paid": 40.00,
        "total_amount": 539.99,
        "delivery_status": "Out for Delivery",
        "carrier": "DHL Express",
        "tracking_number": "DHL-7718290123",
        "estimated_delivery": "2026-08-22",
        "warranty_period_years": 2,
        "rma_status": None
    }
]

SEED_TICKETS = [
    {
        "ticket_id": "TCK-10021-VND",
        "customer_id": "CUST-9921",
        "customer_name": "Alex Mercer",
        "customer_email": "alex.mercer@example.com",
        "customer_phone": "+1-555-0199",
        "order_id": "ORD-10021",
        "product_name": "UltraHD 65\" 4K Smart TV",
        "category": "Vendor Engineering / Hardware Diagnostics",
        "subject": "Mainboard Wi-Fi Chipset Firmware Incompatibility",
        "description": "Customer experiencing repeated Wi-Fi drops on custom mesh network (Eero 6+). Standard TV-NET-502 manual troubleshooting exhausted.",
        "priority": "High",
        "status": "Vendor Responded",
        "created_at": "2026-08-24 09:15:00",
        "updated_at": "2026-08-24 16:40:00",
        "assigned_vendor": "LG/Samsung Panel & Smart TV Authorized Vendor Engineering",
        "estimated_sla": "Within 24-48 business hours",
        "vendor_response": "We have identified a known firmware compatibility issue with 160MHz Wi-Fi 6 mesh channels on v1.08 firmware. We have dispatched an Over-The-Air (OTA) hotfix patch (build v1.09-patch2) directly to serial SN-TV-98214-X. Please go to Settings > System > Software Update > Check Patch to apply.",
        "vendor_responded_at": "2026-08-24 16:40:00",
        "vendor_responder_name": "Marcus Vance (Senior Vendor Hardware Specialist)"
    },
    {
        "ticket_id": "TCK-10023-VND",
        "customer_id": "CUST-7741",
        "customer_name": "David Kim",
        "customer_email": "david.kim@example.com",
        "customer_phone": "+1-555-0144",
        "order_id": "ORD-10023",
        "product_name": "BaristaPro Espresso Machine",
        "category": "Third-Party Courier & Customs Clearance",
        "subject": "Customs inspection hold on imported portafilter accessory",
        "description": "Courier DHL tracking indicates customs inspection delay at regional distribution port.",
        "priority": "Medium",
        "status": "Pending Vendor Response",
        "created_at": "2026-08-25 08:30:00",
        "updated_at": "2026-08-25 08:30:00",
        "assigned_vendor": "BaristaPro Logistics & Customs Brokerage",
        "estimated_sla": "Within 24-48 business hours (as per vendor agent availability)",
        "vendor_response": None,
        "vendor_responded_at": None,
        "vendor_responder_name": None
    }
]


def init_db(force_reseed: bool = False) -> Dict[str, Any]:
    """Initializes collections, creates unique indexes, and seeds initial data."""
    if not is_mongo_connected():
        return {"status": "error", "message": "MongoDB is not reachable."}

    db = get_db()
    results = {}

    # 1. Tickets Collection
    tickets_col = db["tickets"]
    tickets_col.create_index([("ticket_id", ASCENDING)], unique=True)
    tickets_col.create_index([("customer_id", ASCENDING)])
    tickets_col.create_index([("order_id", ASCENDING)])
    tickets_col.create_index([("created_at", ASCENDING)])

    if force_reseed or tickets_col.count_documents({}) == 0:
        for t in SEED_TICKETS:
            tickets_col.update_one({"ticket_id": t["ticket_id"]}, {"$set": t}, upsert=True)
        results["tickets_seeded"] = len(SEED_TICKETS)
    else:
        results["tickets_count"] = tickets_col.count_documents({})

    # 2. Orders Collection
    orders_col = db["orders"]
    orders_col.create_index([("order_id", ASCENDING)], unique=True)
    orders_col.create_index([("customer_id", ASCENDING)])

    if force_reseed or orders_col.count_documents({}) == 0:
        for o in SEED_ORDERS:
            orders_col.update_one({"order_id": o["order_id"]}, {"$set": o}, upsert=True)
        results["orders_seeded"] = len(SEED_ORDERS)
    else:
        results["orders_count"] = orders_col.count_documents({})

    # 3. RMA Returns Collection
    rma_col = db["rma_returns"]
    rma_col.create_index([("rma_code", ASCENDING)], unique=True)
    rma_col.create_index([("order_id", ASCENDING)])

    # 4. Warranty Claims Collection
    claims_col = db["warranty_claims"]
    claims_col.create_index([("claim_id", ASCENDING)], unique=True)
    claims_col.create_index([("order_id", ASCENDING)])

    # 5. Courtesy Credits Collection
    credits_col = db["courtesy_credits"]
    credits_col.create_index([("voucher_code", ASCENDING)], unique=True)
    credits_col.create_index([("order_id", ASCENDING)])

    results["status"] = "success"
    results["database"] = MONGODB_DB_NAME
    return results


if __name__ == "__main__":
    print("Testing MongoDB Connection...")
    if is_mongo_connected():
        print(f"✅ Connected to MongoDB at {MONGODB_URI}")
        init_res = init_db()
        print("Initialization Results:", init_res)
    else:
        print(f"❌ Failed to connect to MongoDB at {MONGODB_URI}")
