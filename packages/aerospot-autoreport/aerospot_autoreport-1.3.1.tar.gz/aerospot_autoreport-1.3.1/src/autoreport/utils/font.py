from docx.shared import Pt
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from ..config.fonts import SONG_FONT_NAMES, TIMES_NEW_ROMAN, HEI_FONT_NAMES
import logging

# 获取模块日志记录器
logger = logging.getLogger(__name__)

def apply_font(run, font_name, size=None, bold=None, italic=None):
    """应用字体样式到文本
    
    Args:
        run: 文本对象
        font_name: 字体名称
        size: 字体大小（磅值）
        bold: 是否加粗
        italic: 是否斜体
    """
    # 设置字体名称
    run.font.name = font_name
    
    # 设置东亚字体
    rpr = run._element.get_or_add_rPr()
    if 'Song' in font_name or '宋' in font_name:
        rpr.rFonts.set(qn('w:eastAsia'), font_name)
    
    # 设置字体大小
    if size is not None:
        run.font.size = Pt(size)
    
    # 设置字体粗细
    if bold is not None:
        run.font.bold = bold
    
    # 设置字体样式
    if italic is not None:
        run.font.italic = italic

def set_default_font(doc):
    """设置文档默认字体为宋体(中文)和Times New Roman(英文和数字)"""
    # 修改Normal样式（默认样式）
    normal_style = doc.styles['Normal']
    
    # 设置西文字体为Times New Roman
    normal_style.font.name = "Times New Roman"
    
    # 设置东亚文字字体为宋体
    rpr = normal_style._element.get_or_add_rPr()
    rpr.rFonts.set(qn('w:eastAsia'), SONG_FONT_NAMES[0])
    
    # 确保ASCII字体是Times New Roman
    rpr.rFonts.set(qn('w:ascii'), "Times New Roman")
    # 设置非Unicode字符的字体
    rpr.rFonts.set(qn('w:hAnsi'), "Times New Roman")
    # 设置高位ASCII字符的字体
    rpr.rFonts.set(qn('w:cs'), "Times New Roman")
    
    # 设置默认字体大小为小四号(12pt)
    normal_style.font.size = Pt(12)
    
    # 设置默认段落格式，优化分段显示
    normal_style.paragraph_format.space_before = Pt(0)  # 段前间距为0
    normal_style.paragraph_format.space_after = Pt(0)   # 段后间距为0
    normal_style.paragraph_format.first_line_indent = Pt(24)  # 首行缩进(2个中文字符)
    
    from docx.enum.text import WD_LINE_SPACING
    normal_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE  # 1.5倍行距
    normal_style.paragraph_format.line_spacing = Pt(24)  # 设置具体行距值
    
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY  # 两端对齐
    
    logger.info(f"已将文档默认字体设置为：中文-{SONG_FONT_NAMES[0]}，英文和数字-Times New Roman")
    return doc

def get_font_by_name(font_name):
    """根据字体名称获取字体对象
    
    Args:
        font_name: 字体名称或字体类型描述
        
    Returns:
        字体名称字符串
    """
    if font_name.lower() in ['song', 'simsun', '宋体', 'songti']:
        return SONG_FONT_NAMES[0]
    elif font_name.lower() in ['hei', 'simhei', '黑体', 'heiti']:
        return HEI_FONT_NAMES[0]
    elif font_name.lower() in ['times', 'times new roman', 'roman', 'tnr']:
        return TIMES_NEW_ROMAN
    else:
        # 无法识别时默认返回宋体
        return SONG_FONT_NAMES[0]


# 导出所有符号以保持向后兼容性
__all__ = [
    'apply_font',
    'set_default_font',
    'get_font_by_name'
]