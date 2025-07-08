import os

import psutil
import ctypes
import ctypes.wintypes as wintypes

import re

UUID_REGEX = re.compile(rb'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}')
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress",       ctypes.c_void_p),
        ("AllocationBase",    ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize",        ctypes.c_size_t),
        ("State",             wintypes.DWORD),
        ("Protect",           wintypes.DWORD),
        ("Type",              wintypes.DWORD),
    ]

def find_process_by_name(name):
    for proc in psutil.process_iter(["name", "pid"]):
        if name.lower() in proc.info["name"].lower():
            return proc
    return None

def read_process_memory(pid):
    process_handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not process_handle:
        raise OSError("Не удалось открыть процесс (нужны права администратора?)")

    mbi = MEMORY_BASIC_INFORMATION()
    address = 0
    found = []

    while kernel32.VirtualQueryEx(process_handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        if mbi.State == MEM_COMMIT and mbi.Protect == PAGE_READWRITE:
            buffer = ctypes.create_string_buffer(mbi.RegionSize)
            bytesRead = ctypes.c_size_t()
            if kernel32.ReadProcessMemory(process_handle, ctypes.c_void_p(address), buffer, mbi.RegionSize, ctypes.byref(bytesRead)):
                data = buffer.raw[:bytesRead.value]
                matches = UUID_REGEX.findall(data)
                items = set()
                if matches:
                    print(f"\n✅ Найдено UUID в блоке @ {hex(address)}:")
                    for match in set(matches):
                        print(f"   - {match.decode('utf-8')}")
                        items.add(match.decode('utf-8'))
                    found.append((address, items))
        address += mbi.RegionSize

    kernel32.CloseHandle(process_handle)
    return found

def dump_nearby_data(pid, address_hex, context_bytes=1024):
    import ctypes
    import ctypes.wintypes as wintypes

    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_VM_READ = 0x0010
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    class MEMORY_BASIC_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BaseAddress", ctypes.c_void_p),
            ("AllocationBase", ctypes.c_void_p),
            ("AllocationProtect", wintypes.DWORD),
            ("RegionSize", ctypes.c_size_t),
            ("State", wintypes.DWORD),
            ("Protect", wintypes.DWORD),
            ("Type", wintypes.DWORD),
        ]

    address = int(address_hex, 16)
    process_handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not process_handle:
        raise OSError("Не удалось открыть процесс")

    try:
        mbi = MEMORY_BASIC_INFORMATION()
        if not kernel32.VirtualQueryEx(process_handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            print(f"Не удалось получить информацию о памяти по адресу {hex(address)}")
            return

        start_read = max(address - context_bytes, mbi.BaseAddress)
        max_size = mbi.RegionSize - (start_read - mbi.BaseAddress)
        read_size = min(context_bytes * 2, max_size)

        buffer = ctypes.create_string_buffer(read_size)
        bytesRead = ctypes.c_size_t()

        success = kernel32.ReadProcessMemory(process_handle, ctypes.c_void_p(start_read), buffer, read_size, ctypes.byref(bytesRead))
        if not success or bytesRead.value == 0:
            print(f"Не удалось прочитать память по адресу {hex(start_read)}")
            return

        data = buffer.raw[:bytesRead.value]
        print(f"\n📍 Dump вокруг {hex(address)} (адрес чтения: {hex(start_read)}, размер: {bytesRead.value}):")
        print("-" * 60)
        print(data.decode('utf-8', errors='replace'))
        print("-" * 60)
    finally:
        kernel32.CloseHandle(process_handle)




def get_blueprint_folder_uuids(blueprint_root):
    return {name for name in os.listdir(blueprint_root)
            if re.fullmatch(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', name.lower())}

def compare_sets(memory_uuids, folder_uuids, pid):
    print("\n📊 Сравнение UUID-ов:")
    for memory_rg, uuids in memory_uuids:
        set_uuids = uuids

        intersection = set_uuids & folder_uuids
        only_in_memory = set_uuids - folder_uuids
        only_in_folder = folder_uuids - set_uuids
        if len(intersection) > 0:
            print('---Region '+ hex(memory_rg)+ '---')
            print(f'in both: {len(intersection)}')
            print(f'in memory: {len(only_in_memory)}')
            print(f'in folder: {len(only_in_folder)}')
            dump_nearby_data(pid, hex(memory_rg), context_bytes=8192)

target = "card_stack_colored_1"

if __name__ == "__main__":
    proc = find_process_by_name("ScrapMechanic")
    if not proc:
        print("❌ Процесс Scrap Mechanic не найден.")
    else:
        mem_uuids = read_process_memory(proc.pid)

        # 💡 путь до папки Blueprints
        blueprint_dir = 'C:/Users/abras/AppData/Roaming/Axolot Games/Scrap Mechanic/User/User_76561198121774007/Blueprints'
        if not os.path.isdir(blueprint_dir):
            print(f"❌ Папка блюпринтов не найдена: {blueprint_dir}")
        else:
            folder_uuids = get_blueprint_folder_uuids(blueprint_dir)
            compare_sets(mem_uuids, folder_uuids, proc.pid)