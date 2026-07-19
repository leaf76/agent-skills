---
name: firmware-feature-writer
description: Use when implementing, debugging, or refactoring embedded firmware features (C/C++/Rust). Focus on deterministic behavior, peripheral/register correctness, RTOS/task safety, and testability on constrained devices.
metadata:
  short-description: Embedded firmware feature implementation workflow
---

# Firmware Feature Writer

Goal: Deliver firmware logic that is behaviorally correct on real hardware and maintainable under constraints.

## Scope
- Add or refactor drivers, protocol handlers, control loops, sensor/actuator logic, state machines, power management, and error handling in embedded codebases.
- C/C++/Rust firmware projects using HAL/SDK, RTOS, or bare-metal build systems.
- Firmware feature tasks that require hardware constraints and timing awareness.
- Do **not** use this skill for hardware design or PCB/layout tasks.

## Workflow

1. **Confirm hardware boundaries**
   - MCU/SoC family, clock, and memory limits
   - Relevant peripherals, pin map, and IRQ priorities
   - RTOS presence/version, and interfaces (I2C/SPI/UART/CAN/USB/ADC/PWM, etc.)
   - Power, timing, watchdog, and safety requirements
2. **Locate existing patterns and interfaces**
   - Read the module/driver ABI and call graph first
   - Identify shared data paths (global state, ISR-to-task communication)
   - Verify error codes/return conventions and retry policies
3. **Define feature contract**
   - Explicitly specify inputs, outputs, boundary conditions, error paths, timeouts, and fallback behavior
   - Define state transitions and invariants for safe and failure states
4. **Implement with a minimal first pass**
   - Build the smallest verifiable version first, then add exception handling and optimization
   - Keep ISR work minimal: capture + wake mechanism only; move heavy processing to tasks/threads
   - Use fixed-width integer types (`uint8_t`, `uint16_t`, etc.) and avoid ambiguous casts
5. **Verify logical correctness**
   - Set clear synchronization and memory-barrier rules across async/sync boundaries
   - Add parameter validation and `assert`/error reporting to avoid silent failures
   - Document timing assumptions and measurement points for time-sensitive paths
6. **Integrate and regression check**
   - Update init/shutdown ordering and sequence-sensitive flows to avoid interrupt-related regressions
   - Ensure low-power, reset, and watchdog flows do not violate new logic
   - Add diagnostic logging (non-sensitive values) for field troubleshooting

## Firmware Checklist
- Is shared data protected from races (`volatile`, mutex/queue/critical sections as appropriate)?
- Is ISR re-entry safe? Can ISR/task interleaving create ghost states?
- Do timeout and retry loops have hard limits and a reporting path to avoid infinite blocking?
- Are external inputs validated, debounced, and filtered when required?
- Are integer overflow, fixed-point arithmetic, division-by-zero, and uninitialized values handled?
- Are build warnings reduced to zero (at least in modified modules)?

## Typical Output Format
- Summarize requirement understanding first.
- List changed modules and side effects per step.
- Document key before/after behavior for critical code sections (avoid unrelated edits).
- Include hardware validation plan (host test, HIL/SIL, bootloader/flash validation).

## Default Guidance
- Supported toolchains include CMake / Make / Zephyr / NuttX / ESP-IDF / STM32Cube / HAL.
- Do not hardcode vendor-specific private process details across projects.
- If critical hardware information is missing (datasheet section, interrupt table, power-up sequence), request it before implementation.
- For timing-critical work, require measurement scripts and explicit boundary-condition tests.
