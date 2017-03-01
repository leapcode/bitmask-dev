import React from 'react'
import { Button, Glyphicon, Alert } from 'react-bootstrap'
import SectionLayout from './section_layout'

import Spinner from 'components/spinner'
import bitmask from 'lib/bitmask'

export default class VPNSection extends React.Component {

  static get defaultProps() {return{
    account: null
  }}

  constructor(props) {
    super(props)
    this.state = {
      error: null,
      expanded: false,
      vpn: "down",
    }
    this.expand     = this.expand.bind(this)
    this.connect    = this.connect.bind(this)
    this.disconnect = this.disconnect.bind(this)
    this.cancel     = this.cancel.bind(this)
    this.unblock    = this.unblock.bind(this)
    this.location   = this.location.bind(this)
  }

  expand() {
    this.setState({expanded: !this.state.expanded})
  }

  connect() {
    this.setState({vpn: "up"})
  }

  disconnect() {
    this.setState({vpn: "down"})
  }

  cancel() {

  }

  unblock() {

  }

  location() {

  }

  render () {
    let message = null
    let body = null
    let button = null
    let icon = null

    let header = <h1>VPN</h1>
    if (this.state.error) {
      // style may be: success, warning, danger, info
      message = (
        <Alert bsStyle="danger">{this.state.error}</Alert>
      )
    }
    if (this.state.expanded) {
      body = <div>traffic details go here</div>
    }

    switch(this.state.vpn) {
      case "down":
        button = <Button onClick={this.connect}>Turn ON</Button>
        icon = "disabled"
        break
      case "up":
        button = <Button onClick={this.disconnect}>Turn OFF</Button>
        icon = "on"
        break
      case "connecting":
        button = <Button onClick={this.cancel}>Cancel</Button>
        icon = "wait"
        break
      case "disconnecting":
        button = <Button onClick={this.cancel}>Cancel</Button>
        icon = "wait"
        break
      case "failed":
        button = <div>
          <Button onClick={this.connect}>Turn ON</Button>
          <Button onClick={this.unblock}>Unblock</Button>
        </div>
        icon = "off"
        break
    }

    return (
      <SectionLayout icon="planet" buttons={button} status={icon}
        onExpand={this.expand} header={header} body={body} message={message} />
    )
  }

}
