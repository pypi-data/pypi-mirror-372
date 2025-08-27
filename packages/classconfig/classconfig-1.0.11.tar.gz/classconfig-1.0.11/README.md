# classconfig
Package for creating (yaml) configuration files automatically and loading objects from those configuration files.

## Installation
You can install it using pip:

    pip install classconfig

## Usage
At first we need a class that is configurable it means that it has `ConfigurableAttribute` class members. Such as
`ConfigurableValue` or `ConfigurableFactory`. Let's create two simple classes where one of them will have the other 
instance as a member:

```python
from classconfig import ConfigurableValue, ConfigurableFactory, ConfigurableMixin


class Inventory(ConfigurableMixin):
    size: int = ConfigurableValue(desc="Size of an inventory", user_default=10, validator=lambda x: x > 0)


class Character(ConfigurableMixin):
    lvl: int = ConfigurableValue(desc="Level of a character", user_default=1, validator=lambda x: x > 0)
    name: str = ConfigurableValue(desc="Name of a character")
    inventory: Inventory = ConfigurableFactory(desc="Character's inventory", cls_type=Inventory)

```

You can see that the usage is similar to dataclasses as it also uses descriptors. You can omit the `ConfigurableMixin`
inheritance but then you will have to write your own `__init__` method e.g.:

```python
class Inventory:
    size: int = ConfigurableValue(desc="Size of an inventory", user_default=10, validator=lambda x: x > 0)

    def __init__(self, size: int):
        self.size = size
```

### Creating configuration file
Now let's create a configuration file for our `Character` class. You can do it by calling `save` method of `Config` class:

```python
from classconfig import Config

Config(Character).save("config.yaml")
```

You will get a file with the following content:


```yaml
lvl: 1  # Level of a character
name: # Name of a character
inventory: # Character's inventory
  size: 10  # Size of an inventory
```

### Validation
As you have seen in the previous example, it is possible to add a validator. 
A validator could be any callable that takes one argument and return `True` when valid. 
You can also raise an exception if the argument is invalid to specify the reason for the failure.

There are various predefined validators in `classconfig.validators` module.

### Transformation
It is possible to specify a transformation (`transform` attribute) that will transform user input. The transformation
is done before the validation. Thus, it can be used to transform input into valid form.

It can be any callable that takes one argument and returns the transformed value, but there also exist some predefined
transformations in `classconfig.transforms` module.


### Loading
Now let's load the configuration file we just created and create an instance of `Character` class:

```python
from classconfig import Config, ConfigurableFactory

config = Config(Character).load(path)   # load configuration file
loaded_obj = ConfigurableFactory(Character).create(config)  # create an instance of Character class
```

## Why YAML?
YAML is a human-readable data serialization language. It is easy to read and write. It is also easy to parse and
generate.

It supports hierarchical data structures, which are very useful when you need to represent configuration 
of a class that has other configurable classes as members.

It supports comments, unlike e.g. json, which is also a big advantage.

