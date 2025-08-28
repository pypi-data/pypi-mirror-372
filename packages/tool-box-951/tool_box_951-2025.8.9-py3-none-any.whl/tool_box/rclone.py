# coding:utf-8
import os
import json
import subprocess
from loguru import logger


def _rclone_transfer_operation(
    cmd, source_path, target_path=None, flags=None, verbose=False
):
    command = cmd.copy()
    command.append(source_path)
    if target_path is not None:
        command.append(target_path)
    if flags is not None:
        command += flags
    if verbose:
        logger.info("run {}", command)
    result = subprocess.run(
        " ".join(command),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        check=False,
        shell=True,
        executable="/bin/bash",
        env=os.environ,  # 继承完整环境变量
        cwd=os.getcwd(),
    )
    if verbose and result.returncode != 0:
        logger.error(
            "run {} fail, code:{} reason:{}",
            " ".join(command),
            result.returncode,
            result.stderr.decode("utf-8"),
        )

    return result.returncode


def get_servers():
    command = ["rclone", "config", "dump"]
    result = subprocess.run(
        " ".join(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=os.environ,
        cwd=os.getcwd(),
        executable="/bin/bash",
        shell=True,
    )
    if result.returncode == 0:
        output = json.loads(result.stdout.decode("utf-8"))
        return list(output.keys())
    reason = result.stderr.decode("utf-8")
    logger.error("{}", reason)
    return None


def ls(source_path):
    command = ["rclone", "lsf", source_path]

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if result.returncode == 0:
        return sorted(result.stdout.decode("utf-8").splitlines())
    reason = result.stderr.decode("utf-8")
    if "directory not found" in reason:
        return []
    logger.error("{}", result.stderr.decode("utf-8"))
    return []


def lsd(source_path):
    """列出目录下的文件夹"""
    command = ["rclone", "lsd", source_path]

    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if result.returncode == 0:
        ll = result.stdout.decode("utf-8").splitlines()
        ll[:] = [i.split()[-1] for i in ll]
        return sorted(ll)
    reason = result.stderr.decode("utf-8")
    if "directory not found" in reason:
        return []
    logger.error("{}", result.stderr.decode("utf-8"))
    return []


def move(source_path, target_path, flags=None, verbose=False):
    return _rclone_transfer_operation(
        ["rclone", "move"], source_path, target_path, flags, verbose=verbose
    )


def copy(source_path, target_path, flags=None, verbose=False):
    return _rclone_transfer_operation(
        ["rclone", "copy"], source_path, target_path, flags, verbose=verbose
    )


def sync(source_path, target_path, flags=None, verbose=False):
    """
    rclone sync source_path target_path
    """
    if os.path.isfile(source_path):
        logger.error("source_path must be directory, but input is {}", source_path)
        return None
    return _rclone_transfer_operation(
        ["rclone", "sync"], source_path, target_path, flags, verbose=verbose
    )
