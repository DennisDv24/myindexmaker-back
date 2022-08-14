import brownie
from brownie import TheIndexToken, AuditingDao, TestCollection
from brownie import accounts, network, config, chain
from brownie.exceptions import VirtualMachineError
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

def try_delegation_post_suggestion():
    acc = accounts[0]
    extra_acc = accounts[1]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    audit_dao.suggestNewCollection(test_colle, {'from': acc})
    chain.mine(1)
    print('Voting power without delegating:')
    print(audit_dao.votingPowerFor(test_colle, {'from': acc}))
    token.delegate(acc, {'from': acc})
    print('Voting power after delegating:')
    print(audit_dao.votingPowerFor(test_colle, {'from': acc}))
    print('So basically you need to delegate before anything')

def delegation():
    acc = accounts[0]
    extra_acc = accounts[1]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    token.delegate(acc, {'from': acc})
    audit_dao.suggestNewCollection(test_colle, {'from': acc})
    chain.mine(1)
    print('Voting power:')
    print(audit_dao.votingPowerFor(test_colle, {'from': acc}))

def main():
    try_delegation_post_suggestion()
