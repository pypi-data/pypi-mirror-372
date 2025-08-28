import logging
from docx import Document
from docx.shared import Pt
from ..config.styles import STYLE_CONFIGS
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from ..config.fonts import SONG_FONT_NAMES

# 获取模块日志记录器
logger = logging.getLogger(__name__)

def apply_paragraph_style(paragraph, style_name, alignment=None):
    """应用段落样式
    
    Args:
        paragraph: 段落对象
        style_name: 样式名称
        alignment: 对齐方式
    """
    if style_name:
        paragraph.style = style_name
    
    if alignment is not None:
        paragraph.alignment = alignment

def set_paragraph_spacing(paragraph, before=None, after=None, line_spacing=None):
    """设置段落间距
    
    Args:
        paragraph: 段落对象
        before: 段前间距（磅值）
        after: 段后间距（磅值）
        line_spacing: 行间距（磅值）
    """
    if before is not None:
        paragraph.paragraph_format.space_before = Pt(before)
    
    if after is not None:
        paragraph.paragraph_format.space_after = Pt(after)
    
    if line_spacing is not None:
        paragraph.paragraph_format.line_spacing = Pt(line_spacing)

def create_styles(doc):
    """根据配置创建文档样式"""
    # 标题样式大纲级别映射
    outline_levels = {
        "一级标题": 1,
        "二级标题": 2,
        "三级标题": 3
    }
    
    for style_name, style_config in STYLE_CONFIGS.items():
        logger.info(f"  创建样式 '{style_name}'")
        
        if style_name in doc.styles:
            style = doc.styles[style_name]
        else:
            style = doc.styles.add_style(style_name, style_config["type"])
        
        # 设置字体
        font = style.font
        font.name = style_config["font_names"][0]
        font.size = style_config["font_size"]
        font.bold = style_config.get("bold", False)
        
        # 设置东亚文字字体
        rpr = style._element.get_or_add_rPr()
        if hasattr(rpr, 'rFonts'):
            rpr.rFonts.set(qn('w:eastAsia'), style_config["font_names"][0])
        
        # 设置段落格式
        if style_config["type"] == WD_STYLE_TYPE.PARAGRAPH:
            paragraph_format = style.paragraph_format
            paragraph_format.alignment = style_config.get("alignment")
            paragraph_format.space_before = style_config.get("space_before")
            paragraph_format.space_after = style_config.get("space_after")
            paragraph_format.first_line_indent = style_config.get("first_line_indent", 0)
            
            if "line_spacing_rule" in style_config:
                paragraph_format.line_spacing_rule = style_config["line_spacing_rule"]
            
            # 正文样式特殊处理 - 确保使用配置中的值
            if style_name == "正文":
                # 注意这里不再硬编码值，而是使用配置中的值
                paragraph_format.space_before = style_config.get("space_before", Pt(0))
                paragraph_format.space_after = style_config.get("space_after", Pt(0))
                paragraph_format.first_line_indent = style_config.get("first_line_indent", Pt(24))
                
                from docx.enum.text import WD_LINE_SPACING
                paragraph_format.line_spacing_rule = style_config.get("line_spacing_rule", WD_LINE_SPACING.ONE_POINT_FIVE)
                paragraph_format.line_spacing = style_config.get("line_spacing", Pt(24))
                
                from docx.enum.text import WD_ALIGN_PARAGRAPH
                paragraph_format.alignment = style_config.get("alignment", WD_ALIGN_PARAGRAPH.JUSTIFY)
            
            # 设置标题大纲级别
            if style_name in outline_levels:
                # 使用XML方式设置大纲级别
                pPr = style._element.get_or_add_pPr()
                
                # 删除已有的大纲级别设置（如果有）
                for old_outline in pPr.xpath('w:outlineLvl'):
                    pPr.remove(old_outline)
                
                # 添加新的大纲级别设置
                outline_lvl = OxmlElement('w:outlineLvl')
                outline_lvl.set(qn('w:val'), str(outline_levels[style_name] - 1))  # Word中大纲级别从0开始
                pPr.append(outline_lvl)
                logger.info(f"  已设置'{style_name}'的大纲级别为{outline_levels[style_name]}")
    
    logger.info("样式创建完成")
    return doc

def apply_styles_to_document(doc: Document) -> Document:
    """应用样式到文档
    
    Args:
        doc: 文档对象
        
    Returns:
        应用样式后的文档对象
    """
    logger.info("开始应用样式到文档")
    
    # 创建基本样式
    create_styles(doc)
    
    # 创建目录样式
    create_toc_styles(doc)
    
    logger.info("样式应用完成")
    return doc

def create_toc_styles(doc):
    """设置目录样式使用宋体"""
    # 设置TOC样式使用宋体
    for i in range(1, 4):  # 处理三级目录
        toc_style_name = f'TOC{i}'
        if toc_style_name in doc.styles:
            style = doc.styles[toc_style_name]
            
            # 设置目录字体大小和字体
            font = style.font
            font.name = SONG_FONT_NAMES[0]
            font.size = Pt(10.5)  # 五号字体
            
            # 设置东亚文字字体
            rpr = style._element.get_or_add_rPr()
            if hasattr(rpr, 'rFonts'):
                rpr.rFonts.set(qn('w:eastAsia'), SONG_FONT_NAMES[0])
            
            logger.info(f"已设置目录样式 {toc_style_name} 为宋体五号")
    
    logger.info("目录样式设置完成")
    return doc


# 导出所有符号以保持向后兼容性
__all__ = [
    'set_paragraph_spacing',
    'apply_paragraph_style',
    'create_styles',
    'apply_styles_to_document',
    'create_toc_styles'
] 