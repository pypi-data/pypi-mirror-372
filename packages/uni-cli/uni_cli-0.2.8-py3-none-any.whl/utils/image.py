import base64

import cv2
import imagehash
import numpy as np
from PIL import Image


def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        # 读取图片文件并转换为base64
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode("utf-8")  # 转换为字符串


def calculate_similarity(image_path: str, template_path: str, region: tuple) -> float:
    """
    计算指定区域与模板图片的相似度
    这个calculate_similarity方法使用了OpenCV的模板匹配方法
    (Template Matching),具体使用了cv2.matchTemplate函数,匹配模式为cv2.TM_CCOEFF_NORMED。

    Args:
        image_path (str): 原始图片路径
        template_path (str): 模板图片路径
        region (tuple): 指定区域的左上角和右下角坐标 (x1, y1, x2, y2)

    Returns:
        float: 相似度得分
    """
    # 读取图片
    image = cv2.imread(image_path)
    template = cv2.imread(template_path)

    # 裁剪指定区域
    x1, y1, x2, y2 = region
    cropped_image = image[y1:y2, x1:x2]

    # 调整模板大小与裁剪区域一致
    template_resized = cv2.resize(template, (x2 - x1, y2 - y1))

    # 计算相似度
    result = cv2.matchTemplate(cropped_image, template_resized, cv2.TM_CCOEFF_NORMED)
    similarity = np.max(result)

    return similarity


def calculate_similarity_histogram(
    image_path: str, template_path: str, region: tuple
) -> float:
    """
    使用直方图比较计算图片相似度
    通过比较图像的颜色直方图来计算相似度
    直方图比较法:
    优点：计算速度快，对图像旋转和缩放有一定的容忍度
    缺点：不考虑图像的空间信息，可能会出现误判

    Args:
        image_path (str): 原始图片路径
        template_path (str): 模板图片路径
        region (tuple): 指定区域的左上角和右下角坐标 (x1, y1, x2, y2)

    Returns:
        float: 相似度得分 (0-1之间)
    """
    # 读取图片
    image = cv2.imread(image_path)
    template = cv2.imread(template_path)

    # 裁剪区域
    x1, y1, x2, y2 = region
    cropped_image = image[y1:y2, x1:x2]
    template_resized = cv2.resize(template, (x2 - x1, y2 - y1))

    # 计算直方图
    hist1 = cv2.calcHist(
        [cropped_image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]
    )
    hist2 = cv2.calcHist(
        [template_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]
    )

    # 归一化直方图
    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)

    # 计算相似度
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return similarity


def calculate_similarity_features(
    image_path: str, template_path: str, region: tuple
) -> float:
    """
    使用特征点匹配计算图片相似度
    使用特征检测和描述符（如 SIFT、SURF、ORB)来匹配图像中的关键点。
    特征点匹配法:
    优点：对图像旋转、缩放、视角变化都有很好的鲁棒性
    缺点：计算量较大，速度相对较慢
    Args:
        image_path (str): 原始图片路径
        template_path (str): 模板图片路径
        region (tuple): 指定区域的左上角和右下角坐标 (x1, y1, x2, y2)

    Returns:
        float: 相似度得分 (0-1之间)
    """
    # 读取图片
    image = cv2.imread(image_path)
    template = cv2.imread(template_path)

    # 裁剪区域
    x1, y1, x2, y2 = region
    cropped_image = image[y1:y2, x1:x2]
    template_resized = cv2.resize(template, (x2 - x1, y2 - y1))

    # 创建SIFT检测器
    sift = cv2.SIFT_create()

    # 检测关键点和描述符
    kp1, des1 = sift.detectAndCompute(cropped_image, None)
    kp2, des2 = sift.detectAndCompute(template_resized, None)

    if des1 is None or des2 is None:
        return 0.0

    # 创建FLANN匹配器
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # 进行匹配
    matches = flann.knnMatch(des1, des2, k=2)

    # 应用Lowe's ratio测试找到好的匹配
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    # 计算相似度得分
    similarity = len(good_matches) / max(len(kp1), len(kp2))
    return similarity


def calculate_similarity_phash(
    image_path: str, template_path: str, region: tuple
) -> float:
    """
    使用感知哈希计算图片相似度
    通过生成图像的感知哈希值来比较图像。
    使用 imagehash 库。
    感知哈希法:
    优点：计算速度快，存储空间小，对图像的细微变化不敏感
    缺点：对图像的旋转和大幅度变化比较敏感

    Args:
        image_path (str): 原始图片路径
        template_path (str): 模板图片路径
        region (tuple): 指定区域的左上角和右下角坐标 (x1, y1, x2, y2)

    Returns:
        float: 相似度得分 (0-1之间)
    """
    # 读取图片
    image = Image.open(image_path)
    template = Image.open(template_path)

    # 裁剪区域
    x1, y1, x2, y2 = region
    cropped_image = image.crop((x1, y1, x2, y2))
    template_resized = template.resize((x2 - x1, y2 - y1))

    # 计算感知哈希
    hash1 = imagehash.average_hash(cropped_image)
    hash2 = imagehash.average_hash(template_resized)

    # 计算汉明距离并转换为相似度
    max_bits = len(str(hash1)) * 4  # 哈希值的位数
    hamming_distance = hash1 - hash2
    similarity = 1 - (hamming_distance / max_bits)

    return similarity
