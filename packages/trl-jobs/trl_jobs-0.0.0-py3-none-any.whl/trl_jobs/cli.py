
import json
from argparse import ArgumentParser, Namespace, _SubParsersAction
from importlib.resources import files
from typing import Optional

import yaml
from huggingface_hub import HfApi, SpaceHardware
from huggingface_hub.utils import get_token_to_send, logging

logger = logging.get_logger(__name__)


SUGGESTED_FLAVORS = [item.value for item in SpaceHardware if item.value != "zero-a10g"]

CONFIGS = {
    ("Qwen/Qwen3-0.6B", "a100-large"): "Qwen3-0.6B-a100-large.yaml",
}


class RunCommand:
    @staticmethod
    def register_subcommand(parser: _SubParsersAction) -> None:
        sft_parser = parser.add_parser("sft", help="Run a Job")
        sft_parser.add_argument(
            "--flavor",
            type=str,
            help=f"Flavor for the hardware, as in HF Spaces. Defaults to `cpu-basic`. Possible values: {', '.join(SUGGESTED_FLAVORS)}.",
        )
        sft_parser.add_argument(
            "--timeout",
            type=str,
            help="Max duration: int/float with s (seconds, default), m (minutes), h (hours) or d (days).",
        )
        sft_parser.add_argument(
            "-d",
            "--detach",
            action="store_true",
            help="Run the Job in the background and print the Job ID.",
        )
        sft_parser.add_argument(
            "--namespace",
            type=str,
            help="The namespace where the Job will be created. Defaults to the current user's namespace.",
        )
        sft_parser.add_argument(
            "--token",
            type=str,
            help="A User Access Token generated from https://huggingface.co/settings/tokens",
        )
        sft_parser.add_argument(
            "--model",
            type=str,
            required=True,
            help="Model name or path (e.g., Qwen/Qwen3-4B-Base)",
        )
        sft_parser.add_argument(
            "--dataset",
            type=str,
            required=True,
            help="Dataset name or path (e.g., trl-lib/tldr)",
        )
        sft_parser.set_defaults(func=RunCommand)

    def __init__(self, args: Namespace) -> None:
        self.flavor: Optional[SpaceHardware] = args.flavor
        self.timeout: Optional[str] = args.timeout
        self.detach: bool = args.detach
        self.namespace: Optional[str] = args.namespace
        self.token: Optional[str] = args.token
        self.model: str = args.model
        self.dataset: str = args.dataset

        # Check if the requested configuration exists
        if (self.model, self.flavor) in CONFIGS:
            config_file = CONFIGS[(self.model, self.flavor)]
        else:
            raise ValueError(
                f"No configuration file found for model {self.model} and flavor {self.flavor}"
            )

        # Load YAML file
        config_file = files("trl_jobs.configs").joinpath(config_file)
        with open(config_file, "r") as f:
            args_dict = yaml.safe_load(f)

        # Convert to CLI-style args, ensuring complex structures are JSON-encoded
        self.cli_args = []
        for k, v in args_dict.items():
            if isinstance(v, (dict, list, bool, type(None))):
                # Serialize complex types and booleans to JSON-compatible format
                v_str = json.dumps(v)
            else:
                v_str = str(v)
            self.cli_args.extend([f"--{k}", v_str])

    def run(self) -> None:
        api = HfApi(token=self.token)
        job = api.run_job(
            image="qgallouedec/trl:dev",
            command=["trl", "sft", *self.cli_args],
            secrets={"HF_TOKEN": get_token_to_send(self.token)},
            flavor=self.flavor,
            timeout=self.timeout,
            namespace=self.namespace,
        )
        # Always print the job ID to the user
        print(f"Job started with ID: {job.id}")
        print(f"View at: {job.url}")

        if self.detach:
            return

        # Now let's stream the logs
        for log in api.fetch_job_logs(job_id=job.id):
            print(log)


def main():
    parser = ArgumentParser("trl-jobs", usage="hf <command> [<args>]")
    commands_parser = parser.add_subparsers(help="trl-jobs command helpers")
    RunCommand.register_subcommand(commands_parser)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)

    service = args.func(args)
    if service is not None:
        service.run()


if __name__ == "__main__":
    main()
