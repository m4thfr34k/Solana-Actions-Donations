# Actions Donation example using Python 

* Demonstrates creation of an action using Python and a platform such as Pipedream

## Installation

* Create account on [Pipedream](https://pipedream.com/)
* Create a new project on Pipedream
* Create a new workflow within the project
  * Your workflow will consist of three parts:
    * http trigger
    * Python code
    * http response
* In Python update the:
  * RECEIVE_ACCOUNT
  * BASE_URL - The is the url of the http trigger
  * action_response
* In the workflow variables, add a new project variable named RPC_PROTECTED. This will be set to your RPC provider. I use the Helius' Secure RPC URL for this.


## TODO

* In-depth guide demonstrating the full setup from start to finish


## References / Tools
* [Actions and Blinks](https://docs.dialect.to/documentation)
* [Solana Py](https://github.com/michaelhly/solana-py/)
* [Solders](https://github.com/kevinheavey/solders)
