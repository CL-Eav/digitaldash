"""Wrapper around kivy.uix.label"""
from kivy.uix.label import Label
from kivy.logger import Logger
from static.constants import KE_PID
from static.constants import PID_UNIT_LABEL

# pylint: disable=too-many-instance-attributes


class KELabel(Label):
    """
    Simple wrapper around Kivy.uix.label.
    """

    def __init__(self, **args):
        """
        Args:
          default (str)     : The text that should always be displayed ie "Max: <num>"
            (default is nothing)
          color (tuple)     : RGBA values for text color
            (default is white (1, 1, 1, 1))
          font_size (int)   : Font size of label
            (default is 25)
          decimals (int)    : Number of decimal places displayed if receiving data
            (default is 2)
          pid (str)         : Byte code value of PID to get data from
            (default is nothing)
        """
        super().__init__()
        self.default = args.get("default", "")
        self.configColor = args.get("color", (1, 1, 1, 1))  # White
        self.color = self.configColor
        self.configFontSize = args.get("font_size", 25)
        self.font_size = self.configFontSize
        self.pid = args.get("pid", None)
        self.decimals = (
            "2"  # Default to 2 and update later if a value is provided
        )
        self.unitString = ""

        # Min/Max handling args
        self.isMin = args.get("Min", False)
        self.isMax = args.get("Max", False)

        if self.pid:
            self.unit = self.pid.unitLabel

            if PID_UNIT_LABEL.get(self.unit, None) is not None:
                self.unitString = str(PID_UNIT_LABEL.get(self.unit, ""))
            else:
                if self.unit != "n/a":
                    Logger.error(
                        "GUI: Found unit: %s but no PID_UNIT_LABEL value found",
                        self.unit,
                    )
            if (
                self.pid.range
                and self.pid.range.get("decimals", None) is not None
            ):
                self.decimals = self.pid.range["decimals"]

        self.objectType = "Label"
        self.markup = True

        if self.default == "__PID__":
            if self.pid.value in KE_PID:
                self.default = str(KE_PID[self.pid.value]["shortName"])
            else:
                self.default = self.pid.value
                Logger.error(
                    "Could not load shortName from Static.Constants for PID: %s",
                    self.pid.value,
                )
        if "data" in args and args["data"]:
            self.text = self.default + " 0"
        else:
            self.text = self.default

        self.setPos(**args)

    def setPos(self, **args):
        """This allows the position code to be overwritten, we use this
        for alerts."""
        posHints = args.get("pos", (0, 0))

        if args.get("gauge"):
            self.pos = (
                args.get("xPosition") + posHints[0],
                self.pos[1] + posHints[1],
            )
        else:
            self.pos_hint = {"x": posHints[0] / 100, "y": posHints[1] / 100}

    def setData(self, value="") -> None:
        """
        Send data to Label widget.

        Args:
            self (<lib.keLabel>): KELabel object
            value (float) : value that label is being updated to
        """
        try:
            value = float(value)

            if self.isMin:
                self.pid.minObserved = min(self.pid.minObserved, value)
                self.text = f"{self.pid.minObserved:.{self.decimals}f}"
            elif self.isMax:
                self.pid.maxObserved = max(self.pid.maxObserved, value)
                self.text = f"{self.pid.maxObserved:.{self.decimals}f}"
            else:
                self.text = f"{self.default}{value:.{self.decimals}f}"
                if self.unitString:
                    self.text = (
                        self.text
                        + "[size=25]"
                        + " "
                        + self.unitString
                        + "[/size]"
                    )
        except ValueError as e:
            Logger.error("GUI: keLabel.py is not numeric: %s", e)
