//
// The main panel manages the current account and the list of available accounts
//
// It displays multiple sections, one for each service.
//

import React from 'react'
import App from 'app'
import Login from 'components/login'
import Account from 'models/account'
import Spinner from 'components/spinner'

import './main_panel.less'
import AccountList from './account_list'
import UserSection from './user_section'
import EmailSection from './email_section'
import VPNSection from './vpn_section'

export default class MainPanel extends React.Component {

  static get defaultProps() {return{
    initialAccount: null
  }}

  constructor(props) {
    super(props)
    this.state = {
      account: null,
      provider: null,
      accounts: []
    }
    this.activateAccount = this.activateAccount.bind(this)
    this.removeAccount = this.removeAccount.bind(this)
  }

  componentWillMount() {
    if (this.props.initialAccount) {
      this.activateAccount(this.props.initialAccount)
    }
  }

  activateAccount(account) {
    account.getProvider().then(provider => {
      this.setState({
        account: account,
        provider: provider,
        accounts: Account.list
      })
    })
  }

  removeAccount(account) {
    Account.remove(account).then(
      newActiveAccount => {
        if (newActiveAccount == null) {
          App.start()
        } else {
          this.activateAccount(newActiveAccount)
        }
      },
      error => {
        console.log(error)
      }
    )
  }

  render() {
    if (this.state.account && this.state.provider) {
      return this.renderPanel()
    } else {
      return <div className="main-panel">
      </div>
    }
  }

  renderPanel() {
    let emailSection = null
    let vpnSection = null
    let sidePanel = null

    if (this.state.account.authenticated) {
      if (this.state.provider.hasEmail) {
        emailSection = <EmailSection account={this.state.account} />
      }
    }

    if (this.state.provider.hasVPN) {
      vpnSection = <VPNSection account={this.state.account} />
    }

    sidePanel = (
      <AccountList account={this.state.account}
        accounts={this.state.accounts}
        onSelect={this.activateAccount}
        onRemove={this.removeAccount}/>
    )

    return (
      <div className="main-panel">
        {sidePanel}
        <div className="body">
          <UserSection account={this.state.account} onLogin={this.activateAccount} onLogout={this.activateAccount}/>
          {vpnSection}
          {emailSection}
        </div>
      </div>
    )
  }

}
