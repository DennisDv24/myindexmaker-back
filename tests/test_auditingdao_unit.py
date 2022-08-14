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

deploy_auditing_dao = lambda _from, token: AuditingDao.deploy(
    token,
    config['networks'][network.show_active()]['fx_child'],
    {'from': _from}
)

def deploy_infra(acc = None):
    if not acc: acc = accounts[0]
    token = deploy_token(acc)
    audit_dao = deploy_auditing_dao(acc, token)
    return token, audit_dao

def test_base_cases():
    token, audit_dao = deploy_infra()
    assert audit_dao.getAuditPendingDerivedCollections() == []
    assert audit_dao.daoToken == token
    assert audit_dao.theIndexDao() == brownie.ZERO_ADDRESS

@pytest.mark.skip()
def test_voting_power():
    acc = accounts[0]
    extra_acc = accounts[1]
    token, audit_dao = deploy_infra(acc)
    assert audit_dao.votingPowerOf(acc) == INITIAL_SUPPLY
    token.transfer(extra_acc, 1, {'from': acc})
    assert audit_dao.votingPowerOf(extra_acc) == 1
    assert audit_dao.votingPowerOf(acc) == INITIAL_SUPPLY - 1

@pytest.mark.skip()
def test_suggest_new_collection():
    acc = accounts[0]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    assert audit_dao.getAuditPendingDerivedCollections() == [test_colle]

@pytest.mark.skip()
def test_audit_can_vote():
    acc = accounts[0]
    extra_acc = accounts[1]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    assert audit_dao.canVote(acc, test_colle)
    assert not audit_dao.canVote(extra_acc, test_colle)

@pytest.mark.skip()
def test_audit_vote():
    acc = accounts[0]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    audit_dao.submitAuditForCollection(test_colle, True, {'from': acc})
    assert audit_dao.getVotesFor(test_colle) == (token.balanceOf(acc), 0)

@pytest.mark.skip()
def test_cant_vote_twice():
    acc = accounts[0]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    audit_dao.submitAuditForCollection(test_colle, True, {'from': acc})
    audit_dao.getVotesFor(test_colle) == (token.balanceOf(acc), 0)
    with brownie.reverts():
        audit_dao.submitAuditForCollection(test_colle, True, {'from': acc})
        assert False
    assert True

@pytest.mark.skip()
def test_tries_to_vote():
    acc = accounts[0]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    with brownie.reverts():
        audit_dao.submitAuditForCollection(
            test_colle, False, {'from': accounts[1]}
        )
        assert False
    assert True

@pytest.mark.skip()
def test_multiple_votes():
    acc0, acc1, acc2 = accounts[0], accounts[1], accounts[2]
    token, audit_dao = deploy_infra(acc0)
    test_colle = TestCollection.deploy({'from': acc0})
    audit_dao.suggestNewCollection(test_colle)
    bal1 = INITIAL_SUPPLY/2
    bal2 = INITIAL_SUPPLY/4
    bal0 = INITIAL_SUPPLY - bal1 - bal2
    token.transfer(acc1, bal1, {'from': acc0})
    token.transfer(acc2, bal2, {'from': acc0})
    audit_dao.submitAuditForCollection(test_colle, False, {'from': acc0})
    audit_dao.submitAuditForCollection(test_colle, True, {'from': acc1})
    audit_dao.submitAuditForCollection(test_colle, False, {'from': acc2})
    assert audit_dao.getVotesFor(test_colle) == (bal1, bal0 + bal2)

# TODO FIXME
@pytest.mark.skip()
def test_voting_twice_different_wallets():
    acc, extra_acc = accounts[0], accounts[1]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)

    initial_bal = token.balanceOf(acc)
    audit_dao.submitAuditForCollection(test_colle, True, {'from': acc})
    token.transfer(extra_acc, extra_acc, {'from': acc})
    audit_dao.submitAuditForCollection(test_colle, True, {'from': extra_acc})
    proVotes, againstVotes = audit_dao.getVotesFor(test_colle)
    assert proVotes + againstVotes < INITIAL_SUPPLY
    assert proVotes + againstVotes == initial_bal



