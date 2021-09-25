# bitvavo-dca
Automate your bitvavo transactions. This repo uses the bitvavo API to perform your desired transactions and generate a (simple) performance overview.

## Set up
1. Create an `apikey` and `apisecret` in your bitvavo account. It needs to have at least `gegevens inzien`, `kopen en verkopen` rights.
2. Copy `.env.example` into `.env` and put the `apikey` and `apisecret` in there.
3. Copy `strategy_example.py` into `strategy.py` and set up your desired strategy
4. Create a `.bat` file to run the program (e.g., each month) to perform DCA.

