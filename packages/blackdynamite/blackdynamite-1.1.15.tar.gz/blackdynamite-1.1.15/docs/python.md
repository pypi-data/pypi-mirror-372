# Python interface

First we need to set the python headers and to import the **BlackDynamite** modules by
```python
#!/usr/bin/env python

import BlackDynamite as BD
```

Then you have to create a generic black dynamite parser
and parse the system (including the connection parameters and credentials)

```python
parser = BD.BDParser()
params = parser.parseBDParameters()
```

This mechanism allows to easily inherit from the parser mechanism
of BlackDynamite, including the completion (if activated: see installation instructions).
Then you can connect to the black dynamite database

```python
base = BD.base.Base(**params)
```
