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
import threading
import tempfile
import os
import time
from datetime import datetime
from bstack_utils.bstack11ll111llll_opy_ import bstack11ll11l1ll1_opy_
from bstack_utils.constants import bstack11l1ll11111_opy_, bstack111111lll_opy_
from bstack_utils.bstack111l111ll_opy_ import bstack1l11llll1_opy_
from bstack_utils import bstack1l1l11111_opy_
bstack11l1l11l1ll_opy_ = 10
class bstack1111ll1l_opy_:
    def __init__(self, bstack11ll1l11ll_opy_, config, bstack11l1l1l1l11_opy_=0):
        self.bstack11l1l11l111_opy_ = set()
        self.lock = threading.Lock()
        self.bstack11l1l11ll11_opy_ = bstack1111lll_opy_ (u"ࠦࢀࢃ࠯ࡵࡧࡶࡸࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠳ࡦࡶࡩ࠰ࡸ࠴࠳࡫ࡧࡩ࡭ࡧࡧ࠱ࡹ࡫ࡳࡵࡵࠥ᫉").format(bstack11l1ll11111_opy_)
        self.bstack11l1l11lll1_opy_ = os.path.join(tempfile.gettempdir(), bstack1111lll_opy_ (u"ࠧࡧࡢࡰࡴࡷࡣࡧࡻࡩ࡭ࡦࡢࡿࢂࠨ᫊").format(os.environ.get(bstack1111lll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ᫋"))))
        self.bstack11l1l1l1l1l_opy_ = os.path.join(tempfile.gettempdir(), bstack1111lll_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪ࡟ࡵࡧࡶࡸࡸࡥࡻࡾ࠰ࡷࡼࡹࠨᫌ").format(os.environ.get(bstack1111lll_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ᫍ"))))
        self.bstack11l1l1ll111_opy_ = 2
        self.bstack11ll1l11ll_opy_ = bstack11ll1l11ll_opy_
        self.config = config
        self.logger = bstack1l1l11111_opy_.get_logger(__name__, bstack111111lll_opy_)
        self.bstack11l1l1l1l11_opy_ = bstack11l1l1l1l11_opy_
        self.bstack11l1l1l11l1_opy_ = False
        self.bstack11l1l1ll1ll_opy_ = not (
                            os.environ.get(bstack1111lll_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡓࡗࡑࡣࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒࠣᫎ")) and
                            os.environ.get(bstack1111lll_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡑࡓࡉࡋ࡟ࡊࡐࡇࡉ࡝ࠨ᫏")) and
                            os.environ.get(bstack1111lll_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡔ࡚ࡁࡍࡡࡑࡓࡉࡋ࡟ࡄࡑࡘࡒ࡙ࠨ᫐"))
                        )
        if bstack1l11llll1_opy_.bstack11l1l1ll1l1_opy_(config):
            self.bstack11l1l1ll111_opy_ = bstack1l11llll1_opy_.bstack11l1l1l111l_opy_(config, self.bstack11l1l1l1l11_opy_)
            self.bstack11l1l1lll11_opy_()
    def bstack11l1l1l1111_opy_(self):
        return bstack1111lll_opy_ (u"ࠧࢁࡽࡠࡽࢀࠦ᫑").format(self.config.get(bstack1111lll_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ᫒")), os.environ.get(bstack1111lll_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡘࡕࡏࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭᫓")))
    def bstack11l1l11ll1l_opy_(self):
        try:
            if self.bstack11l1l1ll1ll_opy_:
                return
            with self.lock:
                try:
                    with open(self.bstack11l1l1l1l1l_opy_, bstack1111lll_opy_ (u"ࠣࡴࠥ᫔")) as f:
                        bstack11l1l11l11l_opy_ = set(line.strip() for line in f if line.strip())
                except FileNotFoundError:
                    bstack11l1l11l11l_opy_ = set()
                bstack11l1l11l1l1_opy_ = bstack11l1l11l11l_opy_ - self.bstack11l1l11l111_opy_
                if not bstack11l1l11l1l1_opy_:
                    return
                self.bstack11l1l11l111_opy_.update(bstack11l1l11l1l1_opy_)
                data = {bstack1111lll_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࡖࡨࡷࡹࡹࠢ᫕"): list(self.bstack11l1l11l111_opy_), bstack1111lll_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡐࡤࡱࡪࠨ᫖"): self.config.get(bstack1111lll_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ᫗")), bstack1111lll_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡖࡺࡴࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠥ᫘"): os.environ.get(bstack1111lll_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡈࡕࡊࡎࡇࡣࡗ࡛ࡎࡠࡋࡇࡉࡓ࡚ࡉࡇࡋࡈࡖࠬ᫙")), bstack1111lll_opy_ (u"ࠢࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠧ᫚"): self.config.get(bstack1111lll_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭᫛"))}
            response = bstack11ll11l1ll1_opy_.bstack11l1l111lll_opy_(self.bstack11l1l11ll11_opy_, data)
            if response.get(bstack1111lll_opy_ (u"ࠤࡶࡸࡦࡺࡵࡴࠤ᫜")) == 200:
                self.logger.debug(bstack1111lll_opy_ (u"ࠥࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺࠢࡶࡩࡳࡺࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࡀࠠࡼࡿࠥ᫝").format(data))
            else:
                self.logger.debug(bstack1111lll_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡴࡧࡱࡨࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶ࠾ࠥࢁࡽࠣ᫞").format(response))
        except Exception as e:
            self.logger.debug(bstack1111lll_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡦࡸࡶ࡮ࡴࡧࠡࡵࡨࡲࡩ࡯࡮ࡨࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳ࠻ࠢࡾࢁࠧ᫟").format(e))
    def bstack11l1l1l1lll_opy_(self):
        if self.bstack11l1l1ll1ll_opy_:
            with self.lock:
                try:
                    with open(self.bstack11l1l1l1l1l_opy_, bstack1111lll_opy_ (u"ࠨࡲࠣ᫠")) as f:
                        bstack11l1l11llll_opy_ = set(line.strip() for line in f if line.strip())
                    failed_count = len(bstack11l1l11llll_opy_)
                except FileNotFoundError:
                    failed_count = 0
                self.logger.debug(bstack1111lll_opy_ (u"ࠢࡑࡱ࡯ࡰࡪࡪࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࠦࡣࡰࡷࡱࡸࠥ࠮࡬ࡰࡥࡤࡰ࠮ࡀࠠࡼࡿࠥ᫡").format(failed_count))
                if failed_count >= self.bstack11l1l1ll111_opy_:
                    self.logger.info(bstack1111lll_opy_ (u"ࠣࡖ࡫ࡶࡪࡹࡨࡰ࡮ࡧࠤࡨࡸ࡯ࡴࡵࡨࡨࠥ࠮࡬ࡰࡥࡤࡰ࠮ࡀࠠࡼࡿࠣࡂࡂࠦࡻࡾࠤ᫢").format(failed_count, self.bstack11l1l1ll111_opy_))
                    self.bstack11l1l1l1ll1_opy_(failed_count)
                    self.bstack11l1l1l11l1_opy_ = True
            return
        try:
            response = bstack11ll11l1ll1_opy_.bstack11l1l1l1lll_opy_(bstack1111lll_opy_ (u"ࠤࡾࢁࡄࡨࡵࡪ࡮ࡧࡒࡦࡳࡥ࠾ࡽࢀࠪࡧࡻࡩ࡭ࡦࡕࡹࡳࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳ࠿ࡾࢁࠫࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࡀࡿࢂࠨ᫣").format(self.bstack11l1l11ll11_opy_, self.config.get(bstack1111lll_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭᫤")), os.environ.get(bstack1111lll_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪ᫥")), self.config.get(bstack1111lll_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪ᫦"))))
            if response.get(bstack1111lll_opy_ (u"ࠨࡳࡵࡣࡷࡹࡸࠨ᫧")) == 200:
                failed_count = response.get(bstack1111lll_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࡔࡦࡵࡷࡷࡈࡵࡵ࡯ࡶࠥ᫨"), 0)
                self.logger.debug(bstack1111lll_opy_ (u"ࠣࡒࡲࡰࡱ࡫ࡤࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡤࡱࡸࡲࡹࡀࠠࡼࡿࠥ᫩").format(failed_count))
                if failed_count >= self.bstack11l1l1ll111_opy_:
                    self.logger.info(bstack1111lll_opy_ (u"ࠤࡗ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨࠥࡩࡲࡰࡵࡶࡩࡩࡀࠠࡼࡿࠣࡂࡂࠦࡻࡾࠤ᫪").format(failed_count, self.bstack11l1l1ll111_opy_))
                    self.bstack11l1l1l1ll1_opy_(failed_count)
                    self.bstack11l1l1l11l1_opy_ = True
            else:
                self.logger.error(bstack1111lll_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡰ࡮࡯ࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡹ࡫ࡳࡵࡵ࠽ࠤࢀࢃࠢ᫫").format(response))
        except Exception as e:
            self.logger.error(bstack1111lll_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡥࡷࡵ࡭ࡳ࡭ࠠࡱࡱ࡯ࡰ࡮ࡴࡧ࠻ࠢࡾࢁࠧ᫬").format(e))
    def bstack11l1l1l1ll1_opy_(self, failed_count):
        with open(self.bstack11l1l11lll1_opy_, bstack1111lll_opy_ (u"ࠧࡽࠢ᫭")) as f:
            f.write(bstack1111lll_opy_ (u"ࠨࡔࡩࡴࡨࡷ࡭ࡵ࡬ࡥࠢࡦࡶࡴࡹࡳࡦࡦࠣࡥࡹࠦࡻࡾ࡞ࡱࠦ᫮").format(datetime.now()))
            f.write(bstack1111lll_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࠦࡣࡰࡷࡱࡸ࠿ࠦࡻࡾ࡞ࡱࠦ᫯").format(failed_count))
        self.logger.debug(bstack1111lll_opy_ (u"ࠣࡃࡥࡳࡷࡺࠠࡃࡷ࡬ࡰࡩࠦࡦࡪ࡮ࡨࠤࡨࡸࡥࡢࡶࡨࡨ࠿ࠦࡻࡾࠤ᫰").format(self.bstack11l1l11lll1_opy_))
    def bstack11l1l1lll11_opy_(self):
        def bstack11l1l1l11ll_opy_():
            while not self.bstack11l1l1l11l1_opy_:
                time.sleep(bstack11l1l11l1ll_opy_)
                self.bstack11l1l11ll1l_opy_()
                self.bstack11l1l1l1lll_opy_()
        bstack11l1l1ll11l_opy_ = threading.Thread(target=bstack11l1l1l11ll_opy_, daemon=True)
        bstack11l1l1ll11l_opy_.start()