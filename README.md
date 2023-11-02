# SOLBENCH

To examine the evolution of error handling in the context of Solidity we have developed SOLBENCH. Through SOLBENCH we are able to collect real-world contracts incrementally and analyse them in a well-defined manner.

The `dataset` folder contains a `sample`of 10 real-world smart contracts.
You can find the whole solbench dataset in Dropbox [solbenchdataset](https://www.dropbox.com/scl/fo/syt16map4ucuxbkgzptnq/h?rlkey=z15p3m7scqk5gb0yuwbljywfc&dl=0).

The `src` folder contains the scripts of our tool:
 - `contract_vistor.py` : which takes as input every contract of the sample folder and extract each error-handling feature.
 - `HR.py` : which finds *external calls, function arguments, external contract creation, revert statement-function, division by zero, enum type conversion, overflows/underflows, division by zero*.
 - `fetchdata.py` : the script to collect contracts from etherscan.

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
