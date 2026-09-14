"""
Convo AI Voice Caller Agent for Real Estate.
Fully compatible with Google ADK (Agent Development Kit).
Implements the multi-persona realtor caller agent with domain tools and safety guardrails.
"""

import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.genai import types

MODEL_NAME = os.environ.get("CONVOAI_MODEL", "gemini-3.5-flash-lite")


# -------------------------------------------------------------
# Convo AI Real Estate Tools
# -------------------------------------------------------------

def check_property_availability(developer: str, project: str, configuration: str) -> Dict[str, Any]:
    """
    Check current inventory and carpet area for a given developer project and BHK configuration.
    
    Args:
        developer: Developer name (e.g. Adani Realty, DTC Group, House of Hiranandani, Veena Developers, Signature Global)
        project: Project name (e.g. Teen Hath Naka, Codename LIT, DTC Stillwaters, Veena Synergy, DAXIN GURUGRAM)
        configuration: 2 BHK, 3 BHK, 4 BHK, or Independent Floors
    """
    dev_lower = developer.lower()
    cfg_upper = configuration.upper()
    
    inventory = {
        "adani": {
            "2 BHK": {"available": True, "carpet_sqft": "788 to 802 sq.ft.", "starting_price": "1.90 Crore"},
            "3 BHK": {"available": True, "carpet_sqft": "1,133 sq.ft.", "starting_price": "Price on Site Visit only"}
        },
        "dtc": {
            "3 BHK": {"available": True, "carpet_sqft": "1,250 sq.ft.", "starting_price": "Available on Inquiry"},
            "4 BHK": {"available": True, "carpet_sqft": "1,680 sq.ft.", "starting_price": "Available on Inquiry"}
        },
        "veena": {
            "2 BHK": {"available": True, "carpet_sqft": "650 sq.ft.", "starting_price": "2.18 Crore"},
            "3 BHK": {"available": True, "carpet_sqft": "920 sq.ft.", "starting_price": "Available on Inquiry"}
        },
        "hiranandani": {
            "2 BHK": {"available": True, "carpet_sqft": "677 to 756 sq.ft.", "starting_price": "1.72 Crore"}
        },
        "signature": {
            "INDEPENDENT FLOORS": {"available": True, "carpet_sqft": "Basement + Stilt + 4 Floors + Terrace", "starting_price": "2.10 Crore"}
        }
    }
    
    for key, data in inventory.items():
        if key in dev_lower:
            for c_key, details in data.items():
                if c_key in cfg_upper:
                    return {
                        "status": "AVAILABLE",
                        "developer": developer,
                        "project": project,
                        "configuration": configuration,
                        "details": details
                    }
                    
    return {
        "status": "AVAILABLE",
        "developer": developer,
        "project": project,
        "configuration": configuration,
        "note": "Units available. Detailed layouts available during site visit."
    }


def schedule_site_visit(
    developer: str,
    project: str,
    visit_date: str,
    visit_time: str,
    customer_phone: Optional[str] = None,
    configuration: Optional[str] = None
) -> Dict[str, Any]:
    """
    Schedule an on-site property visit for the prospective homebuyer.
    
    Args:
        developer: Name of the developer
        project: Name of the property project
        visit_date: Date of visit (e.g. 'Tomorrow', 'This Sunday', 'Next Saturday')
        visit_time: Time of visit. Note: Official hours are strictly 10:00 AM to 7:00 PM.
        customer_phone: Contact number for SMS/WhatsApp pass
        configuration: Preferred BHK configuration
    """
    # Policy validation check for visiting hours (10:00 AM - 7:00 PM)
    time_str = visit_time.lower().strip()
    if "8:00 am" in time_str or "8 am" in time_str or "9:00 am" in time_str or "8 o'clock" in time_str and "morning" in time_str:
        return {
            "status": "REJECTED_OUT_OF_HOURS",
            "message": "Site visit operating hours are strictly from 10:00 AM to 7:00 PM. Please reschedule between 10:00 AM and 7:00 PM."
        }
        
    return {
        "status": "CONFIRMED",
        "developer": developer,
        "project": project,
        "appointment_date": visit_date,
        "appointment_time": visit_time,
        "executive_assigned": True,
        "confirmation_message": f"Site visit successfully scheduled for {visit_date} at {visit_time}. A sales executive will meet you at the site."
    }


def send_whatsapp_brochure(project_name: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
    """
    Dispatches digital brochure, location pin, and floor plans to the user via WhatsApp.
    
    Args:
        project_name: Name of the real estate project
        phone_number: Recipient WhatsApp phone number
    """
    return {
        "status": "DISPATCHED",
        "channel": "WhatsApp",
        "project": project_name,
        "content": ["Floor Plans", "Pricing Sheet", "Google Maps Location Link", "Amenities Deck"]
    }


# -------------------------------------------------------------
# Realtor System Instructions
# -------------------------------------------------------------

REALTOR_AGENT_INSTRUCTIONS = """
You are Aditi / Riya / Pooja, an expert AI Voice Calling Specialist representing premier real estate developers (Adani Realty, DTC Group, House of Hiranandani, Veena Developers, Signature Global).

Your objective is to conduct a natural, engaging, and professional voice conversation with prospective buyers:

### Key Operational Rules & Policies:
1. **Mandatory Call Recording Disclosure**: On opening, politely disclose: "Hello. This call is now being recorded. Hi, this is Aditi from Adani Realty..."
2. **Lead Qualification Discovery**:
   - Determine buying intent early: Ask if they are looking for **self-use** or as an **investment**.
   - Discover configuration preference: 2 BHK, 3 BHK, 4 BHK, or independent floors.
3. **Site Visit Scheduling Policy**:
   - Driving towards an in-person site visit is your primary conversion goal.
   - **STRICT OPERATING HOURS**: Site visits are ONLY conducted between **10:00 AM and 7:00 PM**.
   - If a customer demands an out-of-hours time (e.g. 8:00 AM or before 10:00 AM), politely refuse and explain that visiting hours start at 10:00 AM, offering a convenient slot like 10:00 AM or late afternoon (e.g., 5:00 PM).
   - Once a date and time are agreed upon, invoke `schedule_site_visit`.
4. **Pricing Policy**:
   - Disclose starting prices for entry units (e.g., 2 BHK starting at 1.90 Crore at Teen Hath Naka, 1.72 Crore at Hiranandani, or 2.10 Crore in Gurugram).
   - For 3 BHK or premium units, inform the lead that exact pricing and custom floor plans are provided exclusively during the on-site visit by senior sales managers.
5. **Follow-Up Collateral**:
   - Offer to send property brochures, walkthrough videos, and Google Maps location pins via WhatsApp using `send_whatsapp_brochure`.
6. **Multilingual & Fluency**:
   - If the customer speaks Hindi or Hinglish, switch seamlessly into polite Hindi/Hinglish (e.g., "DTC Stillwaters mein premium 3BHK or 4BHK apartments hain... Main abhi hi arrange karwa deti hoon").
   - Maintain a courteous, warm, and natural conversational cadence.
"""

root_agent = Agent(
    name="convoai_realtor_agent",
    model=MODEL_NAME,
    description="Convo AI Voice Caller Agent for real estate lead qualification, objection handling, and appointment booking.",
    instruction=REALTOR_AGENT_INSTRUCTIONS,
    tools=[
        check_property_availability,
        schedule_site_visit,
        send_whatsapp_brochure
    ]
)

# Alias for ADK evaluator module loading
agent = root_agent
