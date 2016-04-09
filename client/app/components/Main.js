var React = require('react');

var Main = React.createClass({
  render: function () {
    return (
      <div className="main-container full-height">
        <nav className="navbar navbar-default" role="navigation">
          <div className="col-sm-7 col-sm-offset-2" style={{ marginTop: 15 }}>
            MENU
          </div>
        </nav>
        {this.props.children}
      </div>
    );
  },
});

module.exports = Main;
