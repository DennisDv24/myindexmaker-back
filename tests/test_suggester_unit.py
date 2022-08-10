from brownie import NewCollectionSuggester, TestCollection
from brownie import accounts, config, network
import pytest

def test_is_721():
    acc = accounts[0]
    net = network.show_active()
    collection = TestCollection.deploy({'from': acc})
    suggester = NewCollectionSuggester.deploy(
        config['networks'][net]['checkpoint_manager'],
        config['networks'][net]['fx_root'],
        {'from': acc}
    )
    assert suggester.isERC721(collection)
    with pytest.raises(Exception):
        suggester.isERC721(suggester)
    with pytest.raises(Exception):
        suggester.isERC721(acc)

