import requests, json, deepl, os
from datetime import date

from keys import keys


class OutdatedMenuError(Exception):
    pass


translator = deepl.Translator(keys['deepl'])


restaurant_codes = {
    'teknikens': '0f0s11r2fPPxl/HCPKfcfw==',
    'stuk': 'pqoaIFGvfWDNJYeU8bOQSA=='
}
days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
tag_translations = {
    'Vegansk': 'Vegan',
    'Glutenfri': 'Gluten free',
    'Laktosfri': 'Lactose free',
    'Äggfri': 'Egg free',
    'Nötfri': 'Nut free',
    'Fiskfri': 'Fish free',
    'Vegetarisk': 'Vegetarian',
}
    

def scrape_menu(code):
    print("Scraping menu")
    
    page = requests.get(f"https://www.matochmat.se/rest/menu?restaurant={restaurant_codes[code]}")
    if page.status_code != 200:
        return None
    
    # Get the menu
    menu = page.json()['data']['raw'][0]
    
    # Translate days to english
    keys = list(menu['content'].keys())
    for i, key in enumerate(keys):
        menu['content'][days[i]] = menu['content'].pop(key)
        
    # Translate menu to english
    query = []
    for day in menu['content']:
        for i in range(len(menu['content'][day])):
            if len(menu['content'][day][i]['description']) > 0:
                query.append (menu['content'][day][i]['description'])
            if len(menu['content'][day][i]['name']) > 0:
                query.append(menu['content'][day][i]['name'])
                
    result = translator.translate_text(query, target_lang='EN-GB')
    
    j = 0
    for day in menu['content']:
        for i in range(len(menu['content'][day])):
            if len(menu['content'][day][i]['description']) > 0:
                menu['content'][day][i]['description'] = result[j].text
                j += 1
            if len(menu['content'][day][i]['name']) > 0:
                menu['content'][day][i]['name'] = result[j].text
                j += 1
                
            for k in range(len(menu['content'][day][i]['tags'])):
                try:
                    menu['content'][day][i]['tags'][k] = tag_translations[menu['content'][day][i]['tags'][k]]
                except KeyError:
                    pass
    
    return menu


def get_menu(code):
    if code not in restaurant_codes:
        return None
    
    today = date.today().isocalendar()
    
    try:
        with open(os.path.join(os.path.join(os.getcwd(), f'menus/{code}.json')), 'r') as f:
            menu = json.load(f)
            if menu['year'] != today.year or menu['week'] != today.week:
                print('Outdated menu')
                raise OutdatedMenuError
            return menu['content'][days[today.weekday - 1] if today.weekday != 6 else 'sunday'] 
        
    except (FileNotFoundError, OutdatedMenuError, json.decoder.JSONDecodeError):
        with open(os.path.join(os.path.join(os.getcwd(), f'menus/{code}.json')), 'w') as f:
            menu = scrape_menu(code)
            json.dump(menu, f)
            return menu['content'][days[today.weekday - 1] if today.weekday != 6 else 'sunday']
    

if __name__ == "__main__":
    print(get_menu('teknikens'))