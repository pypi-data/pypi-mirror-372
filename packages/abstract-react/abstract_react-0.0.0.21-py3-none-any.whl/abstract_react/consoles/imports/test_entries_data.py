from abstract_utilities import *
from functions import get_entry_output,parse_tsc_output
ABS_PATH = os.path.abspath(__file__)
ABS_DIR = os.path.dirname(ABS_PATH)
TEST_PATH = os.path.join(ABS_DIR,'test_entries.txt')
TEST_ENTRIES = read_from_file(TEST_PATH)

def get_tsc_output(entries = None):
    entries = entries or TEST_ENTRIES
    # parse & split to errors/warnings for filtering and lists
    # parse & split to errors/warnings for filtering and lists
    res = parse_tsc_output(entries)
    return res
 
def get_data_string(data_input=None):
    data_input = data_input or TEST_DATA
    all_datas = {}
    for key,values in data_input.items():
        string = f"data == {key}\n"
        string += f"VALUES:\n"
        for datas in values:
            if isinstance(datas,dict):
                for typkey,typval in datas.items():
                    string += f"{typkey} == {typval}\n"
         
            string += '\n'
        all_datas[key] = string
    return all_datas
TSC_DATA = get_tsc_output(TEST_ENTRIES)

TEST_DATA = get_entry_output(TEST_ENTRIES)
DATA_LIST = get_data_string()
def display_data_string(key,data_js = None):
    data_js = data_js or DATA_LIST
    types = list(data_js.keys())
    if key not in types:
        key = key.lower()
        for i,typ in enumerate(types):
            typ_lower = typ.lower()
            if key in typ_lower or typ_lower in key:
                key = typ
                break
    
    data_to_display = data_js.get(key)
    
def display_errors():
    display_data_string('errors')
def display_warnings():
    display_data_string('warnings')
def display_all():
    display_data_string('all')

