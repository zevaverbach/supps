# Purpose

To keep track of my vitamins, minerals, supplements and prescriptions so I can know when to order more, and to have enough when I do my monthly 'packaging' of them into easy to use containers.

# Inventory CLI

```bash
> sup status

The next fill-up is on <date>, and you won't have enough of

- x (need quantity x')
- y (need quantity y')
- z (need quantity z')

> sup fill

Okay, next fill-up set to <date X days from now> (configured in `sup.toml`::FILL_EVERY_X_DAYS)

# (this is to add to the inventory; any changes to consumption should be done in `supps.toml`)
> sup add                 
>> name? <name>
>> date? (today)
>> number of bottles? (1)
>> quantity?
>> serving quantity?
>> serving unit? (mg)
```

# Configuration

TODO: talk about product_aliases

To configure what you take, how much, and when, add entries to `supps.toml`.  The fields are configured as such in the `Supp` class:

```python
name: str
units: t.Literal["caps", "mg", "g", "ml", "mcg", "iu"] = "mg"

# these are meant to be doses; units are defined below
morning: int | float = 0
lunch: int | float = 0
dinner: int | float = 0
bedtime: int | float = 0

days_per_week: int = 7
winter_only: bool = False
```
