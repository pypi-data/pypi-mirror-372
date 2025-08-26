import logging
import itchi.runnable.instrumentation
from pathlib import Path
from itchi.config import (
    TaskStateInstMicrosarConfig,
    InstrumentationTypeEnum,
    RunnableInstrumentationConfig,
)
from itchi.templates.render import render_template_from_templates
from itchi.swat.encoding import size_to_mask
from itchi.swat.state import SwatState


def swat_config_h(state: SwatState):
    TEMPLATE_FILE = "swat_config.h"

    destination_file = state.swat_config.swat_config_h
    if destination_file.name != TEMPLATE_FILE:
        logging.error(
            f"SWAT config header must have name `{TEMPLATE_FILE}`, not `{destination_file.name}`."
            "Did not render."
        )
        return

    if not destination_file.parent.exists():
        logging.error(
            f"Target directory '{destination_file.parent}' does not exist! Did not render."
        )
        return

    if destination_file == Path():
        logging.error(f"Did not render '{TEMPLATE_FILE}'.")
        return

    def raise_helper(msg):
        raise ValueError(msg)

    kwargs = {
        "raise": raise_helper,
        "filename": destination_file.name,
        "include_guard_str": str(destination_file.name).upper().replace(".", "_"),
        "generic": state.generic_encoding,
        "config": state.swat_config,
        "microsar_thread": state.microsar_thread_encoding,
        "microsar_runnable": state.microsar_runnable_encoding,
        "signals": state.signal_encodings,
        "size_to_mask": size_to_mask,
        "slot_count": state.swat_config.slot_count,
        "max_retries": state.swat_config.max_retries,
        "time_right_shift": state.swat_config.time_right_shift,
        "version": state.version,
    }

    content = render_template_from_templates(Path(TEMPLATE_FILE), kwargs)
    if not isinstance(content, str):
        logging.error(f"Could not render '{destination_file}'.")
        return

    logging.info(f"Render template '{TEMPLATE_FILE}' into '{destination_file}'.")
    with open(destination_file, "w", encoding="utf-8") as f:
        f.write(content)


def microsar_timing_hooks(config: TaskStateInstMicrosarConfig):
    TEMPLATE_FILE = "Os_TimingHooks_swat.h"
    destination_file = config.vector_os_timing_hooks_h

    if destination_file == Path():
        logging.error("Did not render because 'vector_os_timing_hooks_h' is empty.")
        return

    include_guard_h = str(destination_file.name).upper().replace(".", "_")
    kwargs: dict = {"include_guard_str": include_guard_h}

    content = render_template_from_templates(Path(TEMPLATE_FILE), kwargs)
    if not isinstance(content, str):
        logging.error(f"Could not render '{destination_file}'.")
        return

    logging.info(f"Render template '{TEMPLATE_FILE}' into '{destination_file}'.")
    with open(destination_file, "w", encoding="utf-8") as f:
        f.write(content)


def microsar_vfb_runnable_hooks(config: RunnableInstrumentationConfig):
    hooks = itchi.runnable.instrumentation.get_rte_runnable_hooks_vector(
        config.rte_hook_h, config.regex
    )
    config.instrumentation_type = InstrumentationTypeEnum.SWAT
    itchi.runnable.instrumentation.write_rte_hook_file(hooks, config)
