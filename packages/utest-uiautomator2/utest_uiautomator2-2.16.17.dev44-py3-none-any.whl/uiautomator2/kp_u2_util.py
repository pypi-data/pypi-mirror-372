import logging
import os
import subprocess

import requests


G_AGENT_PORT_SET = '8912'


def is_str_value_able(a_str) -> bool:
    i_str = str(a_str)

    if None is i_str:
        return False

    if "" == i_str:
        return False

    return True


def cmd_sync(a_cmd, a_show_out_put=True) -> str:
    try:
        i_process = subprocess.Popen(a_cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     stdin=subprocess.PIPE, shell=True)
        (i_output, __) = i_process.communicate()
        if is_str_value_able(i_output):
            i_output = i_output.decode('utf-8').strip()
            return i_output

    except (RuntimeError, OSError, UnicodeError) as e:
        print(f"cmd_sync Exception:{e} cmd:{a_cmd}")

    return None


def get_agent_port_by_cmd(a_serial_num) -> str:
    i_output = cmd_sync(f"adb -s {a_serial_num} forward --list")
    if is_str_value_able(i_output):
        i_tcp_key_word = 'tcp:'
        i_tcp_key_word_len = len(i_tcp_key_word)

        i_arr = i_output.split("\n")
        for i_v in i_arr:
            if is_str_value_able(i_v):
                i_idx = i_v.find(a_serial_num)
                if -1 == i_idx:
                    continue

                i_port_arr = i_output.split(" ")
                if len(i_port_arr) < 3:
                    continue

                i_port_tcp = i_port_arr[2]
                i_idx_tcp = i_port_tcp.find(i_tcp_key_word)
                if -1 == i_idx_tcp:
                    continue

                i_start_idx = i_idx_tcp + i_tcp_key_word_len
                i_port = i_port_tcp[i_start_idx:]
                i_port = i_port.strip()

                global G_AGENT_PORT_SET
                if not (G_AGENT_PORT_SET == i_port):
                    continue

                i_port_tcp = i_port_arr[1]
                i_idx_tcp = i_port_tcp.find(i_tcp_key_word)
                if -1 == i_idx_tcp:
                    continue

                i_start_idx = i_idx_tcp + i_tcp_key_word_len
                i_port = i_port_tcp[i_start_idx:]
                i_port = i_port.strip()

                return i_port

    return ""


def get_agent_port_by_cfg(a_serial_num, a_cfg='/data/iaas-agent/deviceForwardMap') -> str:
    if not os.path.isfile(a_cfg):
        return ""

    i_key_word = 'RequestUrl:'
    i_key_word_len = len(i_key_word)

    for i_line in open(a_cfg):
        i_idx = i_line.find(a_serial_num)
        if -1 == i_idx:
            continue

        print(f"get_agent_port_by_cfg:{i_line}")
        i_idx_url = i_line.find(i_key_word)
        if -1 == i_idx_url:
            continue

        i_start_idx = i_idx_url + i_key_word_len
        i_url = i_line[i_start_idx:]
        i_idx_url_ex = i_url.find("/}")
        if -1 != i_idx_url_ex:
            i_url = i_url[:i_idx_url_ex]

        print(f"get_agent_port_by_cfg url:{i_url}")

        i_port_arr = i_url.split(":")
        if len(i_port_arr) > 0:
            i_port = i_port_arr[-1]
            return i_port

    return ""


def get_agent_port(a_serial_num) -> str:
    g_agent_port = get_agent_port_by_cmd(a_serial_num)
    return g_agent_port


def check_u2_alive(a_serial_num) -> bool:
    port = get_agent_port(a_serial_num)
    if not is_str_value_able(port):
        return False

    global G_AGENT_PORT_SET
    print(f"check_u2_alive Forward: local:tcp:{port} -> remote:tcp:{G_AGENT_PORT_SET}")

    try:
        i_url = f"http://127.0.0.1:{port}/version"
        print(f"check_u2_alive url {i_url}")

        version = requests.get(i_url).text.strip()
        print(f"check_u2_alive version {version}")
    except requests.exceptions.RequestException as e:
        print(f"check_u2_alive Exception:{e}")
        return False

    return True


def url_cfg_line(a_serial_num, a_port):
    i_line = a_serial_num + ":{"
    i_line += f"Port:{a_port} SerialNum:{a_serial_num} RequestUrl:http://127.0.0.1:{a_port}/"
    i_line += "}\n"
    return i_line

if __name__ == "__main__":
    get_agent_port("UKGA4HWS5PEM7TT8")