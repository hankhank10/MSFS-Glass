import json
import re

import requests
import unicodedata

from bs4 import BeautifulSoup


# Sample HTML content
# function to extract html document from given url
def getHTMLdocument(url):
    # request for HTML document of given url
    response = requests.get(url)
    response.encoding = 'utf-8'
    # response will be provided in JSON format
    return response.text


# assign required credentials
# assign URL
urls_to_scrape = [
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Aircraft_Autopilot_Flight_Assist_Events.htm",
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Aircraft_Electrical_Events.htm",
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Aircraft_Engine_Events.htm",
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Aircraft_Flight_Control_Events.htm",
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Aircraft_Fuel_System_Events.htm",
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Aircraft_Instrumentation_Events.htm",
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Aircraft_Misc_Events.htm",
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Aircraft_Radio_Navigation_Events.htm",
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Helicopter_Specific_Events.htm",
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/Miscellaneous_Events.htm",
    "https://docs.flightsimulator.com/html/Programming_Tools/Event_IDs/View_Camera_Events.htm"
]
# Create a dictionary to store the events
events_dict = {}

for url in urls_to_scrape:

    # create document
    html_content = getHTMLdocument(url)

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the main title (h2) in the section
    main_title = soup.find('h2').text

    events_dict[main_title] = {}

    # Loop through all the subsections (h3 or h4)
    for subsection in soup.find_all(['h3', 'h4']):
        subsection_title = subsection.text.strip()
        # Find the following table
        table = subsection.find_next('table')
        events = []

        # Loop through each row in the table (skip the header row)
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) == 3:
                p_tags = cols[0].find_all('p')
                a_tags = cols[0].find_all('a')
                if len(p_tags) > 1:
                    for p_tag in p_tags:
                        event_name = p_tag.getText().strip()
                        parameters = unicodedata.normalize("NFKD", cols[1].text.strip())
                        description = unicodedata.normalize("NFKD", cols[2].text.strip())
                        events.append((event_name, parameters, description))
                elif len(a_tags) > 1:
                    for a_tag in a_tags:
                        event_name = a_tag.attrs["id"].strip()
                        parameters = unicodedata.normalize("NFKD", cols[1].text.strip())
                        description = unicodedata.normalize("NFKD", cols[2].text.strip())
                        events.append((event_name, parameters, description))

                else:
                    event_name = cols[0].text.strip()
                    parameters = unicodedata.normalize("NFKD", cols[1].text.strip())
                    description = unicodedata.normalize("NFKD", cols[2].text.strip())
                    events.append((event_name, parameters, description))

        # Add the events to the dictionary for the subsection
        events_dict[main_title][subsection_title] = events

json.dump(events_dict, open("../events.json", "w"), indent=4)

all_events = []
# Open the output Python file in write mode
with open('../SimConnect/EventSet.py', 'w') as f:
    # Create a list to store all set names
    set_names = []

    # Loop through the main titles
    for main_title, subsections in events_dict.items():
        # Create the set name by replacing spaces and slashes with a single underscore
        set_name = main_title.replace(' ', '_').replace('/', '_')

        # Collapse multiple underscores into one
        set_name = re.sub(r'_{2,}', '_', set_name).lower()

        # Add set name to the list of set names
        set_names.append(set_name)

        # Start defining the set inline with events
        f.write(f"{set_name} = {{\n")

        # Loop through the subsections of each main_title
        for subsection_title, events in subsections.items():
            # Add a comment for the subsection title
            f.write(f"    # {subsection_title}\n")

            # Add the event names to the set for this main_title (flattened) with newlines
            event_names = [event[0] for event in events]
            for event_name in event_names:
                f.write(f"    {repr(event_name)},\n")

        # Close the set definition for this main_title
        f.write("}\n\n")

    # Define the valid_events set by unioning all the individual sets
    f.write(f"valid_events = {' | '.join(set_names)}\n")
