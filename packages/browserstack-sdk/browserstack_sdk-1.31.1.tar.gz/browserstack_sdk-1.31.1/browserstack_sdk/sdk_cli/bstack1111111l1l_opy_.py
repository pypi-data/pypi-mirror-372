# coding: UTF-8
import sys
bstack1ll1111_opy_ = sys.version_info [0] == 2
bstack1111l1l_opy_ = 2048
bstack1l111_opy_ = 7
def bstack1111lll_opy_ (bstack1llll11_opy_):
    global bstack1llll1_opy_
    bstack1l111l_opy_ = ord (bstack1llll11_opy_ [-1])
    bstack11111l_opy_ = bstack1llll11_opy_ [:-1]
    bstack1l11ll_opy_ = bstack1l111l_opy_ % len (bstack11111l_opy_)
    bstack1l111l1_opy_ = bstack11111l_opy_ [:bstack1l11ll_opy_] + bstack11111l_opy_ [bstack1l11ll_opy_:]
    if bstack1ll1111_opy_:
        bstack1_opy_ = unicode () .join ([unichr (ord (char) - bstack1111l1l_opy_ - (bstack1l11l_opy_ + bstack1l111l_opy_) % bstack1l111_opy_) for bstack1l11l_opy_, char in enumerate (bstack1l111l1_opy_)])
    else:
        bstack1_opy_ = str () .join ([chr (ord (char) - bstack1111l1l_opy_ - (bstack1l11l_opy_ + bstack1l111l_opy_) % bstack1l111_opy_) for bstack1l11l_opy_, char in enumerate (bstack1l111l1_opy_)])
    return eval (bstack1_opy_)
import os
import threading
import os
from typing import Dict, Any
from dataclasses import dataclass
from collections import defaultdict
from datetime import timedelta
@dataclass
class bstack1111111ll1_opy_:
    id: str
    hash: str
    thread_id: int
    process_id: int
    type: str
class bstack1lllll1l111_opy_:
    bstack11llll11l1l_opy_ = bstack1111lll_opy_ (u"ࠧࡨࡥ࡯ࡥ࡫ࡱࡦࡸ࡫ࠣᗞ")
    context: bstack1111111ll1_opy_
    data: Dict[str, Any]
    platform_index: int
    def __init__(self, context: bstack1111111ll1_opy_):
        self.context = context
        self.data = dict({bstack1lllll1l111_opy_.bstack11llll11l1l_opy_: defaultdict(lambda: timedelta(microseconds=0))})
        self.platform_index = int(os.environ.get(bstack1111lll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ᗟ"), bstack1111lll_opy_ (u"ࠧ࠱ࠩᗠ")))
    def ref(self) -> str:
        return str(self.context.id)
    def bstack1lllll11lll_opy_(self, target: object):
        return bstack1lllll1l111_opy_.create_context(target) == self.context
    def bstack1l1lllllll1_opy_(self, context: bstack1111111ll1_opy_):
        return context and context.thread_id == self.context.thread_id and context.process_id == self.context.process_id
    def bstack1l11ll111_opy_(self, key: str, value: timedelta):
        self.data[bstack1lllll1l111_opy_.bstack11llll11l1l_opy_][key] += value
    def bstack1lll111l1ll_opy_(self) -> dict:
        return self.data[bstack1lllll1l111_opy_.bstack11llll11l1l_opy_]
    @staticmethod
    def create_context(
        target: object,
        thread_id=threading.get_ident(),
        process_id=os.getpid(),
    ):
        return bstack1111111ll1_opy_(
            id=hash(target),
            hash=hash(target),
            thread_id=thread_id,
            process_id=process_id,
            type=target,
        )