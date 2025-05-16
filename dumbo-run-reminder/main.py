import requests
# use slack client
import os
from slack_sdk import WebClient
import time

DISNEY_EVENT_STATUS_URL = "https://www.rundisney.com/run/api/v1/content/520589,521173,520608,520572,521126,436597,521123,520545,520548,411920,520558/event-cache/disneyland-half-marathon-weekend/?page=%2Fevents%2Fdisneyland%2Fdisneyland-half-marathon-weekend%2F"

# Post message
CHANNEL_ID = "C0821FRU2F7"
CHECK_EVERY_X_SECONDS = 30

SOLD_OUT_STATUS = "Sold Out"
SOLD_OUT_MESSAGE = "Dumbo Double Dare is sold out:\nhttps://www.rundisney.com/events/disneyland/disneyland-half-marathon-weekend/events/challenges/"
NOT_SOLD_OUT_MESSAGE = "Dumbo Double Dare is Ready to Register:\nhttps://www.rundisney.com/events/disneyland/disneyland-half-marathon-weekend/events/challenges/"

class SimpleBot:
    def __init__(self,token):
        self.client = WebClient(token=token)
        
    def send_message(self, channel, message):
        self.client.chat_postMessage(channel=channel, text=message)
    
    
def get_dumbo_run_event_status(event_status_url=DISNEY_EVENT_STATUS_URL) -> dict | None:
    try:
        response = requests.get(event_status_url)
        full_response = response.json()
        if 'eventBoxes' in full_response and 'eventInfo' in full_response['eventBoxes']:
            sub_events = full_response['eventBoxes']['eventInfo'].get('subEvents', [])
            for event in sub_events:
                    if event.get('title', '').lower() == "dumbo double dare":
                        return {'status': event.get('eventStatus', {}).get('statusName', '')}
    except Exception as e:
        print(f"Error getting event status: {e}")
        return None



def main_loop(client: SimpleBot):
    last_status = SOLD_OUT_STATUS
    while True:
        event_status = get_dumbo_run_event_status()
        print(f"received event status: {event_status}")
        if event_status is not None:
            if event_status['status'] != last_status:
                last_status = event_status['status']
                if event_status['status'] == SOLD_OUT_STATUS:
                    client.send_message(CHANNEL_ID, SOLD_OUT_MESSAGE)
                else:
                    client.send_message(CHANNEL_ID, NOT_SOLD_OUT_MESSAGE)
            # else do nothing
        time.sleep(CHECK_EVERY_X_SECONDS)
if __name__ == "__main__":
    bot_token = os.getenv('SLACK_SIMPLE_BOT_TOKEN')
    client = SimpleBot(bot_token)
    client.send_message(CHANNEL_ID, "Dumbo Run Reminder is running!")
    main_loop(client)



