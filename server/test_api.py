import requests
import json
import hashlib

base_url = 'http://localhost:6543'


def build_url(model, token, _id=False):
    if _id:
        return base_url + '/api/' + model + '/' + _id + '?token=' + token
    else:
        return base_url + '/api/' + model + '?token=' + token


def do_login(email, password):
    data = json.dumps({
        'email': email,
        'password': hashlib.sha256('password'.encode('utf-8')).hexdigest(),
    })
    resp = requests.post(base_url + '/api/users/login', data)
    print(resp.text)
    return json.loads(resp.text)


def do_get(model, _id):
    resp = requests.get(build_url(url, _id))
    print(resp.text)
    return json.loads(resp.text)


def do_get_all(model):
    resp = requests.get(build_url(url))
    return json.loads(resp.text)


def do_post(token, model, payload):
    data = json.dumps(payload)
    url = build_url(model, token)
    resp = requests.post(build_url(model, token), data)
    print(data)
    print(url)
    print(resp.status_code)
    print(resp.text)
    return json.loads(resp.text)


def do_load(token, model, fields, data):
    resp = []
    for d in data:
        payload = {}
        i = 0
        for f in fields:
            payload[f] = d[i]
            i += 1
        r = do_post(token, model, payload)
        resp.append(r)
    return resp


def create_beacon(token, topics, description, lat, lng, radius, expires):

    payload = dict(
        topics=topics,
        description=description,
        lat=lat,
        lng=lng,
        radius=radius,
        expires=expires,
    )

    beacon = do_post(token, 'beacons', payload)
    
    return beacon


def get_beacons(token, lat, lng, radius):

    url = base_url + '/api/beacons?token=' + token
    url += '&lat=' + str(lat) + '&lng=' + str(lng) + '&radius=' + str(radius)
    print(url)
    resp = requests.get(url)
    print(json.dumps(json.loads(resp.text), indent=4))
    return json.loads(resp.text)


def search_beacons(token, topic, lat, lng, radius):
    
    topic = topic.replace('#', '%23')

    url = base_url + '/api/beacons/_search?token=' + token
    url += '&topic=' + topic + '&lat=' + str(lat) + '&lng=' + str(lng) + '&radius=' + str(radius)
    print(url)
    resp = requests.get(url)
    #print(resp.status_code)
    print(json.dumps(json.loads(resp.text), indent=4))
    return json.loads(resp.text)

if __name__ == '__main__':

    print('Start\n')

    print('Getting Token ...')
    sys_user = do_login('system', 'password')
    token = sys_user['token']
    print('... Done.\n')

    print("\nCreating Beacon:\n")

    create_beacon(
        token=token,
        topics='#FeelTheBern #BernieSanders',
        description="Mah test beacon.",
        lat=43.1610,
        lng=-77.6109,
        radius=4,
        expires=30,
    )

    print("\nGetting Beacon List:\n")

    get_beacons(
        token=token,
        lat=43.1610,
        lng=-77.6109,
        radius=4,
    )

    print("\nSearching for 'apples'\n")

    search_beacons(
        token=token,
        topic='apples',
        lat=43.1610,
        lng=-77.6109,
        radius=4,
    )

    print("\nSearching for '#FeelTheBern'\n")

    search_beacons(
        token=token,
        topic='#FeelTheBern',
        lat=43.1610,
        lng=-77.6109,
        radius=4,
    )

