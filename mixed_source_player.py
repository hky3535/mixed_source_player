"""
何恺悦 hekaiyue 2023-07-07
"""
import os
import cv2


def yield_source_frames(source):

    def yield_local_file(source):
        if source.endswith((".jpg", ".png")):       # 如果读图片
            frame = cv2.imread(source)
            if frame is not None:
                yield True, frame                   # 返回该帧
        elif source.endswith((".mp4", ".avi")):                 # 如果读视频
            local_video_capture = cv2.VideoCapture(source)      # 打开视频
            while True:
                if not local_video_capture: break               # 取流失败或取流停止 退出
                if not local_video_capture.isOpened(): break    # 取流后无法正常打开或取流停止 退出
                ret, frame = local_video_capture.read()         # 读一帧
                if not ret: break                               # 取流并打开后无法正常读取或取流停止 退出
                yield ret, frame                                # 循环返回当前帧
            local_video_capture.release()                       # 推出后 释放视频
        else:
            print("未知本地源文件格式")
        yield False, None                                       # 当前文件取帧结束后返回停止信息

    def yield_local_folder(source):
        source_files_list = list()                          # 获取文件夹下所有文件
        for _, _, files in os.walk(source):
            source_files_list = files.copy()
            source_files_list.sort(key=lambda x: len(x))    # 排列为合理格式

        for source_file in source_files_list:
            current_source_file = yield_local_file(f"{source}/{source_file}")   # 尝试用yield_local_file读取当前文件
            while True:
                ret, frame = next(current_source_file)                          # 循环获取当前文件的帧
                if not ret:         # 取帧失败或取帧停止 退出当前文件 开始下一个文件
                    break
                yield ret, frame    # 循环返回当前帧
        yield False, None           # 全部文件读取完成后返回停止信息

    if os.path.isdir(source):
        return yield_local_folder(source)
    elif os.path.isfile(source):
        return yield_local_file(source)
    else:
        print("本地源文件或文件夹读取失败")


def cameras_thread_main_loop():
    source = "./storage"
    ret_frame = yield_source_frames(source)

    while True:
        ret, frame = next(ret_frame)
        if not ret:
            break
        cv2.imshow("frame", cv2.resize(frame, (640, 480)))
        cv2.waitKey(1)

cameras_thread_main_loop()