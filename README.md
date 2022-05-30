This is a python code to bootstrap the OIS discount factors/zero rates from OIS market quotes. OIS quotes for the EUR market refer to the EUR STR rates, and those for the USD market to the USD SOFR rates.

The bootstrapped zero rates/discount factors could then used for Swap valuations or for Proceeds XCCY Swap valuations.

How to use the files?<br> <br>
All source codes are stored in the src folder, and the sample input file contains the market quotes from Bloomberg. The following fields for the bonds need to be input by the user to get a IRR, which is the yield after hedging with Cross Currency Basis Swaps.

<ul>
  <li> Coupon rate
  <li> Coupon Frequency
  <li> Next Coupon Date
   <li> Workout Date
   <li> Trading Price
      
</ul>

<br>
How to run?
<br>

```bash
cd src
python -m main.py
```

