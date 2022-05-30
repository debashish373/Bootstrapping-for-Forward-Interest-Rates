This is a python code to bootstrap the OIS discount factors/zero rates from OIS market quotes. OIS quotes for the EUR market refer to the EUR STR rates, and those for the USD market to the USD SOFR rates.

The bootstrapped zero rates/discount factors could then used for Swap valuations or for Proceeds XCCY Swap valuations.

How to use the files?<br> <br>
All source codes are stored in the src folder, and the sample input file contains the market quotes from Bloomberg. The following fields for the bonds can be user input to get a IRR, which is the yield after hedging with Cross Currency Basis Swaps.


