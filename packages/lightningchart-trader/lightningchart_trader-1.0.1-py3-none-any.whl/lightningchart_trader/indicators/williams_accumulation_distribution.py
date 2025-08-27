from lightningchart_trader.indicators import LineIndicator


class WilliamsAccumulationDistribution(LineIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addWilliamsAccumulationDistribution', {'traderID': trader.id})

    def set_volume_use(self, use_volume: bool):
        """Sets whether to include volume in the Williams Accumulation/Distribution calculation.

        Args:
            use_volume (bool): If True, the volume will be used in the calculation. If False, volume is excluded.
        """
        self.instance.send(self.id, 'setVolumeUse', {'useVolume': use_volume})
        return self
