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


def get_profiles_collection() -> Optional[Any]:
    db = get_db()
    return db["customer_profiles"] if db is not None else None


def get_episodes_collection() -> Optional[Any]:
    db = get_db()
    return db["customer_episodes"] if db is not None else None


def get_exemplars_collection() -> Optional[Any]:
    db = get_db()
    return db["gold_exemplars"] if db is not None else None


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

# -------------------------------------------------------------
# Cross-Session Long-Term Memory Seed Data
# -------------------------------------------------------------

SEED_PROFILES = [
    {
        "customer_id": "CUST-9921",
        "customer_name": "Alex Mercer",
        "customer_email": "alex.mercer@example.com",
        "customer_phone": "+1-555-0199",
        "preferred_tone": "Technical & Concise",
        "preferred_language": "English",
        "churn_risk": 0.35,
        "churn_risk_level": "Medium Risk",
        "total_credits_issued": 0.0,
        "owned_devices": [
            {
                "order_id": "ORD-10021",
                "item_name": "UltraHD 65\" 4K Smart TV",
                "item_model": "UTV-65-4K-PRO",
                "serial_number": "SN-TV-98214-X",
                "purchase_date": "2026-08-05",
                "delivery_date": "2026-08-08"
            }
        ],
        "active_tickets": ["TCK-10021-VND"],
        "persistent_notes": [
            "Uses Eero 6+ Wi-Fi mesh network with 160MHz channels",
            "Prefers step-by-step firmware debugging instructions before hardware RMA",
            "Reported error TV-NET-502 resolved via vendor OTA patch build v1.09-patch2"
        ],
        "last_interaction_at": "2026-08-24 16:40:00"
    },
    {
        "customer_id": "CUST-8812",
        "customer_name": "Sarah Connor",
        "customer_email": "s.connor@example.com",
        "customer_phone": "+1-555-0188",
        "preferred_tone": "Polite & Direct",
        "preferred_language": "English",
        "churn_risk": 0.12,
        "churn_risk_level": "Low Risk",
        "total_credits_issued": 0.0,
        "owned_devices": [
            {
                "order_id": "ORD-10022",
                "item_name": "ProSound ANC Wireless Headphones",
                "item_model": "PS-ANC-900",
                "serial_number": "SN-HP-44019-B",
                "purchase_date": "2026-08-15",
                "delivery_date": "2026-08-18"
            }
        ],
        "active_tickets": [],
        "persistent_notes": [
            "Regularly pairs headphones via Bluetooth Multipoint between iPhone 15 and MacBook Pro",
            "Inquired about 30-day return policy; within eligible return window until Sep 17, 2026"
        ],
        "last_interaction_at": "2026-08-19 14:20:00"
    },
    {
        "customer_id": "CUST-7741",
        "customer_name": "David Kim",
        "customer_email": "david.kim@example.com",
        "customer_phone": "+1-555-0144",
        "preferred_tone": "Empathetic & Detailed",
        "preferred_language": "English",
        "churn_risk": 0.72,
        "churn_risk_level": "High Risk",
        "total_credits_issued": 25.0,
        "owned_devices": [
            {
                "order_id": "ORD-10023",
                "item_name": "BaristaPro Espresso Machine",
                "item_model": "BPE-15BAR",
                "serial_number": "SN-ESP-11983-Z",
                "purchase_date": "2026-08-19",
                "delivery_date": None
            }
        ],
        "active_tickets": ["TCK-10023-VND"],
        "persistent_notes": [
            "Order delayed due to regional DHL customs port inspection hold",
            "Customer was highly frustrated by delivery lag; granted $25 courtesy store credit voucher",
            "Awaiting DHL customs clearance release update under vendor ticket TCK-10023-VND"
        ],
        "last_interaction_at": "2026-08-25 08:30:00"
    }
]

