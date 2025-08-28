"""
文档生成模块
===========

负责生成Word文档的各个组件，包括：
- 图片处理
- 页面设置
- 段落格式
- 样式设置
- 表格生成
"""

# 延迟导入以避免循环依赖和减少启动时间
# from .images import add_image_to_doc
# from .pages import (
#     set_page_size_to_a4,
#     add_toc,
#     add_header_footer,
#     update_fields_in_word,
#     add_watermark_to_doc
# )
# from .paragraphs import add_paragraph_with_style, add_mixed_font_paragraph
# from .styles import create_styles, create_toc_styles
# from .tables import add_data_table

__all__ = [
    "add_image_to_doc",
    "set_page_size_to_a4",
    "add_toc",
    "add_header_footer",
    "update_fields_in_word",
    "add_watermark_to_doc",
    "add_paragraph_with_style",
    "add_mixed_font_paragraph",
    "create_styles",
    "create_toc_styles",
    "add_data_table",
]