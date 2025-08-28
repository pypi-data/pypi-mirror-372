import os
# 定义默认图片资源目录路径
DEFAULT_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "images")

DEFAULT_COMPANY_INFO = {
    "name": "无锡谱视界科技有限公司",
    "address": "江苏省无锡市新吴区菱湖大道200号E2-111",
    "email": "company@specvision.com.cn",
    "phone": "0510-85290662",
    "logo_path": os.path.join(DEFAULT_IMAGES_DIR, "logo.png"),
    "watermark_path": os.path.join(DEFAULT_IMAGES_DIR, "waterpicture.png"),
    "profile": """无锡谱视界科技有限公司（以下简称谱视界）2021年成立于无锡，由江苏双利合谱科技有限公司和长春长光辰谱科技有限公司及核心团队成员共同出资组建。谱视界以江苏双利合谱科技有限公司和长春长光辰谱科技有限公司领先的光谱技术实力作为支撑，是国内唯一一家以光谱滤光片为核心分光元件，聚焦光谱相机小型化、轻量化、集成化的高光谱系统解决方案的光电科技公司。产品广泛应用于机载高光谱、精细农业、工业分选、刑侦物证鉴定、考古、食品检测等领域。
    随着人们对水环境质量的要求不断提高，河湖水质监测也需要向精细化、全面化方向发展。无人机智能机场光谱遥感技术能够提供高分辨率的水质信息，满足对河湖水质精细化管理的需求，为制定科学合理的水环境治理方案提供依据。无锡谱视界科技有限公司根据不同领域的市场需求，推出了智能小型机载光谱指数分析基站AeroSpot全自动智能光谱感知无人机场系统。""",
    # Spire.Doc水印配置
    "watermark_enabled": True,           # 是否启用水印
    "watermark_text": "无锡谱视界科技有限公司",        # 水印文本
    "watermark_size": 65,                # 水印字体大小
    "watermark_color": (200, 0, 0),      # 水印颜色，RGB格式
    "watermark_diagonal": True,          # 是否使用对角线布局
    "watermark_use_spire": True          # 是否使用Spire.Doc添加水印
}