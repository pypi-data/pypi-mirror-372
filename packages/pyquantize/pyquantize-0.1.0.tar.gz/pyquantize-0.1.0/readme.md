general-purpose quantization. includes [directed rounding](https://en.wikipedia.org/wiki/Rounding#Directed_rounding_to_an_integer), [tie-breaking rounding](https://en.wikipedia.org/wiki/Rounding#Rounding_to_the_nearest_integer), [randomized rounding](https://en.wikipedia.org/wiki/Rounding#Randomized_rounding_to_an_integer), [truncation](https://en.wikipedia.org/wiki/Truncation), [rounding to multiples](https://en.wikipedia.org/wiki/Rounding#Rounding_to_a_specified_multiple), [negative zeroes](https://en.wikipedia.org/wiki/Rounding#Negative_zero_in_meteorology), and a bit more!

# how to install

```shell
pip install pyquantize
```

# how to use

there is only one function in the module: `quantize`  
import it like so:

```python
from pyquantize import quantize

quantize(3.14, 0.8)
# 3.2
```

usage:
```python
quantize(number,
		quantum     = 1,
		offset      = 0,
		centre      = 0,
		threshold   = 0.5,
		directed    = False,
		signed_zero = True,
		mode        = 'even')
```

number: an `int` or a `float` type. no default. the number to be quantized

quantum: an `int` or a `float` type. default is 1. the number will be quantized to multiples of this quantum. `quantize(x, quantum=0.7)` will snap the number to […, -1.4, -0.7, 0, 0.7, 1.4, …]

offset: an `int` or a `float` type. default is 0. the quantization grid will be offset by this amount. `quantize(x, quantum=0.7, offset=0.2)` will change the grid from […, -1.4, -0.7, 0, 0.7, 1.4, …] to […, -1.2, -0.5, 0.2, 0.9, 1.6, …]

centre: an `int` or a `float` type. default is 0. affects `'towards'` and `'away'` modes. `quantize(x, centre=float('inf'), mode='towards')` is the same as `quantize(x, mode='ceil')`. `quantize(x, centre=float('-inf'), mode='towards')` is the same as `quantize(x, mode='floor')`
similarly so for `mode='away'`

threshold an `int` or a `float` type. default is 0.5. must satisfy 0 ≤ threshold ≤ 1. it determines the percentage at which the number is rounded up or down

directed: a `bool` type. default is False. if False, `mode` is only applied for ties (where the number is exactly between multiples of quantum, like 0.5 between 0 and 1). if True, `mode` is *always* applied

signed_zero: a `bool` type. default is True. if True, whenever the result is zero, it shows whether it was rounded from the negative or positive side. for example, -0.1 rounds to -0.0 instead of 0.0. if False, this rounds to 0.0 as usual

mode: a `str` type. default is 'even'. determines the method for quantization. options are:  
`'threshold'` - quantize down if the fractional part is less than threshold  
`'floor'` - quantize down towards -∞  
`'ceil'` - quantize up towards +∞  
`'towards'` - quantize towards centre  
`'away'` - quantize away from centre  
`'even'` - quantize towards nearest even multiple (default)  
`'odd'` - quantize towards nearest odd multiple  
`'alternate'` - quantize up or down alternately according to quantize.alternate_last  
`'random'` - quantize up or down randomly  
`'stochastic'` - quantize up or down according to stochastic probability  

`'alternate'`, `'random'`, `'stochastic'` are [non-deterministic](https://en.wikipedia.org/wiki/Nondeterministic_algorthm)

when mode is `'alternate'`, the last state is remembered as an attribute of the function, which you can access as `quantize.alternate_last` (a bool type)

(this function may occasionally round to unexpected results, due to [floating point imprecision](https://en.wikipedia.org/wiki/Floating-point_arithmetic))

# tidbits 

to simulate rounding, try: 
```python
def qround(number, digits=0, *args, **kwargs):
	return quantize(number, quantum=10**-digits, *args, **kwargs)

print(qround(2.34, 1, directed=True, mode='stochastic'))
# 2.3 or 2.4
```
unlike python's `round`, you can even round a number to a non-integer amount of digits!
```
print(qround(2.34, 1.5))
# 2.2135943621178655
```

to simulate rounded division, try:
```python
def qdivmod(dividend, divisor, *args, **kwargs):
	result = quantize(dividend/divisor, *args, **kwargs)
	return result, dividend-result*divisor

print(qdivmod(2.34, 1, directed=True, mode='stochastic'))
# (1, 1.0) or (2, -0.5)

```
stochastic division! neat huh?? or try even-rounded integer division:

```
print(qdivmod(3, 2, mode='even'))
# (2, -1)
print(qdivmod(4, 2, mode='even'))
# (2, 0)
print(qdivmod(5, 2, mode='even'))
# (2, 1)
```

or check that stochastic mode works:

```python
count = 0
for i in range(10**5):
	count += quantize(0.9, directed=True, mode='stochastic')

print(count/10**5)
# ≈0.9
```

(psst! these functions arent actually defined in pyquantize. just fun little trinkets. or you can ask me if youd like them to be included!)

# how to uninstall

```shell
pip uninstall pyquantize
```

# the end ~
if you can help me port this to other languages, ~~i~~ *the open-source community* would be super grateful! :)  
and if you liked this, please please give me a star it really helps
