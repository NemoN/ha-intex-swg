# Intex Salt-Water Chlorine Generators (SWG) — Home Assistant Integration

Connect an **Intex ECO 6220 / CG-26670 / QS500 Salt-Water Chlorine Generator** to Home Assistant over a fully local REST API.

## Prerequisite Hardware

The generator lacks built-in networking.  
Install an custom **ESP32 board** flashed with the firmware from https://github.com/NemoN/intex-swg-iot and place it between the SWG display panel and the main board. The ESP32 serves JSON on port `8080` - this integration talks to that API.

## Features

| Category  | Description |
|-----------|-------------|
| **Telemetry** | shows diplays status, uptime, free heap |
| **Status / Alarms** | boost, sleep, ozone generation, low-flow, low/high salt, service, working, programming, display on/off |
| **Control** | **Power ON / OFF / STANDBY** buttons |
| **Watch-dog** | optional scheduled reboot every *n* minutes (default 720 min) |
| **Power sensor** | map any existing wattage sensor into the SWG device card |
| **Local-only** | `iot_class: local_polling` — no cloud involved |

## Installation (HACS)

1. In **HACS → Integrations → ⋯ Custom repositories** add https://github.com/NemoN/ha-intex-swg as type **Integration**
2. Install **“Intex Salt Water Chlorine Generators (SWG)”** from the list.  
3. Restart Home Assistant.

**OR**

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=NemoN&repository=ha-intex-swg)

