import React from 'react';
import { Map, Marker, Popup, TileLayer } from 'react-leaflet';

import getAllBeacons from '../utils/helpers';

var MapPage = React.createClass({
  getInitialState: () => {
    return {
      beacons: getAllBeacons(),
    };
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
    const position = [51.505, -0.09];
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
        <a href="javascript:void(0)" className="btn btn-primary btn-fab add-beacon">
          <i className="material-icons">add</i>
        </a>
      </div>
    );
  },
});

module.exports = MapPage;
