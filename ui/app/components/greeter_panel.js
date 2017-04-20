import React from 'react'
import Login from './login'
import Center from './center'
import Splash from './splash'
import Area from './area'
import { Glyphicon, Button, ButtonToolbar } from 'react-bootstrap'
import App from 'app'

export default class GreeterPanel extends React.Component {

  constructor(props) {
    super(props)
  }

  newAccount() {
    App.show('wizard')
  }

  onLogin(account) {
    App.start()
  }

  quit() {
    App.show('bye_splash')
  }

  render () {
    return <div>
      <Splash speed="slow" mask={false} />
      <Center width="400">
        <Area position="top" type="light" className="greeter">
          <Login onLogin={this.onLogin.bind(this)}
            rememberAllowed={false} autoAllowed={true} />
        </Area>
        <Area position="bottom" type="dark" className="greeter">
          <ButtonToolbar>
            <Button onClick={this.quit.bind(this)} className="pull-right">
              <Glyphicon glyph="off" />
            </Button>
            <Button onClick={this.newAccount.bind(this)}>
              <Glyphicon glyph="user" /> New account...
            </Button>
          </ButtonToolbar>
        </Area>
      </Center>
    </div>
  }
}
