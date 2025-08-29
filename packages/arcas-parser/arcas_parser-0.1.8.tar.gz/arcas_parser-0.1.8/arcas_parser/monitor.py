# tested1

# import psutil
# import time
# import threading
# import logging

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# def log_system_usage(interval=5):
#     while True:
#         cpu = psutil.cpu_percent()
#         mem = psutil.virtual_memory().percent
#         disk = psutil.disk_usage('/').percent

#         logging.info(f'CPU: {cpu}% | Memory: {mem}% | Disk: {disk}%')
#         print(f"CPU: {cpu:.1f}% | Memory: {mem:.1f}% | Disk: {disk:.1f}%")
#         time.sleep(interval)

# def start_monitoring(interval=5):
#     t = threading.Thread(target=log_system_usage, args=(interval,), daemon=True)
#     t.start()





# updated2


# monitor.py
import psutil
import time
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

_monitor_thread = None
_stop_monitoring = False

def log_system_usage(interval=5):
    global _stop_monitoring
    while not _stop_monitoring:
        try:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            logging.info(f'CPU: {cpu:.1f}% | Memory: {mem:.1f}% | Disk: {disk:.1f}%')
        except Exception as e:
            logging.error(f"Error monitoring system usage: {e}")
        time.sleep(interval)

def start_monitoring(interval=5):
    global _monitor_thread, _stop_monitoring
    _stop_monitoring = False
    _monitor_thread = threading.Thread(target=log_system_usage, args=(interval,), daemon=True)
    _monitor_thread.start()

def stop_monitoring():
    global _stop_monitoring
    _stop_monitoring = True
    if _monitor_thread:
        _monitor_thread.join(timeout=2)


        


# # tested2

# import psutil
# import time
# import threading
# import logging

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# def log_system_usage(interval=5):
#     while True:
#         cpu = psutil.cpu_percent()
#         mem = psutil.virtual_memory().percent
#         disk = psutil.disk_usage('/').percent

#         logging.info(f'CPU: {cpu}% | Memory: {mem}% | Disk: {disk}%')
#         print(f"CPU: {cpu:.1f}% | Memory: {mem:.1f}% | Disk: {disk:.1f}%")
#         time.sleep(interval)

# def start_monitoring(interval=5):
#     t = threading.Thread(target=log_system_usage, args=(interval,), daemon=True)
#     t.start()





