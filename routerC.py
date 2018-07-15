from pyroutelib3 import Router
router = Router("car", "/home/user/Desktop/maps/RU-PRI.osm")

lat, lon = 45.944457, 133.805337
lat1, lon1 = 43.745925, 135.284925
start = router.data.findNode(lat, lon) # Find start and end nodes
end = router.data.findNode(lat1, lon1)

status, route = router.doRoute(start, end) # Find the route - a list of OSM nodes

if status == 'success':
    routeLatLons = list(map(router.nodeLatLon, route)) # Get actual route coordinates

#print(status)
print(route, routeLatLons, sep = '\n')

distance = 0;

for i in range(1, len(route)):
    distance += router.distance(route[i-1],route[i])

print(distance)