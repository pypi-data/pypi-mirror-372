from lightningchart_trader.indicators import (
    LineIndicator,
    PeriodIndicator,
    SourceIndicator,
)
from datetime import datetime
from dateutil.parser import parse


class CorrelationCoefficient(LineIndicator, PeriodIndicator, SourceIndicator):
    def __init__(self, trader):
        super().__init__(trader)
        self.instance.send(self.id, 'addCorrelationCoefficient', {'traderID': trader.id})

    def set_dataset(self, dataset):
        """Sets the dataset to be used for the correlation coefficient calculation.

        Args:
            dataset (Any): The dataset on which the correlation coefficient will be computed.
        """
        if isinstance(dataset, list):
            for item in dataset:
                if 'dateTime' in item:
                    date_time = item['dateTime']

                    if isinstance(date_time, datetime):
                        item['dateTime'] = date_time.isoformat()

                    elif isinstance(date_time, str):
                        try:
                            parsed_date = parse(date_time)
                            item['dateTime'] = parsed_date.isoformat()
                        except (ValueError, OverflowError):
                            pass

                    elif isinstance(date_time, (float, int)):
                        try:
                            item['dateTime'] = datetime.fromtimestamp(date_time).isoformat()
                        except (OverflowError, ValueError):
                            item['dateTime'] = None

        self.instance.send(self.id, 'setDataset', {'dataset': dataset})
        return self

    def set_symbol(self, symbol: str):
        """Sets the symbol to be used in the correlation coefficient calculation.

        Args:
            symbol (str): The symbol representing the financial instrument.
        """
        self.instance.send(self.id, 'setSymbol', {'symbol': symbol})
        return self
