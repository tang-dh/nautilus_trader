# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2020 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

from collections import deque

from nautilus_trader.core.correctness cimport Condition
from nautilus_trader.indicators.base.indicator cimport Indicator
from nautilus_trader.model.bar cimport Bar
from nautilus_trader.model.tick cimport QuoteTick
from nautilus_trader.model.tick cimport TradeTick

from nautilus_trader.indicators.average.ma_factory import MovingAverageFactory
from nautilus_trader.indicators.average.ma_factory import MovingAverageType

from nautilus_trader.core.functions cimport fast_std_with_mean


cdef class BollingerBands(Indicator):
    """
    A Bollinger Band® is a technical analysis tool defined by a set of
    trend lines plotted two standard deviations (positively and negatively) away
    from a simple moving average (SMA) of a security's price, but which can be
    adjusted to user preferences.
    """

    def __init__(
            self,
            int period,
            double k,
            ma_type not None: MovingAverageType=MovingAverageType.SIMPLE,
    ):
        """
        Initialize a new instance of the DonchianChannel class.

        Parameters
        ----------
        period : int
            The rolling window period for the indicator (> 0).
        k : double
            The standard deviation multiple for the indicator (> 0).
        ma_type : MovingAverageType
            The moving average type for the indicator.

        Raises
        ------
        ValueError
            If period is not positive (> 0).
        ValueError
            If k is not positive (> 0).

        """
        Condition.positive_int(period, "period")
        Condition.positive(k, "k")
        super().__init__(params=[period, k, ma_type.name])

        self._period = period
        self._k = k
        self._ma = MovingAverageFactory.create(period, ma_type)
        self._prices = deque(maxlen=period)

        self._value_upper = 0
        self._value_lower = 0

    @property
    def period(self):
        """
        The indicators period for the moving average.

        Returns
        -------
        int

        """
        return self._period

    @property
    def k(self):
        """
        The indicators standard deviation multiple.

        Returns
        -------
        double

        """
        return self._k

    @property
    def upper(self):
        """
        The value of the upper band.

        Returns
        -------
        double

        """
        return self._value_upper

    @property
    def middle(self):
        """
        The value of the moving average.

        Returns
        -------
        double

        """
        return self._ma.value

    @property
    def lower(self):
        """
        The value of the lower band.

        Returns
        -------
        double

        """
        return self._value_lower

    cpdef void handle_quote_tick(self, QuoteTick tick) except *:
        """
        Update the indicator with the given ticks high and low prices.

        Parameters
        ----------
        tick : TradeTick
            The tick for the update.

        """
        Condition.not_none(tick, "tick")

        cdef double ask = tick.ask.as_double()
        cdef double bid = tick.bid.as_double()
        cdef double mid = (ask + bid / 2)
        self.update_raw(ask, bid, mid)

    cpdef void handle_trade_tick(self, TradeTick tick) except *:
        """
        Update the indicator with the given ticks price.

        Parameters
        ----------
        tick : TradeTick
            The tick for the update.

        """
        Condition.not_none(tick, "tick")

        cdef double price = tick.price.as_double()
        self.update_raw(price, price, price)

    cpdef void handle_bar(self, Bar bar) except *:
        """
        Update the indicator with the given bar.

        Parameters
        ----------
        bar : Bar
            The update bar.

        """
        Condition.not_none(bar, "bar")

        self.update_raw(
            bar.high.as_double(),
            bar.low.as_double(),
            bar.close.as_double(),
        )

    cpdef void update_raw(self, double high, double low, double close) except *:
        """
        Update the indicator with the given prices.

        Parameters
        ----------
        high : double
            The high price for calculations.
        low : double
            The low price for calculations.
        close : double
            The closing price for calculations

        """
        # Add data to queues
        cdef double typical = (high + low + close) / 3

        self._prices.append(typical)
        self._ma.update_raw(typical)

        # Initialization logic
        if not self._initialized:
            self._set_has_inputs(True)
            if len(self._prices) >= self._period:
                self._set_initialized(True)

        # Calculate values
        cdef double std = fast_std_with_mean(values=list(self._prices), mean=self._ma.value)

        # Set values
        self._value_upper = self._ma.value + (self._k * std)
        self._value_lower = self._ma.value - (self._k * std)

    cpdef void reset(self) except *:
        """
        Reset the indicator.

        All stateful values are reset to their initial value.

        """
        self._reset_base()
        self._ma.reset()
        self._prices.clear()

        self._value_upper = 0
        self._value_lower = 0
