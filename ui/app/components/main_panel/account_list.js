import React from 'react'
import {Button, ButtonGroup, ButtonToolbar, Glyphicon} from 'react-bootstrap'

import App from 'app'
import Account from 'models/account'
import Confirmation from 'components/confirmation'
import AppButtons from './app_buttons'
import bitmask from 'lib/bitmask'

export default class AccountList extends React.Component {

  static get defaultProps() {return{
    account: null,
    accounts: [],
    onAdd: null,
    onRemove: null,
    onSelect: null
  }}

  constructor(props) {
    super(props)

    this.state = {
      mode: 'expanded',
      showRemoveConfirmation: false,
      activeVpnDomain: null,
      activeVpnStatus: null
    }

    // prebind:
    this.select = this.select.bind(this)
    this.add    = this.add.bind(this)
    this.remove = this.remove.bind(this)
    this.askRemove = this.askRemove.bind(this)
    this.cancelRemove = this.cancelRemove.bind(this)
    this.expand = this.expand.bind(this)
    this.collapse = this.collapse.bind(this)
    this.statusEvent = this.statusEvent.bind(this)
  }

  componentWillMount() {
    // Listen to state changes so we can update the vpn status icon
    bitmask.events.register("VPN_STATUS_CHANGED", 'account list update', this.statusEvent)
    this.updateStatus()
  }

  componentWillUnmount() {
    bitmask.events.unregister("VPN_STATUS_CHANGED", 'acconut list update')
  }

  statusEvent() {
    this.updateStatus()
  }

  /*
   * Simple check to update the VPN status icon. We assume that if it's not up or
   * connecting, it's down.
   */
  updateStatus() {
    bitmask.vpn.status().then(
      vpn => {
        this.setState({'activeVpnDomain': vpn.domain})
        if (vpn.status == "on") {
          this.setState({'activeVpnState': "up"})
        } else if (vpn.status == "starting") {
          this.setState({'activeVpnState': "connecting"})
        } else {
          this.setState({'activeVpnState': "down"})
        }
      }
    )
  }

  select(e) {
    let account = this.props.accounts.find(
      account => account.id == e.currentTarget.dataset.id
    )
    if (this.props.onSelect) {
      this.props.onSelect(account)
    }
  }

  add() {
    App.show('wizard')
  }

  remove() {
    this.setState({showRemoveConfirmation: false})
    if (this.props.onRemove) {
      this.props.onRemove(this.props.account)
    }
  }

  askRemove() {
    this.setState({showRemoveConfirmation: true})
  }
  cancelRemove() {
    this.setState({showRemoveConfirmation: false})
  }

  expand() {
    this.setState({mode: 'expanded'})
  }

  collapse() {
    this.setState({mode: 'collapsed'})
  }

  render() {
    let style = {}
    let expandButton = null
    let plusminusButtons = null
    let removeModal = null

    if (this.state.mode == 'expanded') {
      expandButton = (
        <Button onClick={this.collapse} className="expander btn-inverse btn-flat pull-right">
          <Glyphicon glyph="triangle-left" />
        </Button>
      )
      let removeDisabled = !this.props.account || this.props.account.authenticated
      plusminusButtons = (
        <ButtonGroup style={style}>
          <Button onClick={this.add} className="btn-inverse">
            <Glyphicon glyph="plus" />
          </Button>
          <Button disabled={removeDisabled} onClick={this.askRemove} className="btn-inverse">
            <Glyphicon glyph="minus" />
          </Button>
        </ButtonGroup>
      )
    } else {
      style.width = '60px'
      expandButton = (
        <Button onClick={this.expand} className="expander btn-inverse btn-flat pull-right">
          <Glyphicon glyph="triangle-right" />
        </Button>
      )
    }

    if (this.state.showRemoveConfirmation) {
      let domain = this.props.account.domain
      let title = `Are you sure you wish to remove ${domain}?`
      removeModal = (
        <Confirmation title={title} onAccept={this.remove} onCancel={this.cancelRemove} />
      )
    }

    let items = this.props.accounts.map((account, i) => {
      let className = account == this.props.account ? 'active' : 'inactive'
      let icon = null;
      if (account.domain === this.state.activeVpnDomain){
        icon = <Glyphicon glyph="lock" />
      }
      return (
        <li key={i} className={className} onClick={this.select} data-id={account.id}>
          <div className="account-details">
            <span className="username">{account.userpart}</span>
            <span className="domain">{account.domain}</span>
          </div>
          <div className={`vpn-status ${this.state.activeVpnState}`}>
            {icon}
          </div>
          <span className="arc top"></span>
          <span className="arc bottom"></span>
        </li>
      )
    })

    expandButton = null // for now, disable expand  button

    return (
      <div className="accounts" style={style}>
        <AppButtons />
        <ul>
          {items}
        </ul>
        <ButtonToolbar>
          {plusminusButtons}
          {expandButton}
        </ButtonToolbar>
        {removeModal}
      </div>
    )
  }


}
