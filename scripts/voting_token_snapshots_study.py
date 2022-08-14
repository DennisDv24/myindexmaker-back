import brownie
from brownie import TheIndexToken, AuditingDao, TestCollection
from brownie import accounts, network, config
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

def show_blocks_for_infra():
    acc = accounts[0]
    extra_acc = accounts[1]
    token, audit_dao = deploy_infra(acc)
    test_colle = TestCollection.deploy({'from': acc})
    tx = audit_dao.suggestNewCollection(test_colle, {'from': acc})
    tx.wait(1)
    print('Block for new suggestion:')
    print(audit_dao.votationStartForCollection(test_colle))
    print('Voting power for that block:')
    print(audit_dao.votingPowerFor(test_colle, {'from': acc}))

def main():
    show_blocks_for_infra()
