# SPDX-FileCopyrightText: 2025 Alexander Kalinovsky <a@k8y.ru>
#
# SPDX-License-Identifier: Apache-2.0

"""Quickbot CLI."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("quickbot-cli")
except PackageNotFoundError:
    __version__ = "0.0.0"
