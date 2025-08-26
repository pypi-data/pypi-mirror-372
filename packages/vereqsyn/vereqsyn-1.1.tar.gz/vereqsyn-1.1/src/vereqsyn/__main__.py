import argparse

import vereqsyn


def main(argv=None):
    parser = argparse.ArgumentParser(
        "vereqsyn",
        "%(prog)s <versions.cfg> <requirements.txt>",
        "Bi-directional versions.cfg <-> requirements.txt synchronization",
    )
    parser.add_argument(
        "versions_cfg", action="store", help="path to versions.cfg"
    )
    parser.add_argument(
        "requirements_txt", action="store", help="path to requirements.txt"
    )
    parser.add_argument(
        "--versions-section",
        action="store",
        help="section in versions.cfg containing the versions"
        " (default: 'versions')",
        default="versions",
    )

    args = parser.parse_args(argv)
    command = vereqsyn.VersionsCfgRequirementsTxtSync(
        args.requirements_txt, args.versions_cfg, args.versions_section
    )
    command.update()


if __name__ == "__main__":  # pragma: no cover
    main()
