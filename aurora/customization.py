"""This is where the customization logic happens. 
Let's have a runner instance for every device.
"""


class CustomizationRunner:
    def __init__(self, customize_to):
        self.customize_to = customize_to

    def __repr__(self):
        return f"{self.__class__.__name__}({self.customize_to})"

    def __str__(self):
        return f"A customization runner for {self.customize_to.upper()}"

    def start(self):
        print(f"Customizing: {self.customize_to}")
