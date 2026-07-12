INTENTS = {
    "create_complaint": ["complaint", "issue", "problem", "billing"],
    "update_priority": ["priority", "urgent", "high"],
    "close_complaint": ["close", "resolved", "done"],
    "check_status": ["status", "progress"],
    "greeting": ["hello", "hi", "hey"]
}


def classify_intent(text: str):

    text = text.lower()

    best_intent = "unknown"
    best_matches = []

    for intent, keywords in INTENTS.items():

        matches = [k for k in keywords if k in text]

        if len(matches) > len(best_matches):
            best_matches = matches
            best_intent = intent

    confidence = (
        len(best_matches) /
        len(INTENTS.get(best_intent, []))
        if best_intent != "unknown"
        else 0.0
    )

    return {
        "intent": best_intent,
        "confidence": round(confidence, 2),
        "matched_keywords": best_matches
    }

def generate_response(intent):
#make responses for each intent work 
    responses = {

        "greeting":
            "Hello! How can I help you today?",

        "create_complaint":
            "Your complaint has been recorded.",

        "update_priority":
            "Your complaint priority has been updated.",

        "close_complaint":
            "Your complaint has been closed.",

        "check_status":
            "Your complaint is currently under review.",

        "unknown":
            "Sorry, I couldn't understand your request."

    }

    return responses.get(intent, "Unknown request.")