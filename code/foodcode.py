import json
import googlemaps
from geopy.distance import geodesic


with open("fulldata.json", "r") as file:
    data = json.load(file)

#find how well macros match
def macros_match(inp, food, calorie_margin = 100, mac_margin = 8):
    score  = 2
    if "Protein" in food and food["Protein"] == "-":
        del food["Protein"]             
    if inp["calories"] == None:  cal_dif = 0
    else : cal_dif = abs(inp["calories"] - food["Calories"]) / calorie_margin
    if inp["protein"] == None:  prot_dif = 0
    elif "Protein" not in food : prot_dif = 2
    else : prot_dif = abs(inp["protein"] - food["Protein"]) / mac_margin
    if inp["fats"] == None:  fat_dif = 0
    elif "Fats" not in food : fat_dif = 2
    else : fat_dif = abs(inp["fats"] - food["Fats"]) / mac_margin
    if inp["carbohydrates"] == None:  carb_dif = 0
    else : carb_dif = abs(inp["carbohydrates"] - food["Carbs"]) / mac_margin

    for ing in inp["restrictions"]:
        if ing in food["includes"]: return 0
        
    
    if cal_dif == 0 : score += 3
    elif cal_dif < 0.5  : score += 2
    elif cal_dif < 1 : score +=1
    else : return 0

    if carb_dif == 0 : score += 2
    elif carb_dif < 0.5  : score += 1.5
    elif carb_dif < 1: score
    else : return 0
    
    if prot_dif == 0 : score += 2
    elif prot_dif < 0.5  : score += 1.5
    elif prot_dif < 1 : score += 1
    else : return 0
    
    if fat_dif == 0 : score += 2
    elif fat_dif < 0.5  : score += 1.5
    elif fat_dif < 1 : score += 1
    else : return 0
    
    return score/11

#checking data
def data_check(inp):
    matches = {}

    for rest in data:
        for food in data[rest]:
                if macros_match(inp, data[rest][food]) > 0.4:
                    print(food)
                    if rest not in matches: matches[rest]  = {}
                    matches[rest][food] = macros_match(inp,  data[rest][food])

                if "Protein" not in data[rest][food] : data[rest][food]["Protein"] = "-"
                if "Fats" not in data[rest][food] : data[rest][food]["Fats"] = "-"
                
    for i in matches:
        sorted_dict = dict(sorted(matches[i].items(), key=lambda item: item[1], reverse = True))
        matches[i] = dict(list(sorted_dict.items()))
        for food in matches[i]:
            matches[i][food] = {"rating" : matches[i][food],
                                "carbs" : data[i][food]["Carbs"],
                                "fats" : data[i][food]["Fats"],
                                "proteins" : data[i][food]["Protein"],
                                "calories" : data[i][food]["Calories"],
                                }
                    
    return matches

#finding nearby restaurants

def find_nearby(lat, lng):
    API_KEY = "-"
    gmaps = googlemaps.Client(key=API_KEY)
    restaurants =['taco bell', 'mcdonalds', 'little caesars', 'krispy kreme', 'jack in the box', 'wendys', 'burger king', 'panda express', 'zaxbys', 'sonic', 'subway', 'caseys', 'chick fil a', 'arbys', 'starbucks', 'dominos', 'kfc', 'popeyes', 'five guys', 'wingstop', 'raising canes', 'in n out burger']

    radius = 16000
    results = {}

    for name in restaurants:
        try:
            r = gmaps.places_nearby(
                location=(lat, lng),
                radius=radius,
                keyword=name,
                type='restaurant'
            )
            if r['results']:
                place = r['results'][0]
                p_lat = place['geometry']['location']['lat']
                p_lng = place['geometry']['location']['lng']
                dist = geodesic((lat, lng), (p_lat, p_lng)).miles
                results[name] = {
                    'distance_miles': round(dist, 2),
                    'address': place.get('vicinity', 'N/A')
                }
            else:
                results[name] = None
        except:
            results[name] = None

    return dict(sorted(
        results.items(),
        key=lambda x: float('inf') if x[1] is None else x[1]['distance_miles']
    ))

#main return
def main(inp):
    food_result = data_check(inp)
    restaurants = find_nearby(inp["lat"], inp["long"])

    results = {}
    
    for restaurant in restaurants:
        if restaurants[restaurant] != None and restaurant in food_result:
            results[restaurant] = {}
            results[restaurant]["distance"]= restaurants[restaurant]['distance_miles']
            results[restaurant]["address"] = restaurants[restaurant]["address"]
            results[restaurant]["foods"] = food_result[restaurant.lower()]

    return results

    
    

