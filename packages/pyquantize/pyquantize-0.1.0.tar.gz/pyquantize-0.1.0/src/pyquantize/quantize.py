from typing import Literal, Union
from math import floor, ceil, copysign, isinf, isnan
from random import random, randint

def quantize(
		number     :Union[int,float],
		quantum    :Union[int,float] = 1,
		offset     :Union[int,float] = 0,
		centre     :Union[int,float] = 0,
		threshold  :Union[int,float] = 0.5,
		directed   :bool             = False,
		signed_zero:bool             = True,
		mode       :str              = 'even',
		) -> Union[int,float]:
	"""quantize a number to a grid of multiples.

	Parameters
	----------
	number : int or float
		The number to quantize.
	quantum : int or float, default=1
		The number will be quantized to multiples of this.
	offset : int or float, default=0
		The grid will be shifted by this amount.
	centre : int or float, default=0
		(see 'towards' and 'away' modes)
	threshold : int or float, default=0.5
		Threshold at which the number is rounded up or down. must satisfy 0 ≤ threshold ≤ 1.
	directed : bool, default=False
		Forces quantization mode, even if not tied.
	signed_zero: bool, default=True
		If True, -0.1 rounds to -0.0 instead of 0.0, for example
	mode : {'threshold','floor','ceil','towards','away','even','odd','alternate','random','stochastic'}, default='even'
		Quantization method. options are:
		'threshold'  → quantize down if the fractional part is less than threshold
		'floor'      → quantize down towards -∞
		'ceil'       → quantize up towards +∞
		'towards'    → quantize towards centre
		'away'       → quantize away from centre
		'even'       → quantize towards nearest even multiple (default)
		'odd'        → quantize towards nearest odd multiple
		'alternate'  → quantize up or down alternately according to quantize.alternate_last
		'random'     → quantize up or down randomly
		'stochastic' → quantize up or down according to stochastic probability

	Returns
	-------
	int or float
		The quantized value.

	Raises
	------
	ValueError
		If mode is not recognized, or if mode='stochastic' and directed=False

	Examples
	--------
	>>> quantize(3.14, 0.5, directed=True, mode='stochastic')
	3 # or occasionally 3.5
	>>> quantize(3.7, quantum=1)
	4
	>>> quantize(3.7, quantum=2, mode='floor')
	2

	Notes
	-----
	The function keeps track of state when using mode='alternate' via the attribute quantize.alternate_last (bool)
	"""
	if isinf(number) or isnan(number):
		return number

	if mode == 'stochastic' and not directed:
		raise ValueError(f"mode={mode} requires directed={True}")

	number_scaled = (number-offset) / quantum # the number is now scaled to the grid

	index_lower = floor(number_scaled)    # index of lower nearest grid point
	index_upper =  ceil(number_scaled)    # index of upper nearest grid point
	frac = number_scaled - index_lower    # fractional part, on the grid

	multiple_lower = quantum*index_lower + offset
	multiple_upper = quantum*index_upper + offset

	is_tied:bool = number_scaled % 1 == 0.5  # equally distant from multiple_lower and multiple_upper

	if not directed and not is_tied:
		result = multiple_lower if frac < threshold else multiple_upper
	else:
		if mode == 'threshold':
			result = multiple_lower if frac < threshold else multiple_upper
		elif mode == 'floor':
			result = multiple_lower
		elif mode == 'ceil':
			result = multiple_upper
		elif mode == 'towards':
			result = multiple_lower if abs(multiple_lower-centre) < abs(multiple_upper-centre) else multiple_upper
		elif mode == 'away':
			result = multiple_upper if abs(multiple_lower-centre) < abs(multiple_upper-centre) else multiple_lower
		elif mode == 'even':
			result = multiple_upper if index_upper % 2 == 0 else multiple_lower
		elif mode == 'odd':
			result = multiple_lower if index_upper % 2 == 0 else multiple_upper
		elif mode == 'alternate':
			quantize.alternate_last = not quantize.alternate_last
			result = multiple_lower if quantize.alternate_last else multiple_upper
		elif mode == 'random':
			result = multiple_lower if randint(0, 1) else multiple_upper
		elif mode == 'stochastic':
			result = multiple_upper if random() < frac else multiple_lower
		else:
			raise ValueError("invalid mode. must be one of {'threshold','floor','ceil','towards','away','even','odd','alternate','random','stochastic'}")
	
	if signed_zero and result == 0:
		result = copysign(0.0, number)
	
	return result

quantize.alternate_last = False
