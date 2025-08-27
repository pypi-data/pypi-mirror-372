import concurrent.futures
import json, traceback, pretty_errors, asyncio
import gc
import multiprocessing
import tkinter as tk
import queue

from .web_api import AsyncApiClient
import threading, time, copy
from typing import Callable, Optional


class YuanmeiJob:
    def __init__(self,
                 jobId: str,
                 status: str,
                 companyCode: str,
                 platform: str,
                 queueName: str,
                 jobData: str,
                 resultData: str,
                 msg: str,
                 fileName: str,
                 errorFile: str,
                 shopId: int,
                 startDate: int,
                 endDate: int,
                 totalTime: int,
                 createDate: int,
                 successCount: int,
                 errorCount: int,
                 errorMsg: str,
                 taskName: str,
                 requestId: str,
                 createStaffId: str,
                 lastHeartbeatTime: int,
                 jobLockKey: str
                 ):
        self.jobId = jobId
        self.status = status
        self.companyCode = companyCode
        self.platform = platform
        self.queueName = queueName
        self.jobData = jobData
        self.resultData = resultData
        self.msg = msg
        self.fileName = fileName
        self.errorFile = errorFile
        self.shopId = shopId
        self.startDate = self.date_str_to_int(startDate)
        self.endDate = self.date_str_to_int(endDate)
        self.totalTime = totalTime
        self.createDate = self.date_str_to_int(createDate)
        self.successCount = successCount
        self.errorCount = errorCount
        self.errorMsg = errorMsg
        self.taskName = taskName
        self.requestId = requestId
        self.createStaffId = createStaffId
        self.lastHeartbeatTime = self.date_str_to_int(lastHeartbeatTime)
        self.jobLockKey = jobLockKey
        # 临时信息
        self.error_msg_list = []
        self.log_list = []

    @staticmethod
    def date_str_to_int(date_str):
        if type(date_str) == str:
            return int(time.mktime(time.strptime(date_str, '%Y-%m-%d %H:%M:%S')))
        else:
            return date_str

    @staticmethod
    def date_int_to_str(obj: dict):
        for key in ["startDate", "endDate", "createDate", "lastHeartbeatTime"]:
            if obj.get(key):
                if len(str(obj[key])) == 10:
                    lt = time.localtime(obj[key])
                else:
                    lt = time.localtime(obj[key] / 1000)
                obj[key] = time.strftime('%Y-%m-%d %H:%M:%S', lt)

    def sum_total_time(self):
        self.totalTime = self.endDate - self.startDate

    def to_json(self):
        res_json = copy.deepcopy(self.__dict__)
        self.date_int_to_str(res_json)
        if self.error_msg_list is not None:
            self.errorMsg = json.dumps(self.error_msg_list, ensure_ascii=False)
        return res_json

    def get_job_vars(self):
        local_vars = {}
        if self.jobData:
            job_data = json.loads(self.jobData)
            for job_param in job_data:
                if job_param.get("yingdaoFlag"):
                    local_vars[job_param.get("name")] = job_param.get("value")
        return local_vars


