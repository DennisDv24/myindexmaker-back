import brownie
from brownie import TheIndexToken, AuditingDao, TestCollection
from brownie import accounts, network, config
from brownie.exceptions import VirtualMachineError
import pytest
from web3 import Web3

INITIAL_SUPPLY = Web3.toWei(10**6, 'ether')

deploy_token = lambda _from: TheIndexToken.deploy(
    INITIAL_SUPPLY, {'from': _from}
)

deploy_dao = lambda _from, token: AuditingDao.deploy(
    token,
    config['networks'][network.show_active()]['fx_child'],
    {'from': _from}
)

def deploy_infra(acc = None):
    if not acc: acc = accounts[0]
    token = deploy_token(acc)
    dao = deploy_dao(acc, token)
    return token, dao

def test_base_cases():
    token, dao = deploy_infra()
    assert dao.getDerivedCollections() == []
    assert dao.getAuditPendingDerivedCollections() == []
    assert dao.daoToken() == token

def test_voting_power():
    acc = accounts[0]
    extra_acc = accounts[1]
    token, dao = deploy_infra(acc)
    assert dao.votingPowerOf(acc) == INITIAL_SUPPLY
    token.transfer(extra_acc, 1, {'from': acc})
    assert dao.votingPowerOf(extra_acc) == 1
    assert dao.votingPowerOf(acc) == INITIAL_SUPPLY - 1

def test_suggest_new_collection():
    acc = accounts[0]
    token, dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    dao.suggestNewCollection(test_colle)
    assert dao.getAuditPendingDerivedCollections() == [test_colle]

def test_audit_voting():
    acc = accounts[0]
    extra_acc = accounts[1]
    token, dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    dao.suggestNewCollection(test_colle)
    assert dao.canVoteOn(acc, test_colle)
