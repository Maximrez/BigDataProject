import pandas
import requests
import threading
import time

reader = pandas.read_csv("gkhinfo3.csv", sep=";", encoding="utf-8")


def NetResponse(geocoder_request):
    try:
        response = requests.get(geocoder_request)
        return response
    except:
        print("Yandex api не отвечает")
        time.sleep(5)
        response = NetResponse(geocoder_request)
        return response


def coords(place):
    # place = row['address']
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode=" + place + ", 1&format=json"
    response = NetResponse(geocoder_request)

    json_response = response.json()
    return json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]


reader["lon"] = 0
reader["lat"] = 0


# reader['coords'] = reader.apply(coords, axis=1)

def heart(q):
    coordinates = coords(reader["address"][q]).split()
    reader["lon"][q], reader["lat"][q] = coordinates[0], coordinates[1]
    print(str(q) + "/13694")


for q in range(0, len(list(reader["address"])), 2):
    t1 = threading.Thread(target=heart, args=[q])
    t2 = threading.Thread(target=heart, args=[q + 1])
    # t3 = threading.Thread(target=heart, args=[q+2])
    # t4 = threading.Thread(target=heart, args=[q +3])
    try:
        t1.start()
    except:
        pass
    try:
        t2.start()
    except:
        pass
    if q % 2000 == 0 and q > 0:
        print("Жду")
        time.sleep(60)
    # try:
    #     t3.start()
    # except:
    #     pass
    # try:
    #     t4.start()
    # except:
    #     pass
input()
reader.to_csv("gkhinfofinal3.csv", sep=";", encoding="utf-8")
