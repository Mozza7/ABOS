from main_ import run_all
from models import return_id
import multiprocessing


def core_init(cores):
    id_list = return_id()
    id_range = len(id_list)
    pool = multiprocessing.Pool(cores)
    for i in pool.imap_unordered(run_all, range(id_range)):
        print('Backup finished:', i)
