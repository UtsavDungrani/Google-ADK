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


def get_faqs_collection() -> Optional[Any]:
    db = get_db()
    return db["faqs"] if db is not None else None


def get_knowledge_docs_collection() -> Optional[Any]:
    db = get_db()
    return db["knowledge_docs"] if db is not None else None


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


SEED_KNOWLEDGE_DOCS = [
    # Smart TV Manual
    {
        "doc_id": "KNOW-TV-001",
        "category": "Smart TV",
        "doc_title": "Smart TV User Manual & Diagnostics Guide",
        "heading": "Issue: Error Code TV-NET-502 (Cannot Connect to Wi-Fi)",
        "content": "Symptoms: Network setup failure, flashing red Wi-Fi indicator.\nTroubleshooting Steps:\n1. Power cycle the TV by unplugging power for 60 seconds.\n2. Hold down Remote Home + Back buttons for 5 seconds to initiate Bluetooth re-pairing.\n3. Navigate to Settings > Network > Forget Network and reconnect to your 2.4GHz/5GHz Wi-Fi network.\n4. If error persists, assign static DNS 8.8.8.8.",
        "tags": ["tv", "wifi", "network", "TV-NET-502", "error"],
        "status": "active"
    },
    {
        "doc_id": "KNOW-TV-002",
        "category": "Smart TV",
        "doc_title": "Smart TV User Manual & Diagnostics Guide",
        "heading": "Issue: No Sound or Delayed Audio via Soundbar / AV Receiver",
        "content": "Troubleshooting Steps:\n1. Ensure HDMI eARC / ARC cable is connected to HDMI Port 2 (eARC enabled).\n2. Navigate to Settings > Sound > Digital Audio Output and change setting from PCM to Auto / Pass-Through.\n3. Turn off TV and Soundbar, wait 30 seconds, then power on soundbar first.",
        "tags": ["tv", "audio", "soundbar", "earc", "delay"],
        "status": "active"
    },
    {
        "doc_id": "KNOW-TV-003",
        "category": "Smart TV",
        "doc_title": "Smart TV User Manual & Diagnostics Guide",
        "heading": "Display Flickering & Black Screen Calibration",
        "content": "Troubleshooting Steps:\n1. Disable Ambient Light Sensor and Eco Energy Saver under Picture Settings.\n2. Perform a Picture Test under Settings > Support > Self Diagnosis.\n3. If vertical/horizontal lines remain visible, request a hardware warranty panel replacement.",
        "tags": ["tv", "display", "flicker", "screen", "picture"],
        "status": "active"
    },
    {
        "doc_id": "KNOW-TV-004",
        "category": "Smart TV",
        "doc_title": "Smart TV User Manual & Diagnostics Guide",
        "heading": "Factory Reset Procedure",
        "content": "To restore TV to factory default settings:\n1. Navigate to Settings > General > Reset to Initial Settings.\n2. Enter default PIN (0000).\n3. Allow 3 minutes for system reboot.",
        "tags": ["tv", "reset", "factory", "pin"],
        "status": "active"
    },

    # Espresso Machine Manual
    {
        "doc_id": "KNOW-ESP-001",
        "category": "Espresso Machine",
        "doc_title": "BaristaPro Espresso Machine Manual",
        "heading": "First-Time Setup & Water Circuit Priming",
        "content": "Steps:\n1. Fill water reservoir with filtered water.\n2. Turn dial to Hot Water position for 20 seconds to purge air pockets from boiler.\n3. Attach portafilter without coffee grounds and run 2 single-shot flush cycles.",
        "tags": ["espresso", "setup", "priming", "water"],
        "status": "active"
    },
    {
        "doc_id": "KNOW-ESP-002",
        "category": "Espresso Machine",
        "doc_title": "BaristaPro Espresso Machine Manual",
        "heading": "Automatic Alert: Orange Scale Buildup Icon",
        "content": "Descaling Instructions:\n1. Mix 50% white vinegar or official descaling solution with 50% water in reservoir.\n2. Hold Brew + Steam buttons for 3 seconds to initiate Descaling Mode.\n3. Dispense full reservoir through steam wand and group head, then rinse with fresh water twice.",
        "tags": ["espresso", "descaling", "cleaning", "orange light", "scale"],
        "status": "active"
    },
    {
        "doc_id": "KNOW-ESP-003",
        "category": "Espresso Machine",
        "doc_title": "BaristaPro Espresso Machine Manual",
        "heading": "Low Extraction Pressure / Weak Crema Troubleshooting",
        "content": "Fixes:\n1. Ensure coffee grind size is set to Fine (Setting 2-4).\n2. Apply 30 lbs of firm tamping pressure.\n3. Ensure portafilter basket is not overfilled (18g for double shot).",
        "tags": ["espresso", "pressure", "crema", "grind"],
        "status": "active"
    },
    {
        "doc_id": "KNOW-ESP-004",
        "category": "Espresso Machine",
        "doc_title": "BaristaPro Espresso Machine Manual",
        "heading": "Grinder Jam & Bean Hopper Clearance",
        "content": "Fixes:\n1. Turn off power switch and remove bean hopper.\n2. Vacuum out residual unground beans from burr chamber.\n3. Rotate upper burr counterclockwise to unblock hard beans.",
        "tags": ["espresso", "grinder", "jam", "beans"],
        "status": "active"
    },

    # Headphones Manual
    {
        "doc_id": "KNOW-HP-001",
        "category": "Headphones",
        "doc_title": "ProSound ANC Headphones Manual",
        "heading": "Bluetooth Pairing & Dual Device Multipoint",
        "content": "Pairing Steps:\n1. Press and hold Power button for 5 seconds until LED blinks blue/red.\n2. Select PS-ANC-900 in your smartphone's Bluetooth settings.\n3. Multipoint: Pair Device 1, disconnect Bluetooth, pair Device 2, then reconnect Device 1.",
        "tags": ["headphones", "bluetooth", "pairing", "multipoint"],
        "status": "active"
    },
    {
        "doc_id": "KNOW-HP-002",
        "category": "Headphones",
        "doc_title": "ProSound ANC Headphones Manual",
        "heading": "Active Noise Cancellation (ANC) & Ambient Transparency Mode",
        "content": "Instructions:\n1. Tap left earcup ANC button to cycle: ANC High -> Transparency -> ANC Off.\n2. Transparency mode uses exterior microphones to pass ambient conversation.",
        "tags": ["headphones", "anc", "noise cancellation", "ambient"],
        "status": "active"
    },
    {
        "doc_id": "KNOW-HP-003",
        "category": "Headphones",
        "doc_title": "ProSound ANC Headphones Manual",
        "heading": "Audio Lag / Video Sync & Static Noise Fix",
        "content": "Fixes:\n1. Enable Low Latency Gaming/Media Mode in ProSound App.\n2. Disconnect and re-pair Bluetooth connection.\n3. Keep distance within 30 feet of source device.",
        "tags": ["headphones", "latency", "lag", "static"],
        "status": "active"
    },

    # Return & Warranty Policy
    {
        "doc_id": "KNOW-POL-001",
        "category": "Returns",
        "doc_title": "Official Return & Warranty Policy",
        "heading": "30-Day Hassle-Free Return Policy",
        "content": "Return Rules:\n- Customers may return eligible products within 30 days of delivery.\n- Items must be in original condition with included accessories and packaging.\n- We issue 100% full refunds with zero restocking fees.\n- Prepaid return shipping labels (FedEx/UPS) are provided instantly via chat.",
        "tags": ["returns", "policy", "30-day", "refund", "rma"],
        "status": "active"
    },
    {
        "doc_id": "KNOW-POL-002",
        "category": "Warranty",
        "doc_title": "Official Return & Warranty Policy",
        "heading": "1-Year Limited Manufacturer Warranty",
        "content": "Warranty Coverage:\n- Covers internal motherboard defects, heating element failures, power supply faults, and screen panel issues.\n- Excludes liquid damage, physical drops, and unauthorized disassembly.\n- Replacements are dispatched with free return shipping for defective hardware.",
        "tags": ["warranty", "coverage", "claims", "hardware"],
        "status": "active"
    },

    # Shipping & Health FAQs
    {
        "doc_id": "KNOW-FAQ-001",
        "category": "Shipping",
        "doc_title": "Store FAQ & Policy Guide",
        "heading": "Standard Shipping Options & Delivery Timelines",
        "content": "Shipping Tiers:\n- Standard Ground: 3-5 business days (Free over $50).\n- Expedited Express: 2 business days ($12.99).\n- Overnight Priority: 1 business day ($24.99).\nOrders before 2:00 PM EST ship same day.",
        "tags": ["shipping", "options", "timelines", "ground", "express"],
        "status": "active"
    },
    {
        "doc_id": "KNOW-FAQ-002",
        "category": "Health & Safety",
        "doc_title": "Store FAQ & Policy Guide",
        "heading": "Health Issues or Skin Irritation from Product Usage",
        "content": "Safety Protocol:\nDiscontinue use immediately and rinse affected area with water. Contact Customer Support with your Order ID for an immediate health report, prepaid return authorization, or courtesy credit.",
        "tags": ["health", "safety", "rashes", "skin", "allergy", "irritation"],
        "status": "active"
    }
]


