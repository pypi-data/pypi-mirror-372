"""
Torrent download utilities for QuickDownload.

This module provides functionality to download torrents using magnet links,
.torrent files, or .torrent URLs using the libtorrent library.
"""

import os
import sys
import time
import tempfile
import urllib.request

try:
    import libtorrent as lt

    LIBTORRENT_AVAILABLE = True
except ImportError:
    LIBTORRENT_AVAILABLE = False

# Comprehensive list of public trackers for better peer discovery
DEFAULT_TRACKERS = [
    # User-provided high-performance trackers
    "udp://93.158.213.92:1337/announce",
    "udp://23.168.232.9:1337/announce",
    "udp://185.243.218.213:80/announce",
    "http://200.111.152.54:1337/announce",
    "udp://23.157.120.14:6969/announce",
    "udp://83.31.31.143:6969/announce",
    "udp://23.175.184.30:23333/announce",
    "udp://51.222.82.36:6969/announce",
    "udp://60.249.37.20:80/announce",
    "udp://94.136.190.183:6969/announce",
    "udp://45.154.214.21:6969/announce",
    "udp://82.67.44.197:9999/announce",
    "udp://135.125.236.64:6969/announce",
    "udp://144.126.245.19:6969/announce",
    "udp://193.233.161.213:6969/announce",
    "udp://77.91.85.95:6969/announce",
    "udp://54.36.179.216:6969/announce",
    "udp://35.227.59.57:6969/announce",
    "udp://94.136.190.183:2710/announce",
    "udp://94.136.190.183:1337/announce",
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.demonii.com:1337/announce",
    "udp://open.stealth.si:80/announce",
    "udp://exodus.desync.com:6969/announce",
    "http://open.tracker.cl:1337/announce",
    "udp://tracker.theoks.net:6969/announce",
    "udp://explodie.org:6969/announce",
    "udp://wepzone.net:6969/announce",
    "udp://udp.tracker.projectk.org:23333/announce",
    "udp://ttk2.nbaonlineservice.com:6969/announce",
    "udp://tracker2.dler.org:80/announce",
    "udp://tracker.zupix.online:6969/announce",
    "udp://tracker.yume-hatsuyuki.moe:6969/announce",
    "udp://tracker.wepzone.net:6969/announce",
    "udp://tracker.valete.tf:9999/announce",
    "udp://tracker.tryhackx.org:6969/announce",
    "udp://tracker.torrust-demo.com:6969/announce",
    "udp://tracker.therarbg.to:6969/announce",
    "udp://tracker.srv00.com:6969/announce",
    "udp://tracker.skillindia.site:6969/announce",
    # Additional popular public trackers
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker.bittor.pw:1337/announce",
    "udp://public.popcorn-tracker.org:6969/announce",
    "udp://tracker.dler.org:6969/announce",
    "udp://opentracker.i2p.rocks:6969/announce",
    "http://tracker.files.fm:6969/announce",
    "udp://tracker.internetwarriors.net:1337/announce",
    "udp://tracker.gbitt.info:80/announce",
    "udp://tracker.tiny-vps.com:6969/announce",
    "udp://retracker.lanta-net.ru:2710/announce",
    "http://tracker.bt4g.com:2095/announce",
    "udp://bt1.archive.org:6969/announce",
]


def is_torrent_url(url):
    """
    Check if URL is a torrent file or magnet link.

    Args:
        url (str): The URL or file path to check

    Returns:
        bool: True if it's a torrent-related URL/file
    """
    return (
        url.startswith("magnet:")
        or url.endswith(".torrent")
        or (os.path.isfile(url) and url.endswith(".torrent"))
    )


def check_libtorrent():
    """
    Check if libtorrent is available and provide helpful error message.

    Raises:
        ImportError: If libtorrent is not available
    """
    if not LIBTORRENT_AVAILABLE:
        print("Error: libtorrent is required for torrent downloads.")
        print("Install it with: pip install libtorrent")
        print("Or on macOS: brew install libtorrent-rasterbar")
        sys.exit(1)


