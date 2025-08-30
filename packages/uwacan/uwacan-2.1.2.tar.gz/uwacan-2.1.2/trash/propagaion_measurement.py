import itertools
import time
import click
import sounddevice as sd
import numpy as np
import pendulum
from pathlib import Path
import toml

def decidecade_center(f):
    return 10**(np.round(np.log10(f) * 10) / 10)


sweeps = {
    "316Hz decidecade": {
        "lower": decidecade_center(316) * 10**(-1 / 20),
        "upper": decidecade_center(316) * 10**(1 / 20),
        "duration": 4,
        "prerecord": 50e-3,
        "postrecord": 150e-3,
        "fade": 25e-3,
    },
    "1kHz decade": {
        "lower": 1e3 * 10**(-1 / 2),
        "upper": 1e3 * 10**(1 / 2),
        "duration": 10,
        "prerecord": 50e-3,
        "postrecord": 150e-3,
        "fade": 25e-3,
    }
}


class SweepMeasurement:
    _log_file = 'measurerement_log.csv'

    def __init__(self,
        output_folder,
        audio_device,
        samplerate,
        output_channels,
        input_channels,
        repeats,
        repeat_delay,
        cycle,
        sweep_sequence,
        sequence_delay,
        input_gain,
        output_gain,
    ):
        self.output_folder = Path(output_folder)
        if not self.output_folder.exists():
            self.output_folder.mkdir(parents=True)
        self.measurement_log = self.output_folder / "measurement_log.toml"

        self.audio_device = audio_device
        self.samplerate = samplerate
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.input_gain = input_gain
        self.output_gain = output_gain

        self.repeats = repeats
        self.repeat_delay = repeat_delay
        self.sweep_sequence = sweep_sequence
        self.sequence_delay = sequence_delay
        self.cycle = cycle

    def write_to_log(self, category, data):
        with open(self.measurement_log, 'a') as logfile:
            toml.dump(
                {
                    category: [data],
                },
                logfile,
            )

    @property
    def audio_device_index(self):
        for device in sd.query_devices():
            if self.audio_device in device["name"]:
                return device["index"]

    def playrec(self, output_signal):
        # return output_signal
        return sd.playrec(
            data=output_signal,
            samplerate=self.samplerate,
            device=self.audio_device_index,
            input_mapping=self.input_channels,
            output_mapping=self.output_channels,
            blocking=True,
        ).transpose()

    def play(self, output_signal):
        sd.play(
            data=output_signal,
            samplerate=self.samplerate,
            device=self.audio_device_index,
            mapping=self.output_channels,
            blocking=True,
        )

    def create_sweep(self, sweep, repeats=1, repeat_delay=0):
        if sweep in sweeps:
            sweep = sweeps[sweep]
        else:
            raise ValueError(f"Unknown sweep `{sweep}`")

        k = round(sweep["lower"] * sweep["duration"] / np.log(sweep["upper"] / sweep["lower"]))
        sweep_duration = k * np.log(sweep["upper"] / sweep["lower"]) / sweep["lower"]
        sweep_samples = round(sweep_duration * self.samplerate)
        phase_rate = sweep_duration / np.log(sweep["upper"] / sweep["lower"])

        t = np.arange(sweep_samples) / self.samplerate
        sweep_signal = np.sin(2 * np.pi * sweep["lower"] * phase_rate * np.exp(t / phase_rate))

        prerecord_samples = round(sweep["prerecord"] * self.samplerate)
        fade_samples = round(sweep["fade"] * self.samplerate)
        postrecord_samples = round(sweep["postrecord"] * self.samplerate)
        pause_samples = round(repeat_delay * self.samplerate)

        total_samples = prerecord_samples + postrecord_samples + sweep_signal.size * repeats + pause_samples * (repeats - 1)

        sweep_signal[:fade_samples] *= np.sin(np.linspace(0, np.pi / 2, fade_samples))**2
        sweep_signal[-fade_samples:] *= np.sin(np.linspace(np.pi / 2, 0, fade_samples))**2

        repeat_samples = sweep_signal.size + pause_samples
        signal = np.zeros(total_samples)
        for repeat in range(repeats):
            start_idx = prerecord_samples + repeat * repeat_samples
            signal[start_idx:start_idx + sweep_signal.size] = sweep_signal

        return signal

    # def measure_one_sweep(self, sweep):
        # self.write_to_log("measurement.sweep", {"sweep": sweep})

    def run_measurement(self):
        self.write_to_log("measurement", {
            "input_channels": self.input_channels,
            "output_channels": self.output_channels,
            "samplerate": self.samplerate,
            "input_gain": self.input_gain,
            "output_gain": self.output_gain,
            "sequence": self.sweep_sequence,
            "cycle": self.cycle,
            "repeats": self.repeats,
            "repeat_delay": self.repeat_delay,
            "sequence_delay": self.sequence_delay,
        })

        for sweep in (itertools.cycle(self.sweep_sequence) if self.cycle else self.sweep_sequence):
            signal = self.create_sweep(sweep, self.repeats, self.repeat_delay)
            now = pendulum.now(tz="UTC").format("YYYY-MM-DD HH-mm-ss")
            click.echo(f"Staring sweep {sweep} at {now}")
            self.write_to_log("measurement.sweep", {"sweep": sweep, "time": now})
            if len(self.input_channels):
                response = self.playrec(signal)
                np.save(self.output_folder / f"{now}.npy", response)
            else:
                self.play(signal)
            time.sleep(self.sequence_delay)


@click.command()
@click.argument("output-folder")
@click.option("--audio-device", default="ASIO MADIface USB", type=str)
@click.option("--samplerate", default=192000, type=int)
@click.option("--output", "-o", "output_channels", multiple=True, help="Output channels used on the audio interface", type=int)
@click.option("--input", "-i", "input_channels", multiple=True, help="Input channels used on the audio interface", type=int)
@click.option("--output-gain", "output_gain", multiple=True, help="Gain used for the output channels on the audio interface", type=float)
@click.option("--input-gain", "input_gain", multiple=True, help="Gain used for the input channels used on the audio interface", type=float)
@click.option("--repeats", type=int, default=1, help="How many times in a row to send each sweep.")
@click.option("--repeat-delay", type=float, default=0.5, help="The delay (in seconds) between each sweep repetition.")
@click.option("--cycle", flag_value=True, help="Give this flag to cycle through the supplied sweeps.")
@click.option("--sequence-delay", type=float, default=2, help="How long to pause after each sweep group.")
@click.option("--sweep", "-s", "sweep_sequence", multiple=True, help="Name of a sweep to send", type=click.Choice(list(sweeps)))
def send_sweeps_cli(
        output_folder,
        audio_device,
        samplerate,
        output_channels,
        input_channels,
        repeats,
        repeat_delay,
        cycle,
        sweep_sequence,
        sequence_delay,
        input_gain,
        output_gain,
):
    measurement_runner = SweepMeasurement(
        output_folder=output_folder,
        audio_device=audio_device,
        samplerate=samplerate,
        output_channels=output_channels,
        input_channels=input_channels,
        repeats=repeats,
        repeat_delay=repeat_delay,
        cycle=cycle,
        sweep_sequence=sweep_sequence,
        sequence_delay=sequence_delay,
        input_gain=input_gain,
        output_gain=output_gain,
    )
    measurement_runner.run_measurement()

if __name__ == "__main__":
    send_sweeps_cli()