# import required libraries
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# source url
url = "https://docs.google.com/spreadsheets/d/1wQVypefm946ch4XDp37uZ-wartW4V7ILdg-qYiDXUHM/htmlview?usp=sharing&sle=true#"

# get the data from url
page = requests.get(url)

# create soup
soup = BeautifulSoup(page.text, 'html.parser')

# find the latest update timestamp
latest_sheet = soup.find(id="sheet-menu").find('a').text
latest_sheet_ts = datetime.strptime(latest_sheet, '%b%d_%I%M%p')

# get the data from current sheet
current_sheet = soup.find(id="sheets-viewport").find_all("div")[0]
current_table = current_sheet.find("table")

rows = current_table.find_all("tr")
contents = []
for i in range(2, len(rows)):
    row = rows[i]
    fields = row.find_all("td")
    content = {
        'State': fields[0].text,
        'Country': fields[1].text,
        'Last Update': datetime.strptime(fields[2].text, '%m/%d/%y %H:%M'),
        'Confirmed': int(fields[3].text),
        'Deaths': int(fields[4].text),
        'Recovered': int(fields[5].text)
    }
    contents.append(content)

# Sorting
contents_sorted = sorted(contents, key = lambda i: (i['Country'], i['State']))

# process contents
processed_content = []
country_data = None
country_details = []

for i in range(0, len(contents_sorted)):
    ct = contents_sorted[i]
    if country_data is None:
        country_details.append(ct)
        country_data = {
            'Country': ct['Country'],
            'Confirmed': ct['Confirmed'],
            'Deaths': ct['Deaths'],
            'Recovered': ct['Recovered'],
            'Details': country_details,
            'DetailsCount': len(country_details)
        }
    else:
        if country_data['Country'] == ct['Country']:
            country_details.append(ct)
            country_data = {
                'Country': country_data['Country'],
                'Confirmed': country_data['Confirmed'] + ct['Confirmed'],
                'Deaths': country_data['Deaths'] + ct['Deaths'],
                'Recovered': country_data['Recovered'] + ct['Recovered'],
                'Details': country_details,
                'DetailsCount': len(country_details)
            }
        else:
            processed_content.append(country_data)
            country_details = []
            country_details.append(ct)
            country_data = {
                'Country': ct['Country'],
                'Confirmed': ct['Confirmed'],
                'Deaths': ct['Deaths'],
                'Recovered': ct['Recovered'],
                'Details': country_details,
                'DetailsCount': len(country_details)
            }

    if (i == len(contents)):
        processed_content.append(country_data)


# final data
crna_data = {
    "sheet_update": latest_sheet_ts.replace(year=2020),
    "data": processed_content 
}

file='data.json' 
with open('data.json', 'w') as outfile:
    json.dump(crna_data, outfile, default=str)

