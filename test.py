from blockchain import Blockchain, Transaction, Block
from time import time
import pprint

pp = pprint.PrettyPrinter(indent=4)

blockchain = Blockchain()
transaction = Transaction("Prajwal Diwate", "Shreyas Kalvankar", 10)

blockchain.pendingTransactions.append(transaction)

# transaction  = Transaction("Animish Akadkar", "Atharva Thoke", 200)
#
# blockchain.pendingTransactions.append(transaction)

blockchain.minePendingTransactions("Nang")

pp.pprint(blockchain.chainJSONencode())
print("Length: ", len(blockchain.chain))
