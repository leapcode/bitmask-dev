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
      vpn: "waiting",
    }
    this.expand     = this.expand.bind(this)
    this.connect    = this.connect.bind(this)
    this.disconnect = this.disconnect.bind(this)
    this.cancel     = this.cancel.bind(this)
    this.unblock    = this.unblock.bind(this)
    this.location   = this.location.bind(this)
  }

  componentWillMount() {
    bitmask.vpn.status().then(
      status => {
        console.log("status: ", status)
        if (status.VPN == "OFF") {
          this.setState({vpn: "down"})
        } else if (status.VPN == "ON") {
          if (status.domain == this.props.account.domain) {
            this.setState({vpn: "up"})
          } else {
            this.setState({vpn: "down"})
          }
        } else {
          // this.setState({vpn: "????"})
        }
      },
      error => {
        this.setState({vpn: "failed", error: error})
      }
    )
  }

  expand() {
    this.setState({expanded: !this.state.expanded})
  }

  // turn on button pressed
  connect() {
    this.setState({vpn: "connecting", error: null})
    bitmask.vpn.check(this.props.account.domain).then(
      status => {
        console.log('check: ', status)
        if (status.vpn_ready == true) {
          this.startVPN()
        } else if (status.vpn == "disabled") {
          this.setState({vpn: "failed", error: "VPN support disabled"})
        } else {
          bitmask.vpn.get_cert(this.props.account.id).then(
            uid => {
              this.startVPN()
            },
            error => {
              this.setState({vpn: "failed", error: error})
            }
          )
        }
      },
      error => {
        this.setState({vpn: "failed", error: error})
      }
    )
  }

  // turn off button pressed
  disconnect() {
    this.setState({vpn: "disconnecting", error: null})
    bitmask.vpn.stop().then(
      success => {
        console.log('stop:')
        console.log(success)
        this.setState({vpn: "down"})
      },
      error => {
        this.setState({vpn: "failed", error: error})
      }
    )
  }

  cancel() {

  }

  unblock() {

  }

  location() {

  }

  // call startVPN() only when everything is ready
  startVPN() {
    bitmask.vpn.start(this.props.account.domain).then(
      status => {
        console.log('start: ', status)
        if (status.result == "started") {
          this.setState({vpn: "up", error: null})
        } else {
          this.setState({vpn: "failed"})
        }
      },
      error => {
        this.setState({vpn: "failed", error: error})
      }
    )
  }

  render () {
    console.log(this.state)
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
        </div>
        // <Button onClick={this.unblock}>Unblock</Button>
        icon = "off"
        break
      case "disabled":
        button = <div>Disabled</div>
        icon = "disabled"
        break
      case "waiting":
        button = <Spinner />
        icon = "wait"
        break
    }

    return (
      <SectionLayout icon="planet" buttons={button} status={icon}
        onExpand={this.expand} header={header} body={body} message={message} />
    )
  }

}