SEED_EPISODES = [
    {
        "episode_id": "EPS-9921-01",
        "customer_id": "CUST-9921",
        "session_id": "sess_alex_01",
        "timestamp": "2026-08-24 09:15:00",
        "summary": "Alex reported recurring Wi-Fi disconnects and TV-NET-502 error on UltraHD 65\" TV. Unplugging and DNS 8.8.8.8 failed. Vendor ticket TCK-10021-VND opened with authorized hardware engineering.",
        "topics": ["Wi-Fi Disconnect", "Error TV-NET-502", "Ticket Creation"],
        "sentiment_at_conclusion": "Frustrated but appreciative of quick ticket SLA",
        "resolved": False
    },
    {
        "episode_id": "EPS-9921-02",
        "customer_id": "CUST-9921",
        "session_id": "sess_alex_02",
        "timestamp": "2026-08-24 16:40:00",
        "summary": "Vendor Senior Hardware Specialist Marcus Vance responded to ticket TCK-10021-VND with OTA firmware patch (build v1.09-patch2) for 160MHz mesh channel compatibility. Alex was instructed to apply via TV settings.",
        "topics": ["Ticket Resolution", "OTA Patch", "Firmware v1.09"],
        "sentiment_at_conclusion": "Relieved / Satisfied",
        "resolved": True
    },
    {
        "episode_id": "EPS-8812-01",
        "customer_id": "CUST-8812",
        "session_id": "sess_sarah_01",
        "timestamp": "2026-08-19 14:20:00",
        "summary": "Sarah checked Bluetooth dual-device multipoint pairing for ProSound ANC Headphones. Successfully paired both laptop and phone simultaneously. Also inquired about 30-day return policy guarantee.",
        "topics": ["Bluetooth Multipoint", "Headphone Setup", "Return Window"],
        "sentiment_at_conclusion": "Satisfied / Confident",
        "resolved": True
    },
    {
        "episode_id": "EPS-7741-01",
        "customer_id": "CUST-7741",
        "session_id": "sess_david_01",
        "timestamp": "2026-08-25 08:30:00",
        "summary": "David inquired about delayed BaristaPro Espresso Machine (ORD-10023). Tracking indicated customs inspection hold. Escalation agent provided $25 courtesy credit and filed vendor ticket TCK-10023-VND with customs brokerage.",
        "topics": ["Shipping Delay", "Customs Hold", "Courtesy Credit $25", "Ticket TCK-10023-VND"],
        "sentiment_at_conclusion": "Mollified after courtesy credit and direct ticket opening",
        "resolved": False
    }
]

# -------------------------------------------------------------
# Dynamic Few-Shot Gold-Standard Exemplars
# Curated high-performance human resolutions for in-context learning
# -------------------------------------------------------------

