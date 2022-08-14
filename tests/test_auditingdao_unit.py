import brownie
from brownie import TheIndexToken, AuditingDao, TestCollection
from brownie import accounts, network, config, chain
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
    assert audit_dao.daoToken() == token
    assert audit_dao.theIndexDao() == brownie.ZERO_ADDRESS

def test_suggest_first_collection():
    acc = accounts[0]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    assert audit_dao.getAuditPendingDerivedCollections() == [test_colle]

def test_suggest_new_collection():
    acc = accounts[0]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle, {'from': acc})
    assert audit_dao.getAuditPendingDerivedCollections() == [test_colle]
    test_colle2 = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle2, {'from': acc})
    assert audit_dao.getAuditPendingDerivedCollections() == [
        test_colle, test_colle2
    ]

def test_voting_power():
    acc = accounts[0]
    extra_acc = accounts[1]
    token, audit_dao = deploy_infra(acc)

    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle, {'from': acc})
    chain.mine(1)

    voting_power = audit_dao.votingPowerFor(test_colle, {'from': acc})
    expected_voting_power = INITIAL_SUPPLY
    assert voting_power == expected_voting_power

def test_multiple_voting_power():
    acc = accounts[0]
    extra_acc = accounts[1]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})

    expected_extra_acc_voting_power = 1
    expected_acc_voting_power = (
        INITIAL_SUPPLY - expected_extra_acc_voting_power
    )
    token.transfer(extra_acc, 1, {'from': acc})  
    audit_dao.suggestNewCollection(test_colle, {'from': acc})
    chain.mine(1)

    acc_power = audit_dao.votingPowerFor(test_colle, {'from': acc})
    extra_acc_power = audit_dao.votingPowerFor(test_colle, {'from': extra_acc})
    assert acc_power == expected_acc_voting_power
    assert extra_acc_power == expected_extra_acc_voting_power

def test_audit_vote():
    acc = accounts[0]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    audit_dao.submitAuditForCollection(test_colle, True, {'from': acc})
    assert audit_dao.getVotesFor(test_colle) == (token.balanceOf(acc), 0)

def test_multiple_votes_same_wallet():
    acc = accounts[0]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    audit_dao.submitAuditForCollection(test_colle, True, {'from': acc})
    with brownie.reverts():
        audit_dao.submitAuditForCollection(test_colle, True, {'from': acc})
        assert False
    assert True
    
def test_audit_can_vote():
    acc = accounts[0]
    extra_acc = accounts[1]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    chain.mine(1)
    assert audit_dao.canVote(acc, test_colle)
    assert not audit_dao.canVote(extra_acc, test_colle)

def test_tries_to_vote():
    acc = accounts[0]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    chain.mine(1)
    with brownie.reverts():
        audit_dao.submitAuditForCollection(
            test_colle, False, {'from': accounts[1]}
        )
        assert False
    assert True

def test_multiple_votes():
    acc0, acc1, acc2 = accounts[0], accounts[1], accounts[2]
    token, audit_dao = deploy_infra(acc0)
    test_colle = TestCollection.deploy({'from': acc0})

    bal1 = INITIAL_SUPPLY/2
    bal2 = INITIAL_SUPPLY/4
    bal0 = INITIAL_SUPPLY - bal1 - bal2

    token.transfer(acc1, bal1, {'from': acc0})
    token.transfer(acc2, bal2, {'from': acc0})

    audit_dao.suggestNewCollection(test_colle)
    chain.mine(1)

    audit_dao.submitAuditForCollection(test_colle, False, {'from': acc0})
    audit_dao.submitAuditForCollection(test_colle, True, {'from': acc1})
    audit_dao.submitAuditForCollection(test_colle, False, {'from': acc2})
    assert audit_dao.getVotesFor(test_colle) == (bal1, bal0 + bal2)

def test_voting_twice_different_wallets():
    acc, extra_acc = accounts[0], accounts[1]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle)
    chain.mine(1)

    initial_bal = token.balanceOf(acc)
    audit_dao.submitAuditForCollection(test_colle, True, {'from': acc})
    token.transfer(extra_acc, initial_bal, {'from': acc})

    with brownie.reverts(): 
        audit_dao.submitAuditForCollection(test_colle, True, {'from': extra_acc})
        assert False
    assert True

    proVotes, againstVotes = audit_dao.getVotesFor(test_colle)
    assert proVotes + againstVotes <= INITIAL_SUPPLY
    assert proVotes + againstVotes == initial_bal

def test_voting_power_flow():
    acc, extra_acc = accounts[0], accounts[1]
    token, audit_dao = deploy_infra(acc)
    chain.mine(1)

    full_supply_block = chain.height
    assert token.balanceOf(acc) == token.getVotes(acc)
    transfered_amount = 666
    token.transfer(extra_acc, transfered_amount, {'from': acc})
    chain.mine(1)

    post_transfer_block = chain.height
    assert token.balanceOf(acc) == token.getVotes(acc)
    assert token.balanceOf(extra_acc) == token.getVotes(extra_acc)
    assert INITIAL_SUPPLY == token.getPastVotes(acc, full_supply_block)
    assert 0 == token.getPastVotes(extra_acc, full_supply_block)
    
    post_transfer_amount = 665
    token.transfer(acc, post_transfer_amount, {'from': extra_acc}) 
    chain.mine(1)
    assert INITIAL_SUPPLY - transfered_amount == token.getPastVotes(
        acc, post_transfer_block
    )
    assert transfered_amount == token.getPastVotes(extra_acc, post_transfer_block)
    assert token.balanceOf(acc) == token.getVotes(acc)
    assert token.balanceOf(extra_acc) == token.getVotes(extra_acc)


