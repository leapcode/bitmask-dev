import React from 'react'
import { Button, ButtonToolbar, Glyphicon, Alert } from 'react-bootstrap'
import SectionLayout from './section_layout'

import Spinner from 'components/spinner'
import bitmask from 'lib/bitmask'

export default class vpnSection extends React.Component {

  static get defaultProps() {return{
    account: null
  }}

  constructor(props) {
    super(props)
    this.state = {
      interval: null,  // timer callback
      error: null,     // error message
      message: null,   // info message
      expanded: false, // show vpn section expanded or compact
      ready: false,    // true if vpn can start
      vpn: "unknown",  // current state of vpn
      up: null,        // \ throughput
      down: null       // / labels
    }
    this.expand     = this.expand.bind(this)
    this.connect    = this.connect.bind(this)
    this.disconnect = this.disconnect.bind(this)
    this.retry      = this.retry.bind(this)
    this.enable     = this.enable.bind(this)
    this.installHelper = this.installHelper.bind(this)

    this.statusEvent = this.statusEvent.bind(this)
    this.loginEvent  = this.loginEvent.bind(this)
  }

  // called whenever a new account is selected
  componentWillReceiveProps(nextProps) {
    this.stopWatchingStatus()
    if (this.props.account.domain != nextProps.account.domain) {
      this.checkReadiness(nextProps.account.domain)
    }
  }

  // called only once
  componentWillMount() {
    this.checkReadiness()
    bitmask.events.register("VPN_STATUS_CHANGED", 'vpn section update', this.statusEvent)
    bitmask.events.register("BONAFIDE_AUTH_DONE", 'vpn section auth', this.loginEvent)
  }

  // not sure if this is ever called
  componentWillUnmount() {
    bitmask.events.unregister("VPN_STATUS_CHANGED", 'vpn section update')
    bitmask.events.unregister("BONAFIDE_AUTH_DONE", 'vpn section auth')
    this.stopWatchingStatus()
  }

  updateStatus(domain = null) {
    domain = domain || this.props.account.domain
    bitmask.vpn.status().then(
      vpn => {
        this.stopWatchingStatus()
        // If the current active VPN does not match this domain, ignore the status info.
        if (vpn.domain !== domain || vpn.status === "off") {
          this.setState({vpn: "down"})
        } else if (vpn.status === "on") {
          this.setState({
            vpn: "up",
            up: vpn.up,
            down: vpn.down
          })
          this.startWatchingStatus()
        } else if (vpn.status === "disabled") {
          this.setState({vpn: "disabled"})
        } else if (vpn.status === "starting") {
          this.setState({vpn: "connecting"})
        } else {
          console.log("UNKNOWN STATUS", vpn.status)
          // it should not get here...
          this.setState({vpn: "waiting"})
        }
      },
      error => {
        this.setState({vpn: "failed", error: error})
      }
    )
  }

  //
  // Check if all the prerequisites have been met.
  // This is called whenever the widget is shown, and also whenever a user
  // authenticates
  //
  checkReadiness(domain = null) {
    domain = domain || this.props.account.domain
    bitmask.vpn.check(domain).then(
      status => {
        console.log('check()', status)
        if (status.vpn == 'disabled') {
          this.setState({vpn: "disabled"})
        } else if (!status.installed) {
          this.setState({vpn: "nohelpers"})
        } else if (!status.vpn_ready) {
          this.renewCert()
        } else {
          this.setState({
            message: null,
            error: null,
            ready: true
          })
          this.updateStatus(domain)
        }
      },
      error => {
        console.log('check()', error)
        if (error == "Missing VPN certificate") {
          this.renewCert()
        }
        if (error == 'nopolkit') {
          this.setState({vpn: "nopolkit"})
        } else {
          this.setState({vpn: "failed", error: error})
        }
      }
    )
  }

  //
  // install the necessary helper files
  //
  installHelper() {
    bitmask.vpn.install().then(
      ok => {
        this.checkReadiness()
      },
      error => {
        console.log('install()', error)
        this.setState({vpn: "failed", error: error})
      }
    )
  }


  //
  // event callback: something new has happened, time to re-poll
  //
  statusEvent() {
    console.log('statusEvent')
    this.updateStatus()
  }

  //
  // event callback: the user successfully logged in
  //
  loginEvent(event, user) {
    let address = user[1]
    this.checkReadiness(address.split('@')[1])
  }

