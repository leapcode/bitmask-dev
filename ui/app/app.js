import bitmask from 'lib/bitmask'
import Account from 'models/account'
import Provider from 'models/provider'

class Application {
  constructor() {
  }

  //
  // main entry point for the application
  //
  initialize() {
    window.addEventListener("error", this.showError.bind(this))
    window.addEventListener("unhandledrejection", this.showError.bind(this))
    this.start()
  }

  start() {
    Provider.list(false).then(domains => {
      Account.initializeList(domains)
      Account.active().then(account => {
        if (account == null) {
          this.show('greeter')
        } else {
          Account.addPrimary(account)
          this.show('main', {initialAccount: account})
        }
      }, error => {
        this.showError(error)
      })
    }, error => {
      this.showError(error)
    })
  }

  show(panel, properties) {
    this.switcher.show(panel, properties)
  }

  showError(e) {
    this.switcher.showError(e)
    return true
  }

  hideError() {
    this.switcher.hideError()
    return true
  }
}

var App = new Application
export default App