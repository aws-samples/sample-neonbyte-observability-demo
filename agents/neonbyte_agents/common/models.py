# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Single source of truth for which model each agent uses.

Same palette as the One Observability Demo's Waggle agents: four providers on
Amazon Bedrock (Anthropic · Amazon · DeepSeek · OpenAI-OSS), all via SigV4.
"""

from __future__ import annotations

import os

from neonbyte_agents.common import config

# --- Model palette; override any via env.
SONNET_4_6 = config.CLAUDE_MODEL_ID  # backbone Claude, from config (BEDROCK_CLAUDE_MODEL_ID)
NOVA_2_LITE = os.getenv("BEDROCK_NOVA_LITE_MODEL_ID", "us.amazon.nova-2-lite-v1:0")
# Meta Llama models are Legacy on Bedrock (not invocable in accounts that haven't used them in 30 days);
# DeepSeek V3.2 is active, on-demand in-Region (no cross-Region routing) and supported by LlamaIndex.
DEEPSEEK_V3_2 = os.getenv("BEDROCK_SUPPORT_MODEL_ID", "deepseek.v3.2")
GPT_OSS = config.GPT_OSS_MODEL_ID  # from config (BEDROCK_GPT_OSS_MODEL_ID)

# --- Per-agent assignment (env override wins), tiered by task cost: capable models for reasoning only.
AGENT_MODELS: dict[str, str] = {
    "orchestrator": os.getenv("ORCHESTRATOR_MODEL_ID", SONNET_4_6),  # routing / reasoning
    "advisor": os.getenv("ADVISOR_MODEL_ID", SONNET_4_6),  # product comparison, reasoning-heavy
    "orderdesk": os.getenv("ORDERDESK_MODEL_ID", NOVA_2_LITE),  # lightweight tool calls
    "support": os.getenv("SUPPORT_MODEL_ID", DEEPSEEK_V3_2),  # LlamaIndex on DeepSeek V3.2
    "concierge": os.getenv("CONCIERGE_MODEL_ID", GPT_OSS),  # OpenAI SDK on gpt-oss
}


def model_id(agent: str) -> str:
    """Return the Bedrock model id assigned to `agent`."""
    try:
        return AGENT_MODELS[agent]
    except KeyError:
        raise KeyError(f"Unknown agent '{agent}'. Known: {sorted(AGENT_MODELS)}") from None


def litellm_model(agent: str) -> str:
    """Return the LiteLLM-style id (``bedrock/<model-id>``) for CrewAI and the OpenAI Agents SDK."""
    return f"bedrock/{model_id(agent)}"
