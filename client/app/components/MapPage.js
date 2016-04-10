import React from 'react';
import { Link } from 'react-router';
import { Map, Marker, Popup, TileLayer } from 'react-leaflet';

import getAllBeacons from '../utils/helpers';

var MapPage = React.createClass({
  getInitialState: () => {
    console.log('initialstate');
    return {
      beacons: [],
    };
  },

  componentDidMount: function () {
    console.log('component');
    navigator.geolocation.getCurrentPosition((data) => {
      getAllBeacons(data.coords.latitude, data.coords.longitude)
      .then((response) => {
        this.setState({ beacons: response });
        renderBeacons();
      });
    });
  },

  renderBeacons: function () {
    let beacons = this.state.beacons.map((beacon, index) => {
      let position = [beacon.lat, beacon.lng];
      return (
        <Marker position={position} key={index}>
          <Popup>
            <span>{beacon.description}</span>
          </Popup>
        </Marker>
      );
    });
    return beacons;
  },

  render: function () {
    const position = [43.16, -77.5];
    const mapStyle = { height: '100%' };
    return (
      <div className="map">
        <Map center={position} zoom={13} style={mapStyle}>
          <TileLayer
            url='http://{s}.tile.osm.org/{z}/{x}/{y}.png'
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          />
        { this.renderBeacons() }
        </Map>
        <Link to='new-beacon' className="btn btn-primary btn-fab add-beacon">
          <i className="material-icons">add</i>
        </Link>
      </div>
    );
  },
});

module.exports = MapPage;
