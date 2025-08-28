# Yappatron Basic Browser

```python
from yappatronbasicbrowser import run, YappatronSettings

# Run default browser
run()

# Run browser with custom settings
settings = YappatronSettings(start_url="https://google.com", width=1280, height=720)
run(settings=settings)
