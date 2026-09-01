"""
Interactive Vendor & Support Specialist Portal CLI
Allows support engineers and vendor representatives to view open tickets,
submit technical responses, and resolve/close tickets.
"""

import os
import sys
import datetime

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from customer_care.ticket_service import (
    load_all_tickets,
    get_ticket,
    update_vendor_response,
    close_ticket
)


def display_tickets_table():
    tickets = load_all_tickets()
    print("\n" + "=" * 95)
    print(" 📋 CURRENT SUPPORT & ESCALATION TICKETS")
    print("=" * 95)
    print(f"{'Ticket ID':<20} | {'Status':<25} | {'Priority':<10} | {'Order ID':<10} | {'Assigned Team / Vendor'}")
    print("-" * 95)

    if not tickets:
        print("  (No tickets found in store)")
        print("-" * 95)
        return tickets

    for tid, t in tickets.items():
        status = t.get("status", "Unknown")
        priority = t.get("priority", "Medium")
        order_id = t.get("order_id", "N/A")
        assigned = t.get("assigned_vendor", "General Support")[:35]
        print(f"{tid:<20} | {status:<25} | {priority:<10} | {order_id:<10} | {assigned}")

    print("=" * 95)
    return tickets


def view_ticket_details():
    tid = input("\n👉 Enter Ticket ID to inspect (e.g. TCK-10023-17ACC or ESC-2942-T2): ").strip()
    ticket = get_ticket(tid)
    if not ticket:
        print(f"❌ Ticket '{tid}' not found.")
        return

    print("\n" + "-" * 60)
    print(f"🎫 TICKET DETAILS: {ticket['ticket_id']}")
    print("-" * 60)
    print(f"• Customer:      {ticket.get('customer_name')} ({ticket.get('customer_id')})")
    print(f"• Contact Phone: {ticket.get('customer_phone')}")
    print(f"• Email:         {ticket.get('customer_email')}")
    print(f"• Order ID:      {ticket.get('order_id')}")
    print(f"• Product:       {ticket.get('product_name')}")
    print(f"• Category:      {ticket.get('category')}")
    print(f"• Priority:      {ticket.get('priority')}")
    print(f"• Status:        {ticket.get('status')}")
    print(f"• Created At:    {ticket.get('created_at')}")
    print(f"• Subject:       {ticket.get('subject')}")
    print(f"• Description:   {ticket.get('description')}")
    print(f"• Assigned Team: {ticket.get('assigned_vendor')}")
    print(f"• Estimated SLA: {ticket.get('estimated_sla')}")
    if ticket.get("vendor_response"):
        print(f"\n✅ VENDOR RESOLUTION:")
        print(f"  Responder:     {ticket.get('vendor_responder_name')}")
        print(f"  Responded At:  {ticket.get('vendor_responded_at')}")
        print(f"  Response:      {ticket.get('vendor_response')}")
    print("-" * 60)


def submit_resolution():
    tid = input("\n👉 Enter Ticket ID to resolve/reply: ").strip()
    ticket = get_ticket(tid)
    if not ticket:
        print(f"❌ Ticket '{tid}' not found.")
        return

    print(f"\nReplying to Ticket: {ticket['ticket_id']} ({ticket.get('subject')})")
    responder_name = input("Your Name & Role (e.g. Marcus Vance - Senior Hardware Lead): ").strip()
    if not responder_name:
        responder_name = "Authorized Vendor Specialist"

    print("\nEnter your technical resolution / response:")
    response_text = input("> ").strip()
    if not response_text:
        print("❌ Response text cannot be empty.")
        return

    status_choice = input("Set status to [1] 'Vendor Responded' or [2] 'Closed' (Default 1): ").strip()
    status = "Closed" if status_choice == "2" else "Vendor Responded"

    updated = update_vendor_response(
        ticket_id=tid,
        vendor_response=response_text,
        vendor_responder_name=responder_name,
        status=status
    )

    if updated:
        print(f"\n🎉 Successfully recorded vendor resolution for {tid}!")
        print(f"Status updated to: '{status}'")
    else:
        print(f"❌ Failed to update ticket {tid}.")


def main():
    while True:
        print("\n" + "═" * 50)
        print(" 🛠️  CUSTOMER CARE VENDOR & RESOLUTIONS PORTAL")
        print("═" * 50)
        print(" [1] 📋 View all tickets")
        print(" [2] 🔍 Inspect specific ticket details")
        print(" [3] ✍️  Submit vendor response / resolve ticket")
        print(" [4] ❌ Exit")
        choice = input("\nSelect an option (1-4): ").strip()

        if choice == "1":
            display_tickets_table()
        elif choice == "2":
            view_ticket_details()
        elif choice == "3":
            submit_resolution()
        elif choice == "4":
            print("\nExiting Vendor Portal. Goodbye!\n")
            break
        else:
            print("Invalid option. Please choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
