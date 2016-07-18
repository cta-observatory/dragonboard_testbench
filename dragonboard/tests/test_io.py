def test_reading_v5_1_05():
    from ..io import EventGenerator_v5_1_05

    eg = EventGenerator_v5_1_05(
        'data/random_noise_v5_1_05.dat',
        max_events=10,
    )

    repr(eg)
    assert eg.event_size == 32816

    event = next(eg)
    assert event.roi == 1024


def test_reading_v5_1_0B():
    from ..io import EventGenerator_v5_1_0B

    eg = EventGenerator_v5_1_0B(
        'data/random_noise_v5_1_0B.dat',
        max_events=10,
    )

    repr(eg)
    assert eg.event_size == 32832

    event = next(eg)
    assert event.roi == 1024


def test_performance_v5_1_05():
    from ..io import read
    events = read('data/random_noise_v5_1_05.dat')

    assert len(events) == 100


def test_performance_v5_1_0B():
    from ..io import read
    events = read('data/random_noise_v5_1_0B.dat')

    assert len(events) == 100
