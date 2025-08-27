import click

from mosamatic.tasks import SelectSliceFromScanTask


@click.command(help='Automatically selects L3 or T4 slice from full CT scan')
@click.option(
    '--scans_dir', 
    required=True, 
    type=click.Path(exists=True), 
    help='Directory with scan folders',
)
@click.option(
    '--output_dir', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--vertebral_level',
    default='none',
    help='Options: "vertebrae_L3", "vertebrae_T4"'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite (true/false)'
)
def selectslicefromscan(scans_dir, output_dir, vertebral_level, overwrite):
    """
    Automatically selects L3 or T4 slice from full CT scan.
    
    Parameters
    ----------
    scans_dir : str
        Directory with scan folders (one folder for each scan).

    output_dir : str
        Path to output directory.

    vertebral_level : str
        Options: 'vertebrae_L3', 'vertebrae_T4'
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    task = SelectSliceFromScanTask(scans_dir, output_dir, vertebral_level, overwrite=overwrite)
    task.run()