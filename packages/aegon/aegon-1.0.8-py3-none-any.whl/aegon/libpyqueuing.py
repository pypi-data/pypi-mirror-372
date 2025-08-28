import queue
import time
import subprocess
from multiprocessing import Process, Queue, current_process
# ------------------------------------------------------------------------------------------
import warnings
import logging
# Configuración de advertencias y logging
warnings.filterwarnings("ignore")
logging.captureWarnings(True)
# ------------------------------------------------------------------------------------------
def execute_bash(tasks_to_accomplish, tasks_that_are_done):
    """Ejecuta archivos de ordenes bash en paralelo."""
    while True:
        try:
            task = tasks_to_accomplish.get_nowait()
        except queue.Empty:
            break
        else:
            try:
                subprocess.run(f"bash {task}", shell=True, check=True)
                tasks_that_are_done.put(f"{task} calculated by {current_process().name}")
            except subprocess.CalledProcessError as e:
                print(f"Error executing bash for {task}: {e}")
            time.sleep(0.01)  # Pequeña pausa para evitar sobrecargar el sistema

# ------------------------------------------------------------------------------------------
def parallel_bash_execution(list_of_sh_files, NparCalcs=4):
    """Ejecuta cálculos en paralelo usando multiprocessing."""
    tasks_to_accomplish = Queue()
    tasks_that_are_done = Queue()
    processes = []

    for sh_file in list_of_sh_files:
        tasks_to_accomplish.put(sh_file)

    for _ in range(NparCalcs):
        p = Process(target=execute_bash, args=(tasks_to_accomplish, tasks_that_are_done))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    while not tasks_that_are_done.empty():
        print(tasks_that_are_done.get())

# ------------------------------------------------------------------------------------------
#import glob
#cases_list=['stage2'+str(i+1).zfill(5) for i in range(45)]
#output_files = sorted(glob.glob("stage2[0-9][0-9][0-9][0-9][0-9].out"))
#shfiles_to_send = [ibname+'.sh' for ibname in cases_list if ibname+'.out' not in output_files]
#parallel_bash_execution(shfiles_to_send, NparCalcs=2)