class AutoRefreshWindow:
    def __init__(self, initial_text="", refresh_interval=1000):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg="black")

        # 确保窗口尺寸正确
        self.root.update_idletasks()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.window_height = max(self.screen_height // 30, 20)
        self.root.geometry(f"{self.screen_width}x{self.window_height}+0+0")

        # 字体设置
        self.font_size = max(self.window_height // 2, 10)

        # 内容标签
        self.label = tk.Label(
            self.root,
            text=initial_text,
            font=("Arial", self.font_size, "bold"),
            fg="white",
            bg="black",
            justify="center"
        )
        self.label.pack(expand=True, fill=tk.BOTH)

        # 拖拽功能
        self.drag_data = {"start_y": 0, "dragging": False}
        self.label.bind("<ButtonPress-1>", self.start_drag)
        self.label.bind("<ButtonRelease-1>", self.stop_drag)
        self.label.bind("<B1-Motion>", self.on_drag)

        # 刷新控制
        self.refresh_interval = refresh_interval
        self.is_running = True
        self._after_id = None

        # 消息队列（用于线程间通信）
        self.message_queue = queue.Queue()

    def start_drag(self, event):
        self.drag_data["start_y"] = event.y_root
        self.drag_data["dragging"] = True

    def stop_drag(self, event):
        self.drag_data["dragging"] = False

    def on_drag(self, event):
        if self.drag_data["dragging"]:
            delta = event.y_root - self.drag_data["start_y"]
            new_y = self.root.winfo_y() + delta
            new_y = max(0, min(new_y, self.screen_height - self.window_height))
            self.root.geometry(f"+0+{new_y}")
            self.drag_data["start_y"] = event.y_root

    def update_content(self, new_text: str = None):
        if not self.is_running:
            return
        self.label.config(text=new_text)
        self._after_id = self.root.after(self.refresh_interval, self.update_content)

    def safe_call(self, func, *args):
        self.root.after(0, func, *args)

    def check_queue(self):
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get_nowait()
                if message == "SHOW":
                    self.root.deiconify()
                elif message == "DESTROY":
                    self.is_running = False
                    self.root.after_cancel(self._after_id)
                    self.root.destroy()
                    return
        except queue.Empty:
            pass

        if self.is_running:
            self.root.after(100, self.check_queue)

    def show(self):
        self.message_queue.put("SHOW")

    def destroy(self):
        self.message_queue.put("DESTROY")

    async def start_mainloop(self):
        self.safe_call(self.show)
        self.safe_call(self.check_queue)
        self.root.mainloop()


class AsyncConsumer:
    def __init__(self, api_client: AsyncApiClient, queue_name: str = None, _print: Callable = print, consumer_name: str = "AsyncConsumer"):
        self.api_client = api_client
        self.queue_name = queue_name
        self.print = _print
        self.currentJob: Optional[YuanmeiJob] = None
        self.consumer_running = True
        self.heart_beat_task: Optional[asyncio.Task] = None
        self.async_run_consumer_task: Optional[asyncio.Task] = None
        self.auto_refresh_window: Optional[AutoRefreshWindow] = None
        self.consumer_name = consumer_name
        # 使用线程池执行同步代码
        self.loop = asyncio.get_running_loop()

    async def start(self):
        """启动消费者"""
        # 启动心跳任务
        self.heart_beat_task = asyncio.create_task(self.heart_beat_loop())
        # 启动主任务处理循环
        await self.async_run()

    async def async_run(self):
        self.auto_refresh_window = AutoRefreshWindow(
            initial_text="消费者已经启动..等待任务中",
            refresh_interval=1000
        )
        self.async_run_consumer_task = asyncio.create_task(self.async_run_consumer_loop())
        # 启动gui
        return self.auto_refresh_window.start_mainloop()

    async def async_run_consumer_loop(self):
        """异步任务处理循环"""
        while self.consumer_running:
            try:
                await self.get_job()
                if self.currentJob:
                    app_code, max_exec_time = await self.get_app_code()
                    self.auto_refresh_window.update_content(f"正在执行任务:{self.currentJob.jobId}")
                    try:
                        await self.start_job()
                        # 准备执行环境
                        local_vars = self.currentJob.get_job_vars()
                        local_vars["log"] = self.log
                        local_vars["error_log"] = self.error_log
                        local_vars["api_client"] = self.api_client
                        local_vars["job"] = self.currentJob
                        # 执行用户代码 - 在单独的线程中执行以避免阻塞事件循环
                        code_block = "def run_code():\n"
                        for line in str(app_code).splitlines():
                            code_block += f"\t{line}\n"
                        code_block += "run_code()"
                        exec_time_out_flag = await self.async_run_time_out(code_block, local_vars, max_exec_time)
                        if not exec_time_out_flag:
                            error_msg = f"任务执行超时, 超过最大执行时间: {int(max_exec_time)}秒"
                            await self.error_log(error_msg)
                            await self.error_job()
                        # 检查任务结果
                        elif exec_time_out_flag and self.currentJob.errorCount == 0:
                            await self.end_job("SUCCESS")
                        else:
                            await self.error_job()
                    except Exception as ex:
                        await self.error_log(traceback.format_exc())
                        await self.error_job()
                    finally:
                        await self.update_job()
                else:
                    self.auto_refresh_window.update_content("等待新任务...")
                    await asyncio.sleep(10)
            except Exception as e:
                self.print(f"主循环异常: {traceback.format_exc()}")
            finally:
                # 清理当前任务
                self.currentJob = None
                gc.collect()  # 强制垃圾回收，清理内存

    async def async_run_time_out(self, code_block, local_vars=None, max_exec_time: int = 60 * 60 * 3):
        if local_vars is None:
            local_vars = {}
        process = multiprocessing.Process(
            target=self.execute_user_code,
            args=(code_block, local_vars)
        )
        process.start()
        start_time = time.time()
        try:
            while process.is_alive():
                # 等待 2 秒
                if (time.time() - start_time) >= max_exec_time and process.is_alive():
                    process.terminate()  # 强制终止
                    process.join()  # 等待进程资源回收
                    self.print("任务超时，强制终止进程")
                    return False
                else:
                    await asyncio.sleep(1.0)
        finally:
            if process.is_alive():
                process.terminate()
        return True

    def execute_user_code(self, code_block: str, local_vars: dict):
        """在单独的线程中执行用户代码"""
        try:
            exec(code_block, local_vars, local_vars)
        except Exception as ex:
            # 捕获用户代码中的异常
            error_msg = traceback.format_exc()
            self.currentJob.error_msg_list.append(error_msg)
            self.currentJob.errorCount += 1
            self.print(f"用户代码执行错误: {error_msg}")

    async def update_result_data(self, local_vars: dict):
        """更新任务结果数据"""
        result_data = {}
        for key in local_vars:
            if type(local_vars.get(key)) in [str, int, float, dict, list]:
                result_data[key] = local_vars.get(key)

        if self.currentJob:
            self.currentJob.resultData = json.dumps(result_data, ensure_ascii=False)
            await self.update_job()

    async def log(self, msg: str):
        """记录日志"""
        if self.currentJob:
            self.currentJob.log_list.append(msg)
            self.currentJob.msg = msg
            self.print(msg)
            await self.update_job()

    async def error_log(self, error_msg: str):
        """记录错误日志"""
        if self.currentJob:
            self.currentJob.error_msg_list.append(error_msg)
            self.currentJob.errorCount += 1
            self.print(error_msg)
            await self.update_job()

    async def start_job(self):
        """标记任务开始"""
        if self.currentJob:
            self.currentJob.status = "PROCESS"
            self.currentJob.startDate = int(time.time() * 1000)
            org_task_name = str(self.currentJob.taskName).split("-")[0].strip()
            self.currentJob.taskName = f"{org_task_name}-{self.consumer_name}"
            await self.update_job()

    @staticmethod
    def convert_milliseconds_to_hms(milliseconds: int) -> str:
        """将毫秒转换为小时:分钟:秒格式"""
        seconds = milliseconds / 1000.0
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}小时 {minutes}分钟 {secs}秒"

    async def end_job(self, status: str = "SUCCESS"):
        """结束任务"""
        if self.currentJob:
            self.currentJob.status = status
            self.currentJob.endDate = int(time.time() * 1000)
            self.currentJob.sum_total_time()

            duration_str = self.convert_milliseconds_to_hms(self.currentJob.totalTime)
            if status == "ERROR":
                self.currentJob.msg = f"机器人: {self.consumer_name} {self.currentJob.taskName}-任务执行失败, 耗时{duration_str}"
            else:
                self.currentJob.msg = f"机器人: {self.consumer_name} {self.currentJob.taskName}-任务执行成功, 耗时{duration_str}"
            await self.update_job()

    async def error_job(self):
        """标记任务失败"""
        await self.end_job("ERROR")

    async def heart_beat_loop(self):
        """心跳循环任务"""
        while self.consumer_running:
            try:
                await self.heart_beat()
                await asyncio.sleep(60)  # 每60秒发送一次心跳
            except asyncio.CancelledError:
                break
            except Exception as ex:
                self.print(f"心跳任务异常: {traceback.format_exc()}")

    async def heart_beat(self):
        """发送心跳"""
        if self.currentJob and self.currentJob.jobId:
            await self.api_client.post(
                "/YuanmeiJob/open/sendHeartbeat",
                {"jobId": self.currentJob.jobId}
            )
        self.auto_refresh_window.update_content(f"{('正在执行任务: ' + self.currentJob.jobId) if self.currentJob else '等待新任务.....'}")

    async def get_job(self) -> Optional[YuanmeiJob]:
        """获取一个待处理任务"""
        req_url = "/YuanmeiJob/open/getOneWaitJob"
        if self.queue_name:
            req_url += f"?queueName={self.queue_name}"

        job_result = await self.api_client.get(req_url)
        if job_result:
            self.print(f"获取任务成功:{json.dumps(job_result, ensure_ascii=False)}")
            # 移除不需要的字段
            job_result.pop("id", None)
            job_result.pop("isDel", None)
            self.currentJob = YuanmeiJob(**job_result)
            return self.currentJob
        return None

    async def get_app_code(self) -> (str, int):
        """获取任务关联的应用程序代码"""
        if self.currentJob and self.currentJob.queueName:
            app_data = await self.api_client.get(
                "/YuanmeiYingdaoApp/open/getApp",
                request_params={"queueName": self.currentJob.queueName}
            )
            return app_data.get("pythonCodeBlock", ""), app_data.get("maxExecTime", 60 * 60 * 3)
        raise Exception("未知任务队列")

    async def update_job(self):
        """更新任务状态"""
        if self.currentJob:
            job_json = self.currentJob.to_json()
            await self.api_client.post_json(
                "/YuanmeiJob/open/updateJob",
                request_json=job_json
            )

    async def close(self):
        """关闭消费者并清理资源"""
        self.consumer_running = False

        # 取消心跳任务
        if self.heart_beat_task and not self.heart_beat_task.done():
            self.heart_beat_task.cancel()
            try:
                await self.heart_beat_task
            except asyncio.CancelledError:
                pass

        # 关闭API客户端
        await self.api_client.close()
