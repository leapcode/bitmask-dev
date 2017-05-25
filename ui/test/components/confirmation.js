import React from 'react';
import {shallow} from 'enzyme';
import chaiEnzyme from 'chai-enzyme'
import sinon from 'sinon'
import chai, { expect } from 'chai'
import Confirmation from '../../app/components/confirmation';


describe('Confirmation Component', () => {

  it('Passed functionss run on click', () => {
    const onAcceptFuncTest = sinon.spy();
    const onCancelFuncTest = sinon.spy();

    const confirmation = shallow(
      <Confirmation
          onAccept={onAcceptFuncTest}
          onCancel={onCancelFuncTest}
      />
    )

    confirmation.find('Button').at(0).simulate('click')
    expect(onAcceptFuncTest.calledOnce).to.equal(true)
    confirmation.find('Button').at(1).simulate('click')
    expect(onCancelFuncTest.calledOnce).to.equal(true)
  })

  it('sets defaults correctly', () => {
    const confirmation = shallow(
      <Confirmation
          onAccept={() => {}}
          onCancel={() => {}}
      />
    )

    expect(confirmation.find("ModalTitle").first().children()).to.have.text("Are you sure?")
    expect(confirmation.find('Button').at(0).children().first()).to.have.text("Accept")
    expect(confirmation.find('Button').at(1).children().first()).to.have.text("Cancel")
  })

  it('overwrites defaults correctly', () => {
    const onAcceptFuncTest = () => {}
    const onCancelFuncTest = () => {}
    const testTitle = "Test Title"
    const testAcceptStr = "Test accept string"
    const testCancelStr = "Test cancel string"

    const confirmation = shallow(
      <Confirmation
          onAccept={() => {}}
          onCancel={() => {}}
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
