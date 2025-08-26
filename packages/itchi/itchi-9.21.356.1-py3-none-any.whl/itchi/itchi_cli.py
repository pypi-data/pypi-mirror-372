import argparse
import logging
import os
import sys
import pathlib
import traceback
from typing import Optional

import itchi.config
import itchi.config_attrs_doc
import itchi.preprocess
import itchi.profilerxml
import itchi.signals
from itchi import __version__
from itchi.ortilib import osprober
from itchi.ortilib.orti import Orti
from itchi.runnable.instrumentation import runnable_instrumentation
from itchi.runnable.program_flow import runnable_program_flow
from itchi.runningtask.basic import running_taskisr
from itchi.runningtask.btf import running_taskisr_btf
from itchi.runningtask.ksar import running_taskisr_ksar
from itchi.runningtask.sampling import running_taskisr_sampling
from itchi.swat.swat import swat
from itchi.spinlock.instrumentation_microsar import spinlock_instrumentation_microsar
from itchi.taskstate.arti import arti
from itchi.taskstate.complex_inspectors import task_state_complex_inspectors
from itchi.taskstate.complex_native import task_state_complex_native
from itchi.taskstate.eb_mk_gen_config_h import task_state_eb_mk_gen_config_h
from itchi.taskstate.instrumentation_microsar import task_state_instrumentation_microsar
from itchi.taskstate.instrumentation_autocore import task_state_instrumentation_autocore
from itchi.taskstate.single_variable import task_state_single_variable


def init_logging(log_file: pathlib.Path):
    logFormat = "%(levelname)-8s| %(asctime)s | %(message)s"

    # Log everything to logFile.
    logging.basicConfig(
        level=logging.DEBUG,
        filemode="w",
        filename=log_file,
        datefmt="%d.%m %H:%M.%S",
        format=logFormat,
        force=True,
    )

    # Log info and above to console
    console = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(levelname)-8s | %(message)s")
    console.setFormatter(formatter)
    console.setLevel(logging.INFO)
    logging.getLogger("").addHandler(console)
    logging.info(f"Logging to '{log_file}'.")


def log_version() -> None:
    logging.info(__version__)


def create_parser() -> argparse.ArgumentParser:
    description = "iTCHi Trace Configuration Helper"
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--config",
        metavar="config",
        default="itchi.json",
        help="""path to config file (default: %(default)s)""",
        type=str,
    )

    parser.add_argument(
        "--log_file",
        metavar="log_file",
        default="itchi.log",
        help="""path to log file (default: %(default)s)""",
        type=str,
    )

    parser.add_argument(
        "--write_default_config",
        action="store_true",
        help="Writes an empty configuration file and exits.",
    )

    parser.add_argument(
        "--arti",
        action="store_true",
        help="Creates profiler XML and instrumentation code "
        "for tracing as specified by the ARTI standard.",
    )

    parser.add_argument(
        "--running_taskisr",
        action="store_true",
        help="Prepares profiler XML for running Task/ISR tracing.",
    )

    parser.add_argument(
        "--running_taskisr_btf",
        action="store_true",
        help="Same as --running_taskisr but with BTF export.",
    )

    parser.add_argument(
        "--running_taskisr_sampling",
        action="store_true",
        help="Profiler XML for running Task/ISR sampling.",
    )

    parser.add_argument(
        "--running_taskisr_ossignaling",
        action="store_true",
        help="Not supported via iTCHi. Import ORTI directly.",
    )

    parser.add_argument(
        "--task_state_single_variable",
        action="store_true",
        help="Prepares profiler XML for task state tracing "
        "based on a single variable for each task.",
    )

    parser.add_argument(
        "--task_state_complex_expression",
        "--task_state_inspectors",
        action="store_true",
        help="Prepares profiler XML and "
        "Inspectors for task state tracing with complex "
        "expressions.",
    )

    parser.add_argument(
        "--task_state_complex_native",
        action="store_true",
        help="Prepares profiler XML for native task state tracing via complex expressions.",
    )

    parser.add_argument(
        "--task_state_instrumentation_microsar",
        "--task_state_instrumentation",
        action="store_true",
        help="Creates profiler XML and instrumentation code "
        "for state tracing with the Vector MICROSAR OS.",
    )

    parser.add_argument(
        "--task_state_instrumentation_autocore",
        action="store_true",
        help="Creates profiler XML and instrumentation code "
        "for state tracing with the EB AutoCore OS.",
    )

    parser.add_argument(
        "--task_state_swat_microsar",
        action="store_true",
        help="Creates profiler XML and swat_config.h for Task/ISR state tracing "
        "via SWAT using the Vector MICROSAR Timing Hooks.",
    )

    parser.add_argument(
        "--runnable_instrumentation",
        action="store_true",
        help="Creates profiler XML and instrumentation for Runnable tracing.",
    )

    parser.add_argument(
        "--runnable_swat",
        action="store_true",
        help="Creates profiler XML and swat_config.h for Runnable tracing via SWAT "
        "using the AUTOSAR RTE VFB trace hooks.",
    )

    parser.add_argument(
        "--runnable_program_flow",
        action="store_true",
        help="Prepares profiler XML for Runnable tracing based on program flow trace.",
    )

    parser.add_argument("--signals", action="store_true", help="Prepares profiler XML for signals.")

    parser.add_argument(
        "--signals_swat",
        action="store_true",
        help="Creates profiler XML and swat_config.h to record the configured SWAT signals.",
    )

    parser.add_argument(
        "--spinlock_instrumentation_microsar",
        "--spinlock_instrumentation",
        action="store_true",
        help="Experimental: prepares profiler XML for spinlock profiling.",
    )

    parser.add_argument(
        "--log_trace_symbols",
        action="store_true",
        help="Logs symbols that have to be traced for current Profiler XML.",
    )

    parser.add_argument("--version", action="store_true", help="Prints version and exits.")

    parser.add_argument(
        "--help_attributes",
        action="store_true",
        help="Prints documentation for all available configuration attributes and exits.",
    )

    return parser


