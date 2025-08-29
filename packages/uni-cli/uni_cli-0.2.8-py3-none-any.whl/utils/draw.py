import cv2


def rectangle(
    source_path, start_pos, end_pos, save_path, color=(255, 0, 0), thickness=1
):
    """在图片上画矩形框

    Args:
        source_path (str): 源图片路径
        start_pos (tuple): 左上角坐标 (x1, y1)
        end_pos (tuple): 右下角坐标 (x2, y2)
        save_path (str): 保存的新图片路径
        color (tuple): BGR颜色值
        thickness (int): 线条粗细,默认2
    """
    # 读取源图片
    img = cv2.imread(source_path)

    if img is None:
        print(f"💊 无法读取图片: {source_path}")
        return

    # 画矩形
    cv2.rectangle(
        img,
        start_pos,  # 左上角坐标
        end_pos,  # 右下角坐标
        color,  # BGR颜色值
        thickness,  # 线条粗细
    )

    # 保存结果
    cv2.imwrite(save_path, img)
    print(f"✅ 已保存标注图片: {save_path}")
