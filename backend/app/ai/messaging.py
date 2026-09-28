import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.8-flash")


def generate_message_template(restaurant_name, target_date, slot_start, offer_type, offer_value) -> str:
    """One message for the whole campaign. {name} is filled in later for each customer."""
    offer_text = "no special offer" if offer_type == "NONE" else f"{offer_type.replace('_', ' ').lower()}: {offer_value}"
    prompt = f"""Write a short, warm SMS (under 300 characters) from {restaurant_name}
inviting a customer to book a table on {target_date.strftime('%A, %B %d')} around {slot_start.strftime('%I:%M %p')}.
Start with a greeting that uses the exact text {{name}} where the customer's name goes.
Mention this offer naturally: {offer_text}.
Keep it friendly and not pushy. No hashtags, no emojis, no links."""

    try:
        text = model.generate_content(prompt).text.strip()
    except Exception as e:
        print("Gemini failed:", e)
        offer_line = ""
        if offer_type == "FREEBIE":
            offer_line = f" Enjoy a {offer_value.lower()} when you book."
        elif offer_type == "DISCOUNT_PERCENT":
            offer_line = f" Enjoy {offer_value}% off when you book."
        text = (f"Hi {{name}}, {restaurant_name} has a table free on "
                f"{target_date.strftime('%A')} at {slot_start.strftime('%I:%M %p')}.{offer_line}")

    if "{name}" not in text:          # safety: Gemini forgot the placeholder
        text = "Hi {name}, " + text
    return text