SEED_EXEMPLARS = [
    {
        "exemplar_id": "EXEMP-RET-01",
        "title": "30-Day Return Grace Period Exception",
        "category": "Returns & Warranty",
        "situation": "Customer requests return on day 32 (2 days past standard 30-day window) due to hospitalization or extenuating hardship.",
        "customer_inquiry": "I was hospitalized for a week and missed the 30-day return cutoff for my UltraHD TV (order ORD-10021). Can I please still return it for a refund?",
        "expert_thought": "Customer is only 2 days outside the standard 30-day window with extenuating medical hardship. Policy allows Tier-2 supervisor 48-72h grace waivers with zero restocking fees. Express high empathy, grant the exception, generate prepaid FedEx RMA, and state clear refund timeline.",
        "expert_response": (
            "I am so sorry to hear that you were hospitalized, and I truly hope you are recovering well. "
            "While our standard return window is 30 days, we gladly authorize a **Medical Grace Exception** for you today with a 100% full refund and **zero restocking fees**.\n\n"
            "Here are your return details:\n"
            "• **RMA Authorization Code**: `RMA-GRACE-9921`\n"
            "• **Prepaid Return Label**: Dispatched to your email via FedEx Freight.\n"
            "• **Refund Timeline**: Full amount of $863.99 will be credited to your original payment method within 3-5 business days of carrier drop-off.\n\n"
            "Please prioritize your recovery, and let us know if you need any assistance scheduling a carrier pickup!"
        ),
        "policy_citation": "*Source: Official Store Policy - Section 4.2 Grace Waivers*",
        "tags": ["return", "rma", "grace period", "exception", "medical", "hospital", "refund", "tv"]
    },
    {
        "exemplar_id": "EXEMP-DIAG-01",
        "title": "Wi-Fi Mesh Handshake & Error TV-NET-502 Diagnostics",
        "category": "Product Diagnostics",
        "situation": "Smart TV shows error TV-NET-502 on Wi-Fi 6 mesh network with frequent drops.",
        "customer_inquiry": "My 65 inch TV shows error code TV-NET-502 and keeps dropping from my Eero Wi-Fi mesh network. I restarted my router and it still won't connect.",
        "expert_thought": "Error TV-NET-502 indicates a 160MHz channel handshake timeout on Wi-Fi 6 mesh networks. Provide structured numbered manual steps: discharge TV capacitors for 60s, separate or split 2.4/5GHz SSID bands, assign Google static DNS 8.8.8.8, and advise checking for OTA patch build v1.09.",
        "expert_response": (
            "Error code **TV-NET-502** indicates a known channel handshake timeout that commonly occurs with 160MHz channels on Wi-Fi 6 mesh systems (like Eero 6+). "
            "Please follow these exact diagnostic steps from our hardware engineering manual:\n\n"
            "1. **Capacitance Discharge**: Unplug the TV's power cord from the wall for a full **60 seconds** (this clears the Wi-Fi card's volatile memory cache).\n"
            "2. **Bluetooth Remote Re-pair**: Hold down `Home` + `Back` buttons on your remote for 5 seconds until the pairing LED blinks.\n"
            "3. **Forget & Reconnect**: Navigate to `Settings` > `Network` > `Forget Network`, then reconnect specifically to your 2.4GHz or 5GHz band.\n"
            "4. **Static DNS Override**: Set DNS from Auto to Manual and input **`8.8.8.8`** (Primary) and **`8.8.4.4`** (Secondary).\n"
            "5. **Check Firmware**: Go to `Settings` > `System` > `Software Update` > `Check Patch` to apply Over-The-Air hotfix build **v1.09-patch2**.\n\n"
            "If your Wi-Fi still disconnects after step 5, let me know and I will immediately dispatch a vendor engineering replacement panel under your 2-year warranty!"
        ),
        "policy_citation": "*Source: Smart TV User Manual & Hardware Diagnostics Guide (Doc: KNOW-TV-001)*",
        "tags": ["wifi", "mesh", "tv-net-502", "error", "tv", "dns", "firmware", "diagnostics"]
    },
    {
        "exemplar_id": "EXEMP-ESC-01",
        "title": "Severe Courier Delay & Customer Frustration De-Escalation",
        "category": "Escalations & Courtesy Credits",
        "situation": "Customer is furious that high-value purchase is delayed by 4+ days with no tracking updates.",
        "customer_inquiry": "My order ORD-10023 was supposed to arrive 4 days ago! This is ridiculous and unacceptable service, I needed this machine for an event this weekend!",
        "expert_thought": "Customer frustration velocity is extremely high (churn risk > 0.7). Do not give robotic tracking status or defensive excuses. Apologize sincerely with deep empathy, acknowledge the unacceptable 4-day delay, immediately issue a $25-$50 courtesy credit voucher, open a direct courier priority investigation, and provide personal accountability.",
        "expert_response": (
            "I completely understand your frustration, and you are 100% right—a 4-day delay without clear communication is unacceptable, especially when you were relying on your machine for a weekend event. I sincerely apologize for this experience.\n\n"
            "I am taking immediate action to make this right:\n"
            "1. **Instant Courtesy Credit**: I have credited **$25.00** directly to your customer wallet (`CARE-CREDIT-7741`), usable immediately with no expiration.\n"
            "2. **Carrier Escalation Ticket**: I have opened priority case **`TCK-10023-VND`** directly with DHL customs logistics management to force-release your package from inspection.\n"
            "3. **Personal Monitoring**: I am actively tracking your shipment checkpoints and will notify you as soon as the package enters the final delivery van.\n\n"
            "If the courier cannot guarantee delivery within 24 hours, I will gladly offer you a 100% full refund or arrange an expedited overnight replacement."
        ),
        "policy_citation": "*Source: Customer Care Executive Escalation Guidelines (Section 3: Goodwill Credits)*",
        "tags": ["delay", "frustration", "courtesy credit", "voucher", "apology", "churn", "shipping", "dhl"]
    },
    {
        "exemplar_id": "EXEMP-CLM-01",
        "title": "2-Year Hardware Warranty Replacement for Screen Artifacts",
        "category": "Returns & Warranty",
        "situation": "TV displays black horizontal lines after 10 days of normal usage.",
        "customer_inquiry": "My TV from order ORD-10021 has black horizontal lines running across the bottom half of the screen. It was never dropped. Can I get this replaced under warranty?",
        "expert_thought": "Defect involves display panel horizontal lines without physical damage, covered under the 2-Year Manufacturer Hardware Warranty. Guide picture self-test, verify 2-year warranty validity, approve replacement claim CLM-TV-98214 with 24-hour express dispatch, and arrange carrier pickup for defective unit.",
        "expert_response": (
            "Thank you for reaching out, and I am sorry to hear about the display artifacts on your 65\" Smart TV. Horizontal lines indicate an internal T-Con board or display panel matrix defect, which is **100% covered under your 2-Year Manufacturer Warranty**.\n\n"
            "I have officially authorized your warranty replacement claim:\n"
            "• **Claim Number**: `CLM-TV-98214`\n"
            "• **Coverage Status**: Verified Active (24 months total coverage, expires August 8, 2028).\n"
            "• **Replacement Unit**: A brand new **UltraHD 65\" 4K Smart TV (UTV-65-4K-PRO)** is being prepared for 24-hour express courier dispatch.\n"
            "• **Defective Unit Pickup**: The courier will bring the replacement box and collect your defective unit with a prepaid label—no packaging hassle for you.\n\n"
            "You will receive live tracking information via SMS and email as soon as the replacement leaves the fulfillment center!"
        ),
        "policy_citation": "*Source: Official Return & Warranty Policy - Section 2.1 Hardware Panel Coverage*",
        "tags": ["warranty", "claim", "replacement", "tv", "screen", "lines", "hardware defect", "panel"]
    },
    {
        "exemplar_id": "EXEMP-HP-01",
        "title": "ProSound ANC Headphones Dual-Device Multipoint Setup",
        "category": "Product Diagnostics",
        "situation": "Customer struggling to connect Bluetooth headphones to both work laptop and personal smartphone simultaneously.",
        "customer_inquiry": "How do I pair my ProSound headphones to both my MacBook and my iPhone at the same time? When I connect to one, the other disconnects.",
        "expert_thought": "Bluetooth multipoint requires pairing device 1, temporarily disabling Bluetooth on device 1, pairing device 2, and then re-enabling device 1. Explain clear sequence and mention automatic audio priority switching.",
        "expert_response": (
            "Your ProSound ANC Wireless Headphones support **Dual-Device Multipoint Bluetooth**, which allows you to take phone calls on your iPhone while listening to audio or video on your MacBook. "
            "To set up multipoint pairing seamlessly, please follow this exact order:\n\n"
            "1. **Enter Pairing Mode**: Power off the headphones, then press and hold the Power button for **5 seconds** until the LED blinks alternating Red and Blue.\n"
            "2. **Pair Device 1 (iPhone)**: Open Bluetooth Settings on your phone and tap **`PS-ANC-900`** to connect.\n"
            "3. **Disconnect Temporarily**: Turn off Bluetooth on your iPhone momentarily.\n"
            "4. **Pair Device 2 (MacBook)**: Re-enter pairing mode on the headphones (hold Power for 5s), open MacBook Bluetooth settings, and select **`PS-ANC-900`**.\n"
            "5. **Re-Enable Device 1**: Turn Bluetooth back on your iPhone. Both devices will now display as **Connected** simultaneously!\n\n"
            "The headphones will automatically switch audio to whichever device initiates a call or plays media."
        ),
        "policy_citation": "*Source: ProSound ANC Wireless Headphones Manual (Doc: KNOW-HP-001)*",
        "tags": ["headphones", "bluetooth", "multipoint", "pairing", "laptop", "phone", "audio", "macbook"]
    },
    {
        "exemplar_id": "EXEMP-ESP-01",
        "title": "Espresso Machine Orange Light Descaling Alert & Pressure Recovery",
        "category": "Product Diagnostics",
        "situation": "Espresso machine orange light is flashing and espresso extraction pressure is low.",
        "customer_inquiry": "The orange light on my BaristaPro espresso machine started flashing today and the pressure gauge barely reaches 5 bars. What is wrong with it?",
        "expert_thought": "Flashing orange icon is the automatic scale buildup sensor alert. Scale accumulation in boiler restricts flow and drops extraction pressure. Guide 50/50 water-vinegar descaling cycle (Brew + Steam 3s hold), followed by 30lb tamping and fine grind size (setting 2-4) to reach optimal 15 bars.",
        "expert_response": (
            "The flashing orange icon is your machine's **Automatic Descaling Alert**, which triggers every 200 brew cycles. Mineral scale accumulation inside the thermocoil restricts water flow and prevents the pump from building the required 15 bars of extraction pressure.\n\n"
            "Here is how to clear the alert and restore full 15-bar crema pressure:\n\n"
            "1. **Prepare Solution**: Mix 50% white vinegar (or official BaristaPro descaler) with 50% warm filtered water in the reservoir.\n"
            "2. **Initiate Descaling Mode**: Ensure the machine is turned on, then press and hold the **Brew + Steam** buttons simultaneously for **3 seconds**. The orange light will turn solid.\n"
            "3. **Purge Circuits**: Turn the dial to Hot Water for 30 seconds, then Steam for 30 seconds, and run the rest through the group head.\n"
            "4. **Rinse**: Fill reservoir with fresh clean water and run 2 complete purge cycles to eliminate any residual descaler.\n"
            "5. **Pressure Calibration**: Set grinder size to **Fine (Setting 2-3)** and tamp with **30 lbs of firm, level pressure** using 18g of freshly roasted beans.\n\n"
            "Once descaling completes, the orange light will shut off automatically and extraction pressure will return to optimal 15 bars!"
        ),
        "policy_citation": "*Source: BaristaPro Espresso Machine Manual (Doc: KNOW-ESP-002 & KNOW-ESP-003)*",
        "tags": ["espresso", "descaling", "orange light", "pressure", "crema", "cleaning", "grinder"]
    }
]


