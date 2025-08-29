
class ProgressConstants:
    """进度相关常量"""
    MIN_PROGRESS = 0.0
    MAX_PROGRESS = 100.0
    BATCH_UPDATE_SIZE = 100

    # 上传步骤的内部进度分配
    UPLOAD_SAVE_DETAIL = 30
    UPLOAD_S3_DETAIL = 70
    UPLOAD_S3_CHARTS = 90

