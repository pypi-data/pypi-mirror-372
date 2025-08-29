import sys
import argparse
import typing as T

from SSDraw.core import SSDraw


def get_args(
    args: T.Optional[T.List[str]] = None,
) -> T.Tuple[argparse.Namespace, argparse.ArgumentParser]:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="SSDraw is a program that generates publication-quality protein secondary structure diagrams from three-dimensional protein structures. To depict relationships between secondary structure and other protein features, diagrams can be colored by conservation score, B-factor, or custom scoring.",
        epilog="",
    )
    parser.add_argument(
        "-f",
        "--fasta",
        help="(required) sequence/alignment file in fasta format",
    )
    parser.add_argument("-p", "--pdb", help="(required) pdb file")
    parser.add_argument(
        "-n",
        "--name",
        help="(required) id of the protein in the alignment file",
    )
    parser.add_argument(
        "-o", "--output", help="(required) name for output file"
    )
    parser.add_argument(
        "--SS",
        default=None,
        help="secondary structure annotation in DSSP or .horiz format. If this option is not provided, SSDraw will compute secondary structure from the given PDB file with DSSP.",
    )
    parser.add_argument(
        "--chain_id",
        default="A",
        help="chain id to use in pdb. Defaults to chain A.",
    )
    parser.add_argument(
        "--color_map",
        default=["inferno"],
        nargs="*",
        help="color map to use for heat map",
    )
    parser.add_argument(
        "--scoring_file",
        default=None,
        help="custom scoring file for alignment",
    )
    parser.add_argument(
        "--color",
        default="white",
        help="color for the image. Can be a color name (eg. white, black, green), or a hex code",
    )
    parser.add_argument(
        "-conservation_score",
        action="store_true",
        help="score alignment by conservation score",
    )
    parser.add_argument(
        "--output_file_type",
        default="png",
        help="output file type. Options: png, ps, eps, tif, svg",
    )
    parser.add_argument(
        "-bfactor", action="store_true", help="score by B-factor"
    )
    parser.add_argument(
        "-mview", action="store_true", help="color by mview color map"
    )
    parser.add_argument(
        "--dpi", default=600, type=int, help="dpi to use for final plot"
    )
    parser.add_argument(
        "--ticks", default=0, type=int, help="set ticks at every nth position"
    )
    parser.add_argument("--start", default=0, type=int)
    parser.add_argument("--end", default=0, type=int)
    parser.add_argument(
        "--dssp_exe",
        default="mkdssp",
        help="The path to your dssp executable. Default: mkdssp",
    )
    parser.add_argument(
        "--consurf",
        default="",
        help="consurf or rate4site file to color image with. If rate4site file is given, SSDraw will convert raw scores to grades.",
    )

    args = parser.parse_args(args)

    return args, parser


def main(args=None):
    args, parser = get_args(args)

    if args.start > args.end:
        parser.error("--start cannot be greater than --end")

    if not args.fasta or not args.pdb or not args.output or not args.name:
        parser.print_help()
        sys.exit(1)

    SSDraw(args)


if __name__ == "__main__":
    main()
