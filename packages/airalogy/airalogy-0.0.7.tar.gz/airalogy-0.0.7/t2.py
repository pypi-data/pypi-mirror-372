from datetime import datetime
from traceback import print_tb

from pydantic import BaseModel

from airalogy.types import ATCG, CurrentTime, UserName


class DNA(BaseModel):
    # seq: ATCG
    time: CurrentTime
    # user: UserName


# m = DNA(seq="ATCGGATC")

# s1 = DNA.model_json_schema()
t1 = datetime.strptime("2025-08-27T10:59:40+08:00", "%Y-%m-%dT%H:%M:%S%z")
print(t1)
print(t1.isoformat())
t2 = datetime.now()
print(t2)
print(t2.isoformat())

print(DNA.model_json_schema())
test_payload: dict[str, str] = {"time": "2025-08-27T10:59:40+08:00"}
d1 = DNA(**test_payload)
print(d1)

d2 = DNA(time="2025-08-27 10:59:40.123")
print(d2)
