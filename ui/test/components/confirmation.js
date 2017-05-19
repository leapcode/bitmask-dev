import React from 'react';
import {shallow} from 'enzyme';
import chaiEnzyme from 'chai-enzyme'
import Confirmation from '../../app/components/confirmation';
import chai, { expect } from 'chai'


describe('Confirmation Component', () => {

  const simpleFunction0 = () => {return 0}
  const simpleFunction1 = () => {return 1}

  it('Passed functionss run on click', () => {
    const confirmation = shallow(
      <Confirmation
          onAccept={simpleFunction0}
          onCancel={simpleFunction1}
      />
    )

    expect(confirmation.find('Button').get(0).props.onClick()).to.equal(simpleFunction0())
    expect(confirmation.find('Button').get(1).props.onClick()).to.equal(simpleFunction1())
  })

  it('sets defaults correctly', () => {
    const confirmation = shallow(
      <Confirmation
          onAccept={simpleFunction0}
          onCancel={simpleFunction1}
      />
    )

    expect(confirmation.find("ModalTitle").first().children()).to.have.text("Are you sure?")
    expect(confirmation.find('Button').at(0).children().first()).to.have.text("Accept")
    expect(confirmation.find('Button').at(1).children().first()).to.have.text("Cancel")
  })

  it('overwrites defaults correctly', () => {
    const testTitle = "Test Title"
    const testAcceptStr = "Test accept string"
    const testCancelStr = "Test cancel string"

    const confirmation = shallow(
      <Confirmation
          onAccept={simpleFunction0}
          onCancel={simpleFunction1}
          title={testTitle}
          acceptStr={testAcceptStr}
          cancelStr={testCancelStr}
      />
    )

    expect(confirmation.find("ModalTitle").first().children()).to.have.text(testTitle)
    expect(confirmation.find('Button').at(0).children().first()).to.have.text(testAcceptStr)
    expect(confirmation.find('Button').at(1).children().first()).to.have.text(testCancelStr)
  })
})
