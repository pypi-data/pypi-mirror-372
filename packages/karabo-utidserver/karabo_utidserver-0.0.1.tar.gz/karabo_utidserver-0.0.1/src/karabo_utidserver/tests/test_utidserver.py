from datetime import datetime

import numpy as np
import pytest
import pytest_asyncio  # noqa

from karabo.middlelayer import (
    Device, State, String, TimeMixin, background, get_timestamp, sleep, slot)
from karabo.middlelayer.testing import event_loop_policy  # noqa
from karabo.middlelayer.testing import (
    AsyncDeviceContext, create_instanceId, sleepUntil)
from karabo_utidserver.utid_server import UTIDServer


class TestConnector(Device):

    timeServerId = String()

    async def onInitialization(self):
        self._timer_task = None
        self.utids = {}
        self.recv_utids = []
        # we use the internal async_connect function here,
        # just like the MDL server does.
        await self.signalSlotable.async_connect(
                self.timeServerId, "signalTimeTick", self.slotTimeTick)
        self.state = State.ACTIVE

    def onDestruction(self):
        if self._timer_task is not None:
            self._timer_task.cancel()

    @slot
    def slotTimeTick(self, utid, sec, frac, period):
        # this is copied over from the middlelayer server to test the
        # the accepatance of the signal, without the overhead of a
        # middlelayer sever
        TimeMixin.set_reference(utid, sec, frac, period)
        self.recv_utids.append(utid)
        if self._timer_task is None:
            self._timer_task = background(self._timer())

    async def _timer(self):
        then = datetime.now()
        last_utid = get_timestamp().tid
        while True:
            utid = get_timestamp().tid
            if utid != last_utid:
                now = datetime.now()
                self.utids[utid] = (now - then).total_seconds() * 1000
                then = now
                last_utid = utid
            # short sleeps to be sufficiently accurate on the delays
            await sleep(0.001)


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_utids_100ms(mocker):
    test_id = create_instanceId()
    _TEST_CONFIG_ = {
        "deviceId": f"{test_id}",
        "publishPeriod": 1000,  # ms
    }

    _CONNECTOR_CONFIG_ = {
        "deviceId": f"timer_{test_id}",
        "timeServerId": f"{test_id}",
    }

    device = UTIDServer(_TEST_CONFIG_)
    connector = TestConnector(_CONNECTOR_CONFIG_)

    async with AsyncDeviceContext(connector=connector, device=device) as ctx:
        assert ctx.instances["device"] is device
        assert ctx.instances["connector"] is connector
        # we start with valid configurations
        await sleepUntil(lambda: device.state == State.ACTIVE)
        await sleepUntil(lambda: connector.state == State.ACTIVE)
        await sleep(1)
        utid0 = device.currentUTID.value
        publishPeriod = device.publishPeriod.value
        period = device.period.value
        num_fails = 0
        for i in range(5):
            expected_uuid = int(publishPeriod / period * i + utid0)
            if device.currentUTID.value != expected_uuid:
                num_fails += 1
            await sleep(device.publishPeriod)

        # allow for a low ammount of flakeyness here
        assert num_fails <= 3

        # now test what was received over the signal
        utids = np.array(list(connector.utids.keys()))
        # drop the first which will may not be accurate as we bootstrap
        # our collection anywhere within a period
        utids = utids[1:]
        # all should be unique
        assert utids.size == np.unique(utids).size
        # and monotonically increasing by one
        assert np.allclose(utids[1:] - utids[:-1], 1)

        # the update period should have a mean value close to our period
        dt = np.array(list(connector.utids.values()))
        # again drop the first element
        dt = dt[1:]
        mn = np.mean(dt)
        msg = f"Mean value is {mn}, and not {device.period.value} ms!"
        assert np.isclose(mn, device.period.value, atol=3.5), msg

        # now check that the utids that were received via the signal
        # are spaced by publishPeriod
        recv_utids = np.array(connector.recv_utids)
        # all should be unique
        assert recv_utids.size == np.unique(recv_utids).size
        # and monotonically increasing by the number of period between each
        # publish cycle. We allow for some flakiness here.
        dutid_per_publish = device.publishPeriod.value / device.period.value
        assert np.allclose(recv_utids[1:] - recv_utids[:-1],
                           dutid_per_publish, atol=2)


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_update_period_must_be_larger_equal_period(mocker):
    test_id = create_instanceId()

    # this should fail because publishPeriod is less than period.
    _TEST_CONFIG_ = {
        "deviceId": f"{test_id}",
        "period": 100,  # ms
        "publishPeriod": 10,  # ms
    }

    with pytest.raises(AssertionError):
        _ = UTIDServer(_TEST_CONFIG_)

    # this should work
    _TEST_CONFIG_ = {
        "deviceId": f"{test_id}",
        "period": 10,  # ms
        "publishPeriod": 10,  # ms
    }

    _ = UTIDServer(_TEST_CONFIG_)
