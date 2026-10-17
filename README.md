# dotabyss-translation

> 鸡渊简体中文汉化文件

- **PC端Mod**: [AbyssMod](https://github.com/anosu/AbyssMod)
- **安卓端Mod**: [DMM-Mod](https://github.com/anosu/DMM-Mod)

UI 译文保存在 `translations/ui_texts/zh_Hans.json`，结构为「路径 → 日文原文 → 中文译文」。

UI 路径沿用现有插件支持的完整运行时路径和单层 `*` 通配符，不引入新的匹配语法。离线提取的资源路径需要先根据已有规则或采集记录补全运行时父层级；尚未确定完整路径的译文不进入正式翻译表。

修改译文后运行 `python manifest.py` 更新清单，运行 `npm run build` 生成本地分发文件。
