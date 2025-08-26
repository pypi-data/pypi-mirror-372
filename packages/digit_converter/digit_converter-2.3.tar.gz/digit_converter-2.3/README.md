# digit_converter

A useful tool for digit conversion, applicable in Genetic Algorithms (GA). It transforms a number into a list of digits under any base, for example, `[1, 0, 1, 0, 1, 1, 1, 0] <-> 174`. 🔢

## Abstract

A cool tool for digits converting. It transforms a number to a list and verse vice, such as represent a number by a binary list.
It could be applied in GA.

**Keywords** Converter, Digits

## Classes and Objects

Classes:
```
    BaseConverter: 
        .tonumber(lst), .tolist(num, L)
        
    DigitConverter:
    BinaryConverter: subclass of DigitConverter
    IntervalConverter
```
Objects:
```
    colorConverter: instance of BinaryConverter
    unitIntervalConverter: instance of IntervalConverter  == IntervalConverter(lb=0, ub=1)
```

## Grammar
Install the lib, by `pip install digit_converter`

### Import

```python
import digit_converter
```

### Basic usage

```pyhon
print('=*= Example 1 =*=')
print(f'color-converter: {colorConverter.tonumber([1,0,1,0,1,1,1,0])}<->{colorConverter.tolist(174)}')

print('=*= Example 2 =*=')
c = BinaryConverter(exponent=3)
d = c.tolist(12.223, L=8)
print(f'binary-converter: {d}<->{c.tonumber(d)}={c.pretty(d)}')
i, f = c.seperate(12.223, L=8)
print(f'integer part: {i}, fractional part: {f}')

print('=*= Example 3 =*=')
c = IntervalConverter(lb=0, ub=10)
d = c.tolist(2.4, L=8)
print(f'[{c.lb},{c.ub}]-converter: {d}<->{c(d)} -> {c.pretty(d)}-th number')

print('=*= Example 4 =*=')
c = DigitConverter(base=16)
d = c.tolist(2.4, L=8)
print(f'16-converter: {d}<->{c(d)}={c.pretty(d)}')
```

OUTPUT::

    =*= Example 1 =*=
    color-converter: 174<->[1, 0, 1, 0, 1, 1, 1, 0]
    =*= Example 2 =*=
    binary-converter: [1, 1, 0, 0, 0, 0, 1, 1]<->12.1875=2^{3} + 2^{2} + 2^{-3} + 2^{-4}
    integer part: [1, 1, 0, 0], fractional part: [0, 0, 1, 1]
    =*= Example 3 =*=
    [0,10]-converter: [0, 0, 1, 1, 1, 1, 0, 1]<->2.3828125 -> 2^{5} + 2^{4} + 2^{3} + 2^{2} + 2^{0}-th number
    =*= Example 4 =*=
    16-converter: [0, 2, 6, 6, 6, 6, 6, 6]<->2.399999976158142=2*16^{0} + 6*16^{-1} + 6*16^{-2} + 6*16^{-3} + 6*16^{-4} + 6*16^{-5} + 6*16^{-6}

