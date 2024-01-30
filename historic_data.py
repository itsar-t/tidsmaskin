from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import re
import pickle

# Lista för att hålla alla händelser från båda källorna
all_historic_events = []

def save_to_cache(data, filename='event_cache.pkl'):
    """Sparar data till en fil för caching."""
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def load_from_cache(filename='event_cache.pkl'):
    """Läser och returnerar cachade data från en fil, om filen finns."""
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

def extract_events_from_historysite():
    # Skapa en instans av Options och sätt den i headless-läge
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Initiera webbläsaren med ChromeDriverManager och inställningarna
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Gå till webbsidan
    driver.get("https://historiesajten.se/handelser2.asp?id=24#1500")

    # Hitta alla rader i tabellen
    rows = driver.find_elements(By.CSS_SELECTOR, "table.TFtable tr")

    # Skapa en lista för att hålla alla händelser
    historic_events = []

    # Iterera över alla rader och extrahera årtalet och händelserna
    for row in rows:
        # Hitta alla celler i raden
        cells = row.find_elements(By.TAG_NAME, "td")
        # Kontrollera att raden har rätt struktur
        if len(cells) == 2:
            # Årtal är i första cellen, händelse i andra cellen
            year = cells[0].text.strip()
            event = cells[1].text.strip()
            # Lägg till ett tuple med (år, händelse) till listan
            historic_events.append((year, event))

    # Stäng webbläsaren
    driver.quit()

    return historic_events

def add_linebreaks_after_eight_words(text):
    words = text.split()
    # Dela upp texten var åttonde ord
    lines = [' '.join(words[i:i+8]) for i in range(0, len(words), 8)]
    # Kombinera linjerna med en radbrytning
    return '\n'.join(lines)

def extract_events_from_wikipedia(url):
    # Skapa en instans av Options och sätt den i headless-läge
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Initiera webbläsaren med ChromeDriverManager och inställningarna
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Gå till webbsidan
    driver.get(url)

    # Hitta alla listpunkter på sidan
    list_items = driver.find_elements(By.CSS_SELECTOR, "ul > li")

    # Skapa en lista för att hålla alla händelser
    wikipedia_events = []

    # Iterera över alla listpunkter och extrahera informationen
    for item in list_items:
        text = item.text
        # Matcha olika mönster: enskilda år, årtal (ex. "1100-talet") och intervall (ex. "1521-23")
        match = re.match(r'(\d+)(\-\d+)?(talet)?(?: – )?(.*)', text)
        if match:
            start_year = match.group(1)
            end_year = match.group(2)
            century = match.group(3)
            event_text = match.group(4)
            formatted_event_text = add_linebreaks_after_eight_words(event_text)
            
            if century:  # Det är ett årtal
                wikipedia_events.append((f"{start_year}{century}", f"· {formatted_event_text}"))
            elif end_year:  # Det är ett årtalsintervall
                end_year = end_year.lstrip('-')
                if len(end_year) == 2:  # Kortare format, t.ex. "21" istället för "1521"
                    end_year = start_year[:2] + end_year
                range_text = f"({start_year}-{end_year})"
                for year in range(int(start_year), int(end_year) + 1):
                    wikipedia_events.append((str(year), f"· {range_text} {formatted_event_text}"))
            else:  # Det är ett enskilt år
                wikipedia_events.append((start_year, f"· {formatted_event_text}"))

    # Stäng webbläsaren
    driver.quit()

    return wikipedia_events

def getEvents(year):
    found_events = []
    for event_year, event in all_historic_events:
        if event_year == str(year):
            if "(Wikipedia)" in event:
                # Wikipedia händelse, se till att korrekt år visas och lägg till punkt
                event = f"· {event.replace('(Wikipedia)', '').strip()}"
            found_events.append(event)

    if not found_events:
        found_events.append("Ingen händelse registrerad för detta år.")

    return found_events

# Kombinera händelserna från historiesajten och Wikipedia
if __name__ == "__main__":
    cached_events = load_from_cache()
    if cached_events is None:
        print("Ingen cachad data hittad. Utför skrapning...")
        all_historic_events = []
        all_historic_events.extend(extract_events_from_historysite())
        all_historic_events.extend(extract_events_from_wikipedia("https://sv.wikipedia.org/wiki/Tidsaxel_%C3%B6ver_Sveriges_historia"))
        save_to_cache(all_historic_events)

    else:
        print("Använder cachad data.")
        all_historic_events = cached_events
        
       
        


