# pythagore

allows you to solve the Pythagorean theorem in Python

## ✨ Features

- Calculate the hypotenuse from the two adjacent sides (`a` and `b`)
- Calculate a missing side if the hypotenuse and another side are known
- Check if a triangle is a right triangle by applying the Pythagorean theorem

## 🔧 Installation

You can install this module with `pip`:

```bash
pip install pythagore
```

## 🚀 Utilisation
Here is an example of using the module :

```python
from pythagore import Pythagore

pythagore = Pythagore()

a = 3
b = 4
hypotenuse = pythagore.hypotenus(a,b) # hypotenus 

if pythagore.is_rectangle(hypotenuse, a, b) == True:
    print("the triangle is indeed right-angled according to the Pythagorean theorem")
else:
    print("the triangle is not a right triangle")

find_missing_side = pythagore.adjacent_side(hypotenuse, a) # 4
if find_missing_side == b:
    print(f"the missing side is b its value and : {find_missing_side}")

print()

print(f"hypotenus : {hypotenuse}\ncoter_a : {a}\ncote_b : {b}")
```

## ❗ Prerequisites

- Python >= 3.13.0

📄 Licence

This project is distributed under the MIT License.
See the LICENSE file for more information.
[LICENSE](./LICENSE)