def itchi_main(args: argparse.Namespace, config: itchi.config.ItchiConfig) -> int:
    """
    iTCHi's main procedure that writes the Profiler XML file and instrumentation
    code based on the provided command line arguments and the iTCHi configuration file.

    Args:
        args (argparse.Namespace): command line arguments
        config (src.config.ItchiConfig): iTCHi configuration object
    """

    if config.commands is None:
        raise ValueError("iTCHi been started without commands configuration")

    orti = Orti(config.orti_file)
    itchi.preprocess.update_orti(config, orti)
    profiler_xml = itchi.profilerxml.load_or_create(config.profiler_xml_file)
    itchi.preprocess.set_meta_tags(orti, profiler_xml)

    if config.commands.is_swat_enabled():
        swat(orti, profiler_xml, config)

    if config.commands.arti:
        arti(orti, profiler_xml, config)

    if config.commands.running_taskisr:
        if osprober.probe(orti) == osprober.Os.KSAR:
            running_taskisr_ksar(orti, profiler_xml)
        else:
            running_taskisr(orti, profiler_xml)

    if config.commands.running_taskisr_btf:
        running_taskisr_btf(orti, profiler_xml)

    if config.commands.running_taskisr_sampling:
        running_taskisr_sampling(orti, profiler_xml, config)

    if config.commands.task_state_single_variable:
        if config.task_state and config.task_state.autocore_mk_gen_config_h != pathlib.Path():
            # EB Mk_gen_config.h requires special handling because the ORTI does not follow the spec.
            task_state_eb_mk_gen_config_h(orti, profiler_xml, config)
        else:
            task_state_single_variable(orti, profiler_xml, config)

    if config.commands.task_state_complex_expression:
        task_state_complex_inspectors(orti, profiler_xml, config)

    if config.commands.task_state_complex_native:
        task_state_complex_native(orti, profiler_xml, config)

    if config.commands.task_state_instrumentation_microsar:
        task_state_instrumentation_microsar(orti, profiler_xml, config)

    if config.commands.task_state_instrumentation_autocore:
        task_state_instrumentation_autocore(orti, profiler_xml, config)

    if config.commands.runnable_program_flow:
        runnable_program_flow(profiler_xml, config)

    if config.commands.runnable_instrumentation:
        runnable_instrumentation(profiler_xml, config)

    if config.commands.signals:
        itchi.signals.signals(profiler_xml, config)

    if config.commands.spinlock_instrumentation_microsar:
        spinlock_instrumentation_microsar(orti, profiler_xml, config)

    if config.commands.log_trace_symbols:
        itchi.signals.log_trace_symbols(profiler_xml)

    if config.commands.all_false():
        logging.warning("No commands provided. Do not write Profiler XML.")
    else:
        logging.info(f"Write '{config.profiler_xml_file}'.")
        profiler_xml.save(config.profiler_xml_file)

    logging.info("Finished successfully.")
    return 0


def write_default_config(config_file: pathlib.Path) -> int:
    """Write default config to config_file.

    Args:
        config_file (pathlib.Path): config file path

    Returns:
        int: Return 0 on success and 1 on error.
    """
    if os.path.isfile(config_file):
        logging.error(f"{config_file} already exists!")
        return 1
    itchi.config.write_default_config(config_file)
    logging.info(f"Write default config {config_file=}.")
    return 0


def main(args: Optional[argparse.Namespace] = None) -> int:
    if not args:
        args = create_parser().parse_args()
    # Initiate command line arg parser and logging.
    init_logging(args.log_file)
    logging.debug(f"Running '{' '.join(sys.argv)}'")

    if args.version:
        log_version()
        return 0

    if args.write_default_config:
        return write_default_config(args.config)

    if args.help_attributes:
        itchi.config_attrs_doc.log_attrs_doc()
        return 0

    config = itchi.preprocess.load_config(args.config)
    if config is None:
        logging.critical("Could not load iTCHi config.")
        return 1

    # Working directory should be location of config file.
    new_cwd = os.path.dirname(os.path.abspath(args.config))
    os.chdir(new_cwd)
    logging.info(f"Working directory is '{new_cwd}'.")

    # Add command line provided commands to config.
    config.add_args([k for k, v in vars(args).items() if v is True])

    if len(sys.argv) == 1 and config.commands is not None and config.commands.all_false():
        logging.info("Run iTCHi with --help to see help.")
        return 1

    return itchi_main(args, config)


if __name__ == "__main__":
    try:
        return_code = main()
        sys.exit(return_code)
    except Exception as e:
        logging.critical(f"{type(e).__name__}: {e}")
        logging.critical("If you think this is a bug, please report it to support.tasking.com.")
        logging.critical("Please attach itchi.json, itchi.log, and all other referenced files.")
        log_version()
        logging.debug(traceback.format_exc())
        sys.exit(1)
