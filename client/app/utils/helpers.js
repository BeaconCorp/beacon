import axios from 'axios';
import auth from '../components/auth/helpers';

export function createBeacon(options) {
  let token = auth.getToken();
  return axios.post(`http://beacon.mycodespace.net/api/beacons?token=${token}`, {
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
  let token = auth.getToken();
  return axios.get(`http://beacon.mycodespace.net/api/beacons`, {
    params: {
      lat: lat,
      lng: lng,
      radius: 4000,
      token: token,
    },
  });

};
