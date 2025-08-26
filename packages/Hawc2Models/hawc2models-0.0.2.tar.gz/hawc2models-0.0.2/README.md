# HAWC2 Models

Collection of pip-installable hawc2 models.

## Installation

```
pip install hawc2models
```


# Example


```python
from hawc2models import IEA22MW
htc = IEA22MW('IEA-22-280-RWT')
```


# Issues, questions and future work

- where should model source files be stored
- how to obtain/download control dlls
- how to handle updates of control dlls and models
- what is a standard model (wsp, turbulence, controller/fixed)
- which standard sensors should exist
- documentation
- images of models (automatically via hawc2visualization)