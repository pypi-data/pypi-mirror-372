import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.exceptions import IncompatibleOptions
from qualitative_coding.logs import configure_logger

@click.command()
@click.argument("codes", nargs=-1)
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-p", "--pattern", 
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", 
        help="File path containing a list of filenames to use")
@click.option("-c", "--coders", help="Coders", multiple=True)
@click.option("-d", "--depth", help="Maximum depth in code tree", type=int)
@click.option("-n", "--unit", default="line", help="Unit of analysis",
        type=click.Choice(['line', 'paragraph', 'document']))
@click.option("-r", "--recursive-codes", "recursive_codes", is_flag=True, 
        help="Include child codes")
@click.option("-B", "--before", default=2, type=int, 
        help="Number of lines before the code to show")
@click.option("-C", "--after", default=2, type=int, 
        help="Number of lines after the code to show")
@click.option("-o", "--no-codes", "no_codes", is_flag=True,
        help="Do not show matching codes")
@click.option("-l", "--no-line-numbers", "no_line_numbers", is_flag=True,
        help="Do not show line numbers")
@click.option("-j", "--json", is_flag=True, help="Export as JSON")
@handle_qc_errors
def find(codes, settings, pattern, filenames, coders, depth, unit, recursive_codes, 
         before, after, no_codes, no_line_numbers, json):
    "Find all coded text"
    if no_codes and json:
        raise IncompatibleOptions("--no-codes and --json are incompatible")
    if no_line_numbers and json:
        raise IncompatibleOptions("--no-line_numbers and --json are incompatible")
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("codes find", codes=codes, pattern=pattern, filenames=filenames, coders=coders,
             depth=depth, unit=unit, recursive_codes=recursive_codes, before=before, 
             after=after, no_codes=no_codes, json=json)
    corpus = QCCorpus(settings_path)
    viewer = QCCorpusViewer(corpus)
    if json:
        viewer.show_coded_text_json(
            codes, 
            before=before, 
            after=after, 
            recursive_codes=recursive_codes,
            depth=depth,
            unit=unit,
            pattern=pattern,
            file_list=read_file_list(filenames),
            coders=coders,
        )
    else:
        viewer.show_coded_text(
            codes, 
            before=before, 
            after=after, 
            recursive_codes=recursive_codes,
            depth=depth,
            unit=unit,
            pattern=pattern,
            file_list=read_file_list(filenames),
            coders=coders,
            show_codes=not no_codes,
            show_line_numbers=not no_line_numbers,
        )

