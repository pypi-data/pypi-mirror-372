from datetime import datetime, timedelta

import pytest

from calllogdb.db.models import ApiVars, Call, Date, Event


@pytest.fixture
def call_instance():
    return Call(
        call_id="call123",
        call_status="completed",
        call_type="outgoing",
        src_num="1001",
        dst_num="1002",
        call_date=datetime(2024, 1, 1, 12, 0),
        answer_date=datetime(2024, 1, 1, 12, 1),
        end_time=datetime(2024, 1, 1, 12, 5),
        total_time=timedelta(minutes=5),
        wait_time=timedelta(seconds=30),
        talk_time=timedelta(minutes=4, seconds=30),
        transfered_linked_to=False,
    )


def test_create_call(call_instance):
    assert call_instance.call_id == "call123"
    assert call_instance.call_status == "completed"
    assert call_instance.call_type == "outgoing"
    assert call_instance.total_time == timedelta(minutes=5)


def test_call_with_date(call_instance):
    date = Date(call_id=call_instance.call_id, year=2024, month=1, day=1, hours=12, minutes=0, seconds=0)
    call_instance.date = date

    assert call_instance.date.year == 2024
    assert call_instance.date.call_id == call_instance.call_id


def test_call_with_event(call_instance):
    event = Event(
        id=1,
        call_id=call_instance.call_id,
        event_type="ringing",
        event_status="ok",
        event_total_time=timedelta(seconds=30),
    )
    call_instance.events.append(event)

    assert len(call_instance.events) == 1
    assert call_instance.events[0].event_type == "ringing"


def test_event_with_api_vars():
    event = Event(id=1, call_id="call123")
    api_var = ApiVars(id=1, event_id="call123", account_id="acc1", other={"key": "value"})
    event.api_vars.append(api_var)

    assert event.api_vars[0].account_id == "acc1"
    assert event.api_vars[0].other["key"] == "value"
