import brownie
from brownie import TheIndexToken, TheIndexDao
from brownie import accounts, network, config
from brownie.exceptions import VirtualMachineError
import pytest
from web3 import Web3

INITIAL_SUPPLY = Web3.toWei(10**6, 'ether')


def deploy_infra():
    acc = accounts[0]
    token = TheIndexToken.deploy(INITIAL_SUPPLY, {'from': acc})
    dao = TheIndexDao.deploy(
        token,
        config['networks'][network.show_active()]['fx_child'],
        {'from': acc}
    )
    return token, dao

def test_base_cases():
    token, dao = deploy_infra()
    assert dao.getDerivedCollections() == []
    assert dao.getAuditPendingDerivedCollections() == []
    assert dao.daoToken() == token

@pytest.mark.skip
def test_audit_pending_collections():
    acc = accounts[0]
    token, dao = deploy_infra()
    with brownie.reverts():
        dao.suggestNewCollection(acc, {'from': acc})
        assert False
    assert True

