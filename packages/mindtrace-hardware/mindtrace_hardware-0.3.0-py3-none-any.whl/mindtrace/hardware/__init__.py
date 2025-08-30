"""
Mindtrace Hardware Module

A comprehensive hardware abstraction layer providing unified access to
cameras, PLCs, sensors, and other industrial hardware components with
lazy imports to prevent cross-contamination between different backends.

Key Features:
    - Lazy import system to avoid loading all backends at startup
    - Unified interface for different hardware types
    - Async-first design for optimal performance
    - Thread-safe operations across all components
    - Comprehensive error handling and logging
    - Configuration management system
    - Mock backends for testing and development

Hardware Components:
    - CameraManager: Unified camera management (Daheng, Basler, OpenCV)
    - PLCManager: Unified PLC management (Allen-Bradley, Siemens, Modbus)
    - SensorManager: Sensor data acquisition and monitoring (Future)
    - ActuatorManager: Actuator control and positioning (Future)

Design Philosophy:
    This module uses lazy imports to prevent SWIG warnings from pycomm3
    appearing in camera tests, and to avoid loading heavy SDKs unless
    they are actually needed. Each manager is only imported when accessed.

Usage:
    # Import managers only when needed
    from mindtrace.hardware import CameraManager, PLCManager

    # Camera operations
    async with CameraManager() as camera_manager:
        cameras = camera_manager.discover_cameras()
        camera = await camera_manager.get_camera(cameras[0])
        image = await camera.capture()

    # PLC operations
    async with PLCManager() as plc_manager:
        await plc_manager.register_plc("PLC1", "AllenBradley", "192.168.1.100")
        await plc_manager.connect_plc("PLC1")
        values = await plc_manager.read_tag("PLC1", ["Tag1", "Tag2"])

Configuration:
    All hardware components use the unified configuration system:
    - Environment variables with MINDTRACE_HW_ prefix
    - JSON configuration files
    - Programmatic configuration via dataclasses
    - Hierarchical configuration inheritance

Thread Safety:
    All hardware managers are thread-safe and can be used concurrently
    from multiple threads without interference.
"""


def __getattr__(name):
    """Lazy import implementation to avoid loading all backends at once."""
    if name == "CameraManager":
        from .cameras.camera_manager import CameraManager

        return CameraManager
    elif name == "PLCManager":
        from .plcs.plc_manager import PLCManager

        return PLCManager
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ["CameraManager", "PLCManager"]
