import yaml
from pymusiclooper.audio import MLAudio


class SampleRateAnalyzer:
    file: str
    output: str


    def __init__(self, yaml_data: dict, output_path: str):

        self.file = yaml_data["File"]
        self.output = output_path


    def run(self) -> bool:

        print("Running sample rate analysis")

        try:
            audio_file = MLAudio(self.file)
            sample_rate = audio_file.rate
            duration = audio_file.total_duration
            return self.print_yaml(True, "", sample_rate, duration)
        except Exception as e:
            return self.print_yaml(False, f"Error analyzing audio {str(e)}")


    def print_yaml(self, successful: bool, error: str, sample_rate: int, duration: int) -> bool:
        data = dict(
            Successful=successful,
            Error=error,
            SampleRate=sample_rate,
            Duration=duration
        )

        try:
            with open(self.output, 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            return successful
        except Exception as e:
            print(e)
            return False