Restart your instance and head over to the integration overview (Or use [this link](https://my.home-assistant.io/redirect/config_flow_start/?domain=nemon_intex_swg) to directly go to the configuration of this component) to start configuring the integration.

![Dashboard overview](https://github.com/NemoN/ha-intex-swg/blob/main/documentation/images/overview.png?raw=true)

## Configuration

Modify settings any time under **Settings → Devices & Services → Intex SWG → ⋯ Configure**.

| Option                | Default   | Purpose                               |
|-----------------------|-----------|---------------------------------------|
| **Host**              | —         | IP address of the ESP32 board         |
| **Port**              | `8080`    | REST API port                         |
| **Scan interval**     | `30 s`    | Polling period                        |
| **Enable auto-reboot**| `false`   | Toggle the watch-dog                  |
| **Reboot every**      | `720 min` | Minutes between reboots               |
| **Power entity**      | —         | Home Assistant sensor providing watts |

## Entities per Generator

* **Sensors:** `display_brightness`, `display_code`, `uptime`, `free_heap`, `power` (optional)  
* **Binary sensors:** `display_on`, `boost_mode`, `sleep_mode`, `o3_generation`, `low_flow`, `low_salt`, `high_salt`, `service_alarm`, `working`, `programming`  
* **Buttons:** `reboot_esp32`, `power_on`, `power_off`, `power_standby`

## Example (Lovelace button card)

```yaml
type: button
entity: button.intex_swg_power_on
name: Chlorinator ON
icon: mdi:power
```

![Dashboard overview](https://github.com/NemoN/ha-intex-swg/blob/main/documentation/images/dashboard.png?raw=true)

```yaml
type: vertical-stack
cards:
  - type: vertical-stack
    cards:
      - type: picture-elements
        image: /api/nemon_intex_swg/icons/back.png
        elements:
          - type: image
            title: Current_Code
            entity: sensor.working_mode
            image: /api/nemon_intex_swg/icons/currentcode.png
            state_filter:
              "off": brightness(10%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/currentcode.png
            style:
              bottom: 52%
              left: 48%
          - type: state-label
            title: Current_Code
            entity: sensor.display_code
            style:
              bottom: 39%
              left: 48%
              font-size: 70px
              font-weight: bold
              color: rgb(255, 0, 0)
          - type: state-label
            entity: input_text.blank
            prefix: working
            style:
              bottom: 69.2%
              left: 16.2%
              color: rgb(0,0,0)
              font-family: Quicksand
              font-size: 100%
              font-weight: bold
              border-radius: 50%
              text-align: center
          - type: image
            title: working
            entity: sensor.working_mode
            image: /api/nemon_intex_swg/icons/ledg.png
            state_filter:
              "off": brightness(10%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/ledg.png
            style:
              bottom: 80.5%
              left: 16.2%
          - type: state-label
            entity: input_text.blank
            prefix: boost
            style:
              bottom: 51.2%
              left: 16.2%
              color: rgb(0,0,0)
              font-family: Quicksand
              font-size: 100%
              font-weight: bold
              border-radius: 50%
              text-align: center
          - type: image
            title: boost
            entity: sensor.boost_mode
            image: /api/nemon_intex_swg/icons/ledg.png
            state_filter:
              "off": brightness(10%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/ledg.png
            style:
              bottom: 62.5%
              left: 16.2%
          - type: state-label
            entity: input_text.blank
            prefix: sleep
            style:
              bottom: 32.2%
              left: 16.2%
              color: rgb(0,0,0)
              font-family: Quicksand
              font-size: 100%
              font-weight: bold
              border-radius: 50%
              text-align: center
          - type: image
            title: sleep
            entity: sensor.sleep_mode
            image: /api/nemon_intex_swg/icons/ledg.png
            state_filter:
              "off": brightness(10%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/ledg.png
            style:
              bottom: 44.5%
              left: 16.2%
          - type: state-label
            entity: input_text.blank
            prefix: low_flow
            style:
              bottom: 74.2%
              right: 10%
              transform: none
              color: rgb(0,0,0)
              font-family: Quicksand
              font-size: 100%
              font-weight: bold
              border-radius: 50%
          - type: image
            title: low_flow
            entity: sensor.low_flow_alarm
            image: /api/nemon_intex_swg/icons/ledr.png
            state_filter:
              "off": brightness(10%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/ledr.png
            style:
              bottom: 80.5%
              right: 13%
          - type: state-label
            entity: input_text.blank
            prefix: low_salz
            style:
              bottom: 56.2%
              right: 10%
              transform: none
              color: rgb(0,0,0)
              font-family: Quicksand
              font-size: 100%
              font-weight: bold
              border-radius: 50%
          - type: image
            title: low_salz
            entity: sensor.low_salt_alarm
            image: /api/nemon_intex_swg/icons/ledr.png
            state_filter:
              "off": brightness(10%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/ledr.png
            style:
              bottom: 62.5%
              right: 13%
          - type: state-label
            entity: input_text.blank
            prefix: high_salz
            style:
              bottom: 37.2%
              right: 10%
              transform: none
              color: rgb(0,0,0)
              font-family: Quicksand
              font-size: 100%
              font-weight: bold
              border-radius: 50%
          - type: image
            title: high_salz
            entity: sensor.high_salt_alarm
            image: /api/nemon_intex_swg/icons/ledr.png
            state_filter:
              "off": brightness(10%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/ledr.png
            style:
              bottom: 44.5%
              right: 13%
          - type: state-label
            entity: input_text.blank
            prefix: service
            style:
              bottom: 18.2%
              right: 10%
              transform: none
              color: rgb(0,0,0)
              font-family: Quicksand
              font-size: 100%
              font-weight: bold
              border-radius: 50%
          - type: image
            title: service
            entity: sensor.service_alarm
            image: /api/nemon_intex_swg/icons/ledr.png
            state_filter:
              "off": brightness(10%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/ledr.png
            style:
              bottom: 26.5%
              right: 13%
          - type: image
            title: Boost
            entity: sensor.boost_mode
            image: /api/nemon_intex_swg/icons/boost.png
            state_filter:
              "off": brightness(100%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/boost.png
            style:
              bottom: 39%
              left: 48.5%
          - type: image
            title: SelfClean
            entity: sensor.service_alarm
            image: /api/nemon_intex_swg/icons/selfclean.png
            state_filter:
              "off": brightness(100%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/selfclean.png
            style:
              bottom: 2.0%
              left: 48.5%
          - type: image
            title: Lock_Unlock
            entity: sensor.service_alarm
            image: /api/nemon_intex_swg/icons/lockunlock.png
            state_filter:
              "off": brightness(100%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/lockunlock.png
            style:
              bottom: 19.7%
              left: 33.4%
          - type: image
            title: Timer
            entity: sensor.service_alarm
            image: /api/nemon_intex_swg/icons/timer.png
            state_filter:
              "off": brightness(100%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/timer.png
            style:
              bottom: 19.7%
              left: 63.9%
          - type: image
            title: Power
            entity: sensor.working_mode
            image: /api/nemon_intex_swg/icons/power.png
            state_filter:
              "off": brightness(100%) saturate(1)
              "on": brightness(100%) saturate(1)
            state_image:
              "on": /api/nemon_intex_swg/icons/power.png
            style:
              bottom: 16.2%
              left: 48.7%
  - type: entities
    entities:
      - entity: button.power_standby
      - entity: button.power_on
      - entity: button.power_off
      - entity: button.reboot_esp32
      - entity: sensor.power
      - entity: sensor.working_mode
      - entity: sensor.uptime_dd_hh_mm
```
