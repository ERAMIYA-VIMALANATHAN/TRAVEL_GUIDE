import pandas as pd
import nltk
import os
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

base_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(base_dir, "top_indian_places_to_visit.csv")

if not os.path.exists(csv_file):
    print("CSV file not found at:", csv_file)
    exit(1)

df = pd.read_csv(csv_file)
df.columns = [col.strip() for col in df.columns]

regional_food = {
    "north": ["Chole Bhature", "Paratha", "Dal Makhani"],
    "south": ["Idli", "Dosa", "Sambar"],
    "east": ["Pakhala", "Macher Jhol", "Rosogolla"],
    "west": ["Dhokla", "Pav Bhaji", "Seafood"],
    "central": ["Poha", "Biryani", "Sabzi"],
    "northeast": ["Thukpa", "Momos", "Yak meat"]
}

regional_activity = {
    "beach": ["Beach walks", "Water sports"],
    "heritage": ["Heritage tours", "Museum visits"],
    "wildlife": ["Wildlife safari", "Bird watching"],
    "hill_station": ["Trekking", "Cable car rides"],
    "religious": ["Temple visits", "Pilgrimage walks"]
}

def preprocess(text):
    tokens = nltk.word_tokenize(text.lower())
    return [lemmatizer.lemmatize(token) for token in tokens]

def get_response(user_input):
    words = preprocess(user_input)

    if "hi" in words or "hello" in words:
        return "Hello! Ask me about Indian cities or tourist places."
    if "bye" in words or "exit" in words:
        return "Goodbye! Have a great trip!"

    city_matches = df[df['City'].str.lower().apply(lambda x: x in user_input.lower())]

    if not city_matches.empty:
        city = city_matches['City'].iloc[0]
        zone = city_matches['Zone'].iloc[0].lower()

        response = f"Top places in {city} ({zone.title()} India):\n"

        for _, row in city_matches.iterrows():
            response += f"- {row['Name']} ({row['Type']}, Best time: {row['Best Time to visit']}, Entry ₹{row['Entrance Fee in INR']})\n"

        if zone in regional_food:
            response += "Local food: " + ", ".join(regional_food[zone]) + "\n"

        activities = set()
        for place_type in city_matches['Type'].str.lower().unique():
            if "beach" in place_type:
                activities.update(regional_activity["beach"])
            elif "fort" in place_type or "palace" in place_type:
                activities.update(regional_activity["heritage"])
            elif "park" in place_type or "wildlife" in place_type:
                activities.update(regional_activity["wildlife"])
            elif "hill" in place_type:
                activities.update(regional_activity["hill_station"])
            elif "temple" in place_type:
                activities.update(regional_activity["religious"])

        if activities:
            response += "Popular activities: " + ", ".join(activities) + "\n"

        places = list(city_matches['Name'].head(4))
        if len(places) >= 2:
            response += f"Sample Itinerary:\nDay 1: {places[0]} → {places[1]}\n"
            if len(places) > 2:
                response += f"Day 2: {places[2]} → {places[3]}\n"

        return response

    state_matches = df[df['State'].str.lower().apply(lambda x: x in user_input.lower())]
    if not state_matches.empty:
        state = state_matches['State'].iloc[0]
        places = ", ".join(state_matches['Name'].head(10).tolist())
        return f"Top places in {state}:\n{places}"

    return "Sorry, I don't understand. Ask about an Indian city or state."

print("TravelBot: Namaste! Ask me about any Indian city or tourist place (type 'exit' to quit).")

while True:
    user_input = input("You: ")
    reply = get_response(user_input)
    print("TravelBot:", reply)
    if "bye" in user_input.lower() or "exit" in user_input.lower():
        break
