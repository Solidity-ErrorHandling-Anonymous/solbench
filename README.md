# SOLBENCH

To examine the evolution of error handling in the context of Solidity we have developed SOLBENCH. Through SOLBENCH we are able to collect real-world contracts incrementally and analyse them in a well-defined manner.

The `dataset` folder contains a `sample`of 10 real-world smart contracts.
You can find the whole solbench dataset in Dropbox [solbenchdataset](https://www.dropbox.com/scl/fo/syt16map4ucuxbkgzptnq/h?rlkey=z15p3m7scqk5gb0yuwbljywfc&dl=0). To decompress the dataset use the following commands:

```
# Install lz4
$ sudo apt-get install lz4

# Decompress a lz4 compressed file
$ lz4 -d datasol.tar.lz4
```

The `src` folder contains the scripts of our tool:
 - `delete_comments.py` : delete comments from smart contract's source code
 - `contract_vistor.py` : which takes as input every contract of the sample folder and extract each error-handling feature.
 - `HR.py` : which finds *external calls, function arguments, external contract creation, revert statement-function, division by zero, enum type conversion, overflows/underflows, division by zero*.
 - `fetchdata.py` : the script to collect contracts from etherscan.
 - `ast_detector.py` : produce the AST of the smart contract and find Error Handling instances.

Note that the scripts take as input the the contracts from the `sample` folder.

The output of `contract_visitor.py` is a JSON file with error-handling features and informations abou them.
The output of `HR.py` is the patterns that contains the usages described above.

To run the Contract Visitor script, use the following command:
```
$ python3 contract_visitor.py
```

To run the HeuristiRules script run the command:
```
$ python3 HR.py
```

To run the Error Messages detector script run the command:
```
$ python eh_messages.py --directory ./dataset/sample
```

To run the SMTChecker detector for a file run the command:
```
$ python3 smtchecker_found.py --file ./dataset/sample/0xfd1d97f0d8b100a9df095b40a13520af13df7ec1.sol
```