def download_torrent_file(url):
    """
    Download a .torrent file from URL to a temporary file.

    Args:
        url (str): URL to the .torrent file

    Returns:
        str: Path to the downloaded temporary .torrent file
    """
    print(f"Downloading .torrent file from: {url}")
    temp_file = tempfile.NamedTemporaryFile(suffix=".torrent", delete=False)
    try:
        urllib.request.urlretrieve(url, temp_file.name)
        return temp_file.name
    except Exception as e:
        print(f"Error downloading .torrent file: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise


def format_size(bytes_size):
    """
    Format bytes as human readable string.

    Args:
        bytes_size (int): Size in bytes

    Returns:
        str: Formatted size string
    """
    if bytes_size == 0:
        return "0 B"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_time(seconds):
    """
    Format seconds as human readable time string.

    Args:
        seconds (int): Time in seconds

    Returns:
        str: Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds // 60:.0f}m {seconds % 60:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {minutes:.0f}m"


def add_trackers_to_magnet(magnet_uri, additional_trackers=None):
    """
    Add default and additional trackers to a magnet URI.

    Args:
        magnet_uri (str): The original magnet URI
        additional_trackers (list): Additional tracker URLs to add

    Returns:
        str: Enhanced magnet URI with added trackers
    """
    # Combine default trackers with additional ones
    all_trackers = DEFAULT_TRACKERS.copy()
    if additional_trackers:
        all_trackers.extend(additional_trackers)

    # Add tracker parameters to magnet URI
    enhanced_magnet = magnet_uri
    for tracker in all_trackers:
        if f"tr={tracker}" not in enhanced_magnet:
            enhanced_magnet += f"&tr={tracker}"

    return enhanced_magnet


def download_torrent(
    torrent_input,
    output_dir=None,
    seed_time=0,
    high_speed=True,
    additional_trackers=None,
):
    """
    Download a torrent file or magnet link with speed optimizations.

    Args:
        torrent_input (str): Path to .torrent file, magnet link, or URL to .torrent
        output_dir (str): Directory to save downloaded files (default: current directory)
        seed_time (int): Time to seed in minutes after download completes (default: 0)
        high_speed (bool): Enable aggressive speed optimizations (default: True)
        additional_trackers (list): Additional tracker URLs to use (optional)
    """
    check_libtorrent()

    if output_dir is None:
        output_dir = os.getcwd()

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print("QuickDownload - Torrent Mode")
    print(f"Output directory: {output_dir}")
    print("=" * 50)

    # Create libtorrent session with speed optimization settings
    # Compatible with libtorrent 2.0.11
    settings = {
        # Basic settings
        "user_agent": "QuickDownload/1.1",
        "listen_interfaces": "0.0.0.0:6881,[::]:6881",
        # Peer discovery and connectivity
        "enable_dht": True,
        "enable_lsd": True,
        "enable_upnp": True,
        "enable_natpmp": True,
        "enable_incoming_utp": True,
        "enable_outgoing_utp": True,
        # Connection limits (updated for libtorrent 2.x)
        "connections_limit": 500,
        "unchoke_slots_limit": 100,  # Replaces connections_limit_factor
        "max_peerlist_size": 4000,
        # Download optimization (updated for libtorrent 2.x)
        "max_queued_disk_bytes": 16 * 1024 * 1024,
        "use_read_cache": True,
        "coalesce_reads": True,
        "coalesce_writes": True,
        # Piece selection and requesting
        "piece_timeout": 20,
        "request_timeout": 15,
        "max_out_request_queue": 1500,
        "max_allowed_in_request_queue": 2000,
        "whole_pieces_threshold": 20,
        # Bandwidth settings
        "upload_rate_limit": 0,
        "download_rate_limit": 0,
        # Advanced optimizations
        "prefer_udp_trackers": True,
        "allow_multiple_connections_per_ip": True,
        "send_buffer_watermark": 1024 * 1024,
        "send_buffer_low_watermark": 512 * 1024,
        # Tracker optimization
        "tracker_completion_timeout": 20,
        "tracker_receive_timeout": 15,
        "dht_announce_interval": 900,
        # Encryption
        "out_enc_policy": 1,
        "in_enc_policy": 1,
        "allowed_enc_level": 2,
    }

    session = lt.session(settings)

    temp_torrent_file = None

    try:
        # Add torrent based on input type with speed optimizations
        add_params = {
            "save_path": output_dir,
            "flags": (
                lt.torrent_flags.auto_managed | lt.torrent_flags.duplicate_is_error
            ),
        }

        # Add speed optimization flags if high_speed mode is enabled
        if high_speed:
            add_params["flags"] |= lt.torrent_flags.sequential_download
            # Note: Connection and upload limits are set differently in libtorrent 2.x
            # These settings are applied via the session settings instead

        if torrent_input.startswith("magnet:"):
            print("Adding magnet link...")
            # Enhance magnet URI with additional trackers for better peer discovery
            enhanced_magnet = add_trackers_to_magnet(torrent_input, additional_trackers)
            tracker_count = len(DEFAULT_TRACKERS) + (
                len(additional_trackers) if additional_trackers else 0
            )
            print(f"Using {tracker_count} trackers for peer discovery...")
            handle = lt.add_magnet_uri(session, enhanced_magnet, add_params)
        elif torrent_input.startswith("http"):
            print("Downloading and adding .torrent file...")
            temp_torrent_file = download_torrent_file(torrent_input)
            info = lt.torrent_info(temp_torrent_file)
            add_params["ti"] = info
            handle = session.add_torrent(add_params)
        else:
            print(f"Loading .torrent file: {torrent_input}")
            if not os.path.exists(torrent_input):
                raise FileNotFoundError(f"Torrent file not found: {torrent_input}")
            info = lt.torrent_info(torrent_input)
            add_params["ti"] = info
            handle = session.add_torrent(add_params)

        # Wait for metadata (especially important for magnet links)
        print("Waiting for metadata...", end="", flush=True)
        metadata_timeout = 60  # 60 seconds timeout
        start_time = time.time()
        dots_count = 0

        while not handle.has_metadata():
            if time.time() - start_time > metadata_timeout:
                raise TimeoutError("Timeout waiting for torrent metadata")

            # Create animated dots (max 6 dots, then reset)
            dots_count = (dots_count + 1) % 7
            dots = "." * dots_count + " " * (6 - dots_count)
            elapsed = time.time() - start_time
            print(f"\rWaiting for metadata{dots} ({elapsed:.0f}s)", end="", flush=True)
            time.sleep(1)

        print("\nMetadata received!")
        print(f"Torrent name: {handle.name()}")
        print(f"Total size: {format_size(handle.status().total_wanted)}")
        print(f"Files: {handle.get_torrent_info().num_files()}")

        # Apply additional speed optimizations after metadata is available
        if high_speed:
            print("Applying speed optimizations...")
            # Force the torrent to be active and start downloading immediately
            handle.resume()
            handle.set_priority(255)  # Highest priority

            # Set piece priorities for faster start (prioritize first/last pieces)
            torrent_info = handle.get_torrent_info()
            if torrent_info.num_pieces() > 0:
                # Prioritize first and last few pieces for faster startup
                for i in range(min(5, torrent_info.num_pieces())):
                    handle.piece_priority(i, 7)  # Highest piece priority
                for i in range(
                    max(0, torrent_info.num_pieces() - 5), torrent_info.num_pieces()
                ):
                    handle.piece_priority(i, 7)  # Highest piece priority

        print("=" * 50)

        # Download loop
        print("Starting download...")
        last_progress = -1.0
        last_update_time = 0
        start_download_time = time.time()

        while not handle.is_seed():
            status = handle.status()

            # Calculate progress and stats
            progress = status.progress * 100
            download_rate = status.download_rate / 1024  # KB/s
            upload_rate = status.upload_rate / 1024
            downloaded = status.total_done
            total_size = status.total_wanted
            num_peers = status.num_peers
            num_seeds = status.num_seeds

            # Calculate ETA
            if download_rate > 0:
                remaining_bytes = total_size - downloaded
                eta_seconds = remaining_bytes / (download_rate * 1024)
                eta_str = format_time(eta_seconds)
            else:
                eta_str = "∞"

            # Update progress in real-time with smart throttling
            # Update immediately if progress changed, but limit to reasonable frequency
            current_time = time.time()
            time_since_last_update = current_time - last_update_time
            progress_changed = (
                abs(progress - last_progress) >= 0.05
            )  # More sensitive: 0.05%

            should_update = (
                progress_changed  # Any significant progress change
                or time_since_last_update
                >= 0.8  # Force update every 0.8 seconds for live stats
                or last_progress < 0  # First update
            )

            if should_update:
                # Create progress bar for torrent download
                bar_length = 30
                filled_length = int(bar_length * progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                # Print progress with proper line clearing
                progress_line = (
                    f"[{bar}] {progress:.1f}% | "
                    f"{format_size(downloaded)}/{format_size(total_size)} | "
                    f"↓{download_rate:.1f} KB/s ↑{upload_rate:.1f} KB/s | "
                    f"Peers: {num_peers} Seeds: {num_seeds} | "
                    f"ETA: {eta_str}"
                )

                # Clear line and print (ensure we clear enough space)
                print(f"\r{' ' * 120}", end="", flush=True)
                print(f"\r{progress_line}", end="", flush=True)

                last_progress = progress
                last_update_time = current_time

            time.sleep(1)

        download_time = time.time() - start_download_time
        print(f"\n{'=' * 50}")
        print(f"Download completed: {handle.name()}")
        print(f"Time taken: {format_time(download_time)}")
        print(
            f"Average speed: {format_size(handle.status().total_wanted / download_time)}/s"
        )

        # Seed for specified time
        if seed_time > 0:
            print(f"\nSeeding for {seed_time} minutes...")
            seed_end = time.time() + (seed_time * 60)
            total_seed_time = seed_time * 60

            while time.time() < seed_end:
                status = handle.status()
                upload_rate = status.upload_rate / 1024
                uploaded = status.total_upload
                remaining_time = seed_end - time.time()
                elapsed_time = total_seed_time - remaining_time

                # Create seeding progress bar
                seed_progress = (elapsed_time / total_seed_time) * 100
                bar_length = 20
                filled_length = int(bar_length * seed_progress / 100)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)

                print(
                    f"\rSeeding [{bar}] {seed_progress:.1f}% | "
                    f"↑{upload_rate:.1f} KB/s | "
                    f"Uploaded: {format_size(uploaded)} | "
                    f"Time left: {format_time(remaining_time)}",
                    end="",
                    flush=True,
                )
                time.sleep(1)

            print("\nSeeding completed.")

        print(f"Files saved to: {output_dir}")

    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during torrent download: {e}")
        sys.exit(1)
    finally:
        # Clean up temporary torrent file
        if temp_torrent_file and os.path.exists(temp_torrent_file):
            os.unlink(temp_torrent_file)
