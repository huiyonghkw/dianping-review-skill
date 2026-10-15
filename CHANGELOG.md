# Changelog · dianping-review-skill

## 1.1.1 · 2026-10-15

- 引入协作 skill [hekouwang-writer-skill](https://github.com/huiyonghkw/hekouwang-writer-skill)：点评以外的中文文档（办事指南、方案、报告、邮件、长篇攻略）交给它。SKILL.md 新增「协作」一节，description 的「不用于」写明交接对象。
- `references/style.md`：装了 hekouwang-writer-skill 时，长笔记可选跑它的锯末词和长句体检，只作提醒，门禁仍以 `content_gate.py` 为准。
- README 新增「相关 Skill」。

## 1.1.0 · 2026-10-13

- 首图叠字：发布包的第一张是 3:4 封面，白字黑边标题 `<地点 · 名称>`，下面 2–4 行浅黄事实。原图从 02 开始编号。
- 封面文案里的数字同样要在事实卡里找得到。合成封面需要 Pillow。
- 引导消费：正文改成五段，新增行动段（点什么、几点去、怎么去）和「不适合谁」；访谈补问怎么买、几点去、怎么去。
- 内容检查新增拦截：硬推销词、商家口吻、AI 腔套话和升华句。新增提醒：行动信息、不适合谁、破折号、排比三连、句长过于整齐。
- 新增 `references/style.md`：引导消费和去 AI 味的写法，以及交付前的改写自查。
- 手动发布包默认输出到当前项目的 `dist/<店名>-发布/`（此前在 `~/Downloads`），`dist/` 已加入 .gitignore 不进版本库；`--out-dir` 可覆盖。

## 1.0.0 · 2026-10-12

首个公开版本，MIT-0。

- 事实卡：一次问清缺的事实，连同照片里看得到的记成一张卡，正文只写卡上有的。
- 评价与笔记分开写，开头卖点不撞车；附标题、标签、图片顺序和用户给的星级。
- 5 个品类必写项：餐饮、美容美发、休闲娱乐、亲子体验、酒店民宿。
- 内容检查 `content_gate.py`：数字出处、人均一致、广告法极限词、手机号微信等站外联系方式。
- 手动发布包 `manual_package.py`：照片按上传顺序编号，文案存成文件。
- 只需要 Python 3 标准库。
- 主页：https://huiyonghkw.github.io/dianping-review-skill/
