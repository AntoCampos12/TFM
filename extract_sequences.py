import json
import os
import input

if not os.path.exists("full.json"):
    with open("full.json", "w") as file:
        actividades = input.__obtener_modelo_3()
        json.dump(actividades, file)
else:
    with open("full.json", "r") as file:
        actividades = json.load(file)

with open("2010_3.txt", "w")as file:
    for user in actividades:
        file.write(user + ";")
        reduced_activities = {}
        for week in actividades[user]:
            actividades[user][week] = sorted(actividades[user][week], key= lambda x: x['date'])
            reduced_activities[int(week)] = input.__parse_valores3(actividades[user][week])
        file.write(json.dumps(reduced_activities) + "\n")

