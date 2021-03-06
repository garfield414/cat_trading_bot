#    Copyright 2017 yiwen song
# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
wallet_api.py

Provides an API to manipulate the cryptokitty wallet.
"""

from cat_trading_bot.exceptions import InsufficientFundsException
from cat_trading_bot.exceptions import KittyNotOwnedException
from cat_trading_bot.cats_abi import SALE_ABI, CORE_ABI, SIRE_ABI
from ethereum import utils
from ethereum.transactions import Transaction
import os
import web3


# CryptoKitty Contract addresses
CAT_CONTRACTS = {
    'sale': {
        'name': 'CryptoKittiesSalesAuction',
        'addr': '0xb1690C08E213a35Ed9bAb7B318DE14420FB57d8C',
        'abi': SALE_ABI,
    },
    'core': {
        'name': 'CryptoKittiesCore',
        'addr': '0x06012c8cf97bead5deae237070f9587f8e7a266d',
        'abi': CORE_ABI,
    },
    'sire': {
        'name': 'CryptoKittiesSiringAuction',
        'addr': '0xC7af99Fe5513eB6710e6D5f44F9989dA40F27F26',
        'abi': SIRE_ABI,
    }
}

def get_cats_contract(contract_type):
    name = CAT_CONTRACTS[contract_type]['name']
    address = CAT_CONTRACTS[contract_type]['addr']
    abi = CAT_CONTRACTS[contract_type]['abi']
    cats_contract = web3.eth.contract(
        address=address,
        name=name,
        abi=abi,
    )
    return cats_contract

class CatWallet():
    def __init__(self, addr=None, key=None):
        if not key:
            key = os.urandom(4096)
        if not addr:
            addr = web3.personal.importRawKey(key)
        self.addr = addr
        self.key = key
        
        
    def send_eth(self, address, amt, data=None, **kwargs):
        """Sends `amt` ethereum to `address` with the `data`
        field attached to it.
        
        If you do not have enough ethereum, raises 
        `InsufficientFundsException`.
        """
        transaction = {
            'from': self.addr,
            'to': address,
            'value': web3.toWei(amt, 'ether'),
            'data': data,
        }
        transaction.update(kwargs)
        return web3.eth.sendTransaction(transaction)
    
    
    def list_sire(self, kitty_id, start_amt, end_amt, duration, **kwargs):
        """Lists a cat to sire."""
        cats_contract = get_cats_contract('core')
        contract_args = kwargs
        contract_args.update({'from': self.addr})
        return cats_contract.transact(contract_args).createSiringAuction(
            kitty_id,
            web3.toWei(start_amt, 'ether'),
            web3.toWei(end_amt, 'ether'),
            duration,
        )
    
    
    def cancel_sire(self, kitty_id, **kwargs):
        """Cancels a siring listing."""
        cats_contract = get_cats_contract('sire')
        contract_args = kwargs
        contract_args.update({'from': self.addr})
        return cats_contract.transact(contract_args).cancelAuction(kitty_id)
    
    
    def purchase_sire(self, kitty_id, sire_id, amt, **kwargs):
        """Makes your cat fuck the other cat."""
        cats_contract = get_cats_contract('core')
        contract_args = kwargs
        contract_args.update({'from': self.addr})
        contract_args.update({'value': web3.toWei(amt, 'ether')})
        return cats_contract.transact(contract_args).bidOnSiringAuction(
            sire_id,
            kitty_id,
        )
    
    
    def give_birth(self, kitty_id, amt, **kwargs):
        """Makes your kitty give birth."""
        cats_contract = get_cats_contract('core')
        contract_args = kwargs
        contract_args.update({'from': self.addr})
        contract_args.update('value': web3.toWei(amt, 'ether'))
        return cats_contract.transact(contract_args).giveBirth(
            kitty_id,
        )
    
    
    def list_kitty(self, kitty_id, start_amt, end_amt, duration, **kwargs):
        """Lists the cat with id `kitty_id` for sale on the
        exchange for `amt`.
        
        If you do not own the cat with that id, raises
        `KittyNotOwnedException`.
        """
        cats_contract = get_cats_contract('core')
        contract_args = kwargs
        contract_args.update({'from': self.addr})
        return cats_contract.transact(contract_args).createSaleAuction(
            kitty_id,
            web3.toWei(start_amt, 'ether'),
            web3.toWei(end_amt, 'ether'),
            duration,
        )
        
        
    def cancel_list(self, kitty_id, **kwargs):
        """Cancels the listing for the cat."""
        cats_contract = get_cats_contract('sale')
        contract_args = kwargs
        contract_args.update({'from': self.addr})
        return cats_contract.transact(contract_args).cancelAuction(kitty_id)
        
    
    def buy_kitty(self, kitty_id, amt, **kwargs):
        """Tries to purchase the cat with id `kitty_id` by
        sending `amt` ether to the CryptoKittiesSaleAuction
        contract address.
        
        If you do not have enough ethereum, raises
        `InsufficientFundsException`.
        """
        cats_contract = get_cats_contract('sale')
        contract_args = kwargs
        contract_args.update({'from': self.addr})
        contract_args.update({'value': web3.toWei(amt, 'ether')})
        return cats_contract.transact(contract_args).bid(kitty_id)
