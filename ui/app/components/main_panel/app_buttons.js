import React from 'react'
import {Modal, Button, ButtonGroup, ButtonToolbar, Glyphicon} from 'react-bootstrap'

import App from 'app'
import Splash from 'components/splash'
import bitmask from 'lib/bitmask'

export default class AppButtons extends React.Component {

  static get defaultProps() {return{
  }}

  constructor(props) {
    super(props)

    this.state = {
      showAbout: false,
      version: null
    }

    // prebind:
    this.showAbout     = this.showAbout.bind(this)
    this.hideAbout     = this.hideAbout.bind(this)
    this.quit          = this.quit.bind(this)
    this.openBugReport = this.openBugReport.bind(this)
    this.openDonate    = this.openDonate.bind(this)
    this.openCode      = this.openCode.bind(this)
  }

  showAbout() {
    bitmask.core.version().then(result => {
      this.setState({version: result.version_core})
    })
    this.setState({showAbout: true})
  }

  hideAbout() {
    this.setState({showAbout: false})
  }

  quit() {
    App.show('bye_splash')
  }

  openURL(url) {
    if (typeof(bitmaskApp) == 'undefined') {
      window.open(url)
    } else {
      bitmaskApp.openSystemBrowser(url)
    }
  }

  openBugReport() { this.openURL('https://0xacab.org/leap/bitmask-dev') }
  openDonate()    { this.openURL('https://leap.se/donate') }
  openCode()      { this.openURL('https://leap.se/source') }

  render() {
    let style = {}
    let quitButton = null
    let aboutButton = null
    let aboutModal = null

    quitButton = (
      <Button onClick={this.quit} className="btn-inverse">
        <Glyphicon glyph="off" />
      </Button>
    )

    aboutButton = (
      <Button onClick={this.showAbout} className="btn-inverse">
        <Glyphicon glyph="info-sign" />
      </Button>
    )

    if (this.state.showAbout) {
      aboutModal = (
        <Modal show={true} onHide={this.hideAbout}>
          <Splash speed="fast" mask={true} fullscreen={false} />
          <Modal.Body>
            <h2><b>Bitmask</b></h2>
            <p>
            Bitmask Desktop Client, Version {this.state.version}
            </p>
            <p>
              Bitmask is Free Software, released under the GNU General Public License, version 3.<br/>
              Copyright 2017 LEAP Encryption Access Project.
            </p>
            <p>
              The Bitmask application is lovingly hand-crafted by developers
              all over the world. Development is principally sponsored by the
              LEAP Encryption Access Project, an organization dedicated to
              defending the fundamental right to whisper.
            </p>
            <ButtonToolbar>
              <Button onClick={this.hideAbout}>
                <Glyphicon glyph="remove" /> Close
              </Button>
              <Button onClick={this.openBugReport}>
                <Glyphicon glyph="alert" /> Report Bug
              </Button>
              <Button onClick={this.openDonate}>
                <Glyphicon glyph="heart" /> Donate
              </Button>
              <Button onClick={this.openCode}>
                <Glyphicon glyph="circle-arrow-down" /> Clone Source
              </Button>
            </ButtonToolbar>
          </Modal.Body>
        </Modal>
      )
    }

    return (
      <ButtonToolbar className="app-buttons">
        {quitButton}
        {aboutButton}
        {aboutModal}
      </ButtonToolbar>
    )
  }


}
