import os
import cv2
import numpy as np
import tkinter as tk
from pathlib import Path
import concurrent.futures
from tkinter import filedialog
from tkinter.ttk import Progressbar


class ImageProcessor:
    def __init__(self):
        self.input_folder = ""
        self.output_folder = ""
        self.image_files = []
        self.total_images = 0

        # 创建 GUI 窗口
        self.root = tk.Tk()
        self.root.title("Image Processor")

        # 输入文件夹选择按钮和文本框
        self.input_folder_label = tk.Label(self.root, text="输入文件夹：")
        self.input_folder_label.pack()
        self.input_folder_entry = tk.Entry(self.root, width=80)
        self.input_folder_entry.pack()
        self.input_folder_button = tk.Button(self.root, text="选择文件夹", command=self.choose_input_folder)
        self.input_folder_button.pack()

        # 输出文件夹选择按钮和文本框
        self.output_folder_label = tk.Label(self.root, text="输出文件夹：")
        self.output_folder_label.pack()
        self.output_folder_entry = tk.Entry(self.root, width=80)
        self.output_folder_entry.pack()
        self.output_folder_button = tk.Button(self.root, text="选择文件夹", command=self.choose_output_folder)
        self.output_folder_button.pack()

        # 进度条
        self.progressbar = Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progressbar.pack()

        # 开始按钮
        self.start_button = tk.Button(self.root, text="开始处理", command=self.process_images)
        self.start_button.pack()

        self.root.mainloop()

    def choose_input_folder(self):
        self.input_folder = filedialog.askdirectory()
        self.input_folder_entry.delete(0, tk.END)
        self.input_folder_entry.insert(0, self.input_folder)

    def choose_output_folder(self):
        self.output_folder = filedialog.askdirectory()
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, self.output_folder)

    def process_image(self, image_file):
        input_path = Path(self.input_folder) / Path(image_file)
        output_path = Path(self.output_folder) / Path(image_file)

        # 使用 OpenCV 处理图像，直方图均衡化和增强对比度操作
        img = cv2.imread(str(input_path))

        # # 增强对比度
        alpha = 1.5  # 可调整增强对比度的倍数
        beta = -0.5    # 可调整增强亮度的值
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

        # 定义拉普拉斯滤波器的卷积核
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        img = cv2.filter2D(img, 1, kernel)

        # # 定义膨胀腐蚀的卷积核
        # kernel = np.ones((3, 3), np.uint8)
        #
        # # 腐蚀掉黑色方块以外的区域
        # img = cv2.erode(img, kernel, iterations=1)  # 膨胀
        # img = cv2.dilate(img, kernel, iterations=1)  # 腐蚀

        # 将处理后的图像保存到输出文件夹
        cv2.imwrite(str(output_path), img)

    def process_images(self):
        # 获取输入文件夹中的所有图片文件
        self.image_files = os.listdir(self.input_folder)
        self.total_images = len(self.image_files)

        # 统计pdf总数，设置进度条最大值
        self.progressbar['maximum'] = self.total_images
        print(self.total_images)

        # 使用ProcessPoolExecutor处理图像
        with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:

            # 线程保存
            futures = []

            for i, img_file in enumerate(self.image_files):

                # 创建线程
                futures.append(executor.submit(self.process_image, img_file))

                # 更新进度条
                self.progressbar['value'] = i + 1
                self.progressbar.update()

            # 等待所有任务完成
            concurrent.futures.wait(futures)
            print('success!')


if __name__ == "__main__":
    ImageProcessor()
