import argparse

parser = argparse.ArgumentParser(description="Server to convert text to speech and send the audio back")
parser.add_argument(
    "--logfile",
    help="log to file",
    action="store_const",
    const=True
)
args = parser.parse_args()