import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import manual_package as mpkg  # noqa: E402

BODY = ("我们这次带娃来同治龙窑，冲着拉坯来的。参观是免费的，制作陶罐2个100元，老师可以在旁边指导。"
        "最后做了一个花瓶、一个葫芦瓶，瓶身上还刻了字。做好的陶罐要等1个月左右，会联系寄送。"
        "离市区30多公里，适合自驾；吃饭可以去周边1公里的镇上。我觉得适合亲子家庭。"
        "你们家娃做出来的是什么形状？")
FACTS = {"category": "亲子体验", "notes": ["陶罐2个100元", "1个月", "30多公里", "1公里"]}


class ErrorCodeTest(unittest.TestCase):
    def test_code_in_message(self):
        self.assertEqual(str(mpkg.PublishError("店铺页没有入口", code="E202")), "[E202] 店铺页没有入口")
        self.assertEqual(str(mpkg.PublishError("x")), "x")


class StarValidationTest(unittest.TestCase):
    def payload(self, stars):
        return {"shop": "同治龙窑", "body": BODY, "facts": FACTS, "stars": stars}

    def test_auto_publish_needs_int(self):
        with self.assertRaises(mpkg.PublishError) as e:
            mpkg.validate_payload(self.payload(4.5), "review", False)
        self.assertEqual(e.exception.code, "E402")
        mpkg.validate_payload(self.payload(4), "review", False)

    def test_manual_allows_half(self):
        mpkg.validate_payload(self.payload(4.5), "review", False, allow_half=True)
        with self.assertRaises(mpkg.PublishError):
            mpkg.validate_payload(self.payload(4.3), "review", False, allow_half=True)
        with self.assertRaises(mpkg.PublishError):
            mpkg.validate_payload(self.payload(True), "review", False, allow_half=True)


class StageManualTest(unittest.TestCase):
    def test_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            imgs = []
            for name in ("IMG_2921.jpg", "IMG_2893.jpg"):
                (tmp / name).write_bytes(b"jpg")
                imgs.append(str(tmp / name))
            payload = {"shop": "同治龙窑", "body": BODY, "facts": FACTS, "stars": 4.5,
                       "images": imgs, "tags": ["#成都亲子", "#陶艺体验"]}
            with mock.patch.object(mpkg, "load_sibling_hooks", return_value=[]):
                d = mpkg.stage_manual(payload, "review", str(tmp / "out"))
            self.assertEqual(d, tmp / "out" / "评价")
            self.assertEqual(sorted(p.name for p in d.iterdir()),
                             ["01-IMG_2921.jpg", "02-IMG_2893.jpg", "文案.txt"])
            text = (d / "文案.txt").read_text(encoding="utf-8")
            self.assertIn("总体星级：4.5", text)
            self.assertIn("#成都亲子 #陶艺体验", text)

    def test_gate_blocks_staging(self):
        payload = {"shop": "同治龙窑", "body": BODY + "全网第一。", "facts": FACTS, "stars": 4}
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(mpkg, "load_sibling_hooks", return_value=[]):
            with self.assertRaises(mpkg.PublishError) as e:
                mpkg.stage_manual(payload, "review", tmp)
            self.assertEqual(e.exception.code, "E401")


if __name__ == "__main__":
    unittest.main()
