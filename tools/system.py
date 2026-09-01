import psutil


def system_status():
    cpu = psutil.cpu_percent(interval=0.2)
    memory = psutil.virtual_memory()

    return (
        f"CPU usage is {cpu:.0f} percent. "
        f"Memory usage is {memory.percent:.0f} percent."
    )
