import concurrent.futures


def execute_by_multi_thread(tasks, max_workers=8):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        # 提交任务给线程池，并返回 Future 对象列表
        futures = [executor.submit(*task) for task in tasks]
        # 获取任务的结果
        for future in concurrent.futures.as_completed(futures):
            try:
                results.extend(future.result())  # 阻塞等待任务完成并获取结果
            except Exception as e:
                print(f"Exception occurred: {e}")
    return results