# Flitsmeister DOT

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

**✨ Develop in the cloud:** Want to contribute or customize this integration? Open it directly in GitHub Codespaces - no local setup required!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/DaanVervacke/hass-flitsmeister-dot?quickstart=1)

Home Assistant integration for the [Flitsmeister DOT](https://www.flitsmeister.nl/), the dashboard device that warns drivers about speed cameras and hazards. It connects over Bluetooth Low Energy and works without the Flitsmeister phone app.

> [!IMPORTANT]
> Unofficial and not endorsed by Flitsmeister. A firmware update can break it. The DOT accepts one Bluetooth connection at a time, so while Home Assistant is connected the phone app is not.

## ✨ Features

- **No credentials**: the DOT is paired over Bluetooth, nothing to sign in to
- **Live status**: battery level, charging state and motion, pushed while the DOT is awake
- **Alerts from Home Assistant**: play any Flitsmeister alert on the DOT from an automation, with the LED pattern and sound the app uses
- **Approach progress**: light the LED ring in a DOT color or any RGB color to show how close the car is to a hazard
- **Button events**: trigger automations from the red and blue button, short and long press
- **Settings control**: change the volume, LED brightness and LED orientation
- **Discovery**: the DOT is found automatically once it wakes up

**This integration will set up the following platforms.**

| Platform | Description                                         |
| -------- | --------------------------------------------------- |
| `sensor` | Battery, charging state, motion and speech language |
| `select` | Volume, LED brightness and LED orientation          |
| `event`  | Red and blue button, each with short and long press |

## 🚀 Quick Start

### Step 1: Install the Integration

**Prerequisites:** Home Assistant 2026.11 or newer has the Marketplace built in (**Settings** → **Marketplace**). On older versions, install [HACS](https://hacs.xyz/) (Home Assistant Community Store) first.

Click the button below to open the integration in the Marketplace, or in HACS on older versions:

[![Open your Home Assistant instance and open this repository in the Marketplace.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=DaanVervacke&repository=hass-flitsmeister-dot&category=integration)

Then:

1. Click "Download" to install the integration
2. With HACS (before Home Assistant 2026.11), **restart Home Assistant**. The Marketplace loads it right away.

> [!NOTE]
> The My Home Assistant redirect will first take you to a landing page. Click the button there to open your Home Assistant instance.

<details>
<summary><strong>Manual Installation (Advanced)</strong></summary>

If you prefer not to use the Marketplace or HACS:

1. Download the `custom_components/flitsmeister_dot/` folder from this repository
2. Copy it to your Home Assistant's `custom_components/` directory
3. Restart Home Assistant

</details>

### Step 2: Add the DOT

The DOT sleeps while it is parked and wakes when its accelerometer senses motion, so pick it up or take it for a drive before setup.

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"** and search for "Flitsmeister DOT"
3. Pick your DOT from the discovered devices, or enter its Bluetooth address by hand
4. Home Assistant connects once to check the DOT, then finishes

Once the DOT wakes up, Home Assistant connects and stays connected while it is awake. While it sleeps in a parked car, its entities show as unavailable.

### Step 3: Start Using!

The integration creates these entities for your DOT:

- **Sensors**: battery level, charging state (unplugged, charging, plugged in), motion (parked, driving), speech language (diagnostic)
- **Selects**: volume (silent, low, normal, hard), LED brightness (10 to 100), LED orientation (normal, upside down)
- **Events**: red button and blue button, each with short_press and long_press

Find all entities in **Settings** → **Devices & Services** → **Flitsmeister DOT** → click on the device.

## Actions

Two actions drive the DOT from automations. Both target the DOT device and fail with a clear error while it is asleep.

### `flitsmeister_dot.play_animation`

Play one of the alert animations the Flitsmeister app uses, with the matching LED pattern and sound.

```yaml
action: flitsmeister_dot.play_animation
data:
  device_id: your_dot_device_id
  preset: speed_trap
```

Presets include `speed_trap`, `speed_cam`, `traffic_camera`, `avg_speed_check_start`, `avg_speed_check_end`, `traffic_jam_start`, `traffic_jam_end`, `police_hotspot`, `roadworks`, `ambulance`, `fire_truck`, `police`, `emergency_vehicle`, `railway_crossing`, `wrong_way_driving`, `wrong_way_driver`, incident variants like `accident`, `object_on_road` and `animal_on_the_road`, lane closures, and utilities like `startup`, `fade_out` and `updating`.

### `flitsmeister_dot.play_progress`

Light the LED ring to show how close the car is to a hazard, like the approach progress in the app.

```yaml
action: flitsmeister_dot.play_progress
data:
  device_id: your_dot_device_id
  color: speed_trap
  fraction: 50
  blink: false
```

Set `blink: true` for the blinking overspeed warning with the reduce speed sound. Give `color` for one of the DOT's own
colors, or `rgb_color` for any color, such as `rgb_color: [255, 85, 0]`. A call takes one of the two.

## Button events

The DOT has two buttons. A press under one second is a short press, holding longer is a long press, the same thresholds the Flitsmeister app uses. In the app a long press files a report with Flitsmeister, which Home Assistant cannot do, so the buttons are yours: trigger any automation from the event entities.

## Troubleshooting

### The DOT does not show up in discovery

The DOT only advertises after accelerometer motion. Pick it up, shake it, or drive with it, then try again. You can also add it by its Bluetooth address without discovery.

### Entities are unavailable

While the DOT sleeps in a parked car its entities are unavailable. That is normal. They come back when the DOT wakes and Home Assistant reconnects.

### The phone app cannot connect

The DOT accepts one Bluetooth connection at a time. While Home Assistant is connected, the Flitsmeister app is not. To give the DOT back to the app, disable or remove the integration.

### Enable Debug Logging

To enable debug logging for this integration, add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.flitsmeister_dot: debug
    flitsmeister_dot_ble: debug
```

### Diagnostics

Download diagnostics from **Settings** → **Devices & Services** → **Flitsmeister DOT** → the 3 dots menu. The Bluetooth address and serial number are redacted before download.

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request if you have suggestions or improvements.

You have two options to set up a development environment — expand below for full details.

<details>
<summary><strong>Development Setup</strong></summary>

Both options provide the same fully-configured environment with Home Assistant, Python 3.14, Node.js LTS, and all necessary tools.

### Option 1: GitHub Codespaces (Recommended) ☁️

Develop directly in your browser without installing anything locally!

1. Click the green **"Code"** button in this repository
2. Switch to the **"Codespaces"** tab
3. Click **"Create codespace on main"**
4. **Wait for setup** (2-3 minutes first time) — everything installs automatically
5. **Review and commit** your changes in the Source Control panel (`Ctrl+Shift+G`)

> [!TIP]
> Codespaces gives you **60 hours/month free** for personal accounts. When you start Home Assistant (`script/develop`), port 8123 forwards automatically.

### Option 2: Local Development with VS Code 💻

#### Prerequisites

You'll need these installed locally:

- **A Docker-compatible container engine** — see options by platform:

  | Option                                                                                                                   | 🍎 macOS | 🐧 Linux | 🪟 Windows | Notes                                                                                                                                                                             |
  | ------------------------------------------------------------------------------------------------------------------------ | :------: | :------: | :--------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | [Docker Desktop](https://www.docker.com/products/docker-desktop/)                                                        |    ✅    |    ✅    |     ✅     | **Easiest starting point for all platforms.** GUI-based, well-documented, one installer. Uses WSL2 as default backend on Windows (Hyper-V also available). Free for personal use. |
  | [OrbStack](https://orbstack.dev/) ⭐                                                                                     |    ✅    |    —     |     —      | **Recommended for macOS** once Docker Desktop feels slow. Starts in ~2s, much lighter on RAM, full Docker API compatibility. Free for personal use.                               |
  | [Docker CE](https://docs.docker.com/engine/install/) (native) ⭐                                                         |    —     |    ✅    |     —      | **Recommended for Linux.** Install directly via your package manager — no VM, no GUI, no overhead. Free for personal use.                                                         |
  | [WSL2](https://learn.microsoft.com/windows/wsl/install) + [Docker CE](https://docs.docker.com/engine/install/ubuntu/) ⭐ |    —     |    —     |     ✅     | **Recommended for Windows** once you're comfortable with WSL2. Docker runs natively inside WSL2 — no GUI overhead. Requires one-time WSL2 setup.                                  |
  | [Rancher Desktop](https://rancherdesktop.io/)                                                                            |    ✅    |    ✅    |     ✅     | Open source by SUSE. GUI-based, uses WSL2 on Windows. Good alternative to Docker Desktop. Free for personal use.                                                                  |
  | [Colima](https://github.com/abiosoft/colima)                                                                             |    ✅    |    ✅    |     —      | CLI-only, very lightweight. Good alternative for terminal-focused users. Free for personal use.                                                                                   |

- **VS Code** with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- **Git** — macOS and Linux usually have it already; see below if not, or to get a newer version:
  - **🍎 macOS:** The system Git (`xcode-select --install`) works fine. Recommended: `brew install git` ([Homebrew](https://brew.sh/)) for a current version.
  - **🐧 Linux:** Usually pre-installed. If not: `sudo apt install git` (or your distro's equivalent).
  - **🪟 Windows + WSL2 ⭐:** Install Git _inside WSL2_ with `sudo apt install git`. Git on Windows itself is not needed — VS Code clones and operates entirely within WSL2.
  - **🪟 Windows + Docker Desktop:** Install via `winget install Git.Git` or download [Git for Windows](https://git-scm.com/download/win).
- **Hardware** — the devcontainer runs a full Home Assistant instance including Python tooling:

  |          | Minimum    | Recommended                           |
  | -------- | ---------- | ------------------------------------- |
  | **RAM**  | 8 GB       | 16 GB or more                         |
  | **CPU**  | 4 cores    | 8 cores or more                       |
  | **Disk** | 10 GB free | 20 GB free (SSD strongly recommended) |

> [!TIP]
> **Not sure which Docker option to pick?** Start with [Docker Desktop](https://www.docker.com/products/docker-desktop/) — it works on all platforms, has a GUI, and needs no extra setup. The ⭐ options are faster alternatives once you're comfortable. macOS and Linux offer the best devcontainer experience — containers run with no extra VM layer and file I/O is fast. Windows works well too — this integration uses named container volumes (files live inside WSL2, not on the Windows drive) to keep performance acceptable.

> [!NOTE]
> **New to Dev Containers?** See the [VS Code Dev Containers documentation](https://code.visualstudio.com/docs/devcontainers/containers#_system-requirements) for system requirements and how to install the extension. **Once the extension is installed, you're done** — this repository already ships a complete devcontainer configuration. You don't need to follow the rest of the VS Code guide; the setup steps below are all that's needed.

#### Setup Steps

1. **Clone in a Dev Container:**

   **🍎 macOS / 🐧 Linux:** Clone the repository and open the folder in VS Code → click **"Reopen in Container"** when prompted (or `F1` → **Dev Containers: Reopen in Container**).

   **🪟 Windows:** In VS Code, press `F1` → **Dev Containers: Clone Repository in Named Container Volume..."** and enter the repository URL. This keeps files inside WSL2 for best I/O performance.

2. Wait for the container to build (2-3 minutes first time)

3. **Review and commit** changes in Source Control (`Ctrl+Shift+G`)

4. **Start developing**:

   ```bash
   script/develop  # Home Assistant runs at http://localhost:8123
   ```

> [!NOTE]
> Both Codespaces and local DevContainer provide the exact same experience. The only difference is where the container runs (GitHub's cloud vs. your machine).

### Option 3: Without a Dev Container 🧑‍💻

Claude Code, Codex, OpenCode or GitHub Copilot can work on the repository directly — on your machine or in their
cloud environments. When a session starts, the agent's hook prepares the checkout: in a Claude Code cloud session it
installs everything by itself, and Codex cloud picks up the install command from `AGENTS.md`. Nothing has to be
configured in the cloud environment.

On your own machine, install [mise](https://mise.jdx.dev/getting-started.html) for the pinned tool versions (optional,
the scripts fall back to what is on your `PATH`) and run:

```bash
script/setup/bootstrap  # Python, the tools from mise.toml, Home Assistant and the test dependencies
script/develop          # Home Assistant runs at http://localhost:8123
```

</details>

---

## 🤖 AI-Assisted Development

> [!NOTE]
> **Transparency Notice:** This integration was developed with assistance from AI coding agents (GitHub Copilot,
> Claude, and others). AI assistance by itself neither guarantees nor rules out software quality. To make an informed
> installation decision, review the project's stated maturity, known limitations, automated test coverage, real-device
> testing, and the extent of human review. See the blueprint's [`AI_POLICY.md`](AI_POLICY.md) for
> guidance.
>
> - **AI assistance:** substantial
> - **Human review:** partial, the maintainer decided the feature scope, entity list and connection model in a structured interview
> - **Automated tests:** full suite passing, 179 tests covering setup, config flow, entities and actions against an in-memory fake device
> - **Real-device or service testing:** not performed yet, pending verification against a live DOT
> - **Maturity and known limitations:** first release, depends on the unofficial flitsmeister-dot-ble library, a firmware update can break the protocol
>
> If you encounter unexpected behavior, please [open an issue](../../issues) on GitHub.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [@DaanVervacke][user_profile]**

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/DaanVervacke/hass-flitsmeister-dot.svg?style=for-the-badge
[commits]: https://github.com/DaanVervacke/hass-flitsmeister-dot/commits/main
[hacs]: https://www.hacs.xyz/docs/marketplace/
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/DaanVervacke/hass-flitsmeister-dot.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40DaanVervacke-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/DaanVervacke/hass-flitsmeister-dot.svg?style=for-the-badge
[releases]: https://github.com/DaanVervacke/hass-flitsmeister-dot/releases
[user_profile]: https://github.com/DaanVervacke

<!-- Optional badge definitions - uncomment if needed:
[buymecoffee]: https://www.buymeacoffee.com/DaanVervacke
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
-->