def list_knowledge_chunks(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches knowledge docs and FAQs stored in MongoDB."""
    col = get_knowledge_docs_collection()
    if col is None:
        return []
    query = {"status": "active"}
    if category and category.lower() != "all":
        query["category"] = {"$regex": f"^{category}$", "$options": "i"}
    docs = list(col.find(query))
    return serialize_docs(docs)


def insert_knowledge_chunk(heading: str, content: str, category: str = "General Support", doc_title: str = "Store FAQ Guide", tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Inserts a new knowledge chunk/FAQ into MongoDB knowledge_docs collection."""
    col = get_knowledge_docs_collection()
    import datetime, uuid
    doc_id = f"KNOW-DB-{uuid.uuid4().hex[:6].upper()}"
    new_doc = {
        "doc_id": doc_id,
        "category": category,
        "doc_title": doc_title,
        "heading": heading,
        "content": content,
        "tags": tags or [],
        "status": "active",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if col is not None:
        col.insert_one(new_doc)
    return serialize_doc(new_doc)


def delete_knowledge_chunk(doc_id: str) -> bool:
    """Deletes a knowledge chunk from MongoDB by doc_id."""
    col = get_knowledge_docs_collection()
    if col is None:
        return False
    res = col.delete_one({"doc_id": doc_id})
    return res.deleted_count > 0


def list_faq_docs(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches FAQ documents stored in MongoDB."""
    col = get_faqs_collection()
    if col is None:
        return []
    query = {"status": "active"}
    if category and category.lower() != "all":
        query["category"] = {"$regex": f"^{category}$", "$options": "i"}
    docs = list(col.find(query))
    return serialize_docs(docs)


def insert_faq_doc(question: str, answer: str, category: str = "General Support", tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Inserts a new FAQ document into MongoDB."""
    # Also insert into knowledge_docs for unified search
    insert_knowledge_chunk(heading=question, content=answer, category=category, doc_title="Store FAQ Guide", tags=tags)
    
    col = get_faqs_collection()
    import datetime, uuid
    faq_id = f"FAQ-DB-{uuid.uuid4().hex[:6].upper()}"
    new_doc = {
        "faq_id": faq_id,
        "category": category,
        "question": question,
        "answer": answer,
        "tags": tags or [],
        "status": "active",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if col is not None:
        col.insert_one(new_doc)
    return serialize_doc(new_doc)


def delete_faq_doc(faq_id: str) -> bool:
    """Deletes an FAQ document from MongoDB by faq_id."""
    col = get_faqs_collection()
    if col is None:
        return False
    res = col.delete_one({"faq_id": faq_id})
    delete_knowledge_chunk(faq_id)
    return res.deleted_count > 0


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

    # 6. FAQs Collection
    faqs_col = db["faqs"]
    faqs_col.create_index([("faq_id", ASCENDING)], unique=True)
    faqs_col.create_index([("category", ASCENDING)])

    if force_reseed or faqs_col.count_documents({}) == 0:
        for f in SEED_KNOWLEDGE_DOCS:
            faq_item = {
                "faq_id": f["doc_id"],
                "category": f["category"],
                "question": f["heading"],
                "answer": f["content"],
                "tags": f.get("tags", []),
                "status": f.get("status", "active")
            }
            faqs_col.update_one({"faq_id": f["doc_id"]}, {"$set": faq_item}, upsert=True)
        results["faqs_seeded"] = len(SEED_KNOWLEDGE_DOCS)
    else:
        results["faqs_count"] = faqs_col.count_documents({})

    # 7. Knowledge Docs Collection (100% Pure MongoDB Knowledge Base)
    know_col = db["knowledge_docs"]
    know_col.create_index([("doc_id", ASCENDING)], unique=True)
    know_col.create_index([("category", ASCENDING)])

    if force_reseed or know_col.count_documents({}) == 0:
        for k in SEED_KNOWLEDGE_DOCS:
            know_col.update_one({"doc_id": k["doc_id"]}, {"$set": k}, upsert=True)
        results["knowledge_docs_seeded"] = len(SEED_KNOWLEDGE_DOCS)
    else:
        results["knowledge_docs_count"] = know_col.count_documents({})

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