  //
  // get new vpn cert from provider
  //
  renewCert() {
    if (!this.props.account.authenticated) {
      this.setState({
        message: 'Please log in to renew VPN credentials.',
        vpn: null
      })
    } else {
      let message = (<div>
        <Spinner/>&nbsp;<span>Renewing VPN credentials...</span>
      </div>)
      this.setState({message: message})
      bitmask.vpn.get_cert(this.props.account.id).then(
        ok => {
          console.log('get_cert()', ok)
          this.checkReadiness()
        }, error => {
          console.log('get_cert()', error)
          this.setState({vpn: "failed", error: error})
        }
      )
    }
  }

  // section expand/collapse button pressed
  expand() {
    this.setState({expanded: !this.state.expanded})
  }

  // turn on button pressed
  connect() {
    this.setState({vpn: "connecting", error: null})
    bitmask.vpn.stop().then(
      wasRunning   => {this.startvpn()},
      wasntRunning => {this.startvpn()}
    )
  }

  // turn off button pressed
  disconnect() {
    this.setState({vpn: "disconnecting", error: null})
    bitmask.vpn.stop().then(
      success => {
        this.setState({vpn: "down"})
      },
      error => {
        this.setState({vpn: "failed", error: error})
      }
    )
  }

  // retry button pressed
  retry() {
    this.setState({error: null, message: null, vpn: 'waiting'})
    this.updateStatus()
    this.checkReadiness()
  }

  // enable button pressed
  enable() {
    this.setState({error: null, message: null, vpn: 'waiting'})
    bitmask.vpn.enable().then(
      ok => {
        console.log('enable()', ok)
        this.retry()
      },
      error => {
        this.setState({error: error, message: null, vpn: 'failed'})
        console.log('enable(error)', error)
      }
    )
  }

  //
  // call startvpn() only when everything is ready, and no vpn is currently
  // running.
  //
  startvpn() {
    bitmask.vpn.start(this.props.account.domain).then(
      status => {
        console.log('start success', status)
      }, error => {
        console.log('start error', error)
        this.setState({vpn: "failed", error: error})
      }
    )
  }

  startWatchingStatus() {
    this.interval = setInterval(this.statusEvent, 1000)
  }

  stopWatchingStatus() {
    clearInterval(this.interval)
  }

  render () {
    let message = null
    let error = null
    let body = null
    let button = null
    let icon = null
    let info = null
    let expand = null // this.expand

    // style may be: success, warning, danger, info
    if (this.state.error) {
      error = (
        <Alert bsStyle="danger">{this.state.error}</Alert>
      )
    }
    if (this.state.message) {
      message = (
        <Alert bsStyle="info">{this.state.message}</Alert>
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
        info = "Connected"
        if (this.state.up) {
          info = <span>
            <Glyphicon glyph="chevron-down" />
            {this.state.down}
            &nbsp;&nbsp;
            <Glyphicon glyph="chevron-up" />
            {this.state.up}
          </span>
        }
        break
      case "connecting":
        button = <Button onClick={this.disconnect}>Cancel</Button>
        icon = "wait"
        info = "Connecting..."
        break
      case "disconnecting":
        button = <Button onClick={this.disconnect}>Cancel</Button>
        icon = "wait"
        break
      case "nopolkit":
        info = "Missing authentication agent."
        body = (
          <div>
            <p>Could not find a polkit authentication agent.
            Please run one and try again.</p>
          </div>
        )
        icon= "disabled"
        break
      case "failed":
        info = "Failed"
        if (this.state.ready) {
          button = <ButtonToolbar>
            <Button onClick={this.connect}>Turn ON</Button>
            <Button onClick={this.disconnect}>Unblock</Button>
          </ButtonToolbar>
        } else {
          button = <Button onClick={this.retry}>Retry</Button>
        }
        icon = "off"
        break
      case "disabled":
        button = <Button onClick={this.enable}>Enable</Button>
        icon = "disabled"
        break
      case "waiting":
        button = <Spinner />
        icon = "wait"
        break
      case "nohelpers":
        body = (
          <div>
            <p>The VPN requires that certain helpers are installed on your system.</p>
            <Button onClick={this.installHelper}>Install Helper Files</Button>
          </div>
        )
        break
    }

    let header = (
      <div>
        <h1>VPN</h1>
        <span className="info">{info}</span>
      </div>
    )

    if (button == null) {
      expand = null
    }

    return (
      <SectionLayout icon="planet" buttons={button} status={icon}
        onExpand={expand} header={header} body={body}
        message={message} error={error} />
    )
  }

}
