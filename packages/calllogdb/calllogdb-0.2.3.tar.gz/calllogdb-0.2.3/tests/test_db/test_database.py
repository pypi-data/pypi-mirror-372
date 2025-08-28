from datetime import datetime

from calllogdb.db.database import CallMapper
from calllogdb.db.models import ApiVars, Call, Event


class DummyEvent:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.api_vars = kwargs.get("api_vars", {})

    def del_api_vars(self):
        data = self.__dict__.copy()
        data.pop("api_vars", None)
        return data


class DummyCallData:
    def __init__(self):
        self.call_id = "123"
        self.call_status = "completed"
        self.call_date = datetime(2024, 5, 1, 14, 30, 0)
        self.events = [DummyEvent(event_type="answer", api_vars={"intent": "test"})]

    def del_events(self):
        data = self.__dict__.copy()
        data.pop("events", None)
        return data


def test_call_mapper():
    mapper = CallMapper()
    dummy_data = DummyCallData()

    call_obj = mapper.map(dummy_data)

    assert isinstance(call_obj, Call)
    assert call_obj.call_id == "123"
    assert call_obj.date.year == 2024
    assert len(call_obj.events) == 1
    assert isinstance(call_obj.events[0], Event)
    assert isinstance(call_obj.events[0].api_vars[0], ApiVars)
    assert call_obj.events[0].api_vars[0].intent == "test"
