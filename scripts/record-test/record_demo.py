import argparse
import subprocess
import telnetlib
import xmlrpc.client

from demoparser2 import DemoParser


class CS2Client:
    def __init__(self, host="127.0.0.1", port=2121):
        self.host = host
        self.port = port
        self.client = telnetlib.Telnet(self.host, self.port)

    def send_command(self, command):
        self.client.write(command.encode("ascii") + b"\n")
        return self.client.read_until(b"OK", timeout=1).decode("ascii")

    def play_demo(self, demo_file):
        return self.send_command(f"playdemo {demo_file}")

    def pause_demo(self):
        return self.send_command("demo_pause")

    def resume_demo(self):
        return self.send_command("demo_resume")

    def spectate_player(self, player_name):
        return self.send_command(f"spec_player {player_name}")

    def goto_tick(self, tick):
        return self.send_command(f"demo_gototick {tick}")

    def __del__(self):
        self.client.close()


def wait_for_setup_complete(server):
    while True:
        status = server.supervisor.getProcessInfo("steamcmd")
        if status["statename"] == "EXITED":
            break

    if server.supervisor.getProcessInfo("steamcmd")["exitstatus"] != 0:
        print("Failed to setup server")
        return False

    return True


def record_clip(demo_file, start_tick, end_tick, player_name):
    client = CS2Client()

    # Play the demo
    client.play_demo(demo_file)
    loading_complete = False
    while not loading_complete:
        # Read the output line by line
        output = client.client.read_until(b"\n", timeout=5).decode('ascii').strip()
        print(output)  # For debugging purposes

        # Check for specific messages that indicate loading is complete
        if output == "":
            print("Loading complete")
            loading_complete = True

    # Pause the demo
    client.pause_demo()

    # Go to the start tick
    print("Going to tick")
    client.goto_tick(start_tick)
    print("Spectating player")
    client.spectate_player(player_name)

    # Start ffmpeg to record the clip to a temp file
    # ffmpeg -f x11grab -s 1280x720 -r 60 -i :99 -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 192k output.mp4
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-f",
            "x11grab",
            "-s",
            "1920x1080",
            "-r",
            "60",
            "-i",
            ":99",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "22",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "output.mp4",
        ]
    )

    # Resume the demo
    client.resume_demo()

    # Wait for the clip to finish recording
    sleep_time = (end_tick - start_tick) / 60
    process.wait(timeout=sleep_time)

    # Kill the ffmpeg process
    process.kill()

    # Pause the demo
    client.pause_demo()

    # Stop the demo
    client.send_command("stopdemo")

    # Exit the client
    del client


def get_round_ticks(demo_file, round_number, player_name):
    parser = DemoParser(demo_file)

    # Start parsing the demo
    parser.parse()

    # Find the round start and end ticks
    round_start_tick = None
    round_end_tick = None
    player_alive_ticks = []

    rounds = parser.parse_header().rounds
    if round_number < 1 or round_number > len(rounds):
        raise ValueError("Invalid round number")

    round_data = rounds[round_number - 1]

    # Find the tick where the round begins after freezetime
    for tick in round_data.freezetime_ended_ticks:
        if round_start_tick is None or tick < round_start_tick:
            round_start_tick = tick

    # Find the tick where the round ends
    round_end_tick = round_data.end_tick

    # Find the ticks where the player is alive
    player_found = False
    player_died = False
    for player in parser.parse_demo().players:
        if player.name == player_name:
            player_found = True
            for life in player.lives:
                if life.round == round_number:
                    player_alive_ticks.extend(range(life.start_tick, life.end_tick + 1))
                    if life.end_tick < round_end_tick:
                        player_died = True
            break

    if not player_found:
        raise ValueError("Player not found in the demo")

    # Determine the last tick where the player was alive or the round end tick
    if player_died:
        last_alive_tick = max(player_alive_ticks) if player_alive_ticks else None
    else:
        last_alive_tick = round_end_tick

    return round_start_tick, last_alive_tick


def main():
    parser = argparse.ArgumentParser(description="Record a demo")
    parser.add_argument("demo_file", help="The name of the demo file to record")
    parser.add_argument("player_name", help="The name of the player to record")
    parser.add_argument("round", help="The round to record")
    args = parser.parse_args()

    server = xmlrpc.client.ServerProxy("http://test:test@127.0.0.1:9001/RPC2")

    cs2_status = server.supervisor.getProcessInfo("cs2")
    if cs2_status["statename"] == "STOPPED":
        print("Waiting for Steamcmd to finish updating and validating")
        if not wait_for_setup_complete(server):
            return

        print("Starting CS2")
        server.supervisor.startProcess("cs2")
        while server.supervisor.getProcessInfo("cs2")["statename"] != "RUNNING":
            pass

    record_clip(args.demo_file, 18000, 20000, args.player_name)


if __name__ == "__main__":
    main()
