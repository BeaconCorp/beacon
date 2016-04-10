import axios from 'axios';

export function createBeacon(options) {
  
  console.log('helers, createBeacon(), options: ', options);

  return axios.post('http://beacon.mycodespace.net/api/beacons', {
    title: options.title,
    description: options.description,
    radius: options.radius,
    topics: options.topics,
    expires: 30,
    lat: options.lat,
    lng: options.lng,
    radius: 4,
  });
};

export function getAllBeacons(lat, lng) {

  console.log('helpers, getAllBeacons()');

  return axios.get('http://beacon.mycodespace.net/api/beacons', {
    lat: lat,
    lng: lng,
    radius: 4,
  });

};


