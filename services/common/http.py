# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Shared HTTP client for service-to-service calls (auto-instrumented by ADOT)."""

from __future__ import annotations

import httpx

from common.config import HTTP_TIMEOUT

client = httpx.Client(timeout=HTTP_TIMEOUT)
