from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE

from .fonts import SONG_FONT_NAMES, TIMES_NEW_ROMAN

# 样式配置
STYLE_CONFIGS = {
    "文档标题": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(32),
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "space_before": Pt(12),
        "space_after": Pt(6),
        "first_line_indent": 0
    },
    "一级标题": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(16),  # 小三
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "space_before": Pt(24),
        "space_after": Pt(24),
        "first_line_indent": 0,
        "line_spacing_rule": WD_LINE_SPACING.ONE_POINT_FIVE  # 设置1.5倍行距
    },
    "二级标题": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(14),  # 四号
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "space_before": Pt(12),
        "space_after": Pt(6),
        "first_line_indent": 0
    },
    "三级标题": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(12),  # 小四
        "bold": True,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "space_before": Pt(10),
        "space_after": Pt(6),
        "first_line_indent": 0
    },
    "正文": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(12),  # 小四号
        "alignment": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "space_before": Pt(0),
        "space_after": Pt(0),
        "first_line_indent": Pt(24),  # 首行缩进2个中文字符
        "line_spacing_rule": WD_LINE_SPACING.ONE_POINT_FIVE,
        "line_spacing": Pt(24)  # 1.5倍行距
    },
    "表格标题": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(10.5),  # 五号
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "space_before": Pt(6),
        "space_after": Pt(6),
        "first_line_indent": 0
    },
    "图片标题": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(10.5),  # 五号
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "space_before": Pt(6),
        "space_after": Pt(6),
        "first_line_indent": 0
    },
    "项目符号列表": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(12),  # 小四
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "space_before": Pt(3),
        "space_after": Pt(3),
        "first_line_indent": 0,
        "hanging_indent": True
    },
    "编号列表": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(12),  # 小四
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "space_before": Pt(3),
        "space_after": Pt(3),
        "first_line_indent": 0,
        "hanging_indent": True
    },
    "公司名称": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(18),  # 小二
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "space_before": Pt(6),
        "space_after": Pt(3),
        "first_line_indent": 0
    },
    "日期": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(18),  # 小二
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.CENTER,
        "space_before": Pt(3),
        "space_after": Pt(6),
        "first_line_indent": 0
    },
    "地址": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": SONG_FONT_NAMES,
        "font_size": Pt(12),  # 小四
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "space_before": Pt(3),
        "space_after": Pt(3),
        "first_line_indent": 0
    },
    "邮件": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": TIMES_NEW_ROMAN,  # 英文字体
        "font_size": Pt(12),  # 小四
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "space_before": Pt(3),
        "space_after": Pt(3),
        "first_line_indent": 0
    },
    "电话": {
        "type": WD_STYLE_TYPE.PARAGRAPH,
        "font_names": TIMES_NEW_ROMAN,  # 英文字体
        "font_size": Pt(12),  # 小四
        "bold": False,
        "alignment": WD_ALIGN_PARAGRAPH.LEFT,
        "space_before": Pt(3),
        "space_after": Pt(3),
        "first_line_indent": 0
    }
}

# 表格样式配置
TABLE_STYLE = {
    "header_bg_color": "D9D9D9",
    "border_size": Pt(1),
    "cell_padding": {
        "top": Pt(5),
        "bottom": Pt(5),
        "left": Pt(5),
        "right": Pt(5)
    }
}

# 页面设置
PAGE_SETTINGS = {
    "page_height": Cm(29.7),     # A4纸高度 (297mm)
    "page_width": Cm(21.0),      # A4纸宽度 (210mm)
    "left_margin": Cm(3.18),     # 31.8mm
    "right_margin": Cm(3.18),    # 31.8mm
    "top_margin": Cm(2.54),      # 25.4mm
    "bottom_margin": Cm(2.54),   # 25.4mm
    "header_distance": Cm(1.5),
    "footer_distance": Cm(1.75)
}