def list_knowledge_chunks(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches knowledge docs and FAQs stored in MongoDB with offline seed fallback."""
    col = get_knowledge_docs_collection()
    if col is not None:
        try:
            query = {"status": "active"}
            if category and category.lower() != "all":
                query["category"] = {"$regex": f"^{category}$", "$options": "i"}
            docs = list(col.find(query))
            if docs:
                return serialize_docs(docs)
        except Exception:
            pass
    # Fallback to SEED_KNOWLEDGE_DOCS if MongoDB offline or collection empty
    raw_seed = SEED_KNOWLEDGE_DOCS
    if category and category.lower() != "all":
        raw_seed = [d for d in SEED_KNOWLEDGE_DOCS if d.get("category", "").lower() == category.lower()]
    
    normalized = []
    for d in raw_seed:
        item = dict(d)
        item["doc_id"] = item.get("doc_id") or item.get("exemplar_id", "KNOW-SEED-001")
        item["heading"] = item.get("heading") or item.get("title", "Knowledge Document")
        item["content"] = item.get("content") or item.get("expert_response") or item.get("situation", "")
        item["doc_title"] = item.get("doc_title") or item.get("category", "General Support")
        normalized.append(item)
    return normalized


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
    """Fetches FAQ documents stored in MongoDB with offline seed fallback."""
    col = get_faqs_collection()
    if col is not None:
        try:
            query = {"status": "active"}
            if category and category.lower() != "all":
                query["category"] = {"$regex": f"^{category}$", "$options": "i"}
            docs = list(col.find(query))
            if docs:
                return serialize_docs(docs)
        except Exception:
            pass
    seed_faqs = []
    for f in SEED_KNOWLEDGE_DOCS:
        faq_item = {
            "faq_id": f.get("doc_id") or f.get("exemplar_id", "FAQ-SEED-001"),
            "category": f.get("category", "General Support"),
            "question": f.get("heading") or f.get("title", "Question"),
            "answer": f.get("content") or f.get("expert_response", "Answer"),
            "tags": f.get("tags", []),
            "status": f.get("status", "active")
        }
        if not category or category.lower() == "all" or f.get("category", "").lower() == category.lower():
            seed_faqs.append(faq_item)
    return seed_faqs


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

    # 8. Customer Profiles Collection (Cross-Session Semantic Memory)
    profiles_col = db["customer_profiles"]
    profiles_col.create_index([("customer_id", ASCENDING)], unique=True)
    profiles_col.create_index([("customer_email", ASCENDING)])

    if force_reseed or profiles_col.count_documents({}) == 0:
        for p in SEED_PROFILES:
            profiles_col.update_one({"customer_id": p["customer_id"]}, {"$set": p}, upsert=True)
        results["profiles_seeded"] = len(SEED_PROFILES)
    else:
        results["profiles_count"] = profiles_col.count_documents({})

    # 9. Customer Episodes Collection (Cross-Session Episodic Timeline)
    episodes_col = db["customer_episodes"]
    episodes_col.create_index([("episode_id", ASCENDING)], unique=True)
    episodes_col.create_index([("customer_id", ASCENDING)])
    episodes_col.create_index([("timestamp", ASCENDING)])

    if force_reseed or episodes_col.count_documents({}) == 0:
        for e in SEED_EPISODES:
            episodes_col.update_one({"episode_id": e["episode_id"]}, {"$set": e}, upsert=True)
        results["episodes_seeded"] = len(SEED_EPISODES)
    else:
        results["episodes_count"] = episodes_col.count_documents({})

    # 10. Gold-Standard Exemplars Collection (Dynamic Few-Shot In-Context RAG)
    exemplars_col = db["gold_exemplars"]
    exemplars_col.create_index([("exemplar_id", ASCENDING)], unique=True)
    exemplars_col.create_index([("category", ASCENDING)])

    if force_reseed or exemplars_col.count_documents({}) == 0:
        for ex in SEED_EXEMPLARS:
            exemplars_col.update_one({"exemplar_id": ex["exemplar_id"]}, {"$set": ex}, upsert=True)
        results["exemplars_seeded"] = len(SEED_EXEMPLARS)
    else:
        results["exemplars_count"] = exemplars_col.count_documents({})

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


